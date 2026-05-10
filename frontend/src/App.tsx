import { useState } from 'react';
import { useAgent } from './hooks/useAgent';
import { useAgentStore } from './store/agentStore';

function App() {
  const [input, setInput] = useState('');
  const { runAgent } = useAgent();
  const { status, events, output } = useAgentStore();

  const handleRun = () => {
    if (!input.trim() || status === 'running') return;
    runAgent(input.trim());
  };

  const eventColors: Record<string, string> = {
    plan: '#4A90D9',
    tool_call: '#F5A623',
    tool_result: '#7ED321',
    reason: '#9B59B6',
    output: '#2ECC71',
    error: '#E74C3C',
    done: '#95A5A6',
  };

  return (
    <div style={{ fontFamily: 'monospace', maxWidth: 800, margin: '40px auto', padding: '0 20px' }}>
      <h1>🤖 Autonomous Research Agent</h1>
      <p style={{ color: '#666' }}>Phase 1 — Foundation (API wired, UI coming in Phase 4)</p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleRun()}
          placeholder="Enter a research goal..."
          style={{ flex: 1, padding: '10px 14px', fontSize: 16, borderRadius: 6, border: '1px solid #ccc' }}
        />
        <button
          onClick={handleRun}
          disabled={status === 'running'}
          style={{ padding: '10px 20px', background: '#4A90D9', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 16 }}
        >
          {status === 'running' ? 'Running...' : 'Run Agent'}
        </button>
      </div>

      {events.length > 0 && (
        <div style={{ background: '#111', borderRadius: 8, padding: 16, marginBottom: 24 }}>
          <p style={{ color: '#666', marginTop: 0, fontSize: 12 }}>AGENT THOUGHT STREAM</p>
          {events.map((event, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <span style={{ color: eventColors[event.type] ?? '#fff', fontWeight: 'bold', fontSize: 12, marginRight: 8 }}>
                [{event.type.toUpperCase()}]
              </span>
              <span style={{ color: '#ddd', fontSize: 13, whiteSpace: 'pre-wrap' }}>{event.content}</span>
            </div>
          ))}
        </div>
      )}

      {output && (
        <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 20 }}>
          <h2 style={{ marginTop: 0 }}>📋 Research Output</h2>
          <p>{output.summary}</p>
          {output.sections.map((s, i) => (
            <div key={i}>
              <h3>{s.title}</h3>
              <p style={{ whiteSpace: 'pre-wrap' }}>{s.content}</p>
            </div>
          ))}
          {output.citations.length > 0 && (
            <div>
              <h3>Sources</h3>
              <ul>{output.citations.map((c, i) => <li key={i}><a href={c}>{c}</a></li>)}</ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
