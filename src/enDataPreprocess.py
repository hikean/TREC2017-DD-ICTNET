# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/6/17 下午11:05
# @version: 1.0

import re
import string
import nltk

class EnPreprocess:

    def __init__(self):
        print'English token and stopwords remove...'
        self.regex = re.compile('[%s]' % re.escape(string.punctuation))
    def FileRead(self,filePath):#读取内容
        f =open(filePath)
        raw=f.read()
        return raw
    def WriteResult(self,result,resultPath):
        #self.mkdir(str(resultPath).replace(str(resultPath).split('/')[-1],''))
        f=open(resultPath,"w") #将结果保存到另一个文档中
        f.write(result)
        f.close()
    def SenToken(self,raw):#分割成句子
        sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
        try:
            sents =sent_tokenizer.tokenize(raw)
        except:
            return ""
        return  sents

    def WordTokener(self,sent):#将单句字符串分割成词
        result=''
        wordsInStr= nltk.word_tokenize(sent)
        return wordsInStr

    def CleanLines(self,line):
        identify =string.maketrans('', '')
#         cleanLine= line.translate(identify, delEStr) #去掉ASCII 标点符号和空格
        cleanLine =line.translate(identify) #去掉ASCII 标点符号
        cleanLine = self.regex.sub(' ', cleanLine)
        return cleanLine

    def CleanWords(self,wordsInStr):#去掉标点符号，长度小于3的词以及non-alpha词，小写化
        cleanWords=[]
        #stopwords ={}.fromkeys([ line.rstrip() for line in open(conf.PreConfig.ENSTOPWORDS)])
        for words in wordsInStr:
            cleanWords+= [[w.lower() for w in words if w.lower()  and 1<=len(w)]]
        return cleanWords

    def StemWords(self,cleanWordsList):
        stemWords=[]
#         porter =nltk.PorterStemmer()#有博士说这个词干化工具效果不好，不是很专业
#        result=[porter.stem(t) for t in cleanTokens]
        for words in cleanWordsList:
           stemWords+=[[wn.morphy(w) for w in words]]
        return stemWords

    def WordsToStr(self,stemWords):
        strLine=[]
        for words in stemWords:
           strLine+=[w for w in words]
        return strLine


if __name__ == '__main__':
    pass

__END__ = True