import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large file processing
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(
      `Making ${config.method?.toUpperCase()} request to ${config.url}`
    );
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Upload file
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  // Get file information
  getFileInfo: async (fileId) => {
    const response = await api.get(`/api/file/${fileId}/info`);
    return response.data;
  },

  // Process data
  processData: async (fileId, operation, mode, options = {}) => {
    const formData = new FormData();
    formData.append("file_id", fileId);
    formData.append("operation", operation);
    formData.append("mode", mode);
    formData.append("options", JSON.stringify(options));

    const response = await api.post("/api/process", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  // Get charts
  getCharts: async (fileId, chartTypes = null) => {
    const params = chartTypes ? { chart_types: chartTypes } : {};
    const response = await api.get(`/api/charts/${fileId}`, { params });
    return response.data;
  },

  // Get AI insights
  getInsights: async (fileId) => {
    const response = await api.get(`/api/insights/${fileId}`);
    return response.data;
  },

  // Delete file
  deleteFile: async (fileId) => {
    const response = await api.delete(`/api/file/${fileId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get("/health");
    return response.data;
  },
};

export default api;
