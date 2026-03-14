import Plot from "react-plotly.js";
import { useState } from "react";
import { Download, Maximize2, Eye } from "lucide-react";

const ChartComponent = ({ chart, className = "" }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!chart || !chart.data) {
    return (
      <div
        className={`bg-white rounded-xl shadow-lg border border-gray-200 p-6 ${className}`}
      >
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <Eye className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No chart data available</p>
          </div>
        </div>
      </div>
    );
  }

  // Handle both string and object data formats
  const plotData =
    typeof chart.data === "string" ? JSON.parse(chart.data) : chart.data;

  const handleDownload = () => {
    // Trigger download of the chart as PNG
    const element = document.getElementById(`chart-${chart.id}`);
    if (element) {
      const plotlyDiv = element.querySelector(".plotly");
      if (plotlyDiv) {
        window.Plotly.downloadImage(plotlyDiv, {
          format: "png",
          width: 1200,
          height: 800,
          filename: `${chart.title.replace(/\s+/g, "_").toLowerCase()}`,
        });
      }
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  // Enhanced layout configuration for better responsiveness
  const getResponsiveLayout = (isFullscreen = false) => ({
    ...plotData.layout,
    autosize: true,
    responsive: true,
    margin: isFullscreen
      ? { l: 80, r: 80, t: 80, b: 80 }
      : { l: 60, r: 40, t: 60, b: 60 },
    font: {
      family: "Inter, system-ui, sans-serif",
      size: isFullscreen ? 14 : 12,
    },
    plot_bgcolor: "rgba(0,0,0,0)",
    paper_bgcolor: "rgba(0,0,0,0)",
    showlegend: plotData.layout?.showlegend ?? true,
    legend: {
      orientation: "h",
      yanchor: "bottom",
      y: -0.2,
      xanchor: "center",
      x: 0.5,
      font: { size: isFullscreen ? 12 : 10 },
    },
    // Ensure axes are properly configured
    xaxis: {
      ...plotData.layout?.xaxis,
      automargin: true,
      tickangle: -45,
      tickfont: { size: isFullscreen ? 12 : 10 },
    },
    yaxis: {
      ...plotData.layout?.yaxis,
      automargin: true,
      tickfont: { size: isFullscreen ? 12 : 10 },
    },
  });

  return (
    <>
      <div
        id={`chart-${chart.id}`}
        className={`bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden transition-all duration-300 hover:shadow-xl hover:border-gray-300 ${className}`}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-1">
                {chart.title}
              </h3>
              {chart.description && (
                <p className="text-sm text-gray-600 line-clamp-2">
                  {chart.description}
                </p>
              )}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={toggleFullscreen}
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
                title="View Fullscreen"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
              <button
                onClick={handleDownload}
                className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200"
                title="Download Chart"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Chart Container */}
        <div className="p-4">
          <div className="w-full" style={{ height: "350px" }}>
            <Plot
              data={plotData.data}
              layout={getResponsiveLayout(false)}
              config={{
                displayModeBar: false,
                displaylogo: false,
                responsive: true,
                doubleClick: false,
                showTips: false,
                staticPlot: false,
              }}
              style={{
                width: "100%",
                height: "100%",
                minHeight: "350px",
              }}
              useResizeHandler={true}
              className="plotly-chart"
            />
          </div>
        </div>

        {/* Chart Type Badge */}
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-100">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {chart.type.replace("_", " ").toUpperCase()}
          </span>
        </div>
      </div>

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-95 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full h-full max-w-7xl max-h-full overflow-hidden">
            {/* Modal Header */}
            <div className="px-8 py-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">
                    {chart.title}
                  </h3>
                  {chart.description && (
                    <p className="text-gray-600">{chart.description}</p>
                  )}
                </div>
                <button
                  onClick={toggleFullscreen}
                  className="text-gray-500 hover:text-gray-700 text-3xl font-light hover:bg-gray-100 rounded-full w-10 h-10 flex items-center justify-center transition-all"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Modal Chart */}
            <div className="p-8 h-full">
              <div
                className="w-full h-full"
                style={{ height: "calc(100vh - 200px)" }}
              >
                <Plot
                  data={plotData.data}
                  layout={getResponsiveLayout(true)}
                  config={{
                    displayModeBar: true,
                    displaylogo: false,
                    responsive: true,
                    modeBarButtonsToRemove: [
                      "pan2d",
                      "lasso2d",
                      "select2d",
                      "autoScale2d",
                      "hoverClosestCartesian",
                      "hoverCompareCartesian",
                    ],
                  }}
                  style={{
                    width: "100%",
                    height: "100%",
                    minHeight: "calc(100vh - 200px)",
                  }}
                  useResizeHandler={true}
                  className="plotly-chart-fullscreen"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChartComponent;
