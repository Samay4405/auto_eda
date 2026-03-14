import React, { useState, useEffect } from "react";
import {
  AlertCircle,
  BarChart3,
  Download,
  Eye,
  RefreshCw,
  Settings,
  Sparkles,
  TrendingUp,
  Database,
  Clock,
  FileText,
} from "lucide-react";
import toast from "react-hot-toast";

const DashboardBuilder = ({ fileId, onDashboardGenerated }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [dashboard, setDashboard] = useState(null);
  const [dataProfile, setDataProfile] = useState(null);
  const [selectedType, setSelectedType] = useState("interactive");
  const [businessContext, setBusinessContext] = useState("");

  const dashboardTypes = {
    interactive: {
      name: "Interactive Dashboard",
      description: "Power BI/Tableau-style dashboard with dynamic filters",
      icon: <Settings className="w-5 h-5" />,
      color: "purple",
      badge: "RECOMMENDED",
    },
    auto: {
      name: "AI Auto-Detect",
      description: "Let AI choose the optimal dashboard layout",
      icon: <Sparkles className="w-5 h-5" />,
      color: "blue",
      badge: null,
    },
    executive_summary: {
      name: "Executive Summary",
      description: "High-level overview with key business metrics",
      icon: <TrendingUp className="w-5 h-5" />,
      color: "green",
      badge: null,
    },
    data_quality: {
      name: "Data Quality Report",
      description: "Comprehensive data quality and health assessment",
      icon: <AlertCircle className="w-5 h-5" />,
      color: "orange",
      badge: null,
    },
    exploratory: {
      name: "Exploratory Analysis",
      description: "Detailed statistical analysis and visualizations",
      icon: <Eye className="w-5 h-5" />,
      color: "indigo",
      badge: null,
    },
  };

  useEffect(() => {
    if (fileId) {
      fetchDataProfile();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileId]);

  const fetchDataProfile = async () => {
    try {
      const formData = new FormData();
      formData.append("file_id", fileId);

      const response = await fetch(
        "http://localhost:8000/api/dashboard/analyze-requirements",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      if (data.success) {
        setDataProfile(data);
      }
    } catch (error) {
      console.error("Failed to fetch data profile:", error);
      toast.error("Failed to analyze dataset");
    }
  };

  const generateDashboard = async (useAutoGenerate = false) => {
    if (!fileId) return;

    setIsGenerating(true);
    try {
      const formData = new FormData();
      formData.append("file_id", fileId);

      let response;

      // Use LangGraph dashboard generation for all types (AI-powered, no templates)
      if (
        selectedType === "interactive" ||
        selectedType === "exploratory" ||
        selectedType === "executive" ||
        selectedType === "data_quality"
      ) {
        // Map types
        const dashboardTypeMap = {
          interactive: "exploratory",
          exploratory: "exploratory",
          executive: "executive",
          data_quality: "data_quality",
          auto: "exploratory",
        };

        formData.append(
          "dashboard_type",
          dashboardTypeMap[selectedType] || "exploratory"
        );
        formData.append(
          "user_context",
          businessContext || "Generate a comprehensive dashboard"
        );
        formData.append("target_audience", "analyst");

        response = await fetch(
          "http://localhost:8000/api/langgraph/dashboard/generate",
          {
            method: "POST",
            body: formData,
          }
        );
      } else if (useAutoGenerate) {
        if (businessContext) {
          formData.append("business_context", businessContext);
        }
        response = await fetch(
          "http://localhost:8000/api/dashboard/auto-generate",
          {
            method: "POST",
            body: formData,
          }
        );
      } else {
        // Default to LangGraph for any other type
        formData.append("dashboard_type", selectedType);
        formData.append("user_context", businessContext || "");
        formData.append("target_audience", "analyst");

        response = await fetch(
          "http://localhost:8000/api/langgraph/dashboard/generate",
          {
            method: "POST",
            body: formData,
          }
        );
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      if (data.success) {
        setDashboard(data.dashboard);
        if (onDashboardGenerated) {
          onDashboardGenerated(data.dashboard);
        }

        // Show success message based on dashboard type
        if (selectedType === "interactive") {
          toast.success("Interactive dashboard generated successfully! 🎛️");
        } else {
          toast.success("Dashboard generated successfully!");
        }
      } else {
        throw new Error(data.error || "Failed to generate dashboard");
      }
    } catch (error) {
      console.error("Dashboard generation failed:", error);
      toast.error("Failed to generate dashboard: " + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const exportDashboard = (format = "html") => {
    if (!dashboard) return;

    try {
      const content =
        format === "html" ? dashboard.html : JSON.stringify(dashboard, null, 2);
      const blob = new Blob([content], {
        type: format === "html" ? "text/html" : "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `dashboard-${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success(`Dashboard exported as ${format.toUpperCase()}`);
    } catch (error) {
      console.error("Export failed:", error);
      toast.error("Export failed: " + error.message);
    }
  };

  const openDashboardInNewTab = () => {
    if (!dashboard) return;
    const newWindow = window.open();
    newWindow.document.write(dashboard.html);
    newWindow.document.close();
  };

  const getColorClasses = (color) => {
    const colorMap = {
      purple:
        "border-purple-500 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300",
      blue: "border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300",
      green:
        "border-green-500 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300",
      orange:
        "border-orange-500 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300",
      indigo:
        "border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300",
    };
    return colorMap[color] || colorMap.blue;
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-700 dark:to-purple-700 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">Dashboard Builder</h1>
        <p className="text-blue-100">
          Generate intelligent dashboards with AI-powered insights from your
          data
        </p>
      </div>

      {/* Data Profile Summary */}
      {dataProfile && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-gray-900 dark:text-white">
            <Database className="w-5 h-5" />
            Dataset Overview
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {dataProfile.dataset_info?.shape?.[0]?.toLocaleString() ||
                  "N/A"}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Rows
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {dataProfile.dataset_info?.shape?.[1] || "N/A"}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Columns
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {dataProfile.dataset_info?.columns?.filter(
                  (col) =>
                    dataProfile.dataset_info?.data_types?.[col]?.includes(
                      "int"
                    ) ||
                    dataProfile.dataset_info?.data_types?.[col]?.includes(
                      "float"
                    )
                ).length || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Numeric
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                {dataProfile.dataset_info?.columns?.filter((col) =>
                  dataProfile.dataset_info?.data_types?.[col]?.includes(
                    "object"
                  )
                ).length || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Categorical
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dashboard Type Selection */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-gray-900 dark:text-white">
          <Settings className="w-5 h-5" />
          Select Dashboard Type
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Business Context (Optional)
            </label>
            <textarea
              value={businessContext}
              onChange={(e) => setBusinessContext(e.target.value)}
              placeholder="e.g., Sales analysis, Customer research, Quality assessment..."
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(dashboardTypes).map(([type, info]) => (
              <label
                key={type}
                className={`relative cursor-pointer transition-all duration-200 ${
                  selectedType === type
                    ? `border-2 ${getColorClasses(
                        info.color
                      )} shadow-lg scale-105`
                    : "border-2 border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md"
                } rounded-lg p-4`}
              >
                <input
                  type="radio"
                  name="dashboardType"
                  value={type}
                  checked={selectedType === type}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="sr-only"
                />

                {info.badge && (
                  <div className="absolute -top-2 -right-2 bg-purple-600 text-white text-xs px-2 py-1 rounded-full font-bold">
                    {info.badge}
                  </div>
                )}

                <div className="flex items-start gap-3">
                  <div
                    className={`flex-shrink-0 p-2 rounded-lg ${
                      selectedType === type
                        ? "bg-white dark:bg-gray-800"
                        : `bg-${info.color}-100 dark:bg-${info.color}-900/30`
                    }`}
                  >
                    {info.icon}
                  </div>
                  <div>
                    <h3
                      className={`font-semibold ${
                        selectedType === type
                          ? ""
                          : "text-gray-900 dark:text-white"
                      }`}
                    >
                      {info.name}
                    </h3>
                    <p
                      className={`text-sm mt-1 ${
                        selectedType === type
                          ? ""
                          : "text-gray-600 dark:text-gray-400"
                      }`}
                    >
                      {info.description}
                    </p>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex justify-center">
        <button
          onClick={() => generateDashboard(selectedType === "auto")}
          disabled={!fileId || isGenerating}
          className="flex items-center gap-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          {isGenerating ? (
            <RefreshCw className="w-6 h-6 animate-spin" />
          ) : (
            <Sparkles className="w-6 h-6" />
          )}
          {isGenerating ? "Generating Dashboard..." : "Generate Dashboard"}
        </button>
      </div>

      {/* Dashboard Display */}
      {dashboard && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2 text-gray-900 dark:text-white">
              <BarChart3 className="w-5 h-5" />
              Generated Dashboard
            </h2>

            <div className="flex gap-3">
              <button
                onClick={() => exportDashboard("html")}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Download className="w-4 h-4" />
                Export HTML
              </button>
              <button
                onClick={openDashboardInNewTab}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Eye className="w-4 h-4" />
                Open in New Tab
              </button>
            </div>
          </div>

          {/* Dashboard Metadata */}
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="text-center">
                <div className="font-medium text-gray-900 dark:text-white">
                  Type
                </div>
                <div className="text-gray-600 dark:text-gray-400 capitalize">
                  {dashboard.type?.replace("_", " ")}
                </div>
              </div>
              <div className="text-center">
                <div className="font-medium text-gray-900 dark:text-white">
                  Generated
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  {dashboard.metadata?.generated_at
                    ? new Date(dashboard.metadata.generated_at).toLocaleString()
                    : "Just now"}
                </div>
              </div>
              <div className="text-center">
                <div className="font-medium text-gray-900 dark:text-white">
                  Dataset
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  {dashboard.metadata?.dataset_shape
                    ? `${dashboard.metadata.dataset_shape[0]} × ${dashboard.metadata.dataset_shape[1]}`
                    : "N/A"}
                </div>
              </div>
              <div className="text-center">
                <div className="font-medium text-gray-900 dark:text-white">
                  Charts
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  {dashboard.charts_count || "Multiple"}
                </div>
              </div>
            </div>
          </div>

          {/* Dashboard Preview */}
          <div className="border-2 border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden bg-white">
            <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 border-b border-gray-200 dark:border-gray-600">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="ml-4 text-sm text-gray-600 dark:text-gray-400">
                  Dashboard Preview
                </span>
              </div>
            </div>
            <div className="p-4">
              <iframe
                srcDoc={dashboard.html}
                className="w-full h-96 border-0 rounded"
                title="Dashboard Preview"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardBuilder;
