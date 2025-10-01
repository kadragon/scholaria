import dataProvider from "@refinedev/simple-rest";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api/admin";

const axiosInstance = axios.create();

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const adminDataProvider = dataProvider(API_URL, axiosInstance);
