// Application configuration

import { DemoConfig } from '../types/shared';

export const demoConfig: DemoConfig = {
  productName: 'AI Product Experiment Lab',
  tagline: 'Validate AI product features with statistical confidence',
  navigation: [
    { label: 'Search', href: '/search' },
    { label: 'Experiments', href: '/experiments' },
    { label: 'Release Validation', href: '/release-validation' }
  ],
  defaultSearchQuery: 'Find cheap winter running shoes',
  samplePrompts: [
    'Find cheap winter running shoes',
    'sandals for hot weather',
    'kids shoes under €50',
    'waterproof trail shoes'
  ]
};

// Feature flags for demo functionality
export const featureFlags = {
  enableTraceDetails: true,
  enableStructuredOutput: true,
  enableExportFeatures: false, // Disabled for demo
  enableRealTimeUpdates: false, // Disabled for demo
  enableUserAuthentication: false // Disabled for demo
};

// Simulation settings
export const simulationConfig = {
  searchDelayRange: {
    min: 700,
    max: 1200
  },
  defaultLoadingDelay: 800,
  enableRealisticDelays: true
};

// Demo flow configuration
export const demoFlow = {
  steps: [
    {
      id: 'search',
      title: 'AI Product Search',
      description: 'Demonstrate natural language search capabilities',
      route: '/search'
    },
    {
      id: 'experiments',
      title: 'Experiment Dashboard',
      description: 'Compare AI model performance with controlled experiments',
      route: '/experiments'
    },
    {
      id: 'release-validation',
      title: 'Release Decision',
      description: 'Statistical validation for confident deployment decisions',
      route: '/release-validation'
    }
  ],
  narrative: 'capability → question → evidence → decision'
};