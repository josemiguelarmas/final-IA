import React from 'react';
import { Modal } from './Modal';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  description,
  confirmLabel,
  onConfirm,
  onCancel,
}) => (
  <Modal open={open} onClose={onCancel} labelledBy="confirm-title" className="w-[min(26rem,calc(100vw-2rem))]">
    <div className="rounded-lg border border-rule bg-paper p-5 shadow-[0_12px_32px_-8px_rgb(12_35_64/0.35)]">
      <h2 id="confirm-title" className="font-serif text-lg font-semibold text-ink">
        {title}
      </h2>
      <p className="mt-2 text-sm leading-relaxed text-ink-soft">{description}</p>
      <div className="mt-5 flex justify-end gap-2">
        {/* La acción segura va primero: recibe el foco al abrir */}
        <button type="button" data-autofocus onClick={onCancel} className="btn btn-secondary">
          Cancelar
        </button>
        <button type="button" onClick={onConfirm} className="btn btn-primary">
          {confirmLabel}
        </button>
      </div>
    </div>
  </Modal>
);
