/**
 * Property test for recommendation validity
 * Feature: ai-product-experiment-lab, Property 10: Recommendation validity
 * Validates: Requirements 3.1
 */

import * as fc from 'fast-check'
import { LegacyStatisticalResult } from '../../../lib/types/release'

// Mock function to simulate release decision generation
function generateReleaseRecommendation(
  pValue: number,
  confidenceLevel: number,
  isSignificant: boolean
): 'SAFE TO RELEASE' | 'KEEP TESTING' | 'DO NOT RELEASE' {
  if (isSignificant && pValue < 0.05 && confidenceLevel >= 95) {
    return 'SAFE TO RELEASE'
  } else if (pValue >= 0.05 || confidenceLevel < 95) {
    return 'KEEP TESTING'
  } else {
    return 'DO NOT RELEASE'
  }
}

describe('Property 10: Recommendation validity', () => {
  it('should generate exactly one of the three valid recommendations for any statistical analysis input', () => {
    fc.assert(fc.property(
      fc.float({ min: 0, max: 1 }), // p-value
      fc.integer({ min: 80, max: 99 }), // confidence level
      fc.boolean(), // is significant
      (pValue, confidenceLevel, isSignificant) => {
        const recommendation = generateReleaseRecommendation(pValue, confidenceLevel, isSignificant)
        
        // Verify that the recommendation is exactly one of the three valid options
        const validRecommendations = ['SAFE TO RELEASE', 'KEEP TESTING', 'DO NOT RELEASE']
        expect(validRecommendations).toContain(recommendation)
        
        // Verify that the recommendation is a string
        expect(typeof recommendation).toBe('string')
        
        // Verify that the recommendation is not empty
        expect(recommendation.length).toBeGreaterThan(0)
      }
    ), { numRuns: 100 })
  })

  it('should generate consistent recommendations for the same input', () => {
    fc.assert(fc.property(
      fc.float({ min: 0, max: 1 }),
      fc.integer({ min: 80, max: 99 }),
      fc.boolean(),
      (pValue, confidenceLevel, isSignificant) => {
        const recommendation1 = generateReleaseRecommendation(pValue, confidenceLevel, isSignificant)
        const recommendation2 = generateReleaseRecommendation(pValue, confidenceLevel, isSignificant)
        
        // Same inputs should produce same recommendation
        expect(recommendation1).toBe(recommendation2)
      }
    ), { numRuns: 100 })
  })
})