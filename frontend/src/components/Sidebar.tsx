import { Link, useLocation } from "react-router-dom";
import { useLogout } from "@refinedev/core";

export const Sidebar = () => {
  const location = useLocation();
  const { mutate: logout } = useLogout();

  const menuItems = [
    {
      name: "토픽 관리",
      path: "/admin/topics",
      icon: "📚",
    },
    {
      name: "컨텍스트 관리",
      path: "/admin/contexts",
      icon: "📄",
    },
    {
      name: "분석 대시보드",
      path: "/admin/analytics",
      icon: "📊",
    },
  ];

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  return (
    <aside className="w-64 bg-white border-r border-secondary-200 min-h-screen flex flex-col shadow-sm">
      <div className="p-6 border-b border-secondary-200">
        <h2 className="text-xl font-bold text-primary-700">Scholaria</h2>
        <p className="text-xs text-secondary-500 mt-1">관리자 패널</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
              isActive(item.path)
                ? "bg-gradient-to-r from-primary-50 to-primary-100 text-primary-700 font-semibold shadow-sm border border-primary-200"
                : "text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900"
            }`}
          >
            <span className="text-xl">{item.icon}</span>
            <span className="text-sm">{item.name}</span>
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-secondary-200">
        <button
          onClick={() => logout()}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-secondary-600 hover:bg-red-50 hover:text-red-600 transition-all duration-200"
        >
          <span className="text-xl">🚪</span>
          <span>로그아웃</span>
        </button>
      </div>
    </aside>
  );
};
