import React from 'react';
import { DashboardStatsData } from '../types';

interface StatsProps {
  stats: DashboardStatsData | null;
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
}

export const DashboardStats: React.FC<StatsProps> = ({
  stats,
  selectedCategory,
  onSelectCategory,
  statusFilter,
  onStatusFilterChange,
}) => {
  // Reserva el alto de la franja para que la página no salte al cargar
  if (!stats) return <div className="h-[72px] shrink-0 border-b border-rule bg-paper" aria-hidden="true" />;

  const categories = [
    { id: 'todas', label: 'Todas', count: stats.total_notifications, dot: 'bg-ink-muted' },
    { id: 'requiere_actuacion', label: 'Requiere actuación', count: stats.requiere_actuacion, dot: 'bg-act' },
    { id: 'revision_necesaria', label: 'Revisión necesaria', count: stats.revision_necesaria, dot: 'bg-review' },
    { id: 'informativa', label: 'Informativas', count: stats.informativa, dot: 'bg-info' },
  ];

  const statuses = [
    { id: 'pendiente_revision_humana', label: 'Pendientes', count: stats.pendiente_revision_humana },
    { id: 'revisada', label: 'Revisadas', count: stats.revisadas },
    { id: 'archivada', label: 'Archivadas', count: stats.archivadas },
  ];

  const total = Math.max(stats.total_notifications, 1);
  const resolved = stats.revisadas + stats.archivadas;
  const pct = (n: number) => `${(n / total) * 100}%`;

  const [engine] = Object.entries(stats.ai_engines_distribution ?? {}).sort((a, b) => b[1] - a[1])[0] ?? [
    'reglas_locales_expertas',
  ];

  return (
    <section aria-label="Resumen de la bandeja" className="shrink-0 border-b border-rule bg-paper">
      <div className="flex flex-col gap-4 px-4 py-3 lg:flex-row lg:items-center lg:gap-8 lg:px-6">
        {/* Clasificación: filtro segmentado */}
        <div
          role="group"
          aria-label="Filtrar por clasificación"
          className="flex min-w-0 divide-x divide-rule overflow-x-auto rounded-md border border-rule-strong"
        >
          {categories.map((c) => {
            const selected = selectedCategory === c.id;
            return (
              <button
                key={c.id}
                type="button"
                aria-pressed={selected}
                onClick={() => onSelectCategory(c.id)}
                className={`flex shrink-0 items-center gap-2 px-3.5 py-2 text-[13px] transition-colors duration-150 ${
                  selected ? 'bg-navy text-white' : 'bg-paper text-ink-soft hover:bg-canvas'
                }`}
              >
                <span className={`h-2 w-2 rounded-full ${c.dot} ${selected ? 'ring-2 ring-white/40' : ''}`} aria-hidden="true" />
                <span className="font-medium">{c.label}</span>
                <span className={`tabular-nums ${selected ? 'text-white/80' : 'text-ink-muted'}`}>{c.count}</span>
              </button>
            );
          })}
        </div>

        {/* Avance de la revisión docente */}
        <div className="hidden min-w-0 flex-1 sm:block lg:max-w-sm">
          <div className="flex items-baseline justify-between gap-3 text-[13px]">
            <span className="font-medium text-ink">Revisión docente</span>
            <span className="tabular-nums text-ink-muted">
              {resolved} de {stats.total_notifications} correos resueltos
            </span>
          </div>
          <div
            className="mt-1.5 flex h-1.5 overflow-hidden rounded-full bg-rule"
            role="img"
            aria-label={`${stats.revisadas} revisadas, ${stats.archivadas} archivadas y ${stats.pendiente_revision_humana} pendientes de ${stats.total_notifications}`}
          >
            <div className="bg-brand" style={{ width: pct(stats.revisadas) }} />
            <div className="bg-ink-muted/60" style={{ width: pct(stats.archivadas) }} />
          </div>
          <div role="group" aria-label="Filtrar por estado de revisión" className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1">
            {statuses.map((s) => {
              const selected = statusFilter === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  aria-pressed={selected}
                  onClick={() => onStatusFilterChange(selected ? 'todos' : s.id)}
                  className={`rounded text-xs transition-colors duration-150 ${
                    selected ? 'font-semibold text-brand underline underline-offset-4' : 'text-ink-muted hover:text-ink'
                  }`}
                >
                  {s.label} <span className="tabular-nums">{s.count}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Motor de análisis */}
        <dl className="hidden shrink-0 gap-6 text-xs sm:flex lg:ml-auto lg:block lg:space-y-0.5 lg:text-right">
          <div>
            <dt className="mr-1.5 inline text-ink-muted">Motor</dt>
            <dd className="inline font-medium text-ink">{engine.replace(/_/g, ' ')}</dd>
          </div>
          <div>
            <dt className="mr-1.5 inline text-ink-muted">Tiempo medio</dt>
            <dd className="inline font-medium tabular-nums text-ink">{Math.round(stats.avg_processing_time_ms)} ms</dd>
          </div>
        </dl>
      </div>
    </section>
  );
};
