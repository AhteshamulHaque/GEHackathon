
## function to extract regular expression patterns(strg) 
## form the given string(st)

## We are here using spacy style regex matcher 

def regex_extractor(strg,doc,st):
#  print("in")  
  a=[]
  expression=strg
  for match in re.finditer(expression, doc.text):
    start, end = match.span()
    span = doc.char_span(start, end)
    b=[]
    b.append(st[start:end])
    b.append(start)
    b.append(end)
  #  print(b)
    a.append(b)
#  print("out")  
  return(a)     # returning a list of list containing txt,start_ind,end_index
                # of the matched pattern

## string:- Original String
## nlp:- spacy model trained on english web data
## nlp2:- Retrained spacy en_core_web_sm model on medical data (check final_training_data file)
## choice:- 1 for completing removing dates fron text except year.
##          2 for shifting the dates to protect the information without loss of valuable information(more preffered)

def deidentifier(xml_content,nlp,nlp3,choice):
    
    root = ET.fromstring(xml_content)
    st=root.find('TEXT').text
    
    doc=nlp(root.find('TEXT').text)        ## spacy object containg processed string i.e string after passing through default en_core_web_sm spacy model.
    st=root.find('TEXT').text              ## st=original string
    
  #  print("1")
    
   # time=['YEAR','AGO', 'YEARS', 'AGE', 'AGES', 'MONTH', 'MONTHS', 'DECADE', 'CENTURY', 'WEEK', 'DAILY', 'DAY', 'DAYS', 'NIGHT', 'NIGHTS', 'WEEKLY', 'MONTHLY', 'YEARLY']
    address_identifier=['st','plot','crossing','wing','complex','campus','theatre','highway','cottage','shop','arcade','estate','paradise','mandir','masjid','apt','gaon','crossing','opp','niwas','mahal','plaza','crossing','cinema','aawas','chamber','chambers','compound','drive','rasta','palace','road','block','gali','sector','flr','floor','path','near','oppo','bazar','house','nagar','bypass','bhawan','street','rd','sq','flat','lane','gali','circle','bldg','ave','mandal','avenue','tower','nagar','marg','chowraha','lane','heights','park','garden','gate','villa','market','apartment','chowk']
    
    date_id=['january','fabruary','march','april','may','june','july','august','september','october','november','december','jan','feb','mar','apr','may','jun','aug','sept','oct','nov','dec']
    
    ## regex extractor gets a regex string,doc,original string and returns a list of list containing matched pattern along with
    ## start and end index of the pattern.
   # mail_list=regex_extractor(r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])",doc,st)    
  #  print(mail_list)
    date_list1=regex_extractor(r"\D([0-9]{4}|[0-9]{1,2})(\/|-)[0-9]{1,2}(\/|-)([0-9]{1,2}|[0-9]{4})\D",doc,st)
    
    
    
    for i in range(len(date_list1)):
        date_list1[i][1]=date_list1[i][1]+1
        date_list1[i][2]=date_list1[i][2]-1
        date_list1[i][0]=st[date_list1[i][1]:date_list1[i][2]]
    
    ## If the choice is 1(remove the dates except year) this part of the program executes.
    
    if(choice==1):
        for a in date_list1:
            count=0
            for i in range(a[1],a[1]+4):
                if(st[i].isnumeric()):
                    count=count+1
            if(count==4):
                st=st[:a[1]+4]+'X'*(a[2]-a[1]-4)+st[a[2]:] 
            else:
                count=0
                for j in range(a[2],a[2]-5,-1):
                    if(st[j].isnumeric()):
                        count=count+1
                # print("count",count)        
                if(count==4):
                    # print(st[a[1]:a[2]])
                    st=st[:a[1]]+'X'*(a[2]-4-a[1])+st[a[2]-4:]
                elif(count==3):
                    st=st[:a[1]]+'X'*(a[2]-2-a[1])+st[a[2]-2:]
                else:
                    st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
                    
                    
    ## If the choice is 2(shifting the dates by a value)  this part of code executes and returns a list of shifted dates
    ## along with the shift encountered.
    shifted_datelist=[]
    temp=0
    k=0
    random_val=randint(1,60)   ## getting a random number to shift all the dates by that number
    if(choice==2):
        for kk in range(len(date_list1)):
            llst=[]
            text=date_list1[kk][0]
            front=date_list1[kk][1]+k
            back=date_list1[kk][2]+k 
        
        ### to shift the dates we are convering all the dates to pandas datetime and then by using pandas timedelta 
        ##  we can get the shifted dates.
            new_date=pd.to_datetime(text, infer_datetime_format=True,errors='ignore') 
            if(type(new_date)!=str):
              #  print(new_date)
              #  print(type(new_date))
                new_date=new_date+timedelta(days=random_val)
              #  print(str(new_date)[:-9])
                st=st[:front]+str(new_date)[:-9]+st[back:]
                k=k+(len(str(new_date)[:-9])-len(text))
                llst.append(str(new_date)[:-9])
                llst.append(front)
                llst.append(front+len(str(new_date)[:-9]))
                shifted_datelist.append(llst)
               # k=k+(10-len(text))
    doc=nlp(st)
    ## function call to extract mail,ip address, and aadhar number form the text. 
  #  print("2")
  #  print(st)
    mail_list=regex_extractor(r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])",doc,st)    
    # print(mail_list)
    ip_list=regex_extractor(r"\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",doc,st)    
  #  print(st)
    aadhar_list=regex_extractor(r"(\d{4}(\s|\-)\d{4}(\s|\-)\d{4})",doc,st)
    
    ## replacing all the matched pattern to protect the information.
    
    for a in ip_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in mail_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:] 
    for a in aadhar_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
   

  #  print('3')
    ## Function call to extract urls and license plate numbers form the text
    doc=nlp(st)
    url_list=regex_extractor(r"\b(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/|www.)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?\b",doc,st)    
    license_plate_list=regex_extractor(r"[A-Z]{2}[ -][0-9]{1,2}(?: [A-Z])?(?: [A-Z]*)? [0-9]{4}",doc,st)  
    for a in url_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in license_plate_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
  #  print("4")
  ##  Hiding the extracted information to protect identity
    
    
    ## Function call to extract phone numbers and fax numbers from the text.
    doc=nlp(st)
   # phone_fax_list1=regex_extractor(r"(?:(?:(?:(\+)((?:[\s.,-]*[0-9]*)*)(?:\()?\s?((?:[\s.,-]*[0-9]*)+)(?:\))?)|(?:(?:\()?(\+)\s?((?:[\s.,-]*[0-9]*)+)(?:\))?))((?:[\s.,-]*[0-9]+)+))",doc,st)
  #  print('41')
    phone_fax_list2=regex_extractor(r"\D(\+91[\-\s]?)?[0]?(91)?[789]\d{9}\D",doc,st)
  #  print(phone_fax_list1)
  #  print(phone_fax_list2)
    for i in range(len(phone_fax_list2)):
      phone_fax_list2[i][1]=phone_fax_list2[i][1]+1
      phone_fax_list2[i][2]=phone_fax_list2[i][2]-1
      phone_fax_list2[i][0]=st[phone_fax_list2[i][1]:phone_fax_list2[i][2]]
    
    phone_fax_list=[]
  #  for a in phone_fax_list1:
  #      phone_fax_list.append(a)
    for a in phone_fax_list2:
        phone_fax_list.append(a) 
    
  #  for a in phone_fax_list1:
  #    st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in phone_fax_list2:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
  #  print("5")
    
    ## Function call to extract pan number,passport number,account number,credit card number and medical record number and finally 
    ## hiding them to protect the information.
    doc=nlp(st)
    pan_list=regex_extractor(r"\b[A-Z]{5}\d{4}[A-Z]{1}\b",doc,st)
    passport_list=regex_extractor(r"\b[A-Z]{1}\d{7}\b",doc,st)
    account_and_serial_list=regex_extractor(r"\b\d{9,18}\b",doc,st)
    credit_card_list=regex_extractor(r"\d{5}(\s|\-)\d{5}(\s|\-)\d{5}|\d{4}(\s|\-)\d{4}(\s|\-)\d{4}(\s|\-)\d{4}",doc,st)
    
    for a in account_and_serial_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in pan_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in passport_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in credit_card_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
  #  print("6")
    doc=nlp(st)
    voter_id_list=regex_extractor(r"\b[A-Z0-9]{10}\b",doc,st)
    # print(voter_id_list)
    license_number=regex_extractor(r"\b[A-Z]{2}\d{2}(|-)\d{4}(|-)\d{7}\b",doc,st)
    # print(license_number)
    for a in voter_id_list:
      if(a[0].count('X')<3):
        st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in license_number:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
    doc=nlp(st)
    medical_rep=regex_extractor('\d{7}',doc,st)
    ###  medical_report_no : Assuming the pattern to be 7 digit number as it is organisation dependent and can also be changed later
    ###  accordingly.
    
    for a in medical_rep:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]

  #  print("7")

    ###  After extracting many useful information the below line of code extracts address fron the text.
    ###  Address which are smaller than street name.
    
   ### For extracting addresses we use a list of common words used in addressing and match them with every elemnt in spacy 
   ### doc object and if any match is found it is inserted in addr list.

    doc=nlp(st)
    addr=[]
    for i in doc:
      if(len(i)>1 and '\n' not in str(i)):
           if(str(i).lower() in address_identifier):
             addr.append(i)
    ##  This addr list condains all the matched words from address identifier list.
    ## Now it's time to remove the identified addresses after getting their position in the text.
    
    # print(addr)
    addr_ind=[]
    k=0
    ll=len(st)
    for i in addr:
      while(1):
        ind=st.find(str(i),k,ll)
        if(ind==-1):
          break
        if(ind!=0 and ind!=ll):  
          if((st[ind-1].isalpha() or st[ind+len(str(i))].isalpha())):
            k=ind+len(str(i))
          else:
            break
      addr_ind.append(ind)
      k=ind+len(str(i))      
   ## Here addr index list contains the positions of the matched words front the address identifier list.
    
  #  print(addr_ind)
    
    addr_list=[]  
    if(addr_ind!=[]):
      temp=addr_ind[0]
      a=[]
      for val in addr_ind:
            if(val-temp<20):
              a.append(val)
              temp=val
            else:
              addr_list.append(a)
              a=[]
              a.append(val)
              temp=val
      addr_list.append(a)  
  #  print(addr_list)        
    
    
    
    #### IN ORDER TO REMOVE THE ADDRESSES THE COMPLETE WORD CONTAINING THE ADDRESS IDENTIFIER WORD(matched from the address identifier list)
    #### HAS TO BE REMOVED.
    ##   SO THE BELOW CODE GETS THE SPAN OF THE COMPLETE WORD IN WHICH THE ADDRESS IDENTIFIER WORD WAS USED.
    add_list=[]
    for a in addr_list:
        flag=[]
        jj=a[0]
        while(st[jj] not in [',','\n','.',':'] and jj!=-1):
            jj=jj-1
        strt=jj
        ind1=strt
        count=8
        while(count and jj !=-1 and st[jj]!='\n'):
          if(st[jj].isdigit()):
            strt=jj
          jj=jj-1
          count=count-1
        jj=a[-1]
        while(st[jj] not in [',','\n','.',':'] and jj!=-1):
          jj=jj+1
        end=jj
        ind2=end
        count=7
        while(count and jj !=ll and st[jj]!='\n'):         # ll len(st)
          if(st[jj].isdigit()):
            end=jj
          jj=jj+1
          count=count-1
      #  print(ind1,ind2,st[ind1:ind2])    
        if((st[ind1]!='.' or st[ind2]!='.') and (ind2-ind1)<70):
          if(st[strt]=='\n' or st[strt]==','):
                strt=strt+1
          if(st[end]=='\n' or st[strt]==','):
                end=end-1
          flag.append(st[strt:end+1])
          flag.append(strt)
          flag.append(end)
          add_list.append(flag)    
   ### After the above code executes it gives the complete span of the word which needs to be removed in order to hide the 
   ### address information
    
    for a in add_list:
      strip_add=a[0].strip(' .,"')
    #  print(strip_add,len(strip_add))
    #  print(not(len(a[0])>30 and ',' not in strip_add))
      if(not(len(a[0])>30 and ',' not in strip_add)):
        #  print("inside")  
          st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]

  #  print("8")
    
   ### After covering a lot of area we are now left with names,dates which could not be identified by refular expression
   ### and age.
      
        
        
    ## to extract the dates which could not be identified by regular expression we are using en_core_web_sm spacy language model
    ## some manipulations neede to be done in order to make the default model works according to our requirments.
    doc3=nlp(st)
    date_list2=[]
    for ents in doc3.ents:
                if(str(ents.text).count('X')<2):
                    date=[]
                    if(ents.label_=='DATE' and (sum([True if i in st[ents.start_char:ents.end_char].lower() else False for i in date_id])>0) and (ents.end_char-ents.start_char)>4  and sum(c.isalpha() for c in st[ents.start_char:ents.end_char])>=1):
                        date.append(ents.text)
                        date.append(ents.start_char)
                        date.append(ents.end_char)
                        date_list2.append(date)

    
    for a in date_list2:
        count=0
        for i in range(a[1],a[1]+4):
            if(st[i].isnumeric()):
                count=count+1
        if(count==4):
            st=st[:a[1]+4]+'X'*(a[2]-a[1]-4)+st[a[2]:]
        else:
            count=0
            for j in range(a[2],a[2]-5,-1):                                ## remvoing the year so that
                if(st[j].isnumeric()):                                     ## the year is left untouched.
                    count=count+1                                          ##
            if(count==4):
                st=st[:a[1]]+'X'*(a[2]-4-a[1])+st[a[2]-4:]
            elif(count==3):
                st=st[:a[1]]+'X'*(a[2]-2-a[1])+st[a[2]-2:]
            else:
                st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:] 
    
    date_list=[]
    if(choice==1):
        for a in date_list1:
            date_list.append(a)
    for a in date_list2:
        date_list.append(a)
    ### This date_list contains all the dates we extracted including the regular expression portion and spacy default model portion
    
  #  print("9")

    ### Finally lets go for age.
    ### To identify age we are again using spacy style regex matcher(phrasematcher) which takes as input patterns we want to match
    ### and outputs the start index and end index of the matched pattern.
    
    ### The following line of code extracts age from text and check weather the extracted age is >89 .If yes remove it else leave as it is.
    try:
      age_list=[]
      matcher = PhraseMatcher(nlp.vocab, attr="SHAPE")
      age_indicator=['YEAR', 'YEARS', 'Y/O', 'AGES', 'AGE', 'Y.O', 'Y.O.','AGED','AGE IS']
      matcher.add("age", None, nlp3("76 year old"),nlp('29 years of age'),nlp('98 yo'),nlp("79 Year old"),nlp('93 y.o'),nlp('121 y.o'),nlp3("aged 58"),nlp3('aged 123'),nlp3("54 y/o"),nlp3("age is 59"),nlp3("123 y/o"), nlp3("ages 35"),nlp3("age 45"),nlp3("ages 123"),nlp3("age 123"),nlp3("54 years old"),nlp3("124 years old"),nlp3("41 y.o."),nlp3("123 y.o."),nlp3('113 year old'))
      doc = nlp3(st)
      for match_id, start, end in matcher(doc):
          if(sum([True if i in str(doc[start:end]).upper() else False for i in age_indicator])>=1):
              a=[]
              for i in range(start,end):
                  if(str(doc[i:i+1]).isnumeric()):
                      if(int(str(doc[i:i+1]))>89):
                          result=st.find(str(doc[start:end]))
                          count=0
                          for j in range(result,result+len(str(doc[start:end]))):
                                  if(st[j:j+1].isnumeric() and count==0):
                                      strt=j
                                  if(st[j:j+1].isnumeric()):
                                      count=count+1
                          a.append(st[strt:strt+count])   
                          a.append(strt)
                          a.append(strt+count)
                          age_list.append(a)
                          st=st[:strt]+'X'*count+st[strt+count:]     
    except:
      None 
    
    ### Despite covering a lot of cases related to age detection, some cases are still missing such as year-old,years-old,yr-old
    ### so the below code covers all such type of cases.
    
  #  print("10")
    
    ## creating a doc object of the processed string by passing in to nlp spcay object
    doc=nlp(st)
    ## regular expression to catch the remaining age indicators.
    expression = r"\b\d{2,3}(-| )(year-old|years-old|yr-old|yrs-old|year old|years old|yr old|yrs old)\b"
    ## spacy matcher will match the regex pattern against the string.we will move inside the loop whenever there is a match.
    for match in re.finditer(expression, doc.text):
        ## match.span will give the start and end index of the doc which matches the given pattern
        start, end = match.span()
        span = doc.char_span(start, end)
        # This is a Span object or None if match doesn't map to valid token sequence
        if span is not None:
            ## In case of match find the index of the matched pattern in the original string.
            ind=st.find(str(span.text))
            ## store it in a start variable
            strt=ind
            ## increment ind while st[ind] is number/digit
            while(st[ind].isnumeric()):
                ind=ind+1
            ## store the end index of digit to end varible    
            end=ind   
            ## we have to remove the age only if it is > 89 so the below line of code checks if  the age is > 89 or not.
            ## If yes it will be removed.
            if((int(st[strt:end]))>89):
              st=st[:strt]+'X'*(end-strt)+st[end:]
    
    
  #  print("11")
    ### Finally lets pack all the extracted pattern in a dictionary with key as name of pattern and value as list of list contining
    ### matached pattern ,start_index,end_index.
    d={}
    d['date']=date_list
    d['mail']=mail_list
    d['aadhar']=aadhar_list
    d['ip']=ip_list
    d['url']=url_list
    d['license_plate']=license_plate_list
    d['phone_fax']=phone_fax_list
    d['account_serialno']=account_and_serial_list
    d['pan']=pan_list
    d['passport']=passport_list
    d['credit_card']=credit_card_list
    d['age']=age_list
    d['address']=add_list
    d['shifted_date']=shifted_datelist
    d['medical_report_no']=medical_rep
    d['voter_id']=voter_id_list
    d['license_no.']=license_number
    shift=random_val 
    
    ## Returning the processed string with all the information hidden,along with dictionary containing them and if choice was 2
    ## the shift(by which all the dates are shifted) has to be returned as well ortherwise return shift as None(i.e for choice 1)
    if(choice==1):
        return(st,d,None)
    else:
        return(st,d,shift)


