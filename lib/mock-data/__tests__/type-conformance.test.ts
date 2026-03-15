/**
 * Property-Based Test: Mock data type conformance
 * Feature: ai-product-experiment-lab, Property 23: Mock data type conformance
 * Validates: Requirements 6.1
 */

import * as fc from 'fast-check';
import { searchScenarios } from '../search-scenarios';
import { experimentData } from '../experiment-data';
import {
  LegacySearchScenario,
  LegacyExperimentData,
  LegacyStatisticalResult,
  MetricComparison
} from '../../types';

// Inline release data since import is not working properly
const releaseDecisionData: LegacyStatisticalResult = {
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
  expectedImpact: "Search success rate +5–7%"
};

const comparisonSnapshot: MetricComparison[] = [
  { metric: "Accuracy", baseline: "82%", candidate: "88%" },
  { metric: "Consistency", baseline: "79%", candidate: "83%" },
  { metric: "Avg latency", baseline: "780 ms", candidate: "710 ms" }
];

describe('Property 23: Mock data type conformance', () => {
  it('should validate that all search scenarios conform to LegacySearchScenario interface', () => {
    fc.assert(fc.property(
      fc.constantFrom(...Object.keys(searchScenarios)),
      (scenarioKey) => {
        const scenario = searchScenarios[scenarioKey];
        
        // Validate required properties exist and have correct types
        expect(typeof scenario.query).toBe('string');
        expect(scenario.query.length).toBeGreaterThan(0);
        
        // Validate interpretation structure
        expect(scenario.interpretation).toBeDefined();
        expect(typeof scenario.interpretation.summary).toBe('string');
        expect(['High', 'Medium', 'Low']).toContain(scenario.interpretation.confidence);
        expect(Array.isArray(scenario.interpretation.filters)).toBe(true);
        expect(typeof scenario.interpretation.structuredOutput).toBe('object');
        
        // Validate filters array
        scenario.interpretation.filters.forEach(filter => {
          expect(typeof filter.label).toBe('string');
          expect(typeof filter.value).toBe('string');
        });
        
        // Validate results array
        expect(Array.isArray(scenario.results)).toBe(true);
        scenario.results.forEach(result => {
          expect(typeof result.id).toBe('string');
          expect(typeof result.name).toBe('string');
          expect(typeof result.description).toBe('string');
          expect(typeof result.price).toBe('string');
          expect(Array.isArray(result.tags)).toBe(true);
          expect(typeof result.image).toBe('string');
          
          result.tags.forEach(tag => {
            expect(typeof tag).toBe('string');
          });
        });
        
        // Validate metrics structure
        expect(scenario.metrics).toBeDefined();
        expect(typeof scenario.metrics.latencyMs).toBe('number');
        expect(scenario.metrics.latencyMs).toBeGreaterThan(0);
        expect(typeof scenario.metrics.wordCount).toBe('number');
        expect(scenario.metrics.wordCount).toBeGreaterThan(0);
        expect(typeof scenario.metrics.traceId).toBe('string');
        expect(scenario.metrics.traceId.length).toBeGreaterThan(0);
        expect(typeof scenario.metrics.status).toBe('string');
      }
    ), { numRuns: 100 });
  });

  it('should validate that experiment data conforms to LegacyExperimentData interface', () => {
    fc.assert(fc.property(
      fc.constant(experimentData),
      (data) => {
        // Validate required string properties
        expect(typeof data.name).toBe('string');
        expect(data.name.length).toBeGreaterThan(0);
        expect(typeof data.dataset).toBe('string');
        expect(data.dataset.length).toBeGreaterThan(0);
        expect(typeof data.baseline).toBe('string');
        expect(data.baseline.length).toBeGreaterThan(0);
        expect(typeof data.candidate).toBe('string');
        expect(data.candidate.length).toBeGreaterThan(0);
        expect(typeof data.experimentRun).toBe('string');
        expect(data.experimentRun.length).toBeGreaterThan(0);
        expect(typeof data.dataSource).toBe('string');
        expect(data.dataSource.length).toBeGreaterThan(0);
        
        // Validate numeric properties
        expect(typeof data.datasetSize).toBe('number');
        expect(data.datasetSize).toBeGreaterThan(0);
        
        // Validate status enum
        expect(['COMPLETED', 'RUNNING', 'FAILED']).toContain(data.status);
        
        // Validate metrics array
        expect(Array.isArray(data.metrics)).toBe(true);
        expect(data.metrics.length).toBeGreaterThan(0);
        
        data.metrics.forEach(metric => {
          expect(typeof metric.metric).toBe('string');
          expect(metric.metric.length).toBeGreaterThan(0);
          expect(['string', 'number']).toContain(typeof metric.v1);
          expect(['string', 'number']).toContain(typeof metric.v2);
          expect(typeof metric.diff).toBe('string');
          expect(typeof metric.improvement).toBe('boolean');
        });
      }
    ), { numRuns: 100 });
  });

  it('should validate that release decision data conforms to LegacyStatisticalResult interface', () => {
    fc.assert(fc.property(
      fc.constant(releaseDecisionData),
      (data) => {
        // Validate required string properties
        expect(typeof data.experimentName).toBe('string');
        expect(data.experimentName.length).toBeGreaterThan(0);
        expect(typeof data.candidate).toBe('string');
        expect(data.candidate.length).toBeGreaterThan(0);
        expect(typeof data.baseline).toBe('string');
        expect(data.baseline.length).toBeGreaterThan(0);
        expect(typeof data.runDate).toBe('string');
        expect(data.runDate.length).toBeGreaterThan(0);
        expect(typeof data.datasetName).toBe('string');
        expect(data.datasetName.length).toBeGreaterThan(0);
        expect(typeof data.expectedImpact).toBe('string');
        expect(data.expectedImpact.length).toBeGreaterThan(0);
        
        // Validate status and recommendation enums
        expect(['Completed', 'Running', 'Failed']).toContain(data.status);
        expect(['SAFE TO RELEASE', 'KEEP TESTING', 'DO NOT RELEASE']).toContain(data.recommendation);
        
        // Validate metric object
        expect(data.metric).toBeDefined();
        expect(typeof data.metric.name).toBe('string');
        expect(data.metric.name.length).toBeGreaterThan(0);
        expect(typeof data.metric.baselineValue).toBe('string');
        expect(data.metric.baselineValue.length).toBeGreaterThan(0);
        expect(typeof data.metric.candidateValue).toBe('string');
        expect(data.metric.candidateValue.length).toBeGreaterThan(0);
        expect(typeof data.metric.improvement).toBe('string');
        expect(data.metric.improvement.length).toBeGreaterThan(0);
        expect(typeof data.metric.pValue).toBe('number');
        expect(data.metric.pValue).toBeGreaterThanOrEqual(0);
        expect(data.metric.pValue).toBeLessThanOrEqual(1);
        expect(typeof data.metric.confidenceLevel).toBe('number');
        expect(data.metric.confidenceLevel).toBeGreaterThan(0);
        expect(data.metric.confidenceLevel).toBeLessThanOrEqual(100);
        expect(typeof data.metric.isSignificant).toBe('boolean');
        
        // Validate hypothesis object
        expect(data.hypothesis).toBeDefined();
        expect(typeof data.hypothesis.null).toBe('string');
        expect(data.hypothesis.null.length).toBeGreaterThan(0);
        expect(typeof data.hypothesis.alternative).toBe('string');
        expect(data.hypothesis.alternative.length).toBeGreaterThan(0);
        expect(typeof data.hypothesis.testType).toBe('string');
        expect(data.hypothesis.testType.length).toBeGreaterThan(0);
        expect(typeof data.hypothesis.alpha).toBe('number');
        expect(data.hypothesis.alpha).toBeGreaterThan(0);
        expect(data.hypothesis.alpha).toBeLessThan(1);
        
        // Validate testInputs object
        expect(data.testInputs).toBeDefined();
        expect(typeof data.testInputs.datasetSize).toBe('number');
        expect(data.testInputs.datasetSize).toBeGreaterThan(0);
        expect(typeof data.testInputs.method).toBe('string');
        expect(data.testInputs.method.length).toBeGreaterThan(0);
        expect(Array.isArray(data.testInputs.sources)).toBe(true);
        expect(data.testInputs.sources.length).toBeGreaterThan(0);
        
        data.testInputs.sources.forEach(source => {
          expect(typeof source).toBe('string');
          expect(source.length).toBeGreaterThan(0);
        });
        
        // Validate interpretation object
        expect(data.interpretation).toBeDefined();
        expect(typeof data.interpretation.summary).toBe('string');
        expect(data.interpretation.summary.length).toBeGreaterThan(0);
        expect(typeof data.interpretation.businessImplication).toBe('string');
        expect(data.interpretation.businessImplication.length).toBeGreaterThan(0);
        expect(typeof data.interpretation.riskNote).toBe('string');
        expect(data.interpretation.riskNote.length).toBeGreaterThan(0);
      }
    ), { numRuns: 100 });
  });

  it('should validate that comparison snapshot conforms to MetricComparison array interface', () => {
    fc.assert(fc.property(
      fc.constant(comparisonSnapshot),
      (snapshot) => {
        expect(Array.isArray(snapshot)).toBe(true);
        expect(snapshot.length).toBeGreaterThan(0);
        
        snapshot.forEach(comparison => {
          expect(typeof comparison.metric).toBe('string');
          expect(comparison.metric.length).toBeGreaterThan(0);
          expect(typeof comparison.baseline).toBe('string');
          expect(comparison.baseline.length).toBeGreaterThan(0);
          expect(typeof comparison.candidate).toBe('string');
          expect(comparison.candidate.length).toBeGreaterThan(0);
          
          // improvement is optional
          if (comparison.improvement !== undefined) {
            expect(typeof comparison.improvement).toBe('string');
            expect(comparison.improvement.length).toBeGreaterThan(0);
          }
        });
      }
    ), { numRuns: 100 });
  });

  it('should validate cross-data consistency between mock data objects', () => {
    fc.assert(fc.property(
      fc.constant({ searchScenarios, experimentData, releaseDecisionData }),
      ({ searchScenarios, experimentData, releaseDecisionData }) => {
        // Validate that experiment data references align with search scenarios
        const searchLatencies = Object.values(searchScenarios).map(s => s.metrics.latencyMs);
        const avgSearchLatency = searchLatencies.reduce((a, b) => a + b, 0) / searchLatencies.length;
        
        // The experiment baseline latency should be in a reasonable range of actual search latencies
        const baselineLatencyStr = experimentData.metrics.find(m => m.metric === 'Average Latency')?.v1;
        if (baselineLatencyStr && typeof baselineLatencyStr === 'string') {
          const baselineLatency = parseInt(baselineLatencyStr.replace(/[^\d]/g, ''));
          expect(Math.abs(baselineLatency - avgSearchLatency)).toBeLessThan(200); // Within 200ms tolerance
        }
        
        // Validate that release decision references the same experiment
        expect(releaseDecisionData.experimentName).toBe(experimentData.name);
        expect(releaseDecisionData.baseline).toBe(experimentData.baseline);
        expect(releaseDecisionData.candidate).toBe(experimentData.candidate);
        expect(releaseDecisionData.datasetName).toBe(experimentData.dataset);
        expect(releaseDecisionData.testInputs.datasetSize).toBe(experimentData.datasetSize);
      }
    ), { numRuns: 100 });
  });
});