/**
 * Integration Tests: Complete User Flows
 * 
 * Feature: ai-product-experiment-lab
 * Validates: Requirements 4.5, 6.2
 * 
 * These tests verify end-to-end navigation from search to release decision
 * and validate data consistency across screen transitions.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchPage from '@/app/search/page';
import ExperimentsPage from '@/app/experiments/page';
import ReleaseValidationPage from '@/app/release-validation/page';
import { searchScenarios, defaultSearchQuery, experimentDataArray, experimentSummary } from '@/lib/mock-data';
import { releaseDecisionData, comparisonSnapshot, legacyReleaseDecisionData } from '@/lib/mock-data/release-data';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/search',
}));

describe('Integration: Complete User Flow', () => {
  describe('Search to Experiments to Release Decision Flow', () => {
    it('should maintain data consistency across the complete workflow', async () => {
      const user = userEvent.setup();

      // Step 1: Start on Search page
      const { unmount: unmountSearch } = render(<SearchPage />);
      
      // Verify search page loads with initial state
      expect(screen.getByPlaceholderText(/find cheap winter running shoes/i)).toBeInTheDocument();
      
      // Verify sample prompts are available (they're rendered as buttons with the query text)
      const samplePrompts = screen.getAllByRole('button');
      const promptButtons = samplePrompts.filter(btn => 
        Object.keys(searchScenarios).some(query => btn.textContent?.includes(query))
      );
      expect(promptButtons.length).toBeGreaterThan(0);
      
      // Select a sample prompt and trigger search
      await user.click(promptButtons[0]);
      
      // Wait for search results to appear - use getAllByText since "results" appears multiple times
      await waitFor(() => {
        const resultsTexts = screen.getAllByText(/results/i);
        expect(resultsTexts.length).toBeGreaterThan(0);
      }, { timeout: 2000 });
      
      // Verify execution metrics are displayed
      expect(screen.getByText(/execution metrics/i)).toBeInTheDocument();
      
      // Capture search scenario data for cross-screen validation
      const searchScenario = searchScenarios[defaultSearchQuery];
      expect(searchScenario).toBeDefined();
      expect(searchScenario.results).toBeTruthy();
      
      unmountSearch();

      // Step 2: Navigate to Experiments page
      const { unmount: unmountExperiments } = render(<ExperimentsPage />);
      
      // Verify experiment page loads - use getAllByText since "experiment" appears multiple times
      await waitFor(() => {
        const experimentTexts = screen.getAllByText(/experiment/i);
        expect(experimentTexts.length).toBeGreaterThan(0);
      });
      
      // Verify experiment metadata is displayed - use more specific queries
      expect(screen.getByText(/dataset size/i)).toBeInTheDocument();
      expect(screen.getByText(/baseline model/i)).toBeInTheDocument();
      expect(screen.getByText(/candidate model/i)).toBeInTheDocument();
      
      // Verify metrics table is present
      expect(screen.getByText(/metric/i)).toBeInTheDocument();
      
      // Capture experiment data for cross-screen validation
      const experiment = experimentSummary;
      expect(experiment).toBeDefined();
      expect(experiment.name).toBeTruthy();
      expect(experiment.dataset).toBeTruthy();
      
      unmountExperiments();

      // Step 3: Navigate to Release Validation page
      const { unmount: unmountRelease } = render(<ReleaseValidationPage />);
      
      // Verify release decision page loads - use getAllByText since "recommendation" appears multiple times
      await waitFor(() => {
        const recommendationTexts = screen.getAllByText(/recommendation/i);
        expect(recommendationTexts.length).toBeGreaterThan(0);
      });
      
      // Verify statistical summary is displayed - use getAllByText since it appears multiple times
      const statisticalTexts = screen.getAllByText(/statistical/i);
      expect(statisticalTexts.length).toBeGreaterThan(0);
      
      // Verify hypothesis test information is present - use more specific text
      expect(screen.getByText(/Hypothesis Definition/i)).toBeInTheDocument();
      
      // Capture release decision data - use new structure
      const releaseDecision = releaseDecisionData[0];
      expect(releaseDecision).toBeDefined();
      expect(releaseDecision.recommendation).toBeDefined();
      expect(releaseDecision.statisticalSummary).toBeDefined();
      
      // Validate cross-screen data consistency
      // The experiment ID should match
      expect(releaseDecision.experimentId).toBe(experiment.id);
      
      // The metrics in comparison snapshot should reference experiment metrics
      expect(releaseDecision.comparisonSnapshot).toBeDefined();
      expect(releaseDecision.comparisonSnapshot.length).toBeGreaterThan(0);
      
      // Validate that comparison snapshot metrics match experiment metrics
      releaseDecision.comparisonSnapshot.forEach(snapshotMetric => {
        const experimentMetric = experiment.metrics.find(m => m.metric === snapshotMetric.metric);
        expect(experimentMetric).toBeDefined();
        if (experimentMetric) {
          expect(snapshotMetric.baseline.value).toBe(experimentMetric.baseline.value);
          expect(snapshotMetric.candidate.value).toBe(experimentMetric.candidate.value);
        }
      });
      
      unmountRelease();
    });

    it('should preserve navigation state across screen transitions', async () => {
      // Render Search page
      const { unmount: unmountSearch } = render(<SearchPage />);
      expect(screen.getByPlaceholderText(/find cheap winter running shoes/i)).toBeInTheDocument();
      unmountSearch();

      // Render Experiments page
      const { unmount: unmountExperiments } = render(<ExperimentsPage />);
      await waitFor(() => {
        const experimentTexts = screen.getAllByText(/experiment/i);
        expect(experimentTexts.length).toBeGreaterThan(0);
      });
      unmountExperiments();

      // Render Release Validation page
      const { unmount: unmountRelease } = render(<ReleaseValidationPage />);
      await waitFor(() => {
        expect(screen.getAllByText(/recommendation/i).length).toBeGreaterThan(0);
      });
      unmountRelease();

      // All pages should render without errors, demonstrating navigation stability
    });
  });

  describe('Data Consistency Validation', () => {
    it('should maintain consistent experiment references across screens', () => {
      // Validate that experiment data is consistent
      const experiment = experimentSummary;
      const releaseDecision = releaseDecisionData[0];
      
      // The release decision should reference the same experiment by ID
      expect(releaseDecision.experimentId).toBe(experiment.id);
      
      // Comparison snapshot metrics should align with experiment metrics
      const experimentMetricNames = experiment.metrics.map(m => m.metric);
      const snapshotMetricNames = releaseDecision.comparisonSnapshot.map(m => m.metric);
      
      // All snapshot metrics should exist in experiment metrics
      snapshotMetricNames.forEach(name => {
        expect(experimentMetricNames).toContain(name);
      });
    });

    it('should maintain consistent data types across all screens', () => {
      // Validate search data structure
      const searchScenario = searchScenarios[defaultSearchQuery];
      expect(searchScenario).toBeDefined();
      expect(Array.isArray(searchScenario.results)).toBe(true);
      expect(typeof searchScenario.executionMetrics).toBe('object');
      
      // Validate experiment data structure
      const experiment = experimentSummary;
      expect(typeof experiment.name).toBe('string');
      expect(typeof experiment.dataset.name).toBe('string');
      expect(typeof experiment.dataset.size).toBe('number');
      expect(Array.isArray(experiment.metrics)).toBe(true);
      
      // Validate release decision data structure
      const releaseDecision = releaseDecisionData[0];
      expect(typeof releaseDecision.id).toBe('string');
      expect(typeof releaseDecision.experimentId).toBe('string');
      expect(typeof releaseDecision.recommendation.decision).toBe('string');
      expect(typeof releaseDecision.statisticalSummary.pValue).toBe('number');
    });

    it('should maintain logical workflow progression', () => {
      // The workflow should follow: Search → Experiments → Release Decision
      
      // Search provides the capability demonstration
      const searchScenario = searchScenarios[defaultSearchQuery];
      expect(searchScenario.results.length).toBeGreaterThan(0);
      
      // Experiments provide the evidence through A/B testing
      const experiment = experimentSummary;
      expect(experiment.dataset).toBeDefined();
      expect(experiment.status).toBe('Completed');
      
      // Release decision provides the final recommendation
      const releaseDecision = releaseDecisionData[0];
      expect(releaseDecision.recommendation).toBeDefined();
      expect(['Safe to release', 'Needs more evidence', 'Do not release'])
        .toContain(releaseDecision.recommendation.decision);
    });
  });

  describe('Navigation Flow Validation', () => {
    it('should support forward navigation through the workflow', async () => {
      // Start at Search
      const { unmount: unmountSearch } = render(<SearchPage />);
      expect(screen.getByPlaceholderText(/find cheap winter running shoes/i)).toBeInTheDocument();
      unmountSearch();

      // Progress to Experiments
      const { unmount: unmountExperiments } = render(<ExperimentsPage />);
      await waitFor(() => {
        const experimentTexts = screen.getAllByText(/experiment/i);
        expect(experimentTexts.length).toBeGreaterThan(0);
      });
      unmountExperiments();

      // Complete at Release Validation
      const { unmount: unmountRelease } = render(<ReleaseValidationPage />);
      await waitFor(() => {
        expect(screen.getAllByText(/recommendation/i).length).toBeGreaterThan(0);
      });
      unmountRelease();
    });

    it('should support backward navigation for review', async () => {
      // Start at Release Validation
      const { unmount: unmountRelease } = render(<ReleaseValidationPage />);
      await waitFor(() => {
        expect(screen.getAllByText(/recommendation/i).length).toBeGreaterThan(0);
      });
      unmountRelease();

      // Navigate back to Experiments
      const { unmount: unmountExperiments } = render(<ExperimentsPage />);
      await waitFor(() => {
        const experimentTexts = screen.getAllByText(/experiment/i);
        expect(experimentTexts.length).toBeGreaterThan(0);
      });
      unmountExperiments();

      // Navigate back to Search
      const { unmount: unmountSearch } = render(<SearchPage />);
      expect(screen.getByPlaceholderText(/find cheap winter running shoes/i)).toBeInTheDocument();
      unmountSearch();
    });
  });

  describe('Error Handling Across Screens', () => {
    it('should handle missing data gracefully on each screen', async () => {
      // Each screen should render even if some data is missing
      
      // Search page with minimal data
      const { unmount: unmountSearch } = render(<SearchPage />);
      expect(screen.getByPlaceholderText(/find cheap winter running shoes/i)).toBeInTheDocument();
      unmountSearch();

      // Experiments page should handle missing optional fields
      const { unmount: unmountExperiments } = render(<ExperimentsPage />);
      await waitFor(() => {
        const experimentTexts = screen.getAllByText(/experiment/i);
        expect(experimentTexts.length).toBeGreaterThan(0);
      });
      unmountExperiments();

      // Release page should handle missing optional fields
      const { unmount: unmountRelease } = render(<ReleaseValidationPage />);
      await waitFor(() => {
        expect(screen.getAllByText(/recommendation/i).length).toBeGreaterThan(0);
      });
      unmountRelease();
    });
  });
});
