'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import Link from 'next/link'
import { ArrowLeftIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { safetyApi } from '@/lib/api'

const exampleSMILES = [
  'CC(C)Cc1ccc(C(C)C(=O)O)cc1',
  'CC(=O)Oc1ccccc1C(=O)O',
].join('\n')

const ENDPOINTS = [
  'hepatotoxicity',
  'cardiotoxicity',
  'nephrotoxicity',
  'neurotoxicity',
  'genotoxicity',
  'carcinogenicity',
  'skin_sensitization',
]

export default function ToxicityPage() {
  const [smilesInput, setSmilesInput] = useState('')
  const [selectedEndpoints, setSelectedEndpoints] = useState<string[]>(ENDPOINTS)
  const [results, setResults] = useState<any>(null)

  const predictMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await safetyApi.predictToxicity(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const smilesList = smilesInput
      .split('\n')
      .map((s) => s.trim())
      .filter((s) => s.length > 0)

    if (smilesList.length === 0) return
    predictMutation.mutate({
      smiles: smilesList,
      endpoints: selectedEndpoints.length === ENDPOINTS.length ? undefined : selectedEndpoints,
    })
  }

  const toggleEndpoint = (endpoint: string) => {
    setSelectedEndpoints((prev) =>
      prev.includes(endpoint) ? prev.filter((e) => e !== endpoint) : [...prev, endpoint]
    )
  }

  const getRiskColor = (level: string) => {
    if (level === 'low') return 'bg-green-100 text-green-800 border-green-300'
    if (level === 'moderate') return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    return 'bg-red-100 text-red-800 border-red-300'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center">
            <Link href="/safety" className="text-gray-500 hover:text-gray-700 mr-4">
              <ArrowLeftIcon className="h-5 w-5" />
            </Link>
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Toxicity Prediction</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Assess organ-specific toxicity risks and safety liabilities
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-6">
            <form onSubmit={handleSubmit} className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Input Molecules</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    SMILES Strings
                  </label>
                  <textarea
                    value={smilesInput}
                    onChange={(e) => setSmilesInput(e.target.value)}
                    rows={8}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500 font-mono text-sm"
                    placeholder="Enter SMILES strings..."
                  />
                  <button
                    type="button"
                    onClick={() => setSmilesInput(exampleSMILES)}
                    className="mt-2 text-xs text-red-600 hover:text-red-700"
                  >
                    Load examples
                  </button>
                </div>
                <button
                  type="submit"
                  disabled={predictMutation.isPending || !smilesInput.trim()}
                  className="w-full btn-primary bg-red-600 hover:bg-red-700"
                >
                  {predictMutation.isPending ? 'Predicting...' : 'Predict Toxicity'}
                </button>
              </div>
              {predictMutation.isError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">
                    {(predictMutation.error as any)?.response?.data?.detail || 'Prediction failed'}
                  </p>
                </div>
              )}
            </form>

            <div className="card">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Toxicity Endpoints</h3>
              <div className="space-y-2">
                {ENDPOINTS.map((endpoint) => (
                  <label key={endpoint} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedEndpoints.includes(endpoint)}
                      onChange={() => toggleEndpoint(endpoint)}
                      className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                    />
                    <span className="ml-2 text-sm text-gray-700 capitalize">
                      {endpoint.replace('_', ' ')}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            {!results && !predictMutation.isPending && (
              <div className="card text-center py-12">
                <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">No predictions yet</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Enter SMILES and select endpoints to predict toxicity
                </p>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {results.predictions?.map((pred: any, idx: number) => (
                  <div key={idx} className="card">
                    <div className="flex items-center justify-between mb-4">
                      <code className="text-sm font-mono bg-gray-100 px-3 py-1 rounded">
                        {pred.smiles}
                      </code>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium border ${getRiskColor(
                          pred.overall_risk
                        )}`}
                      >
                        {pred.overall_risk.toUpperCase()} RISK
                      </span>
                    </div>

                    {/* Endpoints Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      {pred.endpoints?.map((ep: any) => (
                        <div
                          key={ep.endpoint}
                          className="border rounded-lg p-3"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="text-sm font-medium text-gray-900 capitalize">
                              {ep.endpoint.replace('_', ' ')}
                            </h4>
                            <span
                              className={`px-2 py-0.5 rounded text-xs font-medium ${getRiskColor(
                                ep.risk_level
                              )}`}
                            >
                              {ep.risk_level}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-xs text-gray-600">
                            <span>Probability:</span>
                            <span className="font-medium">{ep.probability?.toFixed(3)}</span>
                          </div>
                          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                ep.risk_level === 'low'
                                  ? 'bg-green-500'
                                  : ep.risk_level === 'moderate'
                                  ? 'bg-yellow-500'
                                  : 'bg-red-500'
                              }`}
                              style={{ width: `${ep.probability * 100}%` }}
                            ></div>
                          </div>
                          <div className="mt-1 text-xs text-gray-500">
                            Confidence: {(ep.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Structural Alerts */}
                    {pred.alerts && pred.alerts.length > 0 && (
                      <div className="border-t pt-4">
                        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                          <ExclamationTriangleIcon className="h-4 w-4 mr-2 text-yellow-600" />
                          Structural Alerts
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {pred.alerts.map((alert: string, i: number) => (
                            <span
                              key={i}
                              className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded border border-yellow-300"
                            >
                              {alert}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                <div className="flex justify-end">
                  <button
                    onClick={() => {
                      const csv = [
                        'SMILES,Overall Risk,Overall Probability,' +
                          selectedEndpoints.map((e) => `${e}_prob,${e}_risk`).join(','),
                        ...results.predictions.map((p: any) => {
                          const endpointData = selectedEndpoints
                            .map((e) => {
                              const ep = p.endpoints.find((x: any) => x.endpoint === e)
                              return `${ep?.probability?.toFixed(3) || ''},${ep?.risk_level || ''}`
                            })
                            .join(',')
                          return `${p.smiles},${p.overall_risk},${p.overall_probability?.toFixed(3)},${endpointData}`
                        }),
                      ].join('\n')
                      const blob = new Blob([csv], { type: 'text/csv' })
                      const url = window.URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'toxicity_predictions.csv'
                      a.click()
                    }}
                    className="btn-primary bg-red-600 hover:bg-red-700"
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
