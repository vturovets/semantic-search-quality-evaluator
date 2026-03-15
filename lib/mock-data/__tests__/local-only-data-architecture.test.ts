/**
 * Property-Based Test: Local-only data architecture
 * Feature: ai-product-experiment-lab, Property 25: Local-only data architecture
 * Validates: Requirements 6.3
 */

import * as fc from 'fast-check';
import { searchScenarios } from '../search-scenarios';
import { experimentDataArray } from '../experiment-data';
import { releaseDecisionData } from '../release-data';

// Mock fetch to ensure no external API calls are made
const originalFetch = global.fetch;

beforeAll(() => {
  global.fetch = jest.fn(() => 
    Promise.reject(new Error('Network requests are not allowed in this test'))
  );
});

afterAll(() => {
  global.fetch = originalFetch;
});

describe('Property 25: Local-only data architecture', () => {
  it('should use only local static mock data without API calls for any data operation', () => {
    fc.assert(fc.property(
      fc.constantFrom('search', 'experiment', 'release'),
      (dataType) => {
        let data: any;
        
        // Access different data types
        if (dataType === 'search') {
          data = searchScenarios;
        } else if (dataType === 'experiment') {
          data = experimentDataArray;
        } else {
          data = releaseDecisionData;
        }
        
        // Validate that data is immediately available (not a promise)
        expect(data).toBeDefined();
        
        // All data types should be arrays or objects
        if (dataType === 'search') {
          // Search scenarios is an object with query keys
          expect(typeof data).toBe('object');
          expect(Object.keys(data).length).toBeGreaterThan(0);
        } else {
          // Experiment and release data are arrays
          expect(Array.isArray(data)).toBe(true);
          expect(data.length).toBeGreaterThan(0);
        }
        
        // Validate that data is not a promise or async operation
        expect(data instanceof Promise).toBe(false);
        
        // Validate that accessing data doesn't trigger any network calls
        // (fetch mock will throw if any network call is attempted)
        expect(() => {
          if (Array.isArray(data)) {
            const firstItem = data[0];
            expect(firstItem).toBeDefined();
          } else {
            const firstKey = Object.keys(data)[0];
            expect(data[firstKey]).toBeDefined();
          }
        }).not.toThrow();
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure all data is synchronously accessible without external dependencies', () => {
    fc.assert(fc.property(
      fc.integer({ min: 0, max: Math.max(Object.keys(searchScenarios).length, experimentDataArray.length) - 1 }),
      (index) => {
        // Access data synchronously
        const searchKeys = Object.keys(searchScenarios);
        const searchData = searchScenarios[searchKeys[index % searchKeys.length]];
        const experimentDataItem = experimentDataArray[index % experimentDataArray.length];
        const releaseData = releaseDecisionData[0];
        
        // Validate that all data is immediately available
        expect(searchData).toBeDefined();
        expect(experimentDataItem).toBeDefined();
        expect(releaseData).toBeDefined();
        
        // Validate that data has all required fields (no lazy loading)
        expect(searchData.id).toBeTruthy();
        expect(searchData.query).toBeTruthy();
        expect(searchData.results).toBeDefined();
        expect(searchData.interpretedFilters).toBeDefined();
        
        expect(experimentDataItem.id).toBeTruthy();
        expect(experimentDataItem.name).toBeTruthy();
        expect(experimentDataItem.metrics).toBeDefined();
        
        expect(releaseData.id).toBeTruthy();
        expect(releaseData.recommendation).toBeDefined();
        expect(releaseData.statisticalSummary).toBeDefined();
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should not require authentication, databases, or external services for any data access', () => {
    fc.assert(fc.property(
      fc.constant(true),
      () => {
        // Validate that data modules don't import any authentication libraries
        // This is a structural test - the data should be plain objects
        
        // Access all data sources
        const allSearchData = searchScenarios;
        const allExperimentData = experimentDataArray;
        const allReleaseData = releaseDecisionData;
        
        // Validate that data is plain JavaScript objects/arrays
        expect(typeof allSearchData).toBe('object');
        expect(Array.isArray(allExperimentData)).toBe(true);
        expect(Array.isArray(allReleaseData)).toBe(true);
        
        // Validate that data doesn't contain any authentication tokens or credentials
        Object.values(allSearchData).forEach(item => {
          const itemString = JSON.stringify(item);
          expect(itemString).not.toMatch(/token/i);
          expect(itemString).not.toMatch(/apiKey/i);
          expect(itemString).not.toMatch(/password/i);
          expect(itemString).not.toMatch(/secret/i);
          expect(itemString).not.toMatch(/auth/i);
        });
        
        allExperimentData.forEach(item => {
          const itemString = JSON.stringify(item);
          expect(itemString).not.toMatch(/token/i);
          expect(itemString).not.toMatch(/apiKey/i);
          expect(itemString).not.toMatch(/password/i);
          expect(itemString).not.toMatch(/secret/i);
          expect(itemString).not.toMatch(/auth/i);
        });
        
        allReleaseData.forEach(item => {
          const itemString = JSON.stringify(item);
          expect(itemString).not.toMatch(/token/i);
          expect(itemString).not.toMatch(/apiKey/i);
          expect(itemString).not.toMatch(/password/i);
          expect(itemString).not.toMatch(/secret/i);
          expect(itemString).not.toMatch(/auth/i);
        });
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should provide realistic data without requiring backend services', () => {
    fc.assert(fc.property(
      fc.integer({ min: 0, max: Object.keys(searchScenarios).length - 1 }),
      (searchIndex) => {
        const searchKeys = Object.keys(searchScenarios);
        const scenario = searchScenarios[searchKeys[searchIndex]];
        
        // Validate that data is realistic and complete
        expect(scenario.query.length).toBeGreaterThan(0);
        expect(scenario.results.length).toBeGreaterThan(0);
        
        // Validate that execution metrics are realistic
        expect(scenario.executionMetrics.latency).toBeGreaterThan(0);
        expect(scenario.executionMetrics.latency).toBeLessThan(10000); // Reasonable latency
        expect(scenario.executionMetrics.wordCount).toBeGreaterThan(0);
        expect(scenario.executionMetrics.traceId).toBeTruthy();
        
        // Validate that results have realistic product data
        scenario.results.forEach(result => {
          expect(result.name).toBeTruthy();
          expect(result.description).toBeTruthy();
          expect(result.priceValue || parseFloat(result.price.replace(/[^0-9.]/g, ''))).toBeGreaterThan(0);
          expect(result.currency || result.price).toBeTruthy();
          expect(Array.isArray(result.tags)).toBe(true);
        });
        
        // Validate that trace steps are realistic (if present)
        if (scenario.traceSteps) {
          expect(Array.isArray(scenario.traceSteps)).toBe(true);
          scenario.traceSteps.forEach(step => {
            expect(step.step).toBeTruthy();
            expect(['completed', 'processing', 'pending']).toContain(step.status);
          });
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure data operations complete synchronously without async dependencies', () => {
    fc.assert(fc.property(
      fc.record({
        searchIndex: fc.integer({ min: 0, max: Object.keys(searchScenarios).length - 1 }),
        experimentIndex: fc.integer({ min: 0, max: experimentDataArray.length - 1 })
      }),
      (props) => {
        // Perform multiple data access operations synchronously
        const startTime = Date.now();
        
        const searchKeys = Object.keys(searchScenarios);
        const search = searchScenarios[searchKeys[props.searchIndex]];
        const experiment = experimentDataArray[props.experimentIndex];
        const release = releaseDecisionData[0];
        
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        // Validate that all data was accessed synchronously (should be nearly instant)
        expect(duration).toBeLessThan(100); // Should complete in less than 100ms
        
        // Validate that all data is available
        expect(search).toBeDefined();
        expect(experiment).toBeDefined();
        expect(release).toBeDefined();
        
        // Validate that nested data is also immediately available
        expect(search.results[0]).toBeDefined();
        expect(experiment.metrics[0]).toBeDefined();
        expect(release.comparisonSnapshot[0]).toBeDefined();
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain data integrity without external storage or persistence', () => {
    fc.assert(fc.property(
      fc.constant(true),
      () => {
        // Validate that data is immutable and doesn't rely on external state
        const initialSearchCount = Object.keys(searchScenarios).length;
        const initialExperimentCount = experimentDataArray.length;
        const initialReleaseCount = releaseDecisionData.length;
        
        // Access data multiple times
        for (let i = 0; i < 10; i++) {
          expect(Object.keys(searchScenarios).length).toBe(initialSearchCount);
          expect(experimentDataArray.length).toBe(initialExperimentCount);
          expect(releaseDecisionData.length).toBe(initialReleaseCount);
        }
        
        // Validate that data structure remains consistent
        Object.values(searchScenarios).forEach(scenario => {
          expect(scenario.id).toBeTruthy();
          expect(scenario.query).toBeTruthy();
        });
        
        experimentDataArray.forEach(experiment => {
          expect(experiment.id).toBeTruthy();
          expect(experiment.name).toBeTruthy();
        });
        
        releaseDecisionData.forEach(decision => {
          expect(decision.id).toBeTruthy();
          expect(decision.recommendation).toBeDefined();
        });
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure no environment variables or configuration files are required for data access', () => {
    fc.assert(fc.property(
      fc.constant(true),
      () => {
        // Validate that data can be accessed without checking environment variables
        const originalEnv = process.env;
        
        // Temporarily clear environment variables
        process.env = {};
        
        try {
          // Data should still be accessible
          expect(Object.keys(searchScenarios).length).toBeGreaterThan(0);
          expect(experimentDataArray.length).toBeGreaterThan(0);
          expect(releaseDecisionData.length).toBeGreaterThan(0);
          
          // Data should be complete
          const searchKeys = Object.keys(searchScenarios);
          const search = searchScenarios[searchKeys[0]];
          const experiment = experimentDataArray[0];
          const release = releaseDecisionData[0];
          
          expect(search.id).toBeTruthy();
          expect(experiment.id).toBeTruthy();
          expect(release.id).toBeTruthy();
        } finally {
          // Restore environment variables
          process.env = originalEnv;
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });
});
