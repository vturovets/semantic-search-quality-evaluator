/**
 * Property-Based Test: Design system consistency
 * Feature: ai-product-experiment-lab, Property 21: Design system consistency
 * Validates: Requirements 5.4
 */

import * as fc from 'fast-check';
import { render, cleanup } from '@testing-library/react';
import { StatusBadge } from '../status-badge';
import { DecisionBadge } from '../decision-badge';
import { KPIStatCard } from '../kpi-stat-card';
import { ActionButton } from '../action-button';
import { SideDrawer } from '../side-drawer';
import { TooltipInfo } from '../tooltip-info';
import { MetricCard } from '../metric-card';
import { ProgressBar } from '../progress-bar';
import { uiConstants, designTokens } from '../../../lib/constants/ui-constants';

// Ensure cleanup after each test
afterEach(() => {
  cleanup();
});

describe('Property 21: Design system consistency', () => {
  it('should use consistent visual design with white cards, subtle shadows, and rounded corners for any UI component', () => {
    fc.assert(fc.property(
      fc.record({
        // StatusBadge props
        status: fc.constantFrom('COMPLETED', 'RUNNING', 'FAILED', 'PENDING'),
        statusSize: fc.constantFrom('sm', 'md', 'lg'),
        
        // DecisionBadge props
        decision: fc.constantFrom('Safe to release', 'Needs more evidence', 'Do not release'),
        decisionSize: fc.constantFrom('sm', 'md', 'lg'),
        decisionVariant: fc.constantFrom('default', 'prominent'),
        
        // KPIStatCard props
        kpiTitle: fc.string({ minLength: 1, maxLength: 50 }),
        kpiValue: fc.string({ minLength: 1, maxLength: 20 }),
        kpiUnit: fc.option(fc.string({ minLength: 1, maxLength: 10 }), { nil: undefined }),
        kpiVariant: fc.constantFrom('default', 'success', 'warning', 'danger'),
        
        // ActionButton props
        buttonText: fc.string({ minLength: 1, maxLength: 30 }),
        buttonVariant: fc.constantFrom('primary', 'secondary', 'outline', 'ghost'),
        buttonSize: fc.constantFrom('sm', 'md', 'lg'),
        
        // MetricCard props
        metricTitle: fc.string({ minLength: 1, maxLength: 50 }),
        metricValue: fc.string({ minLength: 1, maxLength: 20 }),
        metricSubtitle: fc.string({ minLength: 1, maxLength: 50 }),
        metricVariant: fc.constantFrom('default', 'success', 'warning', 'danger'),
        
        // ProgressBar props
        progressLabel: fc.string({ minLength: 1, maxLength: 50 }),
        progressValue: fc.string({ minLength: 1, maxLength: 20 }),
        progressPercentage: fc.integer({ min: 0, max: 100 }),
        progressColor: fc.constantFrom('blue', 'green', 'red', 'yellow')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Test StatusBadge design consistency
        const { container: statusContainer } = render(
          <StatusBadge status={props.status} size={props.statusSize} />
        );
        
        const statusBadge = statusContainer.querySelector('span[role="status"]');
        expect(statusBadge).toBeInTheDocument();
        expect(statusBadge).toHaveClass('inline-flex', 'items-center', 'rounded-full', 'border', 'font-medium');
        
        // Validate consistent rounded corners (rounded-full for badges)
        expect(statusBadge).toHaveClass('rounded-full');
        
        // Validate consistent border styling
        expect(statusBadge).toHaveClass('border');
        
        cleanup();
        
        // Test DecisionBadge design consistency
        const { container: decisionContainer } = render(
          <DecisionBadge 
            decision={props.decision} 
            size={props.decisionSize} 
            variant={props.decisionVariant} 
          />
        );
        
        const decisionBadge = decisionContainer.querySelector('span[role="status"]');
        expect(decisionBadge).toBeInTheDocument();
        expect(decisionBadge).toHaveClass('inline-flex', 'items-center', 'rounded-full', 'border', 'font-medium');
        
        cleanup();
        
        // Test KPIStatCard design consistency (white cards with subtle shadows and rounded corners)
        const { container: kpiContainer } = render(
          <KPIStatCard 
            title={props.kpiTitle}
            value={props.kpiValue}
            unit={props.kpiUnit}
            variant={props.kpiVariant}
          />
        );
        
        const kpiCard = kpiContainer.querySelector('div');
        expect(kpiCard).toBeInTheDocument();
        expect(kpiCard).toHaveClass('rounded-xl', 'border', 'shadow-sm');
        
        // Validate consistent rounded corners (rounded-xl for cards)
        expect(kpiCard).toHaveClass('rounded-xl');
        
        // Validate subtle shadows
        expect(kpiCard).toHaveClass('shadow-sm');
        
        // Validate hover shadow enhancement
        expect(kpiCard).toHaveClass('hover:shadow-md', 'transition-shadow');
        
        cleanup();
        
        // Test ActionButton design consistency
        const { container: buttonContainer } = render(
          <ActionButton variant={props.buttonVariant} size={props.buttonSize}>
            {props.buttonText}
          </ActionButton>
        );
        
        const button = buttonContainer.querySelector('button');
        expect(button).toBeInTheDocument();
        expect(button).toHaveClass('inline-flex', 'items-center', 'justify-center', 'font-medium', 'rounded-lg');
        
        // Validate consistent rounded corners (rounded-lg for buttons)
        expect(button).toHaveClass('rounded-lg');
        
        // Validate consistent transition effects
        expect(button).toHaveClass('transition-all', 'duration-200');
        
        // Validate focus ring consistency
        expect(button).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-offset-2');
        
        cleanup();
        
        // Test MetricCard design consistency
        const { container: metricContainer } = render(
          <MetricCard 
            title={props.metricTitle}
            value={props.metricValue}
            subtitle={props.metricSubtitle}
            variant={props.metricVariant}
          />
        );
        
        const metricCard = metricContainer.querySelector('div');
        expect(metricCard).toBeInTheDocument();
        expect(metricCard).toHaveClass('rounded-xl', 'border');
        
        // Validate consistent rounded corners
        expect(metricCard).toHaveClass('rounded-xl');
        
        cleanup();
        
        // Test ProgressBar design consistency
        const { container: progressContainer } = render(
          <ProgressBar 
            label={props.progressLabel}
            value={props.progressValue}
            percentage={props.progressPercentage}
            color={props.progressColor}
          />
        );
        
        const progressBar = progressContainer.querySelector('.bg-gray-200.rounded-full');
        const progressFill = progressContainer.querySelector(`div[style*="width: ${props.progressPercentage}%"]`);
        
        expect(progressBar).toBeInTheDocument();
        expect(progressFill).toBeInTheDocument();
        
        // Validate consistent rounded corners for progress elements
        expect(progressBar).toHaveClass('rounded-full');
        expect(progressFill).toHaveClass('rounded-full');
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent color scheme and typography across all UI components', () => {
    fc.assert(fc.property(
      fc.record({
        variant: fc.constantFrom('default', 'success', 'warning', 'danger'),
        size: fc.constantFrom('sm', 'md', 'lg'),
        title: fc.string({ minLength: 1, maxLength: 50 }),
        value: fc.string({ minLength: 1, maxLength: 20 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Test consistent color schemes across components
        const { container: kpiContainer } = render(
          <KPIStatCard 
            title={props.title}
            value={props.value}
            variant={props.variant}
          />
        );
        
        const { container: metricContainer } = render(
          <MetricCard 
            title={props.title}
            value={props.value}
            subtitle="Test subtitle"
            variant={props.variant}
          />
        );
        
        // Validate consistent color application based on variant
        const kpiCard = kpiContainer.querySelector('div');
        const metricCard = metricContainer.querySelector('div');
        
        expect(kpiCard).toBeInTheDocument();
        expect(metricCard).toBeInTheDocument();
        
        // Both components should use consistent color schemes for the same variant
        if (props.variant === 'success') {
          expect(kpiCard).toHaveClass('bg-green-50', 'border-green-200', 'text-green-600');
          expect(metricCard).toHaveClass('bg-green-50', 'border-green-200', 'text-green-600');
        } else if (props.variant === 'warning') {
          expect(kpiCard).toHaveClass('bg-yellow-50', 'border-yellow-200', 'text-yellow-600');
          expect(metricCard).toHaveClass('bg-yellow-50', 'border-yellow-200', 'text-yellow-600');
        } else if (props.variant === 'danger') {
          expect(kpiCard).toHaveClass('bg-red-50', 'border-red-200', 'text-red-600');
          expect(metricCard).toHaveClass('bg-red-50', 'border-red-200', 'text-red-600');
        } else {
          // default variant
          expect(kpiCard).toHaveClass('bg-white', 'border-gray-200', 'text-gray-600');
          expect(metricCard).toHaveClass('bg-gray-50', 'border-gray-200', 'text-gray-600');
        }
        
        // Validate consistent typography hierarchy
        const kpiTitle = kpiContainer.querySelector('h3');
        const kpiValue = kpiContainer.querySelector('span[class*="text-3xl"]');
        
        expect(kpiTitle).toBeInTheDocument();
        expect(kpiValue).toBeInTheDocument();
        
        // Validate consistent font weights and sizes
        expect(kpiTitle).toHaveClass('text-sm', 'font-medium');
        expect(kpiValue).toHaveClass('text-3xl', 'font-bold');
        
        const metricValue = metricContainer.querySelector('div[class*="text-3xl"]');
        const metricSubtitle = metricContainer.querySelector('div[class*="text-sm"]');
        
        expect(metricValue).toBeInTheDocument();
        expect(metricSubtitle).toBeInTheDocument();
        
        // Both components should use consistent typography scales
        expect(metricValue).toHaveClass('text-3xl', 'font-bold');
        expect(metricSubtitle).toHaveClass('text-sm', 'font-medium');
      }
    ), { numRuns: 100 });
  });

  it('should apply consistent spacing and sizing patterns across all interactive components', () => {
    fc.assert(fc.property(
      fc.record({
        size: fc.constantFrom('sm', 'md', 'lg'),
        buttonText: fc.string({ minLength: 1, maxLength: 30 }),
        status: fc.constantFrom('COMPLETED', 'RUNNING', 'FAILED', 'PENDING'),
        decision: fc.constantFrom('Safe to release', 'Needs more evidence', 'Do not release')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Test consistent sizing patterns across interactive components
        const { container: buttonContainer } = render(
          <ActionButton size={props.size}>
            {props.buttonText}
          </ActionButton>
        );
        
        const { container: statusContainer } = render(
          <StatusBadge status={props.status} size={props.size} />
        );
        
        const { container: decisionContainer } = render(
          <DecisionBadge decision={props.decision} size={props.size} />
        );
        
        const button = buttonContainer.querySelector('button');
        const statusBadge = statusContainer.querySelector('span[role="status"]');
        const decisionBadge = decisionContainer.querySelector('span[role="status"]');
        
        expect(button).toBeInTheDocument();
        expect(statusBadge).toBeInTheDocument();
        expect(decisionBadge).toBeInTheDocument();
        
        // Validate consistent size patterns
        if (props.size === 'sm') {
          expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm', 'min-h-[32px]');
          expect(statusBadge).toHaveClass('px-2', 'py-1', 'text-xs');
          expect(decisionBadge).toHaveClass('px-2', 'py-1', 'text-xs');
        } else if (props.size === 'md') {
          expect(button).toHaveClass('px-4', 'py-2', 'text-sm', 'min-h-[40px]');
          expect(statusBadge).toHaveClass('px-3', 'py-1', 'text-sm');
          expect(decisionBadge).toHaveClass('px-3', 'py-1', 'text-sm');
        } else if (props.size === 'lg') {
          expect(button).toHaveClass('px-6', 'py-3', 'text-base', 'min-h-[44px]');
          expect(statusBadge).toHaveClass('px-4', 'py-2', 'text-base');
          expect(decisionBadge).toHaveClass('px-4', 'py-2', 'text-base');
        }
        
        // Validate consistent font weight across interactive elements
        expect(button).toHaveClass('font-medium');
        expect(statusBadge).toHaveClass('font-medium');
        expect(decisionBadge).toHaveClass('font-medium');
      }
    ), { numRuns: 100 });
  });

  it('should maintain consistent overlay and modal styling patterns', () => {
    fc.assert(fc.property(
      fc.record({
        drawerTitle: fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: undefined }),
        drawerPosition: fc.constantFrom('left', 'right'),
        drawerSize: fc.constantFrom('sm', 'md', 'lg'),
        tooltipContent: fc.string({ minLength: 1, maxLength: 100 }),
        tooltipPosition: fc.constantFrom('top', 'bottom', 'left', 'right'),
        tooltipTrigger: fc.constantFrom('hover', 'click', 'focus')
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        // Test SideDrawer design consistency
        const { container: drawerContainer } = render(
          <SideDrawer 
            isOpen={true}
            onClose={() => {}}
            title={props.drawerTitle}
            position={props.drawerPosition}
            size={props.drawerSize}
          >
            <div>Test content</div>
          </SideDrawer>
        );
        
        // Validate consistent overlay styling
        const backdrop = drawerContainer.querySelector('.bg-black.bg-opacity-50.backdrop-blur-sm');
        expect(backdrop).toBeInTheDocument();
        expect(backdrop).toHaveClass('absolute', 'inset-0', 'bg-black', 'bg-opacity-50', 'backdrop-blur-sm', 'transition-opacity');
        
        // Validate consistent drawer styling
        const drawer = drawerContainer.querySelector('[role="dialog"]');
        expect(drawer).toBeInTheDocument();
        expect(drawer).toHaveClass('h-full', 'bg-white', 'shadow-xl', 'transform', 'transition-transform', 'duration-300', 'ease-in-out');
        
        // Validate consistent header styling if title is provided
        if (props.drawerTitle) {
          const header = drawerContainer.querySelector('.border-b.border-gray-200');
          const title = drawerContainer.querySelector('h2');
          const closeButton = drawerContainer.querySelector('button[aria-label="Close drawer"]');
          
          expect(header).toBeInTheDocument();
          expect(title).toBeInTheDocument();
          expect(closeButton).toBeInTheDocument();
          
          expect(header).toHaveClass('flex', 'items-center', 'justify-between', 'p-6', 'border-b', 'border-gray-200');
          expect(title).toHaveClass('text-lg', 'font-semibold', 'text-gray-900');
          expect(closeButton).toHaveClass('p-2', 'text-gray-400', 'hover:text-gray-600', 'focus:outline-none', 'focus:ring-2', 'focus:ring-blue-500', 'rounded-lg');
        }
        
        // Validate consistent content area styling
        const content = drawerContainer.querySelector('.flex-1.overflow-y-auto.p-6');
        expect(content).toBeInTheDocument();
        expect(content).toHaveClass('flex-1', 'overflow-y-auto', 'p-6');
        
        cleanup();
        
        // Test TooltipInfo design consistency
        const { container: tooltipContainer } = render(
          <TooltipInfo 
            content={props.tooltipContent}
            position={props.tooltipPosition}
            trigger={props.tooltipTrigger}
          >
            <button>Trigger</button>
          </TooltipInfo>
        );
        
        // Validate consistent tooltip container structure
        const tooltipWrapper = tooltipContainer.querySelector('.relative.inline-block');
        expect(tooltipWrapper).toBeInTheDocument();
        expect(tooltipWrapper).toHaveClass('relative', 'inline-block');
        
        // Note: Tooltip content is only visible when triggered, so we validate the structure
        // The actual tooltip styling consistency is tested when it becomes visible
      }
    ), { numRuns: 100 });
  });

  it('should ensure all components follow the design system color palette and maintain visual hierarchy', () => {
    fc.assert(fc.property(
      fc.record({
        componentType: fc.constantFrom('status', 'decision', 'kpi', 'metric', 'button'),
        variant: fc.constantFrom('default', 'success', 'warning', 'danger'),
        content: fc.string({ minLength: 1, maxLength: 50 })
      }),
      (props) => {
        // Clean up before each property test iteration
        cleanup();
        
        let container: HTMLElement;
        let component: Element | null = null;
        
        // Render different components based on type
        if (props.componentType === 'status') {
          const { container: statusContainer } = render(
            <StatusBadge status="COMPLETED" />
          );
          container = statusContainer;
          component = container.querySelector('span[role="status"]');
        } else if (props.componentType === 'decision') {
          const { container: decisionContainer } = render(
            <DecisionBadge decision="Safe to release" />
          );
          container = decisionContainer;
          component = container.querySelector('span[role="status"]');
        } else if (props.componentType === 'kpi') {
          const { container: kpiContainer } = render(
            <KPIStatCard title={props.content} value="100" variant={props.variant as any} />
          );
          container = kpiContainer;
          component = container.querySelector('div');
        } else if (props.componentType === 'metric') {
          const { container: metricContainer } = render(
            <MetricCard title={props.content} value="100" subtitle="test" variant={props.variant as any} />
          );
          container = metricContainer;
          component = container.querySelector('div');
        } else {
          // Map variants to ActionButton supported variants
          const buttonVariant = props.variant === 'success' ? 'primary' : 
                               props.variant === 'warning' ? 'secondary' : 
                               props.variant === 'danger' ? 'outline' : 'primary';
          const { container: buttonContainer } = render(
            <ActionButton variant={buttonVariant}>
              {props.content}
            </ActionButton>
          );
          container = buttonContainer;
          component = container.querySelector('button');
        }
        
        expect(component).toBeInTheDocument();
        
        // Validate that all components maintain consistent visual hierarchy through proper use of:
        // 1. Consistent border radius patterns
        // 2. Consistent color application
        // 3. Consistent typography scales
        // 4. Consistent spacing patterns
        
        // Check for consistent border radius usage
        const hasRoundedCorners = component!.classList.contains('rounded-lg') || 
                                 component!.classList.contains('rounded-xl') || 
                                 component!.classList.contains('rounded-full');
        expect(hasRoundedCorners).toBe(true);
        
        // Check for consistent color system usage (gray, blue, green, yellow, red families)
        const hasConsistentColors = Array.from(component!.classList).some(className => 
          className.includes('gray-') || 
          className.includes('blue-') || 
          className.includes('green-') || 
          className.includes('yellow-') || 
          className.includes('red-')
        );
        expect(hasConsistentColors).toBe(true);
        
        // Check for consistent typography usage
        const hasConsistentTypography = Array.from(component!.classList).some(className => 
          className.includes('text-') || className.includes('font-')
        );
        expect(hasConsistentTypography).toBe(true);
        
        // Check for consistent spacing usage
        const hasConsistentSpacing = Array.from(component!.classList).some(className => 
          className.includes('p-') || 
          className.includes('px-') || 
          className.includes('py-') || 
          className.includes('m-') || 
          className.includes('mx-') || 
          className.includes('my-')
        );
        expect(hasConsistentSpacing).toBe(true);
      }
    ), { numRuns: 100 });
  });
});