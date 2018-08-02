
### Install 
* Create a dedicated "arkalos" python: (Assuming anaconda3 is installed)

```
/home/kantale/anaconda3/bin/virtualenv arkalos_python
```

* Activate local python

```
source arkalos_python/bin/activate
```


* Install Django, simplejson, pybtex

```
arkalos_python/bin/pip install simplejson
arkalos_python/bin/pip install pybtex
arkalos_python/bin/pip install Django==1.10.5
```

* Copy files from open repo: https://github.com/kantale/arkalos (do not need to do anything. this repo already contains these files).
   * Go to: cd app/static/app/
   * Run:

```
wget -O arkalos_static.tgz  "https://www.dropbox.com/s/4irt4f5bpn48p22/arkalos_static.tgz?dl=1"
tar zxvf arkalos_static.tgz
```

* Build database

```
python manage.py migrate --run-syncdb 
```

* Run:

```
python manage.py runserver 0.0.0.0:8100
```


* Testing

```
http://139.91.75.205:8100/?token=A71B27C1919C
```

