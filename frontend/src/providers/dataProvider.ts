import dataProvider from "@refinedev/simple-rest";
import axios from "axios";
import type { DataProvider, BaseRecord, GetListParams } from "@refinedev/core";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8001/api/admin";

const axiosInstance = axios.create();

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/admin/login";
    }
    return Promise.reject(error);
  },
);

const baseDataProvider = dataProvider(API_URL, axiosInstance);

export const adminDataProvider: DataProvider = {
  ...baseDataProvider,
  getList: async <TData extends BaseRecord = BaseRecord>({
    resource,
    pagination,
    filters,
    sorters,
    meta,
  }: GetListParams) => {
    const response = await baseDataProvider.getList<TData>({
      resource,
      pagination,
      filters,
      sorters,
      meta,
    });

    // Transform response if it has { data: [], total: N } structure
    if (
      response.data &&
      typeof response.data === "object" &&
      "data" in response.data
    ) {
      const responseData = response.data as unknown as {
        data: TData[];
        total?: number;
      };
      return {
        data: responseData.data,
        total: responseData.total || 0,
      };
    }

    return response;
  },
} as DataProvider;
