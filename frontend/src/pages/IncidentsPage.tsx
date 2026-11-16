import { useEffect, useState } from 'react';
import { analyzeIncident, listIncidents, updateIncident } from '../services/api';
import type { Incident } from '../types';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  const load = async () => {
    const data = await listIncidents();
    setIncidents(data);
  };

  useEffect(() => {
    load();
  }, []);

  const onStatusUpdate = async (incidentId: number, status: string) => {
    await updateIncident(incidentId, { status });
    await load();
  };

  const onAnalyze = async (incidentId: number) => {
    await analyzeIncident(incidentId);
    await load();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Incidents</h2>
      <div className="space-y-4">
        {incidents.map((incident) => (
          <div key={incident.id} className="rounded-xl border border-slate-700 bg-slate-900 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-amber-400">{incident.severity}</p>
                <h3 className="mt-2 text-xl font-semibold text-white">Incident #{incident.id}</h3>
              </div>
              <div className="space-x-2 text-sm">
                <button className="rounded-lg bg-cyan-500 px-3 py-1 font-semibold text-slate-900" onClick={() => onAnalyze(incident.id)}>Analyze</button>
                <button className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-1" onClick={() => onStatusUpdate(incident.id, incident.status === 'Open' ? 'Investigating' : 'Resolved')}>Toggle status</button>
              </div>
            </div>
            <p className="mt-4 text-slate-300">{incident.diagnosis || 'No diagnosis yet.'}</p>
            <p className="mt-2 text-sm text-cyan-300">Recommendation: {incident.recommended_resolution || 'Not available.'}</p>
            <pre className="mt-4 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-300">{incident.error_logs}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
