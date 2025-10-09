import type { AuthProvider } from "@refinedev/core";
import { apiClient } from "../lib/apiClient";
import { API_BASE_URL } from "../lib/apiConfig";

export const authProvider: AuthProvider = {
  login: async ({ email, password }) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }),
    });

    if (!response.ok) {
      return {
        success: false,
        error: {
          name: "LoginError",
          message: "Invalid credentials",
        },
      };
    }

    const { access_token } = await response.json();
    localStorage.setItem("token", access_token);

    return {
      success: true,
      redirectTo: "/admin",
    };
  },

  logout: async () => {
    localStorage.removeItem("token");
    return {
      success: true,
      redirectTo: "/admin/login",
    };
  },

  check: async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      return {
        authenticated: false,
        redirectTo: "/admin/login",
      };
    }

    return {
      authenticated: true,
    };
  },

  getIdentity: async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      return null;
    }

    try {
      const response = await apiClient.get("/auth/me");
      return response.data;
    } catch {
      return null;
    }
  },

  onError: async (error) => {
    if (error.status === 401 || error.status === 403) {
      return {
        logout: true,
        redirectTo: "/admin/login",
        error,
      };
    }

    return { error };
  },
};
