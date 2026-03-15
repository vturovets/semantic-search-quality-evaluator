'use client'

import { ArrowRight } from 'lucide-react'
import { MetricComparison } from '../../lib/types/experiments'
import { MetricCard } from '../ui/metric-card'

interface ExperimentSummaryCardProps {
  metrics: MetricComparison[];
  onNavigateToValidation?: () => void;
}

export function ExperimentSummaryCard({ metrics, onNavigateToValidation }: ExperimentSummaryCardProps) {
  // Extract key improvements for summary display
  const getKeyFindings = () => {
    const findings: Array<{ title: string; value: string; variant: 'success' | 'default' | 'warning' }> = []
    
    metrics.forEach(metric => {
      const isLatencyMetric = metric.metric.toLowerCase().includes('latency')
      const isImprovement = isLatencyMetric 
        ? metric.delta.absolute < 0  // For latency, negative change is good
        : metric.delta.direction === 'positive'  // For other metrics, positive direction is good
      
      if (isImprovement && Math.abs(metric.delta.percentage) > 2) { // Only show meaningful improvements
        const displayValue = metric.unit === '%' || metric.metric.toLowerCase().includes('rate')
          ? `${metric.delta.absolute > 0 ? '+' : ''}${metric.delta.absolute}${metric.unit || ''}`
          : `${metric.delta.absolute > 0 ? '+' : ''}${metric.delta.absolute}${metric.unit ? ` ${metric.unit}` : ''}`
        
        findings.push({
          title: `${metric.metric} ${isLatencyMetric ? 'Reduction' : 'Improvement'}`,
          value: displayValue,
          variant: 'success'
        })
      }
    })
    
    return findings
  }

  const keyFindings = getKeyFindings()
  const hasSignificantImprovements = keyFindings.length > 0

  return (
    <div className="space-y-6">
      {/* Key Metrics Summary */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Experiment Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {keyFindings.slice(0, 3).map((finding, index) => (
            <MetricCard 
              key={index}
              title={finding.title}
              value={finding.value}
              subtitle={finding.title}
              variant={finding.variant}
            />
          ))}
          
          {/* Fill remaining slots if we have fewer than 3 findings */}
          {keyFindings.length < 3 && (
            <MetricCard 
              title="Overall Status"
              value={hasSignificantImprovements ? "Improved" : "Stable"}
              subtitle="Performance Status"
              variant={hasSignificantImprovements ? "success" : "default"}
            />
          )}
        </div>
      </div>

      {/* Navigation to Release Validation */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {hasSignificantImprovements ? "Ready for Statistical Validation" : "Experiment Complete"}
            </h3>
            <p className="text-gray-600 text-sm">
              {hasSignificantImprovements 
                ? "Verify if improvement is statistically significant and safe to release"
                : "Review results and determine next steps for your experiment"
              }
            </p>
          </div>
          <button 
            onClick={onNavigateToValidation || (() => window.location.href = '/release-validation')}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium whitespace-nowrap transition-colors"
          >
            {hasSignificantImprovements ? "Run Statistical Validation" : "View Analysis"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}