import { Component, Output, EventEmitter } from '@angular/core';
import { IdentifyService } from '../identify.service';
import { FormControl, Validators } from '@angular/forms';

@Component({
  selector: 'app-reidentify',
  templateUrl: './reidentify.component.html',
  styles: []
})
export class ReidentifyComponent {

  FLAGS = {
    isDeidentificationInProgress: false
  };

  key = new FormControl('', [Validators.required]);
  identify = new FormControl('', [Validators.required]);
  @Output() public resultEvent = new EventEmitter();


  constructor(public service: IdentifyService) { }

  identifyData() {
    
    if(this.key.valid) {

      this.FLAGS.isDeidentificationInProgress = true;

      const fd = new FormData();
      fd.append('key', this.key.value);

      this.service.httpPost('http://localhost:5000/api/reidentify', fd)
        .subscribe(
          data => {
            // send result to parent element
            this.resultEvent.emit(data.file);
          },
          error => console.log(error),
          () => this.FLAGS.isDeidentificationInProgress = false
        );

    } else {
      this.service.openSnackBar("Key and identifying fields are required");
    }
  }

}
