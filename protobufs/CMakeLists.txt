include(FindProtobuf)
find_package(Protobuf REQUIRED)

PROTOBUF_GENERATE_CPP(PROTO_SRC PROTO_HEADER rsoa-example.proto)
ADD_LIBRARY(proto ${PROTO_HEADER} ${PROTO_SRC})
