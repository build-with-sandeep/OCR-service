import os
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings


def upload_to(instance, filename):
    """Generate upload path with organized folder structure"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(settings.UPLOAD_PATH, instance.file_type, filename)


class Document(models.Model):
    FILE_TYPES = (
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('txt', 'Text File'),
        ('jpg', 'JPEG Image'),
        ('jpeg', 'JPEG Image'),
        ('png', 'PNG Image'),
    )
    
    PROCESSING_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(
        upload_to=upload_to,
        validators=[FileExtensionValidator(allowed_extensions=settings.ALLOWED_FILE_TYPES)]
    )
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.PositiveIntegerField()
    upload_time = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='pending')
    extracted_text = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-upload_time']
        
    def __str__(self):
        return f"{self.name} ({self.file_type})"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            # Get file type from the actual file name, not the document name
            self.file_type = self.file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)