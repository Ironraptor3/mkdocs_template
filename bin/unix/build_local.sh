#!/bin/bash
cd $(dirname $0)/../.. && mkdocs build --config-file local.yml "$@"
