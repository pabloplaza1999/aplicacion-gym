export const onlyLetters  = (v: string) => /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]*$/.test(v)
export const onlyDigits   = (v: string) => /^\d*$/.test(v)
export const isValidEmail = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)
