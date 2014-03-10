#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
@author: T.J. Trimble

Input:
    root: location of files to parse
    location: location of parsing tools
    ace: location of ACE parser executable
    erg: location of ACE compiled ERG file
Output:
    ERG parses of alongside each discovered *auto_conll file
"""

import sys
import subprocess
import os
from ontonotes_yy_converter import convert # Open ontonotes converter

debug = 0

if len(sys.argv) > 1:
    # Commandline arguments
    root = sys.argv[1]
    location = "/NLP_TOOLS/tool_sets/ace/latest/"
    ace = "".join([location, "ace-0.9.13/ace"])
    erg = "".join([location, "erg-1111-x86-64-0.9.13.dat"])
else:
    # Debugging arguments
    ## On the cluster
#    root = "some_data/"
#    location = "/NLP_TOOLS/tool_sets/ace/latest/"
#    ace = "".join([location, "ace-0.9.13/ace"])
#    erg = "".join([location, "erg-1111-x86-64-0.9.13.dat"])
    ## On local
    root = "parse_data/"
    location = "/Users/dantiston/Documents/School/575-MRS/"
    ace = "".join([location, "ace/ace"])
    erg = "".join([location, "erg-1212.dat"])
    #debug = 1

toParse = []

# Get "auto_conll" files
for dirName, subdirs, files in os.walk(root):
    for fname in files:
        if fname[-len("auto_conll"):] == "auto_conll":
            toParse.append("%s/%s" % (dirName, fname))

if toParse == []:
    sys.exit("No data found to parse")

correct = 0.0
count = 0.0
logs = "parse_logs.txt"

for data in toParse:
    output = "".join([data[:-len("auto_conll")], "auto_parse"])
    temp_file = "".join([data.rsplit('/', 1)[0], "/tmp_parse_file.txt"])
    results = []
    document = ""

    with open(data, 'r') as data, open(output, 'w') as output, open('/dev/null', 'w') as null:
        for sentence in data.read().split('\n\n'):
            if sentence:
                comments = [line for line in sentence.split('\n') if line if line[0] == "#"]
                sentence = "\n".join([line for line in sentence.split('\n') if line if line[0] != "#"])
                for line in comments:
                    output.write("".join([line, '\n']))
                if sentence:
                    if sentence[0] not in {"#", "<"}: # sentence: parse sentence
                        sentence = convert(sentence)
                        with open(temp_file, 'w') as temp: # Erase temp file
                            temp.write(sentence)
                        count += 1
                        # Call to ACE at command line
                        p = subprocess.Popen([ace, "-y", "-g", erg, "-1T", "-r", "root_formal root_informal root_frag root_inffrag", temp_file], stdout=subprocess.PIPE, stderr=null)
                        result = p.communicate()[0].strip()
                        if result == "": # Probably an issue with ACE configuration
                            # This might be too strong
                            sys.stderr.write("No output from ACE; Configuration error likely")
                            sys.exit(1)
                        elif result[:len("SKIP:")] == "SKIP:": # No parses found
                            result = "No parse found"
                        else: # Parsed!
                            # This is where to change result to add sentence, if desired
                            results.append(result)
                            correct += 1
                        output.write("".join([" ".join(result.split()), '\n\n'])) # replace whitespace in MRS
                        if debug: print result, '\n'
            else:
                output.write("".join([sentence, '\n']))

    os.remove(temp_file) # delete temp_file

with open(logs, 'a') as logs:
    if count:
        logs.write(" ".join([str(correct), "/", str(count), "=", str(correct/count), "\n"]))
    else:
        logs.write("there was a problem accessing the data")
