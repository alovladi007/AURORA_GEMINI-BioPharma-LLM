# AURORA / GEMINI BioPharma-LLM — 18-Month Build-Out Master Plan

> **Status:** Architecture-complete, ML-incomplete. This document is the authoritative
> 18-month engineering roadmap to take the platform from a scaffolded MVP with demo/placeholder
> ML into a production-grade, scientifically credible AI drug-discovery platform.
>
> It is written to double as a **master prompt**: each Epic below is self-contained and can be
> handed to an engineer (or an AI agent) as a work order, with acceptance criteria.

---

## 0. Where We Are Today (Baseline Audit)

| Layer | State | Reality |
|-------|-------|---------|
| Backend API (FastAPI) | ✅ Complete | 12 routers, ~50 endpoints, CRUD for all entities |
| Auth (backend) | ✅ Complete | JWT, bcrypt, RBAC roles, dependencies |
| Auth (frontend) | ❌ Missing | No login/register UI, no token injection (TODO in `lib/api.ts`) |
| Database | ✅ Complete | 7 models, Alembic migration, Postgres |
| Frontend pages | ⚠️ Skeleton | 20 pages exist; many forms not wired to API |
| **ML — Drug Design** | ❌ **Demo** | Random SMILES sampling; SAR = RF on 20 synthetic mols |
| **ML — Safety** | ❌ **Demo** | Rule-based heuristics on descriptors |
| **ML — Clinical Trials** | ❌ **Demo** | Hardcoded city lists + random estimates |
| **ML — Repurposing** | ❌ **Demo** | Hardcoded disease/target lists + random paths |
| Training scripts | ❌ Missing | Makefile references them; none exist |
| Datasets | ❌ Missing | `ml/data/*` empty |
| Model artifacts | ❌ Missing | `ml/models/artifacts/*` empty |
| Featurization (RDKit) | ✅ Real | Morgan/MACCS/descriptors are genuine |
| Celery | ⚠️ Stubs | Tasks call demo inference |
| Infra | ✅ Good | docker-compose dev+prod, CI, rate-limit, logging |
| Observability | ⚠️ Partial | Structured logs; no metrics/tracing/Sentry verified |
| Visualization | ❌ Missing | No 3D/2D molecule rendering |
| Graph DB | ❌ Disabled | Neo4j commented out |

**Guiding principle for 18 months:** *Replace every "demo" with a real, benchmarked, versioned model,
and wire every screen end-to-end with auth, jobs, and visualization.*

---

## 1. Operating Model

- **Cadence:** 6 phases × ~3 months (Q1–Q6). Two-week sprints.
- **Definition of Done (global):** code + tests (≥80% on new modules) + docs + CI green +
  feature flag + telemetry + reviewed PR.
- **Scientific rigor:** every model ships with a **model card** (data provenance, metrics on a
  held-out + scaffold-split test set, known limitations, intended use, "research use only" banner).
- **Branching:** trunk-based with short-lived `claude/*` feature branches; protected `main`.

---

## 2. Workstreams (vertical themes that span all phases)

1. **WS-ML** — Real models, training, evaluation, registry, MLOps.
2. **WS-DATA** — Ingestion (ChEMBL/PubChem/ClinicalTrials.gov/Open Targets), curation, splits.
3. **WS-APP** — Frontend/UX, auth, visualization, dashboards.
4. **WS-PLATFORM** — Jobs, scaling, multi-tenancy, security, compliance.
5. **WS-OBS** — Observability, evaluation harnesses, drift monitoring.

---

## 3. Phased Roadmap

### PHASE 1 (Months 0–3) — "Make it real & end-to-end"
**Theme:** Close the auth loop, stand up real data + training, replace the most tractable demo (SAR).

**Epics**
- **E1.1 Frontend Auth (WS-APP)** — token storage, axios interceptor w/ refresh, `/login`,
  `/register`, auth context, protected routes, user menu, logout. *AC:* a user can register, log in,
  hit protected APIs, and be redirected on 401.
- **E1.2 Data Ingestion v1 (WS-DATA)** — ChEMBL + PubChem REST clients with caching & rate limiting;
  CLI to pull a target's bioactivity table to parquet. *AC:* `python -m app.data.ingest chembl --target CHEMBL203`
  produces a curated, deduplicated parquet with standardized units (pChEMBL).
- **E1.3 Real SAR Models (WS-ML)** — training pipeline (featurize → scaffold split → train RF +
  GBT + MLP → calibrate → evaluate → register artifact + model card). *AC:* AUC/RMSE reported on
  scaffold-split test set; artifact loaded by inference at runtime (no more demo fallback when a
  model exists).
- **E1.4 Job execution for real (WS-PLATFORM)** — Celery tasks invoke real training/inference;
  progress + logs persisted to `Job`. *AC:* a training job runs async, streams progress, registers a model.
- **E1.5 MLflow tracking (WS-OBS)** — experiment tracking server in compose; runs logged. *AC:* every
  training run appears in MLflow with params/metrics/artifacts.

