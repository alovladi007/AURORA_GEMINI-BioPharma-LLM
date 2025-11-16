'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import Link from 'next/link'
import { ArrowLeftIcon, CogIcon } from '@heroicons/react/24/outline'
import { drugDesignApi } from '@/lib/api'

const exampleLead = 'CC(C)Cc1ccc(C(C)C(=O)O)cc1' // Ibuprofen

export default function OptimizePage() {
  const [leadSmiles, setLeadSmiles] = useState('')
  const [numAnalogs, setNumAnalogs] = useState(50)
  const [similarityThreshold, setSimilarityThreshold] = useState(0.7)
  const [objectives, setObjectives] = useState({
    activity: 8.0,
    LogP: 2.5,
    MW: 400,
  })
  const [results, setResults] = useState<any>(null)

  const optimizeMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await drugDesignApi.optimize(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!leadSmiles.trim()) {
      return
    }

    optimizeMutation.mutate({
      lead_smiles: leadSmiles,
      num_analogs: numAnalogs,
      similarity_threshold: similarityThreshold,
      objectives,
    })
  }

  const loadExample = () => {
    setLeadSmiles(exampleLead)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center">
            <Link href="/drug-design" className="text-gray-500 hover:text-gray-700 mr-4">
              <ArrowLeftIcon className="h-5 w-5" />
            </Link>
            <div className="flex items-center">
              <CogIcon className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Lead Optimization</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Optimize lead compounds for better drug-like properties
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Form */}
          <div className="lg:col-span-1 space-y-6">
            <form onSubmit={handleSubmit} className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Lead Compound</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Lead SMILES
                  </label>
                  <input
                    type="text"
                    value={leadSmiles}
                    onChange={(e) => setLeadSmiles(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                    placeholder="Enter lead compound SMILES..."
                  />
                  <button
                    type="button"
                    onClick={loadExample}
                    className="mt-2 text-xs text-blue-600 hover:text-blue-700"
                  >
                    Load example (Ibuprofen)
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Analogs
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="500"
                    value={numAnalogs}
                    onChange={(e) => setNumAnalogs(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Similarity Threshold
                  </label>
                  <input
                    type="number"
                    min="0.5"
                    max="1.0"
                    step="0.05"
                    value={similarityThreshold}
                    onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Minimum Tanimoto similarity (0.5-1.0)
                  </p>
                </div>
              </div>
            </form>

            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Optimization Objectives</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target Activity
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={objectives.activity}
                    onChange={(e) =>
                      setObjectives({ ...objectives, activity: parseFloat(e.target.value) })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target LogP
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={objectives.LogP}
                    onChange={(e) =>
                      setObjectives({ ...objectives, LogP: parseFloat(e.target.value) })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target Molecular Weight
                  </label>
                  <input
                    type="number"
                    step="10"
                    value={objectives.MW}
                    onChange={(e) =>
                      setObjectives({ ...objectives, MW: parseFloat(e.target.value) })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <button
                    type="submit"
                    onClick={handleSubmit}
                    disabled={optimizeMutation.isPending || !leadSmiles.trim()}
                    className="w-full btn-primary"
                  >
                    {optimizeMutation.isPending ? (
                      <>
                        <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-r-transparent mr-2"></div>
                        Optimizing...
                      </>
                    ) : (
                      <>
                        <CogIcon className="h-5 w-5 mr-2" />
                        Optimize Lead
                      </>
                    )}
                  </button>
                </div>
              </div>

              {optimizeMutation.isError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">
                    {(optimizeMutation.error as any)?.response?.data?.detail ||
                      'Optimization failed'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {!results && !optimizeMutation.isPending && (
              <div className="card text-center py-12">
                <CogIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">No optimization yet</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Enter a lead compound and objectives to start optimization
                </p>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {/* Summary */}
                <div className="card">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Optimization Results</h2>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Lead Compound:</span>
                      <code className="text-sm font-mono text-gray-700 bg-gray-100 px-2 py-1 rounded">
                        {results.lead_smiles}
                      </code>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Analogs Generated:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {results.optimized_molecules?.length || 0}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Optimization Time:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {results.optimization_time?.toFixed(2)}s
                      </span>
                    </div>
                  </div>
                </div>

                {/* Optimized Molecules */}
                <div className="card">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Top Optimized Analogs</h3>
                  <div className="space-y-4">
                    {results.optimized_molecules?.slice(0, 10).map((mol: any, idx: number) => (
                      <div key={idx} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center">
                            <span className="text-sm font-medium text-gray-500 mr-2">
                              #{idx + 1}
                            </span>
                            <span className="badge badge-info text-xs">
                              Score: {mol.optimization_score?.toFixed(3)}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500">
                            Similarity: {mol.similarity_to_lead?.toFixed(2)}
                          </span>
                        </div>

                        <code className="text-sm font-mono text-gray-700 bg-gray-100 px-2 py-1 rounded block mb-3">
                          {mol.smiles}
                        </code>

                        <div className="grid grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Activity:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {mol.predicted_properties?.activity?.toFixed(2) || 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">LogP:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {mol.predicted_properties?.LogP?.toFixed(2) || 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">MW:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {mol.predicted_properties?.MW?.toFixed(1) || 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">TPSA:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {mol.predicted_properties?.TPSA?.toFixed(1) || 'N/A'}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Export Button */}
                <div className="flex justify-end">
                  <button
                    onClick={() => {
                      const csv = [
                        'Rank,SMILES,Optimization Score,Similarity,Activity,LogP,MW,TPSA',
                        ...results.optimized_molecules.map((m: any, i: number) =>
                          [
                            i + 1,
                            m.smiles,
                            m.optimization_score?.toFixed(3),
                            m.similarity_to_lead?.toFixed(2),
                            m.predicted_properties?.activity?.toFixed(2),
                            m.predicted_properties?.LogP?.toFixed(2),
                            m.predicted_properties?.MW?.toFixed(1),
                            m.predicted_properties?.TPSA?.toFixed(1),
                          ].join(',')
                        ),
                      ].join('\n')

                      const blob = new Blob([csv], { type: 'text/csv' })
                      const url = window.URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'optimized_analogs.csv'
                      a.click()
                    }}
                    className="btn-primary"
                  >
                    Export as CSV
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
