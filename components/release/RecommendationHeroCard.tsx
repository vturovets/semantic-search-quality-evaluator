'use client'

import { CheckCircle, AlertTriangle, XCircle, Info, Shield } from 'lucide-react'
import { LegacyStatisticalResult } from '../../lib/types/release'

interface RecommendationHeroCardProps {
  result: LegacyStatisticalResult
}

export function RecommendationHeroCard({ result }: RecommendationHeroCardProps) {
  const getRecommendationStyle = (recommendation: string) => {
    switch (recommendation) {
      case 'SAFE TO RELEASE':
        return {
          bg: 'bg-green-50 border-green-200',
          text: 'text-green-800',
          icon: <CheckCircle className="w-8 h-8 text-green-600" />
        }
      case 'KEEP TESTING':
        return {
          bg: 'bg-yellow-50 border-yellow-200',
          text: 'text-yellow-800',
          icon: <AlertTriangle className="w-8 h-8 text-yellow-600" />
        }
      case 'DO NOT RELEASE':
        return {
          bg: 'bg-red-50 border-red-200',
          text: 'text-red-800',
          icon: <XCircle className="w-8 h-8 text-red-600" />
        }
      default:
        return {
          bg: 'bg-gray-50 border-gray-200',
          text: 'text-gray-800',
          icon: <Info className="w-8 h-8 text-gray-600" />
        }
    }
  }

  const recommendationStyle = getRecommendationStyle(result.recommendation)

  return (
    <div className={`rounded-2xl shadow-sm border p-8 transition-all duration-300 hover:shadow-xl hover:scale-[1.02] ${recommendationStyle.bg}`}>
      <div className="text-center">
        <div className="flex justify-center mb-4 animate-bounce-subtle">
          {recommendationStyle.icon}
        </div>
        
        <h3 className="text-sm font-medium text-gray-600 mb-2">Recommendation</h3>
        <div className={`text-3xl font-bold mb-4 transition-all duration-300 ${recommendationStyle.text}`}>
          {result.recommendation}
        </div>
        
        <p className="text-gray-700 mb-4 leading-relaxed">
          Observed improvement is statistically significant at {result.metric.confidenceLevel}% confidence.
        </p>
        
        <div className="flex items-center justify-center gap-2 mb-4 transition-all duration-200 hover:scale-105">
          <Shield className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-600">
            {result.metric.confidenceLevel}% confidence
          </span>
        </div>
        
        <div className="text-sm text-gray-600">
          <strong>Expected impact:</strong> {result.expectedImpact}
        </div>
      </div>
    </div>
  )
}