**Exit criteria:** A user logs in, uploads/ingests a dataset, launches a real SAR training job,
watches progress, and runs predictions from a trained model — all in the UI.

---

### PHASE 2 (Months 3–6) — "Generative design + ADMET that means something"
**Theme:** Real generative chemistry and real ADMET/property models; molecule visualization.

**Epics**
- **E2.1 De Novo Generation (WS-ML)** — integrate a real generative model: SMILES-LSTM/Transformer
  or a graph-based VAE (e.g., train a SMILES transformer; optionally wrap REINVENT-style scoring).
  Add scaffold-constrained generation. *AC:* generates novel, valid (RDKit-parseable), unique,
  drug-like molecules with validity/uniqueness/novelty metrics.
- **E2.2 ADMET Suite (WS-ML)** — train models on public ADMET sets (Lipophilicity, ESOL, BBBP,
  CYP, hERG, Caco-2, etc. via Therapeutics Data Commons). Multi-task where sensible. *AC:* per-endpoint
  benchmark table matching or near TDC leaderboards; calibrated probabilities.
- **E2.3 Molecule Visualization (WS-APP)** — 2D depiction (RDKit.js / SmilesDrawer) + 3D (3Dmol.js);
  SAR tables, property radar charts, similarity maps. *AC:* paste SMILES → see 2D+3D + properties.
- **E2.4 Multi-Parameter Optimization (WS-ML)** — Pareto/MPO scoring combining potency + ADMET +
  synthetic accessibility (SA score) + QED. *AC:* optimizer returns a Pareto front with rationale.
- **E2.5 Property/SA/Synthesis (WS-ML)** — SA score, retrosynthesis feasibility heuristic hooks.

**Exit criteria:** Drug Design and Safety modules are backed by benchmarked models with visualization.

---

### PHASE 3 (Months 6–9) — "Knowledge graph & repurposing for real"
**Theme:** Stand up a biomedical knowledge graph and real link-prediction.

**Epics**
- **E3.1 KG Construction (WS-DATA)** — ingest Open Targets, Hetionet, DrugBank (licensed),
  DisGeNET into Neo4j (enable the disabled service) + a typed schema (Drug–Target–Pathway–Disease).
  *AC:* Neo4j populated; Cypher queries return real drug–disease paths.
- **E3.2 KG Embeddings & Link Prediction (WS-ML)** — train KGE (TransE/RotatE/ComplEx) or a GNN
  (R-GCN) for drug–disease repurposing scoring. *AC:* ranked repurposing candidates with held-out
  link-prediction AUC; explanations via meta-paths.
- **E3.3 Mechanism-of-Action (WS-ML)** — path-based + embedding-based MoA hypotheses with evidence
  citations from the KG. *AC:* each prediction lists supporting edges/sources.
- **E3.4 Combination Discovery (WS-ML)** — synergy modeling (e.g., on DrugComb/NCI-ALMANAC). *AC:*
  synergy scores with uncertainty.
- **E3.5 Graph UI (WS-APP)** — interactive graph explorer (Cytoscape.js) with path highlighting.

**Exit criteria:** Repurposing module returns evidence-backed, ranked, explainable candidates.

---

### PHASE 4 (Months 9–12) — "Clinical intelligence + LLM copilot"
**Theme:** Real clinical-trial analytics and an LLM-powered research copilot (the "LLM" in BioPharma-LLM).

**Epics**
- **E4.1 ClinicalTrials.gov Ingestion (WS-DATA)** — pull & index trials; eligibility parsing. *AC:*
  searchable trial corpus with structured eligibility.
- **E4.2 Recruitment & Survival Models (WS-ML)** — enrollment forecasting; survival analysis
  (lifelines/Cox, already a dependency) on appropriate datasets. *AC:* calibrated enrollment curves,
  KM/Cox outputs.
- **E4.3 Trial Design Assistant (WS-ML)** — power/sample-size, adaptive design suggestions grounded
  in statistics (not heuristics). *AC:* statistically correct sample-size with assumptions surfaced.
- **E4.4 LLM Copilot (WS-ML/WS-APP)** — Retrieval-Augmented Generation over the platform's data
  (molecules, predictions, trials, KG) using **Claude (claude-opus-4-8 / claude-sonnet-4-6)** via the
  Anthropic API, with tool-use to call platform endpoints. Guardrails + citations + "research use only".
  *AC:* user asks "summarize ADMET risks for these 5 leads and propose next assays" and gets a grounded,
  cited answer that calls real endpoints.
- **E4.5 Reporting (WS-APP)** — PDF/XLSX export of results and model cards.

**Exit criteria:** Clinical module is statistically real; an LLM copilot ties the whole platform together.

---

### PHASE 5 (Months 12–15) — "Enterprise, scale & MLOps"
**Theme:** Multi-tenancy, Kubernetes, model registry/serving, drift & retraining.

