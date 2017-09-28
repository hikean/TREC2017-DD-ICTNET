# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/10 上午2:11
# @version: 1.0


s = '''{
    "topic_id": "DD16-1",
    "doc_id": "ebola-ae8951e07f77c9288331e546ab6349541d70d4fc0c32ca3db9c76c96b0c03c71",
    "ranking_score": "6.0246024",
    "on_topic": "1",
    "subtopics": [
        {
            "subtopic_id": "DD16-1.1",
            "rating": 3,
            "passage_text": "Since Oct. 8 2014 a detachment of 100 U.S. Marines and sailors from Special Purpose Marine Air-Ground Task Force Crisis Response-Africa (SPMAGTF-CR-AF) provided support to Operation United Assistance (OUA) the U.S. response to the Ebola crisis in Liberia."
        },
        {
            "subtopic_id": "DD16-1.1",
            "rating": 2,
            "passage_text": "Since Oct. 8 2014 a detachment of 100 U.S. Marines and sailors from Special Purpose Marine Air-Ground Task Force Crisis Response-Africa (SPMAGTF-CR-AF) provided support to Operation United Assistance (OUA) the U.S. response to the Ebola crisis in Liberia."
        },
        {
            "subtopic_id": "DD16-1.3",
            "rating": 2,
            "passage_text": "Upon completion of their mission the Marines and sailors shifted focus towards conducting maintenance washing-down equipment in accordance with Centers for Disease Control and Prevention guidelines and preparing to move to U.S. Army Garrison Baumholder Germany where they will begin their 21-day controlled monitoring period. \u201c"
        },
        {
            "subtopic_id": "DD16-1.2",
            "rating": 3,
            "passage_text": "of U.S. Africa Command General David M. Rodriguez conducts a briefing on the DoD response to Ebola Oct. 7 2014"
        },
        {
            "subtopic_id": "DD16-1.2",
            "rating": 3,
            "passage_text": "U.S. Army Maj. Gen. Gary J. Volesky (right) commanding general of the 101st Airborne Division speaks with Lt. Col. Bruce Bancroft (left) and Col. David Mounkes of the Kentucky Air National Guard\u2019s 123rd Contingency Response Group Oct. 18 2014 during a tour of the Joint Operations Center for Joint Task Force-Port Opening Senegal at L\u00e9opold S\u00e9dar Senghor International Airport in Dakar"
        },
        {
            "subtopic_id": "DD16-1.2",
            "rating": 3,
            "passage_text": "U.S. Army Maj. Gen. Gary J. Volesky (right) commanding general of the 101st Airborne Division speaks with Lt. Col. Bruce Bancroft (left) and Col. David Mounkes of the Kentucky Air National Guard\u2019s 123rd Contingency Response Group Oct. 18 2014 during a tour of the Joint Operations Center for Joint Task Force-Port Opening Senegal at L\u00e9opold S\u00e9dar Senghor International Airport in Dakar"
        },
        {
            "subtopic_id": "DD16-1.2",
            "rating": 2,
            "passage_text": "of U.S. Africa Command General David M. Rodriguez conducts a briefing on the DoD response to Ebola Oct. 7 2014"
        },
        {
            "subtopic_id": "DD16-1.2",
            "rating": 2,
            "passage_text": "U.S. Navy Lt. Michael A. Schermer SPMAGTF-CR-AF lead medical planner. \u201c"
        },
        {
            "subtopic_id": "DD16-1.2",
            "rating": 2,
            "passage_text": "Africa U.S. Navy Lt. Jeffery Fornadley a flight surgeon with SPMAGTF Crisis Response \u2013"
        },
        {
            "subtopic_id": "DD16-1.2",
            "rating": 3,
            "passage_text": "Special Purpose MAGTF Crisis Response - Africa \u201d said U.S. Marine Corps Col. Robert C. Fulford SPMAGTF-CR-AF commanding officer."
        },
        {
            "subtopic_id": "DD16-1.2",
            "rating": 2,
            "passage_text": "U.S. Navy Lt. Michael A. Schermer SPMAGTF-CR-AF lead medical planner."
        }
    ]
}'''


s = s.strip()

import json

js = json.loads(s)
print js


if __name__ == '__main__':
    pass

__END__ = True