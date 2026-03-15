import { StatusBadgeProps } from '../../lib/types/shared'

export function StatusBadge({ status, icon, size = 'md' }: StatusBadgeProps) {
  const statusStyles = {
    COMPLETED: 'bg-green-100 text-green-800 border-green-200',
    RUNNING: 'bg-yellow-100 text-yellow-800 border-yellow-200', 
    FAILED: 'bg-red-100 text-red-800 border-red-200',
    PENDING: 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const sizeStyles = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base'
  }

  const iconSizeStyles = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  }

  return (
    <div className="flex items-center gap-2">
      {icon && (
        <div className={`flex-shrink-0 ${iconSizeStyles[size]}`} aria-hidden="true">
          {icon}
        </div>
      )}
      <span 
        className={`inline-flex items-center rounded-full border font-medium ${statusStyles[status]} ${sizeStyles[size]}`}
        role="status"
        aria-label={`Status: ${status.toLowerCase()}`}
      >
        {status}
      </span>
    </div>
  )
}