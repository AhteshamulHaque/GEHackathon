import cv2

_dir = 'deidentifier/'
face_cascade = cv2.CascadeClassifier(_dir+'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(_dir+'haarcascade_eye.xml')  


def main(img):
	
	faces = face_cascade.detectMultiScale(img, 1.2, 1)
	flag = 0
 
	for (x, y, w, h) in faces:
		detected = img[y:y+h,x:x+w]
		eyes = eye_cascade.detectMultiScale(detected)  
		if len(eyes) > 0:
			img[y:y+h,x:x+w] = 0
			flag = 1
	
	return img, flag
	