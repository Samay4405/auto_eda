import { useState } from "react";
import { Bot, User, Settings, Zap } from "lucide-react";

const OperationSelector = ({ onSelectOperation, selectedFile }) => {
  const [selectedOperation, setSelectedOperation] = useState("");
  const [selectedMode, setSelectedMode] = useState("");
  const [showOptions, setShowOptions] = useState(false);
  const [options, setOptions] = useState({});

  const operations = [
    {
      id: "clean",
      title: "Data Cleaning",
      description: "Remove duplicates, handle missing values, fix data types",
      icon: "🧹",
      color: "bg-green-100 border-green-300 hover:bg-green-200",
    },
    {
      id: "transform",
      title: "Data Transformation",
      description: "Scale features, encode categories, create new features",
      icon: "🔄",
      color: "bg-blue-100 border-blue-300 hover:bg-blue-200",
    },
    {
      id: "classify",
      title: "Data Classification",
      description: "Analyze data types, patterns, and quality metrics",
      icon: "🏷️",
      color: "bg-purple-100 border-purple-300 hover:bg-purple-200",
    },
    {
      id: "visualize",
      title: "Data Visualization",
      description: "Generate comprehensive charts and dashboards",
      icon: "📊",
      color: "bg-orange-100 border-orange-300 hover:bg-orange-200",
    },
  ];

  const modes = [
    {
      id: "manual",
      title: "Manual Mode",
      description: "Configure specific operations and parameters",
      icon: <Settings className="w-6 h-6" />,
      color: "bg-gray-100 border-gray-300 hover:bg-gray-200",
    },
    {
      id: "ai",
      title: "AI Mode",
      description: "Let AI automatically analyze and process your data",
      icon: <Bot className="w-6 h-6" />,
      color: "bg-indigo-100 border-indigo-300 hover:bg-indigo-200",
    },
  ];

  const handleOperationSelect = (operationId) => {
    setSelectedOperation(operationId);
    setSelectedMode("");
    setShowOptions(false);
  };

  const handleModeSelect = (modeId) => {
    setSelectedMode(modeId);
    if (modeId === "manual") {
      setShowOptions(true);
    } else {
      setShowOptions(false);
      handleSubmit(modeId, {});
    }
  };

  const handleSubmit = (mode = selectedMode, opts = options) => {
    if (selectedOperation && mode) {
      onSelectOperation({
        operation: selectedOperation,
        mode: mode,
        options: opts,
        fileId: selectedFile.file_id,
      });
    }
  };

  const renderOptions = () => {
    if (!showOptions || selectedMode !== "manual") return null;

    const getOptionsForOperation = () => {
      switch (selectedOperation) {
        case "clean":
          return (
            <div className="space-y-4">
              <div>
                <label className="form-label">Missing Values Strategy</label>
                <select
                  className="form-input"
                  value={options.missing_strategy || "impute"}
                  onChange={(e) =>
                    setOptions({ ...options, missing_strategy: e.target.value })
                  }
                >
                  <option value="drop">Drop rows with missing values</option>
                  <option value="impute">Impute missing values</option>
                </select>
              </div>

              {options.missing_strategy === "impute" && (
                <>
                  <div>
                    <label className="form-label">Numerical Imputation</label>
                    <select
                      className="form-input"
                      value={options.numerical_impute_strategy || "mean"}
                      onChange={(e) =>
                        setOptions({
                          ...options,
                          numerical_impute_strategy: e.target.value,
                        })
                      }
                    >
                      <option value="mean">Mean</option>
                      <option value="median">Median</option>
                      <option value="most_frequent">Most Frequent</option>
                    </select>
                  </div>
                  <div>
                    <label className="form-label">Categorical Imputation</label>
                    <select
                      className="form-input"
                      value={
                        options.categorical_impute_strategy || "most_frequent"
                      }
                      onChange={(e) =>
                        setOptions({
                          ...options,
                          categorical_impute_strategy: e.target.value,
                        })
                      }
                    >
                      <option value="most_frequent">Most Frequent</option>
                      <option value="constant">Constant Value</option>
                    </select>
                  </div>
                </>
              )}

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="remove_outliers"
                  checked={options.remove_outliers || false}
                  onChange={(e) =>
                    setOptions({
                      ...options,
                      remove_outliers: e.target.checked,
                    })
                  }
                  className="mr-2"
                />
                <label htmlFor="remove_outliers" className="text-sm">
                  Remove outliers
                </label>
              </div>
            </div>
          );

        case "transform":
          return (
            <div className="space-y-4">
              <div>
                <label className="form-label">Scaling Method</label>
                <select
                  className="form-input"
                  value={options.scaling_method || "standard"}
                  onChange={(e) =>
                    setOptions({ ...options, scaling_method: e.target.value })
                  }
                >
                  <option value="none">No Scaling</option>
                  <option value="standard">Standard Scaling</option>
                  <option value="minmax">Min-Max Scaling</option>
                </select>
              </div>

              <div>
                <label className="form-label">Encoding Method</label>
                <select
                  className="form-input"
                  value={options.encoding_method || "label"}
                  onChange={(e) =>
                    setOptions({ ...options, encoding_method: e.target.value })
                  }
                >
                  <option value="none">No Encoding</option>
                  <option value="label">Label Encoding</option>
                  <option value="onehot">One-Hot Encoding</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="create_features"
                  checked={options.create_features || false}
                  onChange={(e) =>
                    setOptions({
                      ...options,
                      create_features: e.target.checked,
                    })
                  }
                  className="mr-2"
                />
                <label htmlFor="create_features" className="text-sm">
                  Create interaction features
                </label>
              </div>
            </div>
          );

        case "visualize":
          return (
            <div className="space-y-4">
              <div>
                <label className="form-label">Chart Types</label>
                <select
                  className="form-input"
                  value={options.chart_types || "all"}
                  onChange={(e) =>
                    setOptions({ ...options, chart_types: e.target.value })
                  }
                >
                  <option value="all">All Charts</option>
                  <option value="distribution">Distribution Charts</option>
                  <option value="correlation">Correlation Analysis</option>
                  <option value="relationships">Relationship Charts</option>
                  <option value="categorical">Categorical Analysis</option>
                </select>
              </div>
            </div>
          );

        default:
          return null;
      }
    };

    return (
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold mb-4">Configuration Options</h4>
        {getOptionsForOperation()}
        <div className="mt-6 flex space-x-3">
          <button
            onClick={() => handleSubmit()}
            className="btn-primary flex items-center space-x-2"
          >
            <Zap className="w-4 h-4" />
            <span>Start Processing</span>
          </button>
          <button
            onClick={() => setShowOptions(false)}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  };

  if (!selectedFile) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">
          Please upload a file first to begin analysis
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Choose Operation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {operations.map((operation) => (
            <div
              key={operation.id}
              onClick={() => handleOperationSelect(operation.id)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all
                ${
                  selectedOperation === operation.id
                    ? "border-blue-500 bg-blue-50"
                    : operation.color
                }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{operation.icon}</span>
                <div>
                  <h4 className="font-semibold">{operation.title}</h4>
                  <p className="text-sm text-gray-600">
                    {operation.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedOperation && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Choose Mode</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {modes.map((mode) => (
              <div
                key={mode.id}
                onClick={() => handleModeSelect(mode.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all
                  ${
                    selectedMode === mode.id
                      ? "border-blue-500 bg-blue-50"
                      : mode.color
                  }`}
              >
                <div className="flex items-center space-x-3">
                  {mode.icon}
                  <div>
                    <h4 className="font-semibold">{mode.title}</h4>
                    <p className="text-sm text-gray-600">{mode.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {renderOptions()}
    </div>
  );
};

export default OperationSelector;
