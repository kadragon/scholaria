import dataProvider from "@refinedev/simple-rest";
import axios from "axios";
import type { DataProvider } from "@refinedev/core";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api/admin";

const axiosInstance = axios.create();

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const baseDataProvider = dataProvider(API_URL, axiosInstance);

export const adminDataProvider: DataProvider = {
  ...baseDataProvider,
  getList: async ({ resource, pagination, filters, sorters, meta }) => {
    const response = await baseDataProvider.getList({
      resource,
      pagination,
      filters,
      sorters,
      meta,
    });

    // Transform response if it has { data: [], total: N } structure
    if (response.data && typeof response.data === 'object' && 'data' in response.data) {
      return {
        data: (response.data as any).data,
        total: (response.data as any).total || 0,
      };
    }

    return response;
  },
};
