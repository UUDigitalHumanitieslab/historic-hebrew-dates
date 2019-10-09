import { Injectable } from '@angular/core';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class PatternsService {

  constructor(private apiService: ApiService) { }

  languages() {
    return this.apiService.overview();
  }

  textDirection(text: string): 'rtl' | 'ltr' {
    return /[א-ת]/.test(text) ? 'rtl' : 'ltr';
  }
}
