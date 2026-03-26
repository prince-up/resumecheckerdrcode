import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export const analyzeResume = async (formData) => {
  try {
    const response = await apiClient.post('/analyze', formData);
    return response.data.data;
  } catch (error) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error(error.message || 'Failed to analyze resume');
  }
};

export const downloadResume = async (resumeData) => {
  try {
    // If we have resume data directly, create PDF from it
    if (resumeData && typeof resumeData === 'string') {
      // Call backend to generate PDF
      const response = await axios.post(`${API_URL}/download`, 
        { resume_text: resumeData },
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'optimized_resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } else {
      // Try GET endpoint
      const response = await axios.get(`${API_URL}/download`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'optimized_resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
  } catch (error) {
    console.error('Download error:', error);
    throw new Error(error.response?.data?.detail || 'Failed to download resume');
  }
};

export default apiClient;
