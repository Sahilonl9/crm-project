import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import Navbar from "./components/Navbar";
import { homeForRole, useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Leads from "./pages/Lead";
import LeadDetail from "./pages/LeadDetail";
import CustomerDashboard from "./pages/CustomerDashboard";
import CustomerChatRoom from "./pages/CustomerChatRoom";

function AppLayout({ children }) {
  return (
    <div className="page-layout">
      <Navbar />
      <main className="page-content">{children}</main>
    </div>
  );
}

function RoleRedirect() {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to={homeForRole(user.role)} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route
          element={
            <RoleRoute allowedRoles={["agent"]} />
          }
        >
          <Route
            path="/dashboard"
            element={
              <AppLayout>
                <Dashboard />
              </AppLayout>
            }
          />
          <Route
            path="/leads"
            element={
              <AppLayout>
                <Leads />
              </AppLayout>
            }
          />
          <Route
            path="/leads/:id"
            element={
              <AppLayout>
                <LeadDetail />
              </AppLayout>
            }
          />
        </Route>

        <Route
          element={
            <RoleRoute allowedRoles={["customer"]} />
          }
        >
          <Route
            path="/my-chats"
            element={
              <AppLayout>
                <CustomerDashboard />
              </AppLayout>
            }
          />
          <Route
            path="/my-chats/:id"
            element={
              <AppLayout>
                <CustomerChatRoom />
              </AppLayout>
            }
          />
        </Route>
      </Route>

      <Route path="*" element={<RoleRedirect />} />
    </Routes>
  );
}
