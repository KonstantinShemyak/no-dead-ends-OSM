import sys	# for sys.stdout.write()
import re
import fileinput
from time import gmtime, strftime
from pygraph.classes.graph import graph

# Copying and modifying ways seems to be easier with own simple "parser" than with SAX.
# We assume the following structure for the input XML:
# - inside <way>, only two elements are possible: <nd>, <tag>
# - <way id="..." ...other attributes...> is always on one line.
# - <way ...> is never self-closing, i.e. it is followed by </way> later.

def compatible_print(line):
  # Can it be so hard to print without newline in both Python 2 and 3?
  sys.stdout.write(line)

def addTaggedWays(file_input, cut_edges):
  """Go along OSM XML in file_input. Copy everything to stdout.
     Additionally, for each way, see if it has any segment(s) mentioned in cut_edges.
     If it has, output also additional way for each 'cutting' part of the original way.
  """
  
  # New way will be created like this. Second '%s' is for nodes.
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
      compatible_print(line)
      way_found = way_begin.search(line)
      if way_found:
        way_id = way_found.groups()[0]
        way_nodes = []
        way_has_cut_edges = False
        cur_cut_edge_nodes = ""
        in_cut_segment = False
        prev_node = None
        # Collector for all new ways made from cut segments of current way:
        cut_ways_collector = ""		
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
      # First, print the existing way
      compatible_print(out_buffer)
      out_buffer = ""
      way_id = False
      # and the closing tag of the existing way
      compatible_print(line)

      # Now, output new ways, if there are any
      if way_has_cut_edges:
      # We updated cut_ways_collector only when a cutting segment changes to non-cutting.
      # But if the whole way ended and we were in cutting segment, we must
      # update cut_ways_collector separately.
        if in_cut_segment:
          cut_ways_collector += new_way_template % (very_large_offset, cur_cut_edge_nodes)
          very_large_offset += 1
        compatible_print(cut_ways_collector)
      continue

    # We are still inside <way>, so add whatever we found to the future output
    out_buffer += line

