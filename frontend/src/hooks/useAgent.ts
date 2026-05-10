import { useAgentStore } from '../store/agentStore';
import { AgentEvent, AgentOutput } from '../types/agent';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export function useAgent() {
  const { setStatus, addEvent, setOutput, reset } = useAgentStore();

  const runAgent = async (goal: string) => {
    reset();
    setStatus('running');

    try {
      const response = await fetch(`${API_BASE}/api/agent/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;

          try {
            const event: AgentEvent = JSON.parse(raw);
            addEvent(event);
            if (event.type === 'output') setOutput(JSON.parse(event.content) as AgentOutput);
            if (event.type === 'done') setStatus('complete');
            if (event.type === 'error') setStatus('error');
          } catch {
            console.warn('Failed to parse SSE event:', raw);
          }
        }
      }
    } catch (err) {
      setStatus('error');
      addEvent({
        type: 'error',
        content: err instanceof Error ? err.message : 'Unknown error',
        metadata: {},
      });
    }
  };

  return { runAgent };
}
