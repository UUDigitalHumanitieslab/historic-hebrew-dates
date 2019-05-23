import { Component, OnInit, Input } from '@angular/core';
import { ApiService, Parse } from '../api.service';
import { Language, LanguagePattern, PatternsService } from '../patterns.service';

@Component({
  selector: 'dh-parse',
  templateUrl: './parse.component.html',
  styleUrls: ['./parse.component.scss']
})
export class ParseComponent implements OnInit {
  @Input() language: Language;
  @Input() patternType: LanguagePattern<Language>;
  @Input() rows: string[][];

  value: string;
  parse: Parse & { dir: 'ltr' | 'rtl' };
  loading = false;

  constructor(private apiService: ApiService, private patternService: PatternsService) { }

  ngOnInit() {
  }

  async tryParse() {
    this.parse = undefined;
    this.loading = true;
    const parse = await this.apiService.parse(this.language, this.patternType, this.value, this.rows);
    this.parse = Object.assign({
      dir: parse.evaluated && this.patternService.textDirection(parse.evaluated) || undefined
    }, parse);
    this.loading = false;
  }
}
