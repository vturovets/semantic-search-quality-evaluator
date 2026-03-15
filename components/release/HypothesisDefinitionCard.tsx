'use client'

import { LegacyStatisticalResult } from '../../lib/types/release'

interface HypothesisDefinitionCardProps {
  result: LegacyStatisticalResult
}

export function HypothesisDefinitionCard({ result }: HypothesisDefinitionCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Hypothesis Definition</h3>
      
      <div className="space-y-4">
        <div>
          <div className="text-sm font-medium text-gray-500 mb-1">Null hypothesis</div>
          <div className="text-gray-900">{result.hypothesis.null}</div>
        </div>
        
        <div>
          <div className="text-sm font-medium text-gray-500 mb-1">Alternative hypothesis</div>
          <div className="text-gray-900">{result.hypothesis.alternative}</div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <div className="text-sm font-medium text-gray-500 mb-1">Test type</div>
            <div className="text-gray-900">{result.hypothesis.testType}</div>
          </div>
          
          <div>
            <div className="text-sm font-medium text-gray-500 mb-1">Significance threshold</div>
            <div className="text-gray-900">α = {result.hypothesis.alpha}</div>
          </div>
        </div>
      </div>
    </div>
  )
}