import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useEffect } from "react";
import { ThemeProvider } from "./contexts/ThemeContext";
import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import UploadPage from "./pages/UploadPage";
import AnalysisPage from "./pages/AnalysisPage";
import ResultsPage from "./pages/ResultsPage";
import DashboardPage from "./pages/DashboardPage";
import VisualizationPage from "./pages/VisualizationPage";
import "./index.css";

function App() {
  // Add cleanup on page unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Call cleanup endpoint when page is being unloaded
      navigator.sendBeacon(
        "http://localhost:8000/api/cleanup-session",
        new FormData()
      );
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  return (
    <ThemeProvider>
      <Router future={{ v7_relativeSplatPath: true }}>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/analysis/:fileId" element={<AnalysisPage />} />
              <Route path="/results/:fileId" element={<ResultsPage />} />
              <Route
                path="/visualization/:fileId"
                element={<VisualizationPage />}
              />
              <Route path="/dashboard" element={<DashboardPage />} />
            </Routes>
          </main>
          <Toaster position="top-right" />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
