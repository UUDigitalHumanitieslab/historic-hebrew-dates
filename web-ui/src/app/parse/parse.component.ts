import { Component, OnInit, Input } from '@angular/core';
import { faCheck, faCheckDouble } from '@fortawesome/free-solid-svg-icons';

import { ApiService, SearchResult } from '../api.service';
import { PatternsService } from '../patterns.service';
import { NotificationsService } from '../notifications.service';


@Component({
  selector: 'dh-parse',
  templateUrl: './parse.component.html',
  styleUrls: ['./parse.component.scss']
})
export class ParseComponent implements OnInit {
  @Input() language: string;
  @Input() patternType: string;
  @Input() rows: string[][];

  checkDoubleIcon = faCheckDouble;
  checkIcon = faCheck;
  value: string;
  loading = false;
  mode: 'parse' | 'search' = 'parse';
  searchLines: SearchResult[][];

  get dir() {
    return this.language === 'hebrew' ? 'rtl' : 'ltr';
  }

  constructor(
    private apiService: ApiService,
    private patternService: PatternsService,
    private notificationService: NotificationsService) { }

  ngOnInit() {
  }

  toggleMode() {
    this.searchLines = null;
    this.mode = this.mode === 'parse' ? 'search' : 'parse';
    // split or merge lines using three spaces
    if (this.mode === 'parse') {
      this.value = this.value.split('\n').join('   ').replace('\r', '');
    } else {
      this.value = this.value.split('   ').join('\n');
    }
  }

  async tryParse() {
    this.loading = true;
    const parse = await this.apiService.parse(this.language, this.patternType, this.value, this.rows);
    let message: string;
    const dir = parse.evaluated && this.patternService.textDirection(parse.evaluated) || undefined;
    if (parse.expression) {
      message = `<span title="expression value">${parse.expression}</span> ${dir === 'ltr' ? '→' : '←'} <span
      title="evaluated">${parse.evaluated}</span>`;
    } else {
      message = 'No pattern matched!';
    }
    this.notificationService.show(message, parse.expression ? 'success' : 'error', dir);
    this.loading = false;
  }

  async trySearch() {
    this.loading = true;
    this.searchLines = null;
    this.notificationService.clear();
    const search = await this.apiService.search(this.language, this.patternType, this.value, this.rows);

    if (search.error) {
      this.notificationService.show(search.result, 'error', 'ltr');
    } else {
      const result = search.result as SearchResult[];

      // splits the lines
      this.searchLines = result.reduce((list, item) => {
        const lines = item.text.split('\n');
        const last = list[list.length - 1];
        const firstLine = lines.shift();
        last.push({
          eval: item.eval,
          parsed: item.parsed,
          text: firstLine
        });

        list.push(...lines.map(line => ([{
          eval: item.eval,
          parsed: item.parsed,
          text: line
        }])));

        return list;
      }, [[]] as SearchResult[][]);
    }
    this.loading = false;
  }
}
