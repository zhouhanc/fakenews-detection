from operator import itemgetter
from bs4 import BeautifulSoup
from re import search, sub
from collections import defaultdict
from urllib.parse import urlparse
from os import chdir, listdir, environ, makedirs, rename, chmod, walk, remove, path

from nltk import word_tokenize
import readability
import nltk_linguistic_features

# import sys
# sys.path += ['../']


''' Get info of comment's feed through RSS'''

def get_news_feed(dict_rss):
    url_rss = None
    feed_list = sorted(dict_rss.items(), key=itemgetter(1), reverse = True)
    
    if(len(feed_list) > 0):
        url_rss = feed_list[0][0]
    return url_rss


def clean_author_name(name):
    ''' Clean the html tag content to get the author name '''
   
    months = r'\b[jJ]anuary\b|\b[fF]ebruary\b|\b[mM]arch\b|\b[aA]pril\b|\b[mM]ay\b|\b[jJ]une\b|\b[jJ]uly\b|\b[aA]ugust\b|\b[sS]eptember\b|\b[oO]ctober\b|\b[nN]ovember\b|\b[dD]ecember\b'
    usual_words = r'[pP]osted|[wW]ritten|[pP]ublished'
    temp_words = r'\bam\b|\bpm\b|\b[oO]n\b|\b[iI]n\b|\b[aA]t\b'
    punctuations = r'[,.-]'
    
    author_name = sub(r'\d+',' ', name)
    author_name = sub(punctuations,' ', author_name)  
    author_name = sub(months,' ', author_name)
    author_name = sub(usual_words,' ', author_name)
    author_name = sub(temp_words,' ', author_name)

    return author_name.strip()

def verify_usual_tags(tag_name, soup):
    ''' Verify common html tags which used to have author's name '''
    
    attributes_list = ['name', 'rel', 'itemprop', 'class', 'id']
    values_list = ['author', 'byline', 'dc.creator']
    author_name = None
    for t in soup.find_all(tag_name):
        for attr in attributes_list:
            for vals in values_list:
                if ((t.get(attr) != None) and
                    (t.get(attr)[0].find('comment') < 0) and
                    (t.get(attr)[0].find(vals) >= 0)):
                    author_name = str(t)
                    author_name = sub('<[^<]+?>', ' ', author_name)
                    author_name = sub('[<>|:/]|[bB][yY]|[fF]rom','',author_name)
    return author_name


def verify_usual_words(html_content):
    ''' Verify common words which used to have author's name (ex: By/From) '''  
    
    author_name = None    
    pattern = '[bB][yY][\:\s]|[fF]rom[\:\s]'
    match = search(pattern, html_content)
    if(match):
        pos_ini, pos_fim = match.span()[0], match.span()[1]
        line = html_content[pos_ini:pos_fim+100].replace('\n','')
        search_str = sub('<[^<]+?>', ' ', "<"+line+">")
        search_str = sub('[<>|:/]|[bB][yY]|[fF]rom','',search_str)
        author_name = search_str
    return author_name


def get_authors(html_content):
    BS4_parser = 'lxml'  # html.parser
    ''' Get new's author name '''
    is_author, author = '',0
    soup = BeautifulSoup(html_content, BS4_parser)      
     
    #Method 1: Popular authors tags
    popular_authos_tags = ['span','a','p']
    for tag in popular_authos_tags:
        result = verify_usual_tags(tag, soup)
        if(result):
            author = clean_author_name(result)
            #return author
        
    #Method 2: Search for by/from in tags content        
    result = verify_usual_words(html_content)
    if(result):
        author = clean_author_name(result)
        #return author

    if(author != ''):
        is_author = 1
    else:
        is_author = 0  
    return is_author


def get_url_domain(url):
    pos_ini = url.find('://')+3
    pos_end = pos_ini+url[pos_ini:].find('/')
    url_domain = url[pos_ini:pos_end]
    
    return url_domain

def set_news_attr(attr):
    value = ''
    if (attr is not None):
        value = attr
    return value

def count_tag_occurr(soup, list_tags):
    ratio, aux, occurr = 0.0, 0.0, []
    for tag in list_tags:     
        if(soup.find_all(tag) is not None):
            occurr.append(len(soup.find_all(tag)))
            aux += len(soup.find_all(tag))
        else:
            occurr.append(0)
    #ratio = aux/total_tags
    ratio = aux
    return ratio

