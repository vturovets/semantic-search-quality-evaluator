import { ReactNode, useState } from 'react'
import { TooltipProps } from '../../lib/types/shared'

export function Tooltip({ content, children, position = 'top' }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)

  const positionStyles = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  }

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      
      {isVisible && (
        <div className={`absolute z-50 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap ${positionStyles[position]}`}>
          {content}
          <div className="absolute w-2 h-2 bg-gray-900 transform rotate-45 -translate-x-1/2 left-1/2 top-full -mt-1"></div>
        </div>
      )}
    </div>
  )
}