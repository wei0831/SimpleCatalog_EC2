import sys, os
sys.path.insert (0,'/var/www/catalog_app')
os.chdir("/var/www/catalog_app")

from app import app as application
