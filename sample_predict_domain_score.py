import pickle
import requests
from bs4 import BeautifulSoup
from feature_extraction import extract_feature_from_html
import random
import pandas as pd
import numpy as np
from pprint import pprint
from fake_useragent import UserAgent
from urllib.parse import urlsplit
from argparse import ArgumentParser


UA = UserAgent()

def load_classifier(path):
    svm_classifier_sy = pickle.load(open(path, 'rb'))
    return svm_classifier_sy

def add_href_if_same_origin(href, final_domain, unique_links):
    if href is None:
        return
    part = urlsplit(href)
    path = part.path
    netloc = part.netloc
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    if netloc == '' or netloc == final_domain:
        if (path.count('-') >= 3 or path.count('_') >= 3):
            # and 'help' not in href
            # print(path)
            unique_links.add(path)
        elif 'id=' in href:
            if href[0] != '/':
                href = '/' + href
            print('id== {}'.format(href))
            unique_links.add(href)


def get_relevant_article(domain):
    """
    Given a domain name, randomly extract 5 news-like articles from the homepage

    NOTE: By default, the program first uses python request library to visit target domain.
          if there is no result, the program spawns an instance of Selenium, to simulate
          real Chrome browser behavior
    """
    if not domain.startswith('http'):
        domain = 'http://' + domain

    header = {'User-Agent':str(UA.chrome)}
    response = requests.get(domain, headers=header)
    final_url = response.url
    url_split = urlsplit(final_url)
    final_domain = url_split.netloc
    final_scheme = url_split.scheme
    print("final url is {}".format(final_url))
    print("final domain is {}".format(final_domain))

    if final_domain.startswith('www.'):
        final_domain = final_domain[4:]

    soup = BeautifulSoup(response.text, 'lxml')
    links = set([])

    for link in soup.findAll('a'):
        href = link.get('href')
        add_href_if_same_origin(href, final_domain, links)
        
    MAX_NUM_ARTICLE = 5
    all_feature = []
    if len(links) < MAX_NUM_ARTICLE: urls = links    
    else: urls = random.sample(list(links), MAX_NUM_ARTICLE)

    collected_urls = []
    collected_path = []
    
    for index, url in enumerate(urls):
        if not url.startswith('/'):
            url = '/' + url
        try:
            request_url = final_scheme + '://' + final_domain + url
            print('collect feature for URL {}'.format(request_url))
            response = requests.get(request_url, headers=header, timeout=8).text
            feature = extract_feature_from_html(response, request_url)
            if feature is None:
                continue
            all_feature.append(feature)
            collected_urls.append(request_url)
            collected_path.append(url)
        except Exception as e:
            print(e)

    return final_domain, collected_urls, collected_path, all_feature
    

def get_normalized_domain(domain):
    if not domain.startswith('http'):
        domain = 'http://' + domain
    part = urlsplit(domain)
    netloc = part.netloc

    if netloc == '':
        normalized_domain = None

    normalized_domain = netloc
    if netloc.startswith('www.'):
        normalized_domain = netloc[4:]
    return normalized_domain


def get_score(domain, svm_classifier):
    feature_names = np.array(['CC', 'CD', 'DT', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'MD', 'NN', 'NNP', 'NNPS', 'NNS', 'PDT', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB', 'a', 'abbr', 'address', 'article', 'audio', 'automated_readability_index_stat', 'b', 'base', 'big', 'blockquote', 'br', 'button', 'caption', 'center', 'characters_stat', 'cite', 'code', 'coleman_liau_index_stat', 'complexWords_stat', 'count_urls', 'dd', 'del', 'difficult_words_stat', 'dir', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'flesch_kincaid_grade_stat', 'flesch_reading_ease_stat', 'font', 'footer', 'form', 'gunning_fog_stat', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'i', 'iframe', 'img', 'input', 'ins', 'label', 'legend', 'lexicon_count_stat', 'li', 'link', 'linsear_write_formula_stat', 'longWords_stat', 'main', 'mark', 'menu', 'meta', 'nav', 'noscript', 'nr_captalized_words', 'nr_per_stopwords', 'numberSyllables_stat', 'object', 'ol', 'option', 'p', 'param', 'picture', 'pre', 'progress', 's', 'script', 'section', 'select', 'sentence_count_stat', 'small', 'smog_index_stat', 'source', 'span', 'strong', 'style', 'sub', 'sup', 'svg', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'u', 'ul', 'var', 'video', 'wbr', 'word_count', 'words_per_sent'])
    normalized_domain = get_normalized_domain(domain)
    if normalized_domain is None:
        return {'error': '{} is not a valid domain'.format(domain)}

    try:
        final_domain, collected_urls, collected_path, all_feature = get_relevant_article(normalized_domain)
        if collected_urls == []:
            return('Sorry: We are not able to compute a fakeness score for domain {}'.format(domain))
        
        df_X = pd.DataFrame(all_feature)

        # those three columns are not features used during the training process 
        
        X = df_X.drop(['url', 'domain', 'POS'], axis=1)
        X = X[feature_names].values.tolist()

        score = svm_classifier.decision_function(X)
        score = np.around(score, 2)

        X_transformed = svm_classifier.steps[0][1].transform(X)
        score_per_feature = np.multiply(X_transformed, svm_classifier.steps[-1][1].coef_[0])
        
        page_stat = []
        for index, s in enumerate(score):
            arg_sort = np.argsort(score_per_feature[index])
            page_stat.append({
                'full_url': collected_urls[index],
                'path': collected_path[index],
                'score': score[index],
                'score_per_feature': list(np.around(score_per_feature[index][arg_sort], 2)),
                'feature_sorted': list(feature_names[arg_sort])
            })

        score_info = {
                'mean_score': np.mean(score), 
                'std_score': np.std(score), 
                'page_stat': page_stat,
                'domain': normalized_domain,
        }
        return score_info

    except Exception as e:
        print(e)
        print('We are not able to compute a fakeness score')
        return {'error': str(e), 'domain': domain}


if __name__ == '__main__':
    ##################################
    ## change domain to the one     ## 
    ## you are interested in        ##
    ##################################
    parser = ArgumentParser()
    parser.add_argument('--domain', default=None, required=True)    
    params = parser.parse_args()
    # high fakeness score example 
    # domain = 'https://trumptrainnews.com/'

    # low fakeness score example 
    # domain = 'https://wsj.com/'

    # default model path 
    path='pretrained_model/svm_classifier_20200608.pkl'    
    svm_classifier_sy = load_classifier(path=path)
    result = get_score(domain=params.domain, svm_classifier=svm_classifier_sy)
    if 'error' in result:
        pprint(result)
    else:
        pprint(result['domain'])
        pprint(result['mean_score'])
        pprint([(page['full_url'], page['score']) for page in result['page_stat']])



