#! /usr/bin/python3.6

from catalog import app as application
import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/ubuntu/item-catalog/')
application.secret_key = 'secretkey'
