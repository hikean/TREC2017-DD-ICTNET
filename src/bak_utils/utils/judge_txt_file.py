import codecs
import sys

dict_topic_key = {}
cnt = {}
if __name__ == '__main__':
    
    #in_dir = "data/110002679.txt"
    in_dir = sys.argv[1]
    
    list_file_txt =  [line for line in codecs.open(in_dir,encoding='UTF-8').readlines()]
    for line in list_file_txt:
        
        list_line = line.split()
        
        if list_line[0] not in cnt:
            cnt[ list_line[0] ] = 1
        else:
            cnt[ list_line[0] ] += 1
            
        if list_line[0] not in dict_topic_key:
            dict_topic_key[ list_line[0] ] = set([])
        dict_topic_key[ list_line[0] ].add( list_line[2] )
    
    
    for key in dict_topic_key:
        print("topic_name:    ", key , "    cnt_sub:    ", cnt[key],"    cnt_unique:    ",len( dict_topic_key[key] ), "OK:", cnt[key] == len(dict_topic_key[key]) )