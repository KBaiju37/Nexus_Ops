import { useEffect, useState } from 'react';
import StatCard from '../components/StatCard';
import { getHealth, getOverview } from '../services/api';
import type { Overview } from '../types';

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [health, setHealth] = useState<{ status?: string } | null>(null);

  useEffect(() => {
    Promise.all([getOverview(), getHealth()]).then(([data, healthData]) => {
      setOverview(data);
      setHealth(healthData);
    });
  }, []);

  if (!overview) {
    return <div className="text-slate-300">Loading dashboard…</div>;
  }

  return (
    <div className="space-y-8">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-cyan-400">Operations</p>
          <h2 className="mt-2 text-3xl font-bold text-white">Dashboard</h2>
        </div>
        <div className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">
          {health?.status === 'ok' ? 'Service healthy' : 'Checking health'}
        </div>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <StatCard title="Applications" value={String(overview.total_applications)} accent="bg-slate-800" />
        <StatCard title="Deployments" value={String(overview.total_deployments)} accent="bg-slate-800" />
        <StatCard title="Success %" value={`${overview.deployment_success_rate}%`} accent="bg-emerald-900/50" />
        <StatCard title="Open incidents" value={String(overview.open_incidents)} accent="bg-amber-900/40" />
        <StatCard title="Resolved" value={String(overview.resolved_incidents)} accent="bg-cyan-900/40" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
          <h3 className="mb-4 text-lg font-semibold text-white">Deployment summary</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm text-slate-300"><span>Succeeded</span><span>{overview.successful_deployments}</span></div>
            <div className="flex items-center justify-between text-sm text-slate-300"><span>Failed</span><span>{overview.failed_deployments}</span></div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-800">
              <div className="h-full rounded-full bg-emerald-500" style={{ width: `${overview.deployment_success_rate}%` }} />
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
          <h3 className="mb-4 text-lg font-semibold text-white">Incident severity</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            <li>Open incidents: {overview.open_incidents}</li>
            <li>Resolved incidents: {overview.resolved_incidents}</li>
            <li>Failed deployments: {overview.failed_deployments}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
