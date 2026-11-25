export type NotificationCategory = 'requiere_actuacion' | 'informativa' | 'revision_necesaria';
export type ReviewStatus = 'pendiente_analisis' | 'analizada' | 'pendiente_revision_humana' | 'revisada' | 'archivada';
export type MatchCertainty = 'confirmada' | 'confirmada_por_docente' | 'probable' | 'probable_no_encontrado' | 'no_identificado';

export interface Attachment {
  filename: string;
  file_type?: string;
  size_bytes?: number;
  content_summary?: string;
  sample_content_text?: string;
  is_corrupt?: boolean;
}

export interface ExtractedData {
  case_id?: string;
  numeric_case_id?: number;
  project?: string;
  summary_subject?: string;
  student_name?: string;
  student_role?: string;
  note_id?: string;
  mantis_url?: string;
  activity_date?: string;
  student_message?: string;
  attachments: Attachment[];
}

export interface DocumentFact {
  page_or_section: string;
  fact: string;
  grounding: string;
}

export interface DocumentAnalysis {
  document_type: string;
  purpose: string;
  petitioner?: string;
  counterpart_or_entity?: string;
  main_request: string;
  relevant_facts: DocumentFact[];
  legal_grounds: string[];
  complete_aspects: string[];
  incomplete_or_missing_aspects: string[];
  inconsistencies: string[];
  status: 'analizado' | 'corrupto' | 'no_soportado';
}

export interface TimelineActivity {
  id: string;
  author: string;
  role: string;
  date: string;
  text: string;
  attachments?: { name: string; size: number }[];
}

export interface CaseSummary {
  case_id: string;
  project: string;
  citizen_name?: string;
  citizen_doc?: string;
  citizen_phone?: string;
  area?: string;
  status?: string;
  origin_description: string;
  timeline_synthesis: TimelineActivity[];
  recent_activity?: string;
  pending_commitments: string[];
  is_simulated: boolean;
}

export interface HumanDecision {
  action_type: 'aprobado' | 'corregido' | 'descartado' | 'archivado';
  confirmed_category?: string;
  confirmed_case_id?: string;
  edited_draft?: string;
  teacher_notes?: string;
  action_status: 'pendiente' | 'completada' | 'no_requerida';
  reviewed_at?: string;
  reviewer_name?: string;
}

export interface NotificationItem {
  id: string;
  message_id?: string;
  sender: string;
  recipient: string;
  received_at: string;
  subject: string;
  body: string;
  extracted_data: ExtractedData;
  category: NotificationCategory;
  category_confidence: number;
  category_justification: string;
  category_evidence: string[];
  matched_case_id?: string;
  match_certainty: MatchCertainty;
  case_summary?: CaseSummary;
  document_analysis?: DocumentAnalysis;
  preliminary_recommendation: string;
  recommendation_basis: string;
  response_draft: string;
  verification_checklist: string[];
  uncertainties: string[];
  processing_time_ms: number;
  ai_engine_used: string;
  review_status: ReviewStatus;
  human_decision?: HumanDecision;
  created_at: string;
  updated_at: string;
}

export interface DashboardStatsData {
  total_notifications: number;
  requiere_actuacion: number;
  informativa: number;
  revision_necesaria: number;
  pendiente_revision_humana: number;
  revisadas: number;
  archivadas: number;
  avg_processing_time_ms: number;
  ai_engines_distribution: Record<string, number>;
}
