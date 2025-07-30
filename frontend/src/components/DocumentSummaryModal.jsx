import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import FilePdfIcon from '../icons/FilePdfIcon';
import { UploadService } from '../services/uploadService';

function DocumentSummaryModal({ isOpen, onClose, document }) {
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && document?.entryId) {
      fetchSummary();
    }
  }, [isOpen, document]);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const summary = await UploadService.getDocumentSummary(document.entryId);
      setSummaryData(summary);
    } catch (err) {
      setError('Failed to load summary');
      console.error('Error fetching summary:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!document) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={onClose}
        >
          <motion.div 
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Document Summary</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-600">Loading summary...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="border border-red-200 rounded-lg p-4 bg-red-50">
              <p className="text-sm text-red-600">{error}</p>
              <button 
                onClick={fetchSummary}
                className="mt-2 text-xs text-red-700 underline hover:no-underline"
              >
                Try again
              </button>
            </div>
          )}

          {!loading && !error && summaryData && (
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <FilePdfIcon className="w-5 h-5" />
                  <div>
                    <p className="font-medium text-sm">{document.filename || document.name}</p>
                    <p className="text-xs text-gray-500">
                      {document.updated_at 
                        ? `Processed on ${new Date(document.updated_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}`
                        : 'Processing completed'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" className="w-5 h-5">
                      <path fill="#6563FF" d="M21.3,10.08A3,3,0,0,0,19,9H14.44L15,7.57A4.13,4.13,0,0,0,11.11,2a1,1,0,0,0-.91.59L7.35,9H5a3,3,0,0,0-3,3v7a3,3,0,0,0,3,3H17.73a3,3,0,0,0,2.95-2.46l1.27-7A3,3,0,0,0,21.3,10.08ZM7,20H5a1,1,0,0,1-1-1V12a1,1,0,0,1,1-1H7Zm13-7.82-1.27,7a1,1,0,0,1-1,.82H9V10.21l2.72-6.12A2.11,2.11,0,0,1,13.1,6.87L12.57,8.3A2,2,0,0,0,14.44,11H19a1,1,0,0,1,.77.36A1,1,0,0,1,20,12.18Z"></path>
                    </svg>
                  </button>
                  <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" className="w-5 h-5">
                      <path fill="#6563FF" d="M19,2H6.27A3,3,0,0,0,3.32,4.46l-1.27,7A3,3,0,0,0,5,15H9.56L9,16.43A4.13,4.13,0,0,0,12.89,22a1,1,0,0,0,.91-.59L16.65,15H19a3,3,0,0,0,3-3V5A3,3,0,0,0,19,2ZM15,13.79l-2.72,6.12a2.13,2.13,0,0,1-1.38-2.78l.53-1.43A2,2,0,0,0,9.56,13H5a1,1,0,0,1-.77-.36A1,1,0,0,1,4,11.82l1.27-7a1,1,0,0,1,1-.82H15ZM20,12a1,1,0,0,1-1,1H17V4h2a1,1,0,0,1,1,1Z"></path>
                    </svg>
                  </button>
                </div>
              </div>
              
              <div className="mb-4">
                <h4 className="font-medium text-sm mb-2">Document Summary</h4>
                <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {summaryData.document_summary}
                </p>
              </div>
              
              <div>
                <h4 className="font-medium text-sm mb-2">Primary Topics</h4>
                <div className="flex flex-wrap gap-2">
                  {summaryData.primary_topics.map((topic, topicIndex) => (
                    <span 
                      key={topicIndex}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
          </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default DocumentSummaryModal;