'use client'

import Link from 'next/link'
import { useState } from 'react'
import { PlusIcon, FolderIcon } from '@heroicons/react/24/outline'

// Placeholder data - will be replaced with API calls
const mockProjects = [
  {
    id: '1',
    name: 'Oncology Project A',
    description: 'Novel kinase inhibitors for lung cancer',
    created_at: '2024-01-15',
    status: 'active',
  },
]

export default function ProjectsPage() {
  const [projects] = useState(mockProjects)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
              <p className="mt-1 text-sm text-gray-600">
                Manage your pharmaceutical research projects
              </p>
            </div>
            <Link href="/projects/new" className="btn-primary">
              <PlusIcon className="mr-2 h-5 w-5" />
              New Project
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {projects.length === 0 ? (
          <div className="text-center">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-semibold text-gray-900">No projects</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating a new project.
            </p>
            <div className="mt-6">
              <Link href="/projects/new" className="btn-primary">
                <PlusIcon className="mr-2 h-5 w-5" />
                New Project
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className="card group hover:shadow-lg hover:ring-2 hover:ring-primary-500"
              >
                <div className="flex items-start justify-between">
                  <FolderIcon className="h-8 w-8 text-primary-600" />
                  <span className={`badge-${project.status === 'active' ? 'success' : 'warning'}`}>
                    {project.status}
                  </span>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900 group-hover:text-primary-700">
                  {project.name}
                </h3>
                <p className="mt-2 text-sm text-gray-600">{project.description}</p>
                <p className="mt-4 text-xs text-gray-500">
                  Created: {new Date(project.created_at).toLocaleDateString()}
                </p>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
