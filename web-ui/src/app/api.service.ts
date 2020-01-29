import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface Parse {
  expression: string;
  evaluated: string;
  error: boolean;
}

export interface SearchResult {
  text: string;
  matches: {
    parsed: string;
    eval: string;
  }[];
}

export type Search = {
  result: SearchResult[];
  error: false;
} | {
  result: string;
  error: true;
};

export interface LanguagePatterns {
  [language: string]: {
    display: string;
    direction: 'ltr' | 'rtl';
    patterns: {
      eval: string,
      key: string,
      name: string,
      dependencies?: string[]
    }[]
  };
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private httpClient: HttpClient) { }

  async overview() {
    return this.httpClient.get<LanguagePatterns>(`/api/patterns`).toPromise();
  }

  async get(lang: string, patternType: string) {
    const raw = await this.httpClient.get<string[][]>(`/api/patterns/${lang}/${patternType}`).toPromise();

    // first row is the header
    const fields = raw[0];
    const patterns: { [key: string]: string }[] = [];

    for (let i = 1; i < raw.length; i++) {
      patterns.push(raw[i].reduce((dict, cell, index) => ({ ...dict, [fields[index]]: cell }), {}));
    }

    return { fields, patterns };
  }

  async put(
    lang: string,
    patternType: string,
    rows: string[][]) {
    const result = await this.httpClient.put<{ success: boolean, message: string }>(
      `/api/patterns/${lang}/${patternType}`, {
      rows: [['type', 'pattern', 'value'], ...rows]
    }).toPromise().catch((error) => ({
      success: false,
      message: error.message
    }));

    if (!result.success) {
      return { success: false, error: result.message || 'Problem saving the results.' };
    }

    return { success: true };
  }

  async parse(
    lang: string,
    patternType: string,
    input: string,
    rows: string[][]) {
    return this.httpClient.post<Parse>(`/api/parse/${lang}/${patternType}`, {
      input,
      rows
    }).toPromise().catch((error: HttpErrorResponse) => {
      alert(error.statusText);
      console.error(error);
      return { expression: null, evaluated: null, error: true };
    });
  }

  async search(
    lang: string,
    patternType: string,
    input: string,
    rows: string[][]) {
    return this.httpClient.post<Search>(`/api/search/${lang}/${patternType}`, {
      input,
      rows
    }).toPromise().catch(() => ({ result: 'Technical problem during search.', error: true }));
  }
}
