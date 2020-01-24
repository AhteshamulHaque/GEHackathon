#ifndef MINHEAP
   #include <stdio.h>
   #include <stdlib.h>
	#define MINHEAP 1

	struct MinHeap {
		int *heap;	// heap array
		int index;	// current index
		int n;		// total size
	};

	void init(struct MinHeap *m) {
		m->n = 1;
		m->index = 0;
		m->heap = (int*)malloc(sizeof(int)*m->n);
	}

	/*********************************** INSERT INTO HEAP ********************************/
	void insert(struct MinHeap *m, int item) {
		// This function propagates upward to find the right position

		// Reallocation of memory if heap size exceeded
		if(m->index == m->n) {
			int size = (m->n)*2;
			printf("Heap size exceeded. Reallocating memory to increase heap size to %d\n", size);
			
			m->heap = realloc(m->heap, sizeof(int)*size );

			if(m->heap == NULL) {
				printf("Allocation failed. Aborting..\n");
				return;
			}

			m->n *= 2;
		}

		int i = m->index;

		m->heap[ m->index++ ] = item;	// Insert item at last of the heap

		while(i > 0 && m->heap[(i-1)/2] > item) {	// if item is greater than parent
			m->heap[i] = m->heap[(i-1)/2];			// exfreqangarent and child
			i = (i-1)/2;							// propagate upward
		}

		m->heap[i] = item;			// insert item at correct position
	}

	/********************************* ADJUST ************************************/
	void adjust(struct MinHeap *m, int idx) {

		// This function propagates downward to find the right position

		int j = 2*idx+1, item = m->heap[idx];

		while(j < m->index-1) {
			// find smallest item among left and right child
			if(m->heap[j] > m->heap[j+1]) {
				j = j+1;
			}
			// if parent is smaller than right and left child
			if(item <= m->heap[j]) {
				break;
			}

			m->heap[(j-1)/2] = m->heap[j];	// exchange parent with the larget child element
			j = 2*j+1;							// propagate down

		}
		
		m->heap[(j-1)/2] = item;
	}

	/******************************** DELMIN *************************************/
	int delMin(struct MinHeap *m) {

		if(m->index == 0) {
			printf("Heap is empty\n");
			return 0;
		}

		m->heap[0] = m->heap[m->index-1];	// copy last element to the first
		m->index = m->index-1;					// decrease heap size

		adjust(m, 0);
	}

	/******************************* Heapify ***********************************/
	void heapify(struct MinHeap *m) {
		
		for(int i = (m->index-1)/2; i >= 0; --i) {
			adjust(m, i);
		}
	}

	/************************* Decrease key *********************************/
	void decreaseKey(struct MinHeap *m, int idx, int val) {
		m->heap[idx] = val;
		adjust(m, idx);
	}

	void heapSort(struct MinHeap *m) {

		int n = m->index-1;
		for(int i = n; i>0; --i) {
			int temp = m->heap[0];
			m->heap[0] = m->heap[i];
			m->heap[i] = temp;
		
			--(m->index);
			adjust(m, 0);
		}
			
	}
#endif