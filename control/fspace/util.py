import numpy as np

HTL = 1;
LTH = 0;

def findTransitions(values):
  mean = np.mean(values)
  binary = [0 if x < mean else 1 for x in values]
  prv = None
  transitions = []
  i = -1
  for v in binary:
    i += 1
    if prv == None:
      prv = v
      continue
    if prv > v:
      transitions.append((i, v, HTL))
    elif prv < v:
      transitions.append((i-1, prv, LTH))
    prv = v
  return transitions


def findGaps(values):
  transitions = findTransitions(values)
  gaps = []
  i = 0
  while i < len(transitions):
    x, y, t = transitions[i]
    if t == LTH and i < len(transitions) - 1:
      # next transition is ofcourse a HTL
      start = x
      end = transitions[i + 1][0]
      size = end - start
      gaps.append((start, end, size))
    i += 1
  return gaps