import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class PatternsService {

  constructor() { }

  languages() {
    return {
      hebrew: {
        display: 'Hebrew',
        patterns:
        {
          date_types: 'Date Types',
          dates: 'Dates',
          months: 'Months',
          numerals: 'Numerals'
        }
      },
      dutch: {
        display: 'Dutch',
        patterns: {
          dates: 'Dates',
          numerals: 'Numerals'
        }
      }
    };
  }

  textDirection(text: string): 'rtl' | 'ltr' {
    return /[א-ת]/.test(text) ? 'rtl' : 'ltr';
  }
}

export type Language = keyof ReturnType<PatternsService['languages']>;
export type LanguagePattern<T extends Language> = keyof ReturnType<PatternsService['languages']>[T]['patterns'];
