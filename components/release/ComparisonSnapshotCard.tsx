'use client'

import { MetricComparison } from '../../lib/types/release'

interface ComparisonSnapshotCardProps {
  comparisonSnapshot: MetricComparison[]
}

export function ComparisonSnapshotCard({ comparisonSnapshot }: ComparisonSnapshotCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Experiment Results Summary</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 font-semibold text-gray-900">Metric</th>
              <th className="text-center py-2 font-semibold text-gray-900">Baseline</th>
              <th className="text-center py-2 font-semibold text-gray-900">Candidate</th>
            </tr>
          </thead>
          <tbody>
            {comparisonSnapshot.map((row, index) => (
              <tr key={index} className="border-b border-gray-100">
                <td className="py-3 font-medium text-gray-900">{row.metric}</td>
                <td className="py-3 text-center text-gray-700">{row.baseline}</td>
                <td className="py-3 text-center text-gray-700">{row.candidate}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}