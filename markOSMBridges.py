import sys
from pygraph.classes.graph import graph
from pygraph.algorithms.accessibility import cut_edges
from xml.sax import make_parser
from graphBuilder import HighwayGraphBuilder
from markWays import markCutEdges
from time import gmtime, strftime	# Only for print_timing()

def print_timing(line):
  print >> sys.stderr, strftime("%Y-%m-%d %H:%M:%S", gmtime()), line

def main(sourceFileName):

  parser = make_parser()

  # http://wiki.python.org/moin/PythonSpeed
  print_timing('Started')
  # Construct the graph from highways to find cut edges:
  gr = graph()
  parser.setContentHandler(HighwayGraphBuilder(gr))
  # Looks like building the graph is about linear!
  parser.parse(sourceFileName)
  print_timing('Graph built, %d nodes, %d edges' % (len(gr.nodes()), len(gr.edges()) / 2))

  # Find cut edges and collect them to a set
  cutEdges = set(cut_edges(gr))
  print_timing("Cut edges: %d" % len(cutEdges))

  # Do the second pass and output changed highways
  markCutEdges(sourceFileName, cutEdges)
  print_timing('Marked')

if __name__ == "__main__":
  main(sys.argv[1])
