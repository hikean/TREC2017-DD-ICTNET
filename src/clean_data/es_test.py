#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
# import time
# from os.path import exists, isfile, isdir
# from os import listdir

sys.path.append('../utils')

os.sys.path.append(os.path.dirname(os.path.abspath('.')))

# from JigClient import JigClient
# from es_client import ElasticClient


def interact_with_jig(jig, docs, interact_times=10):
    st_ptr = 0

    for i in range(interact_times):
        result = jig.run_itr(docs[st_ptr:st_ptr + 5])
        st_ptr += 5
        print "[#] iteration round:", i + 1
        for item in result:
            print "\t {} {} {} {}".format(
                item["ranking_score"], item["on_topic"], item["doc_id"],
                item.get("subtopics", [{}])[0].get("rating", "none"))


TOPICS = [('DD16-1', 'US Military Crisis Response'),
          ('DD16-2', 'Ebola Conspiracy Theories'),
          ('DD16-3', 'healthcare impacts of ebola'),
          ('DD16-4', 'Daniel Berehulak'),
          ('DD16-5', 'Ewedu as an Ebola Treatment'),
          ('DD16-6', 'Alleged Alternative Treatments for Ebola'),
          ('DD16-7', 'Urbanisation/Urbanization '),
          ('DD16-8', 'Dr. Olivet Buck'),
          ('DD16-9', 'Thomas Eric Duncan'),
          ('DD16-10', 'Economic impact of ebola'),
          ('DD16-11', 'U.S. healthcare workers'),
          ('DD16-12', 'is there a natural immunity to ebola'),
          ('DD16-13', 'Dr. Steven Hatch'),
          ('DD16-14', 'T.B. Joshua'),
          ('DD16-15', 'Maurice Iwu'),
          ('DD16-16', 'Modeling'),
          ('DD16-17', 'Kenema District Government Hospital'),
          ('DD16-18', 'Robots'),
          ('DD16-19', 'Attacks on ebola aid'),
          ('DD16-20', 'Pauline Cafferkey'),
          ('DD16-21', 'Ebola medical waste'),
          ('DD16-22', 'radio school'),
          ('DD16-23', 'Crowdfunding Crowdsourcing'),
          ('DD16-24', 'Olu-Ibukun Koye Spread EVD to Port Harcourt'),
          ('DD16-25', "Emory University's role in Ebola treatment"),
          ('DD16-26', 'Effects of African Culture'),
          ('DD16-27', 'kaci hickox')]

PL_TOPICS = [
          ('DD16-28', 'Is the distribution of permafrost changing in the Arctic?'),
          ('DD16-29', 'ice sheet sea level rise'),
          ('DD16-30', 'Where are basal boundary conditions in East Antarctica?'),
          ('DD16-31', 'sea level rise change strom surge'),
          ('DD16-32', 'polar oceans freshwater sensitivity'),
          ('DD16-33', 'sea-level rise and coastal erosion'),
          ('DD16-34', 'melting ice sheet ocean circulation'),
          ('DD16-35', 'snow accumulation rate Greenland'),
          ('DD16-36', 'Is the rate of snow accumulation changing in Antarctica?'),
          ('DD16-37', 'west antarctic ice sheet'),
          ('DD16-38', 'Are significant changes occurring in ocean productivity'),
          ('DD16-39',
           'How will shipping be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-40', 'Polar terrestrial ecosystems CO2 trace gas'),
          ('DD16-41', 'Artic sea ice fishery'),
          ('DD16-42',
           'How will offshore mineral extraction be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-43', 'Is ice sheet elevation changing'),
          ('DD16-44',
           'Are changes occurring in the distribution and productivity of Arctic vegetation?'),
          ('DD16-45',
           'How will subsistence fishing and hunting be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-46', 'Are changes occurring the coverage of the Arctic Sea ice'),
          ('DD16-47', 'Arctic sea ice thickness'),
          ('DD16-48', 'polar ocean global ocean circulation'),
          ('DD16-49', 'Are changes occurring in the circulation of the Arctic Sea'),
          ('DD16-50', 'planning for sea level rise'),
          ('DD16-51',
           'How will changes in sea-level rise affect coastal freshwater supply'),
          ('DD16-52', 'albedo feedback future climate change Poles'),
          ('DD16-53', 'climate change polar bears')]


