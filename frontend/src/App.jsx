import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import Sidebar from "./components/Sidebar.jsx";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Inspect from "./pages/Inspect.jsx";
import InspectionHistory from "./pages/InspectionHistory.jsx";
import Reports from "./pages/Reports.jsx";
import Analytics from "./pages/Analytics.jsx";
import Settings from "./pages/Settings.jsx";
import ModelManagement from "./pages/ModelManagement.jsx";

function ProtectedShell({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">{children}</div>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedShell><Dashboard /></ProtectedShell>} />
      <Route path="/inspect" element={<ProtectedShell><Inspect /></ProtectedShell>} />
      <Route path="/history" element={<ProtectedShell><InspectionHistory /></ProtectedShell>} />
      <Route path="/reports" element={<ProtectedShell><Reports /></ProtectedShell>} />
      <Route path="/analytics" element={<ProtectedShell><Analytics /></ProtectedShell>} />
      <Route path="/models" element={<ProtectedShell><ModelManagement /></ProtectedShell>} />
      <Route path="/settings" element={<ProtectedShell><Settings /></ProtectedShell>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
