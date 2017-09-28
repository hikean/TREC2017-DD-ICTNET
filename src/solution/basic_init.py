# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/7 下午9:07
# @version: 1.0

import os
import sys

cur = os.path.curdir
up = os.path.join(cur, "..", '..')
up = os.path.abspath(up)

sys.path.append(up)


from src.global_settings import *



__END__ = True