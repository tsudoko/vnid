PREFIX ?= /usr

.PHONY: clean

all: vndb_simple.py vnid.py
	echo "import vnid; vnid.main()" > __main__.py
	$(CURDIR)/zip vnid.zip $^ __main__.py
	sed "1i#!/usr/bin/env python3" < vnid.zip > vnid.pyz
	chmod 755 vnid.pyz
	rm vnid.zip

install: vnid.pyz
	if [ ! -e $(PREFIX)/bin ]; then mkdir $(PREFIX)/bin; fi
	cp vnid.pyz $(PREFIX)/bin/vnid

clean:
	rm vnid.pyz __main__.py
