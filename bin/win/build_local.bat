@echo off
REM This may not be the safest way to perform this
pushd %~dp0\\..\\..\\
SETLOCAL
REM Use a var for consistency, still need to update .gitignore if this is changed
set docs_out=local_docs
mkdocs build --config-file local.yml --site-dir %docs_out% %*
tar.exe -a -cf %docs_out%.zip %docs_out%
ENDLOCAL
popd

