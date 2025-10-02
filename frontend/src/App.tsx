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
import { Analytics } from "./pages/analytics";
import { Toaster } from "./components/ui/toaster";

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div>
      <nav style={{ padding: "20px", borderBottom: "1px solid #ddd" }}>
        <h2>Scholaria Admin</h2>
      </nav>
      <main>{children}</main>
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
