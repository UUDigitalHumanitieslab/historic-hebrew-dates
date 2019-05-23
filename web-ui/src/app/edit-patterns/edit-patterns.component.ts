import { Component, EventEmitter, OnChanges, Input, Output } from '@angular/core';

import { ApiService } from '../api.service';
import { Language, LanguagePattern, PatternsService } from '../patterns.service';

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

  @Output() rowsChange = new EventEmitter<string[][]>();

  cols: { header: string, field: string }[];
  patterns: Pattern[];

  constructor(private apiService: ApiService, private patternService: PatternsService) { }

  async ngOnChanges() {
    if (!this.language || !this.patternType) {
      return;
    }

    this.rowsChange.next(undefined);
    const { fields, patterns } = await this.apiService.get(this.language, this.patternType);

    this.cols = fields.map(col => ({ header: col, field: col }));
    this.patterns = patterns.map(cells => Object.assign(
      {},
      ...Object.keys(cells).map(col => ({
        [col]: {
          value: cells[col],
          dir: this.patternService.textDirection(cells[col]),
          modified: false
        }
      }))));

    this.nextRows();
  }

  onCellChange(pattern: Pattern, column: string) {
    const patternCell = pattern[column];
    patternCell.dir = this.patternService.textDirection(patternCell.value);
    patternCell.modified = true;

    this.nextRows();
  }

  private nextRows() {
    this.rowsChange.next(
      this.patterns.map(pattern =>
        this.cols.map(col => pattern[col.field].value)));
  }
}
