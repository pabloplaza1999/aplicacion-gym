export const onlyLetters  = (v: string) => /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]*$/.test(v)
export const onlyDigits   = (v: string) => /^\d*$/.test(v)
export const isValidEmail = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)

/** Normalizes a UTC datetime string (with or without Z) to a proper ISO UTC string. */
export function normalizeUtcStr(s: string): string {
  const iso = s.replace(' ', 'T')
  return /[Z+]/.test(iso) ? iso : iso + 'Z'
}

export function fmtBogotaDate(utcStr: string | null | undefined): string {
  if (!utcStr) return '—'
  return new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'America/Bogota' }).format(new Date(normalizeUtcStr(utcStr)))
}
