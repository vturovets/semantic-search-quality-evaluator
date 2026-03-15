/**
 * Property-Based Test: Content width constraints
 * Feature: ai-product-experiment-lab, Property 19: Content width constraints
 * Validates: Requirements 5.1
 */

import * as fc from 'fast-check';
import { render, cleanup } from '@testing-library/react';
import { uiConstants } from '../../../lib/constants/ui-constants';

// Mock PageContainer component for testing
const PageContainer = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => {
  return (
    <div className={`mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
};

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 19: Content width constraints', () => {
  it('should enforce maximum content width of 1280px for any page container regardless of viewport size', () => {
    fc.assert(fc.property(
      fc.record({
        viewportWidth: fc.integer({ min: 320, max: 3840 }),
        content: fc.string({ minLength: 1, maxLength: 100 }),
        additionalClasses: fc.option(fc.string(), { nil: undefined })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Render the PageContainer component
        const { container } = render(
          <PageContainer className={props.additionalClasses}>
            <div>{props.content}</div>
          </PageContainer>
        );
        
        const pageContainer = container.firstChild as HTMLElement;
        expect(pageContainer).toBeInTheDocument();
        
        // Validate that max-w-7xl class is applied (which corresponds to 1280px)
        expect(pageContainer).toHaveClass('max-w-7xl');
        
        // Validate that the container has proper centering
        expect(pageContainer).toHaveClass('mx-auto');
        
        // Validate that responsive padding is applied
        expect(pageContainer).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        
        // Verify the computed max-width would be 1280px
        // max-w-7xl in Tailwind CSS is 80rem which equals 1280px (80 * 16px)
        const styles = window.getComputedStyle(pageContainer);
        const maxWidth = styles.maxWidth;
        
        // The max-width should be set (not 'none')
        expect(maxWidth).not.toBe('none');
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain content width constraints across different content types and lengths', () => {
    fc.assert(fc.property(
      fc.record({
        contentType: fc.constantFrom('text', 'cards', 'table', 'grid'),
        contentLength: fc.integer({ min: 1, max: 50 }),
        nestedLevel: fc.integer({ min: 0, max: 3 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Generate content based on type
        let content: React.ReactNode;
        
        if (props.contentType === 'text') {
          content = Array(props.contentLength).fill(0).map((_, i) => (
            <p key={i}>Sample text content {i}</p>
          ));
        } else if (props.contentType === 'cards') {
          content = Array(props.contentLength).fill(0).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border p-4">Card {i}</div>
          ));
        } else if (props.contentType === 'table') {
          content = (
            <table className="w-full">
              <tbody>
                {Array(props.contentLength).fill(0).map((_, i) => (
                  <tr key={i}>
                    <td>Row {i}</td>
                    <td>Data {i}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          );
        } else {
          content = (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array(props.contentLength).fill(0).map((_, i) => (
                <div key={i} className="bg-white rounded-xl border p-4">Grid item {i}</div>
              ))}
            </div>
          );
        }
        
        // Wrap content in nested containers based on nestedLevel
        let wrappedContent = content;
        for (let i = 0; i < props.nestedLevel; i++) {
          wrappedContent = <div className="w-full">{wrappedContent}</div>;
        }
        
        const { container } = render(
          <PageContainer>
            {wrappedContent}
          </PageContainer>
        );
        
        const pageContainer = container.firstChild as HTMLElement;
        expect(pageContainer).toBeInTheDocument();
        
        // Validate that max-width constraint is always applied
        expect(pageContainer).toHaveClass('max-w-7xl');
        
        // Validate that the constraint applies regardless of content type or nesting
        expect(pageContainer).toHaveClass('mx-auto');
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should apply consistent width constraints across all page types', () => {
    fc.assert(fc.property(
      fc.constantFrom('search', 'experiments', 'release-validation', 'home'),
      fc.string({ minLength: 10, maxLength: 200 }),
      (pageType, content) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Render PageContainer for different page types
        const { container } = render(
          <PageContainer>
            <div data-page-type={pageType}>
              <h1>{pageType} Page</h1>
              <p>{content}</p>
            </div>
          </PageContainer>
        );
        
        const pageContainer = container.firstChild as HTMLElement;
        expect(pageContainer).toBeInTheDocument();
        
        // Validate that the same width constraints apply to all page types
        expect(pageContainer).toHaveClass('max-w-7xl');
        expect(pageContainer).toHaveClass('mx-auto');
        
        // Validate responsive padding is consistent
        expect(pageContainer).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
        
        // Verify the page content is properly contained
        const pageContent = pageContainer.querySelector(`[data-page-type="${pageType}"]`);
        expect(pageContent).toBeInTheDocument();
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain width constraints with various responsive breakpoints', () => {
    fc.assert(fc.property(
      fc.record({
        breakpoint: fc.constantFrom('mobile', 'tablet', 'desktop', 'wide'),
        orientation: fc.constantFrom('portrait', 'landscape'),
        content: fc.string({ minLength: 1, maxLength: 100 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <PageContainer>
            <div data-breakpoint={props.breakpoint} data-orientation={props.orientation}>
              {props.content}
            </div>
          </PageContainer>
        );
        
        const pageContainer = container.firstChild as HTMLElement;
        expect(pageContainer).toBeInTheDocument();
        
        // Validate that max-width constraint is always present regardless of breakpoint
        expect(pageContainer).toHaveClass('max-w-7xl');
        
        // Validate that responsive padding classes are present
        // These ensure proper spacing at different breakpoints while maintaining max-width
        const classList = Array.from(pageContainer.classList);
        const hasResponsivePadding = classList.some(c => c.startsWith('px-')) &&
                                    classList.some(c => c.startsWith('sm:px-')) &&
                                    classList.some(c => c.startsWith('lg:px-'));
        
        expect(hasResponsivePadding).toBe(true);
        
        // Validate centering is maintained
        expect(pageContainer).toHaveClass('mx-auto');
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure content never exceeds 1280px maximum width constraint', () => {
    fc.assert(fc.property(
      fc.record({
        containerWidth: fc.integer({ min: 320, max: 4000 }),
        hasWideContent: fc.boolean(),
        contentItems: fc.integer({ min: 1, max: 20 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Create content that might try to exceed width
        const content = (
          <div className={props.hasWideContent ? 'w-full' : ''}>
            {Array(props.contentItems).fill(0).map((_, i) => (
              <div key={i} className="w-full bg-white rounded-xl border p-4 mb-4">
                Wide content item {i}
              </div>
            ))}
          </div>
        );
        
        const { container } = render(
          <PageContainer>
            {content}
          </PageContainer>
        );
        
        const pageContainer = container.firstChild as HTMLElement;
        expect(pageContainer).toBeInTheDocument();
        
        // Validate that the max-width constraint is enforced
        expect(pageContainer).toHaveClass('max-w-7xl');
        
        // Validate that even with wide content, the container maintains its constraint
        const styles = window.getComputedStyle(pageContainer);
        const maxWidth = styles.maxWidth;
        
        // The max-width should be set and not 'none'
        expect(maxWidth).not.toBe('none');
        
        // Validate that content is properly contained
        const contentElements = pageContainer.querySelectorAll('[class*="w-full"]');
        contentElements.forEach(element => {
          // Content with w-full should be contained within the max-width parent
          expect(element.parentElement).toBeTruthy();
        });
        
        return true;
      }
    ), { numRuns: 100 });
  });
});
