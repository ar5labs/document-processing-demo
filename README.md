# Document Processing Demo

A full-stack document processing application that uses AI to analyze Word documents, extract semantic information, and generate comprehensive summaries. The system processes documents through intelligent chunking, semantic analysis, and produces structured metadata for enhanced retrieval and understanding.

## Overview

This application provides:
- Word document upload and storage using AWS S3 (or LocalStack for development)
- Asynchronous document processing with Celery workers
- AI-powered semantic analysis and summarization using OpenAI
- Real-time processing status updates
- RESTful API built with FastAPI
- React-based frontend with real-time progress tracking

## Backend Architecture

The backend follows a microservices architecture with the following components:

### Core Services

1. **API Service** (`src/api/`)
   - FastAPI application handling HTTP requests
   - Endpoints for file upload, processing job submission, and status monitoring
   - CORS-enabled for frontend integration

2. **Worker Service** (`src/worker/`)
   - Celery-based asynchronous task processing
   - Handles CPU-intensive document processing tasks
   - Scalable worker pool for concurrent processing

3. **Storage Services**
   - **S3 Service**: Manages document storage in AWS S3/LocalStack
   - **Database Service**: JSON-based file storage for document metadata and processing results
   - **Redis**: Message broker for Celery task queue

### Processing Pipeline

1. **Document Upload**: Word files are uploaded to S3 and metadata is stored
2. **Chunk Extraction**: Documents are split into manageable chunks using configurable size and overlap
3. **Semantic Analysis**: Each chunk is processed to extract:
   - Topics and themes
   - Named entities
   - Key concepts
   - Semantic relationships
   - Use cases
   - Search queries
   - Knowledge graph edges
4. **Summary Generation**: Chunk summaries are aggregated into a comprehensive document summary

### Key Technologies

- **FastAPI**: Modern Python web framework for building APIs
- **Celery**: Distributed task queue for asynchronous processing
- **Redis**: In-memory data store used as message broker
- **AWS S3/LocalStack**: Object storage for documents
- **OpenAI API**: Powers the AI analysis and summarization
- **python-docx**: Word document text extraction
- **LangChain**: Text splitting and document processing utilities

## System Prompts

The application uses two sophisticated system prompts for AI-powered analysis:

### 1. Document Chunk Analysis Prompt

Located in `backend/src/prompts/system_prompts.py:1-139`

This prompt instructs the AI to analyze individual document chunks and extract:

- **Summary**: Concise 1-2 sentence description of the chunk
- **Topics**: High-level subjects (e.g., "hurricane response", "data privacy")
- **Entities**: Named entities like people, organizations, places
- **Concepts**: Abstract or domain-specific concepts
- **Relationships**: Semantic triples (subject-relation-object)
- **Use Cases**: Scenarios where the chunk information is relevant
- **Search Queries**: Example queries that would retrieve this chunk
- **Graph Edges**: Knowledge graph relationships

The output is structured JSON that enables semantic search and knowledge graph construction.

### 2. Document Summary Generation Prompt

Located in `backend/src/prompts/system_prompts.py:142-246`

This prompt aggregates chunk-level summaries into a comprehensive executive summary including:

- **Purpose/Objective**: Why the document was written
- **Main Ideas**: Primary arguments, findings, or conclusions
- **Key Supporting Points**: Important evidence or arguments
- **Outcomes/Conclusions**: Final takeaways and recommendations
- **Tone and Context**: Document style and intended audience

The summary is structured with multiple paragraphs and bullet points for clarity.

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 16+
- OpenAI API key

### Backend Setup

1. Clone the repository
2. Set up environment variables in `docker-compose.dev.yml`:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `S3_BUCKET_NAME`: S3 bucket name (default: document-processing-bucket)
   - `AWS_REGION`: AWS region (default: us-east-1)

3. Start the backend services:
```bash
cd backend
docker-compose -f docker-compose.dev.yml up
```

This starts:
- Redis on port 6379
- LocalStack (S3) on port 4566
- API service on port 8000
- Worker service with auto-reload

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000

## API Endpoints

- `POST /upload/`: Upload a Word document
- `POST /processing/submit-job`: Submit a processing job
- `GET /processing/status/{entry_id}`: Get job status
- `GET /processing/summary/{entry_id}`: Get document summary
- `GET /health`: Health check endpoint

## Configuration

### Environment Variables

- `REDIS_URL`: Redis connection URL
- `AWS_ENDPOINT_URL`: S3 endpoint (LocalStack for development)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `S3_BUCKET_NAME`: S3 bucket for document storage
- `OPENAI_API_KEY`: OpenAI API key for AI processing

### Processing Configuration

- **Chunk Size**: 25,000 characters (configurable in `processing_service.py`)
- **Chunk Overlap**: 500 characters to maintain context
- **Concurrent Processing**: 10 chunks processed simultaneously
- **Worker Concurrency**: 4 Celery workers by default

## Document Format Support

Currently supports:
- Word documents (.docx)

## Architecture Decisions

1. **Asynchronous Processing**: Long-running document analysis tasks are handled asynchronously to maintain API responsiveness
2. **Chunking Strategy**: Large documents are split into chunks to handle API token limits and enable parallel processing
3. **JSON File Storage**: Simple JSON-based storage for development; can be replaced with a proper database for production
4. **Semantic Analysis**: Rich metadata extraction enables advanced search and knowledge graph capabilities
5. **Progress Tracking**: Real-time progress updates through polling provide user feedback during processing

## Future Enhancements

- Support for additional document formats (PDF, Excel, etc.)
- PostgreSQL or MongoDB for production data storage
- Enhanced authentication and authorization
- Batch processing capabilities
- Export functionality for analysis results
- Integration with vector databases for semantic search
