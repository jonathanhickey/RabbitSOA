FROM docker-cpp-dev-base

WORKDIR /cpp-service
COPY ./cpp-service /cpp-service
COPY ./protobufs /cpp-service/protobufs

ENV CXX=/usr/bin/x86_64-linux-gnu-g++-7
ENV CCFLAGS=--std=c++17

RUN mkdir build && \
    cd build && \
    cmake -DCMAKE_CXX_COMPILER=/usr/bin/x86_64-linux-gnu-g++-7 -DCMAKE_INSTALL_PREFIX=/usr/ .. && \
    make && \
    make install && \
    cd .. && \
    rm -rf build

CMD ["/usr/bin/cpp-service"]
