import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule} from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AutoCompleteModule } from 'primeng/autocomplete';
import { TableModule } from 'primeng/table';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

import { AppComponent } from './app.component';
import { EditPatternsComponent } from './edit-patterns/edit-patterns.component';
import { SelectLanguageComponent } from './select-language/select-language.component';
import { ParseComponent } from './parse/parse.component';
import { AddPatternComponent } from './add-pattern/add-pattern.component';

@NgModule({
  declarations: [
    AppComponent,
    EditPatternsComponent,
    SelectLanguageComponent,
    ParseComponent,
    AddPatternComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    HttpClientModule,
    AutoCompleteModule,
    TableModule,
    FontAwesomeModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
