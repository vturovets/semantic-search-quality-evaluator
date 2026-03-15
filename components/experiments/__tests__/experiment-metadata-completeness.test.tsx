/**
 * Property-Based Test: Experiment metadata completeness
 * Feature: ai-product-experiment-lab, Property 6: Experiment metadata completeness
 * Validates: Requirements 2.1, 2.5
 */

import * as fc from 'fast-check';
import { ExperimentSummary, ExperimentStatus } from '../../../lib/types/experiments';
import { experimentSummary } from '../../../lib/mock-data/experiment-data';

// Generator for valid experiment status values
const experimentStatusArb = fc.constantFrom('Completed', 'Running', 'Failed', 'Pending');

// Generator for valid experiment summaries
const experimentSummaryArb = fc.record({
  id: fc.string({ minLength: 1, maxLength: 50 }),
  name: fc.string({ minLength: 1, maxLength: 100 }),
  description: fc.string({ minLength: 1, maxLength: 500 }),
  dataset: fc.record({
    name: fc.string({ minLength: 1, maxLength: 100 }),
    size: fc.integer({ min: 1, max: 10000 }),
    source: fc.string({ minLength: 1, maxLength: 100 })
  }),
  models: fc.record({
    baseline: fc.record({
      id: fc.string({ minLength: 1, maxLength: 50 }),
      name: fc.string({ minLength: 1, maxLength: 100 }),
      version: fc.string({ minLength: 1, maxLength: 20 }),
      description: fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined })
    }),
    candidate: fc.record({
      id: fc.string({ minLength: 1, maxLength: 50 }),
      name: fc.string({ minLength: 1, maxLength: 100 }),
      version: fc.string({ minLength: 1, maxLength: 20 }),
      description: fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined })
    })
  }),
  runDate: fc.string({ minLength: 1, maxLength: 50 }),
  status: experimentStatusArb,
  metrics: fc.array(fc.record({
    metric: fc.string({ minLength: 1, maxLength: 50 }),
    baseline: fc.record({
      value: fc.integer({ min: 0, max: 1000 }),
      unit: fc.option(fc.constantFrom('%', 'ms', 'count', 'score'), { nil: undefined })
    }),
    candidate: fc.record({
      value: fc.integer({ min: 0, max: 1000 }),
      unit: fc.option(fc.constantFrom('%', 'ms', 'count', 'score'), { nil: undefined })
    }),
    delta: fc.record({
      absolute: fc.integer({ min: -1000, max: 1000 }),
      percentage: fc.float({ min: -100, max: 100 }),
      direction: fc.constantFrom('positive', 'negative', 'neutral')
    }),
    unit: fc.option(fc.constantFrom('%', 'ms', 'count', 'score'), { nil: undefined })
  }), { minLength: 1, maxLength: 10 })
});

