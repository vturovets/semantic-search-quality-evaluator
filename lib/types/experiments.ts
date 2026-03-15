// Experiment data types

export interface ExperimentSummary {
  id: string;
  name: string;
  description: string;
  dataset: {
    name: string;
    size: number;
    source: string;
  };
  models: {
    baseline: ModelVersion;
    candidate: ModelVersion;
  };
  runDate: string;
  status: ExperimentStatus;
  metrics: MetricComparison[];
}

export interface ModelVersion {
  id: string;
  name: string;
  version: string;
  description?: string;
}

export interface MetricComparison {
  metric: string;
  baseline: MetricValue;
  candidate: MetricValue;
  delta: {
    absolute: number;
    percentage: number;
    direction: 'positive' | 'negative' | 'neutral';
  };
  unit?: string;
}

export interface MetricValue {
  value: number;
  unit?: string;
  confidence?: number;
}

export type ExperimentStatus = 'Completed' | 'Running' | 'Failed' | 'Pending';

// Legacy interface for backward compatibility with existing components
export interface LegacyExperimentData {
  name: string;
  dataset: string;
  datasetSize: number;
  baseline: string;
  candidate: string;
  experimentRun: string;
  dataSource: string;
  metrics: {
    metric: string;
    v1: string | number;
    v2: string | number;
    diff: string;
    improvement: boolean;
  }[];
  status: 'COMPLETED' | 'RUNNING' | 'FAILED';
}