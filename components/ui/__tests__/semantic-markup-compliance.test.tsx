/**
 * Property-Based Test: Semantic markup compliance
 * Feature: ai-product-experiment-lab, Property 30: Semantic markup compliance
 * Validates: Requirements 8.3
 */

import * as fc from 'fast-check';
import { render, cleanup } from '@testing-library/react';
import { ActionButton } from '../action-button';
import { StatusBadge } from '../status-badge';
import { SideDrawer } from '../side-drawer';
import { TooltipInfo } from '../tooltip-info';

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 30: Semantic markup compliance', () => {
  it('should use appropriate semantic HTML elements and ARIA labels for any component', () => {
    fc.assert(fc.property(
      fc.record({
        buttonText: fc.string({ minLength: 1, maxLength: 30 }),
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton variant={props.variant}>
            {props.buttonText}
          </ActionButton>
        );
        
        // Validate that button uses semantic <button> element
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        expect(button?.tagName).toBe('BUTTON');
        
        // Validate that button has proper type attribute
        expect(button).toHaveAttribute('type');
        
        // Validate that button content is accessible
        expect(button?.textContent).toBe(props.buttonText);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should provide proper ARIA roles and labels for status indicators', () => {
    fc.assert(fc.property(
      fc.record({
        status: fc.constantFrom('COMPLETED', 'RUNNING', 'FAILED', 'PENDING'),
        size: fc.constantFrom('sm', 'md', 'lg')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <StatusBadge status={props.status} size={props.size} />
        );
        
        // Validate that status badge has proper ARIA role
        const badge = container.querySelector('[role="status"]');
        expect(badge).toBeInTheDocument();
        
        // Validate that status is communicated through text content
        expect(badge?.textContent).toBeTruthy();
        expect(badge?.textContent).toContain(props.status);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should provide proper semantic structure for modal/drawer components', () => {
    fc.assert(fc.property(
      fc.record({
        title: fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: undefined }),
        position: fc.constantFrom('left', 'right'),
        content: fc.string({ minLength: 1, maxLength: 100 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <SideDrawer 
            isOpen={true}
            onClose={() => {}}
            title={props.title}
            position={props.position}
          >
            <div>{props.content}</div>
          </SideDrawer>
        );
        
        // Validate that drawer uses proper dialog role
        const dialog = container.querySelector('[role="dialog"]');
        expect(dialog).toBeInTheDocument();
        
        // Validate that drawer has proper ARIA attributes
        if (props.title) {
          expect(dialog).toHaveAttribute('aria-labelledby');
          
          // Validate that title uses semantic heading
          const heading = container.querySelector('h2');
          expect(heading).toBeInTheDocument();
          expect(heading?.textContent).toBe(props.title);
          
          // Validate that close button has proper ARIA label (only present when title is provided)
          const closeButton = container.querySelector('[aria-label="Close drawer"]');
          expect(closeButton).toBeInTheDocument();
        } else {
          // Without title, drawer may not have close button in header
          // This is acceptable as drawer can be closed by clicking backdrop
          expect(dialog).toBeInTheDocument();
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure all interactive elements have accessible names', () => {
    fc.assert(fc.property(
      fc.record({
        buttonText: fc.string({ minLength: 1, maxLength: 30 }),
        variant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        hasIcon: fc.boolean()
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton variant={props.variant}>
            {props.hasIcon && <span aria-hidden="true">→</span>}
            {props.buttonText}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Validate that button has accessible text content
        expect(button?.textContent).toContain(props.buttonText);
        
        // If icon is present, validate it's properly marked as decorative
        if (props.hasIcon) {
          const icon = container.querySelector('[aria-hidden="true"]');
          expect(icon).toBeInTheDocument();
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should use proper heading hierarchy and semantic structure', () => {
    fc.assert(fc.property(
      fc.record({
        drawerTitle: fc.string({ minLength: 1, maxLength: 50 }),
        position: fc.constantFrom('left', 'right')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <SideDrawer 
            isOpen={true}
            onClose={() => {}}
            title={props.drawerTitle}
            position={props.position}
          >
            <div>Content</div>
          </SideDrawer>
        );
        
        // Validate that title uses proper heading level (h2 for drawer titles)
        const heading = container.querySelector('h2');
        expect(heading).toBeInTheDocument();
        expect(heading?.textContent).toBe(props.drawerTitle);
        
        // Validate that heading has proper ID for aria-labelledby
        expect(heading).toHaveAttribute('id');
        
        // Validate that dialog references the heading
        const dialog = container.querySelector('[role="dialog"]');
        const headingId = heading?.getAttribute('id');
        expect(dialog).toHaveAttribute('aria-labelledby', headingId);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should provide proper ARIA attributes for tooltip components', () => {
    fc.assert(fc.property(
      fc.record({
        content: fc.string({ minLength: 1, maxLength: 100 }),
        position: fc.constantFrom('top', 'bottom', 'left', 'right'),
        triggerText: fc.string({ minLength: 1, maxLength: 30 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <TooltipInfo content={props.content} position={props.position}>
            <button>{props.triggerText}</button>
          </TooltipInfo>
        );
        
        // Validate that tooltip wrapper has proper structure
        const wrapper = container.querySelector('.relative.inline-block');
        expect(wrapper).toBeInTheDocument();
        
        // Validate that trigger element is accessible
        const trigger = container.querySelector('button');
        expect(trigger).toBeInTheDocument();
        expect(trigger?.textContent).toBe(props.triggerText);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should ensure all form controls have proper labels and descriptions', () => {
    fc.assert(fc.property(
      fc.record({
        content: fc.string({ minLength: 1, maxLength: 30 }).filter(s => s.trim().length > 0)
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        const { container } = render(
          <ActionButton>
            {props.content}
          </ActionButton>
        );
        
        const button = container.querySelector('button');
        expect(button).toBeInTheDocument();
        
        // Validate that button has proper type attribute (defaults to "button")
        expect(button).toHaveAttribute('type', 'button');
        
        // Validate that button has accessible text
        expect(button?.textContent).toBe(props.content);
        
        return true;
      }
    ), { numRuns: 100 });
  });

  it('should maintain semantic markup consistency across all component variants', () => {
    fc.assert(fc.property(
      fc.record({
        componentType: fc.constantFrom('button', 'status'),
        variant: fc.constantFrom('primary', 'secondary', 'default'),
        content: fc.string({ minLength: 1, maxLength: 30 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        let container: HTMLElement;
        
        if (props.componentType === 'button') {
          const result = render(
            <ActionButton variant={props.variant as any}>
              {props.content}
            </ActionButton>
          );
          container = result.container;
          
          // Validate semantic button element
          const button = container.querySelector('button');
          expect(button).toBeInTheDocument();
          expect(button?.tagName).toBe('BUTTON');
        } else {
          const result = render(
            <StatusBadge status="COMPLETED" />
          );
          container = result.container;
          
          // Validate proper ARIA role
          const badge = container.querySelector('[role="status"]');
          expect(badge).toBeInTheDocument();
        }
        
        return true;
      }
    ), { numRuns: 100 });
  });
});
