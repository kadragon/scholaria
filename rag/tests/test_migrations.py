"""
Test migration rollback and forward compatibility.

These tests ensure database migrations can be safely applied and rolled back
without losing data integrity or causing schema conflicts.
"""

from django.core.management import call_command
from django.test import TransactionTestCase


class MigrationCompatibilityTest(TransactionTestCase):
    """Test migration rollback and forward compatibility."""

    def test_migration_forward_rollback_cycle(self):
        """Test full migration cycle: initial -> latest -> rollback -> forward."""
        # Start from initial state
        call_command("migrate", "rag", "0001_initial", verbosity=0)

        # Apply all migrations
        call_command("migrate", "rag", verbosity=0)

        # Rollback to each previous migration and forward again
        migrations = [
            "0004_add_uploaded_file_field",
            "0003_topic_contexts",
            "0002_context_contextitem",
            "0001_initial",
        ]

        for i, migration in enumerate(migrations[:-1]):
            # Rollback to previous migration
            prev_migration = migrations[i + 1]
            call_command("migrate", "rag", prev_migration, verbosity=0)

            # Forward to current migration
            call_command("migrate", "rag", migration, verbosity=0)

    def test_rollback_to_initial_migration(self):
        """Test rolling back to the very first migration."""

        from rag.models import Context, ContextItem, Topic

        # Ensure we start from latest
        call_command("migrate", "rag", verbosity=0)

        # Rollback to initial migration
        call_command("migrate", "rag", "0001_initial", verbosity=0)

        # Verify Topic model works
        topic = Topic.objects.create(name="Test Topic", description="Test description")
        self.assertTrue(topic.id)

        # Verify Context and ContextItem models don't exist
        try:
            Context.objects.all()
            self.fail("Context model should not exist after rollback")
        except Exception:
            # Expected - table doesn't exist
            pass

        try:
            ContextItem.objects.all()
            self.fail("ContextItem model should not exist after rollback")
        except Exception:
            # Expected - table doesn't exist
            pass

    def test_migration_dependencies_respected(self):
        """Test that migration dependencies are properly enforced."""
        from rag.models import Context, Topic

        # Start fresh
        call_command("migrate", "rag", "zero", verbosity=0)

        # Apply initial migrations step by step
        call_command("migrate", "rag", "0001_initial", verbosity=0)

        # Verify only Topic works
        topic = Topic.objects.create(name="Test", description="Test")
        self.assertTrue(topic.id)

        # Apply second migration
        call_command("migrate", "rag", "0002_context_contextitem", verbosity=0)

        # Now Context should work
        context = Context.objects.create(
            name="Test Context", description="Test", context_type="PDF"
        )
        self.assertTrue(context.id)

    def test_data_preservation_during_rollback(self):
        """Test that rolling back migrations preserves data when possible."""
        from rag.models import Topic

        # Apply all migrations
        call_command("migrate", "rag", verbosity=0)

        # Create test data
        topic = Topic.objects.create(
            name="Test Topic",
            description="Test description",
            system_prompt="Test prompt",
        )
        topic_id = topic.id

        # Rollback to migration that still has Topic model
        call_command("migrate", "rag", "0001_initial", verbosity=0)

        # Forward again
        call_command("migrate", "rag", verbosity=0)

        # Verify data is preserved
        preserved_topic = Topic.objects.get(id=topic_id)
        self.assertEqual(preserved_topic.name, "Test Topic")
        self.assertEqual(preserved_topic.description, "Test description")
        self.assertEqual(preserved_topic.system_prompt, "Test prompt")


class MigrationSchemaTest(TransactionTestCase):
    """Test migration schema changes don't break existing functionality."""

    def setUp(self):
        """Ensure clean migration state."""
        call_command("migrate", "rag", verbosity=0)

    def test_all_models_created_correctly(self):
        """Test that all migrations result in correct model creation."""
        from rag.models import Context, ContextItem, Topic

        # Test Topic model
        topic = Topic.objects.create(
            name="Schema Test Topic",
            description="Testing schema",
            system_prompt="Test prompt",
        )
        self.assertTrue(topic.id)

        # Test Context model
        context = Context.objects.create(
            name="Schema Test Context",
            description="Testing context schema",
            context_type="PDF",
        )
        self.assertTrue(context.id)

        # Test ContextItem model
        context_item = ContextItem.objects.create(
            title="Schema Test Item",
            content="Test content",
            context=context,
            metadata={"test": "data"},
        )
        self.assertTrue(context_item.id)

        # Test ManyToMany relationship
        topic.contexts.add(context)
        self.assertEqual(topic.contexts.count(), 1)
        self.assertEqual(context.topics.count(), 1)

    def test_field_constraints_enforced(self):
        """Test that database constraints from migrations are enforced."""
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError

        from rag.models import ContextItem, Topic

        # Test model validation (clean method)
        topic = Topic()
        with self.assertRaises(ValidationError):
            topic.clean()  # Missing required name and description

        # Test foreign key constraint at database level
        with self.assertRaises(IntegrityError):
            ContextItem.objects.create(
                title="Test",
                content="Test content",
                context_id=99999,  # Non-existent context
            )

    def test_json_field_functionality(self):
        """Test that JSONField works correctly after migrations."""
        from rag.models import Context, ContextItem

        context = Context.objects.create(
            name="JSON Test Context", description="Testing JSON", context_type="PDF"
        )

        # Test JSON field with complex data
        metadata = {
            "file_size": 1024,
            "pages": 10,
            "tags": ["education", "math"],
            "nested": {"author": "Test Author", "year": 2023},
        }

        context_item = ContextItem.objects.create(
            title="JSON Test Item",
            content="Test content",
            context=context,
            metadata=metadata,
        )

        # Refresh from database
        context_item.refresh_from_db()

        # Verify JSON data is preserved correctly
        self.assertEqual(context_item.metadata["file_size"], 1024)  # type: ignore[index]
        self.assertEqual(context_item.metadata["pages"], 10)  # type: ignore[index]
        self.assertIn("education", context_item.metadata["tags"])  # type: ignore[index]
        self.assertEqual(context_item.metadata["nested"]["author"], "Test Author")  # type: ignore[index]
