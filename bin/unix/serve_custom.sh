#!/bin/bash
cd $(dirname $0)/../.. && mkdocs serve --config-file custom.yml "$@"
