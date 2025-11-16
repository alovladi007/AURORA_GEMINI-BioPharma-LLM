'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import Link from 'next/link'
import { ArrowLeftIcon, ClipboardDocumentCheckIcon } from '@heroicons/react/24/outline'
import { safetyApi } from '@/lib/api'

const exampleSMILES = [
  'CC(C)Cc1ccc(C(C)C(=O)O)cc1',
  'CC(=O)Oc1ccccc1C(=O)O',
  'CN1C=NC2=C1C(=O)N(C(=O)N2C)C',
].join('\n')

export default function ADMETPage() {
  const [smilesInput, setSmilesInput] = useState('')
  const [results, setResults] = useState<any>(null)

  const predictMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await safetyApi.predictADMET(data)
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
    predictMutation.mutate({ smiles: smilesList })
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600 bg-green-50'
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
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
              <ClipboardDocumentCheckIcon className="h-8 w-8 text-red-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">ADMET Prediction</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Predict absorption, distribution, metabolism, excretion, and toxicity properties
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
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
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500 font-mono text-sm"
                    placeholder="Enter SMILES strings..."
                  />
                  <button
                    type="button"
                    onClick={() => setSmilesInput(exampleSMILES)}
                    className="mt-2 text-xs text-red-600 hover:text-red-700"
                  >
                    Load example molecules
                  </button>
                </div>
                <button
                  type="submit"
                  disabled={predictMutation.isPending || !smilesInput.trim()}
                  className="w-full btn-primary bg-red-600 hover:bg-red-700"
                >
                  {predictMutation.isPending ? 'Predicting...' : 'Predict ADMET'}
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

            <div className="card mt-6 bg-blue-50 border-blue-200">
              <h3 className="text-sm font-medium text-blue-900">ADMET Properties</h3>
              <ul className="mt-2 text-xs text-blue-800 space-y-1">
                <li><strong>Absorption:</strong> Caco-2, HIA, Bioavailability</li>
                <li><strong>Distribution:</strong> BBB, PPB, VDss</li>
                <li><strong>Metabolism:</strong> CYP3A4, CYP2D6, CYP2C9</li>
                <li><strong>Excretion:</strong> Half-life, Clearance</li>
                <li><strong>Toxicity:</strong> hERG, Hepatotoxicity, AMES</li>
              </ul>
            </div>
          </div>

          <div className="lg:col-span-2">
            {!results && !predictMutation.isPending && (
              <div className="card text-center py-12">
                <ClipboardDocumentCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">No predictions yet</h3>
                <p className="mt-2 text-sm text-gray-500">Enter SMILES and predict ADMET properties</p>
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
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        getScoreColor(pred.overall_score || 0)
                      }`}>
                        Score: {pred.overall_score?.toFixed(2)}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {/* Absorption */}
                      <div className="border border-blue-200 rounded-lg p-3 bg-blue-50">
                        <h4 className="text-sm font-medium text-blue-900 mb-2">Absorption</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span>Caco-2:</span>
                            <span className="font-medium">{pred.absorption?.Caco2?.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>HIA:</span>
                            <span className="font-medium">{pred.absorption?.HIA?.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Bioavailability:</span>
                            <span className="font-medium">{pred.absorption?.bioavailability?.toFixed(3)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Distribution */}
                      <div className="border border-green-200 rounded-lg p-3 bg-green-50">
                        <h4 className="text-sm font-medium text-green-900 mb-2">Distribution</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span>BBB:</span>
                            <span className="font-medium">{pred.distribution?.BBB?.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>PPB:</span>
                            <span className="font-medium">{pred.distribution?.PPB?.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>VDss (L/kg):</span>
                            <span className="font-medium">{pred.distribution?.VDss?.toFixed(2)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Metabolism */}
                      <div className="border border-yellow-200 rounded-lg p-3 bg-yellow-50">
                        <h4 className="text-sm font-medium text-yellow-900 mb-2">Metabolism</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span>CYP3A4:</span>
                            <span className="font-medium">{pred.metabolism?.CYP3A4_substrate?.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>CYP2D6:</span>
                            <span className="font-medium">{pred.metabolism?.CYP2D6_substrate?.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>CYP2C9:</span>
                            <span className="font-medium">{pred.metabolism?.CYP2C9_substrate?.toFixed(3)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Excretion */}
                      <div className="border border-purple-200 rounded-lg p-3 bg-purple-50">
                        <h4 className="text-sm font-medium text-purple-900 mb-2">Excretion</h4>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span>Half-life (h):</span>
                            <span className="font-medium">{pred.excretion?.half_life?.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Clearance:</span>
                            <span className="font-medium">{pred.excretion?.clearance?.toFixed(2)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Toxicity */}
                      <div className="border border-red-200 rounded-lg p-3 bg-red-50 md:col-span-2">
                        <h4 className="text-sm font-medium text-red-900 mb-2">Toxicity</h4>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div className="flex justify-between">
                            <span>hERG:</span>
                            <span className="font-medium">{pred.toxicity?.hERG?.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Hepatotox:</span>
                            <span className="font-medium">{pred.toxicity?.hepatotoxicity?.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>AMES:</span>
                            <span className="font-medium">{pred.toxicity?.AMES?.toFixed(3)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                <div className="flex justify-end">
                  <button
                    onClick={() => {
                      const csv = [
                        'SMILES,Overall Score,Caco2,HIA,Bioavailability,BBB,PPB,VDss,CYP3A4,CYP2D6,CYP2C9,Half-life,Clearance,hERG,Hepatotoxicity,AMES',
                        ...results.predictions.map((p: any) =>
                          [
                            p.smiles,
                            p.overall_score?.toFixed(3),
                            p.absorption?.Caco2?.toFixed(3),
                            p.absorption?.HIA?.toFixed(3),
                            p.absorption?.bioavailability?.toFixed(3),
                            p.distribution?.BBB?.toFixed(3),
                            p.distribution?.PPB?.toFixed(3),
                            p.distribution?.VDss?.toFixed(2),
                            p.metabolism?.CYP3A4_substrate?.toFixed(3),
                            p.metabolism?.CYP2D6_substrate?.toFixed(3),
                            p.metabolism?.CYP2C9_substrate?.toFixed(3),
                            p.excretion?.half_life?.toFixed(2),
                            p.excretion?.clearance?.toFixed(2),
                            p.toxicity?.hERG?.toFixed(3),
                            p.toxicity?.hepatotoxicity?.toFixed(3),
                            p.toxicity?.AMES?.toFixed(3),
                          ].join(',')
                        ),
                      ].join('\n')
                      const blob = new Blob([csv], { type: 'text/csv' })
                      const url = window.URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'admet_predictions.csv'
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
