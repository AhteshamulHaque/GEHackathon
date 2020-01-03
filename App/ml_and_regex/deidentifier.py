# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'App/ml_and_regex'))
	print(os.getcwd())
except:
	pass
# %%
## function to extract regular expression patterns(strg) 
## form the given string(st)

## We are here using spacy style regex matcher 

def regex_extractor(strg,doc,st):
  a=[]
  expression=strg
  for match in re.finditer(expression, doc.text):
    start, end = match.span()
    span = doc.char_span(start, end)
    b=[]
    b.append(st[start:end])
    b.append(start)
    b.append(end)
    a.append(b)
  return(a)     # returning a list of list containing txt,start_ind,end_index
                # of the matched pattern
    


# %%
## string:- Original String
## nlp:- spacy model trained on english web data
## nlp2:- Retrained spacy en_core_web_sm model on medical data (check final_training_data file)
## choice:- 1 for completing removing dates fron text except year.
##          2 for shifting the dates to protect the information without loss of valuable information(more preffered)

def deidentifier(file_content,nlp,nlp3,choice):
    doc=nlp(file_content)       ## spacy object containg processed string i.e string after passing through default en_core_web_sm spacy model.
    st=file_content              ## st=original string
    
    
    time=['YEAR', 'YEARS', 'AGE', 'AGES', 'MONTH', 'MONTHS', 'DECADE', 'CENTURY', 'WEEK', 'DAILY', 'DAY', 'DAYS', 'NIGHT', 'NIGHTS', 'WEEKLY', 'MONTHLY', 'YEARLY']
    address_identifier=['st','niwas','aawas','palace','road','block','gali','sector','flr','floor','path','near','oppo','bazar','house','nagar','bypass','bhawan','street','rd','sq','flat','lane','gali','circle','bldg','ave','mandal','avenue','tower','nagar','marg','chowraha','lane','heights','plaza','park','garden','gate','villa','market','apartment','chowk']
    
    ## regex extractor gets a regex string,doc,original string and returns a list of list containing matched pattern along with
    ## start and end index of the pattern.
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
                #print("count",count)        
                if(count==4):
                    #print(st[a[1]:a[2]])
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
    random_val=randint(0,60)   ## getting a random number to shift all the dates by that number
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
               # print(new_date)
               # print(type(new_date))
                new_date=new_date+timedelta(days=random_val)
               # print(str(new_date)[:-9])
                st=st[:front]+str(new_date)[:-9]+st[back:]
                k=k+(len(str(new_date)[:-9])-len(text))
                llst.append(str(new_date)[:-9])
                llst.append(front)
                llst.append(front+len(str(new_date)[:-9]))
                shifted_datelist.append(llst)
               # k=k+(10-len(text))
    
    ## function call to extract mail,ip address, and aadhar number form the text. 
    
    mail_list=regex_extractor(r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*)@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])",doc,st)    
    ip_list=regex_extractor(r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",doc,st)    
    aadhar_list=regex_extractor(r"(\d{4}(\s|\-)\d{4}(\s|\-)\d{4})",doc,st)
    
    ## replacing all the matched pattern to protect the information.
    
    for a in ip_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in mail_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:] 
    for a in aadhar_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
   

    
    ## Function call to extract urls and license plate numbers form the text
    doc=nlp(st)
    url_list=regex_extractor(r"(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?",doc,st)    
    license_plate_list=regex_extractor(r"[A-Z]{2}[ -][0-9]{1,2}(?: [A-Z])?(?: [A-Z]*)? [0-9]{4}",doc,st)  
    for a in url_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in license_plate_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
  ##  Hiding the extracted information to protect identity
    
    
    ## Function call to extract phone numbers and fax numbers from the text.
    doc=nlp(st)
    phone_fax_list1=regex_extractor(r"(?:(?:(?:(\+)((?:[\s.,-]*[0-9]*)*)(?:\()?\s?((?:[\s.,-]*[0-9]*)+)(?:\))?)|(?:(?:\()?(\+)\s?((?:[\s.,-]*[0-9]*)+)(?:\))?))((?:[\s.,-]*[0-9]+)+))",doc,st)
    phone_fax_list2=regex_extractor(r"\D(\+91[\-\s]?)?[0]?(91)?[789]\d{9}\D",doc,st)
    for i in range(len(phone_fax_list2)):
      phone_fax_list2[i][1]=phone_fax_list2[i][1]+1
      phone_fax_list2[i][2]=phone_fax_list2[i][2]-1
      phone_fax_list2[i][0]=st[phone_fax_list2[i][1]:phone_fax_list2[i][2]]
    
    phone_fax_list=[]
    for a in phone_fax_list1:
        phone_fax_list.append(a)
    for a in phone_fax_list2:
        phone_fax_list.append(a) 
    
    for a in phone_fax_list1:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in phone_fax_list2:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
    
    ## Function call to extract pan number,passport number,account number,credit card number and medical record number and finally 
    ## hiding them to protect the information.
    doc=nlp(st)
    pan_list=regex_extractor(r"[A-Z]{5}\d{4}[A-Z]{1}",doc,st)
    passport_list=regex_extractor(r"[A-Z]{1}\d{7}",doc,st)
    account_and_serial_list=regex_extractor(r"\d{9,18}",doc,st)
    credit_card_list=regex_extractor(r"\d{5}(\s|\-)\d{5}(\s|\-)\d{5}|\d{4}(\s|\-)\d{4}(\s|\-)\d{4}(\s|\-)\d{4}",doc,st)
    
    for a in account_and_serial_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in pan_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in passport_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    for a in credit_card_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
    doc=nlp(st)
    medical_rep=regex_extractor('\d{7}',doc,st)
    ###  medical_report_no : Assuming the pattern to be 7 digit number as it is organisation dependent and can also be changed later
    ###  accordingly.
    
    for a in medical_rep:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]

   

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
        while(st[jj] not in [',','\n','.',';'] and jj!=-1):
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
        while(st[jj] not in [',','\n','.',';'] and jj!=-1):
          jj=jj+1
        end=jj
        ind2=end
        count=7
        while(count and jj !=ll and st[jj]!='\n'):         # ll len(st)
          if(st[jj].isdigit()):
            end=jj
          jj=jj+1
          count=count-1
        if((st[ind1]!='.' or st[ind2]!='.') and (ind2-ind1)<50):
          if(st[strt]=='\n'):
                strt=strt+1
          if(st[end]=='\n'):
                end=end-1
          flag.append(st[strt:end+1])
          flag.append(strt)
          flag.append(end)
          add_list.append(flag)    
   ### After the above code executes it gives the complete span of the word which needs to be removed in order to hide the 
   ### address information
    
    for a in add_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]


   ### After covering a lot of area we are now left with names,dates which could not be identified by refular expression
   ### and age.
      
        
        
    ## to extract the dates which could not be identified by regular expression we are using en_core_web_sm spacy language model
    ## some manipulations neede to be done in order to make the default model works according to our requirments.
    doc3=nlp(st)
    date_list2=[]
    for ents in doc3.ents:
                if(str(ents.text).count('X')<2):
                    date=[]
                    if(ents.label_=='DATE' and (sum([True if i not in st[ents.start_char:ents.end_char].upper() else False for i in time])==len(time)) and (ents.end_char-ents.start_char)>4 and sum(c.isdigit() for c in st[ents.start_char:ents.end_char])>=1 and sum(c.isalpha() for c in st[ents.start_char:ents.end_char])>=1):
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
    
   

    ### Finally lets go for age.
    ### To identify age we are again using spacy style regex matcher(phrasematcher) which takes as input patterns we want to match
    ### and outputs the start index and end index of the matched pattern.
    
    ### The following line of code extracts age from text and check weather the extracted age is >89 .If yes remove it else leave as it is.
    try:
      age_list=[]
      matcher = PhraseMatcher(nlp.vocab, attr="SHAPE")
      age_indicator=['YEAR', 'YEARS', 'Y/O', 'AGES', 'AGE', 'Y.O', 'Y.O.','AGED','AGE IS']
      matcher.add("age", None, nlp3("76 year old"),nlp3("aged 58"),nlp3('aged 123'),nlp3("54 y/o"),nlp3("age is 59"),nlp3("123 y/o"), nlp3("ages 35"),nlp3("age 45"),nlp3("ages 123"),nlp3("age 123"),nlp3("54 years old"),nlp3("124 years old"),nlp3("41 y.o."),nlp3("123 y.o."),nlp3('113 year old'))
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
    shift=random_val 
    
    ## Returning the processed string with all the information hidden,along with dictionary containing them and if choice was 2
    ## the shift(by which all the dates are shifted) has to be returned as well ortherwise return shift as None(i.e for choice 1)
    if(choice==1):
        return(st,d,None)
    else:
        return(st,d,shift)


