import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to requests if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pharmacy_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercept auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't auto redirect if already on login or checking me
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email, password) => {
    const res = await api.post('/api/auth/login', { email, password });
    return res.data;
  },
  getCurrentUser: async () => {
    const res = await api.get('/api/auth/me');
    return res.data;
  },
};

export const inventoryService = {
  getInventory: async (params = {}) => {
    const res = await api.get('/api/inventory', { params });
    return res.data;
  },
  getBatchDetail: async (inventoryId) => {
    const res = await api.get(`/api/inventory/${inventoryId}`);
    return res.data;
  },
};

export const pharmacyService = {
  getPharmacies: async () => {
    const res = await api.get('/api/pharmacies');
    return res.data;
  },
  getPharmacyDetail: async (pharmacyId) => {
    const res = await api.get(`/api/pharmacies/${pharmacyId}`);
    return res.data;
  },
};

export const medicineService = {
  getMedicines: async (params = {}) => {
    const res = await api.get('/api/medicines', { params });
    return res.data;
  },
};

export const recommendationService = {
  getRecommendations: async (params = {}) => {
    const res = await api.get('/api/recommendations', { params });
    return res.data;
  },
  getDetail: async (recId) => {
    const res = await api.get(`/api/recommendations/${recId}`);
    return res.data;
  },
  approve: async (recId, data = { notes: '', confirmed_high_impact: false }) => {
    const res = await api.post(`/api/recommendations/${recId}/approve`, data);
    return res.data;
  },
  reject: async (recId, data) => {
    const res = await api.post(`/api/recommendations/${recId}/reject`, data);
    return res.data;
  },
  override: async (recId, data) => {
    const res = await api.post(`/api/recommendations/${recId}/override`, data);
    return res.data;
  },
  generate: async (forceRegenerate = false) => {
    const res = await api.post('/api/recommendations/generate', { force_regenerate: forceRegenerate });
    return res.data;
  },
};

export const analyticsService = {
  getDashboardMetrics: async () => {
    const res = await api.get('/api/analytics');
    return res.data;
  },
  getEvaluation: async () => {
    const res = await api.get('/api/evaluation');
    return res.data;
  },
  runEvaluation: async () => {
    const res = await api.post('/api/evaluation/run');
    return res.data;
  },
};

export const auditService = {
  getLogs: async (params = {}) => {
    const res = await api.get('/api/audit-logs', { params });
    return res.data;
  },
};

export const edgeCaseService = {
  getEdgeCases: async () => {
    const res = await api.get('/api/edge-cases');
    return res.data;
  },
};

export const systemService = {
  getHealth: async () => {
    const res = await api.get('/health');
    return res.data;
  },
  reseed: async () => {
    const res = await api.post('/api/seed');
    return res.data;
  },
};

export default api;
