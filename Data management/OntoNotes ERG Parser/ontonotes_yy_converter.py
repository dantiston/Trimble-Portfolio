#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
@author: dantiston
"""

import sys

debug = 0

if len(sys.argv) > 1:
    # Command line arguments
    data = sys.argv[1]
else:
    # Debugging arguments
    data = ""
    debug = 1

def convert(onto):
    results = []
    onto = [[item.split() for item in value.split('\n')] for value in onto.split('\n\n')]
    for sentence in onto:
        string = [item[3] for item in sentence]
        tags = [item[4] for item in sentence]

        def index(data):
            indexes = []
            prev = 0
            pattern = "%s:%s"
            for i in range(len(data)):
                focus = data[i]
                if (focus == " ") or (i == len(data)-1): # If space or end
                    indexes.append(pattern % (prev, i))
                    prev = i+1
            return indexes

        indices = index(" ".join(string))

        result = " ".join(["("+", ".join([str(i),
                                          str(i),
                                          str(i+1),
                                          "<%s>" % indices[i],
                                           "1",
                                           '"%s"' % string[i].lstrip('/'), # cut off /
                                           "0",
                                           '"null"',
                                           '"%s" %s' % (tags[i], "1.0000")])+")"
                                    for i in range(len(sentence))])
        results.append(result)

    return "\n".join(results)

if debug:
    tests = {
    '''bc/msnbc/00/msnbc_0001   0   0              He   PRP   (TOP(S(NP*)       -    -   -    Carl_Kitnea  *    (ARG1*)   (92)
bc/msnbc/00/msnbc_0001   0   1             was   VBD         (VP*        -    -   -    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   2         charged   VBN         (VP*    charge  05   3    Carl_Kitnea  *       (V*)     -
bc/msnbc/00/msnbc_0001   0   3            with    IN         (PP*        -    -   -    Carl_Kitnea  *    (ARG2*      -
bc/msnbc/00/msnbc_0001   0   4          public    JJ      (NP(NP*        -    -   -    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   5    intoxication    NN            *)       -    -   -    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   6             and    CC            *        -    -   -    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   7       resisting   VBG         (NP*        -    -   2    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   8          arrest    NN        *)))))       -    -   1    Carl_Kitnea  *         *)     -
bc/msnbc/00/msnbc_0001   0   9              /.     .           *))       -    -   -    Carl_Kitnea  *         *      -

bc/msnbc/00/msnbc_0002   0   0              He   PRP   (TOP(S(NP*)       -    -   -    Carl_Kitnea  *    (ARG1*)   (92)
bc/msnbc/00/msnbc_0001   0   1             was   VBD         (VP*        -    -   -    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   2         charged   VBN         (VP*    charge  05   3    Carl_Kitnea  *       (V*)     -
bc/msnbc/00/msnbc_0001   0   3            with    IN         (PP*        -    -   -    Carl_Kitnea  *    (ARG2*      -
bc/msnbc/00/msnbc_0001   0   4          public    JJ      (NP(NP*        -    -   -    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   5    intoxication    NN            *)       -    -   -    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   6             and    CC            *        -    -   -    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   7       resisting   VBG         (NP*        -    -   2    Carl_Kitnea  *         *      -
bc/msnbc/00/msnbc_0001   0   8          arrest    NN        *)))))       -    -   1    Carl_Kitnea  *         *)     -
bc/msnbc/00/msnbc_0001   0   9              /.     .           *))       -    -   -    Carl_Kitnea  *         *      -''':

    '''(0, 0, 1, <0:2>, 1, "He", 0, "null", "PRP" 1.0000) (1, 1, 2, <3:6>, 1, "was", 0, "null", "VBD" 1.0000) (2, 2, 3, <7:14>, 1, "charged", 0, "null", "VBN" 1.0000) (3, 3, 4, <15:19>, 1, "with", 0, "null", "IN" 1.0000) (4, 4, 5, <20:26>, 1, "public", 0, "null", "JJ" 1.0000) (5, 5, 6, <27:39>, 1, "intoxication", 0, "null", "NN" 1.0000) (6, 6, 7, <40:43>, 1, "and", 0, "null", "CC" 1.0000) (7, 7, 8, <44:53>, 1, "resisting", 0, "null", "VBG" 1.0000) (8, 8, 9, <54:60>, 1, "arrest", 0, "null", "NN" 1.0000) (9, 9, 10, <61:62>, 1, ".", 0, "null", "." 1.0000)
(0, 0, 1, <0:2>, 1, "He", 0, "null", "PRP" 1.0000) (1, 1, 2, <3:6>, 1, "was", 0, "null", "VBD" 1.0000) (2, 2, 3, <7:14>, 1, "charged", 0, "null", "VBN" 1.0000) (3, 3, 4, <15:19>, 1, "with", 0, "null", "IN" 1.0000) (4, 4, 5, <20:26>, 1, "public", 0, "null", "JJ" 1.0000) (5, 5, 6, <27:39>, 1, "intoxication", 0, "null", "NN" 1.0000) (6, 6, 7, <40:43>, 1, "and", 0, "null", "CC" 1.0000) (7, 7, 8, <44:53>, 1, "resisting", 0, "null", "VBG" 1.0000) (8, 8, 9, <54:60>, 1, "arrest", 0, "null", "NN" 1.0000) (9, 9, 10, <61:62>, 1, ".", 0, "null", "." 1.0000)'''
    }

    for test in tests:
        result = convert(test)

        if result != tests[test]:
            print result

        if True:
#        if False:
            for i in range(len(result)):
                if result[i] != tests[test][i]:
                    print result[i-5:i+5]
        assert result == tests[test]





