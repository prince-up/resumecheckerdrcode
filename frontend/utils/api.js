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
    let resumeText = null;
    
    // Extract resume text from different formats
    if (typeof resumeData === 'string') {
      resumeText = resumeData;
    } else if (resumeData && typeof resumeData === 'object') {
      resumeText = resumeData.optimized_resume || resumeData.resume_text;
    }
    
    if (!resumeText) {
      throw new Error('No resume data available for download');
    }
    
    // Call POST endpoint with resume text
    const response = await axios.post(
      `${API_URL}/download`,
      { resume_text: resumeText },
      { responseType: 'blob', headers: { 'Content-Type': 'application/json' } }
    );
    
    // Create and trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'optimized_resume.pdf');
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Download error:', error);
    throw new Error(error.response?.data?.detail || error.message || 'Failed to download resume');
  }
};

export default apiClient;
