import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("role");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export async function login(username, password) {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);
  const { data } = await api.post("/api/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("role", data.role);
  localStorage.setItem("username", data.username);
  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("role");
  localStorage.removeItem("username");
}

export async function getDashboardSummary() {
  const { data } = await api.get("/api/analytics/dashboard");
  return data;
}

export async function getTrends(days = 30) {
  const { data } = await api.get(`/api/analytics/trends?days=${days}`);
  return data;
}

export async function getInspections(statusFilter) {
  const { data } = await api.get("/api/inspections", { params: { status_filter: statusFilter } });
  return data;
}

export async function getProducts() {
  const { data } = await api.get("/api/products");
  return data;
}

export async function createInspection(productId, imageFile) {
  const form = new FormData();
  form.append("product_id", productId);
  form.append("image", imageFile);
  const { data } = await api.post("/api/inspections", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
