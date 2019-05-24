import { Component, EventEmitter, Input, OnChanges, Output } from '@angular/core';

@Component({
  selector: 'dh-add-pattern',
  templateUrl: './add-pattern.component.html',
  styleUrls: ['./add-pattern.component.scss']
})
export class AddPatternComponent implements OnChanges {
  @Input() types: string[];
  @Output() add = new EventEmitter<{
    type: string,
    pattern: string,
    value: string
  }>(true);

  suggestedTypes: string[];

  type: string;
  pattern: string;
  value: string;

  constructor() { }

  suggestTypes(event: { query: string }) {
    const search = event.query.toLowerCase();
    this.suggestedTypes = this.types.filter(t => t.toLowerCase().includes(search));
  }

  ngOnChanges() {
    this.suggestedTypes = this.types;
  }

  addNext() {
    this.add.next({
      type: this.type,
      pattern: this.pattern,
      value: this.value
    });
  }
}
