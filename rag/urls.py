from django.urls import path

from . import views

app_name = "rag"

urlpatterns = [
    # API endpoints - Topics
    path("topics/", views.TopicListView.as_view(), name="topics"),
    path("topics/<int:pk>/", views.TopicDetailView.as_view(), name="topic-detail"),
    # API endpoints - Contexts
    path("contexts/", views.ContextListView.as_view(), name="contexts"),
    path(
        "contexts/<int:pk>/", views.ContextDetailView.as_view(), name="context-detail"
    ),
    path(
        "contexts/<int:context_id>/chunks/",
        views.ContextChunksView.as_view(),
        name="context-chunks",
    ),
    # API endpoints - RAG
    path("ask/", views.AskQuestionView.as_view(), name="ask-question"),
    # API endpoints - History
    path("history/", views.HistoryListCreateView.as_view(), name="history-list"),
    path(
        "history/favorites/",
        views.HistoryFavoritesView.as_view(),
        name="history-favorites",
    ),
    path(
        "history/<int:history_id>/favorite/",
        views.ToggleFavoriteView.as_view(),
        name="history-favorite",
    ),
    path("history/clear/", views.ClearHistoryView.as_view(), name="history-clear"),
    # API endpoints - Question Suggestions
    path(
        "topics/<int:topic_id>/suggestions/",
        views.QuestionSuggestionsView.as_view(),
        name="question-suggestions",
    ),
    # API endpoints - Chunk Management
    path(
        "contexts/<int:context_id>/chunks/preview/",
        views.ChunkPreviewView.as_view(),
        name="chunk-preview",
    ),
    path(
        "contexts/<int:context_id>/chunks/bulk/",
        views.ChunkBulkOperationsView.as_view(),
        name="chunk-bulk",
    ),
    path(
        "contexts/<int:context_id>/status/",
        views.ProcessingStatusView.as_view(),
        name="processing-status",
    ),
    path(
        "contexts/<int:context_id>/chunks/search/",
        views.ChunkSearchView.as_view(),
        name="chunk-search",
    ),
    path(
        "contexts/<int:context_id>/chunks/validate/",
        views.ChunkValidationView.as_view(),
        name="chunk-validate",
    ),
]
