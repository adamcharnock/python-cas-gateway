FROM python:alpine3.6

RUN \
    apk add -U \
        ca-certificates \
        gcc python3-dev g++ libxml2-dev libxslt-dev && \
    update-ca-certificates && \
    rm -rf /var/cache/apk/*

WORKDIR "/code"
COPY ["setup.py", "Pipfile*", "/code/"]
RUN echo 0.0 > VERSION && pip install pipenv && pipenv install --deploy --system

COPY ["python_cas_gateway", "/code/python_cas_gateway"]
RUN python setup.py develop

CMD ["cas_gateway"]
