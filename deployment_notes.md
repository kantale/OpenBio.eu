
# Deployment notes
These are some rough notes on how to deploy openbio.eu on a server. Hopefully we will create a Dockerfile out of this. 

Current system info:
```
# lsb_release -a
Distributor ID:	Ubuntu
Description:	Ubuntu 16.04.5 LTS
Release:	16.04
Codename:	xenial

# uname -a
Linux ____ 4.4.0-131-generic ____ x86_64 x86_64 x86_64 GNU/Linux
```


### Install Linux packages
``` 
sudo apt-get update
sudo apt-get install unzip apache2 apache2-dev gcc libpq-dev postgresql postgresql-contrib
```

### Install Anaconda
```
wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh 
bash Anaconda3-2019.03-Linux-x86_64.sh 
```

Answer no to the following question:
```
Do you wish the installer to initialize Anaconda3
by running conda init? [yes|no]
>>> no
```

Create a conda environment
```
source /home/akanterakis/anaconda3/bin/activate
conda create --name obc_production_python python==3.7.3
conda activate obc_production_python
```

### Configure PostgreSQL
Following directions from: https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04
```
sudo su - postgres
psql
CREATE DATABASE obc_prod;
CREATE USER obc_prod_user WITH PASSWORD 'YOUR_SECRET_POSTGRESQL_PASSWORD';
ALTER ROLE obc_prod_user SET client_encoding TO 'utf8';
ALTER ROLE obc_prod_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE obc_prod_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE obc_prod TO obc_prod_user;
\q
logout
```

### Install python packages for openbio.eu
(Make sure that the conda obc_prod_python environment is activated)
```
pip install Django==2.1.5 simplejson pybtex mistune requests ansi2html  
pip install psycopg2 # If we want to run on postgresql
pip install bashlex # https://github.com/idank/bashlex , python bash parser 
pip install mistune # Markdown parser 
pip install djangorestframework
```

### Clone and configure openbio.eu
```
cd ~
git clone https://github.com/kantale/OpenBioC  obc_production
cd ~/obc_production/OpenBioC
python manage.py makemigrations app 
python manage.py migrate 
python manage.py migrate admin


# Download javascript and css libraries
cd ~/obc_production/OpenBioC/app/static/app
python get_bash_commands.py | bash
```

Create a file in ~obc_production/OpenBioC/OpenBioC/obc_private.py
With the following content (change these according to your setup):
```python
ALLOWED_HOSTS = ['88.198.44.28', 'www.openbio.eu', 'openbio.eu']

SECRET_KEY = 'YOUR_SECRET_DJANGO_KEY'

POSTGRESQL_PARAMS = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'obc_prod',
        'USER': 'obc_prod_user',
        'PASSWORD': 'YOUR_SECRET_POSTGRESQL_PASSWORD',
        'HOST': 'localhost',
        'PORT': '',
}
```
**DO NOT STAGE THIS FILE IN GIT!**

### Configure Apache2
#### Compile mod_wsgi
```
mkdir ~mod_wsgi
cd ~mod_wsgi/
wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.6.5.tar.gz
tar zxvf 4.6.5.tar.gz 
cd mod_wsgi-4.6.5
# MAKE SURE obc_production environment is activated
./configure --with-python=/home/akanterakis/anaconda3/envs/obc_production_python/bin/python
make
sudo make install
```

#### Add mod_wsgi libraries to LD_CONFIG
```
sudo echo "/home/akanterakis/anaconda3/envs/obc_production_python/lib" > /etc/ld.so.conf.d/obc_production_python.conf
sudo ldconfig
```


#### Setup Apache2
This is an example of a virtual host configuration for apache2.
Create a file in /etc/apache2/sites-available/obc-prod-ssl.conf with the following content:

```
<VirtualHost *:80>
   ServerName www.openbio.eu

   Redirect permanent / https://www.openbio.eu/
</VirtualHost>

<VirtualHost *:443>

    ServerAdmin webmaster@openbio.eu
    ServerName www.openbio.eu
    ServerAlias openbio.eu

    Alias /static/app /home/akanterakis/obc_production/OpenBioC/app/static/app
    <Directory /home/akanterakis/obc_production/OpenBioC/app/static/>
        Require all granted
    </Directory>

    Alias /static/static /home/akanterakis/obc_production/OpenBioC/static/static/static
    <Directory /home/akanterakis/obc_production/OpenBioC/static/static/static/static/>
        Require all granted
    </Directory>

    <Directory /home/akanterakis/obc_production/OpenBioC/OpenBioC>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    WSGIDaemonProcess obc python-path=/home/akanterakis/obc_production/OpenBioC python-home=/home/akanterakis/anaconda3/envs/obc_production_python/
    WSGIProcessGroup obc
    WSGIApplicationGroup %{GLOBAL}
    WSGIScriptAlias / /home/akanterakis/obc_production/OpenBioC/OpenBioC/wsgi.py


    SSLEngine on
    SSLCertificateFile <LOCATION TO YOUR CRT FILE>
    SSLCertificateKeyFile <LOCATTION TO YOUR KEY>

    LogFormat "%a %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
    ErrorLog ${APACHE_LOG_DIR}/sslerror.log
    CustomLog ${APACHE_LOG_DIR}/sslaccess.log combined


</VirtualHost>
```

* Note: the ```WSGIApplicationGroup %{GLOBAL}``` part is for [this issue](https://code.djangoproject.com/ticket/29293)

#### Start Apache2
```
sudo a2ensite obc-prod-ssl.conf
sudo service apache2 reload
```



