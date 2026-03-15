'use client'

import { CheckCircle } from 'lucide-react'
import { StatusBadge } from '../ui/status-badge'
import { ExperimentSummary } from '../../lib/types/experiments'

interface ExperimentInfoCardProps {
  experiment: ExperimentSummary;
}

export function ExperimentInfoCard({ experiment }: ExperimentInfoCardProps) {
  // Convert status to uppercase for StatusBadge compatibility
  const statusForBadge = experiment.status.toUpperCase() as 'COMPLETED' | 'RUNNING' | 'FAILED'

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 transition-all duration-300 hover:shadow-md">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900 transition-colors">
          Experiment: {experiment.name}
        </h3>
        <StatusBadge 
          status={statusForBadge} 
          icon={<CheckCircle className="w-5 h-5 text-blue-600" />} 
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-1 group">
          <dt className="text-sm font-medium text-gray-500 transition-colors group-hover:text-gray-700">Dataset</dt>
          <dd className="text-sm text-gray-900 font-medium">{experiment.dataset.name}</dd>
        </div>
        <div className="space-y-1 group">
          <dt className="text-sm font-medium text-gray-500 transition-colors group-hover:text-gray-700">Dataset size</dt>
          <dd className="text-sm text-gray-900 font-medium">{experiment.dataset.size} queries</dd>
        </div>
        <div className="space-y-1 group">
          <dt className="text-sm font-medium text-gray-500 transition-colors group-hover:text-gray-700">Baseline model</dt>
          <dd className="text-sm text-gray-900 font-medium">{experiment.models.baseline.name} ({experiment.models.baseline.version})</dd>
        </div>
        <div className="space-y-1 group">
          <dt className="text-sm font-medium text-gray-500 transition-colors group-hover:text-gray-700">Candidate model</dt>
          <dd className="text-sm text-gray-900 font-medium">{experiment.models.candidate.name} ({experiment.models.candidate.version})</dd>
        </div>
        <div className="space-y-1 group">
          <dt className="text-sm font-medium text-gray-500 transition-colors group-hover:text-gray-700">Experiment run</dt>
          <dd className="text-sm text-gray-900 font-medium">{experiment.runDate}</dd>
        </div>
        <div className="space-y-1 group">
          <dt className="text-sm font-medium text-gray-500 transition-colors group-hover:text-gray-700">Data source</dt>
          <dd className="text-sm text-gray-900 font-medium">{experiment.dataset.source}</dd>
        </div>
      </div>
      
      {experiment.description && (
        <div className="mt-6 pt-6 border-t border-gray-200 animate-fadeIn">
          <dt className="text-sm font-medium text-gray-500 mb-2">Description</dt>
          <dd className="text-sm text-gray-700 leading-relaxed">{experiment.description}</dd>
        </div>
      )}
    </div>
  )
}