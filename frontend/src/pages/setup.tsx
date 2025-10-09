import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useToast } from "@/hooks/use-toast";

const API_URL =
  import.meta.env.VITE_API_URL?.replace("/admin", "") ||
  "http://localhost:8001/api";

interface SetupCheckResponse {
  needs_setup: boolean;
  admin_exists: boolean;
}

export const SetupPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [checking, setChecking] = useState(true);

  const checkSetupStatus = useCallback(async () => {
    try {
      const response = await axios.get<SetupCheckResponse>(
        `${API_URL}/setup/check`,
      );
      if (!response.data.needs_setup) {
        navigate("/login");
      }
    } catch (err) {
      console.error("Setup check failed:", err);
    } finally {
      setChecking(false);
    }
  }, [navigate]);

  useEffect(() => {
    checkSetupStatus();
  }, [checkSetupStatus]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }

    if (password.length < 8) {
      setError("비밀번호는 최소 8자 이상이어야 합니다.");
      return;
    }

    setIsLoading(true);

    try {
      await axios.post(`${API_URL}/setup/init`, {
        username,
        email,
        password,
      });

      toast({
        title: "계정 생성 성공",
        description:
          "관리자 계정이 생성되었습니다. 로그인 페이지로 이동합니다.",
      });
      navigate("/login");
    } catch (err: unknown) {
      const errorMessage =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "계정 생성에 실패했습니다.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (checking) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg text-secondary-600">확인 중...</div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-primary-50 via-secondary-50 to-accent-50">
      <div className="bg-white p-10 rounded-lg shadow-xl w-full max-w-md border border-secondary-200">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-700 mb-2">
            초기 설정
          </h1>
          <p className="text-secondary-500 text-sm">
            첫 관리자 계정을 생성하세요
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              사용자명
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              className="w-full px-4 py-3 text-base border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="admin"
            />
          </div>

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
              placeholder="admin@scholaria.com"
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
              minLength={8}
              className="w-full px-4 py-3 text-base border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
            <p className="mt-1 text-xs text-secondary-500">
              최소 8자 이상 입력하세요
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              비밀번호 확인
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
              className="w-full px-4 py-3 text-base border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 text-base font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 disabled:from-secondary-400 disabled:to-secondary-500 rounded-md shadow-md hover:shadow-lg transition-all duration-200 disabled:cursor-not-allowed"
          >
            {isLoading ? "생성 중..." : "관리자 계정 생성"}
          </button>
        </form>
      </div>
    </div>
  );
};
