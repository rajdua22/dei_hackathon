## Run this
import speech_recognition as sr
from speech_to_text import get_text
from language import *


def main():
    stored_text = get_text()
    final = syntax_process(stored_text)
    print(final)

    
if __name__ == "__main__":
    main()