NY_TOPICS = [
    ('dd17-1', 'Return of Klimt paintings to Maria Altmann'),
    ('dd17-2', 'Who Outed Valerie Plame?'),
    ('dd17-3', "First Women's Bobsleigh Debut 2002 Olympics"),
    ('dd17-4', 'Origins Tribeca Film Festival'),
    ('dd17-5', "Benazir Bhutto's legal problems"),
    ('dd17-6', 'Dwarf Planets'),
    ('dd17-7', 'Warsaw Pact Dissolves'),
    ('dd17-8', 'Concorde Crash'),
    ('dd17-9', 'Grenada-Cuba connections'),
    ('dd17-10', 'Leaning tower of Pisa Repairs'),
    ('dd17-11', 'Zebra mussel Hudson River'),
    ('dd17-12', 'Dental implants'),
    ('dd17-13', 'Albania pyramid scheme VEFA'),
    ('dd17-14', 'Montserrat eruption effects'),
    ('dd17-15', 'arik afek yair klein link'),
    ('dd17-16', 'Eggs actually are good for you'),
    ('dd17-17', 'Nancy Pelosi election as Speaker of the House'),
    ('dd17-18', 'Celebration of 50th Anniversary of Golden Gate Bridge'),
    ('dd17-19', 'Antioxidant food supplements'),
    ('dd17-20', 'Elizabeth Edwards Cancer'),
    ('dd17-21', 'Mega Borg Oil Spill'),
    ('dd17-22', 'Playstation 2 Console Sales and Prices'),
    ('dd17-23', 'USAF 1st Lt. Flinn discharged'),
    ('dd17-24', 'Melissa virus effect and monetary costs'),
    ('dd17-25', 'Last Checker Taxi Cab in NYC Auctioned'),
    ('dd17-26', 'New Scottish Parliament building'),
    ('dd17-27', 'Doping for professional sports'),
    ('dd17-28', 'Russian Organized Crime Involvement in Skating Scandal'),
    ('dd17-29', 'Chefs at Michelin 3- star Restaurants'),
    ('dd17-30', 'Nicotine addiction'),
    ('dd17-31', 'Implantable Heart Pump'),
    ('dd17-32', 'Million Man March on Washington'),
    ('dd17-33', 'refugees on nauru'),
    ('dd17-34', 'Rudolf Hess dies'),
    ('dd17-35', 'Bedbug infestation rising'),
    ('dd17-36', 'Global Warming Effect on NYC Region'),
    ('dd17-37', 'Gander Community Response After 9/11'),
    ('dd17-38', 'Iceland financial problems'),
    ('dd17-39', 'Munch Scream Recovered'),
    ('dd17-40', 'Church of England first female priests ordained'),
    ('dd17-41', 'Lion King Film'),
    ('dd17-42', 'Asian tiger mosquito'),
    ('dd17-43', 'Harry Connick Jr. on Broadway'),
    ('dd17-44', 'Whitney Museum Expansion to Meatpacking District'),
    ('dd17-45', 'Exhibitions of George Nakashima Works'),
    ('dd17-46', 'PGP'),
    ('dd17-47', 'Freon-12'),
    ('dd17-48', 'defense, precautions against modern ship piracy'),
    ('dd17-49', 'kangaroo survival'),
    ('dd17-50', 'Shrinking ice sheet in Greenland'),
    ('dd17-51', "Hurricane Katrina's Effects"),
    ('dd17-52', 'Solar power for U.S. homes'),
    ('dd17-53', "Alzheimer's and beta amyloid; detection, treatment?"),
    ('dd17-54', 'Indoor air pollution'),
    ('dd17-55', 'North Korea says it has nukes'),
    ('dd17-56', 'Abortion pill in the United States'),
    ('dd17-57', 'Libyan connection to Muslim coup in Trinidad Tobago'),
    ('dd17-58', 'cashew growing'),
    ('dd17-59', "Colonel Denard's mercenary activities"),
    ('dd17-60', 'Tupac Amaru and Shining Path, relationship, differences, similarities')]


def run_test(index, fields, topics, iter_count):
    import logging
    logging.root.setLevel(logging.WARNING)
    es_client = ElasticClient(doc_type="ebola", return_size=50, index=index)
    jig = JigClient(None, 1)
    for topic_id, topic in topics:
        print '\n', '-' * 80
        # if "ebola" not in topic.lower():
        #     topic = topic + ", ebola"
        print "[#] Topic: {}, TopicID: {}".format(topic, topic_id),
        jig.topic_id = topic_id
        result = es_client.search_ebola(keyword=topic, fields=fields)
        tuples = ElasticClient.result2tuple(result)
        print len(tuples)
        interact_with_jig(jig, tuples, iter_count)
    jig.judge()


def main():
    trec_id = 1

    fields = [["title^1.5", "content^2"],
              ["title", "content^2"]]
    index, iter_count = "trec{}".format(("", "2")[trec_id]), 1
    run_test(index, fields[trec_id], TOPICS[:56], iter_count)


if __name__ == '__main__':
    main()