# pip install -U spacy
# python -m spacy download en_core_web_sm
# pip install nltk 
# python -m nltk.downloader wordnet

## Importing all the required dependencies.
import pandas as pd
from pandas import datetime
from datetime import timedelta
import spacy
import re
from spacy.lang.en import English
from spacy.matcher import PhraseMatcher
import random
from random import randint
import pickle
from spacy.tokenizer import Tokenizer
import string
import nltk
from nltk.corpus import wordnet
import xml.etree.ElementTree as ET
# from spellchecker import SpellChecker
# nltk.download('wordnet')
# nltk.data.path.append('/home/nile/nltk_data/corpora/wordnet')

#spell = SpellChecker()

## we have 2 pickle file
## data : containg the terms assosiated with medical fields.
## data2 : containg the names of indian cities
## These are basically used as lookup table to reduce the error

dirs = 'deidentifier/'
with open(dirs+'whitelist5.pkl', 'rb') as f:
    data = pickle.load(f)
with open(dirs+'city_state_list2.pkl', 'rb') as f:
    data2 = pickle.load(f)
with open(dirs+'abbreviation_list5.pkl', 'rb') as f:
    abbr_list = pickle.load(f)
    
## loading spacy en_core_web_sm language model
nlp = spacy.load("en_core_web_sm")
## loading a re-trained spacy language model on medical data
nlp2=spacy.load(dirs+'trained_spacy_model2')
nlp3=English()

