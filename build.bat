py -3.12 -m PyInstaller gcft.spec
if %errorlevel% neq 0 exit /b %errorlevel%
py -3.12 build.py
if %errorlevel% neq 0 exit /b %errorlevel%
