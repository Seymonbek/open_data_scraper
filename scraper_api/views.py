from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination

from .models import Job
from .serializers import JobSerializer

class JobPagination(PageNumberPagination):
    page_size = 10

class JobListView(generics.ListAPIView):
    queryset = Job.objects.all().order_by('-posted_at')
    serializer_class = JobSerializer
    filter_backends = [filters.SearchFilter,]
    search_fields = ['title', 'company']
    pagination_class = JobPagination

class JobDetailView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

