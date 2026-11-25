import React, { useEffect, useRef } from 'react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  labelledBy: string;
  className?: string;
  children: React.ReactNode;
}

// closedby es atributo nuevo y no está en los tipos de React
const closedByAny = { closedby: 'any' } as object;

/** Diálogo modal sobre <dialog> nativo: foco, Esc, capa superior y retorno de foco los gestiona el navegador. */
export const Modal: React.FC<ModalProps> = ({ open, onClose, labelledBy, className = '', children }) => {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) {
      dialog.showModal();
      dialog.querySelector<HTMLElement>('[data-autofocus]')?.focus();
    } else if (!open && dialog.open) {
      dialog.close();
    }
  }, [open]);

  // Esc, clic fuera o close() nativo: sincroniza el estado de React
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    const handleClose = () => onClose();
    dialog.addEventListener('close', handleClose);
    return () => dialog.removeEventListener('close', handleClose);
  }, [onClose]);

  // Respaldo de light dismiss para navegadores sin closedby (Safari)
  const handleClick = (e: React.MouseEvent<HTMLDialogElement>) => {
    if ('closedBy' in HTMLDialogElement.prototype) return;
    const dialog = e.currentTarget;
    if (e.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    const inside = e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
    if (!inside) dialog.close();
  };

  return (
    <dialog
      ref={ref}
      className={`sheet ${className}`}
      aria-labelledby={labelledBy}
      onClick={handleClick}
      {...closedByAny}
    >
      {children}
    </dialog>
  );
};
