from django.urls import path
from .views import JobDetailView, JobListView

urlpatterns = [
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<str:pk>', JobDetailView.as_view(), name='job-detail'),
]