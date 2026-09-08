const recordings = {
  workspace: { src: '/recordings/workspace.cast', kind: 'cli' },
  input: { src: '/recordings/input.cast', kind: 'cli' },
  configuration: { src: '/recordings/configuration.cast', kind: 'cli' },
  execution: { src: '/recordings/execution.cast', kind: 'cli', idleTimeLimit: 2, speed: 2 },
  questions: { src: '/recordings/questions.cast', kind: 'fixture' },
  suggestions: { src: '/recordings/suggestions.cast', kind: 'fixture' },
  'results-history': { src: '/recordings/results-history.cast', kind: 'cli', idleTimeLimit: 2 },
  'history-index': { src: '/recordings/history-index.cast', kind: 'cli', idleTimeLimit: 2 },
  'terminal-sessions': { src: '/recordings/terminal-sessions.cast', kind: 'fixture' },
  'session-tabs': { src: '/recordings/session-tabs.cast', kind: 'fixture' },
  hooks: { src: '/recordings/hooks.cast', kind: 'cli' },
  mcp: { src: '/recordings/mcp.cast', kind: 'cli' },
};

const markerPattern = /^\s*<!-- kodex-player: ([a-z0-9-]+) -->\s*$/m;

export function recordingForText(text) {
  const marker = text.match(markerPattern)?.[1];
  return marker && Object.hasOwn(recordings, marker) ? { marker, ...recordings[marker] } : undefined;
}

export { markerPattern };
