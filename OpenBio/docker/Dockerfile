FROM ubuntu:latest 


RUN apt-get update && apt-get install -y wget git unzip  python3.8  python3-distutils python3-apt curl build-essential python3-dev libffi-dev && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py 

RUN git clone https://github.com/kantale/OpenBio.eu.git 

WORKDIR /OpenBio.eu

RUN pip3.8 install -r requirements.txt 

WORKDIR /OpenBio.eu/OpenBio/app/static/app

RUN python3.8 get_bash_commands.py | bash 

WORKDIR /OpenBio.eu/OpenBio

RUN python3.8 manage.py migrate --run-syncdb && python3.8 manage.py makemigrations && python3.8 manage.py migrate 

EXPOSE 8200

# obc_private.py contains only DEBUG=True. 
# We need this to make all users validated. Otherwise users will not be able to create new objects.
COPY obc_private.py /OpenBio.eu/OpenBio/OpenBioC

CMD python3.8 manage.py runserver 0.0.0.0:8200  

# RUN WITH: 
# docker run -p 8200:8200  -it openbio

# For debugging.. 
# docker run -p 8200:8200  -it openbio /bin/bash  


