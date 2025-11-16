'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { repurposingApi } from '@/lib/api'
import { MagnifyingGlassIcon, BeakerIcon, ChartBarIcon, BoltIcon } from '@heroicons/react/24/outline'

export default function MechanismPredictionPage() {
  const [drugName, setDrugName] = useState('')
  const [diseaseName, setDiseaseName] = useState('')
  const [includePathways, setIncludePathways] = useState(true)
  const [results, setResults] = useState<any>(null)

  const predictMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await repurposingApi.predictMechanism(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const requestData = {
      drug_name: drugName,
      disease_name: diseaseName,
      include_pathways: includePathways,
    }

    predictMutation.mutate(requestData)
  }

  const loadExample = () => {
    setDrugName('Aspirin')
    setDiseaseName("Alzheimer's Disease")
    setIncludePathways(true)
  }

  const exportToCSV = () => {
    if (!results) return

    const rows = [
      ['Mechanism Prediction Summary'],
      ['Drug', results.drug_name],
      ['Disease', results.disease_name],
      ['Confidence Score', results.confidence_score],
      [''],
      ['Mechanism Summary'],
      [results.mechanism_summary],
      [''],
      ['Predicted Targets'],
      ['Target Name', 'Target ID', 'Confidence', 'Interaction Type'],
      ...results.predicted_targets.map((target: any) => [
        target.target_name,
        target.target_id,
        target.prediction_confidence,
        target.interaction_type,
      ]),
      [''],
      ['Enriched Pathways'],
      ['Pathway Name', 'P-value', 'Enrichment Score', 'Genes Involved'],
      ...results.enriched_pathways.map((pathway: any) => [
        pathway.pathway_name,
        pathway.p_value,
        pathway.enrichment_score,
        pathway.genes_involved.join('; '),
      ]),
    ]

    const csvContent = rows.map(row => Array.isArray(row) ? row.join(',') : row).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mechanism_${results.drug_name.replace(/\s+/g, '_')}_${results.disease_name.replace(/\s+/g, '_')}.csv`
    a.click()
  }

  const getInteractionColor = (type: string) => {
    const colors: any = {
      inhibitor: 'bg-red-100 text-red-700 border-red-300',
      antagonist: 'bg-orange-100 text-orange-700 border-orange-300',
      agonist: 'bg-green-100 text-green-700 border-green-300',
      activator: 'bg-blue-100 text-blue-700 border-blue-300',
      modulator: 'bg-purple-100 text-purple-700 border-purple-300',
    }
    return colors[type.toLowerCase()] || 'bg-gray-100 text-gray-700 border-gray-300'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <MagnifyingGlassIcon className="h-8 w-8 text-purple-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Mechanism Prediction</h1>
              <p className="mt-1 text-sm text-gray-600">
                Predict mechanisms of action using network-based approaches
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
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Drug-Disease Pair</h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Drug Name *
                  </label>
                  <input
                    type="text"
                    value={drugName}
                    onChange={(e) => setDrugName(e.target.value)}
                    className="input"
                    placeholder="e.g., Aspirin"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Disease Name *
                  </label>
                  <input
                    type="text"
                    value={diseaseName}
                    onChange={(e) => setDiseaseName(e.target.value)}
                    className="input"
                    placeholder="e.g., Alzheimer's Disease"
                    required
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="includePathways"
                    checked={includePathways}
                    onChange={(e) => setIncludePathways(e.target.checked)}
                    className="h-4 w-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                  />
                  <label htmlFor="includePathways" className="ml-2 block text-sm text-gray-700">
                    Include pathway enrichment analysis
                  </label>
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={predictMutation.isPending}
                    className="btn btn-primary flex-1"
                  >
                    {predictMutation.isPending ? 'Predicting...' : 'Predict Mechanism'}
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
                    Error: {(predictMutation.error as any)?.response?.data?.detail || 'Failed to predict mechanism'}
                  </p>
                </div>
              )}

              {/* Info Box */}
              <div className="mt-6 rounded-lg bg-purple-50 border border-purple-200 p-4">
                <h3 className="text-sm font-semibold text-purple-900 mb-2">What is Mechanism Prediction?</h3>
                <p className="text-xs text-purple-700">
                  Mechanism prediction identifies the molecular targets and biological pathways through which a drug
                  may exert therapeutic effects in a specific disease context.
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2">
            {predictMutation.isPending && (
              <div className="card">
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                </div>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {/* Overall Score */}
                <div className="card border-2 border-purple-200 bg-purple-50">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-purple-900">Mechanism Prediction Summary</h3>
                    <div className="flex items-center gap-2">
                      <span className={`badge ${
                        results.confidence_score >= 0.7 ? 'badge-success' :
                        results.confidence_score >= 0.5 ? 'badge-warning' : 'badge-error'
                      }`}>
                        {(results.confidence_score * 100).toFixed(0)}% confidence
                      </span>
                      <button
                        onClick={exportToCSV}
                        className="btn btn-secondary btn-sm"
                      >
                        Export CSV
                      </button>
                    </div>
                  </div>
                  <p className="text-purple-800">
                    {results.mechanism_summary}
                  </p>
                  <div className="mt-4 pt-4 border-t border-purple-200 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-purple-700">Drug:</span>
                      <span className="ml-2 font-semibold text-purple-900">{results.drug_name}</span>
                    </div>
                    <div>
                      <span className="text-purple-700">Disease:</span>
                      <span className="ml-2 font-semibold text-purple-900">{results.disease_name}</span>
                    </div>
                  </div>
                </div>

                {/* Predicted Targets */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Predicted Molecular Targets ({results.predicted_targets.length})
                  </h3>

                  <div className="space-y-3">
                    {results.predicted_targets.map((target: any, index: number) => (
                      <div
                        key={index}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold text-gray-900">{target.target_name}</h4>
                              <span
                                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getInteractionColor(target.interaction_type)}`}
                              >
                                {target.interaction_type}
                              </span>
                            </div>
                            <p className="text-xs text-gray-500">{target.target_id}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-gray-600">Confidence</p>
                            <p className="text-lg font-bold text-purple-900">
                              {(target.prediction_confidence * 100).toFixed(0)}%
                            </p>
                          </div>
                        </div>

                        <div className="mb-3">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                target.prediction_confidence >= 0.7 ? 'bg-green-500' :
                                target.prediction_confidence >= 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${target.prediction_confidence * 100}%` }}
                            />
                          </div>
                        </div>

                        <div className="pt-3 border-t border-gray-100">
                          <p className="text-xs text-gray-600 mb-2">Supporting Evidence:</p>
                          <div className="space-y-1">
                            {target.supporting_evidence.map((evidence: string, evidenceIdx: number) => (
                              <p key={evidenceIdx} className="text-xs text-gray-700">
                                • {evidence}
                              </p>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Enriched Pathways */}
                {results.enriched_pathways.length > 0 && (
                  <div className="card">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Enriched Biological Pathways ({results.enriched_pathways.length})
                    </h3>

                    <div className="space-y-3">
                      {results.enriched_pathways.map((pathway: any, index: number) => (
                        <div
                          key={index}
                          className="border border-gray-200 rounded-lg p-4 bg-blue-50"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-900">{pathway.pathway_name}</h4>
                              <p className="text-xs text-gray-500 mt-1">{pathway.pathway_id}</p>
                            </div>
                            <span className="badge badge-primary">
                              {pathway.enrichment_score.toFixed(2)}x
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                            <div>
                              <p className="text-xs text-gray-600">P-value</p>
                              <p className="font-semibold text-gray-900">{pathway.p_value.toExponential(2)}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-600">Enrichment Score</p>
                              <p className="font-semibold text-gray-900">{pathway.enrichment_score.toFixed(2)}-fold</p>
                            </div>
                          </div>

                          <div className="pt-3 border-t border-blue-200">
                            <p className="text-xs text-gray-600 mb-2">Genes Involved:</p>
                            <div className="flex flex-wrap gap-1">
                              {pathway.genes_involved.map((gene: string, geneIdx: number) => (
                                <span
                                  key={geneIdx}
                                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                                >
                                  {gene}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Mechanism Insights */}
                <div className="card bg-gray-50">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>

                  <div className="space-y-3">
                    <div className="flex items-start gap-3 p-3 bg-white rounded-lg">
                      <div className="flex-shrink-0 mt-0.5">
                        <BeakerIcon className="h-5 w-5 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Target Diversity</p>
                        <p className="text-xs text-gray-600 mt-1">
                          {results.predicted_targets.length} predicted targets suggest {
                            results.predicted_targets.length > 5 ? 'multi-target' : 'selective'
                          } mechanism of action
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 p-3 bg-white rounded-lg">
                      <div className="flex-shrink-0 mt-0.5">
                        <ChartBarIcon className="h-5 w-5 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Pathway Involvement</p>
                        <p className="text-xs text-gray-600 mt-1">
                          {results.enriched_pathways.length} enriched pathways identified with average enrichment of{' '}
                          {(results.enriched_pathways.reduce((sum: number, p: any) => sum + p.enrichment_score, 0) / results.enriched_pathways.length).toFixed(1)}x
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 p-3 bg-white rounded-lg">
                      <div className="flex-shrink-0 mt-0.5">
                        <BoltIcon className="h-5 w-5 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Interaction Types</p>
                        <p className="text-xs text-gray-600 mt-1">
                          Primary interactions: {
                            [...new Set(results.predicted_targets.map((t: any) => t.interaction_type))].join(', ')
                          }
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!results && !predictMutation.isPending && (
              <div className="card text-center py-12">
                <MagnifyingGlassIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Results Yet
                </h3>
                <p className="text-gray-600">
                  Enter a drug-disease pair and click "Predict Mechanism" to analyze mechanism of action
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
