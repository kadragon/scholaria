from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from rag.models import ContextItem
from rag.retrieval.embeddings import EmbeddingService
from rag.retrieval.qdrant import QdrantService


class Command(BaseCommand):
    """Management command to re-index existing ContextItems to Qdrant."""

    help = "Re-index existing ContextItems to Qdrant vector database"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10,
            help="Number of items to process in each batch (default: 10)",
        )
        parser.add_argument(
            "--reset-collection",
            action="store_true",
            help="Reset the Qdrant collection before reindexing",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        batch_size = options["batch_size"]
        reset_collection = options["reset_collection"]

        self.stdout.write("Initializing services...")
        embedding_service = EmbeddingService()
        qdrant_service = QdrantService()

        if reset_collection:
            self.stdout.write("Resetting Qdrant collection...")
            qdrant_service.reset_collection()
        else:
            self.stdout.write("Ensuring Qdrant collection exists...")
            qdrant_service.create_collection()

        # Get all ContextItems
        context_items = ContextItem.objects.select_related("context").all()
        total_items = context_items.count()

        if total_items == 0:
            self.stdout.write(
                self.style.WARNING("No ContextItems found. Nothing to reindex.")
            )
            return

        self.stdout.write(f"Found {total_items} ContextItems to reindex")

        processed = 0
        failed = 0

        # Process in batches
        for i in range(0, total_items, batch_size):
            batch = context_items[i : i + batch_size]
            self.stdout.write(f"Processing batch {i // batch_size + 1}...")

            for context_item in batch:
                try:
                    # Generate embedding
                    embedding = embedding_service.generate_embedding(
                        context_item.content
                    )

                    # Store in Qdrant
                    metadata = context_item.metadata or {}
                    qdrant_service.store_embedding(
                        context_item_id=context_item.id,
                        embedding=embedding,
                        metadata={
                            "chunk_index": metadata.get("chunk_index", 0),
                            "source_file": metadata.get("source_file", ""),
                        },
                    )

                    processed += 1
                    self.stdout.write(
                        f"✓ Indexed ContextItem {context_item.id}: {context_item.title[:50]}..."
                    )

                except Exception as e:
                    failed += 1
                    self.stderr.write(
                        f"✗ Failed to index ContextItem {context_item.id}: {e}"
                    )

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Reindexing completed!")
        self.stdout.write(f"Total items: {total_items}")
        self.stdout.write(self.style.SUCCESS(f"Successfully indexed: {processed}"))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {failed}"))
        self.stdout.write("=" * 50)
