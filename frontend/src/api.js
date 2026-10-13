// Enhanced API utility with proper error handling
import { API_BASE_URL } from './config';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Get auth headers
  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Generic request method with comprehensive error handling
  async request(method, endpoint, data = null) {
    const url = `${this.baseURL}${endpoint}`;
    
    console.log(`🔄 API ${method} ${endpoint}`);
    
    try {
      const config = {
        method,
        headers: this.getAuthHeaders(),
        credentials: 'include'
      };

      if (data && (method === 'POST' || method === 'PUT')) {
        config.body = JSON.stringify(data);
      }

      const response = await fetch(url, config);
      
      console.log(`📡 Response status: ${response.status}`);

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error(`Server returned non-JSON response: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 401) {
          console.warn('🔐 Authentication failed, clearing session');
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          throw new Error('Authentication failed. Please login again.');
        }
        
        throw new Error(result.error || result.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      console.log(`✅ API ${method} ${endpoint} success`);
      return result;

    } catch (error) {
      console.error(`❌ API ${method} ${endpoint} failed:`, error);
      
      // Network error handling
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error. Please check your connection and try again.');
      }
      
      // Re-throw the error for the caller to handle
      throw error;
    }
  }

  // Convenience methods
  async get(endpoint) {
    return this.request('GET', endpoint);
  }

  async post(endpoint, data) {
    return this.request('POST', endpoint, data);
  }

  async put(endpoint, data) {
    return this.request('PUT', endpoint, data);
  }

  async delete(endpoint) {
    return this.request('DELETE', endpoint);
  }

  // Health check method
  async healthCheck() {
    try {
      const result = await this.get('/api/health');
      console.log('🏥 Backend health check passed:', result);
      return true;
    } catch (error) {
      console.error('🏥 Backend health check failed:', error);
      return false;
    }
  }
}

// Create and export a singleton instance
const apiClient = new ApiClient();

export default apiClient;

// Export specific API methods for common operations
export const api = {
  // Authentication
  login: (credentials) => apiClient.post('/api/auth/login', credentials),
  register: (userData) => apiClient.post('/api/auth/register', userData),
  logout: () => apiClient.post('/api/auth/logout'),

  // Dashboard
  getDashboard: () => apiClient.get('/api/dashboard'),
  getUserProfile: () => apiClient.get('/api/user/profile'),

  // Quiz and Assessment
  getQuizQuestions: (domain = 'programming') => apiClient.get(`/api/quiz/questions?domain=${domain}`),
  submitQuiz: (quizData) => apiClient.post('/api/quiz/submit', quizData),
  getAssessmentStatus: () => apiClient.get('/api/user/assessment-status'),

  // Roadmap
  getRoadmap: () => apiClient.get('/api/roadmap'),
  getTopicDetails: (topicId) => apiClient.get(`/api/roadmap/topic/${topicId}`),
  completeRoadmapTopic: (topicId) => apiClient.post(`/api/roadmap/topic/${topicId}/complete`),

  // Code execution
  runCode: (topicId, codeData) => apiClient.post(`/api/topic/${topicId}/run-code`, codeData),

  // Profile management
  updateProfileLinks: (profileLinks) => apiClient.post('/api/profile/update_links', profileLinks),
  getProfileProgress: () => apiClient.get('/api/profile/progress'),
  syncProgress: () => apiClient.post('/api/profile/sync-progress'),
  updateAvatar: (avatar) => apiClient.post('/api/profile/update_avatar', { avatar }),
  getUserBadges: () => apiClient.get('/api/profile/badges'),
  
  // Enhanced progress tracking
  getProgressInsights: () => apiClient.get('/api/profile/progress-insights'),
  getRecentActivity: () => apiClient.get('/api/profile/recent-activity'),
  getMLAnalysis: () => apiClient.get('/api/profile/ml-progress-analysis'),
  enableAutoSync: () => apiClient.post('/api/profile/enable-auto-sync'),

  // Health check
  healthCheck: () => apiClient.healthCheck()
};