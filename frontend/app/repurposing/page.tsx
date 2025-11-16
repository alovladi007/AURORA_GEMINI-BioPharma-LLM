'use client'

import Link from 'next/link'
import { ArrowPathIcon, ShareIcon, MagnifyingGlassIcon, BeakerIcon } from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Knowledge Graph Mining',
    description: 'Explore drug-disease-target networks to discover new indications',
    icon: ShareIcon,
    href: '/repurposing/knowledge-graph',
  },
  {
    name: 'Mechanism Prediction',
    description: 'Predict mechanisms of action using network-based approaches',
    icon: MagnifyingGlassIcon,
    href: '/repurposing/mechanism',
  },
  {
    name: 'Combination Discovery',
    description: 'Identify synergistic drug combinations for improved efficacy',
    icon: BeakerIcon,
    href: '/repurposing/combinations',
  },
]

export default function RepurposingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <ArrowPathIcon className="h-8 w-8 text-purple-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Drug Repurposing</h1>
              <p className="mt-1 text-sm text-gray-600">
                Knowledge-graph mining and network-based discovery of new indications
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Introduction */}
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900">Welcome to Drug Repurposing</h2>
          <p className="mt-2 text-gray-600">
            Discover new therapeutic uses for existing drugs using AI-powered knowledge graph
            analysis, network-based mechanism prediction, and real-world evidence. Accelerate drug
            development by leveraging existing safety and efficacy data.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <Link
              key={feature.name}
              href={feature.href}
              className="card group hover:shadow-lg hover:ring-2 hover:ring-purple-500"
            >
              <feature.icon className="h-8 w-8 text-purple-600" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900 group-hover:text-purple-700">
                {feature.name}
              </h3>
              <p className="mt-2 text-sm text-gray-600">{feature.description}</p>
              <div className="mt-4 flex items-center text-sm font-medium text-purple-600">
                Get started
                <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>

        {/* Use Cases */}
        <div className="mt-8 card">
          <h3 className="text-lg font-semibold text-gray-900">Repurposing Use Cases</h3>
          <div className="mt-4 space-y-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100">
                  <span className="text-sm font-semibold text-purple-600">1</span>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Find New Indications</h4>
                <p className="mt-1 text-sm text-gray-600">
                  Query the knowledge graph to find potential new therapeutic applications for
                  approved drugs based on shared mechanisms and targets
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100">
                  <span className="text-sm font-semibold text-purple-600">2</span>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Analyze Real-World Evidence</h4>
                <p className="mt-1 text-sm text-gray-600">
                  Use synthetic claims and EHR data to identify associations between drug exposure
                  and clinical outcomes
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100">
                  <span className="text-sm font-semibold text-purple-600">3</span>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Discover Combinations</h4>
                <p className="mt-1 text-sm text-gray-600">
                  Identify drug pairs with potential synergistic effects for combination therapy
                  development
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Graph Visualization Preview */}
        <div className="mt-8 card bg-purple-50 border-purple-200">
          <h3 className="text-lg font-semibold text-purple-900">Interactive Network Visualization</h3>
          <p className="mt-2 text-sm text-purple-700">
            Explore drug-disease-target relationships through interactive graph visualizations.
            Navigate shortest paths, identify key hubs, and discover hidden connections.
          </p>
          <div className="mt-4 rounded-lg border-2 border-dashed border-purple-300 bg-white p-8 text-center">
            <ShareIcon className="mx-auto h-12 w-12 text-purple-400" />
            <p className="mt-2 text-sm text-purple-600">Graph visualization coming soon</p>
          </div>
        </div>

        {/* Placeholder Notice */}
        <div className="mt-8 rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
          <ArrowPathIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">Module Under Development</h3>
          <p className="mt-1 text-sm text-gray-500">
            The Drug Repurposing module is currently being built. Check back soon for full functionality.
          </p>
          <Link href="/" className="mt-4 btn-primary inline-flex">
            Back to Home
          </Link>
        </div>
      </main>
    </div>
  )
}
