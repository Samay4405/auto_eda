import { Link, useLocation } from "react-router-dom";
import {
  BarChart3,
  Upload,
  Home,
  Moon,
  Sun,
  Settings,
  LogOut,
} from "lucide-react";
import { useTheme } from "../contexts/ThemeContext";

const Navbar = () => {
  const location = useLocation();
  const { isDark, toggleTheme } = useTheme();

  const isActive = (path) => {
    return location.pathname === path
      ? "bg-blue-700 dark:bg-blue-800"
      : "hover:bg-blue-700 dark:hover:bg-blue-800";
  };

  const handleClearSession = () => {
    if (
      window.confirm(
        "This will clear all uploaded files and session data. Are you sure?"
      )
    ) {
      // Call the cleanup API endpoint
      fetch("http://localhost:8000/api/cleanup-session", {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            localStorage.clear();
            sessionStorage.clear();
            alert(data.message);
            window.location.reload();
          } else {
            alert("Error clearing session: " + data.message);
            // Still clear local storage
            localStorage.clear();
            sessionStorage.clear();
            window.location.reload();
          }
        })
        .catch((error) => {
          console.error("Error clearing session:", error);
          // Still clear local storage even if API call fails
          localStorage.clear();
          sessionStorage.clear();
          alert("Session data cleared locally");
          window.location.reload();
        });
    }
  };

  return (
    <nav className="bg-blue-600 dark:bg-gray-900 shadow-lg border-b border-blue-700 dark:border-gray-700">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link
            to="/"
            className="flex items-center space-x-2 text-white text-xl font-bold"
          >
            <BarChart3 className="w-8 h-8" />
            <span>Automated EDA</span>
          </Link>

          <div className="flex items-center space-x-4">
            {/* Navigation Links */}
            <div className="flex space-x-1">
              <Link
                to="/"
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-white transition-colors ${isActive(
                  "/"
                )}`}
              >
                <Home className="w-4 h-4" />
                <span>Home</span>
              </Link>

              <Link
                to="/upload"
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-white transition-colors ${isActive(
                  "/upload"
                )}`}
              >
                <Upload className="w-4 h-4" />
                <span>Upload Data</span>
              </Link>
            </div>

            {/* Right side controls */}
            <div className="flex items-center space-x-2 ml-6 pl-6 border-l border-blue-500 dark:border-gray-600">
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-blue-700 dark:bg-gray-800 hover:bg-blue-800 dark:hover:bg-gray-700 transition-colors"
                title={`Switch to ${isDark ? "light" : "dark"} mode`}
              >
                {isDark ? (
                  <Sun className="w-4 h-4 text-yellow-400" />
                ) : (
                  <Moon className="w-4 h-4 text-white" />
                )}
              </button>

              {/* Clear Session */}
              <button
                onClick={handleClearSession}
                className="flex items-center space-x-1 px-3 py-2 bg-red-600 dark:bg-red-700 text-white rounded-lg hover:bg-red-700 dark:hover:bg-red-800 transition-colors"
                title="Clear session and uploaded files"
              >
                <LogOut className="w-4 h-4" />
                <span className="text-sm font-medium hidden sm:block">
                  Clear
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
