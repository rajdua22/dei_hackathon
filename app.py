## Run this
import speech_recognition as sr
from speech_to_text import get_text
from language import *


def main():
    stored_text = get_text()
    file = open("input.txt")
    line = file.read().replace("\n", " ")
    file.close()
    final = new_syntax_process(line)
    final_text = final[0]
    final_score = final[1]
    with open('output.txt',mode ='w') as file:
        if len(final_text) == 0:
            file.write("Your sentence \"" + line + "\" has no exclusive terminology")
        else:
            file.write("Your inclusivity score: " + "{:.2%}".format(final_score))
            file.write("\n")
            file.write("Identified exclusive terminology: ")
            for word in final_text:
                file.write("\n")
                file.write(word)



if __name__ == "__main__":
    main()
