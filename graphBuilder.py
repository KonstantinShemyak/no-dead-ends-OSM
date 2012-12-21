from pygraph.classes.graph import graph
from pygraph.algorithms.accessibility import cut_edges

import sys	# for syt.stdout.write()
from time import gmtime, strftime

from xml.sax import ContentHandler

class HighwayGraphBuilder(ContentHandler):
  "Parse OSM XML and fill provided pygraph object with highways."

  def __init__(self, gr):
    self.gr = gr;		# Does it COPY graph?
    self.inWay = False
    self.inHighWay = False
    self.wayCounter = 0		# How many ways got processed
    self.reportChunk = 1000	# After how many ways to report

  def startElement(self, name, attrs):
  # Assume that ways cannot be nested.
    if name == 'way':
      self.inWay = True
      self.inHighWay = False
      self.wayNodeList = []
      self.id = attrs.get('id')
    elif name == 'tag':
      if self.inWay:
        if attrs.get('k') == 'highway':
          self.inHighWay = True
          # print("Highway: %s" % self.id)
    elif name == 'nd':
      # A node on a way. They appear only inside ways.
      self.wayNodeList.append(attrs.get('ref'))

  
  def endElement(self, name):
    if not name == 'way': return

    # A way is ending here.
    self.inWay = False
    
    if not self.inHighWay: return
    # we do not care about non-highways

    # It was in fact a highway. Add all nodes and segments to graph.
    prev_node = self.wayNodeList[0]
    if not self.gr.has_node(prev_node):
      self.gr.add_node(prev_node)
    for v in self.wayNodeList[1:]:
      if not self.gr.has_node(v):
        self.gr.add_node(v)
      if not self.gr.has_edge((prev_node, v)):
        # Marking the edge: label = way id
        self.gr.add_edge((prev_node, v), label=self.id)
      prev_node = v
    
    self.wayCounter += 1
    if self.wayCounter % self.reportChunk == 0:
      sys.stderr.write('.')


