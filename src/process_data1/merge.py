#! /usr/bin/python

import codecs
from os import listdir


def main(file_dir, out_file_name):
    out_file = codecs.open(out_file_name, "w", "utf-8")
    for file in listdir(file_dir):
        file_name = file_dir + "/" + file
        print file_name
        out_file.write(codecs.open(file_name, "r", "utf-8").read())
        out_file.write("\n")
    out_file.close()


if __name__ == "__main__":
    main("../datas/ebola_json2", "../datas/merge.txt")
