import Link from 'next/link'
import {
  BeakerIcon,
  UserGroupIcon,
  ArrowPathIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'

const modules = [
  {
    name: 'AI Drug Design',
    description:
      'De novo molecular generation, SAR prediction, lead optimization, and multi-parameter optimization for discovering novel drug candidates.',
    icon: BeakerIcon,
    href: '/drug-design',
    color: 'bg-blue-500',
    features: [
      'De novo molecular generation',
      'Structure-Activity Relationship (SAR) prediction',
      'Lead optimization & scaffold hopping',
      'Multi-parameter optimization (MPO)',
    ],
  },
  {
    name: 'Clinical Trial Optimization',
    description:
      'Intelligent patient recruitment, trial design assistance, real-time safety monitoring, and adaptive trial recommendations.',
    icon: UserGroupIcon,
    href: '/clinical-trials',
    color: 'bg-green-500',
    features: [
      'Intelligent patient recruitment',
      'AI-assisted trial design',
      'Real-time safety monitoring',
      'Predictive endpoint analysis',
    ],
  },
  {
    name: 'Drug Repurposing',
    description:
      'Knowledge-graph mining for new indications, network-based mechanism prediction, and real-world evidence analysis.',
    icon: ArrowPathIcon,
    href: '/repurposing',
    color: 'bg-purple-500',
    features: [
      'Knowledge-graph mining',
      'Network-based mechanism prediction',
      'Real-world evidence analysis',
      'Combination therapy discovery',
    ],
  },
  {
    name: 'Safety & Toxicity Prediction',
    description:
      'ADMET property prediction, organ-specific toxicity modeling, drug-drug interaction screening, and genotoxicity alerts.',
    icon: ShieldCheckIcon,
    href: '/safety',
    color: 'bg-red-500',
    features: [
      'ADMET property prediction',
      'Organ-specific toxicity modeling',
      'Drug-drug interaction (DDI) screening',
      'Genotoxicity & carcinogenicity alerts',
    ],
  },
]

const stats = [
  { name: 'Models Trained', value: '12+', icon: CpuChipIcon },
  { name: 'Active Projects', value: '0', icon: ChartBarIcon },
  { name: 'Predictions Made', value: '0', icon: BeakerIcon },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">
                Pharma AI Platform
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Production-ready AI for pharmaceutical research and drug development
              </p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/projects"
                className="btn-secondary"
              >
                View Projects
              </Link>
              <Link
                href="/projects/new"
                className="btn-primary"
              >
                Create Project
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
              Accelerate Drug Discovery with AI
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
              A comprehensive platform supporting researchers through all key stages of drug
              development, from molecular design to clinical trials, with the rigor of modern ML
              engineering.
            </p>
          </div>

          {/* Stats */}
          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-3">
            {stats.map((stat) => (
              <div key={stat.name} className="card text-center">
                <stat.icon className="mx-auto h-8 w-8 text-primary-600" />
                <p className="mt-3 text-3xl font-bold text-gray-900">{stat.value}</p>
                <p className="mt-1 text-sm text-gray-600">{stat.name}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Core Modules */}
        <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Core Modules</h2>
            <p className="mt-2 text-gray-600">
              Four integrated AI-driven modules to accelerate pharmaceutical R&D
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            {modules.map((module) => (
              <Link
                key={module.name}
                href={module.href}
                className="card group transition-all hover:shadow-lg hover:ring-2 hover:ring-primary-500"
              >
                <div className="flex items-start gap-4">
                  <div className={`rounded-lg ${module.color} p-3`}>
                    <module.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 group-hover:text-primary-700">
                      {module.name}
                    </h3>
                    <p className="mt-2 text-sm text-gray-600">{module.description}</p>

                    <ul className="mt-4 space-y-2">
                      {module.features.map((feature) => (
                        <li key={feature} className="flex items-center text-sm text-gray-700">
                          <svg
                            className="mr-2 h-4 w-4 text-green-500"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                          {feature}
                        </li>
                      ))}
                    </ul>

                    <div className="mt-4 flex items-center text-sm font-medium text-primary-600 group-hover:text-primary-700">
                      Explore module
                      <svg
                        className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Tech Stack */}
        <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="card bg-gradient-to-r from-primary-600 to-purple-600 text-white">
            <h2 className="text-2xl font-bold">Built with Modern Tech Stack</h2>
            <div className="mt-6 grid grid-cols-2 gap-8 md:grid-cols-4">
              <div>
                <h3 className="font-semibold">Frontend</h3>
                <ul className="mt-2 space-y-1 text-sm text-primary-100">
                  <li>Next.js 14</li>
                  <li>React 18</li>
                  <li>TypeScript</li>
                  <li>Tailwind CSS</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold">Backend</h3>
                <ul className="mt-2 space-y-1 text-sm text-primary-100">
                  <li>FastAPI</li>
                  <li>PostgreSQL</li>
                  <li>Redis</li>
                  <li>Celery</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold">ML/AI</h3>
                <ul className="mt-2 space-y-1 text-sm text-primary-100">
                  <li>PyTorch</li>
                  <li>RDKit</li>
                  <li>scikit-learn</li>
                  <li>NetworkX</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold">DevOps</h3>
                <ul className="mt-2 space-y-1 text-sm text-primary-100">
                  <li>Docker</li>
                  <li>Docker Compose</li>
                  <li>Pytest</li>
                  <li>Jest</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Disclaimer */}
        <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="rounded-lg border-2 border-warning-300 bg-warning-50 p-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <ShieldCheckIcon className="h-6 w-6 text-warning-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-warning-800">Research Use Only</h3>
                <div className="mt-2 text-sm text-warning-700">
                  <p>
                    This platform is designed for computational research and decision support. It
                    does <strong>NOT</strong> provide wet-lab experimental protocols, replace
                    regulatory-grade clinical trial design, or offer medical advice. All
                    predictions must be validated through appropriate experimental and regulatory
                    processes.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Pharma AI Platform v0.1.0 - Built for the pharmaceutical research community
            </p>
            <div className="flex gap-4">
              <Link href="/docs" className="text-sm text-gray-600 hover:text-gray-900">
                Documentation
              </Link>
              <Link href="/api/docs" className="text-sm text-gray-600 hover:text-gray-900">
                API Reference
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
