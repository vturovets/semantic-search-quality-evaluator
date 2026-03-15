'use client'

import { useState } from 'react'
import { BarChart3, TrendingUp, Info } from 'lucide-react'
import { LegacyStatisticalResult } from '../../lib/types/release'

interface StatisticalSummaryCardProps {
  result: LegacyStatisticalResult
}

export function StatisticalSummaryCard({ result }: StatisticalSummaryCardProps) {
  const [showTooltip, setShowTooltip] = useState<string | null>(null)

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 transition-all duration-300 hover:shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <BarChart3 className="w-5 h-5 text-blue-600 transition-transform duration-300 hover:scale-110" />
        Statistical Summary
      </h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="text-center transition-all duration-300 hover:scale-105 animate-fadeIn" style={{ animationDelay: '0ms' }}>
          <div className="text-sm font-medium text-gray-500 mb-1">Metric</div>
          <div className="text-lg font-semibold text-gray-900">{result.metric.name}</div>
        </div>
        
        <div className="text-center transition-all duration-300 hover:scale-105 animate-fadeIn" style={{ animationDelay: '100ms' }}>
          <div className="text-sm font-medium text-gray-500 mb-1">{result.baseline}</div>
          <div className="text-lg font-semibold text-gray-900">{result.metric.baselineValue}</div>
        </div>
        
        <div className="text-center transition-all duration-300 hover:scale-105 animate-fadeIn" style={{ animationDelay: '200ms' }}>
          <div className="text-sm font-medium text-gray-500 mb-1">{result.candidate}</div>
          <div className="text-lg font-semibold text-gray-900">{result.metric.candidateValue}</div>
        </div>
        
        <div className="text-center transition-all duration-300 hover:scale-105 animate-fadeIn" style={{ animationDelay: '300ms' }}>
          <div className="text-sm font-medium text-gray-500 mb-1">Improvement</div>
          <div className="text-lg font-semibold text-green-600 flex items-center justify-center gap-1">
            <TrendingUp className="w-4 h-4 transition-transform duration-300 hover:rotate-12" />
            {result.metric.improvement}
          </div>
        </div>
      </div>
      
      <div className="mt-6 pt-6 border-t border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center transition-all duration-300 hover:scale-105 animate-fadeIn" style={{ animationDelay: '400ms' }}>
            <div className="text-sm font-medium text-gray-500 mb-1 flex items-center justify-center gap-1">
              p-value
              <button
                onMouseEnter={() => setShowTooltip('pvalue')}
                onMouseLeave={() => setShowTooltip(null)}
                className="relative transition-transform duration-200 hover:scale-125"
              >
                <Info className="w-3 h-3 text-gray-400" />
                {showTooltip === 'pvalue' && (
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap z-10 animate-fadeIn">
                    Probability that the difference is due to chance
                  </div>
                )}
              </button>
            </div>
            <div className="text-lg font-semibold text-gray-900">{result.metric.pValue}</div>
          </div>
          
          <div className="text-center transition-all duration-300 hover:scale-105 animate-fadeIn" style={{ animationDelay: '500ms' }}>
            <div className="text-sm font-medium text-gray-500 mb-1">Confidence Level</div>
            <div className="text-lg font-semibold text-gray-900">{result.metric.confidenceLevel}%</div>
          </div>
          
          <div className="text-center transition-all duration-300 hover:scale-105 animate-fadeIn" style={{ animationDelay: '600ms' }}>
            <div className="text-sm font-medium text-gray-500 mb-1">Result</div>
            <div className={`text-lg font-semibold transition-colors duration-300 ${result.metric.isSignificant ? 'text-green-600' : 'text-red-600'}`}>
              {result.metric.isSignificant ? 'Statistically significant' : 'Not statistically significant'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}