from django.urls import path

from . import views

app_name = "rag"

urlpatterns = [
    path("topics/", views.TopicListView.as_view(), name="topics"),
    path("topics/<int:pk>/", views.TopicDetailView.as_view(), name="topic-detail"),
    path("ask/", views.AskQuestionView.as_view(), name="ask-question"),
]
