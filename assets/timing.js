export function getState(start, now, delay1, delay2, hasSecond) {
  const elapsed = Math.max(0, (now - start) / 1000);
  return { first: elapsed >= delay1, second: hasSecond && elapsed >= delay1 + delay2,
    remaining1: Math.max(0, Math.ceil(delay1 - elapsed)),
    remaining2: Math.max(0, Math.ceil(delay1 + delay2 - elapsed)),
    progress: Math.min(100, elapsed / delay1 * 100) };
}
export function formatTime(seconds) {
  return `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
}
