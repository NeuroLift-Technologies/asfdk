/** Operating modes that determine which Solidarity Framework components are active. */
export enum FoundationMode {
  /** All components active: TOI-OTOI, Sleepwalker Protocol, and RRT Advocate. */
  UNIFIED = 'unified',
  /** Crisis routing only: RRT Advocate active, others disabled. */
  CRISIS_ONLY = 'crisis_only',
  /** Emotional continuity only: Sleepwalker Protocol active, others disabled. */
  CONTINUITY_ONLY = 'continuity',
  /** TOI governance only: TOI-OTOI validation active, others disabled. */
  FRAMEWORK_ONLY = 'framework',
  /** Development mode: TOI-OTOI and Sleepwalker active, RRT Advocate disabled. */
  DEVELOPMENT = 'development',
}

/** Interaction categories that can be routed through the foundation. */
export enum InteractionType {
  EMOTIONAL_ASSESSMENT = 'emotional_assessment',
  CRISIS_ALERT = 'crisis_alert',
  PREFERENCE_UPDATE = 'preference_update',
  OPTIMIZATION_REQUEST = 'optimization_request',
  STATUS_INQUIRY = 'status_inquiry',
  EMERGENCY_ESCALATION = 'emergency_escalation',
}

/** Configuration for creating a {@link NeuroLiftFoundation} instance. */
export interface FoundationConfig {
  userId: string;
  mode: FoundationMode;
  /** Per-component activation overrides; defaults are derived from `mode`. */
  components?: {
    toi_otoi_framework?: boolean;
    sleepwalker_protocol?: boolean;
    rrt_advocate?: boolean;
  };
}

/** A single interaction event submitted to the foundation for processing. */
export interface UserInteraction {
  timestamp: Date;
  interactionType: InteractionType;
  data: Record<string, unknown>;
  userId: string;
  sessionId?: string;
  priority?: number;
  context?: Record<string, unknown>;
}

/** Result returned by {@link NeuroLiftFoundation.processInteraction}. */
export interface FoundationResponse {
  timestamp: Date;
  responseType: string;
  content: Record<string, unknown>;
  /** Names of components that contributed to this response. */
  componentsInvolved: string[];
  success: boolean;
}

/** Live status snapshot for a single Solidarity Framework component. */
export interface ComponentStatus {
  active: boolean;
  mode: string;
  error?: string;
}

/** Aggregate health report returned by {@link NeuroLiftFoundation.healthCheck}. */
export interface HealthCheckResult {
  healthy: boolean;
  components: Record<string, ComponentStatus>;
  timestamp: Date;
}
