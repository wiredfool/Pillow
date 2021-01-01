from gcr.io/oss-fuzz/pillow:_base

COPY ./current.tgz /tmp
RUN tar -C $SRC/Pillow --strip-components=1 -xzf /tmp/current.tgz && rm /tmp/current.tgz
