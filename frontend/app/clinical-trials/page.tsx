'use client'

import Link from 'next/link'
import { UserGroupIcon, UsersIcon, ShieldExclamationIcon, ChartLineIcon } from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Patient Recruitment',
    description: 'Intelligent patient stratification and enrollment optimization',
    icon: UsersIcon,
    href: '/clinical-trials/recruitment',
  },
  {
    name: 'Trial Design',
    description: 'AI-assisted trial design with power analysis and sample size calculation',
    icon: ChartLineIcon,
    href: '/clinical-trials/design',
  },
  {
    name: 'Safety Monitoring',
    description: 'Real-time adverse event monitoring and safety signal detection',
    icon: ShieldExclamationIcon,
    href: '/clinical-trials/safety',
  },
]

export default function ClinicalTrialsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <UserGroupIcon className="h-8 w-8 text-green-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Clinical Trial Optimization</h1>
              <p className="mt-1 text-sm text-gray-600">
                Intelligent patient recruitment, trial design, and safety monitoring
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Introduction */}
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900">Welcome to Clinical Trial Optimization</h2>
          <p className="mt-2 text-gray-600">
            Optimize every aspect of your clinical trials with AI-powered tools for patient
            recruitment, trial design, real-time safety monitoring, and predictive endpoint
            analysis. Make data-driven decisions to improve trial success rates.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <Link
              key={feature.name}
              href={feature.href}
              className="card group hover:shadow-lg hover:ring-2 hover:ring-green-500"
            >
              <feature.icon className="h-8 w-8 text-green-600" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900 group-hover:text-green-700">
                {feature.name}
              </h3>
              <p className="mt-2 text-sm text-gray-600">{feature.description}</p>
              <div className="mt-4 flex items-center text-sm font-medium text-green-600">
                Get started
                <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>

        {/* Capabilities */}
        <div className="mt-8 card">
          <h3 className="text-lg font-semibold text-gray-900">Key Capabilities</h3>
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="rounded-lg bg-green-50 p-4">
              <h4 className="font-medium text-green-900">Patient Stratification</h4>
              <p className="mt-1 text-sm text-green-700">
                Automatically identify and stratify patients based on demographics, biomarkers, and
                risk factors
              </p>
            </div>
            <div className="rounded-lg bg-green-50 p-4">
              <h4 className="font-medium text-green-900">Adaptive Design</h4>
              <p className="mt-1 text-sm text-green-700">
                Receive recommendations for arm expansion, dropping, or dose modifications based on
                interim results
              </p>
            </div>
            <div className="rounded-lg bg-green-50 p-4">
              <h4 className="font-medium text-green-900">Event Prediction</h4>
              <p className="mt-1 text-sm text-green-700">
                Predict time-to-event outcomes using survival analysis and ML models
              </p>
            </div>
            <div className="rounded-lg bg-green-50 p-4">
              <h4 className="font-medium text-green-900">Safety Signals</h4>
              <p className="mt-1 text-sm text-green-700">
                Detect adverse events and safety signals in real-time with automated alerts
              </p>
            </div>
          </div>
        </div>

        {/* Placeholder Notice */}
        <div className="mt-8 rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
          <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">Module Under Development</h3>
          <p className="mt-1 text-sm text-gray-500">
            The Clinical Trial Optimization module is currently being built. Check back soon for full functionality.
          </p>
          <Link href="/" className="mt-4 btn-primary inline-flex">
            Back to Home
          </Link>
        </div>
      </main>
    </div>
  )
}
