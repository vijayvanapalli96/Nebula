import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

const LandingPage        = lazy(() => import("./pages/LandingPage"));
const DashboardPage      = lazy(() => import("./pages/DashboardPage"));
const StoryCreationPage  = lazy(() => import("./pages/StoryCreationPage"));
const StoryGeneratingPage = lazy(() => import("./pages/StoryGeneratingPage"));
const StoryScenePage     = lazy(() => import("./pages/StoryScenePage"));
const StoryGraphPage     = lazy(() => import("./pages/StoryGraphPage"));
const StoryPage          = lazy(() => import("./pages/StoryPage"));
const ComingSoonPage     = lazy(() => import("./pages/ComingSoonPage"));

const Spinner: React.FC = () => (
  <div
    className="min-h-screen flex items-center justify-center"
    style={{ backgroundColor: "var(--bg-base)" }}
  >
    <div className="w-8 h-8 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
  </div>
);

const App: React.FC = () => (
  <BrowserRouter>
    <Suspense fallback={<Spinner />}>
      <Routes>
        {/* -- Public / Marketing -- */}
        <Route path="/"          element={<LandingPage />} />

        {/* -- Dashboard -- */}
        <Route path="/dashboard"                  element={<DashboardPage />} />
        <Route path="/dashboard/stories"          element={<ComingSoonPage />} />
        <Route path="/dashboard/explore"          element={<ComingSoonPage />} />
        <Route path="/dashboard/favorites"        element={<ComingSoonPage />} />
        <Route path="/dashboard/achievements"     element={<ComingSoonPage />} />
        <Route path="/dashboard/settings"         element={<ComingSoonPage />} />

        {/* -- Story creation -- */}
        <Route path="/story/create"      element={<StoryCreationPage />} />
        <Route path="/story/generating"  element={<StoryGeneratingPage />} />
        <Route path="/story/scene"       element={<StoryScenePage />} />
        <Route path="/story/graph"       element={<StoryGraphPage />} />

        {/* -- Story player -- */}
        <Route path="/story/:storyId" element={<StoryPage />} />

        {/* -- Fallback -- */}
        <Route path="*" element={<LandingPage />} />
      </Routes>
    </Suspense>
  </BrowserRouter>
);

export default App;
