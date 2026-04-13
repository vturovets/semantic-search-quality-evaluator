// Application configuration

import { DemoConfig } from '../types/shared';

export const demoConfig: DemoConfig = {
  productName: 'Golden Set Coverage Advisor',
  tagline: 'Evaluate whether your golden sets still represent real production language',
  navigation: [
    { label: 'Dashboard', href: '/quality-evaluation' },
    { label: 'Intake', href: '/quality-evaluation/intake' },
    { label: 'Analysis', href: '/quality-evaluation/analysis' },
    { label: 'Recommendations', href: '/quality-evaluation/recommendations' },
    { label: 'Reports', href: '/quality-evaluation/reports' }
  ]
};

// Feature flags for functionality
export const featureFlags = {
  enableExportFeatures: true,
  enableRealTimeUpdates: false,
  enableUserAuthentication: false
};
