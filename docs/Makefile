# Makefile for Sphinx documentation

# You can set these variables from the command line.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
LANGUAGES     = en it
SPHINXINTL    = sphinx-intl
GETTEXT       = $(SPHINXBUILD) -b gettext
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH.)
endif

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "\nAdditional targets:"
	@echo "  livehtml    to make standalone HTML files and serve them on localhost:8000"
	@echo "  gettext     to make PO message catalogs"
	@echo "  updatepo    to update PO message catalogs"
	@echo "  compilepo   to compile PO message catalogs to MO files"

.PHONY: help Makefile

# Build all languages
all: html

# Build and serve the documentation with live-reload
livehtml:
	sphinx-autobuild -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html

# Generate gettext style message catalogs for translations
gettext:
	$(SPHINXBUILD) -b gettext $(I18NSPHINXOPTS) $(BUILDDIR)/locale
	@echo
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/locale."

# Update the message catalogs
updatepo: gettext
	$(SPHINXINTL) update -p $(BUILDDIR)/locale -l it -d locale/


# Compile the message catalogs
compilepo:
	$(SPHINXINTL) build --locale-dir locale

# Build the documentation in all languages
multilang: compilepo
	@for lang in $(LANGUAGES); do \
		$(MAKE) -e SPHINXOPTS="-D language=$$lang" html; \
		echo "Build finished for language: $$lang"; \
	done

# Clean all build files
clean:
	rm -rf $(BUILDDIR)/*
	rm -rf locale/it/LC_MESSAGES/*.mo

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
