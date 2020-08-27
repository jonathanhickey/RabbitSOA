FROM python:3.8.5

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install unzip && \
    wget https://github.com/google/protobuf/releases/download/v3.5.0/protoc-3.5.0-linux-x86_64.zip && \
    unzip protoc-3.5.0-linux-x86_64.zip -d protoc3 && \
    mv protoc3/bin/* /usr/local/bin/ && \
    mv protoc3/include/* /usr/local/include/

COPY . .

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN protoc -I=proto --python_out=. proto/rsoa-example.proto
RUN pip install protobuf

CMD ["/bin/bash"]