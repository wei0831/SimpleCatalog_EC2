# Simple Catalog on Amazon EC2 Ubuntu

## Sever Info
- IP: 52.24.48.10
- URL: [http://ec2-52-24-48-10.us-west-2.compute.amazonaws.com/](http://ec2-52-24-48-10.us-west-2.compute.amazonaws.com/)

## Requirements
- Python 2.7
- [Flask](http://flask.pocoo.org/)
- [Flask-SeaSurf](https://flask-seasurf.readthedocs.org/en/latest/)
- [dicttoxml](https://github.com/quandyfactory/dicttoxml)
- [SQLAlchemy](http://www.sqlalchemy.org/)
- [Oauth2client](https://github.com/google/oauth2client)
- [Apache2](https://httpd.apache.org/)
- [mod_wsgi](https://code.google.com/p/modwsgi/)

## To Run
Connect to server
```
ssh -i ~/.ssh/udacity_key.rsa root@52.24.48.10
```

Create new user : grader
```
sudo adduser grader
```

Add user grader to sudoers
```
sudo vi /etc/sudoers.d/grader

# Add the following in the document
grader ALL=(ALL) NOPASSWD:ALL
# Save by entering :wq command
```

Add public key to the grader
```
# Change user to grader
su - grader

# Update authorized_keys
mkdir ~/.ssh
touch ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 644 ~/.ssh/authorized_keys
vi ~/.ssh/authorized_keys

# Generate Key at local
ssh-keygen your_key

# copy and paste your public key into the document "authorized_keys"
cat ~/.ssh/your_key.pub
```

Check if the user is successfully configured
```
ssh -i ~/.ssh/your_key grader@52.24.48.10
```

Change SSH port from 22 to 2200
```
sudo vi /etc/ssh/sshd_config
# Save by entering :wq command
# Restart ssh
service ssh restart
# Later on you need to use the following to ssh
ssh -i ~/.ssh/udacity_key.rsa root@52.24.48.10 -p 2200
```

Config UFW (firewall)
```
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH PORT
sudo ufw allow 2200
# HTTP PORT
sudo ufw allow 80
# NTP PORT
sudo ufw allow 123

sudo ufw enable
```

Config Local timezone to UTC
```
sudo dpkg-reconfigure tzdata
# Select None of the above / UTC
```

Update Packages
```
sudo apt-get update
sudo apt-get upgrade
```

Install Packages
```
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo apt-get install git
sudo apt-get install python-flask python-sqlalchemy
sudo apt-get install python-pip
```

Install python Packages
```
pip install oauth2client
pip install flask-httpauth
pip install flask-seasurf
pip install dicttoxml
```

Download the project to server
```
cd /var/www/
git clone https://github.com/wei0831/catalog_app.git
```

Create a user to manage the app
```
sudo adduser catalog-app
```

Change ownership of the project
```
cd /var/www/
chown -R catalog_app. catalog_app
chmod 600 catalog_app/catalog/catalog.db
```

Set up apache config
```
cd catalog_app
sudo cp catalog_app.conf /etc/apache2/sites-available/catalog-app.conf

sudo a2dissite 000-default.conf
sudo a2ensite catalog-app.conf
service apache2 reload
```

Do database initialize once
```
cd /var/www/catalog_app/catalog
python database_init.py
```

Now, go to [http://ec2-52-24-48-10.us-west-2.compute.amazonaws.com/](http://ec2-52-24-48-10.us-west-2.compute.amazonaws.com/)  
Everything should be all set up correctly.


## Optional (If postgresql was used for the app)

Install PostgreSQL and python adapter
```
sudo apt-get install postgresql python-psycopg2
```

Conncect to postgresql
```
sudo -u postgres psql
```

Create new Role
```
CREATE USER catalog_app;
```

Create new database and assign the owner
```
CREATE DATABASE catalog OWNER catalog_app;
```

Check
```
# List all the roles
\due
# List all the database
\list
# exit
\q

# Change user and see if the user can access the database
su - catalog_app
psql -d catalog
```

## Optional - Tools

##### [Glances](https://pypi.python.org/pypi/Glances) - A cross-platform curses-based monitoring tool
```
sudo apt-get install glances
```

##### Add auto update to cron weekly
```
sudo cp /var/www/catalog_app/autoupdate /etc/cron.weekly/autoupdate
```

#### Tiger - Audit system security
```
sudo apt-get install tiger
sudo tiger
```

## Resources
- Manage User Accounts on Instance on Amazon EC2  
[http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/managing-users.html#edit_auth_keys](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/managing-users.html#edit_auth_keys)

- Timezone Change  
[https://wiki.debian.org/TimeZoneChanges](https://wiki.debian.org/TimeZoneChanges)

- Guild for set up mod_wsgi(Apache) with Flask  
[http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/](http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/)

- Details about Apache2 Config File  
[https://httpd.apache.org/docs/2.2/configuring.html](https://httpd.apache.org/docs/2.2/configuring.html)

- Postgres Related  
[http://www.postgresql.org/docs/9.3/static/admin.html](http://www.postgresql.org/docs/9.3/static/admin.html)  
[http://www.postgresql.org/docs/9.3/static/reference.html](http://www.postgresql.org/docs/9.3/static/reference.html)

- Ubuntu autoupdate  
[https://help.ubuntu.com/community/AutoWeeklyUpdateHowTo](https://help.ubuntu.com/community/AutoWeeklyUpdateHowTo)
