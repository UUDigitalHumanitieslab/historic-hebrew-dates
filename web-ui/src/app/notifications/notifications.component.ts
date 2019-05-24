import { Component, OnDestroy } from '@angular/core';
import { NotificationsService, NotificationType } from '../notifications.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'dh-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.scss']
})
export class NotificationsComponent implements OnDestroy {
  dir: 'ltr' | 'rtl';
  message: string;
  type: NotificationType;
  subscription: Subscription;

  constructor(notificationsService: NotificationsService) {
    this.subscription = notificationsService.observable.subscribe(notification => {
      if (!notification) {
        this.message = undefined;
      } else {
        this.dir = notification.dir;
        this.message = notification.message;
        this.type = notification.type;
      }
    });
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }
}
