import { Component, OnInit, Input } from '@angular/core';
import { faCheck, faCheckDouble } from '@fortawesome/free-solid-svg-icons';

import { ApiService, SearchResult } from '../api.service';
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
  searchLines: SearchResult[][];

  get dir() {
    return this.language === 'hebrew' ? 'rtl' : 'ltr';
  }

  constructor(
    private apiService: ApiService,
    private notificationService: NotificationsService) { }

  ngOnInit() {
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
          matches: item.matches,
          text: firstLine
        });

        list.push(...lines.map(line => ([{
          matches: item.matches,
          text: line
        }])));

        return list;
      }, [[]] as SearchResult[][]);
    }

    this.loading = false;
  }
}
