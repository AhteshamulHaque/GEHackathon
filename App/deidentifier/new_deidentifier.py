import zipfile
from time import sleep
import mimetypes
import numpy, cv2, os
import timeit
import threading
from scipy.io.wavfile import write

# import ml/ai models for text deidentification
from deidentifier.text_deidentifier import master, list_returner

# import ml/ai models for image deidentification
from deidentifier.face_redact import main
from deidentifier.burnt_text_redact import main as _main

# import ml/ai models for audio deidentification
from deidentifier.speech_model.SpeechToText import speech_to_text, get_deidentified_file


'''############################## CLASS DEIDENTIFIER ####################################'''

class Deidentifier:   
   
   @staticmethod
   def deidentify_zipfile(self, src_filename, dest_filename):
      '''
         This function is used if admin upload zipfiles
         This function will spawn respective functions for image, text and audio
         deidentification
         Will also wait for all of them to complete
      '''
      
      # file count
      count = 0
      
      start = timeit.default_timer()
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
            print(file, filetype)
            
            # extract the file
            zpin.extract(file)
            
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
               file_obj = zpin.open(file)
               print("Deidentifying audio file %s"%file)
               
               # pass to audio model
               # Returns text data
               transcript, timestamp = speech_to_text(file_obj)
               
               a = list_returner(transcript)   

               array = get_deidentified_file(file, timestamp, a)
               file_obj.close()
               
               write('deidentified_'+file, rate=16000, data=array)
               zpout.write('deidentified_'+file, file)
               os.remove('deidentified_'+file)
         
            os.remove(file)
               
            print("Success...")
         
      print("Done...")
      print("Time taken {:.2f}".format( (timeit.default_timer()-start)/60 ) )
      
      return count
   

   def deidentify_image(self, image):
      '''
         Single image deidentification
         @param - image is a ( file_object/ binary data <- not decided )
      '''
      pass
   
   def deidentify_audio(self, audio):
      '''
         Single audio deidentification
         @param - audio is a ( file_object/ binary data <- not decided )
      '''
      pass
      
   def deidentify_text(self, text):
      '''
         Single text deidentification
         @param - text is a ( file_object/ binary data <- not decided )
      '''
      pass
      