import { Navigate, Outlet } from "react-router-dom";
import { homeForRole, useAuth } from "../context/AuthContext";

export default function RoleRoute({ allowedRoles }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to={homeForRole(user.role)} replace />;
  }

  return <Outlet />;
}
