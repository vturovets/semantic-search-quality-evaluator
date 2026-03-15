'use client'

import { useState } from 'react'
import { Search, Loader2 } from 'lucide-react'

interface SearchBarCardProps {
  query: string
  onQueryChange: (query: string) => void
  onSearch: () => void
  isLoading: boolean
  samplePrompts: string[]
  onSamplePromptClick: (prompt: string) => void
}

export function SearchBarCard({
  query,
  onQueryChange,
  onSearch,
  isLoading,
  samplePrompts,
  onSamplePromptClick
}: SearchBarCardProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading) {
      onSearch()
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
      <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Search using natural language</h3>
      
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="flex-1 relative">
          <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 transition-colors ${
            isLoading ? 'text-blue-500' : 'text-gray-400'
          }`} aria-hidden="true" />
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-base min-h-[44px] ${
              isLoading 
                ? 'border-blue-300 bg-blue-50/30 cursor-not-allowed' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            placeholder="Find cheap winter running shoes"
            aria-label="Search query input"
          />
        </div>
        <button
          onClick={onSearch}
          disabled={isLoading}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium min-w-[120px] min-h-[44px] transition-all focus:outline-none flex items-center justify-center gap-2"
          aria-label={isLoading ? 'Searching...' : 'Run search'}
        >
          {isLoading && <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />}
          {isLoading ? 'Searching...' : 'Run Search'}
        </button>
      </div>

      {/* Sample Prompts */}
      <div className="flex flex-wrap gap-2">
        {samplePrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => onSamplePromptClick(prompt)}
            disabled={isLoading}
            className={`px-3 py-2 rounded-full text-sm font-medium transition-all min-h-[36px] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
              query === prompt
                ? 'bg-blue-100 text-blue-800 border border-blue-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm'
            }`}
            aria-label={`Use sample prompt: ${prompt}`}
          >
            {prompt}
          </button>
        ))}
      </div>
      
      {/* Loading indicator */}
      {isLoading && (
        <div className="mt-4 flex items-center gap-2 text-sm text-blue-600">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span>Processing your query...</span>
        </div>
      )}
    </div>
  )
}