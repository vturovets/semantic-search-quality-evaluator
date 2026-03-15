/**
 * Property-Based Test: Navigation completeness
 * Feature: ai-product-experiment-lab, Property 15: Navigation completeness
 * Validates: Requirements 4.1
 */

import * as fc from 'fast-check';
import { render, screen, cleanup } from '@testing-library/react';
import { usePathname } from 'next/navigation';
import { AppHeader } from '../AppHeader';
import { demoConfig } from '../../../lib/constants/demo-config';

// Mock Next.js navigation hook
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}));

const mockedUsePathname = usePathname as jest.MockedFunction<typeof usePathname>;

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 15: Navigation completeness', () => {
  it('should provide sticky header with product branding and navigation to all three main sections for any page render', () => {
    fc.assert(fc.property(
      fc.constantFrom('/search', '/experiments', '/release-validation', '/', '/other-route'),
      (currentPath) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Mock the current pathname
        mockedUsePathname.mockReturnValue(currentPath);
        
        // Render the AppHeader component
        const { container } = render(<AppHeader />);
        
        // Validate product branding is present
        const productBranding = container.querySelector('h1');
        expect(productBranding).toBeInTheDocument();
        expect(productBranding?.textContent).toBe(demoConfig.productName);
        
        // Validate that all three main navigation sections are present
        const requiredSections = ['Search', 'Experiments', 'Release Validation'];
        
        requiredSections.forEach(sectionLabel => {
          const navigationLink = screen.getByRole('link', { name: sectionLabel });
          expect(navigationLink).toBeInTheDocument();
        });
        
        // Validate that navigation links have correct hrefs
        const searchLink = screen.getByRole('link', { name: 'Search' });
        expect(searchLink).toHaveAttribute('href', '/search');
        
        const experimentsLink = screen.getByRole('link', { name: 'Experiments' });
        expect(experimentsLink).toHaveAttribute('href', '/experiments');
        
        const releaseValidationLink = screen.getByRole('link', { name: 'Release Validation' });
        expect(releaseValidationLink).toHaveAttribute('href', '/release-validation');
        
        // Validate sticky header styling is applied
        const header = container.querySelector('header');
        expect(header).toHaveClass('sticky', 'top-0');
        
        // Validate that the header contains navigation structure
        const navigation = container.querySelector('nav');
        expect(navigation).toBeInTheDocument();
        
        // Validate that all navigation items from config are rendered
        demoConfig.navigation.forEach(navItem => {
          const link = screen.getByRole('link', { name: navItem.label });
          expect(link).toBeInTheDocument();
          expect(link).toHaveAttribute('href', navItem.href);
        });
      }
    ), { numRuns: 100 });
  });

  it('should maintain navigation completeness regardless of component props', () => {
    fc.assert(fc.property(
      fc.record({
        className: fc.option(fc.string(), { nil: undefined })
      }),
      fc.constantFrom('/search', '/experiments', '/release-validation'),
      (props, currentPath) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Mock the current pathname
        mockedUsePathname.mockReturnValue(currentPath);
        
        // Render with various props
        const { container } = render(<AppHeader {...props} />);
        
        // Core navigation elements should always be present regardless of props
        const productBranding = container.querySelector('h1');
        expect(productBranding?.textContent).toBe(demoConfig.productName);
        
        expect(screen.getByRole('link', { name: 'Search' })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Experiments' })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Release Validation' })).toBeInTheDocument();
        
        // Navigation should be functional
        const navigation = container.querySelector('nav');
        expect(navigation).toBeInTheDocument();
        
        // All required navigation links should be present and functional
        const navigationLinks = screen.getAllByRole('link');
        const navigationLabels = navigationLinks.map(link => link.textContent);
        
        expect(navigationLabels).toContain('Search');
        expect(navigationLabels).toContain('Experiments');
        expect(navigationLabels).toContain('Release Validation');
      }
    ), { numRuns: 100 });
  });

  it('should ensure navigation structure matches demo configuration', () => {
    fc.assert(fc.property(
      fc.constant(demoConfig),
      fc.constantFrom('/search', '/experiments', '/release-validation'),
      (config, currentPath) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Mock the current pathname
        mockedUsePathname.mockReturnValue(currentPath);
        
        const { container } = render(<AppHeader />);
        
        // Validate that the rendered navigation matches the configuration
        expect(config.navigation).toHaveLength(3);
        
        // Each navigation item from config should be rendered
        config.navigation.forEach(navItem => {
          const link = screen.getByRole('link', { name: navItem.label });
          expect(link).toBeInTheDocument();
          expect(link).toHaveAttribute('href', navItem.href);
        });
        
        // Product name should match configuration
        const productBranding = container.querySelector('h1');
        expect(productBranding?.textContent).toBe(config.productName);
        
        // Validate that navigation covers all main sections as required
        const mainSections = ['/search', '/experiments', '/release-validation'];
        const configHrefs = config.navigation.map(item => item.href);
        
        mainSections.forEach(section => {
          expect(configHrefs).toContain(section);
        });
      }
    ), { numRuns: 100 });
  });
});