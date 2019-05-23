import { TestBed } from '@angular/core/testing';

import { PatternsService } from './patterns.service';

describe('PatternsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: PatternsService = TestBed.get(PatternsService);
    expect(service).toBeTruthy();
  });
});
