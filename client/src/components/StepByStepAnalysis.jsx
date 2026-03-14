import React, { useState, useEffect } from "react";
import {
  Bot,
  User,
  CheckCircle,
  ArrowRight,
  BarChart3,
  Filter,
  Shuffle,
  Tag,
  Eye,
  AlertCircle,
} from "lucide-react";
import LoadingSpinner from "./LoadingSpinner";

const StepByStepAnalysis = ({ fileId, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedMode, setSelectedMode] = useState("");
  const [stepResults, setStepResults] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);

  const steps = [
    {
      id: "mode",
      title: "Choose Analysis Mode",
      description: "Select how you want to analyze your data",
      icon: <Bot className="w-8 h-8" />,
      component: "mode-selector",
    },
    {
      id: "clean",
      title: "Data Cleaning",
      description: "Clean and prepare your data - can be skipped",
      icon: <Filter className="w-8 h-8" />,
      component: "step-selector",
      operation: "clean",
    },
    {
      id: "transform",
      title: "Data Transformation",
      description: "Transform and scale your data - can be skipped",
      icon: <Shuffle className="w-8 h-8" />,
      component: "step-selector",
      operation: "transform",
    },
    {
      id: "classify",
      title: "Data Classification",
      description: "Analyze data types and patterns - can be skipped",
      icon: <Tag className="w-8 h-8" />,
      component: "step-selector",
      operation: "classify",
    },
    {
      id: "visualize",
      title: "Data Visualization",
      description: "Create charts and dashboards",
      icon: <BarChart3 className="w-8 h-8" />,
      component: "visualization",
    },
  ];

  const processStep = async (operation, shouldProcess, options = {}) => {
    if (!shouldProcess) {
      setStepResults((prev) => ({
        ...prev,
        [operation]: { skipped: true },
      }));
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append("file_id", fileId);
      formData.append("operation", operation);
      formData.append("mode", selectedMode);
      formData.append("options", JSON.stringify(options));

      const response = await fetch("http://localhost:8000/api/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Processing failed for ${operation}`);
      }

      const result = await response.json();
      setStepResults((prev) => ({
        ...prev,
        [operation]: result,
      }));
    } catch (error) {
      console.error(`Error processing ${operation}:`, error);
      setStepResults((prev) => ({
        ...prev,
        [operation]: { error: error.message },
      }));
    } finally {
      setIsProcessing(false);
    }
  };

  const ModeSelector = () => (
    <div className="space-y-8">
      <div className="text-center mb-10">
        <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Choose Your Analysis Mode
        </h3>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          This will determine how each subsequent step is handled throughout the
          analysis process
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
        <div
          onClick={() => setSelectedMode("ai")}
          className={`group p-8 border-2 rounded-2xl cursor-pointer transition-all duration-300 transform hover:scale-[1.02] ${
            selectedMode === "ai"
              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-xl shadow-blue-500/20 dark:shadow-blue-500/10 ring-4 ring-blue-500/20"
              : "border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 hover:bg-gray-50 dark:hover:bg-gray-800 bg-white dark:bg-gray-800 hover:shadow-lg"
          }`}
        >
          <div className="flex flex-col items-center text-center space-y-6">
            <div
              className={`p-5 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-2xl shadow-lg transition-transform duration-300 ${
                selectedMode === "ai" ? "scale-110" : "group-hover:scale-105"
              }`}
            >
              <Bot className="w-10 h-10" />
            </div>
            <div>
              <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                AI Mode
              </h4>
              <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                Let AI automatically analyze and process your data with optimal
                settings using advanced algorithms
              </p>
              <ul className="text-sm text-gray-500 dark:text-gray-400 space-y-2">
                <li className="flex items-center justify-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-blue-500" />
                  <span>Automatic parameter selection</span>
                </li>
                <li className="flex items-center justify-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-blue-500" />
                  <span>Intelligent recommendations</span>
                </li>
                <li className="flex items-center justify-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-blue-500" />
                  <span>Optimal processing pipeline</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div
          onClick={() => setSelectedMode("manual")}
          className={`group p-8 border-2 rounded-2xl cursor-pointer transition-all duration-300 transform hover:scale-[1.02] ${
            selectedMode === "manual"
              ? "border-green-500 bg-green-50 dark:bg-green-900/20 shadow-xl shadow-green-500/20 dark:shadow-green-500/10 ring-4 ring-green-500/20"
              : "border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600 hover:bg-gray-50 dark:hover:bg-gray-800 bg-white dark:bg-gray-800 hover:shadow-lg"
          }`}
        >
          <div className="flex flex-col items-center text-center space-y-6">
            <div
              className={`p-5 bg-gradient-to-br from-green-500 to-teal-600 text-white rounded-2xl shadow-lg transition-transform duration-300 ${
                selectedMode === "manual"
                  ? "scale-110"
                  : "group-hover:scale-105"
              }`}
            >
              <User className="w-10 h-10" />
            </div>
            <div>
              <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                Manual Mode
              </h4>
              <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                Configure each step manually with full control over parameters
                and detailed customization options
              </p>
              <ul className="text-sm text-gray-500 dark:text-gray-400 space-y-2">
                <li className="flex items-center justify-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Full parameter control</span>
                </li>
                <li className="flex items-center justify-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Custom configurations</span>
                </li>
                <li className="flex items-center justify-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Detailed options</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {selectedMode && (
        <div className="animate-in slide-in-from-bottom duration-500">
          {/* Disclaimer */}
          <div className="bg-amber-50 dark:bg-amber-900/20 border-2 border-amber-200 dark:border-amber-800/50 rounded-2xl p-6 max-w-5xl mx-auto mb-8">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <AlertCircle className="w-6 h-6 text-amber-600 dark:text-amber-400 mt-1" />
              </div>
              <div>
                <h4 className="text-lg font-semibold text-amber-800 dark:text-amber-200 mb-3">
                  Important Disclaimer
                </h4>
                <p className="text-amber-700 dark:text-amber-300 mb-4 leading-relaxed">
                  The processing steps (Data Cleaning, Transformation, and
                  Classification) are optional and experimental. Results may not
                  be fully accurate and should be reviewed before making
                  important decisions. Use your judgment when interpreting the
                  outputs.
                </p>
                <div className="bg-amber-100 dark:bg-amber-900/30 rounded-xl p-4 space-y-3">
                  <div className="flex items-start space-x-2">
                    <span className="text-lg">💡</span>
                    <p className="text-sm text-amber-700 dark:text-amber-300">
                      <strong>Tip:</strong> You can skip any or all processing
                      steps and go directly to visualization if you prefer to
                      work with your raw data.
                    </p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-lg">🔍</span>
                    <p className="text-sm text-amber-700 dark:text-amber-300">
                      <strong>Benefits:</strong> When enabled, these steps can
                      help improve data quality and generate insights, but are
                      not required for basic visualization.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={() => setCurrentStep(1)}
              className={`inline-flex items-center gap-3 px-10 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg ${
                selectedMode === "ai"
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-blue-500/25"
                  : "bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white shadow-green-500/25"
              }`}
            >
              Continue with {selectedMode === "ai" ? "AI" : "Manual"} Mode
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const StepSelector = ({ step }) => {
    const [shouldProcess, setShouldProcess] = useState(false); // Changed to false to emphasize optional nature
    const [options, setOptions] = useState({});
    const [showOptions, setShowOptions] = useState(false);

    useEffect(() => {
      if (selectedMode === "manual") {
        setShowOptions(true);
      }
    }, []);

    const handleContinue = async () => {
      await processStep(step.operation, shouldProcess, options);
      setCurrentStep((prev) => prev + 1);
    };

    const renderManualOptions = () => {
      if (!showOptions || selectedMode !== "manual") return null;

      switch (step.operation) {
        case "clean":
          return (
            <div className="space-y-6 bg-gray-50 dark:bg-gray-800/50 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                Cleaning Options
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Missing Values Strategy
                  </label>
                  <select
                    value={options.missing_strategy || "impute"}
                    onChange={(e) =>
                      setOptions((prev) => ({
                        ...prev,
                        missing_strategy: e.target.value,
                      }))
                    }
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  >
                    <option value="impute">Impute missing values</option>
                    <option value="drop">Drop rows with missing values</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Numerical Imputation
                  </label>
                  <select
                    value={options.numerical_impute_strategy || "mean"}
                    onChange={(e) =>
                      setOptions((prev) => ({
                        ...prev,
                        numerical_impute_strategy: e.target.value,
                      }))
                    }
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  >
                    <option value="mean">Mean</option>
                    <option value="median">Median</option>
                    <option value="most_frequent">Most Frequent</option>
                  </select>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <label className="flex items-center space-x-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={options.remove_duplicates !== false}
                    onChange={(e) =>
                      setOptions((prev) => ({
                        ...prev,
                        remove_duplicates: e.target.checked,
                      }))
                    }
                    className="w-4 h-4 text-blue-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:focus:ring-blue-600 focus:ring-2"
                  />
                  <span className="text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors">
                    Remove duplicates
                  </span>
                </label>
                <label className="flex items-center space-x-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={options.remove_outliers || false}
                    onChange={(e) =>
                      setOptions((prev) => ({
                        ...prev,
                        remove_outliers: e.target.checked,
                      }))
                    }
                    className="w-4 h-4 text-blue-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:focus:ring-blue-600 focus:ring-2"
                  />
                  <span className="text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors">
                    Remove outliers
                  </span>
                </label>
              </div>
            </div>
          );
        case "transform":
          return (
            <div className="space-y-6 bg-gray-50 dark:bg-gray-800/50 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                Transformation Options
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Scaling Method
                  </label>
                  <select
                    value={options.scaling_method || "standard"}
                    onChange={(e) =>
                      setOptions((prev) => ({
                        ...prev,
                        scaling_method: e.target.value,
                      }))
                    }
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  >
                    <option value="none">No Scaling</option>
                    <option value="standard">Standard Scaling</option>
                    <option value="minmax">Min-Max Scaling</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Encoding Method
                  </label>
                  <select
                    value={options.encoding_method || "label"}
                    onChange={(e) =>
                      setOptions((prev) => ({
                        ...prev,
                        encoding_method: e.target.value,
                      }))
                    }
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  >
                    <option value="none">No Encoding</option>
                    <option value="label">Label Encoding</option>
                    <option value="onehot">One-Hot Encoding</option>
                  </select>
                </div>
              </div>
            </div>
          );
        default:
          return null;
      }
    };

    return (
      <div className="space-y-8">
        <div className="text-center">
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            {step.title}
          </h3>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            {step.description}
          </p>
        </div>

        {/* Optional Step Disclaimer */}
        <div className="bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-200 dark:border-orange-800/50 rounded-xl p-5 max-w-3xl mx-auto">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-orange-600 dark:text-orange-400 flex-shrink-0" />
            <p className="text-orange-700 dark:text-orange-300">
              <strong>Optional Step:</strong> This processing step is
              experimental and can be skipped. Results may vary in accuracy and
              should be validated for critical use cases.
            </p>
          </div>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl p-8 shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <label className="flex items-center text-xl font-semibold cursor-pointer group">
                <input
                  type="checkbox"
                  checked={shouldProcess}
                  onChange={(e) => setShouldProcess(e.target.checked)}
                  className="mr-4 w-6 h-6 text-blue-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:focus:ring-blue-600 focus:ring-2"
                />
                <span className="text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  Run {step.title.replace(" (Optional)", "")}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400 ml-3 font-normal">
                  (Optional - you can skip this)
                </span>
              </label>
            </div>

            {shouldProcess && selectedMode === "ai" && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-6 rounded-xl">
                <div className="flex items-center space-x-3">
                  <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  <p className="text-blue-800 dark:text-blue-200 font-medium">
                    AI will automatically select the best options for this step
                  </p>
                </div>
              </div>
            )}

            {shouldProcess && renderManualOptions()}

            {!shouldProcess && (
              <div className="bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-800/50 p-6 rounded-xl">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                  <div>
                    <p className="text-green-700 dark:text-green-300 font-medium">
                      <strong>Skipping this step</strong>
                    </p>
                    <p className="text-green-600 dark:text-green-400 text-sm mt-1">
                      You can proceed directly to the next step or
                      visualization.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="text-center mt-8">
            <button
              onClick={handleContinue}
              disabled={isProcessing}
              className="inline-flex items-center gap-3 px-10 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold text-lg rounded-xl transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl disabled:hover:scale-100"
            >
              {isProcessing ? (
                <>
                  <LoadingSpinner className="w-5 h-5" />
                  Processing...
                </>
              ) : (
                <>
                  Continue
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const VisualizationStep = () => {
    const handleComplete = (activeTab = "dashboard") => {
      // Call the completion callback
      onComplete({
        mode: selectedMode,
        results: stepResults,
        activeTab,
      });
    };

    return (
      <div className="space-y-8">
        <div className="text-center">
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Data Visualization
          </h3>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Choose how you want to visualize your processed data and generate
            insights
          </p>
        </div>

        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div
              onClick={() => handleComplete("dashboard")}
              className="group p-8 border-2 border-gray-200 dark:border-gray-700 rounded-2xl cursor-pointer transition-all duration-300 transform hover:scale-[1.02] hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:shadow-xl bg-white dark:bg-gray-800"
            >
              <div className="flex flex-col items-center text-center space-y-6">
                <div className="p-5 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-2xl shadow-lg transition-transform duration-300 group-hover:scale-110">
                  <BarChart3 className="w-10 h-10" />
                </div>
                <div>
                  <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                    Smart Dashboard
                  </h4>
                  <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                    AI-generated consolidated dashboard with the most relevant
                    charts for your dataset
                  </p>
                  <ul className="text-sm text-gray-500 dark:text-gray-400 space-y-2">
                    <li className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-blue-500" />
                      <span>AI-selected important charts</span>
                    </li>
                    <li className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-blue-500" />
                      <span>Interactive dashboard</span>
                    </li>
                    <li className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-blue-500" />
                      <span>Professional layout</span>
                    </li>
                    <li className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-blue-500" />
                      <span>Export capabilities</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div
              onClick={() => handleComplete("charts")}
              className="group p-8 border-2 border-gray-200 dark:border-gray-700 rounded-2xl cursor-pointer transition-all duration-300 transform hover:scale-[1.02] hover:border-green-400 dark:hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20 hover:shadow-xl bg-white dark:bg-gray-800"
            >
              <div className="flex flex-col items-center text-center space-y-6">
                <div className="p-5 bg-gradient-to-br from-green-500 to-teal-600 text-white rounded-2xl shadow-lg transition-transform duration-300 group-hover:scale-110">
                  <Eye className="w-10 h-10" />
                </div>
                <div>
                  <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                    Individual Charts
                  </h4>
                  <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                    Browse and explore individual charts and visualizations
                    separately with detailed customization
                  </p>
                  <ul className="text-sm text-gray-500 dark:text-gray-400 space-y-2">
                    <li className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>All chart types available</span>
                    </li>
                    <li className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>Detailed exploration</span>
                    </li>
                    <li className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>Individual chart export</span>
                    </li>
                    <li className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>Customization options</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-10">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 mb-8 max-w-3xl mx-auto">
              <p className="text-blue-800 dark:text-blue-200 font-medium">
                💡 You can access both visualization modes in the next page and
                switch between them anytime
              </p>
            </div>
            <button
              onClick={() => handleComplete("dashboard")}
              className="inline-flex items-center gap-3 px-10 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold text-lg rounded-xl transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
            >
              Continue to Visualization
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderStepComponent = () => {
    const step = steps[currentStep];

    switch (step.component) {
      case "mode-selector":
        return <ModeSelector />;
      case "step-selector":
        return <StepSelector step={step} />;
      case "visualization":
        return <VisualizationStep />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4">
      {/* Progress Steps */}
      <div className="mb-12">
        <div className="flex items-center justify-between relative">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className="flex flex-col items-center relative z-10"
            >
              <div
                className={`w-16 h-16 rounded-2xl flex items-center justify-center border-3 transition-all duration-300 shadow-lg ${
                  index <= currentStep
                    ? "bg-blue-600 border-blue-600 text-white shadow-blue-500/25"
                    : "bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-400 dark:text-gray-500"
                }`}
              >
                {index < currentStep ? (
                  <CheckCircle className="w-8 h-8" />
                ) : (
                  <div className="scale-75">{step.icon}</div>
                )}
              </div>
              <div className="mt-4 text-center max-w-32">
                <span
                  className={`text-sm font-semibold ${
                    index <= currentStep
                      ? "text-blue-600 dark:text-blue-400"
                      : "text-gray-400 dark:text-gray-500"
                  }`}
                >
                  {step.title}
                </span>
              </div>

              {/* Progress Line */}
              {index < steps.length - 1 && (
                <div className="absolute top-8 left-full w-full h-1 -z-10 hidden md:block">
                  <div
                    className={`h-full transition-all duration-500 ${
                      index < currentStep
                        ? "bg-blue-600"
                        : "bg-gray-300 dark:bg-gray-600"
                    }`}
                    style={{ width: "100%" }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-3xl p-8 md:p-12 shadow-xl">
        {renderStepComponent()}
      </div>

      {/* Results Summary */}
      {Object.keys(stepResults).length > 0 && (
        <div className="mt-10 bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-800/50 rounded-2xl p-8 shadow-lg">
          <h3 className="text-xl font-bold text-green-900 dark:text-green-100 mb-6 flex items-center space-x-2">
            <CheckCircle className="w-6 h-6" />
            <span>Processing Summary</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(stepResults).map(([operation, result]) => (
              <div
                key={operation}
                className="flex items-center space-x-3 bg-green-100 dark:bg-green-900/30 p-4 rounded-xl"
              >
                <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0" />
                <div>
                  <span className="capitalize text-green-800 dark:text-green-200 font-semibold block">
                    {operation}
                  </span>
                  <span className="text-green-600 dark:text-green-400 text-sm">
                    {result.skipped
                      ? "Skipped"
                      : result.error
                      ? "Error"
                      : "Completed"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StepByStepAnalysis;
