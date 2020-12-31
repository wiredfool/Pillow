from gcr.io/oss-fuzz/pillow:_base

COPY ./current.tgz /tmp
RUN (rm -r $SRC/Pillow/* || true) &&  tar -C $SRC/Pillow --strip-components=1 -xvzf /tmp/current.tgz \
    && cp $SRC/Pillow/depends/local-fuzz/fuzz*.py $SRC/Pillow
