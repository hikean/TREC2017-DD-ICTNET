#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/5 上午1:23
# @version: 1.0

'''


是否小写，看情况而定
是否去除数字，暂时不去除

词干化本身会变成全部小写处理

一些细节需要考虑的，实体识别等......
'''

import logging

from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from src.utils.constants import STOPWORDS


old_stopwords = set([u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now', u'd', u'll', u'm', u'o', u're', u've', u'y', u'ain', u'aren', u'couldn', u'didn', u'doesn', u'hadn', u'hasn', u'haven', u'isn', u'ma', u'mightn', u'mustn', u'needn', u'shan', u'shouldn', u'wasn', u'weren', u'won', u'wouldn', u'I', u'Me', u'My', u'Myself', u'We', u'Our', u'Ours', u'Ourselves', u'You', u'Your', u'Yours', u'Yourself', u'Yourselves', u'He', u'Him', u'His', u'Himself', u'She', u'Her', u'Hers', u'Herself', u'It', u'Its', u'Itself', u'They', u'Them', u'Their', u'Theirs', u'Themselves', u'What', u'Which', u'Who', u'Whom', u'This', u'That', u'These', u'Those', u'Am', u'Is', u'Are', u'Was', u'Were', u'Be', u'Been', u'Being', u'Have', u'Has', u'Had', u'Having', u'Do', u'Does', u'Did', u'Doing', u'A', u'An', u'The', u'And', u'But', u'If', u'Or', u'Because', u'As', u'Until', u'While', u'Of', u'At', u'By', u'For', u'With', u'About', u'Against', u'Between', u'Into', u'Through', u'During', u'Before', u'After', u'Above', u'Below', u'To', u'From', u'Up', u'Down', u'In', u'Out', u'On', u'Off', u'Over', u'Under', u'Again', u'Further', u'Then', u'Once', u'Here', u'There', u'When', u'Where', u'Why', u'How', u'All', u'Any', u'Both', u'Each', u'Few', u'More', u'Most', u'Other', u'Some', u'Such', u'No', u'Nor', u'Not', u'Only', u'Own', u'Same', u'So', u'Than', u'Too', u'Very', u'S', u'T', u'Can', u'Will', u'Just', u'Don', u'Should', u'Now', u'D', u'Ll', u'M', u'O', u'Re', u'Ve', u'Y', u'Ain', u'Aren', u'Couldn', u'Didn', u'Doesn', u'Hadn', u'Hasn', u'Haven', u'Isn', u'Ma', u'Mightn', u'Mustn', u'Needn', u'Shan', u'Shouldn', u'Wasn', u'Weren', u'Won', u'Wouldn'])

Lucene_stopwords = set(['secondly', 'all', 'consider', 'whoever', 'four', 'edu', 'go', 'causes', 'seemed', 'rd', 'certainly', 'vs', 'to', 'asking', 'th', 'under', 'sorry', 'sent', 'far', 'every', 'yourselves', 'went', 'did', 'forth', 'try', 'p', 'says', 'yourself', 'likely', 'further', 'even', 'what', 'appear', 'brief', 'goes', 'sup', 'new', 'ever', 'whose', 'respectively', 'never', 'here', 'let', 'others', 'alone', 'along', 'quite', 'k', 'allows', 'howbeit', 'usually', 'whereupon', 'changes', 'thats', 'hither', 'via', 'followed', 'merely', 'while', 'viz', 'everybody', 'use', 'from', 'would', 'contains', 'two', 'next', 'few', 'therefore', 'taken', 'themselves', 'thru', 'tell', 'more', 'knows', 'becomes', 'hereby', 'herein', 'everywhere', 'particular', 'known', 'must', 'me', 'none', 'f', 'this', 'getting', 'anywhere', 'nine', 'can', 'theirs', 'following', 'my', 'example', 'indicated', 'indicates', 'something', 'want', 'needs', 'rather', 'meanwhile', 'how', 'instead', 'okay', 'tried', 'may', 'after', 'different', 'hereupon', 'such', 'a', 'third', 'whenever', 'maybe', 'appreciate', 'q', 'ones', 'so', 'specifying', 'allow', 'keeps', 'six', 'help', 'indeed', 'over', 'mainly', 'soon', 'course', 'through', 'looks', 'still', 'its', 'before', 'thank', 'thence', 'selves', 'inward', 'actually', 'better', 'willing', 'thanx', 'ours', 'might', 'then', 'non', 'someone', 'somebody', 'thereby', 'they', 'not', 'now', 'nor', 'several', 'hereafter', 'always', 'reasonably', 'whither', 'l', 'each', 'entirely', 'mean', 'everyone', 'doing', 'eg', 'ex', 'our', 'beyond', 'out', 'them', 'furthermore', 'since', 'looking', 're', 'seriously', 'got', 'cause', 'thereupon', 'given', 'like', 'que', 'besides', 'ask', 'anyhow', 'g', 'could', 'tries', 'keep', 'w', 'ltd', 'hence', 'onto', 'think', 'first', 'already', 'seeming', 'thereafter', 'one', 'done', 'another', 'awfully', 'little', 'their', 'accordingly', 'least', 'name', 'anyone', 'indicate', 'too', 'gives', 'mostly', 'behind', 'nobody', 'took', 'immediate', 'regards', 'somewhat', 'off', 'believe', 'herself', 'than', 'specify', 'b', 'unfortunately', 'gotten', 'second', 'i', 'r', 'were', 'toward', 'are', 'and', 'beforehand', 'say', 'unlikely', 'have', 'need', 'seen', 'seem', 'saw', 'any', 'relatively', 'zero', 'thoroughly', 'latter', 'that', 'downwards', 'aside', 'thorough', 'also', 'take', 'which', 'exactly', 'unless', 'shall', 'who', 'most', 'eight', 'but', 'nothing', 'why', 'sub', 'especially', 'noone', 'later', 'm', 'yours', 'definitely', 'normally', 'came', 'saying', 'particularly', 'anyway', 'fifth', 'outside', 'should', 'only', 'going', 'do', 'his', 'above', 'get', 'between', 'overall', 'truly', 'cannot', 'nearly', 'despite', 'during', 'him', 'regarding', 'qv', 'h', 'twice', 'she', 'contain', 'x', 'where', 'thanks', 'ignored', 'namely', 'anyways', 'best', 'wonder', 'said', 'away', 'currently', 'please', 'enough', 'various', 'hopefully', 'probably', 'neither', 'across', 'available', 'we', 'useful', 'however', 'come', 'both', 'c', 'last', 'many', 'whereafter', 'according', 'against', 'etc', 's', 'became', 'com', 'comes', 'otherwise', 'among', 'presumably', 'co', 'afterwards', 'seems', 'whatever', 'hers', 'moreover', 'throughout', 'considering', 'sensible', 'described', 'three', 'been', 'whom', 'much', 'wherein', 'hardly', 'wants', 'corresponding', 'latterly', 'concerning', 'else', 'former', 'those', 'myself', 'novel', 'look', 'these', 'value', 'n', 'will', 'near', 'theres', 'seven', 'almost', 'wherever', 'is', 'thus', 'it', 'cant', 'itself', 'in', 'ie', 'y', 'if', 'containing', 'perhaps', 'insofar', 'same', 'clearly', 'beside', 'when', 'gets', 'used', 'see', 'somewhere', 'upon', 'uses', 'kept', 'whereby', 'nevertheless', 'whole', 'well', 'anybody', 'obviously', 'without', 'very', 'the', 'self', 'lest', 'just', 'less', 'being', 'able', 'liked', 'greetings', 'regardless', 'yes', 'yet', 'unto', 'had', 'except', 'has', 'ought', 'around', 'possible', 'five', 'know', 'using', 'apart', 'necessary', 'd', 'follows', 'either', 'become', 'towards', 'therein', 'because', 'old', 'often', 'some', 'somehow', 'sure', 'specified', 'ourselves', 'happens', 'for', 'though', 'per', 'everything', 'does', 'provides', 'tends', 't', 'be', 'nowhere', 'although', 'by', 'on', 'about', 'ok', 'anything', 'oh', 'of', 'v', 'o', 'whence', 'plus', 'consequently', 'or', 'seeing', 'own', 'formerly', 'into', 'within', 'down', 'appropriate', 'right', 'your', 'her', 'there', 'inasmuch', 'inner', 'way', 'was', 'himself', 'elsewhere', 'becoming', 'amongst', 'hi', 'trying', 'with', 'he', 'whether', 'wish', 'j', 'up', 'us', 'until', 'placed', 'below', 'un', 'z', 'gone', 'sometimes', 'associated', 'certain', 'am', 'an', 'as', 'sometime', 'at', 'et', 'inc', 'again', 'uucp', 'no', 'whereas', 'nd', 'lately', 'other', 'you', 'really', 'welcome', 'e', 'together', 'having', 'u', 'serious', 'hello', 'once', 'Secondly', 'All', 'Consider', 'Whoever', 'Four', 'Edu', 'Go', 'Causes', 'Seemed', 'Rd', 'Certainly', 'Vs', 'To', 'Asking', 'Th', 'Under', 'Sorry', 'Sent', 'Far', 'Every', 'Yourselves', 'Went', 'Did', 'Forth', 'Try', 'P', 'Says', 'Yourself', 'Likely', 'Further', 'Even', 'What', 'Appear', 'Brief', 'Goes', 'Sup', 'New', 'Ever', 'Whose', 'Respectively', 'Never', 'Here', 'Let', 'Others', 'Alone', 'Along', 'Quite', 'K', 'Allows', 'Howbeit', 'Usually', 'Whereupon', 'Changes', 'Thats', 'Hither', 'Via', 'Followed', 'Merely', 'While', 'Viz', 'Everybody', 'Use', 'From', 'Would', 'Contains', 'Two', 'Next', 'Few', 'Therefore', 'Taken', 'Themselves', 'Thru', 'Tell', 'More', 'Knows', 'Becomes', 'Hereby', 'Herein', 'Everywhere', 'Particular', 'Known', 'Must', 'Me', 'None', 'F', 'This', 'Getting', 'Anywhere', 'Nine', 'Can', 'Theirs', 'Following', 'My', 'Example', 'Indicated', 'Indicates', 'Something', 'Want', 'Needs', 'Rather', 'Meanwhile', 'How', 'Instead', 'Okay', 'Tried', 'May', 'After', 'Different', 'Hereupon', 'Such', 'A', 'Third', 'Whenever', 'Maybe', 'Appreciate', 'Q', 'Ones', 'So', 'Specifying', 'Allow', 'Keeps', 'Six', 'Help', 'Indeed', 'Over', 'Mainly', 'Soon', 'Course', 'Through', 'Looks', 'Still', 'Its', 'Before', 'Thank', 'Thence', 'Selves', 'Inward', 'Actually', 'Better', 'Willing', 'Thanx', 'Ours', 'Might', 'Then', 'Non', 'Someone', 'Somebody', 'Thereby', 'They', 'Not', 'Now', 'Nor', 'Several', 'Hereafter', 'Always', 'Reasonably', 'Whither', 'L', 'Each', 'Entirely', 'Mean', 'Everyone', 'Doing', 'Eg', 'Ex', 'Our', 'Beyond', 'Out', 'Them', 'Furthermore', 'Since', 'Looking', 'Re', 'Seriously', 'Got', 'Cause', 'Thereupon', 'Given', 'Like', 'Que', 'Besides', 'Ask', 'Anyhow', 'G', 'Could', 'Tries', 'Keep', 'W', 'Ltd', 'Hence', 'Onto', 'Think', 'First', 'Already', 'Seeming', 'Thereafter', 'One', 'Done', 'Another', 'Awfully', 'Little', 'Their', 'Accordingly', 'Least', 'Name', 'Anyone', 'Indicate', 'Too', 'Gives', 'Mostly', 'Behind', 'Nobody', 'Took', 'Immediate', 'Regards', 'Somewhat', 'Off', 'Believe', 'Herself', 'Than', 'Specify', 'B', 'Unfortunately', 'Gotten', 'Second', 'I', 'R', 'Were', 'Toward', 'Are', 'And', 'Beforehand', 'Say', 'Unlikely', 'Have', 'Need', 'Seen', 'Seem', 'Saw', 'Any', 'Relatively', 'Zero', 'Thoroughly', 'Latter', 'That', 'Downwards', 'Aside', 'Thorough', 'Also', 'Take', 'Which', 'Exactly', 'Unless', 'Shall', 'Who', 'Most', 'Eight', 'But', 'Nothing', 'Why', 'Sub', 'Especially', 'Noone', 'Later', 'M', 'Yours', 'Definitely', 'Normally', 'Came', 'Saying', 'Particularly', 'Anyway', 'Fifth', 'Outside', 'Should', 'Only', 'Going', 'Do', 'His', 'Above', 'Get', 'Between', 'Overall', 'Truly', 'Cannot', 'Nearly', 'Despite', 'During', 'Him', 'Regarding', 'Qv', 'H', 'Twice', 'She', 'Contain', 'X', 'Where', 'Thanks', 'Ignored', 'Namely', 'Anyways', 'Best', 'Wonder', 'Said', 'Away', 'Currently', 'Please', 'Enough', 'Various', 'Hopefully', 'Probably', 'Neither', 'Across', 'Available', 'We', 'Useful', 'However', 'Come', 'Both', 'C', 'Last', 'Many', 'Whereafter', 'According', 'Against', 'Etc', 'S', 'Became', 'Com', 'Comes', 'Otherwise', 'Among', 'Presumably', 'Co', 'Afterwards', 'Seems', 'Whatever', 'Hers', 'Moreover', 'Throughout', 'Considering', 'Sensible', 'Described', 'Three', 'Been', 'Whom', 'Much', 'Wherein', 'Hardly', 'Wants', 'Corresponding', 'Latterly', 'Concerning', 'Else', 'Former', 'Those', 'Myself', 'Novel', 'Look', 'These', 'Value', 'N', 'Will', 'Near', 'Theres', 'Seven', 'Almost', 'Wherever', 'Is', 'Thus', 'It', 'Cant', 'Itself', 'In', 'Ie', 'Y', 'If', 'Containing', 'Perhaps', 'Insofar', 'Same', 'Clearly', 'Beside', 'When', 'Gets', 'Used', 'See', 'Somewhere', 'Upon', 'Uses', 'Kept', 'Whereby', 'Nevertheless', 'Whole', 'Well', 'Anybody', 'Obviously', 'Without', 'Very', 'The', 'Self', 'Lest', 'Just', 'Less', 'Being', 'Able', 'Liked', 'Greetings', 'Regardless', 'Yes', 'Yet', 'Unto', 'Had', 'Except', 'Has', 'Ought', 'Around', 'Possible', 'Five', 'Know', 'Using', 'Apart', 'Necessary', 'D', 'Follows', 'Either', 'Become', 'Towards', 'Therein', 'Because', 'Old', 'Often', 'Some', 'Somehow', 'Sure', 'Specified', 'Ourselves', 'Happens', 'For', 'Though', 'Per', 'Everything', 'Does', 'Provides', 'Tends', 'T', 'Be', 'Nowhere', 'Although', 'By', 'On', 'About', 'Ok', 'Anything', 'Oh', 'Of', 'V', 'O', 'Whence', 'Plus', 'Consequently', 'Or', 'Seeing', 'Own', 'Formerly', 'Into', 'Within', 'Down', 'Appropriate', 'Right', 'Your', 'Her', 'There', 'Inasmuch', 'Inner', 'Way', 'Was', 'Himself', 'Elsewhere', 'Becoming', 'Amongst', 'Hi', 'Trying', 'With', 'He', 'Whether', 'Wish', 'J', 'Up', 'Us', 'Until', 'Placed', 'Below', 'Un', 'Z', 'Gone', 'Sometimes', 'Associated', 'Certain', 'Am', 'An', 'As', 'Sometime', 'At', 'Et', 'Inc', 'Again', 'Uucp', 'No', 'Whereas', 'Nd', 'Lately', 'Other', 'You', 'Really', 'Welcome', 'E', 'Together', 'Having', 'U', 'Serious', 'Hello', 'Once'])


my_stopwords = (old_stopwords | Lucene_stopwords)
# english_punctuations = set(''',-.:;?()[]&!*@#$%|"+={}`~_<>^ \n\t''''')
english_punctuations = set(',-.:;?()[]&!*@#$%|"\'+={}`~_<>^ \n\t')
porter_stemmer = PorterStemmer()

def basic_preprocess_for_query(doc, code_type='utf8', if_lower=False, if_stem=False):
    if isinstance(doc, (str, unicode)):
        doc = cut_words(
            "".join(
                map(lambda c: c if c not in set(u"-“”‘’,/|\n\r\t;!?\"") else ' ',
                    doc)
            )
        )

    if not isinstance(doc, list):
        logging.error("basic_preprocess `doc` value error: %s", doc)
        # doc = doc.split()
    # print "BEFORE REMOVE PUNC:", doc
    # doc = remove_punctuations(doc)
    # 解决U.S. 不等于US的问题
    doc = remove_punctuations_word_level(doc)
    doc = remove_stop_words(doc)
    doc = [_.strip() for _ in doc if len(_.strip()) != 0]

    # doc = [_.decode('utf-8') for _ in doc if isinstance(_, unicode)]
    if if_stem:
        doc = stemmer_by_porter(doc)

    new_doc = []
    for _ in doc:
        if type(_) == unicode:
            try:
                new_doc.append( str(_) )
            except Exception, e:
                # print "!!!!!!!!=========> basic_preprocess_for_query CODE ERROR:", _

                logging.info( "!!!!!!!!=========> basic_preprocess_for_query CODE ERROR: %s" , _ )
                continue
        else:
            new_doc.append( _ )
    doc = new_doc
    # doc = [str(_) for _ in doc if type(_) == unicode  ]
    if if_lower:
        # doc = [ _.lower() for _ in doc if isinstance(_, unicode) ]
        doc = [_.lower() for _ in doc ]


    return doc

def basic_preprocess(doc, code_type='utf8', if_lower=False, if_stem=False):
    if isinstance(doc, (str, unicode)):
        doc = cut_words(
            "".join(
                map(lambda c: c if c not in set(u"-“”‘’,/|\n\r\t;!?\"") else ' ',
                    doc)
            )
        )

    if not isinstance(doc, list):
        logging.error("basic_preprocess `doc` value error: %s", doc)
        # doc = doc.split()
    # print "BEFORE REMOVE PUNC:", doc
    # doc = remove_punctuations(doc)
    # 解决U.S. 不等于US的问题
    doc = remove_punctuations_word_level(doc)
    doc = remove_stop_words(doc)
    doc = [_.strip() for _ in doc if len(_.strip()) != 0]

    # doc = [_.decode('utf-8') for _ in doc if isinstance(_, unicode)]
    # doc = [ _.encode('ascii') for _ in doc if type(_) == unicode ]

    # if if_stem:
    #     new_doc_list = []
    #     for w in doc:
    #         try:
    #             w = str(w)
    #             new_doc_list.append(w)
    #         except:
    #             print "ERROR STEM:", w
    #     doc = new_doc_list

    if if_stem:
        doc = stemmer_by_porter(doc)
        # if if_stem:
        #     new_doc_list = []
        #     for w in doc:
        #         try:
        #             w = str(w)
        #             new_doc_list.append(w)
        #         except:
        #             print "ERROR STEM:", w
        #     doc = new_doc_list
    if if_lower:
        # doc = [ _.lower() for _ in doc if isinstance(_, unicode) ]
        doc = [_.lower() for _ in doc ]

    new_doc_list = []
    for w in doc:
        try:
            w = str(w)
            new_doc_list.append(w)
        except:
            # print "ERROR STEM:", w
            pass
    doc = new_doc_list

    return doc

# def basic_preprocess(doc, code_type='utf8'):
#     if isinstance(doc, (str, unicode)):
#         doc = cut_words(
#             "".join(
#                 map(lambda c: c if c not in set(",/|\n\r\t;!?\"") else ' ',
#                     doc)
#             )
#         )
#
#     if not isinstance(doc, list):
#         logging.error("basic_preprocess `doc` value error: %s", doc)
#         # doc = doc.split()
#     # print "BEFORE REMOVE PUNC:", doc
#     # doc = remove_punctuations(doc)
#     # 解决U.S. 不等于US的问题
#     doc = remove_punctuations_word_level(doc)
#     doc = remove_stop_words(doc)
#     doc = [(_.strip()).encode('utf-8') for _ in doc if len(_.strip()) != 0]
#
#
#     return doc


def cut_words(sent, ignorecase=False):
    if ignorecase:
        return [w.lower() for w in word_tokenize(sent)]
    else:
        return word_tokenize(sent)


def remove_punctuations_word_level(word_list):
    global english_punctuations
    return [
        "".join(map(lambda c: c if c not in english_punctuations else '', w))
        for w in word_list
    ]
    ret = []
    for w in word_list:
        nw = ''
        for c in w:
            if c not in english_punctuations:
                nw += c
        ret.append(nw)
    return ret


def remove_punctuations(word_lists):
    global english_punctuations
    return [w for w in word_lists if w not in english_punctuations]


def remove_stop_words(doc):
    # TODO:修改编码。。。
    # [ w for w in doc if w not in stopwords.words('english') ]
    global my_stopwords
    return [w for w in doc if w not in my_stopwords]

# TODO:做得更细致一些...


def doc2clean_words(doc):
    words = doc.split(' ')
    words = [w.lower() for w in words]
    return words


def cut_words(doc):
    if type(doc) == list:
        return doc
    # TODO:需要把文档都处理一遍， 以及分词不要按照空格分
    return doc.split(' ')


def mk_bigrams(doc):
    words = cut_words(doc)
    ret = []
    for i in range(len(words) - 1):
        ret.append([words[i], words[i + 1]])
    return ret


def preprocess_query(q):
    q = q.replace('?', "")
    return q


DEFAULT_LANG = 'english'


def basic_clean(doc_list):
    return [w.strip() for w in doc_list if len(w.strip()) != 0]

# 小写：


def toLower(doc_list):
    return [w.lower() for w in doc_list]

# 词干化,王斌书上说porter算法比较好

def stemmer_by_porter(wordlist):
    global porter_stemmer
    # for w in word_list:
    # return [porter_stemmer.stem(w) for w in wordlist]
    ret = []
    for w in wordlist:
        try:
            ret.append(porter_stemmer.stem(w))
        except Exception as e:
            # print "ERROR STEM:", w
            pass
            # logging.exception("[!] porter_stemmer exception: %s", e)
    if len(ret) == 0 and len(wordlist) != 0:
        logging.warning(
            "empty stemming result, wordlist sample: %s", wordlist[:10])
    return ret

# 去除标点:


def remove_punc(doc_list):
    ret = []
    for w in doc_list:
        if len(w.strip()) == 0:
            continue
        ret.append(w.strip())
    return ret

# 去除停用词


def remove_stopwords(doc_list, lang='english'):
    return [w for w in doc_list if w not in set(stopwords.words(lang))]


if __name__ == '__main__':
    # print string.punctuation
    # pass
    word_list = [
    'Lt.', 'Gerard', 'Farao,', 'Marine', 'Forces',
    'Europe', 'Africa', 'SPMAGTF-CR-AF', 'Osprey', 'Night',
    'Training', 'U.S.']

    word_list = 'kaci hickox'.split()

    print stemmer_by_porter(word_list)

    # from src.utils.sample_doc import *
    # print type(sample_doc)
    # doc = ' Ebola virus disease  - Wikipedia'
    # doc = unicode(doc)
    # if type(doc) == unicode:
    #     doc = doc.encode('utf8')
    # print basic_preprocess(doc)


__END__ = True
