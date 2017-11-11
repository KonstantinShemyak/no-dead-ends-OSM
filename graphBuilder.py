from xml.sax import ContentHandler
import sys      # Only for debugging output


class HighwayGraphBuilder(ContentHandler):
    """Parse OpenStreetMap XML and fill provided pygraph object with highways."""

    def __init__(self, gr):
        self.gr = gr        # Question: does it COPY graph?
        self.inWay = False  # True when XML <way> tag is passed, its end tag is not
        self.inHighWay = False  # True when that way has 'highway=*' tag
        # For debugging only. Progress indicators:
        self.reportChunk = 1000  # After how many ways to report something
        self.wayCounter = 0  # How many ways got processed

    def startElement(self, name, attrs):
        # In OSM XML, ways cannot be nested.
        if name == 'way':
            self.inWay = True
            self.inHighWay = False
            self.wayNodeList = []
            self.id = attrs.get('id')
        elif name == 'tag':
            if self.inWay:
                if attrs.get('k') == 'highway':
                    self.inHighWay = True
        elif name == 'nd':
            # A node on a way. In OSM XML, they appear only inside ways.
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
                self.gr.add_edge((prev_node, v))
            prev_node = v

        self.wayCounter += 1
        if self.wayCounter % self.reportChunk == 0:
            sys.stderr.write('.')
