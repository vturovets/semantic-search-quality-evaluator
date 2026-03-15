'use client'

import { TraceStep } from '../../lib/types/search'

interface ExecutionMetrics {
  latencyMs?: number
  latency?: number
  tokens: number
  traceId: string
  status: string
}

interface ExecutionMetricsCardProps {
  metrics: ExecutionMetrics
  onOpenTraceDetails: () => void
  traceSteps?: TraceStep[]
}

export function ExecutionMetricsCard({ 
  metrics, 
  onOpenTraceDetails,
  traceSteps 
}: ExecutionMetricsCardProps) {
  // Handle both latencyMs and latency properties for backward compatibility
  const latency = metrics.latencyMs || metrics.latency || 0

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'text-green-600'
      case 'processing':
        return 'text-yellow-600'
      case 'failed':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 transition-all duration-300 hover:shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Execution metrics</h3>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg transition-all duration-300 hover:bg-gray-100 hover:shadow-sm hover:scale-105 animate-fadeIn" style={{ animationDelay: '0ms' }}>
          <div className="text-2xl font-bold text-gray-900 transition-colors">{latency} ms</div>
          <div className="text-sm text-gray-600">Latency</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 rounded-lg transition-all duration-300 hover:bg-gray-100 hover:shadow-sm hover:scale-105 animate-fadeIn" style={{ animationDelay: '100ms' }}>
          <div className="text-2xl font-bold text-gray-900 transition-colors">{metrics.tokens}</div>
          <div className="text-sm text-gray-600">LLM tokens</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 rounded-lg transition-all duration-300 hover:bg-gray-100 hover:shadow-sm hover:scale-105 animate-fadeIn" style={{ animationDelay: '200ms' }}>
          <div className="text-2xl font-bold text-gray-900 transition-colors">{metrics.traceId}</div>
          <div className="text-sm text-gray-600">Trace ID</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 rounded-lg transition-all duration-300 hover:bg-gray-100 hover:shadow-sm hover:scale-105 animate-fadeIn" style={{ animationDelay: '300ms' }}>
          <div className={`text-2xl font-bold transition-all duration-300 ${getStatusColor(metrics.status)}`}>
            {metrics.status}
          </div>
          <div className="text-sm text-gray-600">Search status</div>
        </div>
      </div>
      
      <p className="text-xs text-gray-500 mb-3 animate-fadeIn" style={{ animationDelay: '400ms' }}>
        This view exposes lightweight runtime evidence for AI-driven search execution.
      </p>
      
      <button
        onClick={onOpenTraceDetails}
        className="w-full text-blue-600 hover:text-blue-700 text-sm font-medium transition-all duration-300 hover:bg-blue-50 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 min-h-[44px]"
      >
        Open trace details
      </button>
    </div>
  )
}