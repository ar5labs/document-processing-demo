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
                  <button className="flex items-center space-x-1 p-2 text-xs text-blue-800 bg-blue-50 border border-blue-300 rounded-lg hover:bg-blue-100">
                    <span className="font-medium">Export</span>
                  </button>
                  <button className="flex items-center space-x-1 p-2 text-xs text-blue-800 bg-blue-50 border border-blue-300 rounded-lg hover:bg-blue-100">
                    <span className="font-medium">Share</span>
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