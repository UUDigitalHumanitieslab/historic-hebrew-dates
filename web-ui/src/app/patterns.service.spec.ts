import { TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';

import { PatternsService } from './patterns.service';
import { ApiService } from './api.service';

describe('PatternsService', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [
      ApiService,
      {
        provide: HttpClient,
        useValue: {}
      }]
  }));

  it('should be created', () => {
    const service: PatternsService = TestBed.get(PatternsService);
    expect(service).toBeTruthy();
  });
});
