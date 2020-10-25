# Util file to convert speech input into text output

import speech_recognition as sr



def get_text():# create the recognizer
    r = sr.Recognizer()

    # define the microphone
    mic = sr.Microphone(device_index=0)

    # record your speech
    with mic as source:
        audio = r.listen(source)

    # speech recognition
    result = r.recognize_google(audio)

    # export the result
    with open('speech_to_text.txt',mode ='w') as file:
       file.write("Recognized text:")
       file.write("\n")
       file.write(result)

    return result
