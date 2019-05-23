import { Component, OnChanges, Input } from '@angular/core';

import { ApiService } from '../api.service';
import { Language, LanguagePattern } from '../patterns.service';

interface Pattern {
  [field: string]: {
    value: string,
    dir: 'ltr' | 'rtl',
    modified: boolean
  };
}

@Component({
  selector: 'dh-edit-patterns',
  templateUrl: './edit-patterns.component.html',
  styleUrls: ['./edit-patterns.component.scss']
})
export class EditPatternsComponent implements OnChanges {
  @Input() language: Language;
  @Input() patternType: LanguagePattern<Language>;

  cols: { header: string, field: string }[];
  patterns: Pattern[];
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
          dir: this.cellDirection(cells[col]),
          modified: false
        }
      }))));
  }

  onCellChange(pattern: Pattern, column: string) {
    const patternCell = pattern[column];
    patternCell.dir = this.cellDirection(patternCell.value);
    patternCell.modified = true;
  }

  private cellDirection(text: string) {
    return /[א-ת]/.test(text) ? 'rtl' : 'ltr';
  }
}
