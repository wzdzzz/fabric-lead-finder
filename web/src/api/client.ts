import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;

// Auth
export const login = (username: string, password: string) =>
  api.post('/auth/login', { username, password });

// Config
export const getKeywords = () => api.get('/config/keywords');
export const getRegions = () => api.get('/config/regions');

// Tasks
export const createTask = (keywords: string[], regions: string[]) =>
  api.post('/tasks', { keywords, regions });
export const getTasks = (page = 1, pageSize = 20) =>
  api.get('/tasks', { params: { page, page_size: pageSize } });
export const getTask = (id: number) => api.get(`/tasks/${id}`);

// Leads
export const getLeads = (params: Record<string, string | number>) =>
  api.get('/leads', { params });
export const updateLead = (id: number, data: Record<string, unknown>) =>
  api.put(`/leads/${id}`, data);
export const batchUpdateLeads = (data: Record<string, unknown>) =>
  api.put('/leads/batch', data);
export const getAllTags = () => api.get('/leads/tags');
export const getLeadStats = () => api.get('/leads/stats');

// Export
export const exportExcel = (params: Record<string, string>) =>
  api.post('/export', params, { responseType: 'blob' });

// Amap Keys
export const getAmapKeys = () => api.get('/amap-keys');
export const addAmapKey = (data: { key: string; name?: string; monthly_limit?: number }) =>
  api.post('/amap-keys', data);
export const updateAmapKey = (id: number, data: { name?: string; monthly_limit?: number; used_count?: number }) =>
  api.put(`/amap-keys/${id}`, data);
export const activateAmapKey = (id: number) => api.put(`/amap-keys/${id}/activate`);
export const deleteAmapKey = (id: number) => api.delete(`/amap-keys/${id}`);
