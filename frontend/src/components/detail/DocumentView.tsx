import React from 'react';
import { AlertCircle } from 'lucide-react';
import { NotificationItem } from '../../types';

const STATUS_LABEL: Record<string, string> = {
  analizado: 'Analizado',
  corrupto: 'Archivo corrupto',
  no_soportado: 'Formato no soportado',
};

export const DocumentView: React.FC<{ notification: NotificationItem }> = ({ notification }) => {
  const doc = notification.document_analysis;
  if (!doc) return null;

  const ok = doc.status === 'analizado';

  return (
    <div className="mx-auto w-full max-w-3xl space-y-8 px-6 py-6">
      <section aria-labelledby="doc-type">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h3 id="doc-type" className="section-title">
            {doc.document_type}
          </h3>
          <p className={`text-xs font-medium ${ok ? 'text-info' : 'text-act'}`}>{STATUS_LABEL[doc.status] ?? doc.status}</p>
        </div>
        <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">{doc.purpose}</p>
        {doc.main_request && (
          <p className="mt-3 text-[13px] leading-relaxed text-ink-soft">
            <span className="font-semibold text-ink">Petición principal.</span> {doc.main_request}
          </p>
        )}

        <dl className="mt-4 grid grid-cols-1 gap-x-6 gap-y-3 border-y border-rule py-3 sm:grid-cols-2">
          <div>
            <dt className="text-xs text-ink-muted">Peticionario o interesado</dt>
            <dd className="mt-0.5 text-[13px] font-medium text-ink">{doc.petitioner || 'No identificado'}</dd>
          </div>
          <div>
            <dt className="text-xs text-ink-muted">Entidad o contraparte</dt>
            <dd className="mt-0.5 text-[13px] font-medium text-ink">{doc.counterpart_or_entity || 'No identificada'}</dd>
          </div>
        </dl>
      </section>

      {doc.incomplete_or_missing_aspects?.length > 0 && (
        <section aria-labelledby="doc-missing" className="rounded-md bg-act-tint px-4 py-3">
          <h3 id="doc-missing" className="flex items-center gap-2 text-[13px] font-semibold text-act">
            <AlertCircle className="h-4 w-4" aria-hidden="true" />
            Aspectos incompletos o faltantes para subsanar
          </h3>
          <ul className="mt-1.5 list-disc space-y-1 pl-5 text-[13px] leading-relaxed text-ink-soft">
            {doc.incomplete_or_missing_aspects.map((miss, i) => (
              <li key={i}>{miss}</li>
            ))}
          </ul>
        </section>
      )}

      {doc.legal_grounds?.length > 0 && (
        <section aria-labelledby="doc-legal">
          <h3 id="doc-legal" className="section-title">
            Fundamentos de derecho citados
          </h3>
          <ul className="mt-3 flex flex-wrap gap-2">
            {doc.legal_grounds.map((lg, i) => (
              <li key={i} className="rounded border border-rule bg-paper px-2.5 py-1 text-[13px] text-ink-soft">
                {lg}
              </li>
            ))}
          </ul>
        </section>
      )}

      {doc.relevant_facts?.length > 0 && (
        <section aria-labelledby="doc-facts">
          <h3 id="doc-facts" className="section-title">
            Hechos relevantes del documento
          </h3>
          <ul className="mt-3 divide-y divide-rule border-y border-rule">
            {doc.relevant_facts.map((f, i) => (
              <li key={i} className="py-2.5">
                <p className="text-xs text-ink-muted">{f.page_or_section}</p>
                <p className="mt-0.5 text-[13px] leading-relaxed text-ink">{f.fact}</p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
};
