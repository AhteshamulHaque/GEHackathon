import { Component, Output, EventEmitter } from '@angular/core';
import { IdentifyService } from '../identify.service';

@Component({
  selector: 'app-deidentify',
  templateUrl: './deidentify.component.html',
  styles: []
})
export class DeidentifyComponent {

  /* flags for progress spinner */
  color = 'primary';
  mode = 'indeterminate';
  value = 40;
  diameter = 35;

  FLAGS = {
    isDeidentificationInProgress: false,
    isKeyGenerated: false
  };

  fileToUpload = null;
  key = '';
  @Output() public resultEvent = new EventEmitter();

  constructor(public service: IdentifyService) {}

  /* Function to select a filename */
  onFileSelected(event) {

    const filename: any = document.querySelector('#filename');

    this.FLAGS.isKeyGenerated = false;
    this.fileToUpload = event.target.files[0];
    filename.innerText = event.target.files[0].name;

  }

  /* Function to send file and get key and deIdentified result */
  getDeIdentifiedData() {

    if(this.fileToUpload) {

      this.FLAGS.isDeidentificationInProgress = true;

      const fd = new FormData();
      fd.append('file', this.fileToUpload, this.fileToUpload.name);

      this.service.httpPost("http://localhost:5000/api/deidentify", fd)
        .subscribe(
          data => {
            this.FLAGS.isKeyGenerated = true;
            this.key = data.key;

            // send deidentified file content to parent element
            this.resultEvent.emit(data.file);
          },
          error => console.log(error),
          () => this.FLAGS.isDeidentificationInProgress = false
      );

    } else {
      this.service.openSnackBar("First select a file to deidentify");
    }

  }
  
  copyKeyToClipboard() {
    this.service.copy(this.key);
    this.service.openSnackBar("Key copied");
  }

}
