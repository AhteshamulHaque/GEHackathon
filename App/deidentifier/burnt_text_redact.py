from pytesseract import pytesseract
import cv2
import numpy as np
import timeit 

def text_detect(img,ele_size): 

	img_sobel = cv2.Sobel(img,cv2.CV_8U,1,0)
	img_threshold = cv2.threshold(img_sobel,0,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY)
	element = cv2.getStructuringElement(cv2.MORPH_RECT,ele_size)
	img_threshold = cv2.morphologyEx(img_threshold[1],cv2.MORPH_CLOSE,element)
	res = cv2.findContours(img_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	if cv2.__version__.split(".")[0] == '3':
		_, contours, hierarchy = res
	else:
		contours, hierarchy = res
	Rect = [cv2.boundingRect(i) for i in contours if i.shape[0]>100]
	RectP = [(int(i[0]-i[2]*0.08),int(i[1]-i[3]*0.08),int(i[0]+i[2]*1.1),int(i[1]+i[3]*1.1)) for i in Rect]
	return RectP


def euclidean(x1,y1,x2,y2):
	return ((x1-x2)**2+(y1-y2)**2)**(0.5)

def remove_noise_and_smooth(img):
	filtered = cv2.adaptiveThreshold(img.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 41)
	kernel = np.ones((1, 1), np.uint8)
	opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
	closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
	or_image = cv2.bitwise_or(img, closing)
	return or_image

def main(img, imge):

	string = pytesseract.image_to_string(img)
	coord = pytesseract.image_to_boxes(img)
	if string != '':
		x0,y0=img.shape
		coord=coord.split('\n')
		
		for i in coord:
			j = i.split(' ')
			x3 = int(j[2])
			y3 = int(j[1])
			x4 = int(j[4])
			y4 = int(j[3])
			imge[x0-x4 : x0-x3 , y3-10: y4+10] = 0


	rect = text_detect(img,ele_size=(8,2))
	rectangles=[]
	for i in range(len(rect)):
		rectangles.append(list(rect[i]))

	rect_sorted = sorted(rectangles)
	n,m=img.shape


	cluster=[]
	for i in rect_sorted:
		flag=0
		x1=i[1]
		y1=i[0]
		x2=i[3]
		y2=i[2]
		for j in range(len(cluster)):
			d1=euclidean(x1,y1,cluster[j][1],cluster[j][0])
			d2=euclidean(x1,y1,cluster[j][3],cluster[j][2])
			d3=euclidean(x2,y2,cluster[j][1],cluster[j][0])
			d4=euclidean(x2,y2,cluster[j][3],cluster[j][2])
			if min(d1,d2,d3,d4)<100:
				cluster[j][1] = min(x1,x2,cluster[j][1],cluster[j][3])
				cluster[j][0] = min(y1,y2,cluster[j][0],cluster[j][2])
				cluster[j][3] = max(x1,x2,cluster[j][1],cluster[j][3])
				cluster[j][2] = max(y1,y2,cluster[j][0],cluster[j][2])
				flag=1
		if flag==0:
			cluster.append(i)

	tokens=[]
	for roi in cluster:
		x1=max(roi[1],0)
		y1=max(roi[0],0)
		x2=min(roi[3],n)
		y2=min(roi[2],m)
		string = pytesseract.image_to_string(img[x1:x2,y1:y2])
		coord = pytesseract.image_to_boxes(img[x1:x2,y1:y2])
		
		if string != '':
			x0,y0=img[x1:x2,y1:y2].shape
			coord=coord.split('\n')

			
			for i in coord:
				j = i.split(' ')
				x3 = int(j[2])
				y3 = int(j[1])
				x4 = int(j[4])
				y4 = int(j[3])
				imge[x1+x0-x4 : x1+x0-x3 , y1+y3-10: y1+y4+10] = 0

				
		string2 = pytesseract.image_to_string(remove_noise_and_smooth(img[x1:x2,y1:y2]))
		coord2 = pytesseract.image_to_boxes(remove_noise_and_smooth(img[x1:x2,y1:y2]))
		if string2 != '':
			x0,y0=img[x1:x2,y1:y2].shape
			coord2=coord2.split('\n')
		
			for i in coord2:
				j = i.split(' ')
				x3 = int(j[2])
				y3 = int(j[1])
				x4 = int(j[4])
				y4 = int(j[3])
				imge[x1+x0-x4 : x1+x0-x3 , y1+y3-10: y1+y4+10] = 0

	return imge

