type Props = { title: string; value: string; accent?: string };

export default function StatCard({ title, value, accent = 'bg-slate-800' }: Props) {
  return (
    <div className={`${accent} rounded-xl border border-slate-700 p-4 shadow-lg`}>
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <h3 className="mt-3 text-2xl font-semibold text-white">{value}</h3>
    </div>
  );
}
