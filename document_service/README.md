# Document Service API

A Django-based REST API service for document management, supporting various file formats including PDF, DOCX, images (JPG/PNG), and text files.

## Project Structure

```
document_service/
├── media/
│   └── uploads/
│       ├── docx/
│       ├── jpg/
│       ├── pdf/
│       ├── png/
│       └── txt/
├── documents/           # Main app
│   ├── views.py
│   ├── models.py
│   ├── urls.py
│   └── ...
└── document_service/    # Project settings
    ├── settings.py
    ├── urls.py
    └── ...
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Tesseract OCR (required for text extraction from images)
- PostgreSQL (optional, SQLite is configured by default)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd document_service
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/MacOS
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver 8000
```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Upload Endpoints

#### Single File Upload

- **URL**: `api/upload/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `name`:optional
  - `file`: The file to upload
  - `file_type`: optional
- **Supported formats**: PDF, DOCX, JPG, PNG, TXT

#### Multiple Files Upload

- **URL**: `api/upload/multiple/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `name`: optional
  - `files`: Multiple files to upload'
- **Supported formats**: PDF, DOCX, JPG, PNG, TXT

### Document Management

#### List All Documents

- **URL**: `api/files/`
- **Method**: `GET`
- **Response**: List of all uploaded documents with metadata

#### Get Document Details

- **URL**: `api/files/<uuid:pk>/`
- **Method**: `GET`
- **Response**: Detailed information about a specific document

#### Get Document Text Content

- **URL**: `api/files/<uuid:pk>/text/`
- **Method**: `GET`
- **Response**: Extracted text content from the document

#### Download Document

- **URL**: `api/files/<uuid:pk>/download/`
- **Method**: `GET`
- **Response**: File download response

#### Delete Document

- **URL**: `api/files/<uuid:pk>/delete/`
- **Method**: `DELETE`
- **Response**: Confirmation of document deletion


## File Storage

Uploaded files are stored in the `media/uploads/` directory, organized by file type:

- PDF files: `media/uploads/pdf/`
- DOCX files: `media/uploads/docx/`
- JPG files: `media/uploads/jpg/`
- PNG files: `media/uploads/png/`
- TXT files: `media/uploads/txt/`

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `201`: Created (successful upload)
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Security Considerations

- The API implements CORS headers for cross-origin requests
- File size limits and type validation are enforced
- Unique UUIDs are used for file identification
