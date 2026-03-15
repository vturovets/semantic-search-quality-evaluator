'use client'

import { ExternalLink } from 'lucide-react'

interface ProductResultItemProps {
  id: string
  name: string
  description: string
  price: string
  tags: string[]
  badge?: string
  imageUrl?: string
  isBestMatch?: boolean
}

export function ProductResultItem({
  id,
  name,
  description,
  price,
  tags,
  badge,
  imageUrl,
  isBestMatch
}: ProductResultItemProps) {
  return (
    <div
      className={`p-4 rounded-xl border transition-all hover:shadow-md group cursor-pointer ${
        badge || isBestMatch ? 'border-blue-200 bg-blue-50/30' : 'border-gray-200 hover:border-gray-300'
      }`}
    >
      <div className="flex items-start gap-4">
        <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0 flex items-center justify-center">
          {imageUrl ? (
            <img 
              src={imageUrl} 
              alt={name}
              className="w-full h-full object-cover rounded-lg"
            />
          ) : (
            <span className="text-gray-500 text-xs">IMG</span>
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                {name}
              </h4>
              {(badge || isBestMatch) && (
                <span className="inline-block px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded-full mt-1">
                  {badge || 'Best match'}
                </span>
              )}
            </div>
            <span className="text-lg font-bold text-gray-900">{price}</span>
          </div>
          
          <p className="text-gray-600 text-sm mt-1 mb-3">{description}</p>
          
          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-1">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-block px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-700 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
            
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              View Product
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}