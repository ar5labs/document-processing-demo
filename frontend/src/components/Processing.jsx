import { useState } from 'react';
import FilePdfIcon from '../icons/FilePdfIcon';
import EyeIcon from '../icons/EyeIcon';
import InfoCircleIcon from '../icons/InfoCircleIcon';
import DocumentSummaryModal from './DocumentSummaryModal';
import '../styles/progress.css';

function Processing({ documents = [] }) {
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleViewSummary = (item) => {
    setSelectedDocument(item);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedDocument(null);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const processingItems = documents.map(doc => ({
    id: doc.id,
    entryId: doc.entryId,
    name: doc.name,
    size: formatFileSize(doc.file?.size || 0),
    processingProgress: doc.processingProgress || 0,
    status: doc.status === 'uploading' ? 'Uploading' : 
            doc.status === 'processing' ? 'Processing' :
            doc.status === 'completed' ? 'Completed' : 
            doc.status === 'failed' ? 'Failed' : 
            doc.status === 'queued' ? 'Queued' : 'Processing',
    statusMessage: doc.statusMessage || 'Processing document',
    updated_at: doc.updated_at,
    created_at: doc.created_at
  }));

  const getStatusAlert = (status, statusMessage) => {
    const alertConfigs = {
      "Completed": {
        bgColor: "bg-green-50",
        textColor: "text-green-800",
        borderColor: "border-green-300",
        iconColor: "text-green-800"
      },
      "Processing": {
        bgColor: "bg-blue-50",
        textColor: "text-blue-800", 
        borderColor: "border-blue-300",
        iconColor: "text-blue-800"
      },
      "Uploading": {
        bgColor: "bg-blue-50",
        textColor: "text-blue-800",
        borderColor: "border-blue-300", 
        iconColor: "text-blue-800"
      },
      "Starting": {
        bgColor: "bg-yellow-50",
        textColor: "text-yellow-800",
        borderColor: "border-yellow-300",
        iconColor: "text-yellow-800"
      },
      "Queued": {
        bgColor: "bg-yellow-50",
        textColor: "text-yellow-800",
        borderColor: "border-yellow-300",
        iconColor: "text-yellow-800"
      },
      "Failed": {
        bgColor: "bg-red-50",
        textColor: "text-red-800",
        borderColor: "border-red-300",
        iconColor: "text-red-800"
      }
    };

    const config = alertConfigs[status] || alertConfigs["Queued"];
    
    return (
      <div className={`flex items-center p-2 text-xs ${config.textColor} border ${config.borderColor} rounded-lg ${config.bgColor}`} role="alert">
        <div className="relative group">
          <InfoCircleIcon className={`shrink-0 inline w-4 h-4 me-2 ${config.iconColor}`} />
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
            {statusMessage}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
        <span className="font-medium">{status}</span>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-semibold mb-4">Processing Queue</h2>
      
      <div className="space-y-4">
        {processingItems.map((item, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                <FilePdfIcon className="w-5 h-5" />
                <div>
                  <p className="font-medium text-sm">{item.name}</p>
                  <p className="text-xs text-gray-500">{item.size}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusAlert(item.status, item.statusMessage)}
                {item.status === "Completed" && (
                  <button 
                    onClick={() => handleViewSummary(item)}
                    className="flex items-center space-x-1 p-2 text-xs text-blue-800 bg-blue-50 border border-blue-300 rounded-lg hover:bg-blue-100"
                  >
                    <EyeIcon className="w-4 h-4 text-blue-800" />
                    <span className="font-medium">View Summary</span>
                  </button>
                )}
              </div>
            </div>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Processing Progress</span>
                  <span>{item.processingProgress}%</span>
                </div>
                <div className={`progress ${item.processingProgress < 100 && item.status !== 'Failed' ? 'progress-striped active' : ''}`}>
                  <div 
                    className={`progress-bar ${
                      item.status === 'Failed' ? 'progress-bar-danger' :
                      item.processingProgress === 100 ? 'progress-bar-success' : 
                      'progress-bar-primary'
                    }`}
                    style={{ width: `${item.processingProgress}%` }}
                  >
                    <span>{item.processingProgress}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <DocumentSummaryModal 
        isOpen={isModalOpen}
        onClose={closeModal}
        document={selectedDocument}
      />
    </div>
  );
}

export default Processing;