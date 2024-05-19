FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt

# Install dependencies for uwsgi and other build dependencies
RUN apk add --update --no-cache --virtual .build-deps gcc libc-dev linux-headers \
    && pip install --no-cache-dir -r /requirements.txt \
    && apk del .build-deps 

RUN mkdir /app
COPY ./app /app
WORKDIR /app
COPY ./scripts /scripts
RUN chmod +x /scripts/*

# Add debugging step to list contents of /scripts directory
RUN ls -la /scripts


# TODO:  Not needed now, but leave its ok.
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user
RUN chown -R user:user /vol

RUN chmod -R 755 /vol/web

USER user

CMD ["entrypoint.sh"]