# Simple Catalog on Amazon EC2 Ubuntu

## To Run
Connect to Server
```
ssh -i ~/.ssh/udacity_key.rsa root@52.24.48.10
```

Create New User in the server machine
```
sudo adduser grader
```

Add User grader to sudoers
```
sudo vi /etc/sudoers.d/grader

# Add the following in the document
grader ALL=(ALL) NOPASSWD:ALL
# Save by entering :wq command
```

Add public key we generated earlier to the grader's authorized keys
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

# copy and paste your public key into the document
cat ~/.ssh/your_key.pub
```

Change SSH port from 22 to 2200
```
sudo vi /etc/ssh/sshd_config
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

Set up apache config
```
cd catalog_app
sudo cp catalog_app.conf /etc/apache2/sites-available/catalog-app.conf
sudo a2dissite 000-default.conf
sudo a2ensite catalog-app.conf
service apache2 reload
```

Change ownership of the project folder
```
cd /var/www/
chown -R catalog_app. catalog_app
chmod 600 catalog_app/catalog/catalog.db
```

Now, go to [http://ec2-52-24-48-10.us-west-2.compute.amazonaws.com/](http://ec2-52-24-48-10.us-west-2.compute.amazonaws.com/)  
Everything should be all set up correctly.
