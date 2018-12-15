Rationale
=========

`shputil.py` was born out of a need to modify large (>1GB) shapefiles
that could not be easily or successfully managed in programs like QGIS.
As an example QGIS was unable to perform a simple string
search-and-replace on a file over 26000 records, remaining unresponsive
and consuming 100% CPU even after 10 minutes. By comparison `shputil.py`
is able to perform the same operation, using `replace-field-values`, in
under 90 seconds.

Limitation
==========

Development is driven by my needs and not to make `shputil.py`
comprehensive, e.g. `replace-field-values` to support non-string
replacements. *Pull requests are however very welcome!*
