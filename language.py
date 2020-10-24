from google.cloud import language_v1
from google.cloud.language import enums
from google.cloud.language import types
from adj_to_noun import *

def pronoun_detect(text_content):
    client = language_v1.LanguageServiceClient()
    language = "en"
    type_ = enums.Document.Type.PLAIN_TEXT
    document = {"content": text_content, "type": type_, "language": language}

    encoding_type = enums.EncodingType.UTF8
    response_syntax = client.analyze_syntax(document, encoding_type=encoding_type)

    for token in response_syntax.tokens:
        part_of_speech = token.part_of_speech
        if enums.PartOfSpeech.Tag(part_of_speech.tag).name == "PRON":
            return True

    return False

def syntax_process(text_content):
    client = language_v1.LanguageServiceClient()
    language = "en"
    type_ = enums.Document.Type.PLAIN_TEXT
    document = {"content": text_content, "type": type_, "language": language}

    encoding_type = enums.EncodingType.UTF8

    printable = ""

    response_syntax = client.analyze_syntax(document, encoding_type=encoding_type)

    for sentence in response_syntax.sentences:
        index = -1
        document = {"content": sentence.text.content, "type": type_, "language": language}
        response_syntax = client.analyze_syntax(document, encoding_type=encoding_type)
        for token in response_syntax.tokens:
            index += 1
            part_of_speech = token.part_of_speech
            if enums.PartOfSpeech.Tag(part_of_speech.tag).name == "NOUN":
                word = {"content": token.text.content, "type": type_, "language": language}
                response_entity = client.analyze_entities(word, encoding_type=encoding_type)
                for entity in response_entity.entities:
                    if enums.Entity.Type(entity.type).name == "PERSON":
                        for token in response_syntax.tokens:
                            part_of_speech2 = token.part_of_speech
                            if enums.PartOfSpeech.Tag(part_of_speech2.tag).name == "ADJ":
                                dependency_edge = token.dependency_edge
                                head_token_index = dependency_edge.head_token_index
                                if head_token_index == index:
                                    descriptor = {"content": token.text.content, "type": type_, "language": language}
                                    response_sentiment = client.analyze_sentiment(descriptor, encoding_type=encoding_type)
                                    if response_sentiment.document_sentiment.score < 0:
                                        original = token.text.content + " " + entity.name
                                        converted = convert_adj_to_noun(token.text.content)
                                        printable += "Consider replacing \"" + original + "\" with "
                                        for index,convert in enumerate(converted):
                                            if index == 0:
                                                printable += "\"" + entity.name + " experiencing " + convert + "\"" + "\n"
                                            else:
                                                printable += " or \"" + entity.name + " experiencing " + convert + "\"\n"

    if pronoun_detect(text_content):
        printable = "Your message has pronouns! Make sure to be intentional and specific.\n" + printable

    return printable
