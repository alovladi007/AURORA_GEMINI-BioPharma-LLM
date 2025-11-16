'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { repurposingApi } from '@/lib/api'
import { ShareIcon, BeakerIcon, ChartBarIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

export default function KnowledgeGraphPage() {
  const [drugName, setDrugName] = useState('')
  const [maxPaths, setMaxPaths] = useState('10')
  const [pathLength, setPathLength] = useState('3')
  const [results, setResults] = useState<any>(null)

  const mineMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await repurposingApi.mineKnowledgeGraph(data)
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
      max_paths: parseInt(maxPaths),
      path_length: parseInt(pathLength),
    }

    mineMutation.mutate(requestData)
  }

  const loadExample = () => {
    setDrugName('Metformin')
    setMaxPaths('15')
    setPathLength('4')
  }

  const exportToCSV = () => {
    if (!results) return

    const rows = [
      ['Drug', results.drug_name],
      ['Total Paths Found', results.total_paths_found],
      [''],
      ['Candidate Indications'],
      ['Disease Name', 'Disease ID', 'Confidence', 'Shared Targets', 'Mechanism Similarity'],
      ...results.candidate_indications.map((indication: any) => [
        indication.disease_name,
        indication.disease_id,
        indication.confidence_score,
        indication.shared_targets.join('; '),
        indication.mechanism_similarity,
      ]),
    ]

    const csvContent = rows.map(row => Array.isArray(row) ? row.join(',') : row).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `knowledge_graph_${results.drug_name.replace(/\s+/g, '_')}.csv`
    a.click()
  }

  const getNodeTypeColor = (type: string) => {
    const colors: any = {
      drug: 'bg-blue-100 text-blue-700 border-blue-300',
      target: 'bg-green-100 text-green-700 border-green-300',
      pathway: 'bg-purple-100 text-purple-700 border-purple-300',
      disease: 'bg-red-100 text-red-700 border-red-300',
    }
    return colors[type] || 'bg-gray-100 text-gray-700 border-gray-300'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <ShareIcon className="h-8 w-8 text-purple-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Knowledge Graph Mining</h1>
              <p className="mt-1 text-sm text-gray-600">
                Explore drug-disease-target networks to discover new indications
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
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Search Parameters</h2>

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
                    placeholder="e.g., Metformin"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Enter approved drug name
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Maximum Paths
                  </label>
                  <input
                    type="number"
                    value={maxPaths}
                    onChange={(e) => setMaxPaths(e.target.value)}
                    className="input"
                    min="1"
                    max="50"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Number of paths to explore (1-50)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Path Length
                  </label>
                  <select
                    value={pathLength}
                    onChange={(e) => setPathLength(e.target.value)}
                    className="input"
                  >
                    <option value="2">2 hops (Drug → Target → Disease)</option>
                    <option value="3">3 hops (Drug → Target → Pathway → Disease)</option>
                    <option value="4">4 hops (Drug → Target → Pathway → Target → Disease)</option>
                    <option value="5">5 hops (extended search)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Longer paths = more discovery, lower confidence
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={mineMutation.isPending}
                    className="btn btn-primary flex-1"
                  >
                    {mineMutation.isPending ? 'Mining...' : 'Mine Graph'}
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

              {mineMutation.isError && (
                <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-3">
                  <p className="text-sm text-red-800">
                    Error: {(mineMutation.error as any)?.response?.data?.detail || 'Failed to mine knowledge graph'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2">
            {mineMutation.isPending && (
              <div className="card">
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                </div>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="card">
                    <p className="text-xs text-gray-600 mb-1">Total Paths</p>
                    <p className="text-2xl font-bold text-purple-900">
                      {results.total_paths_found}
                    </p>
                  </div>

                  <div className="card">
                    <p className="text-xs text-gray-600 mb-1">Unique Targets</p>
                    <p className="text-2xl font-bold text-green-900">
                      {results.network_statistics.unique_targets}
                    </p>
                  </div>

                  <div className="card">
                    <p className="text-xs text-gray-600 mb-1">Unique Diseases</p>
                    <p className="text-2xl font-bold text-red-900">
                      {results.network_statistics.unique_diseases}
                    </p>
                  </div>

                  <div className="card">
                    <p className="text-xs text-gray-600 mb-1">Avg Confidence</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {(results.network_statistics.avg_confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>

                {/* Candidate Indications */}
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      Candidate Indications ({results.candidate_indications.length})
                    </h3>
                    <button
                      onClick={exportToCSV}
                      className="btn btn-secondary btn-sm"
                    >
                      Export CSV
                    </button>
                  </div>

                  <div className="space-y-3">
                    {results.candidate_indications.map((indication: any, index: number) => (
                      <div
                        key={index}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h4 className="font-semibold text-gray-900">{indication.disease_name}</h4>
                            <p className="text-xs text-gray-500 mt-1">{indication.disease_id}</p>
                          </div>
                          <div className="text-right">
                            <span className={`badge ${
                              indication.confidence_score >= 0.7 ? 'badge-success' :
                              indication.confidence_score >= 0.5 ? 'badge-warning' : 'badge-error'
                            }`}>
                              {(indication.confidence_score * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-xs text-gray-600 mb-1">Mechanism Similarity</p>
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-purple-500 h-2 rounded-full"
                                  style={{ width: `${indication.mechanism_similarity * 100}%` }}
                                />
                              </div>
                              <span className="text-xs font-medium">
                                {(indication.mechanism_similarity * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>

                          <div>
                            <p className="text-xs text-gray-600 mb-1">Shared Targets</p>
                            <p className="text-sm font-medium text-gray-900">
                              {indication.shared_targets.length} targets
                            </p>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t border-gray-100">
                          <p className="text-xs text-gray-600 mb-1">Key Targets:</p>
                          <div className="flex flex-wrap gap-1">
                            {indication.shared_targets.slice(0, 5).map((target: string, idx: number) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
                              >
                                {target}
                              </span>
                            ))}
                            {indication.shared_targets.length > 5 && (
                              <span className="text-xs text-gray-500">
                                +{indication.shared_targets.length - 5} more
                              </span>
                            )}
                          </div>
                        </div>

                        {indication.clinical_evidence && (
                          <div className="mt-3 pt-3 border-t border-gray-100">
                            <p className="text-xs text-gray-600 mb-1">Clinical Evidence:</p>
                            <p className="text-sm text-gray-700">{indication.clinical_evidence}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Knowledge Graph Paths */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Top Knowledge Graph Paths
                  </h3>

                  <div className="space-y-4">
                    {results.paths.slice(0, 5).map((path: any, index: number) => (
                      <div
                        key={index}
                        className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-sm font-medium text-gray-700">Path {index + 1}</span>
                          <span className="badge badge-primary">
                            Confidence: {(path.confidence_score * 100).toFixed(0)}%
                          </span>
                        </div>

                        {/* Path visualization */}
                        <div className="flex items-center gap-2 overflow-x-auto pb-2">
                          {path.nodes.map((node: any, nodeIdx: number) => (
                            <div key={nodeIdx} className="flex items-center">
                              <div
                                className={`px-3 py-2 rounded-lg border-2 ${getNodeTypeColor(node.node_type)} whitespace-nowrap`}
                              >
                                <p className="text-xs font-medium">{node.node_type.toUpperCase()}</p>
                                <p className="text-sm font-semibold">{node.name}</p>
                              </div>
                              {nodeIdx < path.nodes.length - 1 && (
                                <svg className="w-6 h-6 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                              )}
                            </div>
                          ))}
                        </div>

                        {/* Supporting evidence */}
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-600 mb-2">Supporting Evidence:</p>
                          <div className="space-y-1">
                            {path.supporting_evidence.map((evidence: string, evidenceIdx: number) => (
                              <p key={evidenceIdx} className="text-xs text-gray-700">
                                • {evidence}
                              </p>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {results.paths.length > 5 && (
                    <p className="text-sm text-gray-600 mt-4 text-center">
                      Showing top 5 of {results.paths.length} paths
                    </p>
                  )}
                </div>
              </div>
            )}

            {!results && !mineMutation.isPending && (
              <div className="card text-center py-12">
                <ShareIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Results Yet
                </h3>
                <p className="text-gray-600">
                  Enter a drug name and click "Mine Graph" to discover repurposing opportunities
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
