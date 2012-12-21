import sys	# for syt.stdout.write()
import re
import fileinput
from string import rstrip
from time import gmtime, strftime
from pygraph.classes.graph import graph

# We assume the following structure for the input XML:
# - Four top-level elements possible: <bounds>, <node>, <way>, <relation>
# - we just copy everything of <node> and <relation>
# - inside <way>, only two elements are possible: <nd>, <tag>
# - <way id="..." ...other attributes...> is always on one line.
# Copying and modifying ways seems to be easier with own simple "parser" than with SAX.

def markCutEdges(file_input, cut_edges):
  """Go along OSM XML. If a highway is in ways_with_cut set so that it contains segments from cut_edges set,
     do not split this highway into cutting and non-cutting segments, but just
     tag the whole way with deadEndTag.
     Otherwise, output same content.
     cutEdges is a subset of a graph.
  """
  
  # The tag, which we will put to found cut edges:
  deadEndTag = '  <tag k="construction" v="cut-edge"/>'
  way_id = False
  out_buffer = ""		# We collect everything into here while inside <way> element

  # Assumption: all ways begin and end like this. It is so in OSM exports.
  way_begin = re.compile("<way id=\"(\d+)\"")
  way_end = re.compile("</way>")
  nd = re.compile("<nd ref=\"(\d+)\"")

  for line in fileinput.input(file_input):
    if not way_id:
      print line,
      way_found = way_begin.search(line)
      if way_found:
        way_id = way_found.groups()[0]
        way_nodes = []
        way_has_cut_edges = False
        prev_node = None
      continue

    # Here, we are inside <way> element.

    nd_found = nd.search(line)
    if nd_found:	# New node reference on this way
      new_node = nd_found.groups()[0]
      way_nodes.append(new_node)
      if prev_node != None:
        # Check if this subsegment is in cut_edge set.
        if (not way_has_cut_edges) and (prev_node, new_node) in cut_edges:
          way_has_cut_edges = True
      prev_node = new_node

    if way_end.search(line):
      # End of the way. Flush all collected lines and process the way if needed.

      print out_buffer,
      if way_has_cut_edges:
        print deadEndTag
      out_buffer = ""
      way_id = False
      print line,
      continue

    out_buffer += line

if __name__ == "__main__":
  # Some test values:
  cut_edges = set(["41236365", "41230806", "41237255"])
  markCutEdges(sys.argv[1], cut_edges, None)


