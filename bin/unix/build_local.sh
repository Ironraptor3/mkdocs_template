#!/bin/bash

# Use a var for consistency, still need to update .gitignore if this is changed
DOCS_OUT="local_docs"
cd $(dirname $0)/../.. && mkdocs build --config-file local.yml --site-dir $(DOCS_OUT) "$@" && zip "$(DOCS_OUT).zip" $(DOCS_OUT)
unset DOCS_OUT
