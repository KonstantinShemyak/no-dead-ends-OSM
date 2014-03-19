no-dead-ends-OSM
================

Marking all dead ends and cut edges on OpenStreetMap
http://konstantin.shemyak.com/osm

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
  add new way for each cut edge. Give this way a (fake) osm_id, which
  is large enough not to conflict with any other way, and put it on
  layer high enough (e.g. 5).

- Performance. For a town area of about 50.000 inhabitants, graph contains
  67K nodes, 77K edges, and 12K cut edges located on 3K ways; processing
  took 11s. But area of 1M inhabitants, 400K nodes and 450K edges, graph
  construction takes 2 minutes, and then Python repeatedly segfaults in
  pygraph module (Intel Pentium 1.4GHz, 1G mem)

Dependencies
============

The code uses [pygraph.algorithms][http://dl.dropboxusercontent.com/u/1823095/python-graph/docs/pygraph.algorithms.accessibility-module.html] module 
In Ubuntu Linux, it is provided by *python-pygraph* package.

