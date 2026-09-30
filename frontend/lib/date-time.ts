export function formatLocalDateTime(value: string): string {
  return new Date(value).toLocaleString();
}
