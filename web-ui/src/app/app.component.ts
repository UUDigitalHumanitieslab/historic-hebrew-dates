import { Component } from '@angular/core';
import { Language } from './patterns.service';
import { LanguageSelection } from './select-language/select-language.component';

@Component({
  selector: 'dh-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'historic-hebrew-dates-ui';
  language: string;
  patternType: string;

  select(selection: LanguageSelection<Language>) {
    this.language = selection.language;
    this.patternType = selection.patternType;
  }
}
