# -*- coding: utf-8 -*-
from nltk import FreqDist
from nltk.tokenize import sent_tokenize, RegexpTokenizer
from textstat.textstat import textstatistics, legacy_round
from textstat.textstat import textstat
from re import sub, match

easy_word_set = textstat._textstatistics__get_lang_easy_words()

def tokenizer(text):
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    
    return tokens

def sentence_level_attr(text, tokens):
    word_count, word_sent = 0, 0
    words_per_sent = 0.0

    #word count of the whole text
    vocabulary = FreqDist(tokens)
    word_count = len(vocabulary.keys())

    #word count by setence
    sent_tokenize_list = sent_tokenize(text)
    for i in sent_tokenize_list:
        tkn = tokenizer(i)
        vocabulary = FreqDist(tkn)
        word_sent += len(vocabulary.keys())

    if(len(sent_tokenize_list) > 0):
        words_per_sent = round(word_sent/len(sent_tokenize_list), 2)

    return word_count, words_per_sent


# Returns Number of Words in the text
def word_count(text):
    text = sub(r'[^\w\s]',' ',text).strip() #remove punct
    words = len(tokenizer(text))
    return words
 
def character_count(text):
    characters = 0 
    for token in tokenizer(text):
        token = sub(r'[^\w\s]','',token) #remove punct.
        for t in token.split():
            if(bool(match("^[A-Za-z0-9]*$", t)) and t != ''): 
                characters+= len(t)
    return characters

def letter_count(text):
    letters = 0 
    for token in tokenizer(text):
        token = sub(r'[^\D]',' ',token).strip() #remove digits
        token = sub(r'[^\w\s]',' ',token).strip() #remove punct
        for t in token.split():
            if(bool(match("^[A-Za-z0-9]*$", t)) and t != ''):
                letters+= len(t)
    return letters

# Returns average sentence length
def avg_sentence_length(text):
    words = word_count(text)
    sentences = len(sent_tokenize(text))
    if(sentences > 0):
        average_sentence_length = float(words / sentences)
    else:
        average_sentence_length = 0.0
    return average_sentence_length

def syllables_count(word):
    return textstatistics().syllable_count(word)
 
# Returns the average number of syllables per
# word in the text
def avg_syllables_per_word(text):
    syllable = syllables_count(text)
    words = word_count(text)
    if(float(words) > 0):
        ASPW = float(syllable) / float(words)
    else:
        ASPW = 0.0
    return legacy_round(ASPW, 1)
 
# Return total Difficult Words in a text
def difficult_words(text):
 
    # Find all words in the text
    words = []
    sentences = sent_tokenize(text)
    for sentence in sentences:
        words += [token for token in sentence]
 
    # difficult words are those with syllables >= 2
    # easy_word_set is provide by Textstat as 
    # a list of common words
    diff_words_set = set()
     
    for word in words:
        syllable_count = syllables_count(word)
        if word not in easy_word_set and syllable_count >= 2:
            diff_words_set.add(word)
 
    return len(diff_words_set)

# A word is polysyllablic if it has more than 3 syllables
# this functions returns the number of all such words 
# present in the text
def poly_syllable_count(text):
    count = 0
    words = []
    sentences = sent_tokenize(text)
    for sentence in sentences:
        words += [token for token in sentence]
     
 
    for word in words:
        syllable_count = syllables_count(word)
        if syllable_count >= 3:
            count += 1
    return count

def dale_chall_index(text):
    """
        Implements Dale Challe Formula:
        Raw score = 0.1579*(PDW) + 0.0496*(ASL) + 3.6365
        Here,
            PDW = Percentage of difficult words.
            ASL = Average sentence length
    """
    words = word_count(text)
    # Number of words not termed as difficult words
    count = words - difficult_words(text)
    if words > 0:
        # Percentage of words not on difficult word list
        per = float(count) / float(words) * 100
    else:
        per = 0.0

        
    # diff_words stores percentage of difficult words
    diff_words = 100 - per
    raw_score = (0.1579 * diff_words) + \
                (0.0496 * avg_sentence_length(text))
     
    # If Percentage of Difficult Words is greater than 5 %, then;
    # Adjusted Score = Raw Score + 3.6365,
    # otherwise Adjusted Score = Raw Score
 
    if diff_words > 5:       
        raw_score += 3.6365
         
    return legacy_round(raw_score, 2)

def gunning_fog_index(text):
    if(word_count(text) > 0):
        per_diff_words = (difficult_words(text) / word_count(text) * 100) + 5
    else:
        per_diff_words = 5
    score = 0.4 * (avg_sentence_length(text) + per_diff_words)
    return score
 
