import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Language, LanguagePattern } from './patterns.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private httpClient: HttpClient) { }

  async get<Lang extends Language, PatternType extends LanguagePattern<Lang>>(lang: Lang, patternType: PatternType) {
    const raw = await this.httpClient.get<string[][]>(`/api/patterns/${lang}/${patternType}`).toPromise();

    // first row is the header
    const fields = raw[0];
    const patterns: { [key: string]: string }[] = [];

    for (let i = 1; i < raw.length; i++) {
      patterns.push(raw[i].reduce((dict, cell, index) => ({ ...dict, [fields[index]]: cell }), {}));
    }

    return { fields, patterns };
  }
}
