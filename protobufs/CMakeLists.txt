include(FindProtobuf)
find_package(Protobuf REQUIRED)
INCLUDE_DIRECTORIES(${PROTOBUF_INCLUDE_DIR})
PROTOBUF_GENERATE_CPP(PROTO_SRC PROTO_HEADER
        rsoa-example.proto
        cpp-service.proto)
ADD_LIBRARY(protobufs ${PROTO_HEADER} ${PROTO_SRC})
