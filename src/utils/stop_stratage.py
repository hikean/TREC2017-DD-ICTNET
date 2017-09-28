# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/27 上午2:15
# @version: 1.0

from constants import NOT_ON_TOPIC

def get_not_on_topic_cnt(already_cover_topic_dict):
    # not_on_topic_cnt = 0
    # for subtopic_id, info in already_cover_topic_dict.items():
    #     if info.has_key(0):
    #         not_on_topic_cnt += info[0]
    # return not_on_topic_cnt
    if not already_cover_topic_dict.has_key(NOT_ON_TOPIC):
        already_cover_topic_dict[NOT_ON_TOPIC] = 0
    return already_cover_topic_dict[NOT_ON_TOPIC]


if __name__ == '__main__':
    pass

__END__ = True