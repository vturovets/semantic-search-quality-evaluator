'use client'

import { useEffect } from 'react'
import { X } from 'lucide-react'
import { TraceStep } from '../../lib/types/search'

interface TraceDetailsDrawerProps {
  isOpen: boolean
  onClose: () => void
  traceId: string
  traceSteps?: TraceStep[]
}

export function TraceDetailsDrawer({ 
  isOpen, 
  onClose, 
  traceId,
  traceSteps = []
}: TraceDetailsDrawerProps) {
  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  // Default trace steps if none provided
  const defaultSteps: TraceStep[] = [
    {
      id: '1',
      step: 'Input received',
      status: 'completed',
      timestamp: new Date().toISOString(),
      details: 'Query processed and validated'
    },
    {
      id: '2',
      step: 'Interpretation completed',
      status: 'completed',
      timestamp: new Date().toISOString(),
      details: 'Natural language converted to structured filters'
    },
    {
      id: '3',
      step: 'Results returned',
      status: 'completed',
      timestamp: new Date().toISOString(),
      details: 'Product results ranked and formatted'
    }
  ]

  const steps = traceSteps.length > 0 ? traceSteps : defaultSteps

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✓'
      case 'processing':
        return '⏳'
      case 'pending':
        return '⏸'
      default:
        return '?'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600'
      case 'processing':
        return 'text-yellow-600'
      case 'pending':
        return 'text-gray-400'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <>
      {/* Backdrop with fade-in animation */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40 transition-opacity duration-300 ease-in-out"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Drawer with slide-in animation */}
      <div 
        className="fixed right-0 top-0 h-full w-full sm:w-96 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out"
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
      >
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 id="drawer-title" className="text-lg font-semibold text-gray-900">Trace Details</h2>
            <p className="text-sm text-gray-600">Trace ID: {traceId}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Close trace details"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto h-[calc(100%-88px)]">
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div 
                key={step.id} 
                className="flex items-start gap-3 animate-fadeIn"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-medium transition-all ${
                  step.status === 'completed' 
                    ? 'border-green-500 bg-green-50 text-green-600'
                    : step.status === 'processing'
                    ? 'border-yellow-500 bg-yellow-50 text-yellow-600'
                    : 'border-gray-300 bg-gray-50 text-gray-400'
                }`}>
                  {index + 1}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900">{step.step}</h4>
                    <span className={`text-sm ${getStatusColor(step.status)}`}>
                      {getStatusIcon(step.status)}
                    </span>
                  </div>
                  
                  {step.details && (
                    <p className="text-xs text-gray-600 mt-1">{step.details}</p>
                  )}
                  
                  {step.timestamp && (
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(step.timestamp).toLocaleTimeString()}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Execution Summary</h4>
            <div className="text-xs text-gray-600 space-y-1">
              <div className="flex justify-between">
                <span>Total steps:</span>
                <span>{steps.length}</span>
              </div>
              <div className="flex justify-between">
                <span>Completed:</span>
                <span>{steps.filter(s => s.status === 'completed').length}</span>
              </div>
              <div className="flex justify-between">
                <span>Status:</span>
                <span className="text-green-600">Success</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}