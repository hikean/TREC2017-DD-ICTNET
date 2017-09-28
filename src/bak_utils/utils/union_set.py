# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/24 下午11:41
# @version: 1.0


# int parent[];
# int root(int p){
#     if(parent[p]==-1) return p;
#     else return parent[p]=root(parent[p]);
# }
# void merge(int a,int b){
#     a=root(a);
#     b=root(b);
#     parent[a]=b;
# }
# memset(parent,-1,sizeof(parent))

class UnionSet(object):
    def __init__(self, cnt):
        pass

if __name__ == '__main__':
    pass

__END__ = True