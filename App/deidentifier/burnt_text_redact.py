from pytesseract import pytesseract
import cv2
import numpy as np
from deidentifier.text_deidentifier import list_returner


def main(img):

	string = pytesseract.image_to_string(img)
	coord = pytesseract.image_to_boxes(img)
 
	if string != '':
		x0,y0=img.shape
		coord=coord.split('\n')
		
		for i in coord:
			j = i.split(' ')
			if j[0].isalnum():
				x3 = int(j[2])-20
				y3 = int(j[1])-20
				x4 = int(j[4])+20
				y4 = int(j[3])+20
				img[x0-x4 : x0-x3 , y3: y4] = 0
	
	return img