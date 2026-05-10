import { create } from 'zustand';
import { AgentEvent, AgentOutput, AgentStatus } from '../types/agent';

interface AgentStore {
  status: AgentStatus;
  events: AgentEvent[];
  output: AgentOutput | null;
  goal: string;
  setGoal: (goal: string) => void;
  setStatus: (status: AgentStatus) => void;
  addEvent: (event: AgentEvent) => void;
  setOutput: (output: AgentOutput) => void;
  reset: () => void;
}

export const useAgentStore = create<AgentStore>((set) => ({
  status: 'idle',
  events: [],
  output: null,
  goal: '',
  setGoal: (goal) => set({ goal }),
  setStatus: (status) => set({ status }),
  addEvent: (event) => set((state) => ({ events: [...state.events, event] })),
  setOutput: (output) => set({ output }),
  reset: () => set({ status: 'idle', events: [], output: null }),
}));
