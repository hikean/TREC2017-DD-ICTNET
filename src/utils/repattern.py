# -*- encoding: utf-8 -*-

import re, json
import nltk
from nltk.stem.lancaster import LancasterStemmer


def extract_subtopic_candidate(text, query):
    adj = set("JJ,JJR,JJS,LS".split(","))
    noun = set("NN,NNS,NNP,NNPS".split(","))
    verb = set("VB,VBD,VBG,VBN,VBP,VBZ".split(","))
    tags = set(list(adj) + list(noun) + list(verb))
    lancaster = LancasterStemmer()

    def rereplace(pattern):
        for a, b in [("(", "(?:"), ("a", "(?:a\\d+)"),
                     ("n", "(?:n\\d+)"), ("o", "(?:[av]\\d+)")]:
            pattern = pattern.replace(a, b)
        return pattern

    def get_tagname(tag):
        return "n" if tag in noun else "v" if tag in verb else "a"

    def makeres(words):
        return "".join(
            [get_tagname(word[1]) + str(idx) for idx, word in enumerate(words)]
        )

    def match_list(a, b):
        # print json.dumps(a), json.dumps(b)
        # print " ".join(a), "\t", " ".join(b)
        result = 0
        for x, y in zip(a, b):
            if lancaster.stem(x).lower() == lancaster.stem(y).lower():
                result += 1
            else:
                break
        return result

    def extract_index(text):
        # print text
        return [int(n) for n in re.findall("\\d+", text)]

    def takeout(text, index=0):
        return [word[index] for word in text]

    def patterns(query, text):
        # print "Query", query
        # print "Text", text
        wtext = [word[0] for word in text]
        results = []

        def pat1():
            # mheads = set(re.findall(rereplace("(a?n+o*)?"), makeres(text)))
            text_stem = [lancaster.stem(word) for word in takeout(text)]
            query_stem = [lancaster.stem(word) for word in takeout(query)]
            # print " ".join(text_stem), " ".join(query_stem)
            left_index = [index for index, word in enumerate(text_stem)
                          if word == query_stem[0]]
            mheads = []
            for index in left_index:
                mheads.extend(re.findall(
                    rereplace("(a?n+o*)?$"),
                    makeres(text[:index])))
                # print mheads, makeres(text[:index + 1])
            for matched in mheads:
                # print "matched", matched
                wquery = [word[0] for word in query]
                rest_text, mtext = text, []
                if matched != "":
                    idx = extract_index(matched)
                    if len(idx) > 0:
                        mtext = wtext[idx[0]: idx[-1] + 1]
                        rest_text = text[idx[-1] + 1:]
                qlen = match_list(wquery, takeout(rest_text))
                # print "qlen", qlen
                rest_text = rest_text[qlen:]
                if qlen == len(wquery):  # pattern 1
                    mtext += wquery
                    mtails = re.findall(
                        rereplace("^(o*a?n+)?"), makeres(rest_text))
                    if len(mtails) > 0:
                        idx = extract_index(mtails[0])
                        if len(idx) > 0:
                            mtext += takeout(rest_text[0:idx[0] + 1])
                    results.append((" ".join(mtext), 1))
                elif qlen > 0:
                    if matched != "":  # pattern 4
                        results.append((" ".join(mtext + wquery), 4))
                    mtext += wquery[:qlen]
                    wquery = wquery[qlen:]
                    for word, right, tail in pat3(rest_text, wquery):
                        results.append((" ".join(mtext + word + right + tail),
                                        2))  # pattern3

        def pat3(txt, query):
            text = [x for x in txt]
            headt, ret = [], []
            if txt is None or query is None:
                return ret
            while len(text) >= len(query):
                mlen = match_list(takeout(text), query)
                if mlen == len(query):
                    rest_text = text[mlen:]
                    mtails = re.findall(
                        rereplace("^(o*a?n+)?"),
                        makeres(rest_text)
                    )
                    for rtail in set(mtails):
                        idx = extract_index(rtail)
                        tail = []
                        if len(idx) > 0:
                            tail = takeout(rest_text[:idx[-1] + 1])
                        ret.append((headt, query, tail))
                headt.append(text[0])
                text = text[1:]
            return ret

        pat1()
        flag = True
        wquery = takeout(query)
        query = takeout(query)
        while len(query) > 1 and flag:
            query = query[1:]
            for word, right, tail in pat3(text, query):
                results.append((" ".join(wquery + tail), 3))
                flag = False
        return results

    def seperate(text):
        for sep in [". ", "! ", ": ", "; ", "\t"]:
            text = text.replace(sep, "\n")
        return [line.strip() for line in text.split("\n") if len(line) > 0]

    def clean_text(text):
        tokens = [nltk.word_tokenize(sentence) for sentence in seperate(text)]
        lines = [nltk.pos_tag([wd for wd in line if len(wd) > 1]) for line in
                 tokens if len(line) > 0]
        return [[wd for wd in line if wd[1] in tags] for line in lines]

        # lines = [map(lambda wd: wd if wd not in stopwords and len(wd) > 1
        #          else "", line) for line in tokens]
        # lines = [[word for word in line if len(word) > 2]for line in lines if
        #          len(line) > 0]
        return lines
        # return [" ".join(line) for line in lines if len(line) > 0]

    topics = []
    query = clean_text(query)[0]
    for text in clean_text(text):
        topics.extend(patterns(query, text))
    return topics


if __name__ == "__main__":

    ret = extract_subtopic_candidate(u'The word dragon entered the English language in the early 13th century from Old French dragon, which in turn comes from Latin dragon (nominative dragon) meaning "huge strong dragon", from the Greek word δράκων, dragon (genitive dragon, δράκοντος) "serpent giant seafish". The Greek and Latin term referred to any great serpent, not necessarily mythological, and this usage was also current in English up to the 18th century.', 'dragon')
    for topic in ret:
        print topic
    from repattern import extract_subtopic_candidate as extract
    s, q = "we give a brown rice porridge diet's recipe", "rice diet"
    # brown rice nice diet's recipe
    # s, q = "you must be aware of the diet's side-effect", "porridge diet"
    # porridge diet effect
    print "--------"
    print extract(s,q)
