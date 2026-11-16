import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

export async function getOverview() {
  const { data } = await api.get('/analytics/overview');
  return data;
}

export async function getHealth() {
  const { data } = await api.get('/health');
  return data;
}

export async function getMetrics() {
  const { data } = await api.get('/metrics');
  return data;
}

export async function listApplications() {
  const { data } = await api.get('/applications');
  return data;
}

export async function createApplication(payload: Record<string, string>) {
  const { data } = await api.post('/applications', payload);
  return data;
}

export async function listDeployments() {
  const { data } = await api.get('/deployments');
  return data;
}

export async function createDeployment(payload: Record<string, string | number>) {
  const { data } = await api.post('/deployments', payload);
  return data;
}

export async function listIncidents() {
  const { data } = await api.get('/incidents');
  return data;
}

export async function updateIncident(id: number, payload: Record<string, string>) {
  const { data } = await api.patch(`/incidents/${id}`, payload);
  return data;
}

export async function analyzeIncident(id: number) {
  const { data } = await api.post(`/incidents/${id}/analyze`);
  return data;
}
