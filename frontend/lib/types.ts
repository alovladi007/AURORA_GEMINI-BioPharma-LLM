/**
 * TypeScript type definitions for Pharma AI Platform
 */

// ============================================
// Visualization Types
// ============================================

export interface LipinskiResult {
  checks: Record<string, boolean>
  violations: number
  drug_like: boolean
}

export interface MoleculeView {
  smiles: string
  valid: boolean
  svg?: string | null
  descriptors?: Record<string, number> | null
  lipinski?: LipinskiResult | null
}

// ============================================
// Training / Job Launch Types
// ============================================

export interface JobLaunchResponse {
  job_id: number
  task_id: string | null
  status: string
  message: string
}

// ============================================
// User & Auth Types
// ============================================

export type UserRole = "admin" | "researcher" | "viewer"

export interface User {
  id: number
  email: string
  username: string
  full_name: string | null
  role: UserRole
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
  role?: UserRole
}

// ============================================
// Project Types
// ============================================

export type ProjectStatus = "active" | "archived" | "completed"

export interface Project {
  id: number
  name: string
  description: string | null
  status: ProjectStatus
  owner_id: number
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  name: string
  description?: string
  status?: ProjectStatus
}

export interface ProjectUpdate {
  name?: string
  description?: string
  status?: ProjectStatus
}

// ============================================
// Drug Design Types
// ============================================

export interface Molecule {
  smiles: string
  similarity?: number
  properties?: MolecularProperties
}

export interface MolecularProperties {
  molecular_weight: number
  logp: number
  hbd: number
  hba: number
  tpsa: number
  rotatable_bonds: number
  aromatic_rings: number
}

export interface GenerateMoleculesRequest {
  smiles: string
  num_molecules: number
  similarity_threshold: number
}

export interface GenerateMoleculesResponse {
  input_smiles: string
  generated_molecules: Molecule[]
  generation_time: number
}

export interface PredictSARRequest {
  smiles: string
}

export interface SARPrediction {
  smiles: string
  activity_class: string
  activity_probability: number
  predicted_value: number | null
  properties: MolecularProperties
}

export interface OptimizeLeadsRequest {
  smiles: string
  target_property: string
  num_iterations: number
}

export interface OptimizeLeadsResponse {
  input_smiles: string
  optimized_molecules: Molecule[]
  target_property: string
}

// ============================================
// Clinical Trials Types
// ============================================

export interface TrialCriteria {
  disease: string
  age_min: number
  age_max: number
  gender: string | null
  biomarkers: string[]
}

export interface PatientRecruitmentRequest {
  trial_criteria: TrialCriteria
  target_enrollment: number
  trial_duration_months: number
}

export interface PatientRecruitmentResponse {
  estimated_enrollment: number
  recruitment_rate_per_month: number
  estimated_duration_months: number
  recruitment_locations: RecruitmentLocation[]
}

export interface RecruitmentLocation {
  location: string
  estimated_patients: number
  eligibility_rate: number
}

export interface TrialDesignRequest {
  disease: string
  intervention_type: string
  primary_endpoint: string
  estimated_effect_size: number
}

export interface TrialDesignResponse {
  recommended_design: string
  sample_size: number
  power: number
  duration_months: number
  arms: TrialArm[]
}

export interface TrialArm {
  name: string
  description: string
  sample_size: number
}

// ============================================
// Safety & Toxicity Types
// ============================================

export interface ADMETRequest {
  smiles: string
}

export interface ADMETPrediction {
  smiles: string
  absorption: number
  distribution: number
  metabolism: number
  excretion: number
  toxicity: number
  overall_score: number
  warnings: string[]
}

export interface ToxicityRequest {
  smiles: string
}

export interface ToxicityPrediction {
  smiles: string
  hepatotoxicity: number
  cardiotoxicity: number
  nephrotoxicity: number
  overall_toxicity: number
  structural_alerts: string[]
}

export interface DDIRequest {
  drug1_smiles: string
  drug2_smiles: string
}

export interface DDIPrediction {
  drug1_smiles: string
  drug2_smiles: string
  interaction_probability: number
  interaction_type: string
  severity: string
  mechanism: string
}

// ============================================
// Drug Repurposing Types
// ============================================

export interface KnowledgeGraphRequest {
  drug_name: string
  disease: string
  max_paths: number
}

export interface KnowledgeGraphResponse {
  drug_name: string
  disease: string
  paths: GraphPath[]
  confidence_score: number
}

export interface GraphPath {
  nodes: string[]
  edge_types: string[]
  confidence: number
}

export interface MechanismPredictionRequest {
  drug_name: string
  disease: string
}

export interface MechanismPredictionResponse {
  drug_name: string
  disease: string
  predicted_targets: string[]
  predicted_pathways: string[]
  confidence_score: number
}

// ============================================
// Job & Experiment Types
// ============================================

export type JobStatus = "pending" | "running" | "completed" | "failed" | "cancelled"

export interface Job {
  id: number
  job_type: string
  status: JobStatus
  progress: number
  error_message: string | null
  result: any
  celery_task_id: string | null
  project_id: number | null
  user_id: number
  created_at: string
  updated_at: string
  completed_at: string | null
}

export interface Experiment {
  id: number
  name: string
  description: string | null
  config: Record<string, any> | null
  results: Record<string, any> | null
  metrics: Record<string, any> | null
  project_id: number
  model_id: number | null
  dataset_id: number | null
  created_at: string
  updated_at: string
}

// ============================================
// API Response Types
// ============================================

export interface APIError {
  detail: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// ============================================
// File Upload Types
// ============================================

export interface FileUploadResponse {
  file_id: string
  filename: string
  size: number
  content_type: string
  url: string
}

export interface Dataset {
  id: number
  name: string
  description: string | null
  file_path: string | null
  file_size: number | null
  num_records: number | null
  tags: string[]
  metadata: Record<string, any> | null
  project_id: number
  created_at: string
  updated_at: string
}
