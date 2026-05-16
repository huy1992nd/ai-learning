export type MessageRole = 'user' | 'assistant';

export type Severity = 'URGENT' | 'MODERATE' | 'MILD';

export type ConversationStage =
  | 'topic_guard'
  | 'greeting'
  | 'symptoms'
  | 'diagnosis'
  | 'department'
  | 'ended';

export interface DiseasePrediction {
  name: string;
  confidence: number;
  description?: string;
}

export interface DiseasePredictionCard {
  type: 'disease';
  severity: Severity;
  predictions: DiseasePrediction[];
}

export interface DoctorSummary {
  id: string;
  name: string;
  title: string;
  specialty?: string;
  photoUrl?: string;
}

export interface DepartmentSuggestion {
  id: string;
  name: string;
  description: string;
  doctors: DoctorSummary[];
}

export interface DepartmentSuggestionCard {
  type: 'department';
  suggestions: DepartmentSuggestion[];
}

export interface EmergencyAlertCard {
  type: 'emergency';
  reason: string;
  hotline?: string;
}

export interface NoDepartmentCard {
  type: 'no_department';
  diseaseName: string;
  hospitalContact?: string;
}

export type MessageCard =
  | DiseasePredictionCard
  | DepartmentSuggestionCard
  | EmergencyAlertCard
  | NoDepartmentCard;

export interface ChatMessage {
  role: MessageRole;
  content: string;
  card?: MessageCard;
  timestamp?: number;
}

export interface DetectedLanguage {
  code: string;
  name: string;
}
