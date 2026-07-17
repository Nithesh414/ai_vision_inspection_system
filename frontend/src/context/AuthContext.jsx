import { createContext, useContext, useState } from "react";
import { login as apiLogin, logout as apiLogout } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");
    const username = localStorage.getItem("username");
    return token ? { token, role, username } : null;
  });

  async function login(username, password) {
    const data = await apiLogin(username, password);
    setUser({ token: data.access_token, role: data.role, username: data.username });
  }

  function logout() {
    apiLogout();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
