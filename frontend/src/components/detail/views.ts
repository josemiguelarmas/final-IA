export type DetailView = 'correo' | 'recomendacion' | 'historial' | 'documento';

export const VIEW_TITLE: Record<DetailView, string> = {
  correo: 'Correo',
  recomendacion: 'Recomendación IA',
  historial: 'Historial de Mantis',
  documento: 'Análisis documental',
};
