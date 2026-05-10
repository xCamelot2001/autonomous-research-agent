export type EventType =
  | 'plan'
  | 'tool_call'
  | 'tool_result'
  | 'reason'
  | 'output'
  | 'error'
  | 'done';

export interface AgentEvent {
  type: EventType;
  content: string;
  metadata: Record<string, unknown>;
}

export interface AgentOutput {
  summary: string;
  sections: Array<{ title: string; content: string }>;
  citations: string[];
}

export type AgentStatus = 'idle' | 'running' | 'complete' | 'error';
