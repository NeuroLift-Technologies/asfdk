export enum FoundationMode {
  UNIFIED = 'unified',
  CRISIS_ONLY = 'crisis_only',
  CONTINUITY_ONLY = 'continuity',
  FRAMEWORK_ONLY = 'framework',
  DEVELOPMENT = 'development',
}

export enum InteractionType {
  EMOTIONAL_ASSESSMENT = 'emotional_assessment',
  CRISIS_ALERT = 'crisis_alert',
  PREFERENCE_UPDATE = 'preference_update',
  OPTIMIZATION_REQUEST = 'optimization_request',
  STATUS_INQUIRY = 'status_inquiry',
  EMERGENCY_ESCALATION = 'emergency_escalation',
}

export interface FoundationConfig {
  userId: string;
  mode: FoundationMode;
  components?: {
    toi_otoi_framework?: boolean;
    sleepwalker_protocol?: boolean;
    rrt_advocate?: boolean;
  };
}

export interface UserInteraction {
  timestamp: Date;
  interactionType: InteractionType;
  data: Record<string, unknown>;
  userId: string;
  sessionId?: string;
  priority?: number;
  context?: Record<string, unknown>;
}

export interface FoundationResponse {
  timestamp: Date;
  responseType: string;
  content: Record<string, unknown>;
  componentsInvolved: string[];
  success: boolean;
}

export interface ComponentStatus {
  active: boolean;
  mode: string;
  error?: string;
}

export interface HealthCheckResult {
  healthy: boolean;
  components: Record<string, ComponentStatus>;
  timestamp: Date;
}
