FROM ubuntu:22.04

RUN : \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install \
        -qq -y --no-install-recommends \
        python3.10 \
        sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && :

RUN groupadd smi

CMD ["sleep", "infinity"]
