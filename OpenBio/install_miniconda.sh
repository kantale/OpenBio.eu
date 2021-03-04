

MINICONDA_LOCAL=~/miniconda.sh
CONDA_LOCATION=$HOME/miniconda

(conda -V > /dev/null && echo  "conda is installed") || (echo "conda is not installed" && \
  (which wget >/dev/null || (echo "could not find wget" && exit 1)) && \
  (test -f ${MINICONDA_LOCAL}  && echo "${MINICONDA_LOCAL} exists..") || (\
        echo "Downloading ${MINICONDA_LOCAL}" && \
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ${MINICONDA_LOCAL} && \
        bash ${MINICONDA_LOCAL} -b -p ${CONDA_LOCATION}
        ${CONDA_LOCATION}/bin/conda init bash
        source ~/.bashrc
  )
)

