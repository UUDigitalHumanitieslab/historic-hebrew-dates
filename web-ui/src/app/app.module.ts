import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { TableModule } from 'primeng/table';

import { AppComponent } from './app.component';
import { EditPatternsComponent } from './edit-patterns/edit-patterns.component';
import { SelectLanguageComponent } from './select-language/select-language.component';
import { ParseComponent } from './parse/parse.component';

@NgModule({
  declarations: [
    AppComponent,
    EditPatternsComponent,
    SelectLanguageComponent,
    ParseComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    TableModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
