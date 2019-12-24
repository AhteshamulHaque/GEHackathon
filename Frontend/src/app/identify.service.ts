import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class IdentifyService {
  
  /* Properties of a progress bar */
  color = 'primary';
  mode = 'indeterminate';
  value = 40;
  diameter = 35;

  constructor(public snackbar: MatSnackBar, public http: HttpClient) { }

  httpPost(url, data) {
    return this.http.post<any>(url, data);
  }

  openSnackBar(message) {
    this.snackbar.open(message, "OK", {
      duration: 2000
    });
  }
}
