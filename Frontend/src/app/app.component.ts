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

  constructor(public service: IdentifyService) {}

  displayResult(data) {
    this.result = JSON.stringify(data);
    this.isResult = true;
  }

  copyTextToClipboard(result) {
    // result.select();
    // document.execCommand("copy");
    this.service.openSnackBar("Text Copied");
  }
  
}
