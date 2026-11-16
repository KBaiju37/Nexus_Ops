import { NavLink, Outlet } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/applications', label: 'Applications' },
  { to: '/deployments', label: 'Deployments' },
  { to: '/incidents', label: 'Incidents' },
  { to: '/monitoring', label: 'Monitoring' },
  { to: '/about', label: 'About' },
];

export default function Layout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-slate-800 bg-slate-900/80 p-5 backdrop-blur">
        <div className="mb-8">
          <p className="text-sm uppercase tracking-[0.3em] text-cyan-400">NexusOps</p>
          <h1 className="mt-2 text-2xl font-bold text-white">Lite</h1>
        </div>
        <nav className="space-y-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-300 hover:bg-slate-800'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="ml-64 p-8">
        <Outlet />
      </main>
    </div>
  );
}
