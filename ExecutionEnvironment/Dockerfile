#Using ENTRYPOINT

# FROM ubuntu:latest

# RUN  apt-get update \
#  && apt-get install unzip \ 
#  && apt-get install -y wget

# ADD bashscript.sh /root/ 

# RUN chmod +x /root/bashscript.sh  

# ENTRYPOINT ["/root/bashscript.sh"]



#Using CMD

FROM ubuntu:latest

RUN  apt-get update \
  && apt-get install unzip \ 
  && apt-get install -y wget

ADD bashscript.sh /root/ 


RUN cd /root; chmod +x bashfile.sh ; /bin/bash bashscript.sh



