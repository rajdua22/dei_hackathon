from google.cloud import language_v1
from google.cloud.language import enums
from google.cloud.language import types

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

def sensitivity_check(word_content):
    client = language_v1.LanguageServiceClient()
    language = "en"
    type_ = enums.Document.Type.PLAIN_TEXT

    encoding_type = enums.EncodingType.UTF8
    descriptor = {"content": word_content, "type": type_, "language": language}
    response_sentiment = client.analyze_sentiment(descriptor, encoding_type=encoding_type)
    if response_sentiment.document_sentiment.score < 0:
        return True
    else:
        return False

def new_syntax_process(text_content):
    #Check for file and sentiment
    insensitive = []
    total_words = 0
    score = 0

    with open('dictionary.txt') as f:
        lines = [line.rstrip() for line in f]

    client = language_v1.LanguageServiceClient()
    language = "en"
    type_ = enums.Document.Type.PLAIN_TEXT
    document = {"content": text_content, "type": type_, "language": language}

    encoding_type = enums.EncodingType.UTF8
    printable = ""
    response_syntax = client.analyze_syntax(document, encoding_type=encoding_type)

    for sentence in response_syntax.sentences: #SENTENCE
        document = {"content": sentence.text.content, "type": type_, "language": language}
        response_syntax = client.analyze_syntax(document, encoding_type=encoding_type)
        for word in response_syntax.tokens: #WORDS IN SENTENCE
            total_words += 1
            if word.text.content in lines:
                score += 2
                insensitive.append(word.text.content)
            word_dependency_edge = word.dependency_edge
            #Label Guide: acomp: 2, nsubj: 28, root: 54, conj: 12, amod: 5
            if word_dependency_edge.label == 2: #ADJECTIVE LABEL FOR PASSIVE VOICE
                index = -1
                adj_head_token_index = word_dependency_edge.head_token_index
                for possibleHead in response_syntax.tokens: #SEARCH FOR VERB
                    index += 1
                    if adj_head_token_index == index:
                        if possibleHead.text.content == "is":
                            possibleHead_dependency_edge = possibleHead.dependency_edge
                            if possibleHead_dependency_edge.label == 54: #If ROOT
                                for possibleSubject in response_syntax.tokens: #SEARCH FOR SUBJECT
                                    subj_dependency_edge = possibleSubject.dependency_edge
                                    if subj_dependency_edge.label == 28:
                                        part_of_speech = possibleSubject.part_of_speech
                                        if enums.PartOfSpeech.Tag(part_of_speech.tag).name == "PRON":
                                            if(sensitivity_check(word.text.content)):
                                                insensitive.append(word.text.content)
                                                score += 1
                                        elif enums.PartOfSpeech.Tag(part_of_speech.tag).name == "NOUN":
                                            subject = {"content": possibleSubject.text.content, "type": type_, "language": language}
                                            response_entity = client.analyze_entities(subject, encoding_type=encoding_type)
                                            for entity in response_entity.entities:
                                                if enums.Entity.Type(entity.type).name == "PERSON":
                                                    if(sensitivity_check(word.text.content)):
                                                        insensitive.append(word.text.content)
                                                        score += 1
                            elif possibleHead_dependency_edge.label == 48: #If rcmod, check if dependent on person
                                #if rcmod, see what it's dependent on and if it's a PERSON
                                index = -1
                                act_head_token_index = possibleHead_dependency_edge.head_token_index
                                for possibleActor in response_syntax.tokens:
                                    index += 1
                                    if act_head_token_index == index:
                                        actor = {"content": possibleActor.text.content, "type": type_, "language": language}
                                        response_entity = client.analyze_entities(actor, encoding_type=encoding_type)
                                        for entity in response_entity.entities:
                                            if enums.Entity.Type(entity.type).name == "PERSON":
                                                if(sensitivity_check(word.text.content)):
                                                    insensitive.append(word.text.content)
                                                    score += 1
            elif word_dependency_edge.label == 5:
                index = -1
                head_token_index = word_dependency_edge.head_token_index
                for token in response_syntax.tokens:
                    index += 1
                    if head_token_index == index:
                        target = {"content": token.text.content, "type": type_, "language": language}
                        response_entity = client.analyze_entities(target, encoding_type=encoding_type)
                        for entity in response_entity.entities:
                            if enums.Entity.Type(entity.type).name == "PERSON":
                                if(sensitivity_check(word.text.content)):
                                    insensitive.append(word.text.content)
                                    score += 1
            # elif word_dependency_edge.label == 12:
            #     while word_dependency_edge.label == 12:
            #         #set word dependency edge equalto that of the head
            #         pass
            #     #While a conjunction of adjectives, store, analyze, and try and do the other ones for adjectives using head_token_index

    if pronoun_detect(text_content):
        insensitive.append("Be intentional about pronouns")
    return (insensitive, (total_words-score)/total_words)
