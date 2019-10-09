import { Component } from '@angular/core';

import { faSave } from '@fortawesome/free-solid-svg-icons';

import { LanguageSelection } from './select-language/select-language.component';
import { ApiService } from './api.service';
import { NotificationsService } from './notifications.service';

@Component({
  selector: 'dh-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'historic-hebrew-dates-ui';
  language: string;
  patternType: string;
  rows: string[][] = undefined;
  saveIcon = faSave;
  saving = false;

  constructor(private apiService: ApiService, private notificationService: NotificationsService) {
  }

  select(selection: LanguageSelection) {
    this.language = selection.language;
    this.patternType = selection.patternType;
  }

  async save() {
    this.saving = true;
    const result = await this.apiService.put(this.language, this.patternType, this.rows);
    this.saving = false;
    this.notificationService.show(
      result.success ? 'Successfully saved patterns!' : result.error,
      result.success ? 'success' : 'error');
  }
}
