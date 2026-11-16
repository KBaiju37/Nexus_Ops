export default function AboutPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">About NexusOps Lite</h2>
      <div className="rounded-xl border border-slate-700 bg-slate-900 p-5 text-slate-300">
        <p className="mb-4">NexusOps Lite is a local-first DevOps dashboard that simulates deployments, records incidents, and provides lightweight ML-driven diagnostics for logs.</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>Version: 0.1.0</li>
          <li>Deployment simulation: deterministic and reproducible</li>
          <li>Stack: FastAPI, SQLAlchemy, React, TypeScript, Vite, Tailwind CSS, scikit-learn</li>
          <li>Purpose: interview-friendly demonstration of backend engineering and DevOps workflows</li>
        </ul>
      </div>
    </div>
  );
}
