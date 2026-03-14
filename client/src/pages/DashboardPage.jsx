import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import DashboardBuilder from "../components/DashboardBuilder";
import LoadingSpinner from "../components/LoadingSpinner";
import { AlertCircle, ArrowLeft } from "lucide-react";

const DashboardPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [fileId, setFileId] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatedDashboard, setGeneratedDashboard] = useState(null);

  useEffect(() => {
    const id = searchParams.get("fileId");
    if (id) {
      setFileId(id);
      fetchFileInfo(id);
    } else {
      setLoading(false);
      setError("No file ID provided");
    }
  }, [searchParams]);

  const fetchFileInfo = async (id) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/file/${id}/info`);
      const data = await response.json();

      if (response.ok) {
        setFileInfo(data);
      } else {
        setError(data.detail || "Failed to fetch file information");
      }
    } catch {
      setError("Failed to connect to server");
    } finally {
      setLoading(false);
    }
  };

  const handleDashboardGenerated = (dashboard) => {
    setGeneratedDashboard(dashboard);
  };

  const goBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center min-h-[80vh]">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6 text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={goBack}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors mx-auto"
            >
              <ArrowLeft className="w-4 h-4" />
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <div className="mb-6">
          <button
            onClick={goBack}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Analysis
          </button>
        </div>

        {/* File Information Header */}
        {fileInfo && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  Dashboard Builder
                </h1>
                <p className="text-gray-600">
                  Generate automated dashboards for your dataset
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">Dataset</div>
                <div className="font-medium text-gray-900">
                  {fileInfo.shape?.[0]?.toLocaleString()} rows ×{" "}
                  {fileInfo.shape?.[1]} columns
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {fileInfo.missing_values
                    ? `${Object.values(fileInfo.missing_values).reduce(
                        (a, b) => a + b,
                        0
                      )} missing values`
                    : "No missing values"}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Dashboard Builder Component */}
        <DashboardBuilder
          fileId={fileId}
          onDashboardGenerated={handleDashboardGenerated}
        />

        {/* Quick Stats */}
        {fileInfo && (
          <div className="mt-8 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Dataset Overview</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {fileInfo.shape?.[0]?.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Rows</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {fileInfo.shape?.[1]}
                </div>
                <div className="text-sm text-gray-600">Columns</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {fileInfo.numerical_columns?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Numerical</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {fileInfo.categorical_columns?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Categorical</div>
              </div>
            </div>
          </div>
        )}

        {/* Generated Dashboard Info */}
        {generatedDashboard && (
          <div className="mt-8 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
            <h3 className="text-lg font-semibold text-green-900 mb-3">
              Dashboard Generated Successfully!
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="font-medium text-gray-900">Dashboard Type</div>
                <div className="text-gray-600 capitalize">
                  {generatedDashboard.type.replace("_", " ")}
                </div>
              </div>
              <div>
                <div className="font-medium text-gray-900">
                  Charts Generated
                </div>
                <div className="text-gray-600">
                  Multiple visualization types
                </div>
              </div>
              <div>
                <div className="font-medium text-gray-900">AI Insights</div>
                <div className="text-gray-600">Automated analysis included</div>
              </div>
            </div>
            <div className="mt-4 p-3 bg-white rounded border">
              <div className="text-xs text-gray-500">Dashboard ID</div>
              <div className="font-mono text-sm text-gray-700">
                {generatedDashboard.id}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
