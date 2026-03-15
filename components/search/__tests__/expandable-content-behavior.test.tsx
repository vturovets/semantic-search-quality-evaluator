/**
 * Property-Based Test: Expandable content behavior
 * Feature: ai-product-experiment-lab, Property 27: Expandable content behavior
 * Validates: Requirements 7.2, 7.3
 * 
 * This test verifies that accordion and drawer components properly show and hide
 * content with appropriate state management.
 */

import * as fc from 'fast-check'
import { render, screen, fireEvent, cleanup } from '@testing-library/react'
import { InterpretedFiltersCard } from '../InterpretedFiltersCard'
import { TraceDetailsDrawer } from '../TraceDetailsDrawer'

// Ensure cleanup after each test
afterEach(() => {
  cleanup()
})

describe('Property 27: Expandable content behavior', () => {
  // Generator for filter items
  const filterItemArb = fc.record({
    label: fc.string({ minLength: 1, maxLength: 20 }),
    value: fc.string({ minLength: 1, maxLength: 30 })
  })

  // Generator for structured output
  const structuredOutputArb = fc.dictionary(
    fc.string({ minLength: 1, maxLength: 15 }),
    fc.oneof(
      fc.string(),
      fc.integer(),
      fc.boolean()
    )
  )

  describe('InterpretedFiltersCard accordion behavior', () => {
    it('should toggle structured output visibility for any filter configuration', () => {
      fc.assert(
        fc.property(
          fc.array(filterItemArb, { minLength: 1, maxLength: 5 }),
          fc.string({ minLength: 10, maxLength: 100 }),
          fc.constantFrom('High', 'Medium', 'Low'),
          structuredOutputArb,
          (filters, summary, confidence, structuredOutput) => {
            const { container, unmount } = render(
              <InterpretedFiltersCard
                filters={filters}
                summary={summary}
                confidence={confidence as 'High' | 'Medium' | 'Low'}
                structuredOutput={structuredOutput}
              />
            )

            // Initially, structured output should be hidden
            const toggleButton = screen.getByLabelText(/structured output/i)
            expect(toggleButton).toBeInTheDocument()
            
            // Check initial state - content should be hidden (opacity-0 or max-h-0)
            const accordionContent = container.querySelector('.overflow-hidden')
            expect(accordionContent).toHaveClass('max-h-0')
            expect(accordionContent).toHaveClass('opacity-0')

            // Click to expand
            fireEvent.click(toggleButton)

            // After click, content should be visible
            expect(accordionContent).toHaveClass('max-h-96')
            expect(accordionContent).toHaveClass('opacity-100')

            // Click again to collapse
            fireEvent.click(toggleButton)

            // Content should be hidden again
            expect(accordionContent).toHaveClass('max-h-0')
            expect(accordionContent).toHaveClass('opacity-0')

            // Clean up after each iteration
            unmount()

            return true
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should maintain proper aria-expanded state for any content', () => {
      fc.assert(
        fc.property(
          fc.array(filterItemArb, { minLength: 1, maxLength: 3 }),
          fc.string({ minLength: 10, maxLength: 50 }),
          fc.constantFrom('High', 'Medium', 'Low'),
          structuredOutputArb,
          (filters, summary, confidence, structuredOutput) => {
            const { unmount } = render(
              <InterpretedFiltersCard
                filters={filters}
                summary={summary}
                confidence={confidence as 'High' | 'Medium' | 'Low'}
                structuredOutput={structuredOutput}
              />
            )

            const toggleButton = screen.getByLabelText(/structured output/i)

            // Initially collapsed
            expect(toggleButton).toHaveAttribute('aria-expanded', 'false')

            // Expand
            fireEvent.click(toggleButton)
            expect(toggleButton).toHaveAttribute('aria-expanded', 'true')

            // Collapse
            fireEvent.click(toggleButton)
            expect(toggleButton).toHaveAttribute('aria-expanded', 'false')

            // Clean up after each iteration
            unmount()

            return true
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  describe('TraceDetailsDrawer behavior', () => {
    it('should properly show and hide drawer for any trace configuration', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 5, maxLength: 20 }),
          (traceId) => {
            // Clean up any previous renders
            cleanup()
            
            const mockOnClose = jest.fn()

            // Test open state first
            const { rerender, unmount } = render(
              <TraceDetailsDrawer
                isOpen={true}
                onClose={mockOnClose}
                traceId={traceId}
              />
            )

            // Drawer should be visible when open
            const dialogs = screen.queryAllByRole('dialog')
            expect(dialogs.length).toBe(1)
            // Use a more flexible matcher that handles whitespace-only strings
            expect(screen.getByText((content, element) => {
              return element?.textContent === `Trace ID: ${traceId}`
            })).toBeInTheDocument()

            // Test closed state
            rerender(
              <TraceDetailsDrawer
                isOpen={false}
                onClose={mockOnClose}
                traceId={traceId}
              />
            )

            // Drawer should not be in the document when closed
            expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

            // Clean up
            unmount()

            return true
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should call onClose when close button is clicked for any trace', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 5, maxLength: 20 }),
          (traceId) => {
            const mockOnClose = jest.fn()

            const { unmount } = render(
              <TraceDetailsDrawer
                isOpen={true}
                onClose={mockOnClose}
                traceId={traceId}
              />
            )

            // Find and click close button using more specific query
            const closeButton = screen.getByLabelText(/close trace details/i)
            fireEvent.click(closeButton)

            // Verify onClose was called
            expect(mockOnClose).toHaveBeenCalledTimes(1)

            // Clean up
            unmount()

            return true
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should call onClose when backdrop is clicked for any trace', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 5, maxLength: 20 }),
          (traceId) => {
            const mockOnClose = jest.fn()

            const { container, unmount } = render(
              <TraceDetailsDrawer
                isOpen={true}
                onClose={mockOnClose}
                traceId={traceId}
              />
            )

            // Find backdrop (first fixed div with bg-black)
            const backdrop = container.querySelector('.fixed.bg-black')
            expect(backdrop).toBeInTheDocument()

            // Click backdrop
            if (backdrop) {
              fireEvent.click(backdrop)
            }

            // Verify onClose was called
            expect(mockOnClose).toHaveBeenCalledTimes(1)

            // Clean up
            unmount()

            return true
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  describe('State management consistency', () => {
    it('should maintain independent state for multiple toggle operations', () => {
      fc.assert(
        fc.property(
          fc.array(filterItemArb, { minLength: 1, maxLength: 3 }),
          fc.string({ minLength: 10, maxLength: 50 }),
          fc.constantFrom('High', 'Medium', 'Low'),
          structuredOutputArb,
          fc.integer({ min: 2, max: 10 }),
          (filters, summary, confidence, structuredOutput, numToggles) => {
            const { container, unmount } = render(
              <InterpretedFiltersCard
                filters={filters}
                summary={summary}
                confidence={confidence as 'High' | 'Medium' | 'Low'}
                structuredOutput={structuredOutput}
              />
            )

            // Use more specific query to get the button
            const toggleButton = screen.getByLabelText(/structured output/i)
            const accordionContent = container.querySelector('.overflow-hidden')

            // Perform multiple toggles
            for (let i = 0; i < numToggles; i++) {
              fireEvent.click(toggleButton)

              // Check state matches expected (odd clicks = open, even clicks = closed)
              const shouldBeOpen = (i + 1) % 2 === 1
              if (shouldBeOpen) {
                expect(accordionContent).toHaveClass('max-h-96')
                expect(accordionContent).toHaveClass('opacity-100')
              } else {
                expect(accordionContent).toHaveClass('max-h-0')
                expect(accordionContent).toHaveClass('opacity-0')
              }
            }

            // Clean up
            unmount()

            return true
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})
