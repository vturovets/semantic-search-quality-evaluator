/**
 * Property-Based Test: Navigation completeness
 * Validates that the Quality Evaluation navigation is complete and consistent.
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

afterEach(() => {
  cleanup();
});

describe('Navigation completeness', () => {
  it('should provide sticky header with product branding and navigation to all Quality Evaluation sub-pages for any page render', () => {
    fc.assert(fc.property(
      fc.constantFrom(
        '/quality-evaluation',
        '/quality-evaluation/intake',
        '/quality-evaluation/analysis',
        '/quality-evaluation/recommendations',
        '/quality-evaluation/reports',
        '/',
        '/other-route'
      ),
      (currentPath) => {
        cleanup();
        mockedUsePathname.mockReturnValue(currentPath);

        const { container } = render(<AppHeader />);

        // Validate product branding is present
        const productBranding = container.querySelector('h1');
        expect(productBranding).toBeInTheDocument();
        expect(productBranding?.textContent).toBe(demoConfig.productName);

        // Validate that all Quality Evaluation navigation sections are present
        const requiredSections = ['Dashboard', 'Intake', 'Analysis', 'Recommendations', 'Reports'];

        requiredSections.forEach(sectionLabel => {
          const navigationLink = screen.getByRole('link', { name: sectionLabel });
          expect(navigationLink).toBeInTheDocument();
        });

        // Validate that navigation links have correct hrefs
        expect(screen.getByRole('link', { name: 'Dashboard' })).toHaveAttribute('href', '/quality-evaluation');
        expect(screen.getByRole('link', { name: 'Intake' })).toHaveAttribute('href', '/quality-evaluation/intake');
        expect(screen.getByRole('link', { name: 'Analysis' })).toHaveAttribute('href', '/quality-evaluation/analysis');
        expect(screen.getByRole('link', { name: 'Recommendations' })).toHaveAttribute('href', '/quality-evaluation/recommendations');
        expect(screen.getByRole('link', { name: 'Reports' })).toHaveAttribute('href', '/quality-evaluation/reports');

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
      fc.constantFrom(
        '/quality-evaluation',
        '/quality-evaluation/intake',
        '/quality-evaluation/analysis'
      ),
      (props, currentPath) => {
        cleanup();
        mockedUsePathname.mockReturnValue(currentPath);

        const { container } = render(<AppHeader {...props} />);

        const productBranding = container.querySelector('h1');
        expect(productBranding?.textContent).toBe(demoConfig.productName);

        expect(screen.getByRole('link', { name: 'Dashboard' })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Intake' })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Analysis' })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Recommendations' })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Reports' })).toBeInTheDocument();

        const navigation = container.querySelector('nav');
        expect(navigation).toBeInTheDocument();
      }
    ), { numRuns: 100 });
  });

  it('should ensure navigation structure matches demo configuration', () => {
    fc.assert(fc.property(
      fc.constant(demoConfig),
      fc.constantFrom(
        '/quality-evaluation',
        '/quality-evaluation/intake',
        '/quality-evaluation/analysis'
      ),
      (config, currentPath) => {
        cleanup();
        mockedUsePathname.mockReturnValue(currentPath);

        const { container } = render(<AppHeader />);

        expect(config.navigation.length).toBe(5);

        config.navigation.forEach(navItem => {
          const link = screen.getByRole('link', { name: navItem.label });
          expect(link).toBeInTheDocument();
          expect(link).toHaveAttribute('href', navItem.href);
        });

        const productBranding = container.querySelector('h1');
        expect(productBranding?.textContent).toBe(config.productName);

        const configHrefs = config.navigation.map(item => item.href);
        const requiredPaths = [
          '/quality-evaluation',
          '/quality-evaluation/intake',
          '/quality-evaluation/analysis',
          '/quality-evaluation/recommendations',
          '/quality-evaluation/reports'
        ];
        requiredPaths.forEach(path => {
          expect(configHrefs).toContain(path);
        });
      }
    ), { numRuns: 100 });
  });
});
