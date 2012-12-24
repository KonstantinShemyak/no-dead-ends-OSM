import sys	# for syt.stdout.write()
import re
import fileinput
from time import gmtime, strftime
from pygraph.classes.graph import graph

# We assume the following structure for the input XML:
# - Four top-level elements possible: <bounds>, <node>, <way>, <relation>
# - we just copy everything of <node> and <relation>
# - inside <way>, only two elements are possible: <nd>, <tag>
# - <way id="..." ...other attributes...> is always on one line.
# Copying and modifying ways seems to be easier with own simple "parser" than with SAX.

def markCutEdges(file_input, cut_edges):
  """Go along OSM XML. Create new ways for each cut edge and tag them with deadEndTag.
     Was earlier: If a highway is in ways_with_cut set so that it contains segments from cut_edges set,
     tag the whole way with deadEndTag.
     Otherwise, output same content.
  """
  
  # New way will be created like this. Middle '%s' is for nodes.
  new_way_template = \
    ' <way id="%s" user="OSM-dead-end-painter" visible="true">\n' + \
    '%s' +\
    '  <tag k="highway" v="service"/>\n' +\
    '  <tag k="construction" v="cut-edge"/>\n' +\
    '  <tag k="layer" v="10"/>\n' +\
    ' </way>\n'
  # way_id must be unique within DB, so pick some very large start
  very_large_offset = 1000000000

  way_id = False		# False when outside a way. Otherwise, way_id.
  out_buffer = ""		# We collect everything into here while inside <way> element

  # Assumption: all ways begin and end like this. It is so in OSM exports.
  way_begin = re.compile("<way id=\"(\d+)\"")
  way_end = re.compile("</way>")
  nd = re.compile("<nd ref=\"(\d+)\"")

  for line in fileinput.input(file_input):
    if not way_id:
      print(line, end=" ")
      way_found = way_begin.search(line)
      if way_found:
        way_id = way_found.groups()[0]
        way_nodes = []
        way_has_cut_edges = False
        cur_cut_edge_nodes = ""
        in_cut_segment = False
        prev_node = None
        cut_ways_collector = ""		# Collector for all sub-ways made from cut edges of current way
      continue

    # Here, we are inside <way> element.

    nd_found = nd.search(line)
    if nd_found:	# New node reference on this way
      new_node = nd_found.groups()[0]
      way_nodes.append(new_node)
      if prev_node != None:
        # Check if this subsegment is in cut_edge set.
        # It can be also "the other way around", but it is important to store it
        # in the order in which the way traversed it.
        if ((prev_node, new_node) in cut_edges) or ((new_node, prev_node) in cut_edges):
          if in_cut_segment:
          # We were in cut segment, it just continues.
            cur_cut_edge_nodes += '  <nd ref="%s"/>\n' % new_node
          else:
          # We were not in cut segment. It started.
            cur_cut_edge_nodes = '  <nd ref="%s"/>\n  <nd ref="%s"/>\n' % (prev_node, new_node)
            in_cut_segment = True
            way_has_cut_edges = True
        else:
        # Last edge is not cutting.
          if in_cut_segment:
          # We were previously in cut segment, and it ended. Form the new way.
            cut_ways_collector += new_way_template % (very_large_offset, cur_cut_edge_nodes)
            very_large_offset += 1
          else:
          # We were not in cut segment, and are not. No action.
            pass
          in_cut_segment = False

        # end of "if (prev, new) in cut_edges"

      prev_node = new_node

    if way_end.search(line):
      # End of the way. Flush all collected lines and process the way if needed.

      print(out_buffer, end=" ")
      out_buffer = ""
      way_id = False
      print(line, end=" ")
      if way_has_cut_edges:
      # We updated cut_ways_collector only when a cutting segment changes to non-cutting.
      # But if the whole way ended and we were in cutting segment, we must
      # update cut_ways_collector separately.
        if in_cut_segment:
          cut_ways_collector += new_way_template % (very_large_offset, cur_cut_edge_nodes)
        print(cut_ways_collector, end=" ")
      continue

    out_buffer += line

if __name__ == "__main__":
  # Some test values:
  cut_edges = set(["41236365", "41230806", "41237255"])
  markCutEdges(sys.argv[1], cut_edges, None)


