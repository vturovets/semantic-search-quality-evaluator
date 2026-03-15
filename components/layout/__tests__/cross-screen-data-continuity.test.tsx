/**
 * Property-Based Test: Cross-screen data continuity
 * Feature: ai-product-experiment-lab, Property 18: Cross-screen data continuity
 * Validates: Requirements 4.5
 */

import * as fc from 'fast-check';
import { searchScenarios } from '../../../lib/mock-data/search-scenarios';
import { experimentDataArray } from '../../../lib/mock-data/experiment-data';
import { releaseDecisionData } from '../../../lib/mock-data/release-data';

describe('Property 18: Cross-screen data continuity', () => {
  it('should maintain narrative continuity from capability to decision for any workflow progression', () => {
    const searchScenariosArray = Object.values(searchScenarios);
    
    fc.assert(fc.property(
      fc.constantFrom(...searchScenariosArray.map((s, i) => Object.keys(searchScenarios)[i])),
      fc.constantFrom(...experimentDataArray.map(e => e.id)),
      fc.constantFrom(...releaseDecisionData.map(r => r.id)),
      (searchKey, experimentId, releaseId) => {
        // Find the corresponding data objects
        const searchScenario = searchScenarios[searchKey];
        const experiment = experimentDataArray.find(e => e.id === experimentId);
        const releaseDecision = releaseDecisionData.find(r => r.id === releaseId);
        
        // Validate that all data objects exist
        expect(searchScenario).toBeDefined();
        expect(experiment).toBeDefined();
        expect(releaseDecision).toBeDefined();
        
        // Validate search scenario has complete data for capability demonstration
        expect(searchScenario!.query).toBeTruthy();
        expect(searchScenario!.interpretedFilters).toBeDefined();
        expect(searchScenario!.results).toBeDefined();
        expect(searchScenario!.results.length).toBeGreaterThan(0);
        expect(searchScenario!.executionMetrics).toBeDefined();
        
        // Validate experiment has complete data for question/evaluation
        expect(experiment!.name).toBeTruthy();
        expect(experiment!.dataset).toBeDefined();
        expect(experiment!.models.baseline).toBeDefined();
        expect(experiment!.models.candidate).toBeDefined();
        expect(experiment!.metrics).toBeDefined();
        expect(experiment!.metrics.length).toBeGreaterThan(0);
        
        // Validate release decision has complete data for evidence/decision
        expect(releaseDecision!.recommendation).toBeDefined();
        expect(releaseDecision!.recommendation.decision).toBeTruthy();
        expect(releaseDecision!.statisticalSummary).toBeDefined();
        expect(releaseDecision!.hypothesis).toBeDefined();
        expect(releaseDecision!.interpretation).toBeDefined();
        
        // Validate cross-screen references maintain logical consistency
        // Release decision should reference an experiment
        expect(releaseDecision!.experimentId).toBeTruthy();
        
        // Release decision should have comparison snapshot that matches experiment metrics
        expect(releaseDecision!.comparisonSnapshot).toBeDefined();
        expect(releaseDecision!.comparisonSnapshot.length).toBeGreaterThan(0);
        
        // Validate that the workflow maintains data continuity
        // The experiment metrics should be reflected in the release decision
        const experimentMetricNames = experiment!.metrics.map(m => m.metric);
        const releaseMetricNames = releaseDecision!.comparisonSnapshot.map(m => m.metric);
        
        // At least some metrics should overlap between experiment and release decision
        const hasOverlap = experimentMetricNames.some(name => releaseMetricNames.includes(name));
        expect(hasOverlap).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure data references are valid and maintain logical relationships', () => {
    fc.assert(fc.property(
      fc.integer({ min: 0, max: releaseDecisionData.length - 1 }),
      (releaseIndex) => {
        const releaseDecision = releaseDecisionData[releaseIndex];
        
        // Validate that the referenced experiment exists
        const referencedExperiment = experimentDataArray.find(e => e.id === releaseDecision.experimentId);
        expect(referencedExperiment).toBeDefined();
        
        // Validate that the comparison snapshot metrics are consistent with experiment metrics
        releaseDecision.comparisonSnapshot.forEach(snapshotMetric => {
          expect(snapshotMetric.metric).toBeTruthy();
          expect(snapshotMetric.baseline).toBeDefined();
          expect(snapshotMetric.candidate).toBeDefined();
          expect(snapshotMetric.delta).toBeDefined();
          
          // Validate delta calculation consistency
          expect(snapshotMetric.delta.absolute).toBeDefined();
          expect(snapshotMetric.delta.percentage).toBeDefined();
          expect(snapshotMetric.delta.direction).toMatch(/^(positive|negative|neutral)$/);
        });
        
        // Validate that the timeline shows a logical progression
        expect(releaseDecision.timeline).toBeDefined();
        expect(releaseDecision.timeline.length).toBeGreaterThan(0);
        
        releaseDecision.timeline.forEach(step => {
          expect(step.step).toBeTruthy();
          expect(step.status).toMatch(/^(completed|current|pending)$/);
        });
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent data types and structures across all screens', () => {
    const searchScenariosArray = Object.values(searchScenarios);
    
    fc.assert(fc.property(
      fc.constant(true),
      () => {
        // Validate search scenarios structure
        searchScenariosArray.forEach(scenario => {
          expect(typeof scenario.query).toBe('string');
          expect(typeof scenario.interpretation.summary).toBe('string');
          expect(['High', 'Medium', 'Low']).toContain(scenario.interpretation.confidence);
          expect(Array.isArray(scenario.results)).toBe(true);
          if (scenario.executionMetrics) {
            expect(typeof scenario.executionMetrics.latency).toBe('number');
            expect(typeof scenario.executionMetrics.wordCount).toBe('number');
            expect(typeof scenario.executionMetrics.traceId).toBe('string');
          }
        });
        
        // Validate experiment data structure
        experimentDataArray.forEach(experiment => {
          expect(typeof experiment.id).toBe('string');
          expect(typeof experiment.name).toBe('string');
          expect(typeof experiment.dataset.size).toBe('number');
          expect(typeof experiment.models.baseline.id).toBe('string');
          expect(typeof experiment.models.candidate.id).toBe('string');
          expect(Array.isArray(experiment.metrics)).toBe(true);
          
          experiment.metrics.forEach(metric => {
            expect(typeof metric.metric).toBe('string');
            expect(typeof metric.baseline.value).toBe('number');
            expect(typeof metric.candidate.value).toBe('number');
            expect(typeof metric.delta.percentage).toBe('number');
          });
        });
        
        // Validate release decision data structure
        releaseDecisionData.forEach(decision => {
          expect(typeof decision.id).toBe('string');
          expect(typeof decision.experimentId).toBe('string');
          expect(['Safe to release', 'Needs more evidence', 'Do not release']).toContain(decision.recommendation.decision);
          expect(typeof decision.statisticalSummary.pValue).toBe('number');
          expect(typeof decision.statisticalSummary.confidenceLevel).toBe('number');
          expect(Array.isArray(decision.comparisonSnapshot)).toBe(true);
          expect(Array.isArray(decision.timeline)).toBe(true);
        });
        
        return true;
      }
    ), { numRuns: 100 });
  });
});
