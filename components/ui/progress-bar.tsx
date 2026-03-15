import { ProgressBarProps } from '../../lib/types/shared'

export function ProgressBar({ label, value, percentage, color = 'blue' }: ProgressBarProps) {
  const colorStyles = {
    blue: 'bg-blue-500',
    green: 'bg-green-500', 
    red: 'bg-red-400',
    yellow: 'bg-yellow-500'
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-semibold text-gray-900">{value}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div 
          className={`h-3 rounded-full ${colorStyles[color]}`} 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  )
}