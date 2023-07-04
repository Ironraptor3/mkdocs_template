#!/bin/bash

# Use a var for consistency, still need to update .gitignore if this is changed
DOCS_OUT="local_docs"
cd $(dirname $0)/../.. \
&& rm -rf $DOCS_OUT \
&& rm -rf "$DOCS_OUT.zip"
unset DOCS_OUT