### function takes string and choice as input and reutns the processed text along with dictionary of extracted information and shift
def master(xml_content,choice=2):
    ## deidentifier function is called which returns processed string,dictionary and shift
    st,dic,shift=deidentifier(xml_content,nlp,nlp3,choice)  ## 2 for shifted dates.1 to remove them completely
    ## the string we get here has almost all the information hidden except one last remaining part. That is name of persons and organisation.
    ## To extract names from the processed text we are using re-trained spacy model.
    
    ## The below lines of code extract the names of person and org. from the processed text and hides them also.
    num_str='0123456789'
    tokenizer = Tokenizer(nlp3.vocab)
    doc2=nlp2(st)
    person_org_list=[]
    for ents in doc2.ents:
        strt=ents.start_char
        end=ents.end_char-1
        while(not(str(st[strt]).isalpha())):
            # and strt<ents.end_char
                strt=strt+1
                if(strt>=ents.end_char):
                    break
        while(not(str(st[end]).isalpha())):                              #and end>ents.end_char)
                end=end-1
                if(end<=ents.start_char):
                    break
      #  print(ents.text,st[strt:end+1],1)        
        if(str(ents.text).count('X')<3 and str(st[strt:end+1]).lower() not in data and str(st[strt:end+1]).lower() not in data2 and str(st[strt:end+1]).lower() not in abbr_list):
        #  print(ents.text,str(ents.text).lower() in data,str(ents.text).lower() in abbr_list)  
          tokens=tokenizer(str(ents.text))
         # for i in tokens:
          #  print(i)
          if((sum([True if i in str(tokens) else False for i in num_str])==0) and len(str(ents.text))>2 and sum([True if str(i).lower() in data or '\n' in str(i) or str(i).lower() in data2 or str(i).lower() in abbr_list else False for i in tokens])!=len(tokens)):
                     a=[]
                    # print(st[ents.start_char:ents.end_char],ents.start_char,ents.end_char)
                     strt=ents.start_char
                     end=ents.end_char-1
                    # print(strt,end)
                    # print(st[strt],st[end])
                     while(not(str(st[strt]).isalpha())):
                          #  print('1111111')
                           strt=strt+1
                     while(not(str(st[end]).isalpha())):
                          #  print('22222222')
                           end=end-1
                    # print(strt,end) 
                     if('\n' in st[strt:end+1] or '\t' in st[strt:end+1]):
                        split_list=re.split('\n|\t', st[strt:end+1])
                        strip_list=[i.strip() for i in split_list]
                        if(sum([True if str(i).lower() not in data and str(i).lower() not in data2 and str(i).lower() not in abbr_list and len(str(i))>1 else False for i in strip_list])>0):
                             if(not wordnet.synsets(st[strt:end+1])):
                                #  print(st[strt:end+1])
                                 a.append(st[strt:end+1])      
                                 a.append(strt)
                                 a.append(end+1)
                                 person_org_list.append(a)   

                     else:
                         a.append(st[strt:end+1])      
                         a.append(strt)
                         a.append(end+1)      
                     #while(!(st[end_char].isalpha())
                     #      end_char=end_char-1;      
                    # a.append(ents.end_char)   
                         person_org_list.append(a)
    dic['person_and_org']=person_org_list
    for a in person_org_list:
      if(len(a[0])<30):  
          st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
    result=string.punctuation
    for i in range(10):
        result=result+str(i)
  #  print(result)
    num_str='0123456789'
    
    
    doc=nlp(st)
    for token in doc:
        if((token.tag_=="NN" or token.tag_=='NNP') and 'XX' not in str(token)):
            #  print(token)
             # spell_list=[]
             # spell_list.append(str(token))  
            #  misspelled = spell.unknown(a)
            #  for word in misspelled:
               # spell_word=spell.correction(word)  
              if not wordnet.synsets(str(token)):
                # print(token)
                if(str(token).lower() not in data and str(token).lower() not in data2 and str(token).lower() not in abbr_list and sum([True if i in str(token) else False for i in result])==0 and len(str(token))>2):
                    # if(len(str(token))>5):     
                     #   spell_list=[]
                     #   spell_list.append(str(token))  
                     #   misspelled = spell.unknown(spell_list)
                     #   for word in misspelled:
                     #       spell_word=spell.correction(word)
                     #   if not wordnet.synsets(str(spell_word)):  
                          #  print(spell_word)
                    # else: 
                        print(token)
                        index=st.find(str(token))
                        # print(index)
                        if(index!=0 and index+len(str(token))!=len(st)):
                          #  print(index)
                            if(not((st[index-1].isalpha()) and (st[index+len(str(token))+1]).isalpha())):
                                  st=st[:index]+'X'*len(str(token))+st[index+len(str(token)):]
                        elif(index==0 or index+len(str(token))==len(st)):
                            st=st[:index]+'X'*len(str(token))+st[index+len(str(token)):]
    
    ## final processed string,dictionay and shift is returned.
    return(st,dic,shift)

## input the name of text file to be processed.
# FUNCTION - TYPE OF OUTPUT EXPECTED
# final_str,dic,shift=master(input(),2)  ## 2 for shifted dates.1 to remove them completely

## extracted information.
# for items,val  in dic.items():
    # print(items,val)

## final processed string
# print(final_str)