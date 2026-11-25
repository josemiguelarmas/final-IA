import React, { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';

export interface ToastState {
  id: number;
  message: string;
  tone: 'ok' | 'error';
}

interface ToastProps {
  toast: ToastState | null;
  onDismiss: () => void;
}

const DISMISS_MS = 6000;

// popover es atributo nuevo y no está en los tipos de React
const manualPopover = { popover: 'manual' } as object;

export const Toast: React.FC<ToastProps> = ({ toast, onDismiss }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!toast || !el) return;
    try {
      el.showPopover();
    } catch {
      /* sin soporte de popover: el aviso queda visible por CSS */
    }
  }, [toast?.id]);

  // Se cierra solo, pero no mientras el cursor o el foco están sobre el aviso
  useEffect(() => {
    if (!toast || paused) return;
    const timer = setTimeout(onDismiss, DISMISS_MS);
    return () => clearTimeout(timer);
  }, [toast?.id, paused, onDismiss]);

  return (
    <div role="region" aria-label="Notificaciones">
      <div role="status" aria-live="polite" className="sr-only-live">
        {toast?.message}
      </div>
      {toast && (
        <div
          key={toast.id}
          ref={ref}
          className="toast"
          {...manualPopover}
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
          onFocus={() => setPaused(true)}
          onBlur={() => setPaused(false)}
        >
          <div className="flex items-start gap-3 rounded-lg bg-navy py-3 pl-4 pr-2 text-sm text-white shadow-[0_12px_32px_-8px_rgb(12_35_64/0.5)]">
            <span
              className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${toast.tone === 'error' ? 'bg-rose-400' : 'bg-emerald-400'}`}
              aria-hidden="true"
            />
            <p className="flex-1 leading-snug">{toast.message}</p>
            <button
              type="button"
              onClick={onDismiss}
              aria-label="Cerrar aviso"
              className="grid h-7 w-7 shrink-0 place-items-center rounded text-white/80 hover:bg-white/10 hover:text-white"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
