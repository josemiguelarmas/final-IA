import React from 'react';
import { NotificationCategory } from '../types';

const LOCALE = 'es-CO';

const timeFmt = new Intl.DateTimeFormat(LOCALE, { hour: 'numeric', minute: '2-digit' });
const dayFmt = new Intl.DateTimeFormat(LOCALE, { day: 'numeric', month: 'short' });
const dayYearFmt = new Intl.DateTimeFormat(LOCALE, { day: 'numeric', month: 'short', year: 'numeric' });
const fullFmt = new Intl.DateTimeFormat(LOCALE, { dateStyle: 'long', timeStyle: 'short' });

/** Fecha corta estilo bandeja: hora si es de hoy, día y mes si es de este año. */
export function formatListDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const now = new Date();
  if (d.toDateString() === now.toDateString()) return timeFmt.format(d);
  return (d.getFullYear() === now.getFullYear() ? dayFmt : dayYearFmt).format(d);
}

export function formatFullDate(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : fullFmt.format(d);
}

/** Separa "Nombre <correo@dominio>" en nombre y dirección. */
export function parseAddress(raw: string): { name: string; email: string } {
  const match = raw.match(/^\s*"?([^"<]*?)"?\s*<([^>]+)>\s*$/);
  if (match) return { name: match[1].trim() || match[2], email: match[2] };
  return { name: raw, email: raw.includes('@') ? raw : '' };
}

export function initials(name: string): string {
  const parts = name.replace(/[^\p{L}\s]/gu, ' ').split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase();
}

export function isHttpUrl(value?: string): value is string {
  return !!value && /^https?:\/\//i.test(value);
}

const URL_RE = /(https?:\/\/[^\s<>"')]+)/g;

/** Texto plano con las URL http(s) convertidas en enlaces seguros. */
export const Linkified: React.FC<{ text: string }> = ({ text }) => (
  <>
    {text.split(URL_RE).map((part, i) =>
      i % 2 === 1 ? (
        <a
          key={i}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
          className="text-brand underline decoration-brand/40 underline-offset-2 hover:decoration-brand"
        >
          {part}
        </a>
      ) : (
        <React.Fragment key={i}>{part}</React.Fragment>
      )
    )}
  </>
);

interface CategoryMeta {
  label: string;
  dot: string;
  text: string;
  tint: string;
}

export const CATEGORY_META: Record<NotificationCategory, CategoryMeta> = {
  requiere_actuacion: { label: 'Requiere actuación', dot: 'bg-act', text: 'text-act', tint: 'bg-act-tint' },
  revision_necesaria: { label: 'Revisión necesaria', dot: 'bg-review', text: 'text-review', tint: 'bg-review-tint' },
  informativa: { label: 'Informativa', dot: 'bg-info', text: 'text-info', tint: 'bg-info-tint' },
};

export const CategoryTag: React.FC<{ category: NotificationCategory }> = ({ category }) => {
  const meta = CATEGORY_META[category] ?? CATEGORY_META.informativa;
  return (
    <span className={`inline-flex items-center gap-1.5 font-medium ${meta.text}`}>
      <span className={`h-2 w-2 shrink-0 rounded-full ${meta.dot}`} aria-hidden="true" />
      {meta.label}
    </span>
  );
};
