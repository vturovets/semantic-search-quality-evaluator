// Experiment metrics and comparisons

import { LegacyExperimentData, ExperimentSummary } from '../types/experiments';

export const experimentData: LegacyExperimentData = {
  name: "Product Search Prompt Optimization",
  dataset: "Product Search Queries",
  datasetSize: 200,
  baseline: "Prompt v1",
  candidate: "Prompt v2", 
  experimentRun: "12 Mar 2026",
  dataSource: "Promptfoo evaluation dataset",
  metrics: [
    { metric: "Accuracy", v1: "82%", v2: "88%", diff: "+6%", improvement: true },
    { metric: "Consistency", v1: "79%", v2: "83%", diff: "+4%", improvement: true },
    { metric: "Average Latency", v1: "780 ms", v2: "710 ms", diff: "-70 ms", improvement: true },
    { metric: "Failure Rate", v1: "11%", v2: "7%", diff: "-4%", improvement: true }
  ],
  status: 'COMPLETED'
};

// Data consistency: This experiment data connects to the search scenarios
// The search query "Find cheap winter running shoes" is part of the 200 queries dataset
// The latency improvements (780ms -> 710ms) align with search metrics (740ms average)
export const experimentId = "exp-search-prompt-v2-2026-03-12";
export const experimentDescription = "Comparing baseline search prompt against optimized version for natural language product queries";

// Metrics for visualization components
export const accuracyComparison = {
  baseline: { label: "Prompt v1", value: "82%", percentage: 82 },
  candidate: { label: "Prompt v2", value: "88%", percentage: 88 }
};

export const latencyComparison = {
  baseline: { label: "Prompt v1", value: "780ms", percentage: 78 },
  candidate: { label: "Prompt v2", value: "710ms", percentage: 71 }
};

// New ExperimentSummary data matching the proper interface
export const experimentSummary: ExperimentSummary = {
  id: experimentId,
  name: "Product Search Prompt Optimization",
  description: experimentDescription,
  dataset: {
    name: "Product Search Queries",
    size: 200,
    source: "Promptfoo evaluation dataset"
  },
  models: {
    baseline: {
      id: "prompt-v1",
      name: "Prompt v1",
      version: "1.0.0",
      description: "Original search prompt template"
    },
    candidate: {
      id: "prompt-v2", 
      name: "Prompt v2",
      version: "2.0.0",
      description: "Optimized search prompt with better context handling"
    }
  },
  runDate: "12 Mar 2026",
  status: "Completed",
  metrics: [
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
    },
    {
      metric: "Failure Rate",
      baseline: { value: 11, unit: "%" },
      candidate: { value: 7, unit: "%" },
      delta: { absolute: -4, percentage: -36.36, direction: "positive" },
      unit: "%"
    }
  ]
};

// Export as array for consistency with design document
export const experimentDataArray: ExperimentSummary[] = [experimentSummary];