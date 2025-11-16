'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { clinicalTrialsApi } from '@/lib/api'
import { ChartLineIcon, BeakerIcon, ClockIcon, UserGroupIcon } from '@heroicons/react/24/outline'

export default function TrialDesignPage() {
  const [trialType, setTrialType] = useState('phase2')
  const [indication, setIndication] = useState('')
  const [intervention, setIntervention] = useState('')
  const [primaryEndpoint, setPrimaryEndpoint] = useState('')
  const [secondaryEndpoints, setSecondaryEndpoints] = useState('')
  const [targetEnrollment, setTargetEnrollment] = useState('')
  const [treatmentDuration, setTreatmentDuration] = useState('')
  const [results, setResults] = useState<any>(null)

  const predictMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await clinicalTrialsApi.designTrial(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const requestData: any = {
      trial_type: trialType,
      indication: indication,
      intervention: intervention,
      primary_endpoint: primaryEndpoint,
      target_enrollment: parseInt(targetEnrollment),
      treatment_duration_weeks: parseInt(treatmentDuration),
    }

    if (secondaryEndpoints) {
      requestData.secondary_endpoints = secondaryEndpoints.split(',').map(e => e.trim())
    }

    predictMutation.mutate(requestData)
  }

  const loadExample = () => {
    setTrialType('phase3')
    setIndication('Type 2 Diabetes')
    setIntervention('Novel GLP-1 Agonist')
    setPrimaryEndpoint('HbA1c reduction at 24 weeks')
    setSecondaryEndpoints('Weight loss, Fasting glucose, Hypoglycemia events')
    setTargetEnrollment('500')
    setTreatmentDuration('24')
  }

  const exportToCSV = () => {
    if (!results) return

    const rows = [
      ['Trial Design Summary'],
      ['Trial Type', results.trial_type],
      ['Indication', results.indication],
      ['Design', results.recommended_design],
      ['Total Sample Size', results.total_sample_size],
      ['Duration (months)', results.estimated_duration_months],
      [''],
      ['Trial Arms'],
      ['Arm Name', 'Description', 'Sample Size', 'Treatment'],
      ...results.trial_arms.map((arm: any) => [
        arm.arm_name,
        arm.description,
        arm.sample_size,
        arm.treatment,
      ]),
      [''],
      ['Power Analysis'],
      ['Alpha', results.power_analysis.alpha],
      ['Power', results.power_analysis.power],
      ['Effect Size', results.power_analysis.required_effect_size],
    ]

    const csvContent = rows.map(row => Array.isArray(row) ? row.join(',') : row).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `trial_design_${results.trial_type}.csv`
    a.click()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <ChartLineIcon className="h-8 w-8 text-green-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Trial Design Optimization</h1>
              <p className="mt-1 text-sm text-gray-600">
                AI-assisted trial design with power analysis and sample size calculation
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Input Form */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Trial Parameters</h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Trial Phase *
                  </label>
                  <select
                    value={trialType}
                    onChange={(e) => setTrialType(e.target.value)}
                    className="input"
                    required
                  >
                    <option value="phase1">Phase I - Safety & Dosing</option>
                    <option value="phase2">Phase II - Efficacy & Safety</option>
                    <option value="phase3">Phase III - Confirmatory Efficacy</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Indication *
                  </label>
                  <input
                    type="text"
                    value={indication}
                    onChange={(e) => setIndication(e.target.value)}
                    className="input"
                    placeholder="e.g., Type 2 Diabetes"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Intervention *
                  </label>
                  <input
                    type="text"
                    value={intervention}
                    onChange={(e) => setIntervention(e.target.value)}
                    className="input"
                    placeholder="e.g., Novel GLP-1 Agonist"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Primary Endpoint *
                  </label>
                  <input
                    type="text"
                    value={primaryEndpoint}
                    onChange={(e) => setPrimaryEndpoint(e.target.value)}
                    className="input"
                    placeholder="e.g., HbA1c reduction at 24 weeks"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Secondary Endpoints (comma-separated)
                  </label>
                  <textarea
                    value={secondaryEndpoints}
                    onChange={(e) => setSecondaryEndpoints(e.target.value)}
                    className="input"
                    rows={3}
                    placeholder="e.g., Weight loss, Fasting glucose, Safety"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target Enrollment *
                  </label>
                  <input
                    type="number"
                    value={targetEnrollment}
                    onChange={(e) => setTargetEnrollment(e.target.value)}
                    className="input"
                    placeholder="e.g., 500"
                    min="1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Treatment Duration (weeks) *
                  </label>
                  <input
                    type="number"
                    value={treatmentDuration}
                    onChange={(e) => setTreatmentDuration(e.target.value)}
                    className="input"
                    placeholder="e.g., 24"
                    min="1"
                    required
                  />
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={predictMutation.isPending}
                    className="btn btn-primary flex-1"
                  >
                    {predictMutation.isPending ? 'Designing...' : 'Optimize Design'}
                  </button>
                  <button
                    type="button"
                    onClick={loadExample}
                    className="btn btn-secondary"
                  >
                    Example
                  </button>
                </div>
              </form>

              {predictMutation.isError && (
                <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-3">
                  <p className="text-sm text-red-800">
                    Error: {(predictMutation.error as any)?.response?.data?.detail || 'Failed to optimize trial design'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2">
            {predictMutation.isPending && (
              <div className="card">
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
                </div>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="card">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Sample Size</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                          {results.total_sample_size}
                        </p>
                      </div>
                      <UserGroupIcon className="h-10 w-10 text-blue-500" />
                    </div>
                  </div>

                  <div className="card">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Est. Duration</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                          {results.estimated_duration_months} mo
                        </p>
                      </div>
                      <ClockIcon className="h-10 w-10 text-purple-500" />
                    </div>
                  </div>

                  <div className="card">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Trial Arms</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                          {results.trial_arms.length}
                        </p>
                      </div>
                      <BeakerIcon className="h-10 w-10 text-green-500" />
                    </div>
                  </div>
                </div>

                {/* Recommended Design */}
                <div className="card border-2 border-green-200 bg-green-50">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-green-900">Recommended Design</h3>
                        <span className="badge badge-success">{results.trial_type.toUpperCase()}</span>
                      </div>
                      <p className="text-green-800">
                        {results.recommended_design}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-green-200">
                    <p className="text-sm text-green-900">
                      <span className="font-medium">Indication:</span> {results.indication}
                    </p>
                  </div>
                </div>

                {/* Trial Arms */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Trial Arms</h3>

                  <div className="space-y-3">
                    {results.trial_arms.map((arm: any, index: number) => (
                      <div
                        key={index}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-900">{arm.arm_name}</h4>
                            <p className="text-sm text-gray-600 mt-1">{arm.description}</p>
                          </div>
                          <span className="badge badge-primary">n = {arm.sample_size}</span>
                        </div>

                        <div className="mt-3 pt-3 border-t border-gray-100">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Treatment:</span>
                              <span className="ml-2 font-medium text-gray-900">{arm.treatment}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">Allocation:</span>
                              <span className="ml-2 font-medium text-gray-900">
                                {((arm.sample_size / results.total_sample_size) * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Power Analysis */}
                <div className="card bg-blue-50 border-2 border-blue-200">
                  <h3 className="text-lg font-semibold text-blue-900 mb-4">Power Analysis</h3>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="bg-white rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Significance Level (α)</p>
                      <p className="text-2xl font-bold text-blue-900">{results.power_analysis.alpha}</p>
                    </div>

                    <div className="bg-white rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Statistical Power</p>
                      <p className="text-2xl font-bold text-blue-900">
                        {(results.power_analysis.power * 100).toFixed(0)}%
                      </p>
                    </div>

                    <div className="bg-white rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Required Effect Size</p>
                      <p className="text-2xl font-bold text-blue-900 capitalize">
                        {results.power_analysis.required_effect_size}
                      </p>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-blue-900 mb-2">Justification</h4>
                    <p className="text-sm text-blue-800">
                      {results.power_analysis.sample_size_justification}
                    </p>
                  </div>
                </div>

                {/* Statistical Considerations */}
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      Statistical Considerations
                    </h3>
                    <button
                      onClick={exportToCSV}
                      className="btn btn-secondary btn-sm"
                    >
                      Export CSV
                    </button>
                  </div>

                  <div className="space-y-2">
                    {results.statistical_considerations.map((consideration: string, index: number) => (
                      <div
                        key={index}
                        className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex-shrink-0 mt-0.5">
                          <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                            <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 flex-1">{consideration}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Timeline Estimate */}
                <div className="card bg-purple-50 border-2 border-purple-200">
                  <h3 className="text-lg font-semibold text-purple-900 mb-4">Timeline Estimate</h3>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Recruitment Phase</span>
                      <span className="text-sm text-purple-600 font-semibold">
                        ~{Math.ceil(results.total_sample_size / 20)} months
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Treatment Phase</span>
                      <span className="text-sm text-purple-600 font-semibold">
                        {Math.ceil(parseInt(treatmentDuration) / 4.33)} months
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Follow-up Phase</span>
                      <span className="text-sm text-purple-600 font-semibold">
                        ~3 months
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-purple-100 rounded-lg border-2 border-purple-300">
                      <span className="text-base font-bold text-purple-900">Total Duration</span>
                      <span className="text-xl text-purple-700 font-bold">
                        {results.estimated_duration_months} months
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!results && !predictMutation.isPending && (
              <div className="card text-center py-12">
                <ChartLineIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Results Yet
                </h3>
                <p className="text-gray-600">
                  Enter trial parameters and click "Optimize Design" to get recommendations
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
