import { Refine, Authenticated } from "@refinedev/core";
import routerBindings, {
  CatchAllNavigate,
  NavigateToResource,
} from "@refinedev/react-router-v6";
import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import { authProvider } from "./providers/authProvider";
import { adminDataProvider } from "./providers/dataProvider";
import { TopicList } from "./pages/topics/list";
import { TopicCreate } from "./pages/topics/create";
import { TopicEdit } from "./pages/topics/edit";
import { ContextList } from "./pages/contexts/list";
import { ContextCreate } from "./pages/contexts/create";
import { ContextEdit } from "./pages/contexts/edit";
import { ContextShow } from "./pages/contexts/show";
import { LoginPage } from "./pages/login";
import { SetupPage } from "./pages/setup";
import { Analytics } from "./pages/analytics";
import { ChatPage } from "./pages/chat";
import { Toaster } from "./components/ui/toaster";
import { Sidebar } from "./components/Sidebar";

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex min-h-screen bg-secondary-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
      <Toaster />
    </div>
  );
};

function App() {
  const basename = import.meta.env.VITE_BASE_PATH || "/admin/";

  return (
    <BrowserRouter basename={basename}>
      <Refine
        dataProvider={adminDataProvider}
        authProvider={authProvider}
        routerProvider={routerBindings}
        resources={[
          {
            name: "topics",
            list: "/topics",
            create: "/topics/create",
            edit: "/topics/edit/:id",
          },
          {
            name: "contexts",
            list: "/contexts",
            create: "/contexts/create",
            edit: "/contexts/edit/:id",
            show: "/contexts/show/:id",
          },
        ]}
      >
        <Routes>
          <Route path="/setup" element={<SetupPage />} />
          <Route
            element={
              <Authenticated
                key="authenticated-routes"
                fallback={<CatchAllNavigate to="/login" />}
              >
                <Layout>
                  <Outlet />
                </Layout>
              </Authenticated>
            }
          >
            <Route index element={<NavigateToResource resource="topics" />} />
            <Route path="/topics">
              <Route index element={<TopicList />} />
              <Route path="create" element={<TopicCreate />} />
              <Route path="edit/:id" element={<TopicEdit />} />
            </Route>
            <Route path="/contexts">
              <Route index element={<ContextList />} />
              <Route path="create" element={<ContextCreate />} />
              <Route path="edit/:id" element={<ContextEdit />} />
              <Route path="show/:id" element={<ContextShow />} />
            </Route>
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/chat" element={<ChatPage />} />
          </Route>
          <Route
            element={
              <Authenticated key="unauthenticated-routes" fallback={<Outlet />}>
                <NavigateToResource />
              </Authenticated>
            }
          >
            <Route path="/login" element={<LoginPage />} />
          </Route>
        </Routes>
      </Refine>
    </BrowserRouter>
  );
}

export default App;
