import { useEffect, useState } from 'react';
import { getHealth, getMetrics, getOverview } from '../services/api';

export default function MonitoringPage() {
  const [overview, setOverview] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    Promise.all([getOverview(), getMetrics(), getHealth()]).then(([overviewData, metricsData, healthData]) => {
      setOverview(overviewData);
      setMetrics(metricsData);
      setHealth(healthData);
    });
  }, []);

  if (!overview || !metrics) return <div className="text-slate-300">Loading monitoring data…</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Monitoring</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5"><p className="text-xs uppercase text-cyan-400">Health</p><h3 className="mt-3 text-2xl">{health?.status}</h3></div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5"><p className="text-xs uppercase text-cyan-400">Applications</p><h3 className="mt-3 text-2xl">{metrics.applications}</h3></div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5"><p className="text-xs uppercase text-cyan-400">Deployments</p><h3 className="mt-3 text-2xl">{metrics.deployments}</h3></div>
      </div>
      <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
        <h3 className="mb-4 text-lg font-semibold text-white">Overview</h3>
        <ul className="space-y-2 text-slate-300">
          <li>Successful deployments: {overview.successful_deployments}</li>
          <li>Failed deployments: {overview.failed_deployments}</li>
          <li>Open incidents: {overview.open_incidents}</li>
          <li>Success rate: {overview.deployment_success_rate}%</li>
        </ul>
      </div>
    </div>
  );
}
