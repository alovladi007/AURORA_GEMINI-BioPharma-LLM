'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import Link from 'next/link'
import { ArrowLeftIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import { drugDesignApi } from '@/lib/api'

const exampleSMILES = [
  'CC(C)Cc1ccc(C(C)C(=O)O)cc1', // Ibuprofen
  'CC(=O)Oc1ccccc1C(=O)O', // Aspirin
  'CN1C=NC2=C1C(=O)N(C(=O)N2C)C', // Caffeine
].join('\n')

export default function SARPredictionPage() {
  const [smilesInput, setSmilesInput] = useState('')
  const [target, setTarget] = useState('')
  const [results, setResults] = useState<any>(null)

  const predictMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await drugDesignApi.predictSAR(data)
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

    if (smilesList.length === 0) {
      return
    }

    predictMutation.mutate({
      smiles: smilesList,
      target: target || undefined,
    })
  }

  const loadExample = () => {
    setSmilesInput(exampleSMILES)
    setTarget('EGFR')
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
              <ChartBarIcon className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">SAR Prediction</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Predict structure-activity relationships for your compounds
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
          <div className="lg:col-span-1">
            <form onSubmit={handleSubmit} className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Input Molecules</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    SMILES Strings (one per line)
                  </label>
                  <textarea
                    value={smilesInput}
                    onChange={(e) => setSmilesInput(e.target.value)}
                    rows={10}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                    placeholder="Enter SMILES strings, one per line..."
                  />
                  <button
                    type="button"
                    onClick={loadExample}
                    className="mt-2 text-xs text-blue-600 hover:text-blue-700"
                  >
                    Load example molecules
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Target (optional)
                  </label>
                  <input
                    type="text"
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., EGFR, ACE2..."
                  />
                  <p className="mt-1 text-xs text-gray-500">Specify target protein (optional)</p>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <button
                    type="submit"
                    disabled={predictMutation.isPending || !smilesInput.trim()}
                    className="w-full btn-primary"
                  >
                    {predictMutation.isPending ? (
                      <>
                        <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-r-transparent mr-2"></div>
                        Predicting...
                      </>
                    ) : (
                      <>
                        <ChartBarIcon className="h-5 w-5 mr-2" />
                        Predict Activity
                      </>
                    )}
                  </button>
                </div>
              </div>

              {predictMutation.isError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">
                    {(predictMutation.error as any)?.response?.data?.detail || 'Prediction failed'}
                  </p>
                </div>
              )}
            </form>

            {/* Info Card */}
            <div className="card mt-6 bg-blue-50 border-blue-200">
              <h3 className="text-sm font-medium text-blue-900">About SAR Prediction</h3>
              <p className="mt-2 text-xs text-blue-800">
                Structure-Activity Relationship (SAR) prediction models estimate biological
                activity based on molecular structure. The model uses molecular fingerprints and
                descriptors to predict activity scores.
              </p>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {!results && !predictMutation.isPending && (
              <div className="card text-center py-12">
                <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">No predictions yet</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Enter SMILES strings and click "Predict Activity" to start
                </p>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {/* Summary */}
                <div className="card">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Prediction Results</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Molecules Analyzed</p>
                      <p className="text-2xl font-semibold text-gray-900">
                        {results.predictions?.length || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Target</p>
                      <p className="text-2xl font-semibold text-blue-600">
                        {results.target || 'General'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Predictions Table */}
                <div className="card">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Activity Predictions</h3>
                  <div className="space-y-4">
                    {results.predictions?.map((pred: any, idx: number) => (
                      <div key={idx} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center">
                              <span className="text-sm font-medium text-gray-500 mr-2">
                                #{idx + 1}
                              </span>
                              <code className="text-sm font-mono text-gray-700 bg-gray-100 px-2 py-1 rounded">
                                {pred.smiles}
                              </code>
                            </div>

                            {/* Activity Score */}
                            <div className="mt-3">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm text-gray-600">Predicted Activity</span>
                                <span className="text-lg font-semibold text-blue-600">
                                  {pred.predicted_activity?.toFixed(2) || 'N/A'}
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-blue-600 h-2 rounded-full"
                                  style={{
                                    width: `${Math.min(
                                      100,
                                      (pred.predicted_activity / 10) * 100
                                    )}%`,
                                  }}
                                ></div>
                              </div>
                            </div>

                            {/* Confidence */}
                            {pred.confidence !== undefined && (
                              <div className="mt-2">
                                <span className="text-xs text-gray-500">
                                  Confidence: {(pred.confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                            )}

                            {/* Important Features */}
                            {pred.important_features && pred.important_features.length > 0 && (
                              <div className="mt-3">
                                <p className="text-xs font-medium text-gray-700 mb-1">
                                  Key Features:
                                </p>
                                <div className="flex flex-wrap gap-1">
                                  {pred.important_features.map((feat: string, i: number) => (
                                    <span
                                      key={i}
                                      className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded"
                                    >
                                      {feat}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
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
                        'SMILES,Predicted Activity,Confidence',
                        ...results.predictions.map((p: any) =>
                          [
                            p.smiles,
                            p.predicted_activity?.toFixed(2),
                            p.confidence?.toFixed(3),
                          ].join(',')
                        ),
                      ].join('\n')

                      const blob = new Blob([csv], { type: 'text/csv' })
                      const url = window.URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'sar_predictions.csv'
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
