'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import Link from 'next/link'
import { ArrowLeftIcon, SparklesIcon } from '@heroicons/react/24/outline'
import { drugDesignApi } from '@/lib/api'

export default function GeneratePage() {
  const [numMolecules, setNumMolecules] = useState(20)
  const [results, setResults] = useState<any>(null)

  const generateMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await drugDesignApi.generate(data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    generateMutation.mutate({ num_molecules: numMolecules })
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
              <SparklesIcon className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Molecule Generation</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Generate novel molecular structures using AI
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
              <h2 className="text-lg font-medium text-gray-900 mb-4">Generation Parameters</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Molecules
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={numMolecules}
                    onChange={(e) => setNumMolecules(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="mt-1 text-xs text-gray-500">Generate 1-100 molecules</p>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <button
                    type="submit"
                    disabled={generateMutation.isPending}
                    className="w-full btn-primary"
                  >
                    {generateMutation.isPending ? (
                      <>
                        <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-r-transparent mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      <>
                        <SparklesIcon className="h-5 w-5 mr-2" />
                        Generate Molecules
                      </>
                    )}
                  </button>
                </div>
              </div>

              {generateMutation.isError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">
                    {(generateMutation.error as any)?.response?.data?.detail || 'Generation failed'}
                  </p>
                </div>
              )}
            </form>

            {/* Info Card */}
            <div className="card mt-6 bg-blue-50 border-blue-200">
              <h3 className="text-sm font-medium text-blue-900">About this Tool</h3>
              <p className="mt-2 text-xs text-blue-800">
                This tool generates novel molecular structures using baseline random generation.
                In production, this would use advanced generative models like VAE, GAN, or
                Transformer-based architectures.
              </p>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {!results && !generateMutation.isPending && (
              <div className="card text-center py-12">
                <SparklesIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">No molecules generated yet</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Set parameters and click "Generate Molecules" to start
                </p>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {/* Summary */}
                <div className="card">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Generation Results</h2>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Total Generated</p>
                      <p className="text-2xl font-semibold text-gray-900">
                        {results.total_generated}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Valid Molecules</p>
                      <p className="text-2xl font-semibold text-green-600">
                        {results.valid_count}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Generation Time</p>
                      <p className="text-2xl font-semibold text-blue-600">
                        {results.generation_time?.toFixed(2)}s
                      </p>
                    </div>
                  </div>
                </div>

                {/* Molecules Table */}
                <div className="card">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Generated Molecules</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            #
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            SMILES
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Activity
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            MW
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            LogP
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            HBD
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            HBA
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {results.molecules?.map((mol: any, idx: number) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm text-gray-900">{idx + 1}</td>
                            <td className="px-4 py-3 text-sm font-mono text-gray-600 max-w-xs truncate">
                              {mol.smiles}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {mol.predicted_activity?.toFixed(2) || 'N/A'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {mol.predicted_properties?.MW?.toFixed(1) || 'N/A'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {mol.predicted_properties?.LogP?.toFixed(2) || 'N/A'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {mol.predicted_properties?.HBD || 'N/A'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {mol.predicted_properties?.HBA || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Export Button */}
                <div className="flex justify-end">
                  <button
                    onClick={() => {
                      const csv = [
                        'SMILES,Activity,MW,LogP,HBD,HBA,TPSA',
                        ...results.molecules.map((m: any) =>
                          [
                            m.smiles,
                            m.predicted_activity?.toFixed(2),
                            m.predicted_properties?.MW?.toFixed(1),
                            m.predicted_properties?.LogP?.toFixed(2),
                            m.predicted_properties?.HBD,
                            m.predicted_properties?.HBA,
                            m.predicted_properties?.TPSA?.toFixed(1),
                          ].join(',')
                        ),
                      ].join('\n')

                      const blob = new Blob([csv], { type: 'text/csv' })
                      const url = window.URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'generated_molecules.csv'
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
