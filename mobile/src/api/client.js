import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

// ===============================
// CHANGE THIS TO YOUR BACKEND IP
// ===============================
export const API_BASE_URL = "http://172.20.58.149:8000";
console.log("Using API:", API_BASE_URL);

// Axios Instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

// ========================================
// Automatically attach JWT Token
// ========================================

api.interceptors.request.use(async config => {

  const token = await AsyncStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// ========================================
// LOGIN
// ========================================
export async function login(username, password) {

    console.log("LOGIN START");

    const form = new URLSearchParams();

    form.append("username", username);
    form.append("password", password);

    try {

        const response = await fetch(
            "http://172.20.58.149:8000/api/auth/login",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: form.toString(),
            }
        );

        console.log("STATUS:", response.status);

        const data = await response.json();

        console.log(data);

        return data;

    } catch (e) {

        console.log("FETCH ERROR");

        console.log(e);

        throw e;
    }
}
// ========================================
// LOGOUT
// ========================================

export async function logout() {

  await AsyncStorage.removeItem("access_token");
  await AsyncStorage.removeItem("role");

}

// ========================================
// PRODUCTS
// ========================================

export async function getProducts() {

  try {

    const response = await api.get("/api/products");

    return response.data;

  } catch (error) {

    console.log(error.response?.data);

    throw error;

  }

}

// ========================================
// SUBMIT INSPECTION
// ========================================

export async function submitInspection(productId, imageUri) {

  const form = new FormData();

  form.append("product_id", productId);

  form.append("image", {
    uri: imageUri,
    name: "capture.jpg",
    type: "image/jpeg",
  });

  try {

    const response = await api.post(
      "/api/inspections",
      form,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;

  } catch (error) {

    console.log(error.response?.data);

    throw error;

  }

}

// ========================================
// MY INSPECTIONS
// ========================================

export async function getMyInspections() {

  const response = await api.get("/api/inspections");

  return response.data;

}

// ========================================
// TEST BACKEND CONNECTION
// ========================================

export async function testConnection() {

  try {

    const response = await api.get("/");

    console.log("Backend Connected");

    console.log(response.status);

    return true;

  } catch (error) {

    console.log("Cannot reach backend");

    console.log(error.message);

    return false;

  }

}

// ========================================
// TOKEN
// ========================================

export async function getToken() {

  return await AsyncStorage.getItem("access_token");

}

export default api;