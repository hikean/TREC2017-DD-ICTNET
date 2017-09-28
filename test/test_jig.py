# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/9 下午5:01
# @version: 1.0

import commands

stat, output = commands.getstatusoutput('ps -ef | grep python')

print stat, output



__END__ = True