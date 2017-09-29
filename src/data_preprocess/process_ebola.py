import cbor  
from urllib import unquote
from os import listdir
import json
from boilerpipe.extract import Extractor
from HTMLParser import HTMLParser  


def strip_tags(html):  
	html = html.strip()  
	html = html.strip("\n")  
	result = []  
	parser = HTMLParser()  
	parser.handle_data = result.append  
	parser.feed(html)  
	parser.close()  
	return ''.join(result)


files = [f for f in listdir('dd') if 'ebola-web' in str(f)]


count = 0

idx = 0
st = set([])

for f in files:
	file = open('dd/'+f,'r')
	count1 = 0
	try:
		while(1):
			ret = cbor.load(file)
			ouput_file = open('ebola_htmls/'+str(idx)+'.json','w')
			dict = {}
			url = ret["url"]
			url = unquote(url)
			dict["url"] = url
			dict["key"] = ret["key"]
			extractor = Extractor(extractor='ArticleExtractor',html=ret["response"]["body"])
			dict["title"] = extractor.source.getTitle()	
			dict["content"] = extractor.source.getContent()
			if len(dict["content"])<500:
				dict["content"] = strip_tags(ret["response"]["body"])
				print 'Error At %s and restart extract, len = %d'%(str(idx)+'.json',len(dict["content"]))
				pass
			ouput_file.write('['+json.dumps(dict)+']')
			ouput_file.close()
			print 'finish ', idx, 'len = ' , len(dict["content"])
			idx+=1
			count1+=1
	except:
		print 'file = ',f , 'total = ' , count1
		count += count1

print 'count = ', count

for url in st:
	print url

print len(st)
