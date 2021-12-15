set root=C:\ProgramData\Anaconda3
set tarpath=%cd%
call %root%\Scripts\activate.bat %root%
call conda activate colab
cd %tarpath%
python server.py
pause