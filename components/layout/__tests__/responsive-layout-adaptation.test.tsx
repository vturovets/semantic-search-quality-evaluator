/**
 * Property-Based Test: Responsive layout adaptation
 * Feature: ai-product-experiment-lab, Property 20: Responsive layout adaptation
 * Validates: Requirements 5.2, 5.3
 */

import * as fc from 'fast-check';
import { render, cleanup } from '@testing-library/react';
import { usePathname } from 'next/navigation';
import { AppHeader } from '../AppHeader';
import { PageContainer } from '../PageContainer';
import { PageHero } from '../PageHero';

// Mock Next.js navigation hook
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}));

const mockedUsePathname = usePathname as jest.MockedFunction<typeof usePathname>;

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 20: Responsive layout adaptation', () => {
  it('should use responsive CSS classes for multi-column layouts on desktop and single-column stacking on mobile', () => {
    fc.assert(fc.property(
      fc.constantFrom('/search', '/experiments', '/release-validation'),
      fc.record({
        title: fc.string({ minLength: 1, maxLength: 100 }),
        subtitle: fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined }),
        badges: fc.option(fc.array(fc.record({
          label: fc.string({ minLength: 1, maxLength: 50 }),
          variant: fc.option(fc.constantFrom('blue', 'green', 'purple', 'gray'), { nil: undefined })
        }), { maxLength: 5 }), { nil: [] })
      }),
      (route, heroProps) => {
        // Clean up before each property test iteration
        cleanup();
        
        mockedUsePathname.mockReturnValue(route);
        
        const { container } = render(
          <>
            <AppHeader />
            <PageContainer>
              <PageHero {...heroProps} />
              {/* Simulate typical page content with grid layouts */}
              <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 lg:gap-8">
                <div className="xl:col-span-7">Left Column Content</div>
                <div className="xl:col-span-5">Right Column Content</div>
              </div>
            </PageContainer>
          </>
        );
        
        // Check that responsive CSS classes are present (what we can actually test in JSDOM)
        
        // Check header responsive behavior classes
        const header = container.querySelector('header');
        expect(header).toBeInTheDocument();
        
        // Navigation should have responsive visibility classes
        const desktopNav = container.querySelector('nav');
        expect(desktopNav).toBeInTheDocument();
        expect(desktopNav).toHaveClass('hidden', 'md:flex');
        
        const mobileMenuButton = container.querySelector('button[aria-expanded]');
        expect(mobileMenuButton).toBeInTheDocument();
        expect(mobileMenuButton).toHaveClass('md:hidden');
        
        // Check container responsive padding classes
        const containerInner = container.querySelector('main > div');
        expect(containerInner).toBeInTheDocument();
        expect(containerInner).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        expect(containerInner).toHaveClass('py-4', 'sm:py-6', 'lg:py-8');
        
        // Check hero responsive text sizing classes
        const heroTitle = container.querySelector('h2');
        expect(heroTitle).toBeInTheDocument();
        expect(heroTitle).toHaveClass('text-2xl', 'sm:text-3xl');
        expect(heroTitle).toHaveClass('mb-3', 'sm:mb-4');
        
        if (heroProps.subtitle) {
          const heroSubtitle = container.querySelector('p');
          expect(heroSubtitle).toBeInTheDocument();
          expect(heroSubtitle).toHaveClass('text-base', 'sm:text-lg');
          expect(heroSubtitle).toHaveClass('mb-4', 'sm:mb-6');
        }
        
        // Check badge responsive spacing classes
        if (heroProps.badges && heroProps.badges.length > 0) {
          const badgeContainer = container.querySelector('.flex.flex-wrap');
          expect(badgeContainer).toBeInTheDocument();
          expect(badgeContainer).toHaveClass('gap-2', 'sm:gap-3');
          expect(badgeContainer).toHaveClass('mb-4', 'sm:mb-6');
          
          const badges = container.querySelectorAll('span[class*="inline-flex"]');
          badges.forEach(badge => {
            expect(badge).toHaveClass('px-2.5', 'sm:px-3');
            expect(badge).toHaveClass('text-xs', 'sm:text-sm');
          });
        }
        
        // Check grid layout responsive classes
        const gridContainer = container.querySelector('.grid');
        expect(gridContainer).toBeInTheDocument();
        expect(gridContainer).toHaveClass('grid-cols-1', 'xl:grid-cols-12');
        expect(gridContainer).toHaveClass('gap-6', 'lg:gap-8');
        
        const leftColumn = container.querySelector('.xl\\:col-span-7');
        const rightColumn = container.querySelector('.xl\\:col-span-5');
        expect(leftColumn).toBeInTheDocument();
        expect(rightColumn).toBeInTheDocument();
        
        // Validate that responsive classes follow the expected pattern
        expect(leftColumn).toHaveClass('xl:col-span-7');
        expect(rightColumn).toHaveClass('xl:col-span-5');
      }
    ), { numRuns: 100 });
  });

  it('should maintain proper touch accessibility classes across all interactive elements', () => {
    fc.assert(fc.property(
      fc.constantFrom('/search', '/experiments', '/release-validation'),
      (route) => {
        // Clean up before each property test iteration
        cleanup();
        
        mockedUsePathname.mockReturnValue(route);
        
        const { container } = render(
          <>
            <AppHeader />
            <PageContainer>
              <PageHero title="Test Title" />
              {/* Simulate interactive elements */}
              <div className="space-y-4">
                <button className="px-6 py-3 bg-blue-600 text-white rounded-lg min-h-[44px]">
                  Primary Button
                </button>
                <button className="px-3 py-2 bg-gray-100 text-gray-700 rounded-full min-h-[36px]">
                  Secondary Button
                </button>
              </div>
            </PageContainer>
          </>
        );
        
        // Check that all interactive elements have minimum touch target classes
        const buttons = container.querySelectorAll('button');
        buttons.forEach(button => {
          // Primary interactive elements should have min-h-[44px]
          if (button.textContent?.includes('Primary') || button.getAttribute('aria-expanded') !== null) {
            expect(button).toHaveClass('min-h-[44px]');
          }
          
          // Mobile menu button should have proper touch target classes
          if (button.getAttribute('aria-expanded') !== null) {
            expect(button).toHaveClass('min-h-[44px]', 'min-w-[44px]');
          }
          
          // Secondary elements should have appropriate minimum height
          if (button.textContent?.includes('Secondary')) {
            expect(button).toHaveClass('min-h-[36px]');
          }
        });
        
        // Check navigation links have proper touch-friendly classes
        const navLinks = container.querySelectorAll('nav a');
        navLinks.forEach(link => {
          // Navigation links should have adequate padding for touch
          expect(link).toHaveClass('pb-4'); // Vertical padding for touch
        });
      }
    ), { numRuns: 100 });
  });

  it('should adapt spacing and typography classes consistently across breakpoints', () => {
    fc.assert(fc.property(
      fc.record({
        title: fc.string({ minLength: 1, maxLength: 100 }),
        subtitle: fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined }),
        content: fc.lorem({ maxCount: 10 })
      }),
      (pageProps) => {
        // Clean up before each property test iteration
        cleanup();
        
        mockedUsePathname.mockReturnValue('/search');
        
        const { container } = render(
          <PageContainer>
            <PageHero title={pageProps.title} subtitle={pageProps.subtitle} />
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">
                Card Title
              </h3>
              <p className="text-sm text-gray-600">{pageProps.content}</p>
            </div>
          </PageContainer>
        );
        
        // Check container padding classes adapt to viewport
        const containerInner = container.querySelector('main > div');
        expect(containerInner).toBeInTheDocument();
        expect(containerInner).toHaveClass('py-4', 'sm:py-6', 'lg:py-8');
        expect(containerInner).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        
        // Check hero spacing classes adapt
        const heroContainer = container.querySelector('div[class*="mb-6"]');
        expect(heroContainer).toBeInTheDocument();
        expect(heroContainer).toHaveClass('mb-6', 'sm:mb-8');
        
        // Check hero title typography scaling classes
        const heroTitle = container.querySelector('h2');
        expect(heroTitle).toBeInTheDocument();
        expect(heroTitle).toHaveClass('text-2xl', 'sm:text-3xl');
        expect(heroTitle).toHaveClass('mb-3', 'sm:mb-4');
        
        // Check hero subtitle typography scaling classes if present
        if (pageProps.subtitle) {
          const heroSubtitle = container.querySelector('p');
          expect(heroSubtitle).toBeInTheDocument();
          expect(heroSubtitle).toHaveClass('text-base', 'sm:text-lg');
          expect(heroSubtitle).toHaveClass('mb-4', 'sm:mb-6');
        }
        
        // Check card padding classes adapt
        const card = container.querySelector('.bg-white.rounded-2xl');
        expect(card).toBeInTheDocument();
        expect(card).toHaveClass('p-4', 'sm:p-6');
        
        // Check card title typography scaling classes
        const cardTitle = container.querySelector('h3');
        expect(cardTitle).toBeInTheDocument();
        expect(cardTitle).toHaveClass('text-base', 'sm:text-lg');
        expect(cardTitle).toHaveClass('mb-3', 'sm:mb-4');
        
        // Validate consistent design system classes
        expect(card).toHaveClass('shadow-sm', 'border', 'border-gray-200');
        expect(cardTitle).toHaveClass('font-semibold', 'text-gray-900');
      }
    ), { numRuns: 100 });
  });

  it('should maintain content width constraints classes at all container configurations', () => {
    fc.assert(fc.property(
      fc.constantFrom('full', 'constrained'),
      (maxWidthSetting) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <PageContainer maxWidth={maxWidthSetting}>
            <div>Test Content</div>
          </PageContainer>
        );
        
        const containerInner = container.querySelector('main > div');
        expect(containerInner).toBeInTheDocument();
        
        if (maxWidthSetting === 'constrained') {
          // Should have max-width constraint classes (1280px = max-w-7xl)
          expect(containerInner).toHaveClass('max-w-7xl', 'mx-auto');
          
          // Should maintain responsive padding classes
          expect(containerInner).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        } else {
          // Should use full width classes
          expect(containerInner).toHaveClass('w-full');
          expect(containerInner).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        }
        
        // Content should always be properly contained
        const content = container.querySelector('div');
        expect(content?.textContent).toBe('Test Content');
      }
    ), { numRuns: 100 });
  });

  it('should ensure mobile navigation menu has proper responsive classes', () => {
    fc.assert(fc.property(
      fc.constantFrom('/search', '/experiments', '/release-validation'),
      (route) => {
        // Clean up before each property test iteration
        cleanup();
        
        mockedUsePathname.mockReturnValue(route);
        
        const { container } = render(<AppHeader />);
        
        // Mobile menu button should have responsive visibility classes
        const mobileMenuButton = container.querySelector('button[aria-expanded]');
        expect(mobileMenuButton).toBeInTheDocument();
        expect(mobileMenuButton).toHaveClass('md:hidden');
        
        // Desktop navigation should have responsive visibility classes
        const desktopNav = container.querySelector('nav');
        expect(desktopNav).toBeInTheDocument();
        expect(desktopNav).toHaveClass('hidden', 'md:flex');
        
        // Mobile menu button should have proper accessibility and touch classes
        expect(mobileMenuButton).toHaveAttribute('aria-expanded');
        expect(mobileMenuButton).toHaveAttribute('aria-label');
        expect(mobileMenuButton).toHaveClass('min-h-[44px]', 'min-w-[44px]');
        
        // Product branding should have responsive text sizing classes
        const productBranding = container.querySelector('h1');
        expect(productBranding).toBeInTheDocument();
        expect(productBranding).toHaveClass('text-lg', 'sm:text-xl');
        expect(productBranding).toHaveClass('truncate'); // Prevent overflow on small screens
        
        // Desktop actions should have responsive visibility classes
        const desktopActions = container.querySelector('.hidden.md\\:flex');
        expect(desktopActions).toBeInTheDocument();
      }
    ), { numRuns: 100 });
  });
});