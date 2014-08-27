set DIR="winproute"
REM create a directory where we put everything
md "%DIR%"
md "%DIR%\licences"
REM generate the .exe
@echo " * Generating .exe with pyinstaller"
c:\python27\python.exe Build.py -y wxproute\wxproute.spec
REM add the .exe and its directory to the bundle
move /-y wxproute\dist\wxproute "%DIR%"
REM add the licences to the bundle
@echo " * Copying licences and FAQ"
xcopy /s /y ..\local\licences "%DIR%\licences"
copy trunk\FAQ.txt "%DIR%"
REM add sample data files
REM @echo " * Adding sample data"
REM xcopy /s /y "..\local\sample data" "%DIR%"
