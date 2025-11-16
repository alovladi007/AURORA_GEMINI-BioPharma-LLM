'use client'

import Link from 'next/link'
import {
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ClipboardDocumentCheckIcon,
  BeakerIcon,
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'ADMET Prediction',
    description: 'Predict absorption, distribution, metabolism, excretion, and toxicity properties',
    icon: ClipboardDocumentCheckIcon,
    href: '/safety/admet',
  },
  {
    name: 'Toxicity Modeling',
    description: 'Assess organ-specific toxicity risks and safety liabilities',
    icon: ExclamationTriangleIcon,
    href: '/safety/toxicity',
  },
  {
    name: 'DDI Screening',
    description: 'Screen for potential drug-drug interactions and contraindications',
    icon: BeakerIcon,
    href: '/safety/ddi',
  },
]

const admetProperties = [
  { name: 'Absorption', description: 'Oral bioavailability, permeability', color: 'blue' },
  { name: 'Distribution', description: 'Blood-brain barrier, protein binding', color: 'green' },
  { name: 'Metabolism', description: 'CYP450 interactions, metabolic stability', color: 'yellow' },
  { name: 'Excretion', description: 'Clearance, half-life', color: 'purple' },
  { name: 'Toxicity', description: 'Hepatotoxicity, cardiotoxicity, etc.', color: 'red' },
]

export default function SafetyPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <ShieldCheckIcon className="h-8 w-8 text-red-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Safety & Toxicity Prediction</h1>
              <p className="mt-1 text-sm text-gray-600">
                ADMET prediction, toxicity modeling, and drug-drug interaction screening
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Introduction */}
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900">Welcome to Safety & Toxicity Prediction</h2>
          <p className="mt-2 text-gray-600">
            Assess drug safety and identify potential toxicity liabilities early in the development
            process. Our AI models predict ADMET properties, organ-specific toxicity, drug-drug
            interactions, and genotoxicity risks to help prioritize safer candidates.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <Link
              key={feature.name}
              href={feature.href}
              className="card group hover:shadow-lg hover:ring-2 hover:ring-red-500"
            >
              <feature.icon className="h-8 w-8 text-red-600" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900 group-hover:text-red-700">
                {feature.name}
              </h3>
              <p className="mt-2 text-sm text-gray-600">{feature.description}</p>
              <div className="mt-4 flex items-center text-sm font-medium text-red-600">
                Get started
                <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>

        {/* ADMET Properties */}
        <div className="mt-8 card">
          <h3 className="text-lg font-semibold text-gray-900">ADMET Properties Covered</h3>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {admetProperties.map((property) => (
              <div
                key={property.name}
                className={`rounded-lg bg-${property.color}-50 p-4 border border-${property.color}-200`}
              >
                <h4 className={`font-medium text-${property.color}-900`}>{property.name}</h4>
                <p className={`mt-1 text-xs text-${property.color}-700`}>{property.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Toxicity Endpoints */}
        <div className="mt-8 card">
          <h3 className="text-lg font-semibold text-gray-900">Toxicity Endpoints</h3>
          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="flex items-start gap-3 rounded-lg bg-gray-50 p-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-gray-900">Hepatotoxicity</h4>
                <p className="text-xs text-gray-600">Liver damage and dysfunction</p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-lg bg-gray-50 p-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-gray-900">Cardiotoxicity</h4>
                <p className="text-xs text-gray-600">Heart-related adverse effects (hERG, QT)</p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-lg bg-gray-50 p-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-gray-900">Nephrotoxicity</h4>
                <p className="text-xs text-gray-600">Kidney damage and impairment</p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-lg bg-gray-50 p-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-gray-900">Genotoxicity</h4>
                <p className="text-xs text-gray-600">DNA damage and mutagenicity</p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-lg bg-gray-50 p-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-gray-900">Carcinogenicity</h4>
                <p className="text-xs text-gray-600">Cancer-causing potential</p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-lg bg-gray-50 p-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-gray-900">Skin Sensitization</h4>
                <p className="text-xs text-gray-600">Allergic reactions and dermatitis</p>
              </div>
            </div>
          </div>
        </div>

        {/* Safety Alert Example */}
        <div className="mt-8 card border-2 border-red-200 bg-red-50">
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className="h-6 w-6 text-red-600 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-red-900">Example Safety Alert</h3>
              <p className="mt-2 text-sm text-red-700">
                High hepatotoxicity risk detected (score: 0.85). Compound shows structural
                alerts for liver damage. Recommended: prioritize alternative scaffolds or
                implement additional safety studies.
              </p>
              <div className="mt-4 flex gap-2">
                <span className="badge bg-red-200 text-red-800">High Risk</span>
                <span className="badge bg-red-200 text-red-800">Hepatotoxicity</span>
                <span className="badge bg-red-200 text-red-800">Structural Alert</span>
              </div>
            </div>
          </div>
        </div>

        {/* Placeholder Notice */}
        <div className="mt-8 rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
          <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">Module Under Development</h3>
          <p className="mt-1 text-sm text-gray-500">
            The Safety & Toxicity Prediction module is currently being built. Check back soon for full functionality.
          </p>
          <Link href="/" className="mt-4 btn-primary inline-flex">
            Back to Home
          </Link>
        </div>
      </main>
    </div>
  )
}
