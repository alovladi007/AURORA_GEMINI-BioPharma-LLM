'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import {
  ArrowLeftIcon,
  BeakerIcon,
  CircleStackIcon,
  CubeIcon,
  ClockIcon,
  BriefcaseIcon,
} from '@heroicons/react/24/outline'
import { projectsApi, datasetApi, modelApi, experimentApi, jobApi } from '@/lib/api'

type Tab = 'overview' | 'datasets' | 'models' | 'experiments' | 'jobs'

export default function ProjectDetailPage() {
  const params = useParams()
  const projectId = parseInt(params.id as string)
  const [activeTab, setActiveTab] = useState<Tab>('overview')

  // Fetch project with counts
  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const response = await projectsApi.get(projectId.toString())
      return response.data
    },
  })

  // Fetch summaries
  const { data: datasets } = useQuery({
    queryKey: ['datasets', 'summary', projectId],
    queryFn: async () => {
      const response = await datasetApi.summary({ project_id: projectId })
      return response.data
    },
    enabled: activeTab === 'datasets' || activeTab === 'overview',
  })

  const { data: models } = useQuery({
    queryKey: ['models', 'summary', projectId],
    queryFn: async () => {
      const response = await modelApi.summary({ project_id: projectId })
      return response.data
    },
    enabled: activeTab === 'models' || activeTab === 'overview',
  })

  const { data: experiments } = useQuery({
    queryKey: ['experiments', 'summary', projectId],
    queryFn: async () => {
      const response = await experimentApi.summary({ project_id: projectId })
      return response.data
    },
    enabled: activeTab === 'experiments' || activeTab === 'overview',
  })

  const { data: jobs } = useQuery({
    queryKey: ['jobs', 'summary', projectId],
    queryFn: async () => {
      const response = await jobApi.summary({ project_id: projectId })
      return response.data
    },
    enabled: activeTab === 'jobs' || activeTab === 'overview',
  })

  if (projectLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Project not found</p>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'overview' as Tab, name: 'Overview', icon: BeakerIcon },
    { id: 'datasets' as Tab, name: 'Datasets', icon: CircleStackIcon, count: datasets?.length },
    { id: 'models' as Tab, name: 'Models', icon: CubeIcon, count: models?.length },
    { id: 'experiments' as Tab, name: 'Experiments', icon: ClockIcon, count: experiments?.length },
    { id: 'jobs' as Tab, name: 'Jobs', icon: BriefcaseIcon, count: jobs?.length },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center">
            <Link
              href="/projects"
              className="text-gray-500 hover:text-gray-700 mr-4"
            >
              <ArrowLeftIcon className="h-5 w-5" />
            </Link>
            <div className="flex-1">
              <div className="flex items-center">
                <BeakerIcon className="h-8 w-8 text-blue-600 mr-3" />
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
                  <div className="mt-1 flex items-center space-x-3">
                    <span
                      className={`badge ${
                        project.status === 'active'
                          ? 'badge-success'
                          : project.status === 'completed'
                          ? 'badge-info'
                          : 'badge-secondary'
                      }`}
                    >
                      {project.status}
                    </span>
                    <span className="text-sm text-gray-500">
                      Created {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              {project.description && (
                <p className="mt-3 text-sm text-gray-600">{project.description}</p>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors
                      ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5 mr-2" />
                    {tab.name}
                    {tab.count !== undefined && (
                      <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                        {tab.count}
                      </span>
                    )}
                  </button>
                )
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <div className="card">
                <div className="flex items-center">
                  <CircleStackIcon className="h-8 w-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Datasets</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {datasets?.length || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center">
                  <CubeIcon className="h-8 w-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Models</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {models?.length || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center">
                  <ClockIcon className="h-8 w-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Experiments</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {experiments?.length || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center">
                  <BriefcaseIcon className="h-8 w-8 text-orange-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Jobs</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {jobs?.length || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
              <div className="space-y-4">
                {experiments?.slice(0, 5).map((exp: any) => (
                  <div key={exp.id} className="flex items-center justify-between border-b border-gray-100 pb-3">
                    <div className="flex items-center">
                      <ClockIcon className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{exp.name}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(exp.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <span className={`badge badge-${exp.status === 'completed' ? 'success' : 'warning'}`}>
                      {exp.status}
                    </span>
                  </div>
                ))}
                {!experiments || experiments.length === 0 && (
                  <p className="text-sm text-gray-500">No recent activity</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'datasets' && (
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Datasets</h3>
            {datasets && datasets.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rows</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {datasets.map((dataset: any) => (
                      <tr key={dataset.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {dataset.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {dataset.dataset_type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {dataset.num_rows?.toLocaleString() || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(dataset.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No datasets yet</p>
            )}
          </div>
        )}

        {activeTab === 'models' && (
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Models</h3>
            {models && models.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Framework</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {models.map((model: any) => (
                      <tr key={model.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {model.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {model.model_type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {model.version}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {model.framework || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(model.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No models yet</p>
            )}
          </div>
        )}

        {activeTab === 'experiments' && (
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Experiments</h3>
            {experiments && experiments.length > 0 ? (
              <div className="space-y-4">
                {experiments.map((exp: any) => (
                  <div key={exp.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900">{exp.name}</h4>
                      <span className={`badge badge-${
                        exp.status === 'completed' ? 'success' :
                        exp.status === 'running' ? 'info' :
                        exp.status === 'failed' ? 'danger' : 'warning'
                      }`}>
                        {exp.status}
                      </span>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      Created {new Date(exp.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No experiments yet</p>
            )}
          </div>
        )}

        {activeTab === 'jobs' && (
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Jobs</h3>
            {jobs && jobs.length > 0 ? (
              <div className="space-y-4">
                {jobs.map((job: any) => (
                  <div key={job.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{job.job_type}</h4>
                        <div className="mt-1 flex items-center space-x-2">
                          <span className={`badge badge-${
                            job.status === 'completed' ? 'success' :
                            job.status === 'running' ? 'info' :
                            job.status === 'failed' ? 'danger' : 'warning'
                          }`}>
                            {job.status}
                          </span>
                          {job.progress !== undefined && job.progress > 0 && (
                            <span className="text-xs text-gray-500">{job.progress}%</span>
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(job.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No jobs yet</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
