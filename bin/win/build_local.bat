@ECHO OFF
REM This may not be the safest way to perform this
PUSHD %~DP0\\..\\..\\
SETLOCAL
REM Use a var for consistency, still need to update .gitignore if this is changed
set DOCS_OUT=local_docs
mkdocs build --config-file local.yml --site-dir %DOCS_OUT% %*
tar.exe -a -cf %DOCS_OUT%.zip %DOCS_OUT%
ENDLOCAL
POPD
