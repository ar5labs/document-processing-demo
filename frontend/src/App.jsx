import { useState } from 'react';
import './App.css';
import Navbar from './components/Navbar';
import UploadModal from './components/UploadModal';
import { UploadService } from './services/uploadService';
import Processing from './components/Processing';

function App() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [documents, setDocuments] = useState([]);

  const handleUploadComplete = (uploadJobs) => {
    // Add all uploaded documents to the processing queue with "uploading" status
    setDocuments(prev => [...prev, ...uploadJobs.map(job => ({
      ...job,
      status: 'uploading',
      processingProgress: 0,
      statusMessage: 'Uploading file to processing server',
      entryId: null
    }))]);
    
    // Start upload for each file
    uploadJobs.forEach(async (job) => {
      try {
        // Upload file
        const uploadResult = await UploadService.uploadFile(job.file);
        
        // Update document with entry_id
        setDocuments(prevDocs => 
          prevDocs.map(doc => 
            doc.id === job.id 
              ? { 
                  ...doc, 
                  entryId: uploadResult.entry_id,
                  status: 'queued',
                  statusMessage: 'Submitting to processing queue'
                }
              : doc
          )
        );

        // Submit processing job
        await UploadService.submitProcessingJob(uploadResult.entry_id, uploadResult.location);
        
        // Start status polling
        UploadService.startStatusPolling(
          uploadResult.entry_id,
          (status) => {
            // Update progress
            setDocuments(prevDocs => 
              prevDocs.map(doc => 
                doc.entryId === uploadResult.entry_id 
                  ? { 
                      ...doc, 
                      status: status.status,
                      processingProgress: status.progress,
                      statusMessage: status.status === 'processing' ? 'Processing' : status.status,
                      updated_at: status.updated_at,
                      created_at: status.created_at
                    }
                  : doc
              )
            );
          },
          (finalStatus) => {
            // Final status update
            setDocuments(prevDocs => 
              prevDocs.map(doc => 
                doc.entryId === uploadResult.entry_id 
                  ? { 
                      ...doc, 
                      status: finalStatus.status,
                      processingProgress: finalStatus.progress,
                      statusMessage: finalStatus.status === 'completed' 
                        ? 'Document successfully processed and ready for viewing'
                        : 'Processing failed',
                      updated_at: finalStatus.updated_at,
                      created_at: finalStatus.created_at
                    }
                  : doc
              )
            );
          }
        );
        
      } catch (error) {
        // Mark as failed if upload fails
        setDocuments(prevDocs => 
          prevDocs.map(doc => 
            doc.id === job.id 
              ? { 
                  ...doc, 
                  status: 'failed', 
                  statusMessage: `Upload failed: ${error.message}`
                }
              : doc
          )
        );
      }
    });
  };


  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onUploadClick={() => setIsUploadModalOpen(true)} />

      {/* Main Content */}
      <main className="max-w-6xl mx-auto p-6">
        {/* Processing Queue */}
        <section>
          <Processing documents={documents} />
        </section>
      </main>

      {/* Upload Modal */}
      <UploadModal 
        isOpen={isUploadModalOpen} 
        onClose={() => setIsUploadModalOpen(false)}
        onUploadComplete={handleUploadComplete}
      />
    </div>
  );
}

export default App;
