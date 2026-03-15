// Release decision types
import { MetricComparison as ExperimentMetricComparison } from './experiments';

export interface ReleaseDecisionScenario {
  id: string;
  experimentId: string;
  recommendation: ReleaseRecommendation;
  statisticalSummary: StatisticalSummary;
  hypothesis: HypothesisTest;
  interpretation: BusinessInterpretation;
  comparisonSnapshot: ExperimentMetricComparison[];
  timeline: DecisionStep[];
}

export interface ReleaseRecommendation {
  decision: 'Safe to release' | 'Needs more evidence' | 'Do not release';
  confidence: number;
  rationale: string;
  expectedImpact: string[];
  riskAssessment?: string;
}

export interface StatisticalSummary {
  nullHypothesis: string;
  datasetSize: number;
  pValue: number;
  confidenceLevel: number;
  conclusion: string;
  significanceThreshold: number;
}

export interface HypothesisTest {
  baseline: string;
  candidate: string;
  metric: string;
  sampleSize: number;
  testType: string;
  assumptions: string[];
}

export interface BusinessInterpretation {
  summary: string;
  significance: string;
  businessImpact: string;
  nextSteps: string[];
  caveats?: string[];
}

export interface DecisionStep {
  id: string;
  step: string;
  status: 'completed' | 'current' | 'pending';
  timestamp?: string;
  description?: string;
}

export interface MetricComparison {
  metric: string;
  baseline: string;
  candidate: string;
  improvement?: string;
}

// Legacy interface for backward compatibility with existing components
export interface LegacyStatisticalResult {
  experimentName: string;
  candidate: string;
  baseline: string;
  runDate: string;
  datasetName: string;
  status: 'Completed' | 'Running' | 'Failed';
  recommendation: 'SAFE TO RELEASE' | 'KEEP TESTING' | 'DO NOT RELEASE';
  metric: {
    name: string;
    baselineValue: string;
    candidateValue: string;
    improvement: string;
    pValue: number;
    confidenceLevel: number;
    isSignificant: boolean;
  };
  hypothesis: {
    null: string;
    alternative: string;
    testType: string;
    alpha: number;
  };
  testInputs: {
    datasetSize: number;
    method: string;
    sources: string[];
  };
  interpretation: {
    summary: string;
    businessImplication: string;
    riskNote: string;
  };
  expectedImpact: string;
}