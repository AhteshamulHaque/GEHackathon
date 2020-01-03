import { Component } from '@angular/core';
import { IdentifyService } from './identify.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styles: [`
    .example-stretched-tabs {
      padding-top: 30px;
    }
  `]
})
export class AppComponent {
  title = 'GE Health Care'; 

  isResult = false;
  result = '';
  resultToShow = '';

  constructor(public service: IdentifyService) {}

  displayResult(data) {
    this.result = data;
    this.resultToShow = this.result.replace(/\n/g, '<br>');
    this.isResult = true;
  }

  copyTextToClipboard() {
    this.service.copy(this.result);
    this.service.openSnackBar("Text Copied");
  }
  
}