def smog_index(text):
    """
        Implements SMOG Formula / Grading
        SMOG grading = 3 + ?polysyllable count.
        Here, 
           polysyllable count = number of words of more
          than two syllables in a sample of 30 sentences.
    """
    sentence_count = len(sent_tokenize(text))
    if sentence_count >= 3:
        poly_syllab = poly_syllable_count(text)
        SMOG = (1.043 * (30*(poly_syllab / sentence_count))**0.5) \
                + 3.1291
        return legacy_round(SMOG, 1)
    else:
        return 0.0
    
def flesch_index(text):
    """
        Implements Flesch Formula:
        Reading Ease score = 206.835 - (1.015 × ASL) - (84.6 × ASW)
        Here,
          ASL = average sentence length (number of words 
                divided by number of sentences)
          ASW = average word length in syllables (number of syllables 
                divided by number of words)
    """
    score = 206.835 - float(1.015 * avg_sentence_length(text)) -\
          float(84.6 * avg_syllables_per_word(text))
    
    return legacy_round(score, 2) 


def automated_readby_index(text):
    """
        Automated Readability Index:
          ARI = 4.71×(characters/words) + 0.5×(words/sentences) - 21.43
        Here,
          characters =  number of letters and numbers  
    """
    part1,part2 = 0.0 , 0.0
    if(word_count(text)>0):
        part1 = (character_count(text)/word_count(text))
    else:
        part1 = 0.0
    
    if(len(sent_tokenize(text))>0):        
        part2 = (word_count(text)/len(sent_tokenize(text)))
    else:
        part2 = 0.0

    score = 4.71 * part1 + 0.5 * part2 - 21.43

    return score

def coleman_liau_index(text):
    """
        The Coleman–Liau Index:
          CLI = 0.0588×L -0.296×S - 15.8
        Here,
          L = Letters ÷ Words × 100 (average number of letters per 100 words)
          S = Sentences ÷ Words × 100 (average number of sentences per 100 words)
    """
    if(word_count(text) > 0):
        L = character_count(text) / word_count(text) * 100
        S = len(sent_tokenize(text))/ word_count(text) * 100
    else:
        L, S = 0.0, 0.0       
    score = 0.0588 * L - 0.296 * S - 15.8
    return score


def read_dataset(filename, label, text_field):
    list_docs = []

    with open(filename, "r") as arq_in:
        reader_in = reader(arq_in, delimiter=',', quoting=QUOTE_ALL)
        for t in reader_in:
            if(len(t[text_field]) > 1):  # tratando alguns missing data
                list_docs.append([t[text_field], int(t[9]), int(t[10]), int(t[11]),int(t[17])])

    return list_docs  


def characters_stat(text):
    try:
        return character_count(text)
    except ValueError:
        return 0
    
def complexWords_stat(text):
    try:
        return textstat.dale_chall_readability_score(text)
    except ValueError:
        return 0
    
def longWords_stat(text):
    try:
        return avg_sentence_length(text)
    except ValueError:
        return 0
    
def numberSyllables_stat(text):
    try:
        return textstat.syllable_count(text, lang='en_US')
    except ValueError:
        return 0
    
def lexicon_count_stat(text):
    try:
        return textstat.lexicon_count(text, removepunct=True)
    except ValueError:
        return 0

def sentence_count_stat(text):
    try:
        return textstat.sentence_count(text)
    except ValueError:
        return 0
    

def flesch_reading_ease_stat(text):
    try:
        return textstat.flesch_reading_ease(text)
    except ValueError:
        pass
        return 0
    
def smog_index_stat(text):
    try:
        return textstat.smog_index(text)
    except ValueError:
        return 0
    
def flesch_kincaid_grade_stat(text):
    try:
        return textstat.flesch_kincaid_grade(text)
    except ValueError:
        return 0
    
def coleman_liau_index_stat(text):
    try:
        return textstat.coleman_liau_index(text)
    except ValueError:
        return 0
    
def automated_readability_index_stat(text):
    try:
        return textstat.automated_readability_index(text)
    except ValueError:
        return 0
    
def difficult_words_stat(text):
    try:
        return textstat.difficult_words(text)
    except ValueError:
        return 0
    
def linsear_write_formula_stat(text):
    try:
        return textstat.linsear_write_formula(text)
    except ValueError:
        return 0
    
def gunning_fog_stat(text):
    try:
        return textstat.gunning_fog(text)
    except ValueError:
        return 0
    
