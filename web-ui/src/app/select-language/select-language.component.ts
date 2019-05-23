import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { PatternsService, Language, LanguagePattern } from '../patterns.service';

export interface LanguageSelection<T extends Language> {
  language: T;
  patternType: LanguagePattern<T>;
}

@Component({
  selector: 'dh-select-language',
  templateUrl: './select-language.component.html',
  styleUrls: ['./select-language.component.scss']
})
export class SelectLanguageComponent implements OnInit {
  @Output() select = new EventEmitter<LanguageSelection<any>>();

  selectedLanguage: Language;
  selectedPattern: string;

  languageList: { name: Language, display: string }[];
  patterns: { name: string, display: string }[];

  private languages: ReturnType<PatternsService['languages']>;

  constructor(private patternsService: PatternsService) {
  }

  async ngOnInit() {
    this.languages = await this.patternsService.languages();
    this.languageList = Object.keys(this.languages)
      .map((name: Language) => ({ name, display: this.languages[name].display }));

    this.selectedLanguage = this.languageList[0].name;
    this.selectedPattern = Object.keys(this.languages[this.selectedLanguage])[0];

    this.emit();
  }

  emit() {
    const patterns = this.languages[this.selectedLanguage].patterns;
    this.patterns = Object.keys(patterns).map((pattern) => ({ name: pattern, display: patterns[pattern] }));
    if (!this.patterns.find(p => p.name === this.selectedPattern)) {
      this.selectedPattern = this.patterns[0].name;
    }

    this.select.emit({
      language: this.selectedLanguage,
      patternType: this.selectedPattern
    });
  }
}
