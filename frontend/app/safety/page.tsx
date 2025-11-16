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
    status: 'available',
  },
  {
    name: 'Toxicity Modeling',
    description: 'Assess organ-specific toxicity risks and safety liabilities',
    icon: ExclamationTriangleIcon,
    href: '/safety/toxicity',
    status: 'available',
  },
  {
    name: 'DDI Screening',
    description: 'Screen for potential drug-drug interactions and contraindications',
    icon: BeakerIcon,
    href: '/safety/ddi',
    status: 'available',
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
              className="card group hover:shadow-lg hover:ring-2 hover:ring-red-500 transition-all"
            >
              <div className="flex items-center justify-between mb-4">
                <feature.icon className="h-8 w-8 text-red-600" />
                <span className="badge badge-success text-xs">Available</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 group-hover:text-red-700">
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
                className="rounded-lg bg-blue-50 border border-blue-200 p-4"
              >
                <h4 className="font-medium text-blue-900">{property.name}</h4>
                <p className="mt-1 text-xs text-blue-700">{property.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Toxicity Endpoints */}
        <div className="mt-8 card">
          <h3 className="text-lg font-semibold text-gray-900">Toxicity Endpoints</h3>
          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
            {[
              {name: 'Hepatotoxicity', desc: 'Liver damage and dysfunction'},
              {name: 'Cardiotoxicity', desc: 'Heart-related adverse effects (hERG, QT)'},
              {name: 'Nephrotoxicity', desc: 'Kidney damage and impairment'},
              {name: 'Neurotoxicity', desc: 'Neurological and CNS effects'},
              {name: 'Genotoxicity', desc: 'DNA damage and mutagenicity'},
              {name: 'Carcinogenicity', desc: 'Cancer-causing potential'},
              {name: 'Skin Sensitization', desc: 'Allergic reactions and dermatitis'},
            ].map((endpoint) => (
              <div key={endpoint.name} className="flex items-start gap-3 rounded-lg bg-gray-50 p-3">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-medium text-gray-900">{endpoint.name}</h4>
                  <p className="text-xs text-gray-600">{endpoint.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Key Features */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900">Comprehensive Predictions</h3>
            <p className="mt-2 text-sm text-gray-600">
              Get predictions for 20+ ADMET properties and 7 major toxicity endpoints including
              hepatotoxicity, cardiotoxicity, and genotoxicity.
            </p>
          </div>
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900">Structural Alerts</h3>
            <p className="mt-2 text-sm text-gray-600">
              Identify potentially problematic molecular substructures that may cause safety
              concerns before synthesis.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
