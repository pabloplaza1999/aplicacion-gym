export const onlyLetters  = (v: string) => /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]*$/.test(v)
export const onlyDigits   = (v: string) => /^\d*$/.test(v)
export const isValidEmail = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)

/** Normalizes a UTC datetime string (with or without Z) to a proper ISO UTC string. */
export function normalizeUtcStr(s: string): string {
  const iso = s.replace(' ', 'T')
  return /[Z+]/.test(iso) ? iso : iso + 'Z'
}

/**
 * Normalizes a backend date/datetime field to Bogotá local time (-05:00) so the
 * stored calendar date is preserved on display (no timezone drift).
 * Accepts both date-only ("2026-07-20", as returned by /dashboard) and naive
 * datetime ("2026-07-20T00:00:00", as returned by /current-membership).
 * Strings already carrying timezone info (Z or ±HH:MM) are returned unchanged.
 */
export function normalizeDateStr(s: string): string {
  const iso = s.replace(' ', 'T')
  if (/Z|[+-]\d{2}:\d{2}$/.test(iso)) return iso
  const withTime = iso.includes('T') ? iso : iso + 'T00:00:00'
  return withTime + '-05:00'
}

export function fmtBogotaDate(utcStr: string | null | undefined): string {
  if (!utcStr) return '—'
  const d = new Date(normalizeDateStr(utcStr))
  if (isNaN(d.getTime())) return '—'
  return new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'America/Bogota' }).format(d)
}
