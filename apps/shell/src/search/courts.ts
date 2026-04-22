export const COURT_NAMES: Record<string, string> = {
  ZACC:    'Constitutional Court',
  ZASCA:   'Supreme Court of Appeal',
  ZAGPJHC: 'Gauteng HC (Johannesburg)',
  ZAGPPHC: 'Gauteng HC (Pretoria)',
  ZAWCHC:  'Western Cape HC',
  ZAKZDHC: 'KwaZulu-Natal HC (Durban)',
  ZAKZPHC: 'KwaZulu-Natal HC (Pietermaritzburg)',
  ZAECGHC: 'Eastern Cape HC (Grahamstown)',
  ZACT:    'Competition Tribunal',
  ZACAC:   'Competition Appeal Court',
}

export const COURTS = Object.keys(COURT_NAMES)

export function courtLabel(code: string): string {
  return COURT_NAMES[code] ?? code
}
