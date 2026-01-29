export function formatTimeAgo(timestamp) {
  const now = new Date();
  const past = new Date(timestamp);
  const seconds = Math.floor((now - past) / 1000);

  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export function formatDateTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleString();
}

export function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString();
}
