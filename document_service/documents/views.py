import os
import threading
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Document
from .serializers import (
    DocumentSerializer, DocumentUploadSerializer, 
    MultipleDocumentUploadSerializer, DocumentTextSerializer
)
from .utils import DocumentProcessor
import logging

logger = logging.getLogger(__name__)


def process_document_async(document_id):
    """Background task to process document text extraction"""
    try:
        document = Document.objects.get(id=document_id)
        document.processing_status = 'processing'
        document.save()
        
        # Extract text based on file type
        extracted_text = DocumentProcessor.process_document(document)
        
        # Update document with extracted text
        document.extracted_text = extracted_text
        document.processing_status = 'completed'
        document.error_message = None
        document.save()
        
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
    except Exception as e:
        try:
            document = Document.objects.get(id=document_id)
            document.processing_status = 'failed'
            document.error_message = str(e)
            document.save()
        except Document.DoesNotExist:
            pass
        logger.error(f"Error processing document {document_id}: {str(e)}")


class DocumentUploadView(generics.CreateAPIView):
    """Single file upload endpoint"""
    serializer_class = DocumentUploadSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        document = serializer.save()
        # Start background processing
        thread = threading.Thread(target=process_document_async, args=(document.id,))
        thread.daemon = True
        thread.start()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return document info with processing status
        document_serializer = DocumentSerializer(serializer.instance, context={'request': request})
        return Response(document_serializer.data, status=status.HTTP_201_CREATED)


class MultipleDocumentUploadView(generics.CreateAPIView):
    """Multiple files upload endpoint"""
    serializer_class = MultipleDocumentUploadSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        files = serializer.validated_data['files']
        documents = []
        
        for file in files:
            document = Document.objects.create(
                file=file,
                name=file.name
            )
            documents.append(document)
            
            # Start background processing for each document
            thread = threading.Thread(target=process_document_async, args=(document.id,))
            thread.daemon = True
            thread.start()
        
        # Return all uploaded documents
        document_serializer = DocumentSerializer(documents, many=True, context={'request': request})
        return Response(document_serializer.data, status=status.HTTP_201_CREATED)


class DocumentListView(generics.ListAPIView):
    """List all documents with metadata"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        file_type = self.request.query_params.get('type')
        status_filter = self.request.query_params.get('status')
        
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        if status_filter:
            queryset = queryset.filter(processing_status=status_filter)
            
        return queryset


class DocumentDetailView(generics.RetrieveAPIView):
    """Get document details"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentTextView(generics.RetrieveAPIView):
    """Get extracted text from document"""
    queryset = Document.objects.all()
    serializer_class = DocumentTextSerializer


class DocumentDeleteView(generics.DestroyAPIView):
    """Delete document and associated file"""
    queryset = Document.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        
        # Delete physical file
        if document.file and os.path.exists(document.file.path):
            try:
                os.remove(document.file.path)
            except Exception as e:
                logger.error(f"Error deleting file {document.file.path}: {str(e)}")
        
        # Delete database record
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentDownloadView(generics.RetrieveAPIView):
    """Download original document file"""
    queryset = Document.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()
        
        if not document.file or not os.path.exists(document.file.path):
            raise Http404("File not found")
        
        response = FileResponse(
            open(document.file.path, 'rb'),
            as_attachment=True,
            filename=document.name
        )
        return response

