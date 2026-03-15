'use client'

import { useState } from 'react'
import { Download, Plus, TrendingUp, TrendingDown, CheckCircle } from 'lucide-react'
import { AppHeader } from '../../components/layout/AppHeader'
import { PageContainer } from '../../components/layout/PageContainer'
import { PageHero } from '../../components/layout/PageHero'
import { MetricCard } from '../../components/ui/metric-card'
import { ProgressBar } from '../../components/ui/progress-bar'
import { StatusBadge } from '../../components/ui/status-badge'
import { experimentData } from '../../lib/mock-data'

export default function ExperimentDashboard() {
  const [experiment] = useState(experimentData)

  const heroProps = {
    title: "AI Experiment Dashboard",
    subtitle: "Evaluate AI feature performance using controlled experiments"
  }

  return (
    <>
      <AppHeader />
      <PageContainer>
        <div className="flex justify-between items-start mb-8">
          <PageHero {...heroProps} />
          
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-gray-700">
              <Download className="w-4 h-4" />
              Export Results
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
              <Plus className="w-4 h-4" />
              New Experiment
            </button>
          </div>
        </div>

        {/* Experiment Info Panel */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900">
              Experiment: {experiment.name}
            </h3>
            <StatusBadge status={experiment.status} icon={<CheckCircle className="w-5 h-5 text-blue-600" />} />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="space-y-1">
              <dt className="text-sm font-medium text-gray-500">Dataset</dt>
              <dd className="text-sm text-gray-900">{experiment.dataset}</dd>
            </div>
            <div className="space-y-1">
              <dt className="text-sm font-medium text-gray-500">Dataset size</dt>
              <dd className="text-sm text-gray-900">{experiment.datasetSize} queries</dd>
            </div>
            <div className="space-y-1">
              <dt className="text-sm font-medium text-gray-500">Baseline model</dt>
              <dd className="text-sm text-gray-900">{experiment.baseline}</dd>
            </div>
            <div className="space-y-1">
              <dt className="text-sm font-medium text-gray-500">Candidate model</dt>
              <dd className="text-sm text-gray-900">{experiment.candidate}</dd>
            </div>
            <div className="space-y-1">
              <dt className="text-sm font-medium text-gray-500">Experiment run</dt>
              <dd className="text-sm text-gray-900">{experiment.experimentRun}</dd>
            </div>
            <div className="space-y-1">
              <dt className="text-sm font-medium text-gray-500">Data source</dt>
              <dd className="text-sm text-gray-900">{experiment.dataSource}</dd>
            </div>
          </div>
        </div>

        {/* Results Comparison Table */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Results Comparison</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Metric</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-900">Prompt v1 (Baseline)</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-900">Prompt v2 (Candidate)</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-900">Difference</th>
                </tr>
              </thead>
              <tbody>
                {experiment.metrics.map((metric, index) => (
                  <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4 font-medium text-gray-900">{metric.metric}</td>
                    <td className="py-4 px-4 text-center text-gray-700">{metric.v1}</td>
                    <td className="py-4 px-4 text-center text-gray-700">{metric.v2}</td>
                    <td className="py-4 px-4 text-center">
                      <span className={`inline-flex items-center gap-1 font-semibold ${
                        metric.improvement ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {metric.improvement ? (
                          <TrendingUp className="w-4 h-4" />
                        ) : (
                          <TrendingDown className="w-4 h-4" />
                        )}
                        {metric.diff}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Visualization Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Accuracy Comparison Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Accuracy Comparison</h4>
          <div className="space-y-4">
            <ProgressBar 
              label="Prompt v1" 
              value="82%" 
              percentage={82} 
              color="blue" 
            />
            <ProgressBar 
              label="Prompt v2" 
              value="88%" 
              percentage={88} 
              color="green" 
            />
          </div>
          </div>

          {/* Latency Comparison Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Latency Comparison</h4>
          <div className="space-y-4">
            <ProgressBar 
              label="Prompt v1" 
              value="780ms" 
              percentage={78} 
              color="red" 
            />
            <ProgressBar 
              label="Prompt v2" 
              value="710ms" 
              percentage={71} 
              color="green" 
            />
          </div>
          </div>
        </div>

        {/* Improvement Summary Panel */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Experiment Summary</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard 
              title="Accuracy Improvement"
              value="+6%"
              subtitle="Accuracy Improvement"
              variant="success"
            />
            <MetricCard 
              title="Latency Reduction"
              value="-70 ms"
              subtitle="Latency Reduction"
              variant="default"
            />
            <MetricCard 
              title="Consistency Improvement"
              value="+4%"
              subtitle="Consistency Improvement"
              variant="success"
            />
          </div>
        </div>

        {/* Decision Navigation */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Ready for Statistical Validation
              </h3>
              <p className="text-gray-600 text-sm">
                Verify if improvement is statistically significant and safe to release
              </p>
            </div>
            <button 
              onClick={() => window.location.href = '/release-validation'}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium whitespace-nowrap"
            >
              Run Statistical Validation
            </button>
          </div>
        </div>
      </PageContainer>
    </>
  )
}