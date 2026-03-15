import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const Spinner: React.FC = () => (
  <div
    className="min-h-screen flex items-center justify-center"
    style={{ backgroundColor: "var(--bg-base)" }}
  >
    <div className="flex flex-col items-center gap-4">
      <div
        className="w-10 h-10 rounded-full border-2 border-violet-500 border-t-transparent animate-spin"
        style={{ boxShadow: "0 0 16px rgba(139,92,246,0.4)" }}
      />
      <p className="text-xs font-semibold uppercase tracking-widest text-gray-600">
        Loading…
      </p>
    </div>
  </div>
);

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuthStore();
  const location = useLocation();

  // While Firebase is resolving the persisted session, show a spinner
  // to avoid a flash of the login page on reload.
  if (loading) return <Spinner />;

  if (!user) {
    // Preserve the intended destination so we can redirect back after login.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
