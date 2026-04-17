from django.urls import path
from . import views

app_name = 'buckets'

urlpatterns = [
    path('', views.BucketListView.as_view(), name='list'),
    path('create/', views.BucketCreateView.as_view(), name='create'),
    path('api/bucket/', views.APIBucketDetailView.as_view(), name='api_detail'),
    path('api/upload/', views.APIFileUploadView.as_view(), name='api_upload'),
    
    # Compute & PaaS (Real Project Deployment) - High Priority
    path('compute/', views.AppListView.as_view(), name='app_list'),
    path('compute/new/', views.AppCreateView.as_view(), name='app_create'),
    path('compute/a/<int:app_id>/', views.AppDetailView.as_view(), name='app_detail'),
    path('compute/a/<int:app_id>/deploy/', views.AppDeployView.as_view(), name='app_deploy'),
    path('compute/a/<int:app_id>/upload-source/', views.AppSourceUploadView.as_view(), name='app_source_upload'),

    # Object Storage & Buckets
    path('<slug:bucket_name>/', views.BucketDetailView.as_view(), name='detail'),
    path('<slug:bucket_name>/upload/', views.FileUploadView.as_view(), name='upload'),
    path('<slug:bucket_name>/keys/create/', views.APIKeyCreateView.as_view(), name='create_key'),
    path('<slug:bucket_name>/deploy/', views.BucketDeployView.as_view(), name='deploy'),
    
    path('file/<int:file_id>/download/', views.FileDownloadView.as_view(), name='download'),
    path('file/<int:file_id>/delete/', views.FileDeleteView.as_view(), name='delete'),
    
    # Deployment & Static Hosting
    path('s/<slug:dist_id>/', views.PublicServeView.as_view(), name='public_serve_root'),
    path('s/<slug:dist_id>/<path:filename>', views.PublicServeView.as_view(), name='public_serve'),
]
