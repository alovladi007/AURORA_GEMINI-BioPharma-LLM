'use client'

import { useState } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Navbar } from '@/components/Navbar'
import { MoleculeViewer } from '@/components/MoleculeViewer'

const EXAMPLES: { name: string; smiles: string }[] = [
  { name: 'Aspirin', smiles: 'CC(=O)OC1=CC=CC=C1C(=O)O' },
  { name: 'Ibuprofen', smiles: 'CC(C)CC1=CC=C(C=C1)C(C)C(=O)O' },
  { name: 'Caffeine', smiles: 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C' },
  { name: 'Imatinib', smiles: 'CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5' },
]

function MoleculeViewerInner() {
  const [input, setInput] = useState('CC(=O)OC1=CC=CC=C1C(=O)O')
  const [active, setActive] = useState('CC(=O)OC1=CC=CC=C1C(=O)O')

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-4xl px-4 py-10">
        <h1 className="text-2xl font-bold text-gray-900">Molecule Viewer</h1>
        <p className="mt-1 text-sm text-gray-500">
          Render any molecule from SMILES with RDKit-computed properties and a
          Lipinski rule-of-five summary.
        </p>

        <div className="mt-6 flex flex-col gap-2 sm:flex-row">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && setActive(input)}
            placeholder="Enter SMILES…"
            className="flex-1 rounded-md border border-gray-300 px-3 py-2 font-mono text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            onClick={() => setActive(input)}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Render
          </button>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex.name}
              onClick={() => {
                setInput(ex.smiles)
                setActive(ex.smiles)
              }}
              className="rounded-full border border-gray-300 bg-white px-3 py-1 text-xs text-gray-600 hover:border-blue-400 hover:text-blue-700"
            >
              {ex.name}
            </button>
          ))}
        </div>

        <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <MoleculeViewer smiles={active} width={380} height={320} />
        </div>
      </main>
    </div>
  )
}

export default function MoleculeViewerPage() {
  return (
    <ProtectedRoute>
      <MoleculeViewerInner />
    </ProtectedRoute>
  )
}