def count_ads(soup):
    #TO DO add others ads companies
    count = 0
    for t in soup.find_all('script'):
        if ((t.get('src') is not None) and
        (t.get('src')[0].find('google') >= 0)):
            count = count + 1
    return count


from bs4.element import Comment
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def extracted_html_feature(html_content):
    BS4_parser = 'lxml'
    soup = BeautifulSoup(html_content, BS4_parser)
    
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    text = [t.lstrip().rstrip().replace('\t', ' ').replace('\n', ' ') for t in visible_texts]
#     text = [t.lower() for t in text if t != '']
    text = ' '.join(text)
    
    filter_area = soup.find('body')
    if filter_area is None:
        return []
    
    html_body_content = str(filter_area)

    soup = BeautifulSoup(html_body_content, BS4_parser)
    occ = defaultdict(int)
    
    for tag in soup.findAll():
        occ[tag.name] += 1  # add/update dict
    
    total_number_tag = sum(occ.values())
    
    all_tags = ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr', 
                              'abbr', 'address', 'b', 'big', 'blockquote', 'center', 'cite', 
                              'code', 'del', 'em', 'font', 'i', 'ins', 'mark', 'pre', 'progress', 
                              's', 'small', 'strong', 'sub', 'sup', 'time', 'u', 'var', 'wbr', 
                              'form', 'input', 'textarea', 'button', 'select', 'option', 'label', 
                              'fieldset', 'legend', 'iframe', 'img', 'figcaption', 'figure', 'picture', 
                              'svg', 'audio', 'source', 'video', 'a', 'link', 'nav', 'ul', 'ol', 'li', 
                              'dir', 'dl', 'dt', 'dd', 'menu', 'table', 'caption', 'th', 'tr', 'td', 
                              'thead', 'tbody', 'tfoot', 'style', 'div', 'span', 'header', 'footer', 
                              'main', 'section', 'article', 'meta', 'base', 'script', 'noscript', 'embed', 
                              'object', 'param']
    html_feature = {}
    for tag in all_tags:
        html_feature[tag] = occ[tag]
    return text, html_feature


def get_NLTK_features(text):
    if(text.strip()==""):
        # discard this document since there is no content to learn from
        return None

    text, count_urls = nltk_linguistic_features.remove_ulr_corpus(text)
    tokens = nltk_linguistic_features.tokenizer(text)

    pos_tag_numbers = nltk_linguistic_features.part_of_speech_tagger(word_tokenize(text), return_type='dic')
    word_count, words_per_sent = nltk_linguistic_features.sentence_level_attr(text,tokens)
    nr_captalized_words = nltk_linguistic_features.count_captalized_words(tokens)
    nr_per_stopwords = nltk_linguistic_features.count_per_stopwords(tokens)
    # TODO: we have two unused features here
    # nr_punctuation = nltk_linguistic_features.count_punctuation(text,r'['+punctuation+r']+')
    # nr_quotes = nltk_linguistic_features.count_punctuation(text,r'["\']+')

    all_features = {}
    readability_features = ['characters_stat', 'complexWords_stat', 'longWords_stat', 'numberSyllables_stat', 'lexicon_count_stat', 'sentence_count_stat', 'flesch_reading_ease_stat', 'smog_index_stat', 'flesch_kincaid_grade_stat', 'coleman_liau_index_stat', 'automated_readability_index_stat', 'difficult_words_stat', 'linsear_write_formula_stat', 'gunning_fog_stat']
    
    #Adding NLTK features
    all_features['word_count'] = word_count
    all_features['words_per_sent'] = words_per_sent
    all_features['nr_captalized_words'] = nr_captalized_words
    all_features['nr_per_stopwords'] = nr_per_stopwords
    all_features['count_urls'] = count_urls

    #Adding READABILITY features
    for field in readability_features:
        all_features[field] = getattr(readability, field)(text)
    
    for k, v in pos_tag_numbers.items():
        all_features[k] = v
    
    #Adding linguistic features based on NLTK 
    if(len(pos_tag_numbers)!=33):
        print("ERROR. Missing NLTK features-------------------")
        print(len(pos_tag_numbers))

    return all_features


def extract_feature_from_html(html_content, url):
    text, html_feature = extracted_html_feature(html_content)
    nltk_feature = get_NLTK_features(text)
    if nltk_feature is None: return None

    # merge two feature list
    nltk_feature.update(html_feature)
    nltk_feature['url'] = url
    nltk_feature['domain'] = urlparse(url).netloc
    return nltk_feature


if __name__ == '__main__':
    pass
