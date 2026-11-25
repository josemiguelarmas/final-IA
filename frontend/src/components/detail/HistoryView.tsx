import React from 'react';
import { FileText } from 'lucide-react';
import { NotificationItem } from '../../types';

export const HistoryView: React.FC<{ notification: NotificationItem }> = ({ notification }) => {
  const summary = notification.case_summary;

  if (!summary) {
    return (
      <p className="mx-auto max-w-3xl px-6 py-12 text-center text-[13px] text-ink-muted">
        No se encontraron antecedentes vinculados a esta notificación.
      </p>
    );
  }

  const facts = [
    { label: 'Solicitante', value: summary.citizen_name },
    { label: 'Documento', value: summary.citizen_doc },
    { label: 'Teléfono', value: summary.citizen_phone },
  ];

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-6">
      <section aria-labelledby="case-sheet">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h3 id="case-sheet" className="section-title">
            Ficha del expediente {summary.case_id}
          </h3>
          <p className="text-xs text-ink-muted">
            Proyecto <span className="font-medium text-ink-soft">{summary.project}</span>
          </p>
        </div>
        <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-3 border-y border-rule py-3 sm:grid-cols-3">
          {facts.map((f) => (
            <div key={f.label}>
              <dt className="text-xs text-ink-muted">{f.label}</dt>
              <dd className="mt-0.5 text-[13px] font-medium tabular-nums text-ink">{f.value || 'No registrado'}</dd>
            </div>
          ))}
        </dl>
        {summary.is_simulated && (
          <p className="mt-2 text-xs text-ink-muted">Datos de demostración basados en las evidencias del caso.</p>
        )}
      </section>

      <section aria-labelledby="case-timeline" className="mt-8">
        <h3 id="case-timeline" className="section-title">
          Actividad del caso, en orden cronológico
        </h3>
        <ol className="mt-4">
          {summary.timeline_synthesis?.map((act, idx, all) => (
            <li key={act.id ?? idx} className="relative pb-6 pl-6 last:pb-0">
              {idx < all.length - 1 && <span className="absolute bottom-0 left-[3px] top-3 w-px bg-rule-strong" aria-hidden="true" />}
              <span className="absolute left-0 top-[7px] h-[7px] w-[7px] rounded-full bg-brand" aria-hidden="true" />
              <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-0.5">
                <p className="text-[13px] font-semibold text-ink">
                  {act.author} <span className="font-normal text-ink-muted">· {act.role}</span>
                </p>
                <p className="text-xs tabular-nums text-ink-muted">{act.date}</p>
              </div>
              <p className="mt-1 whitespace-pre-wrap text-[13px] leading-relaxed text-ink-soft">{act.text}</p>
              {act.attachments && act.attachments.length > 0 && (
                <ul className="mt-2 flex flex-wrap gap-2">
                  {act.attachments.map((a, i) => (
                    <li
                      key={i}
                      className="inline-flex items-center gap-1.5 rounded border border-rule bg-paper px-2 py-1 text-xs text-ink-soft"
                    >
                      <FileText className="h-3.5 w-3.5 text-brand" aria-hidden="true" />
                      {a.name}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
};