**Epics**
- **E5.1 Multi-tenancy & Collaboration (WS-PLATFORM)** — organizations/workspaces, project sharing,
  RBAC enforcement on every endpoint, audit log. *AC:* org admins manage members; access controlled.
- **E5.2 Kubernetes (WS-PLATFORM)** — Helm charts, HPA, GPU node pools for training, secrets via
  Vault/SealedSecrets. *AC:* one-command deploy to a cluster; autoscaling verified.
- **E5.3 Model Registry & Serving (WS-ML/WS-OBS)** — MLflow registry + dedicated inference service
  (BentoML/Triton) with versioned, A/B-testable endpoints. *AC:* promote model staging→prod; A/B split.
- **E5.4 Drift & Retraining (WS-OBS)** — data/prediction drift monitors; scheduled retraining;
  feature store (Feast optional). *AC:* drift alert triggers a retraining job.
- **E5.5 Object storage (WS-PLATFORM)** — S3/MinIO for datasets & artifacts (replace local FS). *AC:*
  artifacts in S3; signed URLs.

**Exit criteria:** Platform runs on k8s, multi-tenant, with a real MLOps lifecycle.

---

### PHASE 6 (Months 15–18) — "Compliance, validation & GA"
**Theme:** Security hardening, scientific validation, documentation, launch.

**Epics**
- **E6.1 Security & Compliance (WS-PLATFORM)** — pen-test remediation, SSO/OIDC, SOC2-aligned
  controls, data residency, PII handling for clinical data, full audit trail. *AC:* third-party
  security review passed.
- **E6.2 Scientific Validation (WS-ML/WS-OBS)** — prospective/retrospective validation studies,
  benchmark report vs. published baselines, external review. *AC:* validation whitepaper.
- **E6.3 Performance & Cost (WS-PLATFORM)** — load testing, caching, inference cost optimization,
  SLOs/SLAs. *AC:* p95 latencies under target at target QPS.
- **E6.4 Docs & Onboarding (WS-APP)** — full user/admin/API docs, tutorials, sample workflows. *AC:*
  a new user completes a guided drug-discovery workflow unaided.
- **E6.5 GA Launch (all)** — feature-flag cleanup, final QA, marketing site, pricing/tenancy.

**Exit criteria:** General Availability of a validated, secure, scalable platform.

---

## 4. Cross-Cutting Acceptance Standards

- **Model card required** for every shipped model (`ml/model_cards/<model>.md`).
- **Scaffold splits** (not random) for all molecular models to avoid leakage.
- **Calibration** (Platt/Isotonic) for all classifiers exposed to users.
- **"Research Use Only"** banner persists across clinical/medical outputs.
- **Determinism**: seeds pinned; training reproducible from a config.
- **Telemetry**: every prediction logs model version + latency + (opt-in) inputs hash.

---

## 5. Suggested Team & Tooling

- 2 ML engineers (cheminformatics + graph/NLP), 2 full-stack, 1 data engineer, 1 DevOps/MLOps,
  0.5 security, 0.5 PM, fractional comp-chem/biostat SME for validation.
- **Tooling:** RDKit, PyTorch, PyTorch Geometric, DeepChem/TDC, MLflow, Neo4j, MinIO/S3,
  BentoML/Triton, Kubernetes/Helm, Anthropic Claude API for the copilot.

---

## 6. Progress Log

### Phase 1 — delivered
1. ✅ This roadmap (`ROADMAP.md`).
2. ✅ **E1.1** Frontend auth — auth lib, context, login/register, axios interceptor, route guard, navbar.
3. ✅ **E1.2** Data ingestion — ChEMBL client + curation + `python -m app.data.ingest`.
4. ✅ **E1.3** Real SAR training — scaffold split, RF, model card, artifact; endpoint auto-loads the
   trained model. `python -m app.ml.drug_design.train`.
5. ✅ **E1.4** Job execution — `TrackedTask` Celery base syncs the `Job` table (status/progress/result);
   `POST /api/v1/training/sar` launches a tracked training job; all 4 task modules rewritten to call
   real engines (previously crashed the worker on import).
6. ✅ **E1.5** MLflow — tracking service in compose + guarded logging in the training pipeline.

### Phase 2 — in progress
7. ✅ **E2.3 (start)** Molecule visualization — RDKit SVG + descriptors + Lipinski endpoint
   (`/api/v1/visualize/*`), `MoleculeViewer` React component, and a `/tools/molecule-viewer` page.
8. ▶️ Next: ADMET suite training (TDC datasets) reusing the generic trainer; generative model for
   de novo design; wire the viewer into the drug-design generate/SAR pages.

### Fixes made along the way
- Repaired `endpoints/drug_design.py` (mangled `SARInferenceEngine` import — module never compiled).
- Fixed dev `docker-compose.yml` Celery command (`app.core.celery_app` → `app.celery_app`).
- Rewrote task layer to use the real `Job.task_id` column (was a non-existent `celery_task_id`).

> See `ml/model_cards/TEMPLATE.md`, `backend/app/data/`, `backend/app/ml/`, and `backend/app/tasks/`.
