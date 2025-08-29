from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_type', 'file_size_display', 'processing_status', 'upload_time']
    list_filter = ['file_type', 'processing_status', 'upload_time']
    search_fields = ['name', 'extracted_text']
    readonly_fields = ['id', 'file_size', 'upload_time', 'extracted_text']
    
    def file_size_display(self, obj):
        return f"{obj.file_size / (1024*1024):.2f} MB"
    file_size_display.short_description = 'File Size'