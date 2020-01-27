import zipfile
from time import sleep
import mimetypes
import numpy, cv2, os
from deidentifier.face_redact import main
from deidentifier.burnt_text_redact import main as _main

# import ml/ai models here
from deidentifier.text_deidentifier import master

def deidentify_zipfile(src_filename, dest_filename):
   
   # file count
   count = 0
   
   # open both reading and writing zipfile
   with zipfile.ZipFile(src_filename, 'r') as zpin, zipfile.ZipFile(dest_filename, 'w') as zpout:
      
      # read filelist from reading zipfile
      files = zpin.namelist()
      count = len(zpin.namelist())
      
      mime = mimetypes.MimeTypes()
      # add support for dicom images
      mime.add_type('application/dicom', '.dcm')
      
      for file in files:
         
         # get the file type
         filetype = mime.guess_type(file)[0]
         
         ##################### Model for text ###########################
         if 'text' in filetype:
            print("Deidentifying text file %s"%file)
            # read zipinfo from the file
            info = zipfile.ZipInfo(file)
            
            # read data of the file
            data = zpin.read(file)

            # data, dic, shift = master(data)  ## 2 for shifted dates. 1 to remove them completely
            data = master(data)[0]  ## 2 for shifted dates. 1 to remove them completely
            
            # write to the write mode zipfile
            zpout.writestr(info, data)
         
         #################### Model for images ###########################
         elif 'image' in filetype:
            
            print("Deidentifying image file %s"%file)
            
            # open the file
            data = zpin.read(file)
            
            # convert string data to numpy array
            npimg = numpy.frombuffer(data, dtype=numpy.uint8)
            
            # convert numpy array to image
            img = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)

            # cv2.imwrite('deidentified_'+file, img)
            new_img, detected = main(img)
            
            if not detected:
               
               # convert numpy array to image
               imge = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)
               
               new_img = _main(img, imge)
               
               
            cv2.imwrite('deidentified_'+file, new_img)
            
            # write to another zipfile
            zpout.write('deidentified_'+file, file)
            
            # delete the src image file
            os.remove('deidentified_'+file)
            
         ####################### Else the filetype is audio ##########################
         else:
            print("Deidentifying audio file %s"%file)
            pass
         
         print("Success...")
         
   return count