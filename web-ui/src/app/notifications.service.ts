import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type NotificationType = 'success' | 'error' | 'info';
@Injectable({
  providedIn: 'root'
})
export class NotificationsService {
  private subject = new BehaviorSubject<{ dir: 'ltr' | 'rtl', message: string, type: NotificationType }>(undefined);

  observable = this.subject.asObservable();

  constructor() { }

  clear() {
    this.subject.next(undefined);
  }

  show(message: string, type: NotificationType, dir: 'ltr' | 'rtl' = 'ltr') {
    this.subject.next({ message, type, dir });
  }
}
