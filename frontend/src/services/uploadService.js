const API_BASE_URL = 'http://localhost:8000';

export class UploadService {
  static async uploadFile(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  static async submitProcessingJob(entryId, s3Location) {
    try {
      const response = await fetch(`${API_BASE_URL}/processing/submit-job`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          entry_id: entryId,
          s3_location: s3Location
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit processing job');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Processing submission error:', error);
      throw error;
    }
  }

  static async getJobStatus(entryId) {
    try {
      const response = await fetch(`${API_BASE_URL}/processing/status/${entryId}`);
      
      if (!response.ok) {
        throw new Error('Failed to get job status');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Status check error:', error);
      throw error;
    }
  }

  static async getDocumentSummary(entryId) {
    try {
      const response = await fetch(`${API_BASE_URL}/processing/summary/${entryId}`);
      
      if (!response.ok) {
        throw new Error('Failed to get document summary');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Summary fetch error:', error);
      throw error;
    }
  }

  static startStatusPolling(entryId, onUpdate, onComplete) {
    const pollInterval = setInterval(async () => {
      try {
        const status = await this.getJobStatus(entryId);
        onUpdate(status);
        
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollInterval);
          onComplete(status);
        }
      } catch (error) {
        console.error('Polling error:', error);
        clearInterval(pollInterval);
      }
    }, 500); // Poll every half second

    return pollInterval;
  }
}