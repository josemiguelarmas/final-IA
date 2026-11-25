import React, { useRef } from 'react';
import { Thread } from '../lib/threads';
import { Search, Paperclip, Check, Archive } from 'lucide-react';
import { CategoryTag, formatListDate } from '../lib/format';

interface NotificationListProps {
  threads: Thread[];
  selectedKey: string | null;
  onSelect: (key: string) => void;
  searchTerm: string;
  onSearchChange: (val: string) => void;
  statusFilter: string;
  onStatusFilterChange: (val: string) => void;
  isLoading: boolean;
}

const ReviewState: React.FC<{ status: string }> = ({ status }) => {
  if (status === 'revisada') {
    return (
      <span className="inline-flex items-center gap-1 text-brand">
        <Check className="h-3.5 w-3.5" aria-hidden="true" /> Revisada
      </span>
    );
  }
  if (status === 'archivada') {
    return (
      <span className="inline-flex items-center gap-1">
        <Archive className="h-3.5 w-3.5" aria-hidden="true" /> Archivada
      </span>
    );
  }
  return <span className="font-medium text-ink-soft">Pendiente</span>;
};

export const NotificationList: React.FC<NotificationListProps> = ({
  threads,
  selectedKey,
  onSelect,
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  isLoading,
}) => {
  const listRef = useRef<HTMLUListElement>(null);
  const messageCount = threads.reduce((sum, t) => sum + t.items.length, 0);

  // Flechas arriba/abajo recorren la bandeja y abren el correo, como un cliente de correo
  const handleKeyDown = (e: React.KeyboardEvent<HTMLUListElement>) => {
    if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
    const rows = Array.from(listRef.current?.querySelectorAll<HTMLButtonElement>('button[data-thread-key]') ?? []);
    const current = rows.indexOf(document.activeElement as HTMLButtonElement);
    if (current === -1) return;
    const next = rows[current + (e.key === 'ArrowDown' ? 1 : -1)];
    if (!next) return;
    e.preventDefault();
    next.focus();
    onSelect(next.dataset.threadKey!);
  };

  return (
    <div className="flex h-full min-h-0 flex-col border-r border-rule bg-paper">
      <div className="space-y-2 border-b border-rule p-3">
        <div className="relative">
          <label htmlFor="inbox-search" className="sr-only">
            Buscar notificaciones
          </label>
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" aria-hidden="true" />
          <input
            id="inbox-search"
            type="search"
            placeholder="Buscar por caso, estudiante o asunto"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="field py-1.5 pl-9"
          />
        </div>

        <div className="flex items-center justify-between gap-3 text-[13px]">
          <label htmlFor="inbox-status" className="text-ink-muted">
            Estado
          </label>
          <select
            id="inbox-status"
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="field w-auto py-1 pr-8 text-[13px]"
          >
            <option value="todos">Todos</option>
            <option value="pendiente_revision_humana">Pendientes</option>
            <option value="revisada">Revisadas</option>
            <option value="archivada">Archivadas</option>
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between border-b border-rule bg-canvas px-4 py-1.5 text-xs text-ink-muted" aria-live="polite">
        <span className="tabular-nums">
          {threads.length} {threads.length === 1 ? 'caso' : 'casos'} · {messageCount}{' '}
          {messageCount === 1 ? 'correo' : 'correos'}
        </span>
        {isLoading && <span className="font-medium text-brand">Actualizando…</span>}
      </div>

      {threads.length === 0 ? (
        <p className="p-8 text-center text-[13px] leading-relaxed text-ink-muted">
          Ninguna notificación coincide con la búsqueda o los filtros activos.
        </p>
      ) : (
        <ul
          ref={listRef}
          onKeyDown={handleKeyDown}
          aria-label="Bandeja de notificaciones"
          className="min-h-0 flex-1 divide-y divide-rule overflow-y-auto"
        >
          {threads.map((thread) => {
            const notif = thread.latest;
            const isSelected = thread.key === selectedKey;
            const pendingCount = thread.pending.length;
            const pending = pendingCount > 0;
            const student = notif.extracted_data?.student_name || 'Estudiante';
            const caseId = thread.caseId || 'sin ID';
            const attachments = notif.extracted_data?.attachments?.length ?? 0;

            return (
              <li key={thread.key}>
                <button
                  type="button"
                  data-thread-key={thread.key}
                  aria-current={isSelected ? 'true' : undefined}
                  onClick={() => onSelect(thread.key)}
                  className={`relative block w-full py-3 pl-6 pr-4 text-left transition-colors duration-150 ${
                    isSelected ? 'bg-brand-tint' : 'hover:bg-canvas'
                  }`}
                >
                  {pending && (
                    <span
                      className="absolute left-2.5 top-[1.15rem] h-2 w-2 rounded-full bg-brand"
                      role="img"
                      aria-label="Pendiente de revisión"
                    />
                  )}

                  <span className="flex items-baseline justify-between gap-3">
                    <span className={`truncate text-sm ${pending ? 'font-semibold text-ink' : 'font-medium text-ink-soft'}`}>
                      {student}
                    </span>
                    <span className="flex shrink-0 items-baseline gap-2">
                      {thread.items.length > 1 && (
                        <span className="rounded bg-canvas px-1.5 text-xs font-medium tabular-nums text-ink-soft ring-1 ring-rule">
                          {thread.items.length}
                          <span className="sr-only"> correos en este caso</span>
                        </span>
                      )}
                      <time dateTime={notif.received_at} className="text-xs tabular-nums text-ink-muted">
                        {formatListDate(notif.received_at)}
                      </time>
                    </span>
                  </span>

                  <span className={`mt-0.5 block truncate text-[13px] ${pending ? 'font-medium text-ink' : 'text-ink-soft'}`}>
                    {notif.subject}
                  </span>
                  <span className="mt-0.5 line-clamp-2 block text-[13px] leading-snug text-ink-muted">
                    {notif.extracted_data?.student_message || notif.body}
                  </span>

                  <span className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-ink-muted">
                    <span className="tabular-nums">Caso {caseId}</span>
                    <CategoryTag category={notif.category} />
                    {attachments > 0 && (
                      <span className="inline-flex items-center gap-1">
                        <Paperclip className="h-3.5 w-3.5" aria-hidden="true" />
                        <span className="tabular-nums">{attachments}</span>
                        <span className="sr-only">{attachments === 1 ? 'adjunto' : 'adjuntos'}</span>
                      </span>
                    )}
                    <span className="ml-auto">
                      {thread.items.length > 1 && pendingCount > 0 ? (
                        <span className="font-medium text-ink-soft">
                          {pendingCount} {pendingCount === 1 ? 'pendiente' : 'pendientes'}
                        </span>
                      ) : (
                        <ReviewState status={notif.review_status} />
                      )}
                    </span>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};
