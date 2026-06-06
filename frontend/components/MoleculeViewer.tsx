'use client'

/**
 * MoleculeViewer — renders a 2D depiction (server-side RDKit SVG) for a SMILES
 * string along with key descriptors and a Lipinski rule-of-five summary.
 */

import { useQuery } from '@tanstack/react-query'
import { visualizationApi, getErrorMessage } from '@/lib/api'

interface MoleculeViewerProps {
  smiles: string
  width?: number
  height?: number
  showProperties?: boolean
}

const KEY_DESCRIPTORS: { key: string; label: string; digits?: number }[] = [
  { key: 'molecular_weight', label: 'MW', digits: 1 },
  { key: 'logp', label: 'LogP', digits: 2 },
  { key: 'tpsa', label: 'TPSA', digits: 1 },
  { key: 'num_h_donors', label: 'HBD' },
  { key: 'num_h_acceptors', label: 'HBA' },
  { key: 'num_rotatable_bonds', label: 'RotB' },
  { key: 'num_aromatic_rings', label: 'ArRings' },
]

export function MoleculeViewer({
  smiles,
  width = 350,
  height = 300,
  showProperties = true,
}: MoleculeViewerProps) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['molecule', smiles, width, height],
    queryFn: async () => (await visualizationApi.molecule(smiles, width, height)).data,
    enabled: smiles.trim().length > 0,
  })

  if (!smiles.trim()) {
    return <div className="text-sm text-gray-400">Enter a SMILES string to preview.</div>
  }

  if (isLoading) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-gray-200 bg-gray-50"
        style={{ width, height }}
      >
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
        {getErrorMessage(error)}
      </div>
    )
  }

  if (!data || !data.valid) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700">
        Invalid SMILES: <code className="font-mono">{smiles}</code>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start">
      <div
        className="rounded-lg border border-gray-200 bg-white"
        style={{ width, height }}
        // SVG is generated server-side by RDKit (trusted source).
        dangerouslySetInnerHTML={{ __html: data.svg ?? '' }}
      />

      {showProperties && data.descriptors && (
        <div className="min-w-[180px] space-y-3">
          <div>
            <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
              Properties
            </h4>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
              {KEY_DESCRIPTORS.map(({ key, label, digits }) => {
                const value = data.descriptors?.[key]
                if (value === undefined) return null
                return (
                  <div key={key} className="flex justify-between gap-2">
                    <dt className="text-gray-500">{label}</dt>
                    <dd className="font-medium text-gray-900">
                      {digits !== undefined ? value.toFixed(digits) : value}
                    </dd>
                  </div>
                )
              })}
            </dl>
          </div>

          {data.lipinski && (
            <div>
              <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
                Rule of Five
              </h4>
              <span
                className={
                  'inline-block rounded px-2 py-0.5 text-xs font-medium ' +
                  (data.lipinski.drug_like
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800')
                }
              >
                {data.lipinski.drug_like ? 'Drug-like' : 'Non-drug-like'} ·{' '}
                {data.lipinski.violations} violation
                {data.lipinski.violations === 1 ? '' : 's'}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
