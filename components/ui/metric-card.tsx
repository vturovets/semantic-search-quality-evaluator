import { ReactNode } from 'react'
import { MetricCardProps } from '../../lib/types/shared'

export function MetricCard({ title, value, subtitle, icon, variant = 'default' }: MetricCardProps) {
  const variantStyles = {
    default: 'bg-gray-50 border-gray-200 text-gray-600',
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

  const subtitleStyles = {
    default: 'text-gray-800',
    success: 'text-green-800',
    warning: 'text-yellow-800',
    danger: 'text-red-800'
  }

  return (
    <div className={`text-center p-6 rounded-xl border ${variantStyles[variant]}`}>
      {icon && (
        <div className="flex justify-center mb-2">
          {icon}
        </div>
      )}
      <div className={`text-3xl font-bold mb-2 ${valueStyles[variant]}`}>
        {value}
      </div>
      <div className={`text-sm font-medium ${subtitleStyles[variant]}`}>
        {subtitle}
      </div>
    </div>
  )
}