# %%
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

## we have 2 pickle file
## data : containg the terms assosiated with medical fields.
## data2 : containg the names of indian cities
## These are basically used as lookup table to reduce the error
with open('ml_and_regex/whitelist.pkl', 'rb') as f:
    data = pickle.load(f)
with open('ml_and_regex/city_state_list.pkl', 'rb') as f:
    data2 = pickle.load(f)

## loading spacy en_core_web_sm language model
nlp = spacy.load("en_core_web_sm")
## loading a re-trained spacy language model on medical data
nlp2=spacy.load('ml_and_regex/trained_spacy_model2')
nlp3=English()

### function takes string and choice as input and reutns the processed text along with dictionary of extracted information and shift
def master(string,choice):
    ## deidentifier function is called which returns processed string,dictionary and shift
    st,dic,shift=deidentifier(string,nlp,nlp3,choice)  ## 2 for shifted dates.1 to remove them completely
    ## the string we get here has almost all the information hidden except one last remaining part. That is name of persons and organisation.
    ## To extract names from the processed text we are using re-trained spacy model.
    
    ## The below lines of code extract the names of person and org. from the processed text and hides them also.
    tokenizer = Tokenizer(nlp3.vocab)
    doc2=nlp2(st)
    person_org_list=[]
    for ents in doc2.ents:
        if(str(ents.text).count('X')<3):
          tokens=tokenizer(str(ents.text))
          if(sum([True if str(i).lower() in data or '\n' in str(i) or str(i).lower() in data2 else False for i in tokens])!=len(tokens)):
                     a=[]
                     a.append(ents.text)
                     a.append(ents.start_char)
                     a.append(ents.end_char)   
                     person_org_list.append(a)
    dic['person_and_org']=person_org_list
    for a in person_org_list:
      st=st[:a[1]]+'X'*(a[2]-a[1])+st[a[2]:]
    
    ## final processed string,dictionay and shift is returned.
    return(st,dic,shift)


# %%
## input the name of text file to be processed.
# final_str,dic,shift=master(input(),2)  ## 2 for shifted dates.1 to remove them completely


# %%
## extracted information.
# for items,val  in dic.items():
#     print(items,val)


# %%
## final processed string
# print(final_str)


# %%
# f = open("testing5_deidentified.txt", "w")
# f.write(final_str)
# f.close() 


# %%


