import { motion, AnimatePresence } from 'framer-motion';
import { useState, useRef } from 'react';
import CloudUploadIcon from '../icons/CloudUploadIcon';

function UploadModal({ isOpen, onClose, onUploadComplete }) {
  const [uploading, setUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    if (files.length > 0) {
      setSelectedFiles(files);
      setError(null);
    }
  };

  const handleStartUpload = async () => {
    if (selectedFiles.length === 0) return;
    
    setUploading(true);
    setError(null);

    // Add all files to processing queue immediately
    const uploadJobs = selectedFiles.map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      file: file,
      status: 'uploading',
      progress: 0,
      uploadedAt: new Date().toISOString(),
    }));

    // Notify parent component about all files being uploaded
    if (onUploadComplete) {
      onUploadComplete(uploadJobs);
    }

    // Close modal immediately after starting uploads
    onClose();
    setSelectedFiles([]);
    setUploading(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) {
      setSelectedFiles(files);
      setError(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };
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
            className="bg-white rounded-lg p-6 w-96 max-w-md"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Upload Documents</h2>
              <button 
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div 
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                accept=".pdf,.doc,.docx"
                className="hidden"
                disabled={uploading}
                multiple
              />
              
              {selectedFiles.length > 0 ? (
                <div>
                  <CloudUploadIcon className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-600 mb-2">{selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} selected</p>
                  <div className="max-h-32 overflow-y-auto mb-4">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="text-sm text-gray-500 py-1">
                        {file.name}
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2 justify-center">
                    <button 
                      onClick={handleStartUpload}
                      className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800"
                      disabled={uploading}
                    >
                      Start Upload
                    </button>
                    <button 
                      onClick={() => setSelectedFiles([])}
                      className="bg-gray-200 text-gray-700 px-6 py-2 rounded hover:bg-gray-300"
                    >
                      Clear
                    </button>
                  </div>
                </div>
              ) : uploading ? (
                <div>
                  <div className="w-12 h-12 mx-auto mb-4">
                    <svg className="animate-spin h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                  <p className="text-gray-600 mb-2">Starting uploads...</p>
                </div>
              ) : (
                <>
                  <CloudUploadIcon className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-600 mb-2">Drop your PDF or Word files here</p>
                  <p className="text-sm text-gray-500 mb-4">or click to browse files</p>
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800"
                  >
                    Select Files
                  </button>
                </>
              )}
            </div>
            
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
                {error}
              </div>
            )}
            
            <p className="text-xs text-gray-500 mt-4">
              Supported formats: PDF, DOC, DOCX • Maximum file size: 10MB per file
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default UploadModal;