import React from "react";
import PropTypes from "prop-types";

/**
 * LLM Insights Panel Component
 *
 * Displays AI-generated insights from the LLM analysis engine.
 * Shows different insight types based on dashboard type:
 * - Executive: Summary, KPIs, Recommendations, Business Impact
 * - Data Quality: Quality Score, Issues, Remediation
 * - Exploratory: Patterns, Correlations, Hypothesis
 */
const LLMInsightsPanel = ({ llmInsights, dashboardType }) => {
  if (!llmInsights || Object.keys(llmInsights).length === 0) {
    return null;
  }

  const analysisType = llmInsights.analysis_type || dashboardType;
  const source = llmInsights.source || "llm";

  const renderExecutiveInsights = () => (
    <div className="space-y-6">
      {/* Executive Summary */}
      {llmInsights.executive_summary && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center">
            <span className="mr-2">📊</span> Executive Summary
          </h3>
          <p className="text-gray-700 dark:text-gray-300">
            {llmInsights.executive_summary}
          </p>
        </div>
      )}

      {/* Key Insights */}
      {llmInsights.key_insights && llmInsights.key_insights.length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
            <span className="mr-2">🎯</span> Key Performance Insights
          </h3>
          <ul className="space-y-2">
            {llmInsights.key_insights.map((insight, idx) => (
              <li key={idx} className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700 dark:text-gray-300">
                  {insight}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {/* Opportunities */}
        {llmInsights.opportunities && llmInsights.opportunities.length > 0 && (
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
            <h3 className="text-md font-semibold text-green-900 dark:text-green-100 mb-2 flex items-center">
              <span className="mr-2">🚀</span> Strategic Opportunities
            </h3>
            <ul className="space-y-1 text-sm">
              {llmInsights.opportunities.map((opp, idx) => (
                <li key={idx} className="text-green-800 dark:text-green-200">
                  • {opp}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risks */}
        {llmInsights.risks && llmInsights.risks.length > 0 && (
          <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg border border-amber-200 dark:border-amber-800">
            <h3 className="text-md font-semibold text-amber-900 dark:text-amber-100 mb-2 flex items-center">
              <span className="mr-2">⚠️</span> Risk Factors
            </h3>
            <ul className="space-y-1 text-sm">
              {llmInsights.risks.map((risk, idx) => (
                <li key={idx} className="text-amber-800 dark:text-amber-200">
                  • {risk}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {llmInsights.recommendations &&
        llmInsights.recommendations.length > 0 && (
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
            <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-3 flex items-center">
              <span className="mr-2">💡</span> Recommended Actions
            </h3>
            <ol className="space-y-2 list-decimal list-inside">
              {llmInsights.recommendations.map((rec, idx) => (
                <li key={idx} className="text-purple-800 dark:text-purple-200">
                  {rec}
                </li>
              ))}
            </ol>
          </div>
        )}

      {/* Business Impact */}
      {llmInsights.business_impact && (
        <div className="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-lg border border-indigo-200 dark:border-indigo-800">
          <h3 className="text-md font-semibold text-indigo-900 dark:text-indigo-100 mb-2 flex items-center">
            <span className="mr-2">📈</span> Business Impact
          </h3>
          <p className="text-indigo-800 dark:text-indigo-200">
            {llmInsights.business_impact}
          </p>
        </div>
      )}
    </div>
  );

  const renderDataQualityInsights = () => (
    <div className="space-y-6">
      {/* Quality Score */}
      {llmInsights.quality_score !== undefined && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 p-6 rounded-lg border border-green-200 dark:border-green-800">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-1">
                Overall Quality Score
              </h3>
              <p className="text-sm text-green-700 dark:text-green-300">
                {llmInsights.score_justification}
              </p>
            </div>
            <div className="text-5xl font-bold text-green-600 dark:text-green-400">
              {llmInsights.quality_score}
              <span className="text-2xl text-green-500">/100</span>
            </div>
          </div>
        </div>
      )}

      {/* Critical Issues */}
      {llmInsights.critical_issues &&
        llmInsights.critical_issues.length > 0 && (
          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
            <h3 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-3 flex items-center">
              <span className="mr-2">⚠️</span> Critical Issues
            </h3>
            <ul className="space-y-2">
              {llmInsights.critical_issues.map((issue, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-red-500 mr-2 mt-1">⚠</span>
                  <span className="text-red-800 dark:text-red-200">
                    {issue}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

      <div className="grid md:grid-cols-2 gap-4">
        {/* Completeness */}
        {llmInsights.completeness && (
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <h3 className="text-md font-semibold text-blue-900 dark:text-blue-100 mb-2">
              📊 Data Completeness
            </h3>
            <p className="text-blue-800 dark:text-blue-200">
              {llmInsights.completeness}
            </p>
          </div>
        )}

        {/* Consistency */}
        {llmInsights.consistency && (
          <div className="bg-cyan-50 dark:bg-cyan-900/20 p-4 rounded-lg border border-cyan-200 dark:border-cyan-800">
            <h3 className="text-md font-semibold text-cyan-900 dark:text-cyan-100 mb-2">
              🔄 Data Consistency
            </h3>
            <p className="text-cyan-800 dark:text-cyan-200">
              {llmInsights.consistency}
            </p>
          </div>
        )}
      </div>

      {/* Remediation Priorities */}
      {llmInsights.remediation_priorities &&
        llmInsights.remediation_priorities.length > 0 && (
          <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg border border-amber-200 dark:border-amber-800">
            <h3 className="text-lg font-semibold text-amber-900 dark:text-amber-100 mb-3 flex items-center">
              <span className="mr-2">🔧</span> Remediation Priorities
            </h3>
            <ol className="space-y-2 list-decimal list-inside">
              {llmInsights.remediation_priorities.map((priority, idx) => (
                <li key={idx} className="text-amber-800 dark:text-amber-200">
                  {priority}
                </li>
              ))}
            </ol>
          </div>
        )}

      {/* Readiness Assessment */}
      {llmInsights.readiness_assessment && (
        <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
          <h3 className="text-md font-semibold text-purple-900 dark:text-purple-100 mb-2 flex items-center">
            <span className="mr-2">✓</span> Readiness Assessment
          </h3>
          <p className="text-purple-800 dark:text-purple-200">
            {llmInsights.readiness_assessment}
          </p>
        </div>
      )}
    </div>
  );

  const renderExploratoryInsights = () => (
    <div className="space-y-6">
      {/* Key Patterns */}
      {llmInsights.patterns && llmInsights.patterns.length > 0 && (
        <div className="bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 p-4 rounded-lg border border-violet-200 dark:border-violet-800">
          <h3 className="text-lg font-semibold text-violet-900 dark:text-violet-100 mb-3 flex items-center">
            <span className="mr-2">🔍</span> Key Patterns Discovered
          </h3>
          <ul className="space-y-2">
            {llmInsights.patterns.map((pattern, idx) => (
              <li key={idx} className="flex items-start">
                <span className="text-violet-500 mr-2">•</span>
                <span className="text-violet-800 dark:text-violet-200">
                  {pattern}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Correlations */}
      {llmInsights.correlations && (
        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3 flex items-center">
            <span className="mr-2">🔗</span> Correlation Insights
          </h3>
          {typeof llmInsights.correlations === "string" ? (
            <p className="text-blue-800 dark:text-blue-200">
              {llmInsights.correlations}
            </p>
          ) : (
            <ul className="space-y-2">
              {llmInsights.correlations.map((corr, idx) => (
                <li key={idx} className="text-blue-800 dark:text-blue-200">
                  • {corr}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Hypothesis  */}
      {llmInsights.Hypothesis && llmInsights.Hypothesis.length > 0 && (
        <div className="bg-cyan-50 dark:bg-cyan-900/20 p-4 rounded-lg border border-cyan-200 dark:border-cyan-800">
          <h3 className="text-lg font-semibold text-cyan-900 dark:text-cyan-100 mb-3 flex items-center">
            <span className="mr-2">💭</span> Testable Hypothesis
          </h3>
          <ol className="space-y-2 list-decimal list-inside">
            {llmInsights.Hypothesis.map((hyp, idx) => (
              <li key={idx} className="text-cyan-800 dark:text-cyan-200">
                {hyp}
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Statistical Highlights */}
      {llmInsights.statistical_highlights &&
        llmInsights.statistical_highlights.length > 0 && (
          <div className="bg-emerald-50 dark:bg-emerald-900/20 p-4 rounded-lg border border-emerald-200 dark:border-emerald-800">
            <h3 className="text-md font-semibold text-emerald-900 dark:text-emerald-100 mb-2 flex items-center">
              <span className="mr-2">📊</span> Statistical Highlights
            </h3>
            <ul className="space-y-1 text-sm">
              {llmInsights.statistical_highlights.map((stat, idx) => (
                <li
                  key={idx}
                  className="text-emerald-800 dark:text-emerald-200"
                >
                  • {stat}
                </li>
              ))}
            </ul>
          </div>
        )}

      {/* Deep Dive Recommendations */}
      {llmInsights.deep_dive_recommendations &&
        llmInsights.deep_dive_recommendations.length > 0 && (
          <div className="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <h3 className="text-lg font-semibold text-indigo-900 dark:text-indigo-100 mb-3 flex items-center">
              <span className="mr-2">🎯</span> Recommended Deep Dives
            </h3>
            <ul className="space-y-2">
              {llmInsights.deep_dive_recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-indigo-500 mr-2">→</span>
                  <span className="text-indigo-800 dark:text-indigo-200">
                    {rec}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
    </div>
  );

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <span className="mr-3">🤖</span>
            AI-Powered Insights
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Real-time analysis powered by{" "}
            {source === "llm" ? "LLM Intelligence" : "Statistical Analysis"}
          </p>
        </div>
        {llmInsights.generated_at && (
          <span className="text-xs text-gray-500 dark:text-gray-500">
            {new Date(llmInsights.generated_at).toLocaleString()}
          </span>
        )}
      </div>

      {analysisType === "executive" && renderExecutiveInsights()}
      {analysisType === "data_quality" && renderDataQualityInsights()}
      {analysisType === "exploratory" && renderExploratoryInsights()}
    </div>
  );
};

LLMInsightsPanel.propTypes = {
  llmInsights: PropTypes.object,
  dashboardType: PropTypes.string,
};

export default LLMInsightsPanel;
