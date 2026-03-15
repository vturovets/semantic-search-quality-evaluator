'use client'

import { useState } from 'react'
import { Search, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { AppHeader } from '../../components/layout/AppHeader'
import { PageContainer } from '../../components/layout/PageContainer'
import { PageHero } from '../../components/layout/PageHero'
import { ProductResultSkeleton } from '../../components/ui/loading-shimmer'
import { searchScenarios, defaultSearchQuery } from '../../lib/mock-data'
import { LegacySearchScenario } from '../../lib/types/search'

// Use the search scenarios directly since they're already in the correct format
const mockScenarios = searchScenarios;

export default function SearchPage() {
  const [currentQuery, setCurrentQuery] = useState(defaultSearchQuery)
  const [isLoading, setIsLoading] = useState(false)
  const [showStructuredOutput, setShowStructuredOutput] = useState(false)
  const [showTraceDetails, setShowTraceDetails] = useState(false)

  const currentScenario = mockScenarios[currentQuery]

  const handleSearch = async () => {
    setIsLoading(true)
    // Simulate realistic API call delay between 700-1200ms
    const delay = Math.random() * 500 + 700
    await new Promise(resolve => setTimeout(resolve, delay))
    setIsLoading(false)
  }

  const handleSamplePromptClick = async (prompt: string) => {
    setCurrentQuery(prompt)
    // Automatically trigger search when sample prompt is clicked
    setIsLoading(true)
    const delay = Math.random() * 500 + 700
    await new Promise(resolve => setTimeout(resolve, delay))
    setIsLoading(false)
  }

  const heroProps = {
    title: "AI Product Search",
    subtitle: "Search using natural language and see how AI interprets intent, returns results, and exposes execution evidence.",
    badges: [
      { label: "Natural Language Search", variant: "blue" as const },
      { label: "Interpreted Filters", variant: "green" as const },
      { label: "Observable Execution", variant: "purple" as const }
    ]
  }

  return (
    <>
      <AppHeader />
      <PageContainer>
        <PageHero {...heroProps} />

        {/* Main Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 lg:gap-8">
          {/* Left Column - Search and Results */}
          <div className="xl:col-span-7 space-y-4 sm:space-y-6">
            {/* Search Panel */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Search using natural language</h3>
              
              <div className="flex flex-col sm:flex-row gap-3 mb-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" aria-hidden="true" />
                  <input
                    type="text"
                    value={currentQuery}
                    onChange={(e) => setCurrentQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base min-h-[44px]"
                    placeholder="Find cheap winter running shoes"
                    aria-label="Search query input"
                  />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={isLoading}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 font-medium min-w-[120px] min-h-[44px] focus:outline-none"
                  aria-label={isLoading ? 'Searching...' : 'Run search'}
                >
                  {isLoading ? 'Searching...' : 'Run Search'}
                </button>
              </div>

              {/* Sample Prompts */}
              <div className="flex flex-wrap gap-2">
                {Object.keys(mockScenarios).map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => handleSamplePromptClick(prompt)}
                    className={`px-3 py-2 rounded-full text-sm font-medium transition-colors min-h-[36px] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                      currentQuery === prompt
                        ? 'bg-blue-100 text-blue-800 border border-blue-200'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                    aria-label={`Use sample prompt: ${prompt}`}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            {/* Results Panel */}
            {isLoading ? (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Results</h3>
                <div className="space-y-3 sm:space-y-4">
                  <ProductResultSkeleton />
                  <ProductResultSkeleton />
                  <ProductResultSkeleton />
                </div>
              </div>
            ) : currentScenario && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Results</h3>
                
                <div className="space-y-3 sm:space-y-4">
                  {currentScenario.results.map((result) => (
                    <div
                      key={result.id}
                      className={`p-3 sm:p-4 rounded-xl border transition-all hover:shadow-md group cursor-pointer ${
                        result.badge ? 'border-blue-200 bg-blue-50/30' : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row items-start gap-3 sm:gap-4">
                        <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0 flex items-center justify-center">
                          <span className="text-gray-500 text-xs">IMG</span>
                        </div>
                        
                        <div className="flex-1 min-w-0 w-full">
                          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                                {result.name}
                              </h4>
                              {result.badge && (
                                <span className="inline-block px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded-full mt-1">
                                  {result.badge}
                                </span>
                              )}
                            </div>
                            <span className="text-lg font-bold text-gray-900 flex-shrink-0">{result.price}</span>
                          </div>
                          
                          <p className="text-gray-600 text-sm mt-1 mb-3">{result.description}</p>
                          
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div className="flex flex-wrap gap-1">
                              {result.tags.map((tag) => (
                                <span
                                  key={tag}
                                  className="inline-block px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-700 rounded-full"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                            
                            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-sm min-h-[32px] self-start sm:self-auto">
                              View Product
                              <ExternalLink className="w-3 h-3" aria-hidden="true" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Interpretation and Metrics */}
          <div className="xl:col-span-5 space-y-4 sm:space-y-6">
            {/* Interpretation Panel */}
            {isLoading ? (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Interpreted filters</h3>
                <div className="space-y-4 animate-pulse">
                  <div className="flex flex-wrap gap-2">
                    <div className="h-10 bg-gray-200 rounded-lg w-32"></div>
                    <div className="h-10 bg-gray-200 rounded-lg w-28"></div>
                    <div className="h-10 bg-gray-200 rounded-lg w-36"></div>
                  </div>
                  <div className="pt-2 border-t border-gray-100">
                    <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                  </div>
                </div>
              </div>
            ) : currentScenario && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Interpreted filters</h3>
                
                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    {currentScenario.interpretation.filters.map((filter, index) => (
                      <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
                        <span className="text-sm font-medium text-blue-900">{filter.label}:</span>
                        <span className="text-sm text-blue-700 ml-1">{filter.value}</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="pt-2 border-t border-gray-100">
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">AI interpretation summary:</span>
                    </p>
                    <p className="text-sm text-gray-800">{currentScenario.interpretation.summary}</p>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-2 gap-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">Interpretation confidence:</span>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        currentScenario.interpretation.confidence === 'High' 
                          ? 'bg-green-100 text-green-800'
                          : currentScenario.interpretation.confidence === 'Medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {currentScenario.interpretation.confidence}
                      </span>
                    </div>
                    
                    <button
                      onClick={() => setShowStructuredOutput(!showStructuredOutput)}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-sm min-h-[32px] transition-colors"
                      aria-expanded={showStructuredOutput}
                      aria-label={showStructuredOutput ? 'Hide structured output' : 'Show structured output'}
                    >
                      View structured output
                      {showStructuredOutput ? <ChevronUp className="w-4 h-4" aria-hidden="true" /> : <ChevronDown className="w-4 h-4" aria-hidden="true" />}
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
                        {JSON.stringify(currentScenario.interpretation.structuredOutput, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Execution Metrics Panel */}
            {isLoading ? (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Execution metrics</h3>
                <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-4 animate-pulse">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="h-8 bg-gray-200 rounded w-20 mx-auto mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-16 mx-auto"></div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="h-8 bg-gray-200 rounded w-20 mx-auto mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-16 mx-auto"></div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="h-8 bg-gray-200 rounded w-20 mx-auto mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-16 mx-auto"></div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="h-8 bg-gray-200 rounded w-20 mx-auto mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-16 mx-auto"></div>
                  </div>
                </div>
              </div>
            ) : currentScenario && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Execution metrics</h3>
                
                <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-xl sm:text-2xl font-bold text-gray-900">{currentScenario.metrics.latencyMs} ms</div>
                    <div className="text-xs sm:text-sm text-gray-600">Latency</div>
                  </div>
                  
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-xl sm:text-2xl font-bold text-gray-900">{currentScenario.metrics.tokens}</div>
                    <div className="text-xs sm:text-sm text-gray-600">LLM tokens</div>
                  </div>
                  
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-xl sm:text-2xl font-bold text-gray-900">{currentScenario.metrics.traceId}</div>
                    <div className="text-xs sm:text-sm text-gray-600">Trace ID</div>
                  </div>
                  
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-xl sm:text-2xl font-bold text-green-600">{currentScenario.metrics.status}</div>
                    <div className="text-xs sm:text-sm text-gray-600">Search status</div>
                  </div>
                </div>
                
                <p className="text-xs text-gray-500 mb-3">
                  This view exposes lightweight runtime evidence for AI-driven search execution.
                </p>
                
                <button
                  onClick={() => setShowTraceDetails(!showTraceDetails)}
                  className="w-full text-blue-600 hover:text-blue-700 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-sm min-h-[44px] py-2 transition-colors"
                  aria-expanded={showTraceDetails}
                  aria-label={showTraceDetails ? 'Hide trace details' : 'Show trace details'}
                >
                  {showTraceDetails ? 'Hide trace details' : 'Open trace details'}
                </button>
                
                {/* Accordion with smooth animation */}
                <div 
                  className={`overflow-hidden transition-all duration-300 ease-in-out ${
                    showTraceDetails ? 'max-h-48 opacity-100' : 'max-h-0 opacity-0'
                  }`}
                >
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Input received:</span>
                        <span className="text-gray-900">✓</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Interpretation completed:</span>
                        <span className="text-gray-900">✓</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Results returned:</span>
                        <span className="text-gray-900">✓</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer CTA */}
        <div className="mt-8 sm:mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-4 sm:p-6 border border-blue-100">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex-1">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-1">
                Next: Evaluate prompt versions and compare outcomes
              </h3>
              <p className="text-gray-600 text-sm">
                Move to the experiment dashboard to see how different AI approaches perform
              </p>
            </div>
            <button 
              onClick={() => window.location.href = '/experiments'}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium whitespace-nowrap min-h-[44px] focus:outline-none w-full sm:w-auto"
              aria-label="Navigate to experiment dashboard"
            >
              Go to Experiment Dashboard
            </button>
          </div>
        </div>
      </PageContainer>
    </>
  )
}