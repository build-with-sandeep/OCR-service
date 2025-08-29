import os
import pytesseract
from PIL import Image
import PyPDF2
from docx import Document as DocxDocument
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Configure tesseract path
if hasattr(settings, 'TESSERACT_CMD'):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


class DocumentProcessor:
    """Utility class for processing different document types"""
    
    @staticmethod
    def extract_text_from_image(file_path):
        """Extract text from image files using Tesseract OCR"""
        try:
            image = Image.open(file_path)
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from image {file_path}: {str(e)}")
            raise Exception(f"OCR processing failed: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF files"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            raise Exception(f"PDF processing failed: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX files"""
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            raise Exception(f"DOCX processing failed: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_path):
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read().strip()
            except Exception as e:
                logger.error(f"Error extracting text from TXT {file_path}: {str(e)}")
                raise Exception(f"TXT processing failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting text from TXT {file_path}: {str(e)}")
            raise Exception(f"TXT processing failed: {str(e)}")
    
    @classmethod
    def process_document(cls, document):
        """Main method to process document based on file type"""
        file_path = document.file.path
        file_type = document.file_type.lower()
        
        try:
            if file_type == 'pdf':
                return cls.extract_text_from_pdf(file_path)
            elif file_type == 'docx':
                return cls.extract_text_from_docx(file_path)
            elif file_type == 'txt':
                return cls.extract_text_from_txt(file_path)
            elif file_type in ['jpg', 'jpeg', 'png']:
                return cls.extract_text_from_image(file_path)
            else:
                raise Exception(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            raise


def validate_file(file):
    """Validate uploaded file size and type"""
    errors = []
    
    # Check file size
    if file.size > settings.MAX_FILE_SIZE:
        errors.append(f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB")
    
    # Check file type
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_FILE_TYPES:
        errors.append(f"File type '{file_extension}' not allowed. Supported types: {', '.join(settings.ALLOWED_FILE_TYPES)}")
    
    return errors