import { DecisionBadgeProps } from '../../lib/types/shared'

export function DecisionBadge({ decision, size = 'md', variant = 'default' }: DecisionBadgeProps) {
  const decisionStyles = {
    'Safe to release': 'bg-green-100 text-green-800 border-green-200',
    'Needs more evidence': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'Do not release': 'bg-red-100 text-red-800 border-red-200'
  }

  const prominentStyles = {
    'Safe to release': 'bg-green-600 text-white border-green-600',
    'Needs more evidence': 'bg-yellow-600 text-white border-yellow-600',
    'Do not release': 'bg-red-600 text-white border-red-600'
  }

  const sizeStyles = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base'
  }

  const styles = variant === 'prominent' ? prominentStyles : decisionStyles

  return (
    <span 
      className={`inline-flex items-center rounded-full border font-medium ${styles[decision]} ${sizeStyles[size]}`}
      role="status"
      aria-label={`Release decision: ${decision}`}
    >
      {decision}
    </span>
  )
}