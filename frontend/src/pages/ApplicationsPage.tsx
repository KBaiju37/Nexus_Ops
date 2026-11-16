import { useEffect, useState } from 'react';
import { createApplication, listApplications } from '../services/api';
import type { Application } from '../types';

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [form, setForm] = useState({ name: '', description: '', repository_url: '', environment: 'dev' });

  const load = async () => {
    const data = await listApplications();
    setApplications(data);
  };

  useEffect(() => {
    load();
  }, []);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await createApplication(form);
    setForm({ name: '', description: '', repository_url: '', environment: 'dev' });
    await load();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Applications</h2>

      <form onSubmit={onSubmit} className="rounded-xl border border-slate-700 bg-slate-900 p-5 space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <input className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="App name" required />
          <select className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}>
            <option value="dev">Development</option>
            <option value="staging">Staging</option>
            <option value="prod">Production</option>
          </select>
        </div>
        <input className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.repository_url} onChange={(e) => setForm({ ...form, repository_url: e.target.value })} placeholder="Repository URL" />
        <textarea className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" rows={3} />
        <button type="submit" className="rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950">Register application</button>
      </form>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {applications.map((app) => (
          <div key={app.id} className="rounded-xl border border-slate-700 bg-slate-900 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">{app.environment}</p>
            <h3 className="mt-2 text-xl font-semibold text-white">{app.name}</h3>
            <p className="mt-2 text-sm text-slate-300">{app.description || 'No description provided.'}</p>
            <p className="mt-4 text-xs text-slate-400">{app.repository_url || 'No repository URL'}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
