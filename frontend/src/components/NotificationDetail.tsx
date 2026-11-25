import React, { useEffect, useRef, useState } from 'react';
import { HumanDecision } from '../types';
import { Thread, reviewTargetIds } from '../lib/threads';
import { Archive, ArrowLeft, Check, Inbox } from 'lucide-react';
import { CategoryTag } from '../lib/format';
import { DetailView, VIEW_TITLE } from './detail/views';
import { EmailView } from './detail/EmailView';
import { RecommendationView } from './detail/RecommendationView';
import { HistoryView } from './detail/HistoryView';
import { DocumentView } from './detail/DocumentView';

const MATCH_LABEL: Record<string, string> = {
  confirmada: 'confirmado',
  confirmada_por_docente: 'confirmado por el docente',
  probable: 'probable',
  probable_no_encontrado: 'caso no hallado en Mantis',
  no_identificado: 'sin vincular',
};

interface NotificationDetailProps {
  thread: Thread | null;
  onSaveReview: (review: HumanDecision, ids: string[]) => Promise<void>;
  isSaving: boolean;
  /** Vuelve a la bandeja (solo en pantallas donde lista y lector no caben juntos) */
  onBack: () => void;
}

export const NotificationDetail: React.FC<NotificationDetailProps> = ({
  thread,
  onSaveReview,
  isSaving,
  onBack,
}) => {
  const [view, setView] = useState<DetailView>('correo');
  const [draftText, setDraftText] = useState('');
  const [teacherNotes, setTeacherNotes] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const scrollRef = useRef<HTMLDivElement>(null);

  const notification = thread?.latest ?? null;
  const notificationId = notification?.id;

  // Cada mensaje se abre en el correo y con sus datos de revisión. Se reinicia solo al cambiar de mensaje:
  // guardar una decisión no debe pisar lo que el docente acaba de escribir.
  useEffect(() => {
    setView('correo');
    if (notification) {
      setDraftText(notification.human_decision?.edited_draft ?? notification.response_draft ?? '');
      setTeacherNotes(notification.human_decision?.teacher_notes ?? '');
      setSelectedCategory(notification.category);
    }
  }, [notificationId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
  }, [view, notificationId]);

  if (!thread || !notification) {
    return (
      <div className="flex h-full flex-1 flex-col items-center justify-center bg-canvas p-12 text-center">
        <Inbox className="mb-3 h-10 w-10 text-rule-strong" strokeWidth={1.25} aria-hidden="true" />
        <p className="font-serif text-lg text-ink">Seleccione un mensaje</p>
        <p className="mt-1 max-w-sm text-[13px] leading-relaxed text-ink-muted">
          Al abrirlo verá el correo original y podrá pasar al historial de Mantis y a la recomendación de la IA.
        </p>
      </div>
    );
  }

  const isReviewed = notification.review_status === 'revisada';
  const caseId = notification.matched_case_id || notification.extracted_data?.case_id;

  const targetIds = reviewTargetIds(thread);
  const caseWide = targetIds.length > 1 ? ` (${targetIds.length} correos)` : '';

  const handleApprove = () =>
    onSaveReview(
      {
      action_type: 'aprobado',
      confirmed_category: selectedCategory,
      confirmed_case_id: notification.matched_case_id,
      edited_draft: draftText,
      teacher_notes: teacherNotes,
      action_status: 'completada',
      },
      targetIds
    );

  const handleArchive = () =>
    onSaveReview(
      {
      action_type: 'archivado',
      confirmed_category: selectedCategory,
      confirmed_case_id: notification.matched_case_id,
      edited_draft: draftText,
      teacher_notes: teacherNotes || 'Notificación archivada por el docente.',
      action_status: 'no_requerida',
      },
      targetIds
    );

  const otherViews = (['recomendacion', 'historial', 'documento'] as DetailView[]).filter(
    (v) => v !== view && (v !== 'documento' || notification.document_analysis)
  );

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col bg-paper">
      <div className="border-b border-rule px-4 py-3 sm:px-6">
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
          <div className="flex min-w-0 items-center gap-3 text-xs text-ink-muted">
            <button type="button" onClick={onBack} className="btn btn-quiet -ml-2 min-h-8 px-2 sm:hidden">
              <ArrowLeft className="h-4 w-4" aria-hidden="true" />
              Bandeja
            </button>
            <span className="tabular-nums">Expediente {caseId || 'sin ID'}</span>
            <CategoryTag category={notification.category} />
            <span className="hidden md:inline">
              Vínculo con Mantis:{' '}
              <span className="font-medium text-ink-soft">
                {MATCH_LABEL[notification.match_certainty] ?? 'sin vincular'}
              </span>
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button type="button" onClick={handleArchive} disabled={isSaving} className="btn btn-secondary">
              <Archive className="h-4 w-4" aria-hidden="true" />
              Archivar{caseWide}
            </button>
            <button type="button" onClick={handleApprove} disabled={isSaving} className="btn btn-primary">
              <Check className="h-4 w-4" aria-hidden="true" />
              {isReviewed && thread.pending.length === 0 ? 'Actualizar aprobación' : 'Aprobar análisis'}{caseWide}
            </button>
          </div>
        </div>

        <h2 className="mt-2 font-serif text-2xl font-semibold leading-snug text-ink">{notification.subject}</h2>
      </div>

      {view !== 'correo' && (
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 border-b border-rule bg-canvas px-4 py-1.5 sm:px-6">
          <div className="flex items-center gap-3">
            <button type="button" onClick={() => setView('correo')} className="btn btn-quiet -ml-2 min-h-8 px-2">
              <ArrowLeft className="h-4 w-4" aria-hidden="true" />
              Volver al correo
            </button>
            <p className="font-serif text-base font-semibold text-ink">{VIEW_TITLE[view]}</p>
          </div>
          <nav aria-label="Otras secciones del mensaje" className="flex items-center gap-1">
            {otherViews.map((v) => (
              <button key={v} type="button" onClick={() => setView(v)} className="btn btn-quiet min-h-8 px-2.5">
                {VIEW_TITLE[v]}
              </button>
            ))}
          </nav>
        </div>
      )}

      <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto">
        <div key={`${notificationId}-${view}`} className="reader-enter">
          {view === 'correo' && <EmailView key={thread.key} notification={notification} others={thread.items.slice(1)} onNavigate={setView} />}
          {view === 'recomendacion' && (
            <RecommendationView
              notification={notification}
              draftText={draftText}
              onDraftChange={setDraftText}
              teacherNotes={teacherNotes}
              onTeacherNotesChange={setTeacherNotes}
              selectedCategory={selectedCategory}
              onCategoryChange={setSelectedCategory}
              appliesTo={targetIds.length}
            />
          )}
          {view === 'historial' && <HistoryView notification={notification} />}
          {view === 'documento' && <DocumentView notification={notification} />}
        </div>
      </div>
    </div>
  );
};
