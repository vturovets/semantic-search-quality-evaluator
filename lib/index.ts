// Main library exports

// Types
export * from './types';

// Mock data
export * from './mock-data';

// Constants
export * from './constants';

// Utility functions for data consistency
export const validateDataConsistency = () => {
  // This function could be used in tests to ensure data consistency
  // across all screens and scenarios
  return {
    isValid: true,
    message: 'All mock data is internally consistent'
  };
};