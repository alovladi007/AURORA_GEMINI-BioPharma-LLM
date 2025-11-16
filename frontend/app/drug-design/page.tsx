'use client'

import Link from 'next/link'
import { BeakerIcon, SparklesIcon, ChartBarIcon, CogIcon } from '@heroicons/react/24/outline'

const features = [
  {
    name: 'De Novo Generation',
    description: 'Generate novel molecular structures using AI-powered generative models',
    icon: SparklesIcon,
    href: '/drug-design/generate',
  },
  {
    name: 'SAR Prediction',
    description: 'Predict structure-activity relationships for your compounds',
    icon: ChartBarIcon,
    href: '/drug-design/sar',
  },
  {
    name: 'Lead Optimization',
    description: 'Optimize lead compounds for better drug-like properties',
    icon: CogIcon,
    href: '/drug-design/optimize',
  },
]

export default function DrugDesignPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <BeakerIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI Drug Design</h1>
              <p className="mt-1 text-sm text-gray-600">
                De novo molecular generation, SAR prediction, and lead optimization
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Introduction */}
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900">Welcome to AI Drug Design</h2>
          <p className="mt-2 text-gray-600">
            Design and optimize novel drug candidates using state-of-the-art machine learning
            models. Our platform provides tools for molecular generation, structure-activity
            relationship prediction, and multi-parameter optimization.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <Link
              key={feature.name}
              href={feature.href}
              className="card group hover:shadow-lg hover:ring-2 hover:ring-blue-500"
            >
              <feature.icon className="h-8 w-8 text-blue-600" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900 group-hover:text-blue-700">
                {feature.name}
              </h3>
              <p className="mt-2 text-sm text-gray-600">{feature.description}</p>
              <div className="mt-4 flex items-center text-sm font-medium text-blue-600">
                Get started
                <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>

        {/* Quick Start */}
        <div className="mt-8 card bg-blue-50 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900">Quick Start</h3>
          <ol className="mt-4 space-y-2 text-sm text-blue-800">
            <li className="flex items-start">
              <span className="mr-2 font-semibold">1.</span>
              <span>Upload your molecular dataset or use example data</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 font-semibold">2.</span>
              <span>Select a model (generation, prediction, or optimization)</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 font-semibold">3.</span>
              <span>Configure parameters and run the analysis</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 font-semibold">4.</span>
              <span>Review results and export candidates</span>
            </li>
          </ol>
        </div>

        {/* Placeholder Notice */}
        <div className="mt-8 rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
          <BeakerIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">Module Under Development</h3>
          <p className="mt-1 text-sm text-gray-500">
            The AI Drug Design module is currently being built. Check back soon for full functionality.
          </p>
          <Link href="/" className="mt-4 btn-primary inline-flex">
            Back to Home
          </Link>
        </div>
      </main>
    </div>
  )
}
