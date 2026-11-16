import { useEffect, useState } from 'react';
import { createDeployment, listApplications, listDeployments } from '../services/api';
import type { Application, Deployment } from '../types';

const scenarios = ['successful', 'build_failure', 'dependency_installation_failure', 'application_startup_failure', 'health_check_failure'];

export default function DeploymentsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [form, setForm] = useState({ application_id: '', version: 'v1.0.0', scenario: 'successful' });

  const load = async () => {
    const [apps, depData] = await Promise.all([listApplications(), listDeployments()]);
    setApplications(apps);
    setDeployments(depData);
  };

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.application_id) return;
    await createDeployment({ application_id: Number(form.application_id), version: form.version, scenario: form.scenario });
    setForm({ application_id: form.application_id, version: form.version, scenario: form.scenario });
    await load();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Deployments</h2>

      <form onSubmit={handleSubmit} className="rounded-xl border border-slate-700 bg-slate-900 p-5 space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <select className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.application_id} onChange={(e) => setForm({ ...form, application_id: e.target.value })}>
            <option value="">Select application</option>
            {applications.map((app) => (
              <option key={app.id} value={app.id}>{app.name}</option>
            ))}
          </select>
          <input className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.version} onChange={(e) => setForm({ ...form, version: e.target.value })} placeholder="Version" />
          <select className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.scenario} onChange={(e) => setForm({ ...form, scenario: e.target.value })}>
            {scenarios.map((scenario) => (
              <option key={scenario} value={scenario}>{scenario}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="rounded-lg bg-emerald-500 px-4 py-2 font-semibold text-slate-950">Trigger deployment</button>
      </form>

      <div className="space-y-4">
        {deployments.map((deployment) => (
          <div key={deployment.id} className="rounded-xl border border-slate-700 bg-slate-900 p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">{deployment.scenario}</p>
                <h3 className="text-xl font-semibold text-white">Version {deployment.version}</h3>
              </div>
              <span className={`rounded-full px-2 py-1 text-xs ${deployment.status === 'Succeeded' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
                {deployment.status}
              </span>
            </div>
            <pre className="mt-4 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-300">{deployment.logs}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
