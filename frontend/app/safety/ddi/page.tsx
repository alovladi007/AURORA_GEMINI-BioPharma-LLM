'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import Link from 'next/link'
import { ArrowLeftIcon, BeakerIcon } from '@heroicons/react/24/outline'
import { safetyApi } from '@/lib/api'

export default function DDIPage() {
  const [drug1, setDrug1] = useState('')
  const [drug2, setDrug2] = useState('')
  const [drugPairs, setDrugPairs] = useState<Array<{ drug1: string; drug2: string }>>([])
  const [results, setResults] = useState<any>(null)

  const predictMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await safetyApi.screenDDI(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const addPair = () => {
    if (drug1.trim() && drug2.trim()) {
      setDrugPairs([...drugPairs, { drug1: drug1.trim(), drug2: drug2.trim() }])
      setDrug1('')
      setDrug2('')
    }
  }

  const removePair = (index: number) => {
    setDrugPairs(drugPairs.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (drugPairs.length === 0) return
    predictMutation.mutate({
      drug_pairs: drugPairs.map((p) => [p.drug1, p.drug2]),
    })
  }

  const loadExample = () => {
    setDrugPairs([
      { drug1: 'CC(C)Cc1ccc(C(C)C(=O)O)cc1', drug2: 'CC(=O)Oc1ccccc1C(=O)O' },
      { drug1: 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C', drug2: 'CC(C)Cc1ccc(C(C)C(=O)O)cc1' },
    ])
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
              <BeakerIcon className="h-8 w-8 text-red-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">DDI Screening</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Screen for drug-drug interactions and contraindications
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-6">
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Add Drug Pairs</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Drug 1 SMILES
                  </label>
                  <input
                    type="text"
                    value={drug1}
                    onChange={(e) => setDrug1(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500 font-mono text-sm"
                    placeholder="Enter SMILES..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Drug 2 SMILES
                  </label>
                  <input
                    type="text"
                    value={drug2}
                    onChange={(e) => setDrug2(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500 font-mono text-sm"
                    placeholder="Enter SMILES..."
                  />
                </div>
                <button
                  type="button"
                  onClick={addPair}
                  className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium"
                >
                  Add Pair
                </button>
                <button
                  type="button"
                  onClick={loadExample}
                  className="w-full text-xs text-red-600 hover:text-red-700"
                >
                  Load example pairs
                </button>
              </div>
            </div>

            {drugPairs.length > 0 && (
              <div className="card">
                <h3 className="text-sm font-medium text-gray-900 mb-3">
                  Drug Pairs ({drugPairs.length})
                </h3>
                <div className="space-y-2">
                  {drugPairs.map((pair, idx) => (
                    <div
                      key={idx}
                      className="flex items-start justify-between p-2 bg-gray-50 rounded border border-gray-200"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-mono text-gray-600 truncate">
                          {pair.drug1}
                        </div>
                        <div className="text-xs text-gray-400">↔</div>
                        <div className="text-xs font-mono text-gray-600 truncate">
                          {pair.drug2}
                        </div>
                      </div>
                      <button
                        onClick={() => removePair(idx)}
                        className="ml-2 text-red-600 hover:text-red-700 text-xs"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
                <button
                  onClick={handleSubmit}
                  disabled={predictMutation.isPending}
                  className="w-full mt-4 btn-primary bg-red-600 hover:bg-red-700"
                >
                  {predictMutation.isPending ? 'Screening...' : 'Screen for DDI'}
                </button>
              </div>
            )}

            <div className="card bg-blue-50 border-blue-200">
              <h3 className="text-sm font-medium text-blue-900">About DDI Screening</h3>
              <p className="mt-2 text-xs text-blue-800">
                Drug-drug interactions occur when one drug affects the activity of another.
                Our model predicts potential interactions based on CYP enzyme competition,
                P-glycoprotein interactions, and pharmacokinetic similarities.
              </p>
            </div>

            {predictMutation.isError && (
              <div className="card bg-red-50 border-red-200">
                <p className="text-sm text-red-600">
                  {(predictMutation.error as any)?.response?.data?.detail || 'Screening failed'}
                </p>
              </div>
            )}
          </div>

          <div className="lg:col-span-2">
            {!results && !predictMutation.isPending && (
              <div className="card text-center py-12">
                <BeakerIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">No screening results</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Add drug pairs and click "Screen for DDI" to start
                </p>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {results.interactions?.map((interaction: any, idx: number) => (
                  <div key={idx} className="card">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-sm font-medium text-gray-900 mb-2">
                          Drug Pair #{idx + 1}
                        </h3>
                        <div className="space-y-1">
                          <div className="text-xs">
                            <span className="text-gray-500">Drug 1:</span>
                            <code className="ml-2 bg-gray-100 px-2 py-0.5 rounded font-mono">
                              {interaction.drug1_smiles}
                            </code>
                          </div>
                          <div className="text-xs">
                            <span className="text-gray-500">Drug 2:</span>
                            <code className="ml-2 bg-gray-100 px-2 py-0.5 rounded font-mono">
                              {interaction.drug2_smiles}
                            </code>
                          </div>
                        </div>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium border ${getRiskColor(
                          interaction.risk_level
                        )}`}
                      >
                        {interaction.risk_level.toUpperCase()} RISK
                      </span>
                    </div>

                    {/* Interaction Probability */}
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-600">Interaction Probability</span>
                        <span className="text-lg font-semibold text-red-600">
                          {(interaction.interaction_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full ${
                            interaction.risk_level === 'low'
                              ? 'bg-green-500'
                              : interaction.risk_level === 'moderate'
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${interaction.interaction_probability * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Mechanism */}
                    <div className="border-t pt-4 space-y-3">
                      <div>
                        <h4 className="text-xs font-medium text-gray-700 mb-1">Mechanism</h4>
                        <p className="text-sm text-gray-600">{interaction.mechanism}</p>
                      </div>

                      {/* Recommendation */}
                      <div
                        className={`p-3 rounded-lg ${
                          interaction.risk_level === 'low'
                            ? 'bg-green-50 border border-green-200'
                            : interaction.risk_level === 'moderate'
                            ? 'bg-yellow-50 border border-yellow-200'
                            : 'bg-red-50 border border-red-200'
                        }`}
                      >
                        <h4 className="text-xs font-medium text-gray-700 mb-1">
                          Clinical Recommendation
                        </h4>
                        <p className="text-sm text-gray-700">{interaction.recommendation}</p>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Summary Statistics */}
                <div className="card bg-gray-50">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Summary</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Total Pairs</p>
                      <p className="text-2xl font-semibold text-gray-900">
                        {results.interactions?.length || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">High Risk</p>
                      <p className="text-2xl font-semibold text-red-600">
                        {results.interactions?.filter((i: any) => i.risk_level === 'high').length ||
                          0}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Low Risk</p>
                      <p className="text-2xl font-semibold text-green-600">
                        {results.interactions?.filter((i: any) => i.risk_level === 'low').length ||
                          0}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={() => {
                      const csv = [
                        'Drug 1 SMILES,Drug 2 SMILES,Risk Level,Interaction Probability,Mechanism,Recommendation',
                        ...results.interactions.map((i: any) =>
                          [
                            i.drug1_smiles,
                            i.drug2_smiles,
                            i.risk_level,
                            i.interaction_probability?.toFixed(3),
                            `"${i.mechanism}"`,
                            `"${i.recommendation}"`,
                          ].join(',')
                        ),
                      ].join('\n')
                      const blob = new Blob([csv], { type: 'text/csv' })
                      const url = window.URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'ddi_screening.csv'
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
