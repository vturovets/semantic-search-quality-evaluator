'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { FilterItem } from '../../lib/types/search'

interface InterpretedFiltersCardProps {
  filters: FilterItem[]
  summary: string
  confidence: 'High' | 'Medium' | 'Low'
  structuredOutput: Record<string, any>
}

export function InterpretedFiltersCard({
  filters,
  summary,
  confidence,
  structuredOutput
}: InterpretedFiltersCardProps) {
  const [showStructuredOutput, setShowStructuredOutput] = useState(false)

  const getConfidenceStyle = (confidence: string) => {
    switch (confidence) {
      case 'High':
        return 'bg-green-100 text-green-800'
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'Low':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 transition-all duration-300 hover:shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Interpreted filters</h3>
      
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {filters.map((filter, index) => (
            <div 
              key={index} 
              className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 transition-all duration-200 hover:shadow-sm hover:bg-blue-100 hover:border-blue-300 transform hover:scale-105"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <span className="text-sm font-medium text-blue-900">{filter.label}:</span>
              <span className="text-sm text-blue-700 ml-1">{filter.value}</span>
            </div>
          ))}
        </div>
        
        <div className="pt-2 border-t border-gray-100">
          <p className="text-sm text-gray-600 mb-2">
            <span className="font-medium">AI interpretation summary:</span>
          </p>
          <p className="text-sm text-gray-800">{summary}</p>
        </div>
        
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Interpretation confidence:</span>
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getConfidenceStyle(confidence)}`}>
              {confidence}
            </span>
          </div>
          
          <button
            onClick={() => setShowStructuredOutput(!showStructuredOutput)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-sm min-h-[32px]"
            aria-expanded={showStructuredOutput}
            aria-label={showStructuredOutput ? 'Hide structured output' : 'Show structured output'}
          >
            View structured output
            {showStructuredOutput ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
        
        {/* Accordion with smooth animation */}
        <div 
          className={`overflow-hidden transition-all duration-300 ease-in-out ${
            showStructuredOutput ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
          }`}
        >
          <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <pre className="text-xs text-gray-700 overflow-x-auto">
              {JSON.stringify(structuredOutput, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}