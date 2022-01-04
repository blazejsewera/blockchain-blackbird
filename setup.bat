@echo off

echo "Python version should be 3.10 or higher"
mkdir -p ./venv
<<<<<<< HEAD
py -m venv ./venv
=======
python -m venv ./venv
>>>>>>> 88e9d5bc5118980dde95bc060d81a1450351f9a4

call .\venv\bin\activate.bat
& C:/Users/48795/AppData/Local/Programs/Python/python10/python.exe -m pip install -r .\requirements.txt
