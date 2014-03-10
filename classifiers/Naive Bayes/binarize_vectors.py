#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
@author: T.J. Trimble and Jared Kramer

Input:
    Files with real valued vectors
Output:
    Files with binary valued vectors
"""

import sys

if len(sys.argv) > 1:
    # Command line arguments
    train_vectors, test_vectors, train_out, test_out = sys.argv[1:]
else:
    # Debugging arguments
    train_vectors = "train.vectors.txt"
    test_vectors = "test.vectors.txt"
    train_out = "train.vectors.binary.txt"
    test_out = "test.vectors.binary.txt"

def binarize(vec_list, out):
    for vector in vec_list:
        for word in vector.split():
            if ":" in word:
                out.write("".join([word.split(":")[0], ":1 "]))
            else:
                out.write(" ".join([word, ""]))
        out.write("\n")

train_vectors = open(train_vectors, 'r').read().split("\n")
test_vectors = open(test_vectors, 'r').read().split("\n")

train_out = open(train_out, 'w')
test_out = open(test_out, 'w')

binarize(train_vectors, train_out)
binarize(test_vectors, test_out)
