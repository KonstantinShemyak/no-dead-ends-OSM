No-dead-ends-OSM
================

This project marks the dead ends (in fact, all 
[cut edges](https://en.wikipedia.org/wiki/Bridge_(graph_theory)))
on OpenStreetMap.
See an [example](http://konstantin.shemyak.com/osm/no-dead-ends.html).

We want to wonder around, navigating with OpenStreetMap, and never need to go 
back along the same way. To see where not to go, we'd like
to add special marking to all cut-edges on the road graph.

The project reads OSM XML, builds the road graph, finds cut edges and
adds a tag to them (currently `<tag k="construction" v="cut-edge">`).
Later, this XML can be rendered to show the map with cut edges marked.

Technical problems, or dirty temporary workarounds:
---------------------------------------------------

- We could add own tag (like `<tag k="cut-edge" v="yes">`), but the
  Mapnik will not understand it.
  So in order to render with Mapnik, some tag known to it
  must be (ab)used.

- It may sound good to split the way into alternating cutting and
  non-cutting parts, and tag the cutting parts. But splitting an existing
  way into new ways will break relations. So the first approach is to
  add new way for each cut edge. Give this way a fake `osm_id`, which
  is large enough not to conflict with any other way, and put it on
  layer high enough (e.g. 5).

- Performance. For a town area of about 50.000 inhabitants, graph contains
  67K nodes, 77K edges, and 12K cut edges located on 3K ways; processing
  took 11s. But area of 1M inhabitants, 400K nodes and 450K edges, graph
  construction takes 2 minutes, and then Python repeatedly segfaults in
  pygraph module (Intel Pentium 1.4GHz, 1G mem)

Dependencies
============

The code uses [pygraph.algorithms](http://dl.dropboxusercontent.com/u/1823095/python-graph/docs/pygraph.algorithms.accessibility-module.html)
module.
In Ubuntu Linux, it is provided by *python-pygraph* package.

Usage
=====

	python markOSMbridges.py source.xml [> result.xml]

