import { Component, EventEmitter, OnChanges, Input, Output, ViewChild } from '@angular/core';
import { Table } from 'primeng/table';

import { faTrashAlt, faTrashRestoreAlt } from '@fortawesome/free-solid-svg-icons';

import { ApiService } from '../api.service';
import { PatternsService } from '../patterns.service';

interface Pattern {
  deleted: boolean;
  fields: {
    [field: string]: {
      value: string,
      original: string,
      dir: 'ltr' | 'rtl',
      modified: boolean
    }
  };
}

@Component({
  selector: 'dh-edit-patterns',
  templateUrl: './edit-patterns.component.html',
  styleUrls: ['./edit-patterns.component.scss']
})
export class EditPatternsComponent implements OnChanges {
  @Input() language: string;
  @Input() patternType: string;

  @Output() rowsChange = new EventEmitter<string[][]>(true);

  @ViewChild(Table)
  table: Table;

  cols: { header: string, field: string }[];
  patterns: Pattern[];
  dir: 'ltr' | 'rtl' = 'ltr';
  types: string[];

  restoreIcon = faTrashRestoreAlt;
  deleteIcon = faTrashAlt;

  constructor(private apiService: ApiService, private patternService: PatternsService) { }

  async ngOnChanges() {
    if (!this.language || !this.patternType) {
      return;
    }

    this.rowsChange.next(undefined);
    this.dir = this.language === 'hebrew' ? 'rtl' : 'ltr';
    const { fields, patterns } = await this.apiService.get(this.language, this.patternType);

    this.cols = fields.map(col => ({ header: col, field: col }));
    this.patterns = patterns.map(cells => ({
      deleted: false,
      fields: Object.assign(
        {},
        ...Object.keys(cells).map(col => ({
          [col]: {
            value: cells[col],
            original: cells[col],
            dir: this.patternService.textDirection(cells[col]),
            modified: false
          }
        })))
    }));

    this.nextRows();
  }

  onCellChange(pattern: Pattern, column: string) {
    const patternCell = pattern.fields[column];
    patternCell.dir = this.patternService.textDirection(patternCell.value);
    patternCell.modified = patternCell.original !== patternCell.value;

    this.nextRows();
  }

  onCellKeydown(row: HTMLTableRowElement, column: string, event: KeyboardEvent) {
    let jumpRow: Element;
    switch (event.keyCode) {
      case 38:
        // up
        jumpRow = row.previousElementSibling;
        break;
      case 40:
        // down
        jumpRow = row.nextElementSibling;
        break;

      default:
        return;
    }

    if (jumpRow) {
      const cell = jumpRow.children[this.cols.findIndex(c => c.field === column)] as HTMLElement;
      event.preventDefault();
      cell.click();
    }
  }

  toggleDelete(pattern: Pattern) {
    pattern.deleted = !pattern.deleted;

    this.nextRows();
  }

  add(values: { [col: string]: string }) {
    const type = values.type;
    const lastIndex = this.findLastPatternIndex(type);
    const newRow = {
      deleted: false, fields: Object.assign({},
        ...this.cols.map(col => ({
          [col.field]: {
            value: values[col.field],
            dir: this.patternService.textDirection(values[col.field]),
            modified: true
          }
        })))
    };
    if (lastIndex === -1) {
      this.patterns.push(newRow);
    } else {
      this.patterns.splice(lastIndex + 1, 0, newRow);
    }

    this.nextRows();
  }

  findLastPatternIndex(type: string) {
    for (let i = this.patterns.length - 1; i >= 0; i--) {
      if (this.patterns[i].fields.type.value === type) {
        return i;
      }
    }

    return -1;
  }

  private nextRows() {
    this.rowsChange.next(
      this.patterns
        .filter(pattern => !pattern.deleted)
        .map(pattern => this.cols.map(col => pattern.fields[col.field].value)));

    this.types = Array.from(new Set(
      this.patterns.map(pattern => pattern.fields.type.value)));
  }
}
