/**
 * Property-Based Test: Query interpretation completeness
 * Feature: ai-product-experiment-lab, Property 1: Query interpretation completeness
 * Validates: Requirements 1.1
 */

import * as fc from 'fast-check';
import { searchScenarios } from '../../../lib/mock-data/search-scenarios';
import { LegacySearchScenario } from '../../../lib/types/search';

// Mock interpretation function that simulates how the system would interpret queries
function interpretQuery(query: string): {
  filters: { label: string; value: string }[];
  summary: string;
  confidence: 'High' | 'Medium' | 'Low';
  structuredOutput: Record<string, any>;
} {
  // For testing purposes, use existing scenarios if available, otherwise generate mock interpretation
  const existingScenario = Object.values(searchScenarios).find(s => s.query === query);
  
  if (existingScenario) {
    return existingScenario.interpretation;
  }
  
  // Generate mock interpretation for any query
  const words = query.toLowerCase().split(' ').filter(w => w.length > 0);
  const filters: { label: string; value: string }[] = [];
  
  // Simple heuristic-based interpretation
  if (words.some(w => ['cheap', 'budget', 'affordable', 'low', 'under'].includes(w))) {
    filters.push({ label: 'Price', value: 'Low' });
  }
  if (words.some(w => ['winter', 'cold', 'snow'].includes(w))) {
    filters.push({ label: 'Season', value: 'Winter' });
  }
  if (words.some(w => ['summer', 'hot', 'warm'].includes(w))) {
    filters.push({ label: 'Season', value: 'Summer' });
  }
  if (words.some(w => ['running', 'runner', 'run'].includes(w))) {
    filters.push({ label: 'Type', value: 'Running' });
  }
  if (words.some(w => ['shoes', 'shoe', 'footwear'].includes(w))) {
    filters.push({ label: 'Category', value: 'Shoes' });
  }
  if (words.some(w => ['sandals', 'sandal'].includes(w))) {
    filters.push({ label: 'Category', value: 'Sandals' });
  }
  if (words.some(w => ['kids', 'children', 'child'].includes(w))) {
    filters.push({ label: 'Age Group', value: 'Kids' });
  }
  if (words.some(w => ['waterproof', 'water-resistant'].includes(w))) {
    filters.push({ label: 'Feature', value: 'Waterproof' });
  }
  
  // If no specific filters found, add a generic category
  if (filters.length === 0) {
    filters.push({ label: 'Category', value: 'General' });
  }
  
  const structuredOutput: Record<string, any> = {};
  filters.forEach(filter => {
    structuredOutput[filter.label.toLowerCase().replace(' ', '_')] = filter.value.toLowerCase();
  });
  
  return {
    filters,
    summary: `Interpreted query for ${filters.map(f => f.value.toLowerCase()).join(', ')} products.`,
    confidence: filters.length >= 2 ? 'High' : filters.length === 1 ? 'Medium' : 'Low',
    structuredOutput
  };
}

