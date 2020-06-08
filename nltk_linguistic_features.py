from re import sub, findall, MULTILINE
from nltk import FreqDist, pos_tag
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from operator import itemgetter


attr_description = {
    0: 'conjunction, coordinating', 1: 'numeral, cardinal',
    2: 'determiner', 3: 'foreign word', 4: 'preposition or conjunction, subordinating',
    5: 'adjective or numeral, ordinal', 6: 'adjective, comparative',
    7: 'adjective, superlative', 8: 'modal auxiliary',                    
    9: 'noun, common, singular or mass', 10: 'noun, proper, singular',
    11: 'noun, proper, plural', 12: 'noun, common, plural', 13:'pre-determiner',
    14: 'genitive marker', 15: 'pronoun, personal', 16: 'pronoun, possessive',
    17: 'adverb', 18: 'adverb, comparative', 19: 'adverb, superlative',
    20: 'particle', 21: '"to" as preposition/infinitive',
    22: 'interjection', 23: 'verb, base form', 24: 'verb, past tense',
    25: 'verb, present participle or gerund', 26: 'verb, past participle',
    27: 'verb, present tense, not 3rd person singular',
    28: 'verb, present tense, 3rd person singular', 29: 'WH-determiner', 30: 'WH-pronoun',
    31: 'WH-pronoun, possessive',32: 'Wh-adverb',33:'number of words', 34:'number of words per sentence',
    35: 'number of captalized words',36: 'percentage of stopwords', 37:'number of punctuation',
    38:'number of quotes', 39:'number of URls'    
}


def remove_ulr_corpus(text):
    str_template = r'(?i)https?://\S+'
    str_template = r'(?i)\b((?:https?:(?:\/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b\/?(?!@)))'
    new_text = sub(str_template, '', text, flags=MULTILINE)

    count_matches = len(findall(str_template,text))
    return new_text, count_matches

def remove_stopwords_corpus(text):
    content = []
    for w in text:
        if w.lower().strip() not in stopwords.words('english'):
            content.append(w.lower().strip())

    return content

def remove_mention_corpus(text):
    new_text = sub(r'@\w+ ?','',text)
    count_matches = len(findall(r'@\w+ ?',text))
    
    return new_text, count_matches

def tokenizer(text):
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    
    return tokens


def part_of_speech_tagger(tokens, return_type='list'):
    ''' 
    More details in nltk.help.upenn_tagset()
        CC, CD, DT, FW, IN, JJ, JJR, JJS, LS, MD, NN, NNP,
        NNPS, NNS, PDT, POS, PRP, PRP$, RB, RBR, RBS, RP, SYM,
        TO, UH, VB, VBD, VBG, VBN, VBP, VBZ, WDT, WP, WP$, WRB
    '''
    word_tagged_dict = {"CC":0, "CD":0, "DT":0, "FW":0, "IN":0, 
                        "JJ":0, "JJR":0,"JJS":0, "MD":0, "NN":0,
                        "NNP":0, "NNPS":0, "NNS":0,"PDT":0, "POS":0, 
                        "PRP":0, "PRP$":0, "RB":0, "RBR":0, "RBS":0,
                        "RP":0, "TO":0, "UH":0, "VB":0, "VBD":0, 
                        "VBG":0, "VBN":0,"VBP":0, "VBZ":0, "WDT":0,
                        "WP":0, "WP$":0, "WRB":0} 

    word_tagged_list, result = pos_tag(tokens), []
    for item in word_tagged_list:
        if(item[1] in word_tagged_dict.keys()):
            word_tagged_dict[item[1]] += 1

    word_tagged_sorted = sorted(word_tagged_dict.items(), key=itemgetter(0))
    word_tagged_list = []
    for i in word_tagged_sorted:
        word_tagged_list.append(i[1])
    if return_type=='list':
        return word_tagged_list
    elif return_type=='dic':
        word_tagged_dic = {}
        for i in word_tagged_sorted:
            word_tagged_dic[i[0]] = i[1]
        return word_tagged_dic
    else:
        raise Exception("unknown return type")

def count_captalized_words(tokens):
    nro_upper_words = 0
    for i in tokens:
        if(i.isupper()):
            nro_upper_words += 1
    return nro_upper_words

def count_per_stopwords(tokens):
    total_words, words_per_sent = len(tokens), 0.0
    stopwords_nltk = stopwords.words('english')
    count = 0
    for w in tokens:
        if w.lower().strip() in stopwords_nltk:
            count += 1
    if(total_words > 0):
        words_per_sent = round(count/total_words,2)
    return words_per_sent

def count_punctuation(text, regular_exp):
    #r'[' + punctuation+ r']+' and r'["\']+'
    count = 0
    tokenizer = RegexpTokenizer(regular_exp)
    tokens = tokenizer.tokenize(text)
    count = len(tokens)

    return count

def count_quotes(text):
    count = 0
    tokenizer = RegexpTokenizer(r'["\']+')
    tokens = tokenizer.tokenize(text)
    count = len(tokens)

    return count

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


def calculate_mean_confmatrix(confusion_list):
    result = [[0.0,0.0],[0.0,0.0]]
    for cm in confusion_list:
        for i in range(0,len(result)):
            for j in range(0,len(result)):
                result[i][j] += cm[i][j]
    for i in range(0,len(result)):
        for j in range(0,len(result)):
            result[i][j] = result[i][j]/len(confusion_list)
    return result

def show_confusion_matrix(cm):
    for i in cm:
        a = "{:.2f}".format(i[0])
        b = "{:.2f}".format(i[1])
        print("["+a+" "+b+"]")
