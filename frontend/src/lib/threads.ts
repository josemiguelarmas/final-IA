import { NotificationItem } from '../types';

/** Todos los correos que llegaron para un mismo caso de Mantis. */
export interface Thread {
  key: string;
  caseId: string | null;
  /** Correo más reciente: es el que se muestra en la bandeja */
  latest: NotificationItem;
  /** Todos los correos del caso, del más reciente al más antiguo */
  items: NotificationItem[];
  /** Correos que aún esperan decisión docente */
  pending: NotificationItem[];
}

export const isPending = (n: NotificationItem): boolean =>
  n.review_status !== 'revisada' && n.review_status !== 'archivada';

const time = (n: NotificationItem) => new Date(n.received_at).getTime();

export function groupThreads(notifications: NotificationItem[]): Thread[] {
  const groups = new Map<string, NotificationItem[]>();
  for (const n of notifications) {
    const caseId = n.matched_case_id || n.extracted_data?.case_id || null;
    const key = caseId ? `case:${caseId}` : `notif:${n.id}`;
    groups.set(key, [...(groups.get(key) ?? []), n]);
  }

  return [...groups.entries()]
    .map(([key, list]) => {
      const items = [...list].sort((a, b) => time(b) - time(a));
      return {
        key,
        caseId: key.startsWith('case:') ? key.slice(5) : null,
        latest: items[0],
        items,
        pending: items.filter(isPending),
      };
    })
    .sort((a, b) => time(b.latest) - time(a.latest));
}

/** Ids a los que aplica una decisión: los pendientes del caso y el correo que se está viendo. */
export function reviewTargetIds(thread: Thread): string[] {
  return [...new Set([thread.latest.id, ...thread.pending.map((n) => n.id)])];
}
