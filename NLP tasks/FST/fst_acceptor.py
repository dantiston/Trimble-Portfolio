#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
@author: Jared Kramar and T.J. Trimble

Input:
    data: Data to parse in one sentence per line, quoted tokens
    FST: FST definition in Carmel format
Output:
    stdout: Output parse
"""

import sys
import string
from collections import defaultdict
from operator import itemgetter

if len(sys.argv) > 1:
    # Commandline arguments
    fst, inputs = sys.argv[1:]
    with open(inputs, 'r') as inputs:
        inputs = [item.split() for item in inputs.readlines() if item.strip()]
else:
    # Debugging arguments
    #fst = 'input/wfst1'
    fst = 'input/wfst2'
    inputs = [['"can"', '"they"', '"fish"'],
              ['"they"', '"can"', '"fish"'],
              ['"can"', '"they"', '"jump"'],
              ['"they"', '"fish"']]
    with open("input/ex2") as inputs:
        inputs = [item.split() for item in inputs.readlines() if item.strip()]

with open(fst, 'r') as fst:
    fst = fst.read()

############
## Functions
############

class ValidationException(Exception):
    pass

def read(carmel):
    fsa = [' '.join(item.split()) for item in carmel.split('\n')] # Reduce multiple whitespace
    chars = ''.join([string.letters, string.digits, '"*'])
    assert len(fsa) >= 2

    # State definitions
    transitions = {
    0: {'(': 1}, # waiting for new state
    1: {chars: 2}, # found initial parentheses
    2: {' ': 3}, # found beginning of source name
    3: {'(': 4}, # found end of source name
    4: {chars: 5}, # found beginning of transition
    5: {' ': 6}, # found end of transition
    6: {chars: 7}, # found beginning of destination
    7: {' ': 8}, # found end of destination
    8: {chars: 9}, # found beginning of output
    9: {' ': 10, ')': 13}, # found end of output
    10: {chars: 11, ')': 13}, # looking for weight / end of transition
    11: {')': 12}, # found beginning of weight, looking for end of transition
    12: {')': 14, '(': 4}, # found first transition
    13: {')': 14, '(': 4}
    # 14: found end of transition
    }
    # Load the FSA into dictionaries
    final = 14
    pointer = 0
    FSAweight = False
    FSAtransitions = defaultdict(list)
    for line in fsa[1:]:
        state = 0
        for char in range(len(line)):
            if state != final:
                for transition in transitions[state]:
                    if line[char] in transition:
                        state = transitions[state][transition]
                        if state in [2, 5, 7, 9, 11]: pointer = char
                        elif state in [3]: FSAsource = line[pointer:char]
                        elif state in [6]: FSAdestination = line[pointer:char]
                        elif state in [8]: FSAinput = line[pointer:char].strip()
                        elif state in [10, 13]: FSAoutput = line[pointer:char].strip()
                        elif state in [12]: FSAweight = line[pointer:char].strip()
                        elif state == final:
                            if FSAweight:
                                FSAtransitions[FSAsource].append((FSAdestination, FSAinput, FSAoutput, FSAweight))
                            else:
                                FSAtransitions[FSAsource].append((FSAdestination, FSAinput, FSAoutput, '1'))
    if state != final:
        ValidationException(' '.join(["Invalid transition:", line]))
    return FSAtransitions

### This is the recursive algorithm that checks all paths
### through the FST to determine if the input is accepted,
### the specified output, and the weights of the path

def find_path(graph, state, end, output, inputs, p):
    if state == end and len(inputs) == 0:
        results.append([' '.join(output), round(p, 5)])
        return list(output)
    if not state in graph:
        return None
    for tup in graph[state]:
        if float(tup[3]) < 0.0: print "Warning: Negative weight"
        if tup[1] == "*e*":
            output = output + [tup[2]]
            find_path(graph, tup[0], end, output, inputs, p*float(tup[3]))
        elif len(inputs) > 0 and tup[1] == inputs[0]:
            output = output + [tup[2]]
            find_path(graph, tup[0], end, output, inputs[1:], p*float(tup[3]))
            output = output[1:]

########
## Tests
########
readtests = {'''q2
(q0 (q1 "a" "b" 1))
(q1 (q2 "a" *e* 1))''':
    {'q0': [('q1', '"a"', '"b"', '1')], 'q1': [('q2', '"a"', '*e*', '1')]},
'''q2
(q0 (q1 "a" "b"))
(q1 (q2 "a" *e*))''':
    {'q0': [('q1', '"a"', '"b"', '1')], 'q1': [('q2', '"a"', '*e*', '1')]}}

for test in readtests:
    assert dict(read(test)) == readtests[test]

#################
## Initialization
#################
graph = read(fst)
fst = fst.split('\n')
start = fst[1].split('(')[1].strip()
end = fst[0].strip()
p = 1.0

############
## Execution
############

# Loop through th input string an output the answers
for line in inputs:
    output, results = [], []
    find_path(graph, start, end, output, line, p)
    print ' '.join(line), "\t=>",
    if results:
        results.sort(key=itemgetter(1), reverse=True)
        print results[0][0],
        if results[0][1] == 1: print '1'
        else: print results[0][1]
    else:
        print "*none* 0"