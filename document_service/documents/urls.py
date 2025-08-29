from django.urls import path
from . import views

urlpatterns = [
    
    # Upload endpoints
    path('upload/', views.DocumentUploadView.as_view(), name='document-upload'),
    path('upload/multiple/', views.MultipleDocumentUploadView.as_view(), name='multiple-document-upload'),
    
    # Document management
    path('files/', views.DocumentListView.as_view(), name='document-list'),
    path('files/<uuid:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('files/<uuid:pk>/text/', views.DocumentTextView.as_view(), name='document-text'),
    path('files/<uuid:pk>/download/', views.DocumentDownloadView.as_view(), name='document-download'),
    path('files/<uuid:pk>/delete/', views.DocumentDeleteView.as_view(), name='document-delete'),
    
]