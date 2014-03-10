#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
@author: T.J. Trimble and Jared Kramer

Input:
    train: One parse per line in Penn TreeBank Parser
    sentences: sentences to parse
    grammar_out: output location for trained PCFG grammar
    parses: output location for parses
Output:
    grammar_out: trained PCFG grammar
    parses_out: parses from PCFG grammar on sentences
"""

import sys
from nltk.tree import *
from collections import defaultdict, Counter as counter
import time

start_time = time.time()

debug = 0

if len(sys.argv) > 1:
    train, sentences, grammar_out, parses = sys.argv[1:]
else:
    train = "data/parses.train"
    sentences = "data/sents.test"
    grammar_out = "trained.pcfg"
    parses_out = "parses.hyp"
    debug = 1

############
## Functions
############

# This method helps fill in the bottom of each row in the parse table
def find_non_terminals(word):
    values = inversePCFG[(word,)]
    result = [(Tree(item[0], [word, '']), item[1]) for item in values]
    return result

##################
## Initializations
##################
grammar = defaultdict(list)
with open(train, 'r') as train:
    train = train.readlines()
with open(sentences, 'r') as sentences:
    sentences = sentences.readlines()

for s in train:
    for rule in Tree(s).productions():
        grammar[rule.lhs()].append(rule.rhs())

# Create pcfg the key is the lhs of the rule,
# the value is a dictionary where the key is a tuple of the RHS
# and the value is the prob for that RHS
pcfg = defaultdict(dict)
for left in grammar:
    for k, v in counter(grammar[left]).most_common():
        pcfg[left][k] = v/float(len(grammar[left]))

inversePCFG = defaultdict(list) # Load PCFG into inverse dict for bidirectional graph

for key in pcfg:
    for value in pcfg[key]:
        inversePCFG[value].append((key, pcfg[key][value]))

# Output trained grammar
with open(grammar_out, 'w') as grammar_out:
    for left in pcfg:
        for right in pcfg[left]:
            grammar_out.write(" ".join([str(left), "->", " ".join([str(item) for item in right]), "["+str(pcfg[left][right])+"]", "\n"]))

#################
## Main algorithm
#################

# Parse the data
previous = time.time()
numberOfParses = 0
with open(parses_out, 'w') as parses:
    for sentence in sentences:
        if debug: print sentence
        table = defaultdict(lambda: defaultdict(list))
        # Sentences already tokenized
        sentence = sentence.split()
        length = len(sentence)
        # j == end, i == start
        for end in range(2, length+2):
            # Gather a list of terminal tuples in the bottom of each column
            table[end-2][end-1] = find_non_terminals(sentence[end-2])
            for start in range(end-2, -1, -1):
                for split in range(start+1, end):
                    for left in table[start][split]: #list of tree, float tuples
                        for right in table[split][end-1]:
                            rules = inversePCFG[(left[0].node, right[0].node)]
                            table[start][end-1].extend([(Tree(item[0], [left[0], right[0]]), left[1]*right[1]*item[1]) for item in rules])

        if len(table[0][length]) == 0:
            parses.write("\n")
            if debug: print "Fail",
        else:
            numberOfParses += 1
            parse = sorted(table[0][length], key=lambda x: x[1])[-1]
            parses.write("".join([parse[0].pprint(1000000).replace(" )", ")"), "\n"])) # Output on one line
            if debug: print "Success",
        if debug: print time.time() - previous
        previous = time.time()
        if debug: print

if debug:
    print numberOfParses, "of", len(sentences), "parses;", "%%%.2f" % (numberOfParses*100/float(len(sentences)))
    print "%.4f seconds" % (time.time() - start_time)