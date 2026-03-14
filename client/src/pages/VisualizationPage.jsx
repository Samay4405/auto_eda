import React, { useState, useEffect } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  BarChart3,
  Eye,
  Download,
  Grid3X3,
  List,
  Bot,
} from "lucide-react";
import ChartComponent from "../components/ChartComponent";
import DashboardBuilder from "../components/DashboardBuilder";
import LoadingSpinner from "../components/LoadingSpinner";
import toast from "react-hot-toast";

const VisualizationPage = () => {
  const { fileId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [charts, setCharts] = useState([]);
  const [isLoadingCharts, setIsLoadingCharts] = useState(false);
  const [chartLayout, setChartLayout] = useState("grid");
  const [dashboardData, setDashboardData] = useState(null);

  const mode = location.state?.mode || "ai";
  const results = location.state?.results || {};
  const fileData = location.state?.fileData;

  const loadCharts = async () => {
    setIsLoadingCharts(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/charts/${fileId}`
      );
      if (response.ok) {
        const data = await response.json();
        setCharts(data.charts || []);
      }
    } catch (error) {
      console.error("Error loading charts:", error);
      toast.error("Failed to load charts");
    } finally {
      setIsLoadingCharts(false);
    }
  };

  useEffect(() => {
    // Load charts for individual charts tab
    loadCharts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileId]);

  const goBack = () => {
    navigate(`/analysis/${fileId}`, { state: { fileData } });
  };

  const downloadCharts = () => {
    const dataStr = JSON.stringify({ charts, dashboardData }, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `visualization_results_${fileId}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const renderDashboardTab = () => (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-8 shadow-lg">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
            <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
              Smart Dashboard
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              AI-generated consolidated dashboard with relevant insights
            </p>
          </div>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-6">
          <div className="flex items-center space-x-2">
            <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span className="text-blue-800 dark:text-blue-200 font-medium">
              {mode === "ai" ? "AI-Powered Analysis" : "Manual Configuration"}
            </span>
          </div>
          <p className="text-blue-700 dark:text-blue-300 text-sm mt-1">
            This dashboard shows the most important charts and insights for your
            dataset
          </p>
        </div>

        <DashboardBuilder
          fileId={fileId}
          onDashboardGenerated={setDashboardData}
          autoGenerate={true}
        />
      </div>
    </div>
  );

  const renderChartsTab = () => (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-8 shadow-lg">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <Eye className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Individual Charts
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Explore each visualization separately
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setChartLayout("grid")}
              className={`p-2 rounded-lg transition-colors ${
                chartLayout === "grid"
                  ? "bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                  : "text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
              }`}
            >
              <Grid3X3 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setChartLayout("list")}
              className={`p-2 rounded-lg transition-colors ${
                chartLayout === "list"
                  ? "bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                  : "text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {isLoadingCharts ? (
          <LoadingSpinner message="Loading charts..." />
        ) : charts.length === 0 ? (
          <div className="text-center py-12">
            <BarChart3 className="w-16 h-16 text-gray-300 dark:text-gray-700 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-2">
              No charts available
            </p>
            <p className="text-gray-400 dark:text-gray-500 text-sm">
              Charts will be generated automatically during the analysis process
            </p>
          </div>
        ) : (
          <div
            className={`space-y-6 ${
              chartLayout === "grid"
                ? "grid grid-cols-1 lg:grid-cols-2 gap-6"
                : "space-y-6"
            }`}
          >
            {charts.map((chart, index) => (
              <div
                key={index}
                className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {chart.title || `Chart ${index + 1}`}
                  </h4>
                  <span className="text-sm text-gray-500 dark:text-gray-300 bg-gray-200 dark:bg-gray-600 px-3 py-1 rounded-full">
                    {chart.type || "Unknown"}
                  </span>
                </div>
                {chart.description && (
                  <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
                    {chart.description}
                  </p>
                )}
                <ChartComponent chart={chart} className="h-96" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <button
            onClick={goBack}
            className="p-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-all duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Data Visualization
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Explore your data through charts and dashboards
            </p>
          </div>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={downloadCharts}
            className="flex items-center space-x-2 bg-gray-600 dark:bg-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-700 dark:hover:bg-gray-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Mode Indicator */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-6">
        <div className="flex items-center space-x-3">
          <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <span className="font-medium text-gray-900 dark:text-white">
            Analysis Mode:
          </span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              mode === "ai"
                ? "bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200"
                : "bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-200"
            }`}
          >
            {mode === "ai" ? "AI-Powered" : "Manual Configuration"}
          </span>
          {Object.keys(results).length > 0 && (
            <span className="text-gray-500 dark:text-gray-300 text-sm">
              • {Object.keys(results).length} processing step(s) completed
            </span>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === "dashboard"
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600"
            }`}
          >
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>Smart Dashboard</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab("charts")}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === "charts"
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600"
            }`}
          >
            <div className="flex items-center space-x-2">
              <Eye className="w-4 h-4" />
              <span>Individual Charts</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "dashboard" ? renderDashboardTab() : renderChartsTab()}

      {/* Processing Summary */}
      {Object.keys(results).length > 0 && (
        <div className="mt-8 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">
            Processing Summary
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(results).map(([operation, result]) => (
              <div key={operation} className="flex items-center space-x-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    result.error
                      ? "bg-red-500"
                      : result.skipped
                      ? "bg-yellow-500"
                      : "bg-green-500"
                  }`}
                />
                <span className="capitalize text-green-800 dark:text-green-200">
                  {operation}:{" "}
                  {result.skipped
                    ? "Skipped"
                    : result.error
                    ? "Error"
                    : "Completed"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VisualizationPage;
