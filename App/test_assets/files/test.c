#include <stdio.h>

int minJumps(int arr[], int n) {
    int jump = 0;
    int i, j, range = 0, max_idx;

    for(i = 0; i < n;) {
        
        max_idx = i+1;

        if(arr[i] == 0) {
            jump = -1;
            break;
        }

        range = i+arr[i];

        // find max range in range(i, i+arr[i]);
        if(range > n-1) {
            break;
        }

        for(j = i+1; j < n && j <= range; ++j) {

            if(j+arr[j] > max_idx+arr[max_idx]) {
                max_idx = j;
            }
        }

        i = j;
        jump++;
    }

    return jump;

}

int main() {
    int arr[] = {1, 3, 5, 8, 9, 2, 6, 7, 6, 8, 9};
    int n = sizeof(arr)/sizeof(arr[0]);
    int result = minJumps(arr, n);

    if(result == -1) {
        printf("Not possible\n");
    } else {
        printf("Minimum jumps = %d\n", result);
    }

    return 0;
}