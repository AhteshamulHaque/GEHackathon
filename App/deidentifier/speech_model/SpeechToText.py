from deepspeech import Model
import numpy as np
import wave
import json

def words_from_metadata(metadata):
    word = ""
    word_list = {}
    word_start_time = 0
    # Loop through each character
    for i in range(0, metadata.num_items):
        item = metadata.items[i]
        # Append character to word if it's not a space
        if item.character != " ":
            if len(word) == 0:
                # Log the start time of the new word
                word_start_time = item.start_time

            word = word + item.character
        # Word boundary is either a space or the last character in the array
        if item.character == " " or i == metadata.num_items - 1:
            word_duration = item.start_time - word_start_time

            if word_duration < 0:
                word_duration = 0

            
            each_word = {}
            each_word['start_time'] = round(word_start_time, 4)
            each_word['duration'] = round(word_duration, 4)
            
#             each_word["start_time"] = {round(word_start_time, 4)}
#             each_word["duration"] = round(word_duration, 4)
            if word not in word_list.keys():
                word_list[word]=[]
            word_list[word].append(each_word)
            # Reset
            word = ""
            word_start_time = 0

    return word_list


# TODO - need to be changed
dirPath = "deidentifier/speech_model/"
pathToAudioFile = dirPath+"audio/test_2.wav"
newpath = dirPath+"audio/test_2_deid.wav"

model_name = dirPath + "deepspeech-0.6.1-models/output_graph.pbmm"
langauage_model = dirPath + "deepspeech-0.6.1-models/lm.binary"
trie = dirPath + "deepspeech-0.6.1-models/trie"
# audio_file = dirPath + pathToAudioFile
# audio_deid = dirPath + newpath

def speech_to_text(audio_file):
    
    sample_rate = 16000
    BEAM_WIDTH = 500
    LM_ALPHA = 0.75
    LM_BETA = 1.85
    
    ds = Model(model_name, BEAM_WIDTH)
    ds.enableDecoderWithLM(langauage_model, trie, LM_ALPHA, LM_BETA)

    # Read original audio file
    file_obj = open(audio_file,'rb')
    
    fin = wave.open(file_obj)
    fs = fin.getframerate()
    # print("Framerate: ", fs)

    audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

    audio_length = fin.getnframes() * (1/sample_rate)
    timestamp = words_from_metadata(ds.sttWithMetadata(audio))
    fin.close()
    file_obj.close()

    # print("Infering {} file".format(audio_file))
    transcript = ds.stt(audio)
    
    return transcript, timestamp
# print(transcript)


def get_deidentified_file(input_audio_file_path, timestamp, phi_word_list, fs=16000):
    
    #Read file as a numpy array    
    from scipy.io.wavfile import read
    a = read(input_audio_file_path)
    arr = np.array(a[1],dtype=np.int16)
    
    # Each word in given list
    for word in phi_word_list:
        
        word = str(word)
        # Each instance of the word
        for i in range(len(timestamp[word])):
            #Get start position in array
            start = int(timestamp[word][i]['start_time']*fs)
            #Get end position in array
            end = int((timestamp[word][i]['duration']*fs) + start)
            #Mute the required part
            arr[start: end] = 0
    return arr


# array = get_deidentified_file(audio_file, timestamp=timestamp, phi_word_list=['a'])

# Write in new audio file
# from scipy.io.wavfile import write
# write(audio_deid, rate=16000, data=array)


# truecasing_by_pos(transcript)

# nltk.download('averaged_perceptron_tagger')