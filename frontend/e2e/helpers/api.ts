export const getApiBaseUrl = () => {
  return (
    process.env.VITE_API_URL?.replace("/api", "") || "http://localhost:8001"
  );
};

export const getApiUrl = (path: string) => {
  const baseUrl = getApiBaseUrl();
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${baseUrl}${cleanPath}`;
};
