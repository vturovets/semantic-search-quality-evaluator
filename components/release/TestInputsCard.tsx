'use client'

import { LegacyStatisticalResult } from '../../lib/types/release'

interface TestInputsCardProps {
  result: LegacyStatisticalResult
}

export function TestInputsCard({ result }: TestInputsCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Test Inputs</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <div className="text-sm font-medium text-gray-500 mb-1">Dataset size</div>
          <div className="text-gray-900">{result.testInputs.datasetSize} queries</div>
        </div>
        
        <div>
          <div className="text-sm font-medium text-gray-500 mb-1">Method</div>
          <div className="text-gray-900">{result.testInputs.method}</div>
        </div>
      </div>
      
      <div className="mt-4">
        <div className="text-sm font-medium text-gray-500 mb-2">Evidence sources</div>
        <div className="flex flex-wrap gap-2">
          {result.testInputs.sources.map((source: string) => (
            <span
              key={source}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
            >
              {source}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}