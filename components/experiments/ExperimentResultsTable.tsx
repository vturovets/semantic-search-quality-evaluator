'use client'

import { MetricComparison } from '../../lib/types/experiments'
import { MetricDeltaCell } from './MetricDeltaCell'

interface ExperimentResultsTableProps {
  metrics: MetricComparison[];
  baselineLabel?: string;
  candidateLabel?: string;
}

export function ExperimentResultsTable({ 
  metrics, 
  baselineLabel = "Baseline",
  candidateLabel = "Candidate" 
}: ExperimentResultsTableProps) {
  const formatValue = (value: number, unit?: string) => {
    if (unit === '%') {
      return `${value}%`
    }
    if (unit === 'ms') {
      return `${value} ms`
    }
    return `${value}${unit ? ` ${unit}` : ''}`
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 transition-all duration-300 hover:shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Results Comparison</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-900">Metric</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-900">{baselineLabel}</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-900">{candidateLabel}</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-900">Difference</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric, index) => (
              <tr 
                key={index} 
                className="border-b border-gray-100 hover:bg-gray-50 transition-all duration-200 hover:shadow-sm"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <td className="py-4 px-4 font-medium text-gray-900 transition-colors hover:text-blue-600">{metric.metric}</td>
                <td className="py-4 px-4 text-center text-gray-700 transition-all hover:font-semibold">
                  {formatValue(metric.baseline.value, metric.baseline.unit)}
                </td>
                <td className="py-4 px-4 text-center text-gray-700 transition-all hover:font-semibold">
                  {formatValue(metric.candidate.value, metric.candidate.unit)}
                </td>
                <td className="py-4 px-4 text-center">
                  <MetricDeltaCell 
                    delta={metric.delta} 
                    unit={metric.unit}
                    metric={metric.metric}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}