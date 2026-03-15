'use client'

import { ProductResultItem } from './ProductResultItem'

interface ProductResult {
  id: string
  name: string
  description: string
  price: string
  tags: string[]
  badge?: string
  image?: string
  isBestMatch?: boolean
}

interface SearchResultsCardProps {
  results: ProductResult[]
  isLoading?: boolean
}

export function SearchResultsCard({ results, isLoading = false }: SearchResultsCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Results</h3>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-3 bg-gray-200 rounded w-full"></div>
                  <div className="flex gap-2">
                    <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                    <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!results || results.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Results</h3>
        <div className="text-center py-8">
          <p className="text-gray-500">No results found. Try a different search query.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 transition-all duration-300 hover:shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Results</h3>
      
      <div className="space-y-4">
        {results.map((result, index) => (
          <div 
            key={result.id}
            className="animate-fadeIn"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <ProductResultItem
              id={result.id}
              name={result.name}
              description={result.description}
              price={result.price}
              tags={result.tags}
              badge={result.badge}
              imageUrl={result.image}
              isBestMatch={result.isBestMatch}
            />
          </div>
        ))}
      </div>
    </div>
  )
}