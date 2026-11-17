# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
# Cross-build the supplied QDOS port without replacing its original binaries.
CC = qdos-gcc
CFLAGS = -O
CPPFLAGS = -Iinclude -I$(BUILD) -DQDOS
BUILD = build/qdos
QDOS_LIBDIR ?= $(abspath $(dir $(shell command -v $(CC)))/../lib)
SLB ?= $(shell $(CC) -print-prog-name=slb)
DIST = build/dist
EDITOR = blk cmd1 cmd2 ctype curses cut ex input main misc modify move1 \
         move2 move3 move4 move5 opts recycle redraw regexp regsub system \
         tio tmp vars vcmd vi unix tinytcap
OBJECTS = $(addprefix $(BUILD)/,$(addsuffix .o,$(EDITOR)))
OBJECTS += $(BUILD)/qdos_temp_storage.o
PROGRAMS = elvis ctags ref elvrec fmt elvprsv
SOURCES = $(wildcard src/*.c)
HEADERS = $(wildcard include/*.h)
VERSION_HEADER = $(BUILD)/qlvi_version.h

.PHONY: all package bin test test-launcher version bump-version
all: $(addprefix $(BUILD)/,$(PROGRAMS))

version:
	python3 tools/version.py show

bump-version:
	python3 tools/version.py set "$(NEW_VERSION)"

test: package
	python3 tests/test_version.py
	python3 tests/test_version_messages.py
	python3 tests/test_commandline.py
	python3 tests/test_builtin_terminal.py
	python3 tests/test_temp_storage.py
	python3 tests/test_package_qdos.py

test-launcher: package
	python3 tests/test_vi_rext.py

$(BUILD):
	mkdir -p $@

$(VERSION_HEADER): VERSION tools/version.py | $(BUILD)
	python3 tools/version.py header $@

define compile_rule
$(BUILD)/$(shell echo $(notdir $(basename $(1))) | tr A-Z a-z).o: $(1) $(HEADERS) $(VERSION_HEADER) | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -x c -c $$< -o $$@
endef
$(foreach source,$(SOURCES),$(eval $(call compile_rule,$(source))))

$(BUILD)/qdos_temp_storage.o: src/qdos/temp_storage.c $(HEADERS) | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# Force the curses console translator into the link. Merely using -lcurses
# can leave the default libc translator selected, depending on archive order.
$(BUILD)/_conwrite.o: $(QDOS_LIBDIR)/libcurses.a | $(BUILD)
	cd $(BUILD) && $(SLB) -x $(QDOS_LIBDIR)/libcurses.a _conwrite

$(BUILD)/elvis: $(OBJECTS) $(BUILD)/_conwrite.o
	$(CC) -o $@ $(OBJECTS) $(BUILD)/_conwrite.o -lcurses

$(BUILD)/elvprsv: src/elvprsv.c src/prsvunix.c $(HEADERS) $(VERSION_HEADER) $(BUILD)/ctype.o | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ src/elvprsv.c $(BUILD)/ctype.o

define utility_rule
$(BUILD)/$(1): src/$(1).c $(HEADERS) $(VERSION_HEADER) | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -x c $$< -o $$@
endef
$(foreach program,ctags ref elvrec fmt,$(eval $(call utility_rule,$(program))))

$(BUILD)/ctags: src/ctype.c

# A stable executable name for the resident launcher. The SNL daemon strips
# this Q-emulator wrapper and exposes its metadata as a native QDOS header.
package: $(DIST)/elvis $(DIST)/vi_rext $(DIST)/VERSION

# Refresh the checked-in user downloads after building a new version.
bin: package
	mkdir -p bin
	cp $(DIST)/elvis $(DIST)/vi_rext $(DIST)/VERSION bin/

$(DIST):
	mkdir -p $@

$(DIST)/VERSION: VERSION | $(DIST)
	cp $< $@

$(DIST)/elvis: $(BUILD)/elvis tools/package_qdos.py | $(DIST)
	python3 tools/package_qdos.py $< $@

# This linker automatically includes crt.o. Supply our own resident entry
# instead of the C job startup, and explicitly search this directory first.
$(BUILD)/rext/crt.o: src/qdos/vi_rext.s
	mkdir -p $(BUILD)/rext
	qdos-as $< -o $@

$(BUILD)/rext/empty.o: | $(BUILD)
	mkdir -p $(BUILD)/rext
	printf '        .sect .text\n' > $(BUILD)/rext/empty.s
	qdos-as $(BUILD)/rext/empty.s -o $@

$(DIST)/vi_rext: $(BUILD)/rext/crt.o $(BUILD)/rext/empty.o | $(DIST)
	cd $(BUILD)/rext && $(abspath $(dir $(shell command -v $(CC)))/qdos-ld) -L. -L$(QDOS_LIBDIR) -o $(abspath $@) empty.o
