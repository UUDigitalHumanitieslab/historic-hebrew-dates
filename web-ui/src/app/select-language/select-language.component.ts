import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { PatternsService } from '../patterns.service';
import { LanguagePatterns } from '../api.service';

export interface LanguageSelection {
  language: string;
  patternType: string;
}

@Component({
  selector: 'dh-select-language',
  templateUrl: './select-language.component.html',
  styleUrls: ['./select-language.component.scss']
})
export class SelectLanguageComponent implements OnInit {
  @Output() select = new EventEmitter<LanguageSelection>();

  selectedLanguage: string;
  selectedPattern: string;

  languageList: { name: string, display: string, direction: 'rtl' | 'ltr' }[];
  patterns: { name: string, display: string }[];

  private languages: LanguagePatterns;

  constructor(private patternsService: PatternsService) {
  }

  async ngOnInit() {
    this.languages = await this.patternsService.languages();
    this.languageList = Object.entries(this.languages).map(([name, item]) => ({
      name,
      display: item.display,
      direction: item.direction
    }));

    this.selectedLanguage = this.languageList[0].name;
    this.selectedPattern = this.languages[this.selectedLanguage].patterns[0].name;

    this.emit();
  }

  emit() {
    const patterns = this.languages[this.selectedLanguage].patterns;
    this.patterns = patterns.map((pattern) => ({
      name: pattern.name,
      display: `${pattern.name} {${pattern.key}}`
    }));
    if (!this.patterns.find(p => p.name === this.selectedPattern)) {
      this.selectedPattern = this.patterns[0].name;
    }

    this.select.emit({
      language: this.selectedLanguage,
      patternType: this.selectedPattern
    });
  }
}
