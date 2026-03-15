import { useState, useRef, useEffect } from 'react'
import { TooltipInfoProps } from '../../lib/types/shared'

export function TooltipInfo({ 
  content, 
  children, 
  position = 'top', 
  trigger = 'hover',
  maxWidth = '200px'
}: TooltipInfoProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [actualPosition, setActualPosition] = useState(position)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLDivElement>(null)

  const positionStyles = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  }

  const arrowStyles = {
    top: 'top-full left-1/2 transform -translate-x-1/2 border-t-gray-900 border-t-8 border-x-transparent border-x-8 border-b-0',
    bottom: 'bottom-full left-1/2 transform -translate-x-1/2 border-b-gray-900 border-b-8 border-x-transparent border-x-8 border-t-0',
    left: 'left-full top-1/2 transform -translate-y-1/2 border-l-gray-900 border-l-8 border-y-transparent border-y-8 border-r-0',
    right: 'right-full top-1/2 transform -translate-y-1/2 border-r-gray-900 border-r-8 border-y-transparent border-y-8 border-l-0'
  }

  // Auto-position tooltip to stay within viewport
  useEffect(() => {
    if (isVisible && tooltipRef.current && triggerRef.current) {
      const tooltip = tooltipRef.current
      const trigger = triggerRef.current
      const rect = trigger.getBoundingClientRect()
      const tooltipRect = tooltip.getBoundingClientRect()
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight
      }

      let newPosition = position

      // Check if tooltip goes outside viewport and adjust position
      if (position === 'top' && rect.top - tooltipRect.height < 0) {
        newPosition = 'bottom'
      } else if (position === 'bottom' && rect.bottom + tooltipRect.height > viewport.height) {
        newPosition = 'top'
      } else if (position === 'left' && rect.left - tooltipRect.width < 0) {
        newPosition = 'right'
      } else if (position === 'right' && rect.right + tooltipRect.width > viewport.width) {
        newPosition = 'left'
      }

      setActualPosition(newPosition)
    }
  }, [isVisible, position])

  const handleShow = () => setIsVisible(true)
  const handleHide = () => setIsVisible(false)
  const handleToggle = () => setIsVisible(!isVisible)

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      if (trigger === 'click') {
        handleToggle()
      } else {
        handleShow()
      }
    }
  }

  const triggerProps = {
    ...(trigger === 'hover' && {
      onMouseEnter: handleShow,
      onMouseLeave: handleHide,
      onFocus: handleShow,
      onBlur: handleHide
    }),
    ...(trigger === 'click' && {
      onClick: handleToggle,
      onKeyDown: handleKeyDown
    }),
    ...(trigger === 'focus' && {
      onFocus: handleShow,
      onBlur: handleHide,
      onKeyDown: handleKeyDown
    })
  }

  // Handle click outside for click trigger
  useEffect(() => {
    if (trigger === 'click' && isVisible) {
      const handleClickOutside = (event: MouseEvent) => {
        if (
          tooltipRef.current && 
          triggerRef.current &&
          !tooltipRef.current.contains(event.target as Node) &&
          !triggerRef.current.contains(event.target as Node)
        ) {
          setIsVisible(false)
        }
      }

      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [trigger, isVisible])

  // Handle escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isVisible) {
        setIsVisible(false)
        // Return focus to trigger element
        triggerRef.current?.focus()
      }
    }

    if (isVisible) {
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [isVisible])

  return (
    <div className="relative inline-block">
      <div
        ref={triggerRef}
        {...triggerProps}
        tabIndex={0}
        role={trigger === 'click' ? 'button' : 'button'}
        aria-describedby={isVisible ? 'tooltip' : undefined}
        aria-expanded={trigger === 'click' ? isVisible : undefined}
        className={`${trigger === 'click' ? 'cursor-pointer' : ''} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-sm`}
        aria-label={typeof content === 'string' ? `Show tooltip: ${content}` : 'Show tooltip'}
      >
        {children}
      </div>
      
      {isVisible && (
        <div 
          ref={tooltipRef}
          id="tooltip"
          role="tooltip"
          className={`absolute z-50 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg shadow-lg ${positionStyles[actualPosition]}`}
          style={{ maxWidth }}
          aria-live="polite"
        >
          {content}
          <div className={`absolute w-0 h-0 ${arrowStyles[actualPosition]}`} />
        </div>
      )}
    </div>
  )
}