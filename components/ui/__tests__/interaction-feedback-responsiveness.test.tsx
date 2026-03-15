/**
 * Property-Based Test: Interaction feedback responsiveness
 * Feature: ai-product-experiment-lab, Property 22: Interaction feedback responsiveness
 * Validates: Requirements 5.5, 7.1, 7.4
 */

import * as fc from 'fast-check';
import { render, cleanup, fireEvent } from '@testing-library/react';
import { ActionButton } from '../action-button';
import { KPIStatCard } from '../kpi-stat-card';
import { MetricCard } from '../metric-card';
import { StatusBadge } from '../status-badge';
import { DecisionBadge } from '../decision-badge';

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 22: Interaction feedback responsiveness', () => {
  it('should provide appropriate visual feedback for hover and focus states on any interactive element', () => {
    fc.assert(fc.property(
      fc.record({
        buttonText: fc.string({ minLength: 1, maxLength: 30 }).filter(s => s.trim().length > 0),
        buttonVariant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        buttonSize: fc.constantFrom('sm', 'md', 'lg'),
        isDisabled: fc.boolean()
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const handleClick = jest.fn();
        
        const { container } = render(
          <ActionButton 
            variant={props.buttonVariant}
            size={props.buttonSize}
            disabled={props.isDisabled}
            onClick={handleClick}
          >
            {props.buttonText}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Validate hover state classes are present
        const classList = Array.from(button!.classList);
        const hasHoverState = classList.some(c => c.includes('hover:'));
        expect(hasHoverState).toBe(true);
        
        // Validate focus state classes are present
        const hasFocusState = classList.some(c => c.includes('focus:'));
        expect(hasFocusState).toBe(true);
        
        // Validate transition classes for smooth feedback
        expect(button).toHaveClass('transition-all', 'duration-200');
        
        // Validate focus ring for accessibility
        expect(button).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-offset-2');
        
        // Test click interaction (should only work if not disabled)
        fireEvent.click(button!);
        if (props.isDisabled) {
          expect(handleClick).not.toHaveBeenCalled();
        } else {
          expect(handleClick).toHaveBeenCalled();
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should provide hover effects with subtle elevation for card components', () => {
    fc.assert(fc.property(
      fc.record({
        cardType: fc.constantFrom('kpi', 'metric'),
        title: fc.string({ minLength: 1, maxLength: 50 }),
        value: fc.string({ minLength: 1, maxLength: 20 }),
        variant: fc.constantFrom('default', 'success', 'warning', 'danger')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        let container: HTMLElement;
        
        if (props.cardType === 'kpi') {
          const result = render(
            <KPIStatCard 
              title={props.title}
              value={props.value}
              variant={props.variant}
            />
          );
          container = result.container;
        } else {
          const result = render(
            <MetricCard 
              title={props.title}
              value={props.value}
              subtitle="Test subtitle"
              variant={props.variant}
            />
          );
          container = result.container;
        }
        
        const card = container.querySelector('div');
        expect(card).toBeInTheDocument();
        
        // Validate that card has shadow or hover effects
        // KPIStatCard has hover:shadow-md, MetricCard may not
        const classList = Array.from(card!.classList);
        
        if (props.cardType === 'kpi') {
          // KPIStatCard should have hover shadow enhancement
          expect(card).toHaveClass('hover:shadow-md');
          expect(card).toHaveClass('transition-shadow');
        }
        
        // Validate base shadow is present for both types
        const hasBaseShadow = classList.some(c => c.includes('shadow') || c.includes('border'));
        expect(hasBaseShadow).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent interaction feedback across all button variants', () => {
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
        
        // All button variants should have consistent interaction feedback patterns
        const classList = Array.from(button!.classList);
        
        // Validate hover state is present for all variants
        const hasHoverState = classList.some(c => c.includes('hover:'));
        expect(hasHoverState).toBe(true);
        
        // Validate focus state is present for all variants
        const hasFocusState = classList.some(c => c.includes('focus:'));
        expect(hasFocusState).toBe(true);
        
        // Validate active state is present for all variants
        const hasActiveState = classList.some(c => c.includes('active:'));
        expect(hasActiveState).toBe(true);
        
        // Validate transition timing is consistent
        expect(button).toHaveClass('transition-all', 'duration-200');
        
        // Validate disabled state styling is present
        const hasDisabledState = classList.some(c => c.includes('disabled:'));
        expect(hasDisabledState).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should provide immediate visual feedback for loading states', () => {
    fc.assert(fc.property(
      fc.record({
        buttonText: fc.string({ minLength: 1, maxLength: 30 }),
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        isLoading: fc.boolean()
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton 
            variant={props.variant}
            loading={props.isLoading}
          >
            {props.buttonText}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        if (props.isLoading) {
          // Validate loading state is indicated
          expect(button).toBeDisabled();
          
          // Validate loading indicator is present
          const loadingIndicator = container.querySelector('svg[class*="animate-spin"]');
          expect(loadingIndicator).toBeInTheDocument();
        }
        
        // Validate that button maintains interaction feedback classes even when loading
        const classList = Array.from(button!.classList);
        const hasTransition = classList.some(c => c.includes('transition'));
        expect(hasTransition).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure badge components provide appropriate visual states', () => {
    fc.assert(fc.property(
      fc.record({
        badgeType: fc.constantFrom('status', 'decision'),
        status: fc.constantFrom('COMPLETED', 'RUNNING', 'FAILED', 'PENDING'),
        decision: fc.constantFrom('Safe to release', 'Needs more evidence', 'Do not release'),
        size: fc.constantFrom('sm', 'md', 'lg')
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
        
        // Validate that badges have appropriate visual styling
        expect(badge).toHaveClass('inline-flex', 'items-center', 'rounded-full', 'border', 'font-medium');
        
        // Validate that badges have color-coded states
        const classList = Array.from(badge!.classList);
        const hasColorState = classList.some(c => 
          c.includes('bg-') || c.includes('text-') || c.includes('border-')
        );
        expect(hasColorState).toBe(true);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain interaction feedback consistency across different component states', () => {
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
        
        // Validate that interaction feedback is always present
        const classList = Array.from(button!.classList);
        
        // Transition classes should always be present
        expect(button).toHaveClass('transition-all', 'duration-200');
        
        // Focus ring should always be present for accessibility
        expect(button).toHaveClass('focus:outline-none', 'focus:ring-2');
        
        // Disabled or loading state should prevent interaction
        if (props.isDisabled || props.isLoading) {
          expect(button).toBeDisabled();
          
          // Disabled styling should be present
          const hasDisabledStyle = classList.some(c => c.includes('disabled:'));
          expect(hasDisabledStyle).toBe(true);
        } else {
          // Interactive states should be present when not disabled
          const hasHoverState = classList.some(c => c.includes('hover:'));
          const hasActiveState = classList.some(c => c.includes('active:'));
          
          expect(hasHoverState).toBe(true);
          expect(hasActiveState).toBe(true);
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });
});
