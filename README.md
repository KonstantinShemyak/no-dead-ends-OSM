no-dead-ends-OSM
================

Marking all dead ends and cut edges on OpenStreetMap

We want to wonder around with OpenStreetMap and never need to go 
back along the same way. To simplify the navigation, we would like
to add special marking to all cut-edges on the road graph.

The project reads OSM XML, builds the road graph, finds cut edges and
adds a tag to them (currently '<tag k="construction" v="cut-edge">').
Later, this XML can be rendered producing the wanted map.

Some problems:

- We could add own tag (like '<tag k="cut-edge" v="yes">), but the
  Mapnik renderer reads its data from own database, which accepts only
  known tags. So at least to render with Mapnik and DB, some known tag
  must be abused.

- It may sound good to split the way into alternating cutting and
  non-cutting parts, and tag cutting parts. But splitting an existing
  way into new ways will break relations. So the first approach is to
  tag all way which contains any cutting segments.

