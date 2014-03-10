#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
@author: T.J. Trimble and Jared Kramer

Input:
    test: Data to be tagged in:
        sentence_number-word_number-word true_label probability
    boundaries: Sentence boundaries in length of one sentence per line
    model_file: Model with features for each possible class
    beam_size: total beam size
    topN: Number of tags to keep at each node (for pruning)
    topK: Number of paths to keep alive at each time (for pruning)
Output:
    stdout: tagging output in:
        sentence_number-word_number-word true_label predicted_label probability
"""

import sys
import math
from operator import itemgetter
from math import log
from collections import defaultdict

debug = 0

# Print sys_output
if len(sys.argv) > 1:
    # Command line arguments
    test, boundaries, model_data, beam_size, topN, topK = sys.argv[1:]
else:
    # Debugging arguments
    test = "test.txt" # Data to decode
    boundaries = "boundary.txt" # lengths of each sentence on each new line
    model_data = "m1.txt" # Input from training step
    beam_size = 5 # Max gap of lgprob of best path and kept paths
    topN = 5 # Choose only the best topN tags
    topK = 5 # Max number of paths alive at each position
    #debug = 1

#####
# Configure commandline arguments
#####
beam_size, topN, topK = int(beam_size), int(topN), int(topK)

#####
# Functions
#####
# Define prune method
def prune(nodes):
    nodes = sorted([value for item in nodes.values() for value in item], key=itemgetter(1), reverse=True)
    max_prob = nodes[0][1]
    top = nodes[:topK]
    max_log = log(max_prob)
    top = {item[2]: [item] for item in top if (log(item[1]) + beam_size) >= max_log}
    return top

#####
# Open the files
#####
model = defaultdict(lambda: defaultdict(float))
all_labels = set() # these are tags
# Load the model file into a dictionary
with open(model_data, 'r') as model_data:
    model_data = model_data.read().strip().split("\n")
    for line in model_data:
        line = line.strip().split()
        if line[0:3] == ["FEATURES", "FOR", "CLASS"]: # Assumes feature is before instances
            label = line[-1]
            all_labels.add(label)
        else:
            feature, prob = line
            model[label][feature] = float(prob)

with open(boundaries, 'r') as boundaries:
    boundaries = boundaries.read().strip().split('\n')
with open(test, 'r') as test:
    test = test.read().strip().split('\n')

sentences = []
start = 0
for i in boundaries:
    i = int(i)
    sentences.append(test[start:start+i])
    start = start + i
total_correct = 0.0
total_length = 0.0

for sentence in range(len(sentences)):
    #####
    # Initialize some stuff
    #####
    correct = 0
    # data structure is map of depth -> path -> tag/prob
    nodes = defaultdict(lambda: defaultdict(list))

    #####
    # Base case
    #####
    # Form nodes s1,j
    nodes[0]["BOS"] = [("BOS", 1.0, "BOS", 1.0)]

    #####
    # Beam search
    #####
    # Execute beam search
    for i in range(len(sentences[sentence])):
        length = len(sentences[sentence])
        vector = sentences[sentence][i].split()
        i += 1 # Offset for base case
        word = vector[0].split('-')[-1]
        features = [vector[j] for j in range(2,len(vector[2:])+2,2)] # Get binary features
        # Add t-1, t-1/t-2 (remember to skip missing t-1/t-2 pairs)
        for path in nodes[i-1]:
            if debug: print "PATH:", path, '\n'
            for tag in nodes[i-1][path]:
                if debug: print "TAG:", tag
                # Add t-1 and t-2 for this wi, ti pair
                curPath = tag[2].split('_')
                if len(curPath) == 1:
                    curPath = ["BOS", "BOS"]
                # Add PrevT and PrevTwoTags
                features.extend(["prevT="+curPath[-1], "prevTwoTags="+"+".join(curPath[-2:])])
                # Calculate P(Y | X)
                tops = defaultdict(float)
                for label in all_labels:
                    tops[label] = model[label]["<default>"]
                    for feature in features:
                        tops[label] += model[label][feature]
                for label in tops:
                    tops[label] = math.exp(tops[label])
                Z = sum(tops.values())
                result = []
                for l in tops:
                    result.append((l, tops[l]/Z))
                projections = [(item[0], item[1]*tag[1], path+"_"+item[0], item[1]) for item in sorted(result, key=itemgetter(1), reverse=True)[:topN]] # added prob here
                for projection in projections:
                    projected_tag = projection[0]
                    new_path = "_".join([path, projected_tag])
                    nodes[i][new_path] = [projection]
                    if debug: print word, ':', projected_tag, '->', projection
                    if debug: print dict(nodes)
                if debug: print
            if debug: print '-'*10
        nodes[i] = prune(nodes[i])
    results = max([value for item in nodes[max(nodes.keys())].values() for value in item], key=itemgetter(1)) # adding path to nodes
    tags = results[2].split('_')
    # Rebuild probs
    i = length
    probs = [results[1]]
    path = results[2]
    while i != 0:
        i -= 1
        path = path.rsplit('_', 1)[0]
        probs.append(nodes[i][path][0][3])
    probs = list(reversed(probs))
    for i in range(length):
        word = sentences[sentence][i].split()
        gold = word[1]
        word = word[0].split('-')[-1]
        predicted_tag = tags[i+1]
        prob = probs[i+1]
        if gold == predicted_tag:
            correct += 1
        print "%s-%s-%s %s %s %s" % (sentence+1, i+1, word, gold, predicted_tag, prob)
    total_correct += correct
    total_length += length