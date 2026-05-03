import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axiosInstance";

const AuthContext = createContext(null);

const getHomeForRole = (role) => {
  return role === "customer" ? "/my-chats" : "/dashboard";
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }

    api.get("/auth/me/")
      .then(({ data }) => {
        setUser(data);
        localStorage.setItem("user", JSON.stringify(data));
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    const { data } = await api.post("/auth/login/", { email, password });

    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));

    setUser(data.user);
    navigate(getHomeForRole(data.user.role));

    return data.user;
  }, [navigate]);

  const register = useCallback(async (payload) => {
    const { data } = await api.post("/auth/register/", payload);

    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));

    setUser(data.user);
    navigate(getHomeForRole(data.user.role));

    return data.user;
  }, [navigate]);

  const logout = useCallback(async () => {
    const refresh = localStorage.getItem("refresh_token");

    try {
      if (refresh) {
        await api.post("/auth/logout/", { refresh });
      }
    } catch (_) {
      // best effort logout
    }

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setUser(null);
    navigate("/login");
  }, [navigate]);

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

export function homeForRole(role) {
  return getHomeForRole(role);
}
