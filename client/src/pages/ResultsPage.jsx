/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable no-unused-vars */
import { useState, useEffect } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Download,
  BarChart,
  Bot,
  CheckCircle,
  AlertCircle,
  Grid3X3,
  List,
  Eye,
  TrendingUp,
} from "lucide-react";
import ChartComponent from "../components/ChartComponent";
import LoadingSpinner from "../components/LoadingSpinner";
import toast from "react-hot-toast";

const ResultsPage = () => {
  const { fileId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState(location.state?.results || null);
  const [charts, setCharts] = useState([]);
  const [insights, setInsights] = useState(null);
  const [isLoadingCharts, setIsLoadingCharts] = useState(false);
  const [isLoadingInsights, setIsLoadingInsights] = useState(false);
  const [activeTab, setActiveTab] = useState("results");
  const [chartLayout, setChartLayout] = useState("grid"); // grid or list

  const fileData = location.state?.fileData;
  const operationData = location.state?.operationData;

  useEffect(() => {
    if (results) {
      // If results contain charts, set them
      if (results.charts) {
        setCharts(results.charts);
      }

      // If results contain insights, set them
      if (results.insights) {
        setInsights(results.insights);
      }

      // Load additional charts for visualization
      if (operationData?.operation === "visualize" || !results.charts) {
        loadCharts();
      }

      // Load AI insights if not already present
      if (!results.insights && operationData?.mode === "ai") {
        loadInsights();
      }
    }
  }, [results, operationData]);

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

  const loadInsights = async () => {
    setIsLoadingInsights(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/insights/${fileId}`
      );
      if (response.ok) {
        const data = await response.json();
        setInsights(data.insights);
      }
    } catch (error) {
      console.error("Error loading insights:", error);
      toast.error("Failed to load AI insights");
    } finally {
      setIsLoadingInsights(false);
    }
  };

  const downloadResults = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `eda_results_${fileId}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const goBack = () => {
    navigate(`/analysis/${fileId}`, { state: { fileData } });
  };

  const goHome = () => {
    navigate("/");
  };

  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Eye className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-4 text-lg">No results found</p>
          <button onClick={goHome} className="btn-primary">
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const renderOperationResults = () => {
    if (!results) return null;

    const operation = operationData?.operation || "unknown";

    switch (operation) {
      case "clean":
        return (
          <div className="space-y-6">
            {results.cleaning_summary && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800">
                    Cleaning Summary
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-blue-600 font-medium mb-1">
                      Original Shape
                    </p>
                    <p className="text-2xl font-bold text-blue-800">
                      {results.cleaning_summary.original_shape?.[0]?.toLocaleString()} ×{" "}
                      {results.cleaning_summary.original_shape?.[1]}
                    </p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <p className="text-sm text-green-600 font-medium mb-1">
                      Cleaned Shape
                    </p>
                    <p className="text-2xl font-bold text-green-800">
                      {results.cleaning_summary.cleaned_shape?.[0]?.toLocaleString()} ×{" "}
                      {results.cleaning_summary.cleaned_shape?.[1]}
                    </p>
                  </div>
                  <div className="bg-red-50 rounded-lg p-4">
                    <p className="text-sm text-red-600 font-medium mb-1">
                      Rows Removed
                    </p>
                    <p className="text-2xl font-bold text-red-800">
                      {results.cleaning_summary.rows_removed?.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {results.operations_performed && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <h3 className="text-xl font-semibold mb-4 text-gray-800">
                  Operations Performed
                </h3>
                <div className="space-y-3">
                  {results.operations_performed.map((op, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg"
                    >
                      <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                      <span className="text-gray-700">{op}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case "transform":
        return (
          <div className="space-y-6">
            {results.transformation_summary && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800">
                    Transformation Summary
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 font-medium mb-1">
                      Original Columns
                    </p>
                    <p className="text-2xl font-bold text-gray-800">
                      {results.transformation_summary.original_columns}
                    </p>
                  </div>
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-blue-600 font-medium mb-1">
                      Transformed Columns
                    </p>
                    <p className="text-2xl font-bold text-blue-800">
                      {results.transformation_summary.transformed_columns}
                    </p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <p className="text-sm text-green-600 font-medium mb-1">
                      Features Added
                    </p>
                    <p className="text-2xl font-bold text-green-800">
                      +{results.transformation_summary.features_added}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {results.new_columns && results.new_columns.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <h3 className="text-xl font-semibold mb-4 text-gray-800">
                  New Columns Created
                </h3>
                <div className="flex flex-wrap gap-3">
                  {results.new_columns.map((col, index) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 rounded-full text-sm font-medium"
                    >
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case "classify":
        return (
          <div className="space-y-6">
            {results.data_quality && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <h3 className="text-xl font-semibold mb-6 text-gray-800">
                  Data Quality Assessment
                </h3>

                <div className="flex items-center justify-center mb-6">
                  <div className="relative">
                    <svg className="w-32 h-32" viewBox="0 0 120 120">
                      <circle
                        cx="60"
                        cy="60"
                        r="54"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="8"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="54"
                        fill="none"
                        stroke={
                          results.data_quality.score >= 80
                            ? "#10b981"
                            : results.data_quality.score >= 60
                            ? "#f59e0b"
                            : "#ef4444"
                        }
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={`${(results.data_quality.score / 100) * 339} 339`}
                        transform="rotate(-90 60 60)"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-gray-800">
                          {Math.round(results.data_quality.score)}%
                        </div>
                        <div className="text-sm text-gray-600">Quality Score</div>
                      </div>
                    </div>
                  </div>
                </div>

                {results.data_quality.issues &&
                  results.data_quality.issues.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3 text-gray-800">
                        Issues Found:
                      </h4>
                      <div className="space-y-2">
                        {results.data_quality.issues.map((issue, index) => (
                          <div
                            key={index}
                            className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg"
                          >
                            <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
                            <span className="text-gray-700">{issue}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
              </div>
            )}

            {results.column_types && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <h3 className="text-xl font-semibold mb-6 text-gray-800">
                  Column Analysis
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Column
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Unique Values
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Missing %
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {Object.entries(results.column_types).map(
                        ([column, info]) => (
                          <tr key={column} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {column}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <span
                                className={`px-3 py-1 rounded-full text-xs font-medium ${
                                  info.category === "numerical"
                                    ? "bg-blue-100 text-blue-800"
                                    : info.category === "categorical"
                                    ? "bg-green-100 text-green-800"
                                    : "bg-gray-100 text-gray-800"
                                }`}
                              >
                                {info.category}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {info.unique_count?.toLocaleString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {Math.round(info.null_percentage * 100) / 100}%
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        );

      default:
        return (
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">
              Processing Results
            </h3>
            <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto text-gray-700">
              {JSON.stringify(results, null, 2)}
            </pre>
          </div>
        );
    }
  };

  const tabs = [
    {
      id: "results",
      label: "Results",
      icon: <CheckCircle className="w-4 h-4" />,
      count: results ? 1 : 0,
    },
    {
      id: "charts",
      label: "Visualizations",
      icon: <BarChart className="w-4 h-4" />,
      count: charts.length,
    },
    {
      id: "insights",
      label: "AI Insights",
      icon: <Bot className="w-4 h-4" />,
      count: insights ? Object.keys(insights).length : 0,
    },
  ];

  return (
    <div className="max-w-7xl mx-auto min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={goBack}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Analysis Results
              </h1>
              <p className="text-gray-600">
                {operationData?.operation} • {operationData?.mode} mode
              </p>
            </div>
          </div>

          <button
            onClick={downloadResults}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download Results</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 px-6">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.count > 0 && (
                <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === "results" && (
          <div className="fade-in">{renderOperationResults()}</div>
        )}

        {activeTab === "charts" && (
          <div className="fade-in">
            {isLoadingCharts ? (
              <LoadingSpinner message="Loading visualizations..." />
            ) : charts.length > 0 ? (
              <>
                {/* Chart Layout Controls */}
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-800">
                    Data Visualizations ({charts.length})
                  </h2>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setChartLayout("grid")}
                      className={`p-2 rounded-lg transition-colors ${
                        chartLayout === "grid"
                          ? "bg-blue-100 text-blue-600"
                          : "text-gray-500 hover:bg-gray-100"
                      }`}
                      title="Grid View"
                    >
                      <Grid3X3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setChartLayout("list")}
                      className={`p-2 rounded-lg transition-colors ${
                        chartLayout === "list"
                          ? "bg-blue-100 text-blue-600"
                          : "text-gray-500 hover:bg-gray-100"
                      }`}
                      title="List View"
                    >
                      <List className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Charts Grid/List */}
                <div
                  className={
                    chartLayout === "grid"
                      ? "grid grid-cols-1 lg:grid-cols-2 gap-6"
                      : "space-y-6"
                  }
                >
                  {charts.map((chart, index) => (
                    <ChartComponent
                      key={`${chart.id}-${index}`}
                      chart={chart}
                      className={
                        chartLayout === "list" ? "max-w-4xl mx-auto" : ""
                      }
                    />
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-16">
                <BarChart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-4 text-lg">
                  No visualizations available
                </p>
                <button onClick={loadCharts} className="btn-primary">
                  Generate Charts
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === "insights" && (
          <div className="fade-in">
            {isLoadingInsights ? (
              <LoadingSpinner message="Generating AI insights..." />
            ) : insights ? (
              <div className="space-y-6">
                {Object.entries(insights).map(([key, value]) => (
                  <div
                    key={key}
                    className="bg-white rounded-xl shadow-lg border border-gray-200 p-6"
                  >
                    <h3 className="text-xl font-semibold mb-4 text-gray-800 capitalize">
                      {key.replace(/_/g, " ")}
                    </h3>
                    <div className="text-gray-700">
                      {Array.isArray(value) ? (
                        <ul className="space-y-3">
                          {value.map((item, index) => (
                            <li key={index} className="flex items-start space-x-3">
                              <span className="text-blue-500 mt-1 text-lg">•</span>
                              <span className="leading-relaxed">{item}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="leading-relaxed">{value}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16">
                <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-4 text-lg">
                  No AI insights available
                </p>
                <button onClick={loadInsights} className="btn-primary">
                  Generate Insights
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPage;
