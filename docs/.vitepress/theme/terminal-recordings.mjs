const recordings = {
  workspace: { src: '/recordings/workspace.cast', poster: 'npt:2', kind: 'cli' },
  input: { src: '/recordings/input.cast', poster: 'npt:3', kind: 'cli' },
  configuration: { src: '/recordings/configuration.cast', poster: 'npt:3', kind: 'cli' },
  execution: { src: '/recordings/execution.cast', poster: 'npt:15.8', kind: 'cli', idleTimeLimit: 2, speed: 2 },
  questions: { src: '/recordings/questions.cast', poster: 'npt:2', kind: 'fixture' },
  suggestions: { src: '/recordings/suggestions.cast', poster: 'npt:2', kind: 'fixture' },
  // startAt uses source time; poster uses the idle-compressed playback clock.
  'results-history': { src: '/recordings/results-history.cast', poster: 'npt:63.067', startAt: 190.1, kind: 'cli', idleTimeLimit: 2 },
  'history-index': { src: '/recordings/history-index.cast', poster: 'npt:19.7', kind: 'cli', idleTimeLimit: 2 },
  'terminal-sessions': { src: '/recordings/terminal-sessions.cast', poster: 'npt:2', kind: 'fixture' },
  'session-tabs': { src: '/recordings/session-tabs.cast', poster: 'npt:2', kind: 'fixture' },
  hooks: { src: '/recordings/hooks.cast', kind: 'cli' },
  mcp: { src: '/recordings/mcp.cast', kind: 'cli' },
};

const markerPattern = /^\s*<!-- kodex-player: ([a-z0-9-]+) -->\s*$/m;

export function recordingForText(text) {
  const marker = text.match(markerPattern)?.[1];
  return marker && Object.hasOwn(recordings, marker) ? { marker, ...recordings[marker] } : undefined;
}

export { markerPattern };
