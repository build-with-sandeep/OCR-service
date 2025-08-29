from rest_framework import serializers
from .models import Document
from .utils import validate_file


class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'name', 'file_type', 'file_size', 'file_size_mb',
            'upload_time', 'processing_status', 'extracted_text', 
            'error_message', 'file_url'
        ]
        read_only_fields = ['id', 'file_type', 'file_size', 'upload_time', 
                           'processing_status', 'extracted_text', 'error_message']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2)


class DocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    
    class Meta:
        model = Document
        fields = ['file', 'name']
    
    def validate_file(self, value):
        errors = validate_file(value)
        if errors:
            raise serializers.ValidationError(errors)
        return value
    
    def create(self, validated_data):
        file = validated_data['file']
        if not validated_data.get('name'):
            validated_data['name'] = file.name
        
        return Document.objects.create(**validated_data)


class MultipleDocumentUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        max_length=10
    )
    
    def validate_files(self, value):
        for file in value:
            errors = validate_file(file)
            if errors:
                raise serializers.ValidationError(f"File '{file.name}': {', '.join(errors)}")
        return value


class DocumentTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'extracted_text', 'processing_status', 'error_message']