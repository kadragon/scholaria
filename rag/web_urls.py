from django.urls import path

from . import views

app_name = "rag_web"

urlpatterns = [
    # Web UI endpoints
    path("", views.TopicSelectionView.as_view(), name="topic-selection"),
    path("qa/", views.QAInterfaceRedirectView.as_view(), name="qa-interface-redirect"),
    path("qa/<int:topic_id>/", views.QAInterfaceView.as_view(), name="qa-interface"),
]
