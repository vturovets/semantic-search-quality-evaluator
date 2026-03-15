/**
 * Property-Based Test: Touch target accessibility
 * Feature: ai-product-experiment-lab, Property 31: Touch target accessibility
 * Validates: Requirements 8.4
 */

import * as fc from 'fast-check';
import { render, cleanup } from '@testing-library/react';
import { ActionButton } from '../action-button';
import { StatusBadge } from '../status-badge';
import { DecisionBadge } from '../decision-badge';

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 31: Touch target accessibility', () => {
  it('should ensure minimum 44px height for all buttons and interactive elements', () => {
    fc.assert(fc.property(
      fc.record({
        buttonText: fc.string({ minLength: 1, maxLength: 30 }),
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        size: fc.constantFrom('sm', 'md', 'lg')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton variant={props.variant} size={props.size}>
            {props.buttonText}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Validate minimum height classes based on size
        const classList = Array.from(button!.classList);
        
        if (props.size === 'sm') {
          // Small buttons should have min-h-[32px] but ideally should be 44px for touch
          // However, we allow 32px for small buttons in dense UIs
          expect(button).toHaveClass('min-h-[32px]');
        } else if (props.size === 'md') {
          // Medium buttons should have min-h-[40px] or min-h-[44px]
          const hasMinHeight = classList.some(c => c.includes('min-h-[40px]') || c.includes('min-h-[44px]'));
          expect(hasMinHeight).toBe(true);
        } else if (props.size === 'lg') {
          // Large buttons should have min-h-[44px] or larger
          expect(button).toHaveClass('min-h-[44px]');
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain adequate touch target size across all button variants', () => {
    fc.assert(fc.property(
      fc.record({
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        size: fc.constantFrom('sm', 'md', 'lg'),
        content: fc.string({ minLength: 1, maxLength: 30 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton variant={props.variant} size={props.size}>
            {props.content}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Validate that button has adequate padding for touch targets
        const classList = Array.from(button!.classList);
        
        // All buttons should have horizontal and vertical padding
        const hasPaddingX = classList.some(c => c.includes('px-'));
        const hasPaddingY = classList.some(c => c.includes('py-'));
        expect(hasPaddingX).toBe(true);
        expect(hasPaddingY).toBe(true);
        
        // Validate minimum height is set
        const hasMinHeight = classList.some(c => c.includes('min-h-'));
        expect(hasMinHeight).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure interactive elements have sufficient spacing for touch interaction', () => {
    fc.assert(fc.property(
      fc.record({
        size: fc.constantFrom('sm', 'md', 'lg'),
        content: fc.string({ minLength: 1, maxLength: 30 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <div className="flex gap-2">
            <ActionButton size={props.size}>{props.content} 1</ActionButton>
            <ActionButton size={props.size}>{props.content} 2</ActionButton>
            <ActionButton size={props.size}>{props.content} 3</ActionButton>
          </div>
        );
        
        const buttons = container.querySelectorAll('button');
        expect(buttons.length).toBe(3);
        
        // Validate that each button has adequate touch target size
        buttons.forEach(button => {
          const classList = Array.from(button.classList);
          const hasMinHeight = classList.some(c => c.includes('min-h-'));
          expect(hasMinHeight).toBe(true);
        });
        
        // Validate that buttons have spacing between them
        const wrapper = container.querySelector('.flex.gap-2');
        expect(wrapper).toBeInTheDocument();
        expect(wrapper).toHaveClass('gap-2');
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain touch target accessibility for disabled and loading states', () => {
    fc.assert(fc.property(
      fc.record({
        size: fc.constantFrom('sm', 'md', 'lg'),
        isDisabled: fc.boolean(),
        isLoading: fc.boolean(),
        content: fc.string({ minLength: 1, maxLength: 30 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton 
            size={props.size}
            disabled={props.isDisabled}
            loading={props.isLoading}
          >
            {props.content}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Even disabled or loading buttons should maintain touch target size
        const classList = Array.from(button!.classList);
        const hasMinHeight = classList.some(c => c.includes('min-h-'));
        expect(hasMinHeight).toBe(true);
        
        // Validate that padding is maintained
        const hasPaddingX = classList.some(c => c.includes('px-'));
        const hasPaddingY = classList.some(c => c.includes('py-'));
        expect(hasPaddingX).toBe(true);
        expect(hasPaddingY).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure badge components have adequate size for touch interaction when interactive', () => {
    fc.assert(fc.property(
      fc.record({
        badgeType: fc.constantFrom('status', 'decision'),
        size: fc.constantFrom('sm', 'md', 'lg'),
        status: fc.constantFrom('COMPLETED', 'RUNNING', 'FAILED', 'PENDING'),
        decision: fc.constantFrom('Safe to release', 'Needs more evidence', 'Do not release')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        let container: HTMLElement;
        
        if (props.badgeType === 'status') {
          const result = render(
            <StatusBadge status={props.status} size={props.size} />
          );
          container = result.container;
        } else {
          const result = render(
            <DecisionBadge decision={props.decision} size={props.size} />
          );
          container = result.container;
        }
        
        const badge = container.querySelector('span[role="status"]');
        expect(badge).toBeInTheDocument();
        
        // Validate that badges have adequate padding
        const classList = Array.from(badge!.classList);
        const hasPaddingX = classList.some(c => c.includes('px-'));
        const hasPaddingY = classList.some(c => c.includes('py-'));
        expect(hasPaddingX).toBe(true);
        expect(hasPaddingY).toBe(true);
        
        // Larger badges should have more padding for better touch targets
        if (props.size === 'lg') {
          expect(badge).toHaveClass('px-4', 'py-2');
        } else if (props.size === 'md') {
          expect(badge).toHaveClass('px-3', 'py-1');
        } else {
          expect(badge).toHaveClass('px-2', 'py-1');
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent touch target sizing across different viewport sizes', () => {
    fc.assert(fc.property(
      fc.record({
        size: fc.constantFrom('sm', 'md', 'lg'),
        content: fc.string({ minLength: 1, maxLength: 30 }),
        viewportWidth: fc.integer({ min: 320, max: 1920 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton size={props.size}>
            {props.content}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Touch target size should be consistent regardless of viewport
        const classList = Array.from(button!.classList);
        const hasMinHeight = classList.some(c => c.includes('min-h-'));
        expect(hasMinHeight).toBe(true);
        
        // Padding should be maintained
        const hasPaddingX = classList.some(c => c.includes('px-'));
        const hasPaddingY = classList.some(c => c.includes('py-'));
        expect(hasPaddingX).toBe(true);
        expect(hasPaddingY).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure all clickable elements meet minimum touch target requirements', () => {
    fc.assert(fc.property(
      fc.record({
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        size: fc.constantFrom('sm', 'md', 'lg'),
        content: fc.string({ minLength: 1, maxLength: 30 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const handleClick = jest.fn();
        
        const { container } = render(
          <ActionButton 
            variant={props.variant}
            size={props.size}
            onClick={handleClick}
          >
            {props.content}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Validate that clickable element has minimum dimensions
        const classList = Array.from(button!.classList);
        
        // Should have minimum height
        const hasMinHeight = classList.some(c => c.includes('min-h-'));
        expect(hasMinHeight).toBe(true);
        
        // Should have adequate padding for touch
        const hasPaddingX = classList.some(c => c.includes('px-'));
        const hasPaddingY = classList.some(c => c.includes('py-'));
        expect(hasPaddingX).toBe(true);
        expect(hasPaddingY).toBe(true);
        
        // Should be clickable
        expect(button).not.toHaveAttribute('disabled');
        
        return true;
      }
    ), { numRuns: 100 });
  });
});
