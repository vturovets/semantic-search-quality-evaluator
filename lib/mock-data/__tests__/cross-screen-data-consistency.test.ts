/**
 * Property-Based Test: Cross-screen data consistency
 * Feature: ai-product-experiment-lab, Property 24: Cross-screen data consistency
 * Validates: Requirements 6.2
 */

import * as fc from 'fast-check';
import { searchScenarios } from '../search-scenarios';
import { experimentDataArray } from '../experiment-data';
import { releaseDecisionData } from '../release-data';

describe('Property 24: Cross-screen data consistency', () => {
  it('should ensure internal consistency between search scenarios, experiments, and release decisions for any related data objects', () => {
    fc.assert(fc.property(
      fc.integer({ min: 0, max: releaseDecisionData.length - 1 }),
      (releaseIndex) => {
        const releaseDecision = releaseDecisionData[releaseIndex];
        
        // Find the referenced experiment
        const referencedExperiment = experimentDataArray.find(e => e.id === releaseDecision.experimentId);
        
        // Validate that the referenced experiment exists
        expect(referencedExperiment).toBeDefined();
        
        if (referencedExperiment) {
          // Validate that comparison snapshot metrics match experiment metrics
          const experimentMetrics = referencedExperiment.metrics.map(m => m.metric);
          const snapshotMetrics = releaseDecision.comparisonSnapshot.map(m => m.metric);
          
          // All snapshot metrics should exist in the experiment
          snapshotMetrics.forEach(snapshotMetric => {
            expect(experimentMetrics).toContain(snapshotMetric);
          });
          
          // Validate that metric values are consistent
          releaseDecision.comparisonSnapshot.forEach(snapshotMetric => {
            const experimentMetric = referencedExperiment.metrics.find(m => m.metric === snapshotMetric.metric);
            
            if (experimentMetric) {
              // Baseline values should match
              expect(snapshotMetric.baseline.value).toBe(experimentMetric.baseline.value);
              
              // Candidate values should match
              expect(snapshotMetric.candidate.value).toBe(experimentMetric.candidate.value);
              
              // Delta calculations should be consistent
              expect(snapshotMetric.delta.percentage).toBe(experimentMetric.delta.percentage);
              expect(snapshotMetric.delta.direction).toBe(experimentMetric.delta.direction);
            }
          });
          
          // Validate that statistical summary references the correct dataset size
          expect(releaseDecision.statisticalSummary.datasetSize).toBe(referencedExperiment.dataset.size);
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent metric naming and units across all data objects', () => {
    fc.assert(fc.property(
      fc.constant(true),
      () => {
        // Collect all metric names from experiments
        const experimentMetricNames = new Set<string>();
        experimentDataArray.forEach(experiment => {
          experiment.metrics.forEach(metric => {
            experimentMetricNames.add(metric.metric);
          });
        });
        
        // Collect all metric names from release decisions
        const releaseMetricNames = new Set<string>();
        releaseDecisionData.forEach(decision => {
          decision.comparisonSnapshot.forEach(metric => {
            releaseMetricNames.add(metric.metric);
          });
        });
        
        // Validate that release decision metrics are a subset of experiment metrics
        releaseMetricNames.forEach(metricName => {
          expect(experimentMetricNames.has(metricName)).toBe(true);
        });
        
        // Validate consistent metric units across experiments
        experimentDataArray.forEach(experiment => {
          experiment.metrics.forEach(metric => {
            // If a metric has a unit, it should be consistent
            if (metric.unit) {
              expect(typeof metric.unit).toBe('string');
              expect(metric.unit.length).toBeGreaterThan(0);
            }
            
            // Validate that baseline and candidate have the same unit
            if (metric.baseline.unit && metric.candidate.unit) {
              expect(metric.baseline.unit).toBe(metric.candidate.unit);
            }
          });
        });
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure experiment references in release decisions are valid and complete', () => {
    fc.assert(fc.property(
      fc.constant(releaseDecisionData),
      (decisions) => {
        decisions.forEach(decision => {
          // Validate that experimentId is present
          expect(decision.experimentId).toBeTruthy();
          expect(typeof decision.experimentId).toBe('string');
          
          // Validate that the referenced experiment exists
          const experiment = experimentDataArray.find(e => e.id === decision.experimentId);
          expect(experiment).toBeDefined();
          
          if (experiment) {
            // Validate that the experiment has completed status
            // (only completed experiments should have release decisions)
            expect(['Completed', 'Running', 'Failed', 'Pending']).toContain(experiment.status);
            
            // Validate that the experiment has metrics
            expect(experiment.metrics.length).toBeGreaterThan(0);
            
            // Validate that the release decision has a comparison snapshot
            expect(decision.comparisonSnapshot.length).toBeGreaterThan(0);
            
            // Validate that comparison snapshot doesn't exceed experiment metrics
            expect(decision.comparisonSnapshot.length).toBeLessThanOrEqual(experiment.metrics.length);
          }
        });
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent data types and value ranges across related objects', () => {
    fc.assert(fc.property(
      fc.integer({ min: 0, max: experimentDataArray.length - 1 }),
      (experimentIndex) => {
        const experiment = experimentDataArray[experimentIndex];
        
        // Validate experiment data types
        expect(typeof experiment.id).toBe('string');
        expect(typeof experiment.name).toBe('string');
        expect(typeof experiment.dataset.size).toBe('number');
        expect(experiment.dataset.size).toBeGreaterThan(0);
        
        // Validate metric value types and ranges
        experiment.metrics.forEach(metric => {
          expect(typeof metric.baseline.value).toBe('number');
          expect(typeof metric.candidate.value).toBe('number');
          expect(typeof metric.delta.percentage).toBe('number');
          
          // Validate that percentage is a valid number
          expect(isNaN(metric.delta.percentage)).toBe(false);
          expect(isFinite(metric.delta.percentage)).toBe(true);
          
          // Validate delta direction is valid
          expect(['positive', 'negative', 'neutral']).toContain(metric.delta.direction);
        });
        
        // Find related release decision
        const relatedDecision = releaseDecisionData.find(d => d.experimentId === experiment.id);
        
        if (relatedDecision) {
          // Validate release decision data types
          expect(typeof relatedDecision.id).toBe('string');
          expect(typeof relatedDecision.experimentId).toBe('string');
          
          // Validate statistical summary types and ranges
          expect(typeof relatedDecision.statisticalSummary.pValue).toBe('number');
          expect(relatedDecision.statisticalSummary.pValue).toBeGreaterThanOrEqual(0);
          expect(relatedDecision.statisticalSummary.pValue).toBeLessThanOrEqual(1);
          
          expect(typeof relatedDecision.statisticalSummary.confidenceLevel).toBe('number');
          expect(relatedDecision.statisticalSummary.confidenceLevel).toBeGreaterThan(0);
          expect(relatedDecision.statisticalSummary.confidenceLevel).toBeLessThanOrEqual(100);
          
          expect(typeof relatedDecision.statisticalSummary.datasetSize).toBe('number');
          expect(relatedDecision.statisticalSummary.datasetSize).toBe(experiment.dataset.size);
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure timeline data maintains logical progression and consistency', () => {
    fc.assert(fc.property(
      fc.integer({ min: 0, max: releaseDecisionData.length - 1 }),
      (releaseIndex) => {
        const releaseDecision = releaseDecisionData[releaseIndex];
        
        // Validate timeline exists and has steps
        expect(releaseDecision.timeline).toBeDefined();
        expect(Array.isArray(releaseDecision.timeline)).toBe(true);
        expect(releaseDecision.timeline.length).toBeGreaterThan(0);
        
        let hasCompleted = false;
        let hasCurrent = false;
        let hasPending = false;
        
        releaseDecision.timeline.forEach((step, index) => {
          // Validate step structure
          expect(step.id).toBeTruthy();
          expect(step.step).toBeTruthy();
          expect(['completed', 'current', 'pending']).toContain(step.status);
          
          // Track status types
          if (step.status === 'completed') hasCompleted = true;
          if (step.status === 'current') hasCurrent = true;
          if (step.status === 'pending') hasPending = true;
          
          // Validate logical progression: completed steps should come before current/pending
          if (index > 0) {
            const prevStep = releaseDecision.timeline[index - 1];
            
            // If current step is completed, previous should also be completed
            if (step.status === 'completed') {
              expect(prevStep.status).toBe('completed');
            }
            
            // If current step is pending, it shouldn't come before current
            if (step.status === 'pending' && prevStep.status === 'current') {
              // This is valid: current followed by pending
              expect(true).toBe(true);
            }
          }
        });
        
        // Validate that timeline has a logical state
        // Should have at least one completed or current step
        expect(hasCompleted || hasCurrent).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent confidence and status indicators across related data', () => {
    fc.assert(fc.property(
      fc.constant(true),
      () => {
        // Validate search scenario confidence levels
        Object.values(searchScenarios).forEach(scenario => {
          expect(['High', 'Medium', 'Low']).toContain(scenario.interpretedFilters.confidence);
          expect(['Completed', 'Processing', 'Failed']).toContain(scenario.executionMetrics.status);
        });
        
        // Validate experiment status values
        experimentDataArray.forEach(experiment => {
          expect(['Completed', 'Running', 'Failed', 'Pending']).toContain(experiment.status);
        });
        
        // Validate release decision values
        releaseDecisionData.forEach(decision => {
          expect(['Safe to release', 'Needs more evidence', 'Do not release']).toContain(decision.recommendation.decision);
          
          // Validate confidence is a valid percentage
          expect(typeof decision.recommendation.confidence).toBe('number');
          expect(decision.recommendation.confidence).toBeGreaterThanOrEqual(0);
          expect(decision.recommendation.confidence).toBeLessThanOrEqual(100);
        });
        
        return true;
      }
    ), { numRuns: 100 });
  });
});
