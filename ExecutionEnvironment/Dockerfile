#Using ENTRYPOINT

 FROM ubuntu:latest

RUN  apt-get update \
  && apt-get install unzip \ 
  && apt-get install -y wget

ADD bashfile.sh /root/ 

RUN chmod +x /root/bashfile.sh  

ENTRYPOINT ["/root/bashfile.sh"]

CMD ["sh","/bashfile.sh"]

#Using CMD


#FROM ubuntu:latest
#RUN  apt-get update \
#  && apt-get install unzip \ 
#  && apt-get install -y wget

#ADD bashfile.sh /root/ 


#RUN cd /root; chmod +x bashfile.sh ; /bin/bash bashfile.sh



