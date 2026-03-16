import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuthStore } from "./store/authStore";

const LandingPage         = lazy(() => import("./pages/LandingPage"));
const LoginPage           = lazy(() => import("./pages/LoginPage"));
const SignupPage          = lazy(() => import("./pages/SignupPage"));
const DashboardPage       = lazy(() => import("./pages/DashboardPage"));
const StoryCreationPage   = lazy(() => import("./pages/StoryCreationPage"));
const StoryGeneratingPage = lazy(() => import("./pages/StoryGeneratingPage"));
const StoryScenePage      = lazy(() => import("./pages/StoryScenePage"));
const StoryGraphPage      = lazy(() => import("./pages/StoryGraphPage"));
const StoryPage           = lazy(() => import("./pages/StoryPage"));
const ComingSoonPage      = lazy(() => import("./pages/ComingSoonPage"));
const SettingsPage        = lazy(() => import("./pages/SettingsPage"));
const ThemeLoadingPage    = lazy(() => import("./pages/ThemeLoadingPage"));
const ExploreThemesPage   = lazy(() => import("./pages/ExploreThemesPage"));
const MyStoriesPage       = lazy(() => import("./pages/MyStoriesPage"));

const Spinner: React.FC = () => (
  <div
    className="min-h-screen flex items-center justify-center"
    style={{ backgroundColor: "var(--bg-base)" }}
  >
    <div
      className="w-8 h-8 rounded-full border-2 border-violet-500 border-t-transparent animate-spin"
      style={{ boxShadow: "0 0 16px rgba(139,92,246,0.4)" }}
    />
  </div>
);

/** Redirect already-authenticated users away from /login and /signup */
const GuestRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuthStore();
  if (loading) return <Spinner />;
  if (user) return <Navigate to="/loading" replace />;
  return <>{children}</>;
};

const App: React.FC = () => (
  <BrowserRouter>
    <Suspense fallback={<Spinner />}>
      <Routes>
        {/* -- Public / Marketing -- */}
        <Route path="/" element={<LandingPage />} />

        {/* -- Auth (guest-only) -- */}
        <Route path="/login"  element={<GuestRoute><LoginPage /></GuestRoute>} />
        <Route path="/signup" element={<GuestRoute><SignupPage /></GuestRoute>} />

        {/* -- Theme loading (post-auth) -- */}
        <Route path="/loading" element={<ProtectedRoute><ThemeLoadingPage /></ProtectedRoute>} />

        {/* -- Explore all worlds -- */}
        <Route path="/explore" element={<ProtectedRoute><ExploreThemesPage /></ProtectedRoute>} />

        {/* -- Protected: Dashboard -- */}
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/dashboard/stories"      element={<ProtectedRoute><ComingSoonPage /></ProtectedRoute>} />
        <Route path="/dashboard/achievements" element={<ProtectedRoute><ComingSoonPage /></ProtectedRoute>} />
        <Route path="/dashboard/settings"     element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />

        {/* -- My Stories -- */}
        <Route path="/my-stories" element={<ProtectedRoute><MyStoriesPage /></ProtectedRoute>} />

        {/* -- Protected: Story creation -- */}
        <Route path="/story/create"     element={<ProtectedRoute><StoryCreationPage /></ProtectedRoute>} />
        <Route path="/story/generating" element={<ProtectedRoute><StoryGeneratingPage /></ProtectedRoute>} />
        <Route path="/story/scene"      element={<ProtectedRoute><StoryScenePage /></ProtectedRoute>} />
        <Route path="/story/graph"      element={<ProtectedRoute><StoryGraphPage /></ProtectedRoute>} />

        {/* -- Protected: Story player -- */}
        <Route path="/story/:storyId" element={<ProtectedRoute><StoryPage /></ProtectedRoute>} />

        {/* -- Fallback -- */}
        <Route path="*" element={<LandingPage />} />
      </Routes>
    </Suspense>
  </BrowserRouter>
);

export default App;
