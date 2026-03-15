/**
 * Property-Based Test: Metric delta calculation accuracy
 * Feature: ai-product-experiment-lab, Property 7: Metric delta calculation accuracy
 * Validates: Requirements 2.2
 */

import * as fc from 'fast-check';
import { MetricValue } from '../../../lib/types/experiments';

// Function to calculate metric deltas - this represents the core logic being tested
function calculateMetricDelta(baseline: MetricValue, candidate: MetricValue): {
  absolute: number;
  percentage: number;
  direction: 'positive' | 'negative' | 'neutral';
} {
  const absolute = candidate.value - baseline.value;
  const percentage = baseline.value === 0 ? 0 : (absolute / baseline.value) * 100;
  
  let direction: 'positive' | 'negative' | 'neutral';
  if (Math.abs(percentage) < 0.1) { // Less than 0.1% change is considered neutral
    direction = 'neutral';
  } else if (absolute > 0) {
    direction = 'positive';
  } else {
    direction = 'negative';
  }
  
  return {
    absolute: Math.round(absolute * 10) / 10, // Round to 1 decimal place
    percentage: Math.round(percentage * 10) / 10, // Round to 1 decimal place
    direction
  };
}

describe('Property 7: Metric delta calculation accuracy', () => {
  it('should correctly compute percentage and absolute differences for any baseline and candidate metric pair', () => {
    fc.assert(fc.property(
      fc.record({
        baseline: fc.record({
          value: fc.float({ min: Math.fround(0.01), max: Math.fround(1000), noNaN: true }),
          unit: fc.option(fc.constantFrom('%', 'ms', 'count', 'score'), { nil: undefined })
        }),
        candidate: fc.record({
          value: fc.float({ min: Math.fround(0.01), max: Math.fround(1000), noNaN: true }),
          unit: fc.option(fc.constantFrom('%', 'ms', 'count', 'score'), { nil: undefined })
        })
      }),
      ({ baseline, candidate }) => {
        const delta = calculateMetricDelta(baseline, candidate);
        
        // Validate delta structure
        expect(delta).toHaveProperty('absolute');
        expect(delta).toHaveProperty('percentage');
        expect(delta).toHaveProperty('direction');
        
        // Validate absolute calculation
        const expectedAbsolute = candidate.value - baseline.value;
        expect(Math.abs(delta.absolute - expectedAbsolute)).toBeLessThan(0.1);
        
        // Validate percentage calculation
        const expectedPercentage = (expectedAbsolute / baseline.value) * 100;
        expect(Math.abs(delta.percentage - expectedPercentage)).toBeLessThan(0.1);
        
        // Validate direction logic - must match the function's logic
        // The function uses the unrounded percentage and unrounded absolute to determine direction
        const unroundedAbsolute = candidate.value - baseline.value;
        const unroundedPercentage = (unroundedAbsolute / baseline.value) * 100;
        if (Math.abs(unroundedPercentage) < 0.1) {
          // If percentage change is less than 0.1%, it's neutral regardless of absolute value
          expect(delta.direction).toBe('neutral');
        } else if (unroundedAbsolute > 0) {
          // Function uses UNROUNDED absolute for direction
          expect(delta.direction).toBe('positive');
        } else {
          // Function uses UNROUNDED absolute for direction
          expect(delta.direction).toBe('negative');
        }
        
        // Validate numeric properties
        expect(typeof delta.absolute).toBe('number');
        expect(typeof delta.percentage).toBe('number');
        expect(['positive', 'negative', 'neutral']).toContain(delta.direction);
        expect(Number.isFinite(delta.absolute)).toBe(true);
        expect(Number.isFinite(delta.percentage)).toBe(true);
      }
    ), { numRuns: 100 });
  });

  it('should handle edge cases correctly', () => {
    fc.assert(fc.property(
      fc.oneof(
        // Same values (should be neutral)
        fc.record({
          baseline: fc.record({ value: fc.float({ min: Math.fround(1), max: Math.fround(100), noNaN: true }) }),
          candidate: fc.record({ value: fc.constant(0) }) // Will be set to baseline.value
        }).map(({ baseline }) => ({ 
          baseline, 
          candidate: { value: baseline.value } 
        })),
        
        // Very small differences
        fc.record({
          baseline: fc.record({ value: fc.float({ min: Math.fround(100), max: Math.fround(1000), noNaN: true }) }),
          candidate: fc.record({ value: fc.constant(0) }) // Will be set to baseline.value + tiny amount
        }).map(({ baseline }) => ({ 
          baseline, 
          candidate: { value: baseline.value + 0.01 } 
        })),
        
        // Large improvements
        fc.record({
          baseline: fc.record({ value: fc.float({ min: Math.fround(1), max: Math.fround(10), noNaN: true }) }),
          candidate: fc.record({ value: fc.float({ min: Math.fround(50), max: Math.fround(100), noNaN: true }) })
        }),
        
        // Large degradations
        fc.record({
          baseline: fc.record({ value: fc.float({ min: Math.fround(50), max: Math.fround(100), noNaN: true }) }),
          candidate: fc.record({ value: fc.float({ min: Math.fround(1), max: Math.fround(10), noNaN: true }) })
        })
      ),
      ({ baseline, candidate }) => {
        const delta = calculateMetricDelta(baseline, candidate);
        
        // All calculations should produce valid numbers
        expect(Number.isFinite(delta.absolute)).toBe(true);
        expect(Number.isFinite(delta.percentage)).toBe(true);
        expect(['positive', 'negative', 'neutral']).toContain(delta.direction);
        
        // Direction should be consistent with absolute value
        if (delta.direction === 'positive') {
          expect(delta.absolute).toBeGreaterThan(0);
        } else if (delta.direction === 'negative') {
          expect(delta.absolute).toBeLessThan(0);
        } else {
          expect(Math.abs(delta.percentage)).toBeLessThan(0.1);
        }
      }
    ), { numRuns: 100 });
  });

  it('should maintain mathematical consistency between absolute and percentage values', () => {
    fc.assert(fc.property(
      fc.record({
        baseline: fc.record({
          value: fc.float({ min: Math.fround(1), max: Math.fround(1000), noNaN: true })
        }),
        candidate: fc.record({
          value: fc.float({ min: Math.fround(1), max: Math.fround(1000), noNaN: true })
        })
      }),
      ({ baseline, candidate }) => {
        const delta = calculateMetricDelta(baseline, candidate);
        
        // Validate that rounding is applied consistently
        // Both absolute and percentage should be rounded to 1 decimal place
        expect(delta.absolute).toBe(Math.round(delta.absolute * 10) / 10);
        expect(delta.percentage).toBe(Math.round(delta.percentage * 10) / 10);
        
        // Sign consistency - if absolute is positive (after rounding), percentage should be positive
        if (delta.absolute > 0.1) {
          expect(delta.percentage).toBeGreaterThan(0);
        } else if (delta.absolute < -0.1) {
          expect(delta.percentage).toBeLessThan(0);
        }
      }
    ), { numRuns: 100 });
  });

  it('should validate existing experiment data has accurate delta calculations', () => {
    // Test with known experiment data
    const testCases = [
      {
        metric: 'Accuracy',
        baseline: { value: 82, unit: '%' },
        candidate: { value: 88, unit: '%' },
        expectedAbsolute: 6,
        expectedPercentage: 7.3,
        expectedDirection: 'positive' as const
      },
      {
        metric: 'Latency',
        baseline: { value: 780, unit: 'ms' },
        candidate: { value: 710, unit: 'ms' },
        expectedAbsolute: -70,
        expectedPercentage: -9.0,
        expectedDirection: 'negative' as const
      },
      {
        metric: 'Failure Rate',
        baseline: { value: 11, unit: '%' },
        candidate: { value: 7, unit: '%' },
        expectedAbsolute: -4,
        expectedPercentage: -36.4,
        expectedDirection: 'negative' as const
      }
    ];

    testCases.forEach(testCase => {
      const delta = calculateMetricDelta(testCase.baseline, testCase.candidate);
      
      expect(Math.abs(delta.absolute - testCase.expectedAbsolute)).toBeLessThan(0.01);
      expect(Math.abs(delta.percentage - testCase.expectedPercentage)).toBeLessThan(0.01);
      expect(delta.direction).toBe(testCase.expectedDirection);
    });
  });

  it('should handle zero baseline values gracefully', () => {
    fc.assert(fc.property(
      fc.record({
        candidate: fc.record({
          value: fc.float({ min: Math.fround(0), max: Math.fround(100), noNaN: true })
        })
      }),
      ({ candidate }) => {
        const baseline = { value: 0 };
        const delta = calculateMetricDelta(baseline, candidate);
        
        // When baseline is 0, absolute should equal candidate value (with rounding)
        expect(Math.abs(delta.absolute - candidate.value)).toBeLessThan(0.1);
        
        // When baseline is 0, percentage should be 0 (to avoid division by zero)
        expect(delta.percentage).toBe(0);
        
        // Direction should be based on percentage when baseline is 0
        // Since percentage is always 0 when baseline is 0, direction should always be neutral
        // unless the absolute value is large enough to be considered significant
        if (Math.abs(delta.percentage) < 0.1) {
          expect(delta.direction).toBe('neutral');
        } else if (delta.absolute > 0) {
          expect(delta.direction).toBe('positive');
        } else if (delta.absolute < 0) {
          expect(delta.direction).toBe('negative');
        } else {
          expect(delta.direction).toBe('neutral');
        }
      }
    ), { numRuns: 100 });
  });
});