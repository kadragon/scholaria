import { useState, useEffect } from "react";
import { useLogin } from "@refinedev/core";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

export const LoginPage = () => {
  const { mutate: login, isLoading } = useLogin();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    checkSetupStatus();
  }, []);

  const checkSetupStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/setup/check`);
      if (response.data.needs_setup) {
        navigate("/setup");
      }
    } catch (err) {
      console.error("Setup check failed:", err);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login({ email, password });
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-primary-50 via-secondary-50 to-accent-50">
      <div className="bg-white p-10 rounded-lg shadow-xl w-full max-w-md border border-secondary-200">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-700 mb-2">
            Scholaria Admin
          </h1>
          <p className="text-secondary-500 text-sm">관리자 로그인</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              이메일
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 text-base border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="admin@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              비밀번호
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 text-base border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 text-base font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 disabled:from-secondary-400 disabled:to-secondary-500 rounded-md shadow-md hover:shadow-lg transition-all duration-200 disabled:cursor-not-allowed"
          >
            {isLoading ? "로그인 중..." : "로그인"}
          </button>
        </form>
      </div>
    </div>
  );
};
