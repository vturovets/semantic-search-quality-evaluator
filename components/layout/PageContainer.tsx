import { ReactNode } from 'react'
import { uiConstants } from '../../lib/constants/ui-constants'

interface PageContainerProps {
  children: ReactNode;
  className?: string;
  maxWidth?: 'full' | 'constrained';
}

export function PageContainer({ 
  children, 
  className = '', 
  maxWidth = 'constrained' 
}: PageContainerProps) {
  const containerClass = maxWidth === 'constrained' 
    ? 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8' 
    : 'w-full px-4 sm:px-6 lg:px-8'

  return (
    <main className={`min-h-screen bg-gray-50 ${className}`}>
      <div className={`${containerClass} py-4 sm:py-6 lg:py-8`}>
        {children}
      </div>
    </main>
  )
}