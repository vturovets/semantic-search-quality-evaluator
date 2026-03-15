'use client'

import { CheckCircle, BarChart3, Shield } from 'lucide-react'

export function DecisionTimelineStrip() {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Decision Process</h3>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-4 h-4 text-blue-600" />
          </div>
          <span className="font-medium text-gray-900">Experiment completed</span>
        </div>
        
        <div className="hidden md:block w-16 h-px bg-gray-300"></div>
        
        <div className="flex items-center gap-2 text-sm">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <BarChart3 className="w-4 h-4 text-blue-600" />
          </div>
          <span className="font-medium text-gray-900">Metrics compared</span>
        </div>
        
        <div className="hidden md:block w-16 h-px bg-gray-300"></div>
        
        <div className="flex items-center gap-2 text-sm">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-4 h-4 text-green-600" />
          </div>
          <span className="font-medium text-gray-900">Hypothesis test passed</span>
        </div>
        
        <div className="hidden md:block w-16 h-px bg-gray-300"></div>
        
        <div className="flex items-center gap-2 text-sm">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <Shield className="w-4 h-4 text-green-600" />
          </div>
          <span className="font-medium text-gray-900">Release recommendation generated</span>
        </div>
      </div>
    </div>
  )
}