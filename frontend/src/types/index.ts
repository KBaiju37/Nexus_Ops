export type Application = {
  id: number;
  name: string;
  description: string;
  repository_url?: string | null;
  environment: string;
  created_at: string;
};

export type Deployment = {
  id: number;
  application_id: number;
  version: string;
  scenario: string;
  status: string;
  started_at: string;
  completed_at?: string | null;
  logs: string;
  failure_reason?: string | null;
  incident_id?: number | null;
};

export type Incident = {
  id: number;
  deployment_id: number;
  severity: string;
  error_logs: string;
  root_cause_category: string;
  diagnosis: string;
  recommended_resolution: string;
  status: string;
  created_at: string;
  ml_category?: string | null;
  ml_confidence?: number | null;
};

export type Overview = {
  total_applications: number;
  total_deployments: number;
  successful_deployments: number;
  failed_deployments: number;
  open_incidents: number;
  resolved_incidents: number;
  deployment_success_rate: number;
};
