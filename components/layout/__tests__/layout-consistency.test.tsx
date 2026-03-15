/**
 * Property-Based Test: Layout consistency across routes
 * Feature: ai-product-experiment-lab, Property 16: Layout consistency across routes
 * Validates: Requirements 4.2
 */

import * as fc from 'fast-check';
import { render, cleanup } from '@testing-library/react';
import { usePathname } from 'next/navigation';
import { AppHeader } from '../AppHeader';
import { PageContainer } from '../PageContainer';
import { PageHero } from '../PageHero';
import { uiConstants, designTokens } from '../../../lib/constants/ui-constants';

// Mock Next.js navigation hook
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}));

const mockedUsePathname = usePathname as jest.MockedFunction<typeof usePathname>;

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 16: Layout consistency across routes', () => {
  it('should maintain consistent layout elements (header, container width, spacing) for any navigation between pages', () => {
    fc.assert(fc.property(
      fc.constantFrom('/search', '/experiments', '/release-validation', '/', '/other-route'),
      fc.constantFrom('/search', '/experiments', '/release-validation', '/', '/other-route'),
      (fromRoute, toRoute) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Test layout consistency when navigating from one route to another
        
        // First, render layout for the "from" route
        mockedUsePathname.mockReturnValue(fromRoute);
        const { container: fromContainer } = render(<AppHeader />);
        
        // Capture layout characteristics from the first route
        const fromHeader = fromContainer.querySelector('header');
        const fromHeaderClasses = fromHeader?.className || '';
        const fromMaxWidthExists = !!fromContainer.querySelector('.max-w-7xl');
        const fromNavigationExists = !!fromContainer.querySelector('nav');
        const fromProductBrandingText = fromContainer.querySelector('h1')?.textContent || '';
        const fromProductBrandingClasses = fromContainer.querySelector('h1')?.className || '';
        
        // Clean up and render layout for the "to" route
        cleanup();
        mockedUsePathname.mockReturnValue(toRoute);
        const { container: toContainer } = render(<AppHeader />);
        
        // Capture layout characteristics from the second route
        const toHeader = toContainer.querySelector('header');
        const toHeaderClasses = toHeader?.className || '';
        const toMaxWidth = toContainer.querySelector('.max-w-7xl');
        const toNavigation = toContainer.querySelector('nav');
        const toProductBranding = toContainer.querySelector('h1');
        
        // Validate that common layout elements remain consistent
        
        // Header should maintain consistent styling classes
        expect(toHeaderClasses).toContain('sticky');
        expect(toHeaderClasses).toContain('top-0');
        expect(toHeaderClasses).toContain('bg-white/80');
        expect(toHeaderClasses).toContain('backdrop-blur-sm');
        expect(toHeaderClasses).toContain('border-b');
        expect(toHeaderClasses).toContain('border-gray-200');
        
        // Header styling should be identical across routes
        expect(fromHeaderClasses).toBe(toHeaderClasses);
        
        // Container width constraints should be consistent
        expect(toMaxWidth).toBeInTheDocument();
        expect(fromMaxWidthExists).toBe(true);
        
        // Navigation structure should be present and consistent
        expect(toNavigation).toBeInTheDocument();
        expect(fromNavigationExists).toBe(true);
        
        // Product branding should be consistent
        expect(toProductBranding?.textContent).toBe(fromProductBrandingText);
        expect(toProductBranding?.className).toBe(fromProductBrandingClasses);
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent PageContainer layout properties across different content', () => {
    fc.assert(fc.property(
      fc.record({
        maxWidth: fc.constantFrom('full', 'constrained'),
        className: fc.option(fc.string(), { nil: undefined })
      }),
      fc.lorem({ maxCount: 5 }),
      (containerProps, contentText) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <PageContainer {...containerProps}>
            <div>{contentText}</div>
          </PageContainer>
        );
        
        // Validate consistent container structure
        const mainElement = container.querySelector('main');
        expect(mainElement).toBeInTheDocument();
        expect(mainElement).toHaveClass('min-h-screen', 'bg-gray-50');
        
        // Validate container width constraints
        const innerContainer = container.querySelector('main > div');
        expect(innerContainer).toBeInTheDocument();
        
        if (containerProps.maxWidth === 'constrained') {
          expect(innerContainer).toHaveClass('max-w-7xl', 'mx-auto');
        } else {
          expect(innerContainer).toHaveClass('w-full');
        }
        
        // Validate consistent padding and spacing
        expect(innerContainer).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        expect(innerContainer).toHaveClass('py-4', 'sm:py-6', 'lg:py-8');
        
        // Content should be properly contained
        const contentElement = container.querySelector('div');
        expect(contentElement?.textContent).toBe(contentText);
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent PageHero layout structure across different props', () => {
    fc.assert(fc.property(
      fc.record({
        title: fc.string({ minLength: 1, maxLength: 100 }),
        subtitle: fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined }),
        badges: fc.option(fc.array(fc.record({
          label: fc.string({ minLength: 1, maxLength: 50 }),
          variant: fc.option(fc.constantFrom('blue', 'green', 'purple', 'gray'), { nil: undefined })
        }), { maxLength: 5 }), { nil: [] }),
        className: fc.option(fc.string(), { nil: undefined })
      }),
      (heroProps) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(<PageHero {...heroProps} />);
        
        // Validate consistent hero structure
        const heroContainer = container.firstChild as HTMLElement;
        expect(heroContainer).toBeInTheDocument();
        expect(heroContainer).toHaveClass('mb-6', 'sm:mb-8');
        
        // Title should always be present with consistent styling
        const titleElement = container.querySelector('h2');
        expect(titleElement).toBeInTheDocument();
        expect(titleElement).toHaveClass('text-2xl', 'sm:text-3xl', 'font-bold', 'text-gray-900');
        expect(titleElement).toHaveClass('mb-3', 'sm:mb-4');
        expect(titleElement?.textContent).toBe(heroProps.title);
        
        // Subtitle should be rendered if provided with consistent styling
        if (heroProps.subtitle) {
          const subtitleElement = container.querySelector('p');
          expect(subtitleElement).toBeInTheDocument();
          expect(subtitleElement).toHaveClass('text-base', 'sm:text-lg', 'text-gray-600');
          expect(subtitleElement).toHaveClass('mb-4', 'sm:mb-6');
          expect(subtitleElement?.textContent).toBe(heroProps.subtitle);
        }
        
        // Badges should be rendered if provided with consistent styling
        if (heroProps.badges && heroProps.badges.length > 0) {
          const badgeContainer = container.querySelector('.flex.flex-wrap');
          expect(badgeContainer).toBeInTheDocument();
          expect(badgeContainer).toHaveClass('gap-2', 'sm:gap-3');
          expect(badgeContainer).toHaveClass('mb-4', 'sm:mb-6');
          
          const badges = container.querySelectorAll('span[class*="inline-flex"]');
          expect(badges).toHaveLength(heroProps.badges.length);
          
          badges.forEach((badge, index) => {
            expect(badge).toHaveClass('inline-flex', 'items-center', 'rounded-full', 'font-medium');
            expect(badge).toHaveClass('px-2.5', 'sm:px-3');
            expect(badge).toHaveClass('text-xs', 'sm:text-sm');
            expect(badge.textContent).toBe(heroProps.badges![index].label);
          });
        }
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent design system values across all layout components', () => {
    fc.assert(fc.property(
      fc.constantFrom('/search', '/experiments', '/release-validation'),
      (currentRoute) => {
        // Clean up before each property test iteration
        cleanup();
        
        mockedUsePathname.mockReturnValue(currentRoute);
        
        // Test that design system constants are consistently applied
        const { container: headerContainer } = render(<AppHeader />);
        const { container: pageContainer } = render(
          <PageContainer>
            <PageHero title="Test Title" subtitle="Test Subtitle" />
          </PageContainer>
        );
        
        // Validate max-width constraint is applied consistently
        const headerMaxWidth = headerContainer.querySelector('.max-w-7xl');
        const pageMaxWidth = pageContainer.querySelector('.max-w-7xl');
        
        expect(headerMaxWidth).toBeInTheDocument();
        expect(pageMaxWidth).toBeInTheDocument();
        
        // Validate consistent spacing classes
        const headerContainer_inner = headerContainer.querySelector('.max-w-7xl');
        const pageContainer_inner = pageContainer.querySelector('.max-w-7xl');
        
        expect(headerContainer_inner).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        expect(pageContainer_inner).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        
        // Validate consistent card styling patterns
        const heroTitle = pageContainer.querySelector('h2');
        expect(heroTitle).toHaveClass('text-2xl', 'sm:text-3xl', 'font-bold', 'text-gray-900');
        
        // Validate consistent color usage
        const productBranding = headerContainer.querySelector('h1');
        expect(productBranding).toHaveClass('text-gray-900');
      }
    ), { numRuns: 100 });
  });

  it('should ensure layout components maintain structural integrity across different viewport contexts', () => {
    fc.assert(fc.property(
      fc.record({
        route: fc.constantFrom('/search', '/experiments', '/release-validation'),
        containerMaxWidth: fc.constantFrom('full', 'constrained'),
        heroTitle: fc.string({ minLength: 1, maxLength: 100 }),
        additionalClassName: fc.option(fc.string(), { nil: undefined })
      }),
      (testProps) => {
        // Clean up before each property test iteration
        cleanup();
        
        mockedUsePathname.mockReturnValue(testProps.route);
        
        // Render complete layout structure
        const { container } = render(
          <>
            <AppHeader className={testProps.additionalClassName} />
            <PageContainer maxWidth={testProps.containerMaxWidth}>
              <PageHero title={testProps.heroTitle} />
            </PageContainer>
          </>
        );
        
        // Validate that the complete layout structure is maintained
        const header = container.querySelector('header');
        const main = container.querySelector('main');
        const heroTitle = container.querySelector('h2');
        
        expect(header).toBeInTheDocument();
        expect(main).toBeInTheDocument();
        expect(heroTitle).toBeInTheDocument();
        
        // Validate header maintains sticky positioning
        expect(header).toHaveClass('sticky', 'top-0');
        
        // Validate main content area maintains proper structure
        expect(main).toHaveClass('min-h-screen', 'bg-gray-50');
        
        // Validate hero maintains proper typography hierarchy
        expect(heroTitle).toHaveClass('text-2xl', 'sm:text-3xl', 'font-bold', 'text-gray-900');
        expect(heroTitle?.textContent).toBe(testProps.heroTitle);
        
        // Validate that navigation structure is preserved
        const navigation = container.querySelector('nav');
        expect(navigation).toBeInTheDocument();
        
        // Validate that all required navigation links are present
        const navigationLinks = container.querySelectorAll('nav a');
        expect(navigationLinks.length).toBeGreaterThanOrEqual(3);
      }
    ), { numRuns: 100 });
  });
});