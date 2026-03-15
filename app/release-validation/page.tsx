'use client'

import { useState } from 'react'
import { 
  Download, 
  Share, 
  ArrowLeft, 
  CheckCircle
} from 'lucide-react'
import { AppHeader } from '../../components/layout/AppHeader'
import { PageContainer } from '../../components/layout/PageContainer'
import { ReleaseDecisionScenario, LegacyStatisticalResult, MetricComparison } from '../../lib/types/release'
import {
  RecommendationHeroCard,
  StatisticalSummaryCard,
  HypothesisDefinitionCard,
  InterpretationCard,
  ComparisonSnapshotCard,
  DecisionTimelineStrip,
  TestInputsCard
} from '../../components/release'
import { releaseDecisionData, legacyReleaseDecisionData, comparisonSnapshot } from '../../lib/mock-data/release-data'

// Helper function to convert new data structure to legacy format for components
function convertToLegacy(decision: ReleaseDecisionScenario): LegacyStatisticalResult {
  // Map the new decision format to legacy format
  const legacyRecommendation = 
    decision.recommendation.decision === 'Safe to release' ? 'SAFE TO RELEASE' :
    decision.recommendation.decision === 'Needs more evidence' ? 'KEEP TESTING' :
    'DO NOT RELEASE';

  return {
    experimentName: "Product Search Prompt Optimization",
    candidate: decision.hypothesis.candidate,
    baseline: decision.hypothesis.baseline,
    runDate: "12 Mar 2026",
    datasetName: "Product Search Queries",
    status: 'Completed',
    recommendation: legacyRecommendation,
    metric: {
      name: decision.hypothesis.metric,
      baselineValue: `${decision.comparisonSnapshot[0]?.baseline.value}${decision.comparisonSnapshot[0]?.baseline.unit || ''}`,
      candidateValue: `${decision.comparisonSnapshot[0]?.candidate.value}${decision.comparisonSnapshot[0]?.candidate.unit || ''}`,
      improvement: `${decision.comparisonSnapshot[0]?.delta.percentage > 0 ? '+' : ''}${decision.comparisonSnapshot[0]?.delta.percentage.toFixed(1)}%`,
      pValue: decision.statisticalSummary.pValue,
      confidenceLevel: decision.statisticalSummary.confidenceLevel,
      isSignificant: decision.statisticalSummary.pValue < decision.statisticalSummary.significanceThreshold
    },
    hypothesis: {
      null: decision.statisticalSummary.nullHypothesis,
      alternative: `${decision.hypothesis.candidate} is better than ${decision.hypothesis.baseline}`,
      testType: decision.hypothesis.testType,
      alpha: decision.statisticalSummary.significanceThreshold
    },
    testInputs: {
      datasetSize: decision.hypothesis.sampleSize,
      method: decision.hypothesis.testType,
      sources: ["Promptfoo", "Langfuse", "Hypothesis Testing Tool"]
    },
    interpretation: {
      summary: decision.interpretation.summary,
      businessImplication: decision.interpretation.businessImpact,
      riskNote: decision.interpretation.caveats?.[0] || decision.recommendation.riskAssessment || ""
    },
    expectedImpact: decision.recommendation.expectedImpact[0] || ""
  };
}

export default function ReleaseValidation() {
  // Use the new data structure
  const newDecision = releaseDecisionData[0];
  
  // Convert to legacy format for existing components
  const result = convertToLegacy(newDecision);
  
  return (
    <>
      <AppHeader />
      <PageContainer>
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <button 
              onClick={() => window.history.back()}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Experiment Dashboard
            </button>
          </div>
          
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Release Decision</h2>
              <p className="text-lg text-gray-600 mb-4">
                Statistical validation of AI experiment outcomes
              </p>
              
              {/* Experiment Context */}
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                <span><strong>Experiment:</strong> {result.experimentName}</span>
                <span><strong>Candidate:</strong> {result.candidate}</span>
                <span><strong>Baseline:</strong> {result.baseline}</span>
                <span><strong>Run Date:</strong> {result.runDate}</span>
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  <CheckCircle className="w-3 h-3" />
                  {result.status}
                </span>
              </div>
            </div>
            
            <div className="flex gap-3">
              <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-gray-700">
                <Share className="w-4 h-4" />
                Share
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-gray-700">
                <Download className="w-4 h-4" />
                Export Report
              </button>
            </div>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-7 space-y-6">
            <StatisticalSummaryCard result={result} />
            <HypothesisDefinitionCard result={result} />
            <TestInputsCard result={result} />
            <ComparisonSnapshotCard comparisonSnapshot={comparisonSnapshot} />
          </div>

          {/* Right Column */}
          <div className="lg:col-span-5 space-y-6">
            <RecommendationHeroCard result={result} />
            <InterpretationCard result={result} />
          </div>
        </div>

        <DecisionTimelineStrip />

        {/* Footer Navigation */}
        <div className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Statistical validation complete
              </h3>
              <p className="text-gray-600 text-sm">
                The candidate variant shows statistically significant improvement and is recommended for release
              </p>
            </div>
            <div className="flex gap-3">
              <button 
                onClick={() => window.location.href = '/experiments'}
                className="px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium"
              >
                Back to Experiments
              </button>
              <button className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 font-medium whitespace-nowrap">
                Proceed with Release
              </button>
            </div>
          </div>
        </div>
      </PageContainer>
    </>
  )
}