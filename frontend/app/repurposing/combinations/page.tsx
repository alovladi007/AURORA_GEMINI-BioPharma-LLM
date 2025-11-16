'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { repurposingApi } from '@/lib/api'
import { BeakerIcon, ExclamationTriangleIcon, CheckCircleIcon, BoltIcon } from '@heroicons/react/24/outline'

export default function CombinationDiscoveryPage() {
  const [anchorDrug, setAnchorDrug] = useState('')
  const [indication, setIndication] = useState('')
  const [maxCombinations, setMaxCombinations] = useState('10')
  const [synergyThreshold, setSynergyThreshold] = useState('0.5')
  const [results, setResults] = useState<any>(null)

  const discoverMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await repurposingApi.discoverCombinations(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const requestData = {
      anchor_drug: anchorDrug,
      indication: indication,
      max_combinations: parseInt(maxCombinations),
      synergy_threshold: parseFloat(synergyThreshold),
    }

    discoverMutation.mutate(requestData)
  }

  const loadExample = () => {
    setAnchorDrug('Pembrolizumab')
    setIndication('Non-Small Cell Lung Cancer')
    setMaxCombinations('15')
    setSynergyThreshold('0.6')
  }

  const exportToCSV = () => {
    if (!results) return

    const rows = [
      ['Drug Combination Discovery'],
      ['Anchor Drug', results.anchor_drug],
      ['Indication', results.indication],
      ['Total Evaluated', results.total_combinations_evaluated],
      [''],
      ['Recommended Combinations'],
      ['Partner Drug', 'Synergy Score', 'Mechanism', 'Shared Targets', 'Unique Targets', 'Safety Concerns'],
      ...results.recommended_combinations.map((combo: any) => [
        combo.partner_drug,
        combo.synergy_score,
        combo.mechanism_complementarity,
        combo.shared_targets.join('; '),
        combo.unique_targets.join('; '),
        combo.safety_concerns ? combo.safety_concerns.join('; ') : 'None',
      ]),
    ]

    const csvContent = rows.map(row => Array.isArray(row) ? row.join(',') : row).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `combinations_${results.anchor_drug.replace(/\s+/g, '_')}.csv`
    a.click()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <BeakerIcon className="h-8 w-8 text-purple-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Combination Discovery</h1>
              <p className="mt-1 text-sm text-gray-600">
                Identify synergistic drug combinations for improved efficacy
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
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Combination Search</h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Anchor Drug *
                  </label>
                  <input
                    type="text"
                    value={anchorDrug}
                    onChange={(e) => setAnchorDrug(e.target.value)}
                    className="input"
                    placeholder="e.g., Pembrolizumab"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Primary drug for combination therapy
                  </p>
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
                    Max Combinations
                  </label>
                  <input
                    type="number"
                    value={maxCombinations}
                    onChange={(e) => setMaxCombinations(e.target.value)}
                    className="input"
                    min="1"
                    max="50"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Maximum results to return (1-50)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Synergy Threshold
                  </label>
                  <input
                    type="number"
                    value={synergyThreshold}
                    onChange={(e) => setSynergyThreshold(e.target.value)}
                    className="input"
                    min="0"
                    max="1"
                    step="0.1"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Minimum synergy score (0-1)
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={discoverMutation.isPending}
                    className="btn btn-primary flex-1"
                  >
                    {discoverMutation.isPending ? 'Discovering...' : 'Discover Combinations'}
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

              {discoverMutation.isError && (
                <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-3">
                  <p className="text-sm text-red-800">
                    Error: {(discoverMutation.error as any)?.response?.data?.detail || 'Failed to discover combinations'}
                  </p>
                </div>
              )}

              {/* Info Box */}
              <div className="mt-6 rounded-lg bg-purple-50 border border-purple-200 p-4">
                <h3 className="text-sm font-semibold text-purple-900 mb-2">About Synergy</h3>
                <p className="text-xs text-purple-700">
                  Synergistic combinations show greater therapeutic effect than the sum of individual drugs.
                  Our algorithm predicts synergy based on target complementarity and pathway coverage.
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2">
            {discoverMutation.isPending && (
              <div className="card">
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                </div>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {/* Summary */}
                <div className="card border-2 border-purple-200 bg-purple-50">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-purple-900">Analysis Summary</h3>
                    <button
                      onClick={exportToCSV}
                      className="btn btn-secondary btn-sm"
                    >
                      Export CSV
                    </button>
                  </div>
                  <p className="text-purple-800 mb-4">
                    {results.analysis_summary}
                  </p>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white rounded-lg p-3">
                      <p className="text-xs text-purple-600 mb-1">Anchor Drug</p>
                      <p className="font-semibold text-purple-900">{results.anchor_drug}</p>
                    </div>
                    <div className="bg-white rounded-lg p-3">
                      <p className="text-xs text-purple-600 mb-1">Indication</p>
                      <p className="font-semibold text-purple-900">{results.indication}</p>
                    </div>
                    <div className="bg-white rounded-lg p-3">
                      <p className="text-xs text-purple-600 mb-1">Evaluated</p>
                      <p className="font-semibold text-purple-900">{results.total_combinations_evaluated}</p>
                    </div>
                  </div>
                </div>

                {/* Recommended Combinations */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Recommended Combinations ({results.recommended_combinations.length})
                  </h3>

                  {results.recommended_combinations.length === 0 ? (
                    <div className="text-center py-8">
                      <ExclamationTriangleIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600">
                        No combinations found meeting the synergy threshold of {synergyThreshold}
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Try lowering the synergy threshold or changing the anchor drug
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {results.recommended_combinations.map((combo: any, index: number) => (
                        <div
                          key={index}
                          className="border-2 border-gray-200 rounded-lg p-5 hover:shadow-lg transition-shadow"
                        >
                          {/* Header */}
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="text-lg font-bold text-gray-900">{combo.partner_drug}</h4>
                                <span className={`badge ${
                                  combo.synergy_score >= 0.8 ? 'badge-success' :
                                  combo.synergy_score >= 0.6 ? 'badge-warning' : 'badge-primary'
                                } text-sm`}>
                                  {(combo.synergy_score * 100).toFixed(0)}% synergy
                                </span>
                                {combo.clinical_evidence && (
                                  <span className="badge badge-info text-xs">Clinical Evidence</span>
                                )}
                              </div>
                              <p className="text-xs text-gray-500">{combo.partner_drug_id}</p>
                            </div>
                          </div>

                          {/* Synergy Score Bar */}
                          <div className="mb-4">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium text-gray-700">Synergy Score</span>
                              <span className="text-xs font-bold text-purple-900">
                                {(combo.synergy_score * 100).toFixed(0)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div
                                className={`h-3 rounded-full ${
                                  combo.synergy_score >= 0.8 ? 'bg-green-500' :
                                  combo.synergy_score >= 0.6 ? 'bg-yellow-500' : 'bg-blue-500'
                                }`}
                                style={{ width: `${combo.synergy_score * 100}%` }}
                              />
                            </div>
                          </div>

                          {/* Mechanism Complementarity */}
                          <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                            <div className="flex items-start gap-2">
                              <BoltIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                              <div>
                                <p className="text-xs font-semibold text-blue-900 mb-1">Mechanism Complementarity</p>
                                <p className="text-sm text-blue-800">{combo.mechanism_complementarity}</p>
                              </div>
                            </div>
                          </div>

                          {/* Targets */}
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                              <p className="text-xs font-medium text-gray-700 mb-2">
                                Shared Targets ({combo.shared_targets.length})
                              </p>
                              <div className="flex flex-wrap gap-1">
                                {combo.shared_targets.slice(0, 4).map((target: string, idx: number) => (
                                  <span
                                    key={idx}
                                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
                                  >
                                    {target}
                                  </span>
                                ))}
                                {combo.shared_targets.length > 4 && (
                                  <span className="text-xs text-gray-500">
                                    +{combo.shared_targets.length - 4}
                                  </span>
                                )}
                              </div>
                            </div>

                            <div>
                              <p className="text-xs font-medium text-gray-700 mb-2">
                                Unique Targets ({combo.unique_targets.length})
                              </p>
                              <div className="flex flex-wrap gap-1">
                                {combo.unique_targets.slice(0, 4).map((target: string, idx: number) => (
                                  <span
                                    key={idx}
                                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800"
                                  >
                                    {target}
                                  </span>
                                ))}
                                {combo.unique_targets.length > 4 && (
                                  <span className="text-xs text-gray-500">
                                    +{combo.unique_targets.length - 4}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Safety Concerns */}
                          {combo.safety_concerns && combo.safety_concerns.length > 0 && (
                            <div className="mb-3 p-3 bg-red-50 rounded-lg border border-red-200">
                              <div className="flex items-start gap-2">
                                <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                                <div className="flex-1">
                                  <p className="text-xs font-semibold text-red-900 mb-1">Safety Considerations</p>
                                  <ul className="space-y-1">
                                    {combo.safety_concerns.map((concern: string, idx: number) => (
                                      <li key={idx} className="text-xs text-red-800">
                                        • {concern}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Clinical Evidence */}
                          {combo.clinical_evidence && (
                            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                              <div className="flex items-start gap-2">
                                <CheckCircleIcon className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                                <div>
                                  <p className="text-xs font-semibold text-green-900 mb-1">Clinical Evidence</p>
                                  <p className="text-sm text-green-800">{combo.clinical_evidence}</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {!combo.clinical_evidence && !combo.safety_concerns && (
                            <div className="text-center py-2 text-xs text-gray-500">
                              No additional safety concerns or clinical evidence available
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Statistics */}
                {results.recommended_combinations.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="card bg-green-50">
                      <p className="text-xs text-green-600 mb-1">Avg Synergy Score</p>
                      <p className="text-2xl font-bold text-green-900">
                        {(
                          (results.recommended_combinations.reduce((sum: number, c: any) => sum + c.synergy_score, 0) /
                            results.recommended_combinations.length) *
                          100
                        ).toFixed(0)}%
                      </p>
                    </div>

                    <div className="card bg-blue-50">
                      <p className="text-xs text-blue-600 mb-1">With Clinical Evidence</p>
                      <p className="text-2xl font-bold text-blue-900">
                        {results.recommended_combinations.filter((c: any) => c.clinical_evidence).length}
                      </p>
                    </div>

                    <div className="card bg-yellow-50">
                      <p className="text-xs text-yellow-600 mb-1">Safety Monitoring Required</p>
                      <p className="text-2xl font-bold text-yellow-900">
                        {results.recommended_combinations.filter((c: any) => c.safety_concerns && c.safety_concerns.length > 0).length}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {!results && !discoverMutation.isPending && (
              <div className="card text-center py-12">
                <BeakerIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Results Yet
                </h3>
                <p className="text-gray-600">
                  Enter an anchor drug and indication to discover synergistic combinations
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
