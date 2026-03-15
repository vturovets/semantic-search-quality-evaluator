import { ReleaseDecisionScenario } from '../types/release'

export const releaseDecisionData: ReleaseDecisionScenario[] = [
  {
    id: "release-decision-search-prompt-v2-2026-03-12",
    experimentId: "exp-search-prompt-v2-2026-03-12",
    recommendation: {
      decision: 'Safe to release',
      confidence: 95,
      rationale: "The candidate version demonstrates statistically significant improvement over the baseline with p-value of 0.018, well below the significance threshold of 0.05.",
      expectedImpact: [
        "Search success rate +5–7%",
        "Improved accuracy from 82% to 88%",
        "Reduced latency by 70ms on average",
        "Lower failure rate from 11% to 7%"
      ],
      riskAssessment: "Continue monitoring latency and consistency after release. Consider gradual rollout to production."
    },
    statisticalSummary: {
      nullHypothesis: "Prompt v2 is NOT better than Prompt v1",
      datasetSize: 200,
      pValue: 0.018,
      confidenceLevel: 95,
      conclusion: "Reject the null hypothesis. The candidate version shows statistically significant improvement.",
      significanceThreshold: 0.05
    },
    hypothesis: {
      baseline: "Prompt v1",
      candidate: "Prompt v2",
      metric: "Accuracy",
      sampleSize: 200,
      testType: "One-sided binomial test",
      assumptions: [
        "Independent observations",
        "Binary outcomes (success/failure)",
        "Fixed sample size",
        "Consistent evaluation criteria"
      ]
    },
    interpretation: {
      summary: "The candidate version demonstrates a measurable improvement over the baseline.",
      significance: "With a p-value of 0.018, we have strong statistical evidence that the improvement is not due to random chance.",
      businessImpact: "This variant is suitable for release into production. Expected improvements include higher search accuracy, better consistency, and reduced latency.",
      nextSteps: [
        "Proceed with gradual rollout to production",
        "Monitor key metrics during rollout",
        "Set up alerts for latency and failure rate",
        "Plan follow-up evaluation after 2 weeks"
      ],
      caveats: [
        "Results based on 200 test queries - continue monitoring with larger sample",
        "Latency improvements may vary with production load",
        "Consider A/B testing during initial rollout"
      ]
    },
    comparisonSnapshot: [
      {
        metric: "Accuracy",
        baseline: { value: 82, unit: "%" },
        candidate: { value: 88, unit: "%" },
        delta: { absolute: 6, percentage: 7.32, direction: "positive" },
        unit: "%"
      },
      {
        metric: "Consistency",
        baseline: { value: 79, unit: "%" },
        candidate: { value: 83, unit: "%" },
        delta: { absolute: 4, percentage: 5.06, direction: "positive" },
        unit: "%"
      },
      {
        metric: "Average Latency",
        baseline: { value: 780, unit: "ms" },
        candidate: { value: 710, unit: "ms" },
        delta: { absolute: -70, percentage: -8.97, direction: "positive" },
        unit: "ms"
      }
    ],
    timeline: [
      {
        id: "step-1",
        step: "Experiment Design",
        status: "completed",
        timestamp: "2026-03-10T09:00:00Z",
        description: "Defined hypothesis and test parameters"
      },
      {
        id: "step-2",
        step: "Data Collection",
        status: "completed",
        timestamp: "2026-03-11T14:30:00Z",
        description: "Collected 200 test queries from production logs"
      },
      {
        id: "step-3",
        step: "Experiment Execution",
        status: "completed",
        timestamp: "2026-03-12T10:15:00Z",
        description: "Ran both baseline and candidate models on test dataset"
      },
      {
        id: "step-4",
        step: "Statistical Analysis",
        status: "completed",
        timestamp: "2026-03-12T16:45:00Z",
        description: "Performed hypothesis testing and calculated p-values"
      },
      {
        id: "step-5",
        step: "Release Decision",
        status: "current",
        timestamp: "2026-03-12T17:30:00Z",
        description: "Reviewing results and making release recommendation"
      },
      {
        id: "step-6",
        step: "Production Rollout",
        status: "pending",
        description: "Deploy candidate model to production"
      }
    ]
  }
]


// Legacy exports for backward compatibility
import { LegacyStatisticalResult, MetricComparison as LegacyMetricComparison } from '../types/release'

export const comparisonSnapshot: LegacyMetricComparison[] = [
  { metric: "Accuracy", baseline: "82%", candidate: "88%" },
  { metric: "Consistency", baseline: "79%", candidate: "83%" },
  { metric: "Avg latency", baseline: "780 ms", candidate: "710 ms" }
]

export const legacyReleaseDecisionData: LegacyStatisticalResult & { comparisonSnapshot: LegacyMetricComparison[] } = {
  experimentName: "Product Search Prompt Optimization",
  candidate: "Prompt v2",
  baseline: "Prompt v1", 
  runDate: "12 Mar 2026",
  datasetName: "Product Search Queries",
  status: 'Completed',
  recommendation: 'SAFE TO RELEASE',
  metric: {
    name: "Accuracy",
    baselineValue: "82%",
    candidateValue: "88%",
    improvement: "+6.0%",
    pValue: 0.018,
    confidenceLevel: 95,
    isSignificant: true
  },
  hypothesis: {
    null: "Prompt v2 is NOT better than Prompt v1",
    alternative: "Prompt v2 is better than Prompt v1",
    testType: "One-sided test",
    alpha: 0.05
  },
  testInputs: {
    datasetSize: 200,
    method: "Binomial accuracy comparison",
    sources: ["Promptfoo", "Langfuse", "Hypothesis Testing Tool"]
  },
  interpretation: {
    summary: "The candidate version demonstrates a measurable improvement over the baseline.",
    businessImplication: "This variant is suitable for release into production.",
    riskNote: "Continue monitoring latency and consistency after release."
  },
  expectedImpact: "Search success rate +5–7%",
  comparisonSnapshot
}

export const releaseDecisionId = "release-decision-search-prompt-v2-2026-03-12"
