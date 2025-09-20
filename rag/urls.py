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
]