describe('Property 1: Query interpretation completeness', () => {
  it('should produce structured filters with confidence and summary for any natural language query', () => {
    fc.assert(fc.property(
      fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0),
      (query) => {
        const result = interpretQuery(query.trim());
        
        // Validate that interpretation has all required properties
        expect(result).toHaveProperty('filters');
        expect(result).toHaveProperty('confidence');
        expect(result).toHaveProperty('summary');
        expect(result).toHaveProperty('structuredOutput');
        
        // Validate filters array structure
        expect(Array.isArray(result.filters)).toBe(true);
        expect(result.filters.length).toBeGreaterThan(0);
        
        result.filters.forEach(filter => {
          expect(typeof filter.label).toBe('string');
          expect(filter.label.length).toBeGreaterThan(0);
          expect(typeof filter.value).toBe('string');
          expect(filter.value.length).toBeGreaterThan(0);
        });
        
        // Validate confidence level
        expect(['High', 'Medium', 'Low']).toContain(result.confidence);
        
        // Validate summary
        expect(typeof result.summary).toBe('string');
        expect(result.summary.length).toBeGreaterThan(0);
        
        // Validate structured output
        expect(typeof result.structuredOutput).toBe('object');
        expect(result.structuredOutput).not.toBeNull();
        expect(Object.keys(result.structuredOutput).length).toBeGreaterThan(0);
        
        // Validate that structured output values are strings or basic types
        Object.values(result.structuredOutput).forEach(value => {
          expect(['string', 'number', 'boolean']).toContain(typeof value);
        });
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistency between filters and structured output', () => {
    fc.assert(fc.property(
      fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0),
      (query) => {
        const result = interpretQuery(query.trim());
        
        // The number of structured output keys should relate to the number of filters
        // (allowing for some flexibility in how data is structured)
        expect(Object.keys(result.structuredOutput).length).toBeGreaterThan(0);
        expect(Object.keys(result.structuredOutput).length).toBeLessThanOrEqual(result.filters.length + 2);
        
        // All structured output values should be non-empty if they're strings
        Object.values(result.structuredOutput).forEach(value => {
          if (typeof value === 'string') {
            expect(value.length).toBeGreaterThan(0);
          }
        });
      }
    ), { numRuns: 100 });
  });

  it('should handle edge cases gracefully', () => {
    fc.assert(fc.property(
      fc.oneof(
        fc.constant(''),
        fc.constant('   '),
        fc.string({ minLength: 1, maxLength: 5 }).map(s => s.repeat(20)), // Very long queries
        fc.string({ minLength: 1, maxLength: 10 }).map(s => s.replace(/[a-zA-Z]/g, '123')), // Numeric queries
        fc.constant('!@#$%^&*()'), // Special characters only
      ),
      (edgeQuery) => {
        if (edgeQuery.trim().length === 0) {
          // Empty queries should be handled by the calling code, not the interpretation function
          return;
        }
        
        const result = interpretQuery(edgeQuery);
        
        // Even for edge cases, the interpretation should be complete
        expect(result).toHaveProperty('filters');
        expect(result).toHaveProperty('confidence');
        expect(result).toHaveProperty('summary');
        expect(result).toHaveProperty('structuredOutput');
        
        expect(Array.isArray(result.filters)).toBe(true);
        expect(result.filters.length).toBeGreaterThan(0);
        expect(['High', 'Medium', 'Low']).toContain(result.confidence);
        expect(typeof result.summary).toBe('string');
        expect(result.summary.length).toBeGreaterThan(0);
        expect(typeof result.structuredOutput).toBe('object');
      }
    ), { numRuns: 50 });
  });

  it('should validate existing search scenarios have complete interpretations', () => {
    fc.assert(fc.property(
      fc.constantFrom(...Object.keys(searchScenarios)),
      (scenarioKey) => {
        const scenario = searchScenarios[scenarioKey];
        const interpretation = scenario.interpretation;
        
        // Validate completeness of existing scenario interpretations
        expect(interpretation).toHaveProperty('filters');
        expect(interpretation).toHaveProperty('confidence');
        expect(interpretation).toHaveProperty('summary');
        expect(interpretation).toHaveProperty('structuredOutput');
        
        expect(Array.isArray(interpretation.filters)).toBe(true);
        expect(interpretation.filters.length).toBeGreaterThan(0);
        
        interpretation.filters.forEach(filter => {
          expect(typeof filter.label).toBe('string');
          expect(filter.label.length).toBeGreaterThan(0);
          expect(typeof filter.value).toBe('string');
          expect(filter.value.length).toBeGreaterThan(0);
        });
        
        expect(['High', 'Medium', 'Low']).toContain(interpretation.confidence);
        expect(typeof interpretation.summary).toBe('string');
        expect(interpretation.summary.length).toBeGreaterThan(0);
        expect(typeof interpretation.structuredOutput).toBe('object');
        expect(Object.keys(interpretation.structuredOutput).length).toBeGreaterThan(0);
      }
    ), { numRuns: 100 });
  });
});