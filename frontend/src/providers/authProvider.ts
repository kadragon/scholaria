import type { AuthProvider } from "@refinedev/core";

const API_URL = import.meta.env.VITE_API_URL?.replace('/admin', '') || "http://localhost:8001/api";

export const authProvider: AuthProvider = {
  login: async ({ email, password }) => {
    const response = await fetch(`${API_URL}/auth/login`, {
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

    const response = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      return null;
    }

    const user = await response.json();
    return user;
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
