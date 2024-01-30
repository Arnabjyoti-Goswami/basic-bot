# !py -3 -m venv venv # make a new venv (virtual environment in python)

# First set interpreter in vscode:
# CTRL + SHIFT + P in vscode to open the shell at the top for different options, then select Python: Select Interpreter and choose the python.exe in the venv folder
# Always check the python interpreter in vscode when reopening this project
# Then run this script, after which see that (venv) is displayed before the path in the terminal, which means that we are currently using the virtual environment

import os

activation_filename = "activate"
filepath = os.path.join(os.path.abspath(""), "venv", "Scripts", activation_filename)

import subprocess

subprocess.call(filepath, shell=True)

# To deactive the venv simply use '!deactivate'
# !pip freeze > requirements.txt # to generate list of requirements from the installed dependancies in the venv
# '!' prefix before a command means that it needs to be used in the terminal
