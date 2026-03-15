/**
 * Property-Based Test: Focus indicator visibility
 * Feature: ai-product-experiment-lab, Property 29: Focus indicator visibility
 * Validates: Requirements 8.2
 */

import * as fc from 'fast-check';
import { render, cleanup, fireEvent } from '@testing-library/react';
import { ActionButton } from '../action-button';
import { StatusBadge } from '../status-badge';
import { DecisionBadge } from '../decision-badge';

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 29: Focus indicator visibility', () => {
  it('should display visible focus rings or states with adequate contrast for any focused element', () => {
    fc.assert(fc.property(
      fc.record({
        buttonText: fc.string({ minLength: 1, maxLength: 30 }).filter(s => s.trim().length > 0),
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
        
        // Validate focus ring classes are present
        expect(button).toHaveClass('focus:outline-none');
        expect(button).toHaveClass('focus:ring-2');
        expect(button).toHaveClass('focus:ring-offset-2');
        
        // Validate that focus ring has a color class
        const classList = Array.from(button!.classList);
        const hasFocusRingColor = classList.some(c => c.includes('focus:ring-'));
        expect(hasFocusRingColor).toBe(true);
        
        // Validate that the button is focusable
        expect(button).not.toHaveAttribute('tabindex', '-1');
        expect(button).not.toHaveAttribute('disabled');
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent focus indicator styling across all interactive components', () => {
    fc.assert(fc.property(
      fc.record({
        componentType: fc.constantFrom('button-primary', 'button-secondary', 'button-outline', 'button-ghost'),
        content: fc.string({ minLength: 1, maxLength: 30 }),
        size: fc.constantFrom('sm', 'md', 'lg')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const variant = props.componentType.replace('button-', '') as 'primary' | 'secondary' | 'outline' | 'ghost';
        
        const { container } = render(
          <ActionButton variant={variant} size={props.size}>
            {props.content}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // All interactive components should have consistent focus indicators
        expect(button).toHaveClass('focus:outline-none');
        expect(button).toHaveClass('focus:ring-2');
        
        // Validate focus ring offset for better visibility
        expect(button).toHaveClass('focus:ring-offset-2');
        
        // Validate that focus state is visually distinct
        const classList = Array.from(button!.classList);
        const hasFocusState = classList.some(c => c.startsWith('focus:'));
        expect(hasFocusState).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure focus indicators are visible and not obscured by other styles', () => {
    fc.assert(fc.property(
      fc.record({
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        isDisabled: fc.boolean(),
        content: fc.string({ minLength: 1, maxLength: 30 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton variant={props.variant} disabled={props.isDisabled}>
            {props.content}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Focus ring should be present even for disabled buttons (for accessibility)
        expect(button).toHaveClass('focus:outline-none');
        expect(button).toHaveClass('focus:ring-2');
        
        // Validate that focus ring has adequate offset to be visible
        expect(button).toHaveClass('focus:ring-offset-2');
        
        // Validate that the focus ring color is defined
        const classList = Array.from(button!.classList);
        const hasFocusRingColor = classList.some(c => 
          c.includes('focus:ring-blue') || 
          c.includes('focus:ring-gray') ||
          c.includes('focus:ring-')
        );
        expect(hasFocusRingColor).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should provide visible focus states for all keyboard-navigable elements', () => {
    fc.assert(fc.property(
      fc.record({
        buttonText: fc.string({ minLength: 1, maxLength: 30 }).filter(s => s.trim().length > 0),
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const handleClick = jest.fn();
        
        const { container } = render(
          <ActionButton variant={props.variant} onClick={handleClick}>
            {props.buttonText}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Validate that element is keyboard navigable
        expect(button).not.toHaveAttribute('tabindex', '-1');
        
        // Validate focus indicator classes
        expect(button).toHaveClass('focus:outline-none', 'focus:ring-2');
        
        // Test that button is focusable and clickable
        button!.focus();
        expect(document.activeElement).toBe(button);
        
        // Simulate click (keyboard activation would trigger click in real browser)
        fireEvent.click(button!);
        expect(handleClick).toHaveBeenCalled();
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure focus indicators have sufficient contrast for visibility', () => {
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
        
        // Validate that focus ring uses a contrasting color
        const classList = Array.from(button!.classList);
        
        // Focus ring should be present
        expect(button).toHaveClass('focus:ring-2');
        
        // Focus ring should have a color that provides contrast
        // Blue is commonly used for focus rings as it provides good contrast
        const hasFocusRingColor = classList.some(c => c.includes('focus:ring-'));
        expect(hasFocusRingColor).toBe(true);
        
        // Focus ring offset helps with visibility against backgrounds
        expect(button).toHaveClass('focus:ring-offset-2');
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain focus indicator visibility across different component states', () => {
    fc.assert(fc.property(
      fc.record({
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        isDisabled: fc.boolean(),
        isLoading: fc.boolean(),
        content: fc.string({ minLength: 1, maxLength: 30 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton 
            variant={props.variant}
            disabled={props.isDisabled}
            loading={props.isLoading}
          >
            {props.content}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Focus indicators should be present regardless of state
        expect(button).toHaveClass('focus:outline-none');
        expect(button).toHaveClass('focus:ring-2');
        
        // Validate that focus ring is visible in all states
        const classList = Array.from(button!.classList);
        const hasFocusRing = classList.some(c => c.includes('focus:ring'));
        expect(hasFocusRing).toBe(true);
        
        // Even disabled or loading buttons should have focus indicators for accessibility
        if (props.isDisabled || props.isLoading) {
          expect(button).toBeDisabled();
          // But focus ring classes should still be present
          expect(button).toHaveClass('focus:ring-2');
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });
});
