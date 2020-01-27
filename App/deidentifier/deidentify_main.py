import zipfile
from time import sleep

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
      
      for file in files:
         # read zipinfo from the file
         info = zipfile.ZipInfo(file)
         
         # read data of the file
         data = zpin.read(file)

         # data, dic, shift = master(data)  ## 2 for shifted dates. 1 to remove them completely
         data = master(data)[0]  ## 2 for shifted dates. 1 to remove them completely
         
         # write to the write mode zipfile
         zpout.writestr(info, data)
         
   return count