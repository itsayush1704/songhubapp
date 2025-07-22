#!/usr/bin/python3.10

"""
WSGI configuration for SongHub application on PythonAnywhere.

This file contains the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://help.pythonanywhere.com/pages/Flask/
"""

import sys
import os

# Add your project directory to the sys.path
# Replace 'yourusername' with your actual PythonAnywhere username
project_home = '/home/chatgptnci/songhub'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set up virtual environment
venv_path = '/home/chatgptnci/songhub/venv'
activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Change working directory to project directory
os.chdir(project_home)

# Import your Flask application
from app import app as application

# Optional: Set up logging for debugging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('/home/chatgptnci/songhub/app.log'),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    application.run()