import { Component, OnChanges, Input } from '@angular/core';
import { ApiService } from '../api.service';
import { Language , LanguagePattern} from '../patterns.service';

@Component({
  selector: 'dh-edit-patterns',
  templateUrl: './edit-patterns.component.html',
  styleUrls: ['./edit-patterns.component.scss']
})
export class EditPatternsComponent implements OnChanges {
  @Input() language: Language;
  @Input() patternType: LanguagePattern<Language>;

  cols: { header: string, field: string }[];
  patterns: { [field: string]: { value: string, dir: 'ltr' | 'rtl' } }[];
  constructor(private apiService: ApiService) { }

  async ngOnChanges() {
    if (!this.language || !this.patternType) {
      return;
    }

    const { fields, patterns } = await this.apiService.get(this.language, this.patternType);

    this.cols = fields.map(col => ({ header: col, field: col }));
    this.patterns = patterns.map(cells => Object.assign(
      {},
      ...Object.keys(cells).map(col => ({
        [col]: {
          value: cells[col],
          dir: /[א-ת]/.test(cells[col]) ? 'rtl' : 'ltr'
        }
      }))));
  }
}
