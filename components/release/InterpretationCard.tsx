'use client'

import { AlertTriangle } from 'lucide-react'
import { LegacyStatisticalResult } from '../../lib/types/release'

interface InterpretationCardProps {
  result: LegacyStatisticalResult
}

export function InterpretationCard({ result }: InterpretationCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Interpretation</h3>
      
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Statistical Evidence</h4>
          <p className="text-sm text-gray-700">{result.interpretation.summary}</p>
        </div>
        
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Business Implication</h4>
          <p className="text-sm text-gray-700">{result.interpretation.businessImplication}</p>
        </div>
        
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="text-sm font-semibold text-yellow-800 mb-1 flex items-center gap-1">
            <AlertTriangle className="w-4 h-4" />
            Risk Note
          </h4>
          <p className="text-sm text-yellow-700">{result.interpretation.riskNote}</p>
        </div>
      </div>
    </div>
  )
}