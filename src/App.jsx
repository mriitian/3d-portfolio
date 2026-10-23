import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Landing from "./pages/Landing";
import Classic from "./pages/Classic";
import useMediaQuery from "./hooks/useMediaQuery";
import { SMALL_SCREEN_QUERY } from "./game/device";

// the 3D world is only downloaded when someone chooses to play
const Play = lazy(() => import("./pages/Play"));

// small screens never get the 3D world, so they never even download it
const PlayRoute = () => {
  const isSmall = useMediaQuery(SMALL_SCREEN_QUERY);
  if (isSmall) return <Navigate to="/classic" replace />;

  return (
    <Suspense fallback={<div className="min-h-screen bg-primary" />}>
      <Play />
    </Suspense>
  );
};

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/classic" element={<Classic />} />
        <Route path="/play" element={<PlayRoute />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
