import { KPIStatCardProps } from '../../lib/types/shared'

export function KPIStatCard({ 
  title, 
  value, 
  unit, 
  trend, 
  icon, 
  variant = 'default' 
}: KPIStatCardProps) {
  const variantStyles = {
    default: 'bg-white border-gray-200 text-gray-600',
    success: 'bg-green-50 border-green-200 text-green-600',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-600',
    danger: 'bg-red-50 border-red-200 text-red-600'
  }

  const valueStyles = {
    default: 'text-gray-900',
    success: 'text-green-600',
    warning: 'text-yellow-600',
    danger: 'text-red-600'
  }

  const trendStyles = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-500'
  }

  const trendIcons = {
    up: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7m0 0H7" />
      </svg>
    ),
    down: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-9.2 9.2M7 7v10m0 0h10" />
      </svg>
    ),
    neutral: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
      </svg>
    )
  }

  return (
    <div className={`p-6 rounded-xl border shadow-sm hover:shadow-md transition-shadow ${variantStyles[variant]}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        {icon && (
          <div className="w-5 h-5 text-gray-400" aria-hidden="true">
            {icon}
          </div>
        )}
      </div>
      
      <div className="flex items-baseline justify-between">
        <div className="flex items-baseline">
          <span className={`text-3xl font-bold ${valueStyles[variant]}`}>
            {value}
          </span>
          {unit && (
            <span className="ml-1 text-sm text-gray-500">
              {unit}
            </span>
          )}
        </div>
        
        {trend && (
          <div className={`flex items-center text-sm font-medium ${trendStyles[trend.direction]}`}>
            {trendIcons[trend.direction]}
            <span className="ml-1">
              {trend.percentage}%
            </span>
            {trend.label && (
              <span className="ml-1 text-xs text-gray-500">
                {trend.label}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}