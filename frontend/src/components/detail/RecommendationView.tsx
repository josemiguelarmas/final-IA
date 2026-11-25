import React, { useRef, useState } from 'react';
import { AlertTriangle, Copy, Check } from 'lucide-react';
import { NotificationItem } from '../../types';

interface RecommendationViewProps {
  notification: NotificationItem;
  draftText: string;
  onDraftChange: (value: string) => void;
  teacherNotes: string;
  onTeacherNotesChange: (value: string) => void;
  selectedCategory: string;
  onCategoryChange: (value: string) => void;
  /** Cantidad de correos que resolverá la decisión (casos con varios correos) */
  appliesTo: number;
}

type CopyState = 'idle' | 'copied' | 'failed';

export const RecommendationView: React.FC<RecommendationViewProps> = ({
  notification,
  draftText,
  onDraftChange,
  teacherNotes,
  onTeacherNotesChange,
  selectedCategory,
  onCategoryChange,
  appliesTo,
}) => {
  const [copyState, setCopyState] = useState<CopyState>('idle');
  const copyTimer = useRef<ReturnType<typeof setTimeout>>();

  const handleCopy = async () => {
    clearTimeout(copyTimer.current);
    try {
      await navigator.clipboard.writeText(draftText);
      setCopyState('copied');
    } catch {
      setCopyState('failed');
    }
    copyTimer.current = setTimeout(() => setCopyState('idle'), 2000);
  };

  const confidence = Math.round(notification.category_confidence * 100);

  return (
    <div className="mx-auto w-full max-w-3xl space-y-8 px-6 py-6">
      {appliesTo > 1 && (
        <p className="rounded-md bg-brand-tint px-4 py-2.5 text-[13px] text-ink-soft">
          Al aprobar o archivar se resuelven los <span className="font-semibold tabular-nums text-ink">{appliesTo}</span>{' '}
          correos pendientes de este caso con una sola decisión.
        </p>
      )}

      <section aria-labelledby="rec-main">
        <h3 id="rec-main" className="section-title">
          Actuación sugerida al docente
        </h3>
        <p className="mt-2 font-serif text-[17px] leading-snug text-ink">{notification.preliminary_recommendation}</p>
        <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">
          <span className="font-semibold text-ink">Fundamento.</span> {notification.recommendation_basis}
        </p>

        {notification.verification_checklist?.length > 0 && (
          <div className="mt-5">
            <h4 className="text-[13px] font-semibold text-ink">Verificar antes de responder</h4>
            <ol className="mt-2 space-y-2">
              {notification.verification_checklist.map((item, idx) => (
                <li key={idx} className="flex gap-3 text-[13px] leading-relaxed text-ink-soft">
                  <span className="mt-0.5 w-4 shrink-0 text-right font-semibold tabular-nums text-brand">{idx + 1}.</span>
                  <span>{item}</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </section>

      {notification.uncertainties?.length > 0 && (
        <section aria-labelledby="rec-uncertain" className="rounded-md bg-review-tint px-4 py-3">
          <h3 id="rec-uncertain" className="flex items-center gap-2 text-[13px] font-semibold text-review">
            <AlertTriangle className="h-4 w-4" aria-hidden="true" />
            Incertidumbres detectadas
          </h3>
          <ul className="mt-1.5 list-disc space-y-1 pl-5 text-[13px] leading-relaxed text-ink-soft">
            {notification.uncertainties.map((u, i) => (
              <li key={i}>{u}</li>
            ))}
          </ul>
        </section>
      )}

      <section aria-labelledby="rec-why" className="border-t border-rule pt-6">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h3 id="rec-why" className="section-title">
            Por qué esta clasificación
          </h3>
          <p className="text-xs text-ink-muted">
            Motor {notification.ai_engine_used.replace(/_/g, ' ')} · confianza{' '}
            <span className="font-medium tabular-nums text-ink-soft">{confidence}%</span>
          </p>
        </div>
        <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">{notification.category_justification}</p>

        {notification.category_evidence?.length > 0 && (
          <ul className="mt-3 flex flex-wrap gap-2">
            {notification.category_evidence.map((ev, i) => (
              <li key={i} className="rounded border border-rule bg-paper px-2 py-1 text-xs text-ink-soft">
                “{ev}”
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="rec-draft" className="border-t border-rule pt-6">
        <div className="flex items-center justify-between gap-3">
          <h3 id="rec-draft" className="section-title">
            Borrador de respuesta al estudiante
          </h3>
          <div className="relative">
            <button type="button" onClick={handleCopy} className="btn btn-quiet min-h-8 px-2">
              {copyState === 'copied' ? (
                <Check className="h-4 w-4 text-info" aria-hidden="true" />
              ) : (
                <Copy className="h-4 w-4" aria-hidden="true" />
              )}
              Copiar borrador
            </button>
            <span role="status" className="absolute right-2 top-full mt-0.5 whitespace-nowrap text-xs text-ink-muted">
              {copyState === 'copied' && 'Copiado'}
              {copyState === 'failed' && 'No se pudo copiar'}
            </span>
          </div>
        </div>

        <label htmlFor="draft-text" className="sr-only">
          Borrador de respuesta (editable)
        </label>
        <textarea
          id="draft-text"
          rows={7}
          value={draftText}
          onChange={(e) => onDraftChange(e.target.value)}
          placeholder="Redacte o ajuste la respuesta docente."
          className="field mt-3 leading-relaxed"
        />
        <p className="mt-1.5 text-xs text-ink-muted">
          El borrador es solo una propuesta local; el sistema no envía ningún correo.
        </p>

        <div className="mt-5 grid gap-4 sm:grid-cols-[minmax(0,14rem)_1fr]">
          <div>
            <label htmlFor="confirm-category" className="mb-1 block text-[13px] font-medium text-ink">
              Clasificación confirmada
            </label>
            <select
              id="confirm-category"
              value={selectedCategory}
              onChange={(e) => onCategoryChange(e.target.value)}
              className="field"
            >
              <option value="requiere_actuacion">Requiere actuación</option>
              <option value="revision_necesaria">Revisión necesaria</option>
              <option value="informativa">Informativa</option>
            </select>
          </div>
          <div>
            <label htmlFor="teacher-notes" className="mb-1 block text-[13px] font-medium text-ink">
              Anotaciones del docente <span className="font-normal text-ink-muted">(auditoría pedagógica)</span>
            </label>
            <input
              id="teacher-notes"
              type="text"
              value={teacherNotes}
              onChange={(e) => onTeacherNotesChange(e.target.value)}
              placeholder="Ej. Devolución del correo físico constatada en SharePoint"
              className="field"
            />
          </div>
        </div>
      </section>
    </div>
  );
};
