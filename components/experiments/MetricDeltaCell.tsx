'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface MetricDeltaCellProps {
  delta: {
    absolute: number;
    percentage: number;
    direction: 'positive' | 'negative' | 'neutral';
  };
  unit?: string;
  metric?: string;
}

export function MetricDeltaCell({ delta, unit, metric }: MetricDeltaCellProps) {
  // For latency, negative absolute values are improvements (lower is better)
  const isLatencyMetric = metric?.toLowerCase().includes('latency')
  const isImprovement = isLatencyMetric 
    ? delta.absolute < 0  // For latency, negative change is good
    : delta.direction === 'positive'  // For other metrics, positive direction is good
  
  const getDisplayValue = () => {
    if (unit === '%' || metric?.toLowerCase().includes('rate')) {
      return `${delta.absolute > 0 ? '+' : ''}${delta.absolute}${unit || ''}`
    }
    return `${delta.absolute > 0 ? '+' : ''}${delta.absolute}${unit ? ` ${unit}` : ''}`
  }

  const getIcon = () => {
    if (delta.direction === 'neutral' || delta.absolute === 0) {
      return <Minus className="w-4 h-4" />
    }
    return isImprovement ? (
      <TrendingUp className="w-4 h-4" />
    ) : (
      <TrendingDown className="w-4 h-4" />
    )
  }

  const getColorClass = () => {
    if (delta.direction === 'neutral' || delta.absolute === 0) {
      return 'text-gray-600'
    }
    return isImprovement ? 'text-green-600' : 'text-red-600'
  }

  return (
    <span className={`inline-flex items-center gap-1 font-semibold transition-all duration-300 hover:scale-110 ${getColorClass()}`}>
      <span className="transition-transform duration-300 hover:rotate-12">
        {getIcon()}
      </span>
      {getDisplayValue()}
    </span>
  )
}