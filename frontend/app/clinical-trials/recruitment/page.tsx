'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { clinicalTrialsApi } from '@/lib/api'
import { UserGroupIcon, MapPinIcon, ChartBarIcon, ClockIcon } from '@heroicons/react/24/outline'

export default function PatientRecruitmentPage() {
  const [trialName, setTrialName] = useState('')
  const [indication, setIndication] = useState('')
  const [ageMin, setAgeMin] = useState('')
  const [ageMax, setAgeMax] = useState('')
  const [gender, setGender] = useState('All')
  const [diseaseStage, setDiseaseStage] = useState('')
  const [biomarkers, setBiomarkers] = useState('')
  const [exclusionCriteria, setExclusionCriteria] = useState('')
  const [targetEnrollment, setTargetEnrollment] = useState('')
  const [trialLocations, setTrialLocations] = useState('')
  const [results, setResults] = useState<any>(null)

  const predictMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await clinicalTrialsApi.recruitPatients(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const criteria: any = {}
    if (ageMin) criteria.age_min = parseInt(ageMin)
    if (ageMax) criteria.age_max = parseInt(ageMax)
    if (gender && gender !== 'All') criteria.gender = gender
    if (diseaseStage) criteria.disease_stage = diseaseStage
    if (biomarkers) criteria.biomarkers = biomarkers.split(',').map(b => b.trim())
    if (exclusionCriteria) criteria.exclusion_criteria = exclusionCriteria.split(',').map(e => e.trim())

    const requestData: any = {
      trial_name: trialName,
      indication: indication,
      criteria: criteria,
      target_enrollment: parseInt(targetEnrollment),
    }

    if (trialLocations) {
      requestData.trial_locations = trialLocations.split(',').map(l => l.trim())
    }

    predictMutation.mutate(requestData)
  }

  const loadExample = () => {
    setTrialName('Phase 3 Oncology Trial')
    setIndication('Non-Small Cell Lung Cancer')
    setAgeMin('18')
    setAgeMax('75')
    setGender('All')
    setDiseaseStage('Stage III-IV')
    setBiomarkers('PD-L1+, EGFR-')
    setExclusionCriteria('Prior immunotherapy, Active autoimmune disease')
    setTargetEnrollment('300')
    setTrialLocations('')
  }

  const exportToCSV = () => {
    if (!results) return

    const rows = [
      ['Site Location', 'Eligible Patients', 'Recruitment Rate', 'Feasibility Score'],
      ...results.recommended_sites.map((site: any) => [
        site.location,
        site.estimated_eligible_patients,
        site.recruitment_rate,
        site.site_feasibility_score,
      ]),
    ]

    const csvContent = rows.map(row => row.join(',')).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `recruitment_${results.trial_name.replace(/\s+/g, '_')}.csv`
    a.click()
  }

  const getFeasibilityColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getFeasibilityBadge = (score: number) => {
    if (score >= 0.7) return 'badge-success'
    if (score >= 0.5) return 'badge-warning'
    return 'badge-error'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <UserGroupIcon className="h-8 w-8 text-green-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Patient Recruitment Optimization</h1>
              <p className="mt-1 text-sm text-gray-600">
                Intelligent site selection and enrollment forecasting
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
                    Trial Name *
                  </label>
                  <input
                    type="text"
                    value={trialName}
                    onChange={(e) => setTrialName(e.target.value)}
                    className="input"
                    placeholder="e.g., Phase 3 Oncology Trial"
                    required
                  />
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
                    placeholder="e.g., Non-Small Cell Lung Cancer"
                    required
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
                    placeholder="e.g., 300"
                    min="1"
                    required
                  />
                </div>

                <div className="border-t pt-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Eligibility Criteria</h3>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Min Age
                      </label>
                      <input
                        type="number"
                        value={ageMin}
                        onChange={(e) => setAgeMin(e.target.value)}
                        className="input"
                        placeholder="18"
                        min="0"
                        max="120"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Max Age
                      </label>
                      <input
                        type="number"
                        value={ageMax}
                        onChange={(e) => setAgeMax(e.target.value)}
                        className="input"
                        placeholder="75"
                        min="0"
                        max="120"
                      />
                    </div>
                  </div>

                  <div className="mt-3">
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Gender
                    </label>
                    <select
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                      className="input"
                    >
                      <option value="All">All</option>
                      <option value="M">Male</option>
                      <option value="F">Female</option>
                    </select>
                  </div>

                  <div className="mt-3">
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Disease Stage
                    </label>
                    <input
                      type="text"
                      value={diseaseStage}
                      onChange={(e) => setDiseaseStage(e.target.value)}
                      className="input"
                      placeholder="e.g., Stage III-IV"
                    />
                  </div>

                  <div className="mt-3">
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Biomarkers (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={biomarkers}
                      onChange={(e) => setBiomarkers(e.target.value)}
                      className="input"
                      placeholder="e.g., PD-L1+, EGFR-"
                    />
                  </div>

                  <div className="mt-3">
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Exclusion Criteria (comma-separated)
                    </label>
                    <textarea
                      value={exclusionCriteria}
                      onChange={(e) => setExclusionCriteria(e.target.value)}
                      className="input"
                      rows={2}
                      placeholder="e.g., Prior immunotherapy, Active autoimmune"
                    />
                  </div>
                </div>

                <div className="border-t pt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Preferred Locations (optional, comma-separated)
                  </label>
                  <input
                    type="text"
                    value={trialLocations}
                    onChange={(e) => setTrialLocations(e.target.value)}
                    className="input"
                    placeholder="Leave empty for recommendations"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Leave empty to get site recommendations
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={predictMutation.isPending}
                    className="btn btn-primary flex-1"
                  >
                    {predictMutation.isPending ? 'Analyzing...' : 'Optimize Recruitment'}
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
                    Error: {(predictMutation.error as any)?.response?.data?.detail || 'Failed to optimize recruitment'}
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
                        <p className="text-sm text-gray-600">Eligible Patients</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                          {results.total_estimated_eligible.toLocaleString()}
                        </p>
                      </div>
                      <UserGroupIcon className="h-10 w-10 text-blue-500" />
                    </div>
                  </div>

                  <div className="card">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Est. Timeline</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                          {results.estimated_recruitment_time_months} mo
                        </p>
                      </div>
                      <ClockIcon className="h-10 w-10 text-purple-500" />
                    </div>
                  </div>

                  <div className="card">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Feasibility</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                          {(results.feasibility_score * 100).toFixed(0)}%
                        </p>
                      </div>
                      <ChartBarIcon className="h-10 w-10 text-green-500" />
                    </div>
                  </div>
                </div>

                {/* Recruitment Strategy */}
                <div className={`card border-2 ${getFeasibilityColor(results.feasibility_score)}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold">Recruitment Strategy</h3>
                        <span className={`badge ${getFeasibilityBadge(results.feasibility_score)}`}>
                          {results.feasibility_score >= 0.7 ? 'High Feasibility' :
                           results.feasibility_score >= 0.5 ? 'Moderate Feasibility' : 'Low Feasibility'}
                        </span>
                      </div>
                      <p className="text-sm">
                        {results.recruitment_strategy}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Recommended Sites */}
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      Recommended Trial Sites ({results.recommended_sites.length})
                    </h3>
                    <button
                      onClick={exportToCSV}
                      className="btn btn-secondary btn-sm"
                    >
                      Export CSV
                    </button>
                  </div>

                  <div className="space-y-3">
                    {results.recommended_sites.map((site: any, index: number) => (
                      <div
                        key={index}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <MapPinIcon className="h-5 w-5 text-gray-400" />
                            <h4 className="font-semibold text-gray-900">{site.location}</h4>
                          </div>
                          <span className={`badge ${getFeasibilityBadge(site.site_feasibility_score)}`}>
                            Score: {(site.site_feasibility_score * 100).toFixed(0)}%
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <p className="text-xs text-gray-600">Eligible Patients</p>
                            <p className="text-lg font-semibold text-gray-900">
                              {site.estimated_eligible_patients}
                            </p>
                          </div>

                          <div>
                            <p className="text-xs text-gray-600">Recruitment Rate</p>
                            <p className="text-lg font-semibold text-gray-900">
                              {(site.recruitment_rate * 100).toFixed(1)}%
                            </p>
                          </div>

                          <div>
                            <p className="text-xs text-gray-600">Feasibility</p>
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${
                                    site.site_feasibility_score >= 0.7 ? 'bg-green-500' :
                                    site.site_feasibility_score >= 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${site.site_feasibility_score * 100}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Trial Info */}
                <div className="card bg-gray-50">
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">Trial Summary</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Trial Name:</span>
                      <span className="ml-2 font-medium text-gray-900">{results.trial_name}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Indication:</span>
                      <span className="ml-2 font-medium text-gray-900">{results.indication}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!results && !predictMutation.isPending && (
              <div className="card text-center py-12">
                <UserGroupIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Results Yet
                </h3>
                <p className="text-gray-600">
                  Enter trial parameters and click "Optimize Recruitment" to get site recommendations
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
