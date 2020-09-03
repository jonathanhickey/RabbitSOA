FROM python:3.8.5

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install unzip && \
    wget https://github.com/google/protobuf/releases/download/v3.5.0/protoc-3.5.0-linux-x86_64.zip && \
    unzip protoc-3.5.0-linux-x86_64.zip -d protoc3 && \
    rm protoc-3.5.0-linux-x86_64.zip && \
    mv protoc3/bin/* /usr/local/bin/ && \
    mv protoc3/include/* /usr/local/include/

COPY ./rmq-console/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /rmq-console
COPY ./rmq-console /rmq-console
COPY ./protobufs /rmq-console/protobufs

RUN protoc --proto_path=protobufs --python_out=protobufs protobufs/rsoa-example.proto
RUN pip install protobuf

CMD ["/bin/bash"]