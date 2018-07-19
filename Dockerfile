FROM ubuntu:16.04

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y build-essential git python2.7 python-pip ruby

# Install CRF++.
RUN git clone https://github.com/mtlynch/crfpp.git && \
    cd crfpp && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    cd ..

# Install ingredient-phrase-tagger.
RUN git clone https://github.com/NYTimes/ingredient-phrase-tagger && \
    cd ingredient-phrase-tagger && \
    python setup.py install

WORKDIR /ingredient-phrase-tagger
