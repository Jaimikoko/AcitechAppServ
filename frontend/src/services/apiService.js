/**
 * API Service for AcidTech Financial Dashboard
 * Handles all HTTP requests to Flask backend
 */

class ApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders },
      ...options
    };

    // Add Authorization header if token exists
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      
      // Handle different response types
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || errorData.error || `HTTP ${response.status}`);
      }

      // Check if response has content
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    return this.makeRequest('/health');
  }

  // Authentication endpoints
  async validateToken(token) {
    return this.makeRequest('/auth/validate', {
      method: 'POST',
      body: JSON.stringify({ token })
    });
  }

  async refreshToken(refreshToken) {
    return this.makeRequest('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken })
    });
  }

  async logout() {
    return this.makeRequest('/auth/logout', {
      method: 'POST'
    });
  }

  // Transaction endpoints
  async getTransactions(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    const endpoint = queryParams ? `/transactions?${queryParams}` : '/transactions';
    return this.makeRequest(endpoint);
  }

  async getTransaction(id) {
    return this.makeRequest(`/transactions/${id}`);
  }

  async createTransaction(transactionData) {
    return this.makeRequest('/transactions', {
      method: 'POST',
      body: JSON.stringify(transactionData)
    });
  }

  async getTransactionSummary() {
    return this.makeRequest('/transactions/summary');
  }

  // Purchase Order endpoints
  async getPurchaseOrders(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    const endpoint = queryParams ? `/purchase-orders?${queryParams}` : '/purchase-orders';
    return this.makeRequest(endpoint);
  }

  async getPurchaseOrder(id) {
    return this.makeRequest(`/purchase-orders/${id}`);
  }

  async createPurchaseOrder(poData) {
    return this.makeRequest('/purchase-orders', {
      method: 'POST',
      body: JSON.stringify(poData)
    });
  }

  async uploadReceipt(file, poId = null) {
    const formData = new FormData();
    formData.append('file', file);
    if (poId) formData.append('purchase_order_id', poId);

    return this.makeRequest('/purchase-orders/upload-receipt', {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json'
        // Don't set Content-Type for FormData
      }
    });
  }

  // System Logs endpoints
  async getSystemLogs(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    const endpoint = queryParams ? `/system-logs?${queryParams}` : '/system-logs';
    return this.makeRequest(endpoint);
  }

  async getLogEntry(id) {
    return this.makeRequest(`/system-logs/${id}`);
  }

  async getLogStatistics() {
    return this.makeRequest('/system-logs/stats');
  }

  // Dashboard/Analytics endpoints
  async getDashboardData() {
    try {
      const [transactions, purchaseOrders, logs] = await Promise.all([
        this.getTransactionSummary(),
        this.getPurchaseOrders({ limit: 5 }),
        this.getLogStatistics()
      ]);

      return {
        transactions,
        purchaseOrders,
        logs,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      throw error;
    }
  }

  // Utility methods
  setAuthToken(token) {
    if (token) {
      localStorage.setItem('accessToken', token);
    } else {
      localStorage.removeItem('accessToken');
    }
  }

  getAuthToken() {
    return localStorage.getItem('accessToken');
  }

  clearAuthToken() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  // Error handling helper
  handleApiError(error) {
    if (error.message.includes('401')) {
      // Unauthorized - clear tokens and redirect to login
      this.clearAuthToken();
      window.location.href = '/login';
      return;
    }

    if (error.message.includes('403')) {
      // Forbidden - user doesn't have permission
      console.error('Access denied:', error);
      return;
    }

    if (error.message.includes('500')) {
      // Server error
      console.error('Server error:', error);
      return;
    }

    // Generic error handling
    console.error('API Error:', error);
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;