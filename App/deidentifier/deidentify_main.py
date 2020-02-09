import zipfile
from time import sleep
import mimetypes
import numpy, cv2, os
import timeit
from scipy.io.wavfile import write

# import ml/ai models for text deidentification
from deidentifier.text_deidentifier import master, list_returner

# import ml/ai models for image deidentification
from deidentifier.face_redact import main
from deidentifier.burnt_text_redact import main as _main

# import ml/ai models for audio deidentification
from deidentifier.speech_model.SpeechToText import speech_to_text, get_deidentified_file

''' Function to deidentify data in bulk (zip form) '''
def deidentify_zipfile(src_filename, dest_filename):
   
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

            # data, dic, shift = master(data). 2 for shifted dates. 1 to remove them completely
            # pass text string to the function
            data = deidentifyText(data)
            
            # write to the write mode zipfile
            zpout.writestr(info, data)
         
         #################### Model for images ###########################
         elif 'image' in filetype:
            
            print("Deidentifying image file %s"%file)
            
            # open the file
            image_data = zpin.read(file)
            
            # deidentify image data
            new_img = deidentifyImage(image_data)
            
            # save in deidentified file in local
            # Need to be removed after writing to zip file
            cv2.imwrite('deidentified_'+file, new_img)
            
            # write to another zipfile
            zpout.write('deidentified_'+file, file)

            # DUPLICATED IN AUDIO ALSO BECAUSE text file is not extracted
            os.remove('deidentified_'+file)
            os.remove(file)   
         ####################### Else the filetype is audio ##########################
         else:
            print("Deidentifying audio file %s"%file)
            
            # pass to audio model. Returns array of data
            deidentifyAudio(file)
            
            zpout.write('deidentified_'+file, file)
            # os.remove('deidentified_'+file)
        
         # delete the src image file
            os.remove('deidentified_'+file)
            os.remove(file)
             
         print("Success...")
      
   print("Done...")
   print("Time taken {:.2f}".format( (timeit.default_timer()-start)/60 ) )
   
   return count


''' Function to deidentify text data '''
def deidentifyText(text_data):  # text data is in form of string
   return master(text_data)[0]


''' Function to deidentify image data '''
def deidentifyImage(image_data): # image data is in form of string
   # convert string data to numpy array
   npimg = numpy.frombuffer(image_data, dtype=numpy.uint8)
   
   # convert numpy array to image
   img = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)

   # cv2.imwrite('deidentified_'+file, img)
   new_img, detected = main(img)
   
   if not detected:
      
      # convert numpy array to image
      imge = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)
      new_img = _main(img)

   return new_img


''' Function to deidentify audio data '''
# file is file name string
# make a local file for audio
def deidentifyAudio(filename):
   print("Deidentifying audio file %s"%filename)
   
   # pass to audio model. Returns text data
   transcript, timestamp = speech_to_text(filename)
   
   a = list_returner(transcript) 
   
   array = get_deidentified_file(filename, timestamp, a)
   write('deidentified_'+filename, rate=16000, data=array)