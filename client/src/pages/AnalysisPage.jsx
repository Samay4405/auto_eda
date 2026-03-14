import { useState, useEffect } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { FileText, ArrowLeft, BarChart3 } from "lucide-react";
import StepByStepAnalysis from "../components/StepByStepAnalysis";
import LoadingSpinner from "../components/LoadingSpinner";
import toast from "react-hot-toast";

const AnalysisPage = () => {
  const { fileId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [fileData] = useState(location.state?.fileData || null);
  const [fileInfo, setFileInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchFileInfo = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `http://localhost:8000/api/file/${fileId}/info`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch file information");
        }
        const data = await response.json();
        setFileInfo(data);
      } catch (error) {
        console.error("Error fetching file info:", error);
        toast.error("Failed to load file information");
        navigate("/upload");
      } finally {
        setIsLoading(false);
      }
    };

    if (!fileData && fileId) {
      // Fetch file info if not provided via navigation state
      fetchFileInfo();
    } else if (fileData) {
      setFileInfo(fileData);
    }
  }, [fileId, fileData, navigate]);

  const handleAnalysisComplete = (results) => {
    // Navigate to the new visualization page
    navigate(`/visualization/${fileId}`, {
      state: {
        mode: results.mode,
        results: results.results,
        fileData: fileInfo,
      },
    });
  };

  const goBack = () => {
    navigate("/upload");
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading file information..." />;
  }

  if (!fileInfo) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500 mb-4">File not found</p>
        <button onClick={goBack} className="btn-primary">
          Back to Upload
        </button>
      </div>
    );
  }

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
              Step-by-Step Analysis
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Follow our guided workflow to analyze your data
            </p>
          </div>
        </div>
      </div>

      {/* File Information Summary */}
      <div className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl p-8 mb-8 shadow-lg">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
            <FileText className="w-6 h-6 text-blue-500 dark:text-blue-400" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Dataset Overview
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span>File Details</span>
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  Name:
                </span>
                <span className="text-gray-900 dark:text-white font-mono text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                  {fileInfo.filename}
                </span>
              </div>
              <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  Rows:
                </span>
                <span className="text-gray-900 dark:text-white font-semibold">
                  {fileInfo.shape?.[0]?.toLocaleString() || "N/A"}
                </span>
              </div>
              <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  Columns:
                </span>
                <span className="text-gray-900 dark:text-white font-semibold">
                  {fileInfo.shape?.[1] || fileInfo.columns?.length || "N/A"}
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Data Quality</span>
            </h3>
            <div className="space-y-2">
              {fileInfo.missing_values && (
                <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    Missing Values:
                  </span>
                  <span className="text-gray-900 dark:text-white font-semibold">
                    {Object.values(fileInfo.missing_values).reduce(
                      (sum, val) => sum + val,
                      0
                    )}
                  </span>
                </div>
              )}
              <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  Data Types:
                </span>
                <span className="text-gray-900 dark:text-white font-semibold">
                  {fileInfo.dtypes
                    ? Object.keys(fileInfo.dtypes).length
                    : "N/A"}{" "}
                  types
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
              <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
              <span>Quick Stats</span>
            </h3>
            <div className="space-y-2">
              {fileInfo.numerical_summary && (
                <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    Numerical Columns:
                  </span>
                  <span className="text-gray-900 dark:text-white font-semibold">
                    {Object.keys(fileInfo.numerical_summary).length}
                  </span>
                </div>
              )}
              {fileInfo.categorical_summary && (
                <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    Categorical Columns:
                  </span>
                  <span className="text-gray-900 dark:text-white font-semibold">
                    {Object.keys(fileInfo.categorical_summary).length}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Step-by-Step Analysis */}
      <StepByStepAnalysis fileId={fileId} onComplete={handleAnalysisComplete} />
    </div>
  );
};

export default AnalysisPage;