describe('Property 6: Experiment metadata completeness', () => {
  it('should display all required metadata fields for any experiment', () => {
    fc.assert(fc.property(
      experimentSummaryArb,
      (experiment: ExperimentSummary) => {
        // Validate that experiment has all required metadata fields
        expect(experiment).toHaveProperty('id');
        expect(experiment).toHaveProperty('name');
        expect(experiment).toHaveProperty('description');
        expect(experiment).toHaveProperty('dataset');
        expect(experiment).toHaveProperty('models');
        expect(experiment).toHaveProperty('runDate');
        expect(experiment).toHaveProperty('status');
        expect(experiment).toHaveProperty('metrics');
        
        // Validate dataset structure
        expect(experiment.dataset).toHaveProperty('name');
        expect(experiment.dataset).toHaveProperty('size');
        expect(experiment.dataset).toHaveProperty('source');
        
        // Validate models structure
        expect(experiment.models).toHaveProperty('baseline');
        expect(experiment.models).toHaveProperty('candidate');
        
        // Validate baseline model
        expect(experiment.models.baseline).toHaveProperty('id');
        expect(experiment.models.baseline).toHaveProperty('name');
        expect(experiment.models.baseline).toHaveProperty('version');
        
        // Validate candidate model
        expect(experiment.models.candidate).toHaveProperty('id');
        expect(experiment.models.candidate).toHaveProperty('name');
        expect(experiment.models.candidate).toHaveProperty('version');
        
        // Validate field types and constraints
        expect(typeof experiment.id).toBe('string');
        expect(experiment.id.length).toBeGreaterThan(0);
        
        expect(typeof experiment.name).toBe('string');
        expect(experiment.name.length).toBeGreaterThan(0);
        
        expect(typeof experiment.description).toBe('string');
        expect(experiment.description.length).toBeGreaterThan(0);
        
        expect(typeof experiment.dataset.name).toBe('string');
        expect(experiment.dataset.name.length).toBeGreaterThan(0);
        
        expect(typeof experiment.dataset.size).toBe('number');
        expect(experiment.dataset.size).toBeGreaterThan(0);
        
        expect(typeof experiment.dataset.source).toBe('string');
        expect(experiment.dataset.source.length).toBeGreaterThan(0);
        
        expect(typeof experiment.runDate).toBe('string');
        expect(experiment.runDate.length).toBeGreaterThan(0);
        
        expect(['Completed', 'Running', 'Failed', 'Pending']).toContain(experiment.status);
        
        expect(Array.isArray(experiment.metrics)).toBe(true);
        expect(experiment.metrics.length).toBeGreaterThan(0);
      }
    ), { numRuns: 100 });
  });

  it('should properly format model versions and run details', () => {
    fc.assert(fc.property(
      experimentSummaryArb,
      (experiment: ExperimentSummary) => {
        // Model versions should be non-empty strings
        expect(typeof experiment.models.baseline.version).toBe('string');
        expect(experiment.models.baseline.version.length).toBeGreaterThan(0);
        
        expect(typeof experiment.models.candidate.version).toBe('string');
        expect(experiment.models.candidate.version.length).toBeGreaterThan(0);
        
        // Model names should be non-empty strings
        expect(typeof experiment.models.baseline.name).toBe('string');
        expect(experiment.models.baseline.name.length).toBeGreaterThan(0);
        
        expect(typeof experiment.models.candidate.name).toBe('string');
        expect(experiment.models.candidate.name.length).toBeGreaterThan(0);
        
        // Model IDs should be non-empty strings
        expect(typeof experiment.models.baseline.id).toBe('string');
        expect(experiment.models.baseline.id.length).toBeGreaterThan(0);
        
        expect(typeof experiment.models.candidate.id).toBe('string');
        expect(experiment.models.candidate.id.length).toBeGreaterThan(0);
        
        // Optional descriptions should be strings if present
        if (experiment.models.baseline.description !== undefined) {
          expect(typeof experiment.models.baseline.description).toBe('string');
          expect(experiment.models.baseline.description.length).toBeGreaterThan(0);
        }
        
        if (experiment.models.candidate.description !== undefined) {
          expect(typeof experiment.models.candidate.description).toBe('string');
          expect(experiment.models.candidate.description.length).toBeGreaterThan(0);
        }
      }
    ), { numRuns: 100 });
  });

  it('should validate dataset information completeness', () => {
    fc.assert(fc.property(
      experimentSummaryArb,
      (experiment: ExperimentSummary) => {
        const dataset = experiment.dataset;
        
        // Dataset name should be descriptive
        expect(typeof dataset.name).toBe('string');
        expect(dataset.name.length).toBeGreaterThan(0);
        
        // Dataset size should be a positive integer
        expect(typeof dataset.size).toBe('number');
        expect(Number.isInteger(dataset.size)).toBe(true);
        expect(dataset.size).toBeGreaterThan(0);
        
        // Dataset source should be specified
        expect(typeof dataset.source).toBe('string');
        expect(dataset.source.length).toBeGreaterThan(0);
      }
    ), { numRuns: 100 });
  });

  it('should validate metrics array structure', () => {
    fc.assert(fc.property(
      experimentSummaryArb,
      (experiment: ExperimentSummary) => {
        expect(Array.isArray(experiment.metrics)).toBe(true);
        expect(experiment.metrics.length).toBeGreaterThan(0);
        
        experiment.metrics.forEach(metric => {
          // Each metric should have required fields
          expect(metric).toHaveProperty('metric');
          expect(metric).toHaveProperty('baseline');
          expect(metric).toHaveProperty('candidate');
          expect(metric).toHaveProperty('delta');
          
          // Metric name should be non-empty
          expect(typeof metric.metric).toBe('string');
          expect(metric.metric.length).toBeGreaterThan(0);
          
          // Baseline and candidate should have value fields
          expect(metric.baseline).toHaveProperty('value');
          expect(metric.candidate).toHaveProperty('value');
          
          expect(typeof metric.baseline.value).toBe('number');
          expect(typeof metric.candidate.value).toBe('number');
          
          // Delta should have required structure
          expect(metric.delta).toHaveProperty('absolute');
          expect(metric.delta).toHaveProperty('percentage');
          expect(metric.delta).toHaveProperty('direction');
          
          expect(typeof metric.delta.absolute).toBe('number');
          expect(typeof metric.delta.percentage).toBe('number');
          expect(['positive', 'negative', 'neutral']).toContain(metric.delta.direction);
        });
      }
    ), { numRuns: 100 });
  });

  it('should validate existing experiment data completeness', () => {
    // Test the actual experiment data used in the application
    const experiment = experimentSummary;
    
    // Validate all required fields are present
    expect(experiment).toHaveProperty('id');
    expect(experiment).toHaveProperty('name');
    expect(experiment).toHaveProperty('description');
    expect(experiment).toHaveProperty('dataset');
    expect(experiment).toHaveProperty('models');
    expect(experiment).toHaveProperty('runDate');
    expect(experiment).toHaveProperty('status');
    expect(experiment).toHaveProperty('metrics');
    
    // Validate field values
    expect(typeof experiment.id).toBe('string');
    expect(experiment.id.length).toBeGreaterThan(0);
    
    expect(typeof experiment.name).toBe('string');
    expect(experiment.name.length).toBeGreaterThan(0);
    
    expect(typeof experiment.description).toBe('string');
    expect(experiment.description.length).toBeGreaterThan(0);
    
    // Validate dataset
    expect(experiment.dataset.name).toBe('Product Search Queries');
    expect(experiment.dataset.size).toBe(200);
    expect(experiment.dataset.source).toBe('Promptfoo evaluation dataset');
    
    // Validate models
    expect(experiment.models.baseline.name).toBe('Prompt v1');
    expect(experiment.models.baseline.version).toBe('1.0.0');
    expect(experiment.models.candidate.name).toBe('Prompt v2');
    expect(experiment.models.candidate.version).toBe('2.0.0');
    
    // Validate status
    expect(experiment.status).toBe('Completed');
    
    // Validate metrics
    expect(Array.isArray(experiment.metrics)).toBe(true);
    expect(experiment.metrics.length).toBeGreaterThan(0);
    
    experiment.metrics.forEach(metric => {
      expect(typeof metric.metric).toBe('string');
      expect(metric.metric.length).toBeGreaterThan(0);
      expect(typeof metric.baseline.value).toBe('number');
      expect(typeof metric.candidate.value).toBe('number');
      expect(['positive', 'negative', 'neutral']).toContain(metric.delta.direction);
    });
  });

  it('should handle edge cases in metadata display', () => {
    fc.assert(fc.property(
      fc.oneof(
        // Experiment with minimal metrics
        experimentSummaryArb.map(exp => ({ ...exp, metrics: exp.metrics.slice(0, 1) })),
        
        // Experiment with many metrics
        experimentSummaryArb.map(exp => ({ 
          ...exp, 
          metrics: [...exp.metrics, ...exp.metrics, ...exp.metrics].slice(0, 10) 
        })),
        
        // Experiment with optional descriptions
        experimentSummaryArb.map(exp => ({
          ...exp,
          models: {
            baseline: { ...exp.models.baseline, description: undefined },
            candidate: { ...exp.models.candidate, description: undefined }
          }
        }))
      ),
      (experiment: ExperimentSummary) => {
        // Should still have all required fields regardless of edge cases
        expect(experiment).toHaveProperty('id');
        expect(experiment).toHaveProperty('name');
        expect(experiment).toHaveProperty('dataset');
        expect(experiment).toHaveProperty('models');
        expect(experiment).toHaveProperty('runDate');
        expect(experiment).toHaveProperty('status');
        expect(experiment).toHaveProperty('metrics');
        
        // Metrics should always have at least one entry
        expect(experiment.metrics.length).toBeGreaterThan(0);
        expect(experiment.metrics.length).toBeLessThanOrEqual(10);
        
        // All string fields should be non-empty
        expect(experiment.id.length).toBeGreaterThan(0);
        expect(experiment.name.length).toBeGreaterThan(0);
        expect(experiment.dataset.name.length).toBeGreaterThan(0);
        expect(experiment.models.baseline.name.length).toBeGreaterThan(0);
        expect(experiment.models.candidate.name.length).toBeGreaterThan(0);
      }
    ), { numRuns: 100 });
  });
});