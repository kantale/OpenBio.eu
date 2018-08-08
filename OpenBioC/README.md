
## How to install
Run these commands only once!

### Install Anaconda 3

```
wget https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh 

bash Anaconda3-5.2.0-Linux-x86_64.sh 

# REPLACE /home/kanterakis with the directory of your anaconda 3 installation
/home/kanterakis/anaconda3/bin/pip install --upgrade pip
/home/kanterakis/anaconda3/bin/pip install virtualenv 

```

### Create A dedicated python installation from Anaconda:
I assume that you have already cloned this repository: ```https://github.com/kantale/OpenBioC```
Go to the directory: ```OpenBioC``` of this repository.

The file ```manage.py``` should be there. 

Create a dedicated python virtualenv:

```
/home/kanterakis/anaconda3/bin/virtualenv OpenBioC_python 
```


### Start the virtualev

```
source OpenBioC_python/bin/activate
```

### Install Django 2.1.0

```
pip install Django==2.1.0
```

* Build database

```
python manage.py migrate --run-syncdb
```

* Run

Change the port if you want..

```
python manage.py runserver 0.0.0.0:8200
```

## How to Run:
Run these commands whenever you want to run/test your changes. I assume you have followed the instruction of how to install. 
Also you change the port (8200) to anything you like.


```
python manage.py runserver 0.0.0.0:8200
```

Go to  ```http://0.0.0.0:8200``` and check your awesome changes!


## How to setup from Scratch
Ignore these..

```
python manage.py startapp app
```
