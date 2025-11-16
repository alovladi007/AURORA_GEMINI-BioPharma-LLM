'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { clinicalTrialsApi } from '@/lib/api'
import { ShieldExclamationIcon, ExclamationTriangleIcon, ClockIcon, UserGroupIcon } from '@heroicons/react/24/outline'

export default function SafetyMonitoringPage() {
  const [trialId, setTrialId] = useState('')
  const [intervention, setIntervention] = useState('')
  const [patientPopulation, setPatientPopulation] = useState('')
  const [safetyConcerns, setSafetyConcerns] = useState('')
  const [results, setResults] = useState<any>(null)

  const predictMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await clinicalTrialsApi.generateSafetyPlan(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const requestData: any = {
      trial_id: trialId,
      intervention: intervention,
      patient_population: patientPopulation,
    }

    if (safetyConcerns) {
      requestData.known_safety_concerns = safetyConcerns.split(',').map(c => c.trim())
    }

    predictMutation.mutate(requestData)
  }

  const loadExample = () => {
    setTrialId('NCT12345678')
    setIntervention('Novel Kinase Inhibitor')
    setPatientPopulation('Advanced cancer patients')
    setSafetyConcerns('Hepatotoxicity, QT prolongation, Myelosuppression')
  }

  const exportToCSV = () => {
    if (!results) return

    const rows = [
      ['Safety Monitoring Plan'],
      ['Trial ID', results.trial_id],
      [''],
      ['Recommended Safety Metrics'],
      ['Metric Name', 'Monitoring Frequency', 'Alert Threshold', 'Severity'],
      ...results.recommended_metrics.map((metric: any) => [
        metric.metric_name,
        metric.monitoring_frequency,
        metric.alert_threshold,
        metric.severity,
      ]),
      [''],
      ['Stopping Rules'],
      ...results.stopping_rules.map((rule: string) => [rule]),
      [''],
      ['DSMB Recommendations'],
      ...results.dsmb_recommendations.map((rec: string) => [rec]),
    ]

    const csvContent = rows.map(row => Array.isArray(row) ? row.join(',') : row).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `safety_plan_${results.trial_id}.csv`
    a.click()
  }

  const getSeverityColor = (severity: string) => {
    if (severity === 'high') return 'text-red-600 bg-red-50 border-red-200'
    if (severity === 'moderate') return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-blue-600 bg-blue-50 border-blue-200'
  }

  const getSeverityBadge = (severity: string) => {
    if (severity === 'high') return 'badge-error'
    if (severity === 'moderate') return 'badge-warning'
    return 'badge-primary'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <ShieldExclamationIcon className="h-8 w-8 text-green-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Safety Monitoring Plan</h1>
              <p className="mt-1 text-sm text-gray-600">
                Real-time adverse event monitoring and safety signal detection
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
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Trial Information</h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Trial ID *
                  </label>
                  <input
                    type="text"
                    value={trialId}
                    onChange={(e) => setTrialId(e.target.value)}
                    className="input"
                    placeholder="e.g., NCT12345678"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    ClinicalTrials.gov identifier
                  </p>
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
                    placeholder="e.g., Novel Kinase Inhibitor"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Patient Population *
                  </label>
                  <textarea
                    value={patientPopulation}
                    onChange={(e) => setPatientPopulation(e.target.value)}
                    className="input"
                    rows={3}
                    placeholder="e.g., Advanced cancer patients with EGFR mutations"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Known Safety Concerns (comma-separated)
                  </label>
                  <textarea
                    value={safetyConcerns}
                    onChange={(e) => setSafetyConcerns(e.target.value)}
                    className="input"
                    rows={3}
                    placeholder="e.g., Hepatotoxicity, QT prolongation, Myelosuppression"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Optional: List any known or suspected safety issues
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={predictMutation.isPending}
                    className="btn btn-primary flex-1"
                  >
                    {predictMutation.isPending ? 'Generating...' : 'Generate Plan'}
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
                    Error: {(predictMutation.error as any)?.response?.data?.detail || 'Failed to generate safety plan'}
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
                {/* Summary Card */}
                <div className="card border-2 border-green-200 bg-green-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-green-900">Safety Monitoring Plan</h3>
                        <span className="badge badge-success">Generated</span>
                      </div>
                      <p className="text-sm text-green-800">
                        Trial ID: <span className="font-semibold">{results.trial_id}</span>
                      </p>
                    </div>
                    <button
                      onClick={exportToCSV}
                      className="btn btn-secondary btn-sm"
                    >
                      Export CSV
                    </button>
                  </div>
                </div>

                {/* Monitoring Schedule */}
                <div className="card bg-blue-50 border-2 border-blue-200">
                  <div className="flex items-center gap-2 mb-3">
                    <ClockIcon className="h-5 w-5 text-blue-600" />
                    <h3 className="text-lg font-semibold text-blue-900">Monitoring Schedule</h3>
                  </div>
                  <p className="text-blue-800">
                    {results.monitoring_schedule}
                  </p>
                </div>

                {/* Safety Metrics */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Recommended Safety Metrics ({results.recommended_metrics.length})
                  </h3>

                  <div className="space-y-3">
                    {results.recommended_metrics.map((metric: any, index: number) => (
                      <div
                        key={index}
                        className={`border-2 rounded-lg p-4 ${getSeverityColor(metric.severity)}`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold">{metric.metric_name}</h4>
                              <span className={`badge ${getSeverityBadge(metric.severity)} text-xs`}>
                                {metric.severity.toUpperCase()}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mt-3">
                          <div>
                            <p className="text-xs font-medium mb-1">Monitoring Frequency</p>
                            <p className="text-sm font-semibold">{metric.monitoring_frequency}</p>
                          </div>

                          <div>
                            <p className="text-xs font-medium mb-1">Alert Threshold</p>
                            <p className="text-sm font-semibold">{metric.alert_threshold}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Stopping Rules */}
                <div className="card border-2 border-red-200 bg-red-50">
                  <div className="flex items-center gap-2 mb-4">
                    <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
                    <h3 className="text-lg font-semibold text-red-900">Trial Stopping Rules</h3>
                  </div>

                  <div className="space-y-2">
                    {results.stopping_rules.map((rule: string, index: number) => (
                      <div
                        key={index}
                        className="flex items-start gap-3 p-3 bg-white border border-red-200 rounded-lg"
                      >
                        <div className="flex-shrink-0 mt-0.5">
                          <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center">
                            <svg className="w-3 h-3 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                        <p className="text-sm text-red-900 flex-1">{rule}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* DSMB Recommendations */}
                <div className="card bg-purple-50 border-2 border-purple-200">
                  <div className="flex items-center gap-2 mb-4">
                    <UserGroupIcon className="h-5 w-5 text-purple-600" />
                    <h3 className="text-lg font-semibold text-purple-900">
                      Data Safety Monitoring Board (DSMB) Recommendations
                    </h3>
                  </div>

                  <div className="space-y-2">
                    {results.dsmb_recommendations.map((recommendation: string, index: number) => (
                      <div
                        key={index}
                        className="flex items-start gap-3 p-3 bg-white border border-purple-200 rounded-lg"
                      >
                        <div className="flex-shrink-0 mt-0.5">
                          <div className="w-5 h-5 rounded-full bg-purple-100 flex items-center justify-center">
                            <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                        <p className="text-sm text-purple-900 flex-1">{recommendation}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Summary Statistics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="card bg-gray-50">
                    <p className="text-xs text-gray-600 mb-1">Total Metrics</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {results.recommended_metrics.length}
                    </p>
                  </div>

                  <div className="card bg-red-50">
                    <p className="text-xs text-red-600 mb-1">High Severity</p>
                    <p className="text-2xl font-bold text-red-900">
                      {results.recommended_metrics.filter((m: any) => m.severity === 'high').length}
                    </p>
                  </div>

                  <div className="card bg-yellow-50">
                    <p className="text-xs text-yellow-600 mb-1">Moderate Severity</p>
                    <p className="text-2xl font-bold text-yellow-900">
                      {results.recommended_metrics.filter((m: any) => m.severity === 'moderate').length}
                    </p>
                  </div>
                </div>

                {/* Key Considerations */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Considerations</h3>

                  <div className="space-y-3 text-sm text-gray-700">
                    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                          <span className="text-xs font-bold text-green-600">1</span>
                        </div>
                      </div>
                      <p className="flex-1">
                        All adverse events must be documented and reported according to ICH-GCP guidelines
                      </p>
                    </div>

                    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                          <span className="text-xs font-bold text-green-600">2</span>
                        </div>
                      </div>
                      <p className="flex-1">
                        Serious Adverse Events (SAEs) require immediate reporting to the sponsor and IRB within 24 hours
                      </p>
                    </div>

                    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                          <span className="text-xs font-bold text-green-600">3</span>
                        </div>
                      </div>
                      <p className="flex-1">
                        DSMB should review unblinded safety data at pre-specified intervals
                      </p>
                    </div>

                    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                          <span className="text-xs font-bold text-green-600">4</span>
                        </div>
                      </div>
                      <p className="flex-1">
                        Consider implementing a risk-based monitoring approach for efficient oversight
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!results && !predictMutation.isPending && (
              <div className="card text-center py-12">
                <ShieldExclamationIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Results Yet
                </h3>
                <p className="text-gray-600">
                  Enter trial information and click "Generate Plan" to create a safety monitoring plan
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
