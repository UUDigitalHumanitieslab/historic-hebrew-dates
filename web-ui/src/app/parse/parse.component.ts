import { Component, OnInit, Input } from '@angular/core';
import { ApiService, Parse } from '../api.service';
import { Language, LanguagePattern, PatternsService } from '../patterns.service';
import { NotificationsService } from '../notifications.service';

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
  loading = false;

  constructor(
    private apiService: ApiService,
    private patternService: PatternsService,
    private notificationService: NotificationsService) { }

  ngOnInit() {
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
}
