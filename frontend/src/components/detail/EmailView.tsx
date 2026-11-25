import React, { useState } from 'react';
import { ChevronDown, ClipboardCheck, ExternalLink, FileText, History, Paperclip, ScanText } from 'lucide-react';
import { NotificationItem } from '../../types';
import { CategoryTag, Linkified, formatFullDate, initials, isHttpUrl, parseAddress } from '../../lib/format';
import { isPending } from '../../lib/threads';
import { DetailView } from './views';

interface EmailViewProps {
  notification: NotificationItem;
  /** Otros correos del mismo caso, del más reciente al más antiguo */
  others: NotificationItem[];
  onNavigate: (view: DetailView) => void;
}

const STATUS_LABEL: Record<string, string> = { revisada: 'Revisado', archivada: 'Archivado' };

const OtherMessages: React.FC<{ others: NotificationItem[] }> = ({ others }) => {
  // Los pendientes se muestran abiertos: son los que el docente aún debe resolver
  const [open, setOpen] = useState<Set<string>>(() => new Set(others.filter(isPending).map((n) => n.id)));
  const toggle = (id: string) =>
    setOpen((prev) => {
      const next = new Set(prev);
      if (!next.delete(id)) next.add(id);
      return next;
    });
  const pendingCount = others.filter(isPending).length;

  return (
    <section className="mt-10 border-t border-rule pt-5" aria-labelledby="other-messages">
      <h3 id="other-messages" className="section-title">
        Otros correos de este caso <span className="font-normal tabular-nums text-ink-muted">({others.length})</span>
      </h3>
      <p className="mt-0.5 text-xs text-ink-muted">
        {pendingCount > 0
          ? `${pendingCount} ${pendingCount === 1 ? 'espera' : 'esperan'} decisión; se resuelven junto con el correo principal.`
          : 'Todos están resueltos.'}
      </p>
      <ul className="mt-3 divide-y divide-rule rounded-md border border-rule">
        {others.map((m) => {
          const expanded = open.has(m.id);
          const atts = m.extracted_data?.attachments ?? [];
          return (
            <li key={m.id}>
              <button
                type="button"
                aria-expanded={expanded}
                onClick={() => toggle(m.id)}
                className="flex w-full items-start gap-3 px-3 py-2.5 text-left transition-colors duration-150 hover:bg-canvas"
              >
                <ChevronDown
                  className={`mt-0.5 h-4 w-4 shrink-0 text-ink-muted transition-transform duration-150 ${expanded ? '' : '-rotate-90'}`}
                  aria-hidden="true"
                />
                <span className="min-w-0 flex-1">
                  <span className="flex flex-wrap items-baseline justify-between gap-x-3">
                    <span className="truncate text-[13px] font-medium text-ink">
                      {m.extracted_data?.student_name || 'Estudiante'}
                    </span>
                    <time dateTime={m.received_at} className="text-xs tabular-nums text-ink-muted">
                      {formatFullDate(m.received_at)}
                    </time>
                  </span>
                  {!expanded && (
                    <span className="mt-0.5 block truncate text-[13px] text-ink-muted">
                      {m.extracted_data?.student_message || m.body}
                    </span>
                  )}
                  <span className="mt-1 flex flex-wrap items-center gap-x-3 text-xs text-ink-muted">
                    <CategoryTag category={m.category} />
                    <span className={isPending(m) ? 'font-medium text-ink-soft' : ''}>
                      {isPending(m) ? 'Pendiente' : STATUS_LABEL[m.review_status]}
                    </span>
                  </span>
                </span>
              </button>
              {expanded && (
                <div className="border-t border-rule bg-canvas/60 px-4 py-3 pl-10">
                  <div className="whitespace-pre-wrap text-[13px] leading-6 text-ink-soft [overflow-wrap:anywhere]">
                    <Linkified text={m.body} />
                  </div>
                  {atts.length > 0 && (
                    <ul className="mt-2 flex flex-wrap gap-2">
                      {atts.map((a, i) => (
                        <li
                          key={i}
                          className="inline-flex items-center gap-1.5 rounded border border-rule bg-paper px-2 py-1 text-xs text-ink-soft"
                        >
                          <FileText className="h-3.5 w-3.5 text-brand" aria-hidden="true" />
                          {a.filename}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
};

export const EmailView: React.FC<EmailViewProps> = ({ notification, others, onNavigate }) => {
  const from = parseAddress(notification.sender);
  const to = parseAddress(notification.recipient);
  const attachments = notification.extracted_data?.attachments ?? [];
  const timelineCount = notification.case_summary?.timeline_synthesis?.length ?? 0;
  const mantisUrl = notification.extracted_data?.mantis_url;
  const noteId = notification.extracted_data?.note_id;

  return (
    <article className="mx-auto w-full max-w-3xl px-6 py-6">
      <header className="flex items-start gap-3">
        <span
          aria-hidden="true"
          className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-brand-tint text-sm font-semibold text-brand"
        >
          {initials(from.name)}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-0.5">
            <p className="text-sm font-semibold text-ink">{from.name}</p>
            <time dateTime={notification.received_at} className="text-xs text-ink-muted">
              {formatFullDate(notification.received_at)}
            </time>
          </div>
          <dl className="mt-0.5 space-y-0.5 text-xs text-ink-muted">
            {from.email && (
              <div className="flex gap-1.5">
                <dt className="shrink-0">De</dt>
                <dd className="min-w-0 truncate text-ink-soft">{from.email}</dd>
              </div>
            )}
            <div className="flex gap-1.5">
              <dt className="shrink-0">Para</dt>
              <dd className="min-w-0 truncate text-ink-soft">{to.email || to.name}</dd>
            </div>
            {noteId && (
              <div className="flex gap-1.5">
                <dt className="shrink-0">Nota de Mantis</dt>
                <dd className="tabular-nums text-ink-soft">{noteId}</dd>
              </div>
            )}
          </dl>
        </div>
      </header>

      {/* Salto a la información relacionada con este correo */}
      <div className="mt-5 flex flex-wrap gap-2">
        <button type="button" onClick={() => onNavigate('recomendacion')} className="btn btn-primary">
          <ClipboardCheck className="h-4 w-4" aria-hidden="true" />
          Recomendación IA
        </button>
        <button type="button" onClick={() => onNavigate('historial')} className="btn btn-secondary">
          <History className="h-4 w-4" aria-hidden="true" />
          Historial de Mantis
          {timelineCount > 0 && <span className="tabular-nums text-ink-muted">{timelineCount}</span>}
        </button>
        {notification.document_analysis && (
          <button type="button" onClick={() => onNavigate('documento')} className="btn btn-secondary">
            <ScanText className="h-4 w-4" aria-hidden="true" />
            Análisis documental
          </button>
        )}
        {isHttpUrl(mantisUrl) && (
          <a href={mantisUrl} target="_blank" rel="noopener noreferrer" className="btn btn-quiet sm:ml-auto">
            Abrir en Mantis
            <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
          </a>
        )}
      </div>

      <div className="mt-6 border-t border-rule pt-5">
        <div className="whitespace-pre-wrap text-[15px] leading-7 text-ink [overflow-wrap:anywhere]">
          <Linkified text={notification.body} />
        </div>
      </div>

      {attachments.length > 0 && (
        <section className="mt-8 border-t border-rule pt-5" aria-labelledby="email-attachments">
          <h3 id="email-attachments" className="section-title flex items-center gap-1.5">
            <Paperclip className="h-4 w-4 text-ink-muted" aria-hidden="true" />
            Adjuntos
            <span className="font-normal tabular-nums text-ink-muted">({attachments.length})</span>
          </h3>
          <ul className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
            {attachments.map((att, idx) => (
              <li key={idx} className="flex items-center gap-2.5 rounded-md border border-rule bg-paper px-3 py-2">
                <FileText className="h-4 w-4 shrink-0 text-brand" aria-hidden="true" />
                <div className="min-w-0">
                  <p className="truncate text-[13px] font-medium text-ink">{att.filename}</p>
                  <p className="text-xs text-ink-muted">
                    {att.size_bytes ? `${(att.size_bytes / 1024).toFixed(1)} KB` : 'Tamaño no informado'}
                    {att.file_type ? ` · ${att.file_type}` : ''}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {others.length > 0 && <OtherMessages others={others} />}
    </article>
  );
};
