# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/7/18 下午9:22
# @version: 1.0


import os

subdir = "1987  1988  1989  1990  1991  1992  1993  1994  1995  1996  1997  1998  1999  2000  2001  2002  2003  2004  2005  2006  2007"
subdir = [ _.strip() for _ in subdir.split() if len(_.strip()) != 0 ]

print subdir

root_dir = "/home/zhangweimin/Data/TREC/new_york_times/data/"

if __name__ == '__main__':
    for v in subdir:
        path = root_dir + subdir
        cmd = 'cd ' + path + " && " + "for i in $(ls *.tgz);do tar xvf $i;done"
        os.system( cmd )


__END__ = True