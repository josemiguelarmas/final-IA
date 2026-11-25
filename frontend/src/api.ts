import { NotificationItem, DashboardStatsData, HumanDecision } from './types';

const API_BASE = '/api';

export async function fetchNotifications(category?: string, reviewStatus?: string, search?: string): Promise<NotificationItem[]> {
  const params = new URLSearchParams();
  if (category && category !== 'todas') params.append('category', category);
  if (reviewStatus && reviewStatus !== 'todos') params.append('review_status', reviewStatus);
  if (search) params.append('search', search);

  const res = await fetch(`${API_BASE}/notifications?${params.toString()}`);
  if (!res.ok) throw new Error('Error al cargar notificaciones');
  return res.json();
}

export async function fetchNotification(id: string): Promise<NotificationItem> {
  const res = await fetch(`${API_BASE}/notifications/${id}`);
  if (!res.ok) throw new Error('Error al cargar detalle de notificación');
  return res.json();
}

export async function submitHumanReview(id: string, review: HumanDecision): Promise<NotificationItem> {
  const res = await fetch(`${API_BASE}/notifications/${id}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(review),
  });
  if (!res.ok) throw new Error('Error al guardar revisión');
  return res.json();
}

export async function submitHumanReviewBatch(ids: string[], decision: HumanDecision): Promise<NotificationItem[]> {
  const res = await fetch(`${API_BASE}/notifications/review-batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notification_ids: ids, decision }),
  });
  if (!res.ok) throw new Error('Error al guardar revisión');
  return res.json();
}

export async function importNotification(payload: {
  subject: string;
  body: string;
  sender?: string;
  recipient?: string;
  message_id?: string;
  attachments?: any[];
}): Promise<NotificationItem> {
  const res = await fetch(`${API_BASE}/notifications/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Error al importar notificación');
  return res.json();
}

export async function uploadEmlFile(file: File): Promise<NotificationItem> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/notifications/upload-eml`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Error al procesar archivo .eml');
  return res.json();
}

export async function fetchStats(): Promise<DashboardStatsData> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error('Error al consultar estadísticas');
  return res.json();
}

export async function resetSamples(): Promise<{ status: string; imported: number }> {
  const res = await fetch(`${API_BASE}/reset-samples`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Error al restablecer datos de muestra');
  return res.json();
}
