"""Find and mark cut edges in OSM XML way graph. 

Read OSM XML. Construct graph from its ways. Find cut edges in that graph.
Output the same XML but with additional ways created from each cut segment.
These new ways have own tag, which can be used for rendering.

A pipe cannot be used instead of the file, as the input XML is processed in two passes.
"""
import sys
from pygraph.classes.graph import graph
from pygraph.algorithms.accessibility import cut_edges
from xml.sax import make_parser
from graphBuilder import HighwayGraphBuilder
from markWays import markCutEdges
from time import gmtime, strftime	# Only for print_timing()

# Only for watching the progress, can be turned off:
def print_timing(line):
  timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
  sys.stderr.write("%s %s\n" % (timestamp, line))

def main(source_file):

  print_timing('Started')
  parser = make_parser()
  # Construct the graph from highways to find cut edges:
  gr = graph()
  parser.setContentHandler(HighwayGraphBuilder(gr))
  # Looks like building the graph is about linear in time!
  parser.parse(source_file)
  print_timing('Graph built, %d nodes, %d edges' % (len(gr.nodes()), len(gr.edges()) / 2))

  # Find cut edges and collect them to a set
  cutEdges = set(cut_edges(gr))
  print_timing("Cut edges: %d" % len(cutEdges))

  # Do the second pass and output changed highways
  markCutEdges(source_file, cutEdges)
  print_timing('Marked')

if __name__ == "__main__":
  main(sys.argv[1])
