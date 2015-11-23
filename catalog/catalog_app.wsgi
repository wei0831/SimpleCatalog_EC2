import sys, os
sys.path.insert (0,'/var/www/catalog_app/catalog')
os.chdir("/var/www/catalog_app/catalog")

from app import app as application
