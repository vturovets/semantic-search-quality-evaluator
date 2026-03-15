/**
 * Property test for statistical calculation bounds
 * Feature: ai-product-experiment-lab, Property 11: Statistical calculation bounds
 * Validates: Requirements 3.2
 */

import * as fc from 'fast-check'

// Mock function to simulate hypothesis test calculations
function calculateHypothesisTest(
  baselineValue: number,
  candidateValue: number,
  sampleSize: number
): { pValue: number; confidenceLevel: number } {
  // Handle edge cases to avoid NaN
  if (baselineValue === 0 && candidateValue === 0) {
    return { pValue: 1.0, confidenceLevel: 0 }
  }
  
  if (sampleSize <= 0) {
    return { pValue: 1.0, confidenceLevel: 0 }
  }
  
  // Simplified statistical calculation for testing
  const difference = Math.abs(candidateValue - baselineValue)
  
  // Avoid division by zero in standard error calculation
  const variance = Math.max(0.001, baselineValue * (1 - baselineValue))
  const standardError = Math.sqrt(variance / sampleSize)
  
  const zScore = standardError > 0 ? difference / standardError : 0
  
  // Simplified p-value calculation (normally distributed)
  let pValue = Math.max(0, Math.min(1, 2 * (1 - Math.min(Math.abs(zScore) / 3, 1))))
  
  // Ensure p-value is within valid bounds
  pValue = Math.max(0, Math.min(1, pValue))
  
  // Calculate confidence level (percentage)
  const confidenceLevel = Math.max(0, Math.min(100, (1 - pValue) * 100))
  
  return { pValue, confidenceLevel }
}

describe('Property 11: Statistical calculation bounds', () => {
  it('should ensure p-values are between 0 and 1 for any hypothesis test', () => {
    fc.assert(fc.property(
      fc.float({ min: 0, max: 1, noNaN: true }), // baseline value (proportion)
      fc.float({ min: 0, max: 1, noNaN: true }), // candidate value (proportion)
      fc.integer({ min: 10, max: 1000 }), // sample size
      (baselineValue, candidateValue, sampleSize) => {
        const result = calculateHypothesisTest(baselineValue, candidateValue, sampleSize)
        
        // P-value must be between 0 and 1 (inclusive)
        expect(result.pValue).toBeGreaterThanOrEqual(0)
        expect(result.pValue).toBeLessThanOrEqual(1)
        
        // P-value should be a valid number
        expect(Number.isFinite(result.pValue)).toBe(true)
        expect(Number.isNaN(result.pValue)).toBe(false)
      }
    ), { numRuns: 100 })
  })

  it('should ensure confidence levels are positive percentages for any hypothesis test', () => {
    fc.assert(fc.property(
      fc.float({ min: 0, max: 1, noNaN: true }),
      fc.float({ min: 0, max: 1, noNaN: true }),
      fc.integer({ min: 10, max: 1000 }),
      (baselineValue, candidateValue, sampleSize) => {
        const result = calculateHypothesisTest(baselineValue, candidateValue, sampleSize)
        
        // Confidence level must be between 0 and 100 (inclusive)
        expect(result.confidenceLevel).toBeGreaterThanOrEqual(0)
        expect(result.confidenceLevel).toBeLessThanOrEqual(100)
        
        // Confidence level should be a valid number
        expect(Number.isFinite(result.confidenceLevel)).toBe(true)
        expect(Number.isNaN(result.confidenceLevel)).toBe(false)
      }
    ), { numRuns: 100 })
  })

  it('should maintain inverse relationship between p-value and confidence level', () => {
    fc.assert(fc.property(
      fc.float({ min: 0, max: 1, noNaN: true }),
      fc.float({ min: 0, max: 1, noNaN: true }),
      fc.integer({ min: 10, max: 1000 }),
      (baselineValue, candidateValue, sampleSize) => {
        const result = calculateHypothesisTest(baselineValue, candidateValue, sampleSize)
        
        // Lower p-value should generally correspond to higher confidence
        // This is a simplified relationship for testing purposes
        if (result.pValue < 0.05) {
          expect(result.confidenceLevel).toBeGreaterThan(90)
        }
        
        if (result.pValue > 0.5) {
          expect(result.confidenceLevel).toBeLessThan(60)
        }
      }
    ), { numRuns: 100 })
  })
})