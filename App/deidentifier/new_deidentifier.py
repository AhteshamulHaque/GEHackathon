import zipfile
from time import sleep
import threading

# import ml/ai models here

class Deidentifier:
   
   def __init__(self):
      pass
   
   
   def deidentify_zipfile(self, src_filename, dest_filename):
      '''
         This function is used if admin upload zipfiles
         This function will spawn respective functions for image, text and audio
         deidentification
         Will also wait for all of them to complete
      '''
      
      # file count
      count = 0
      
      # open both reading and writing zipfile
      with zipfile.ZipFile(src_filename, 'r') as zpin, zipfile.ZipFile(dest_filename, 'w') as zpout:
         
         # read filelist from reading zipfile
         files = zpin.namelist()
         count = len(zpin.namelist())
         
         for file in files:
            
            # read zipinfo from the file
            info = zipfile.ZipInfo(file)
            
            # open file object
            ########### File can be opened the traditional way #################
            # fp = zpin.open(file)
            
            # read data of the file
            data = zpin.read(file)
            
            # deidentify here
            print("Deidentifying %s"%file)
            sleep(0.3)
            
            print("Done...")
            
            # write to anr zipfile
            zpout.writestr(info, data)
            
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
      