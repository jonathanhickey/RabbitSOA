cmake_minimum_required(VERSION 3.9)
project(cpp-service)

set(CMAKE_CXX_STANDARD 17)

find_package(Protobuf REQUIRED)  # sets PROTOBUF_LIBRARY
find_package(Threads REQUIRED)  # sets CMAKE_THREAD_LIBS_INIT
find_package(Boost 1.65.0 REQUIRED)
include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIR})

add_subdirectory(proto)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/proto)

include_directories(${CMAKE_SOURCE_DIR}/SimpleAmqpCient-master/src)

add_executable(cpp-service
        cpp-service.cpp
        mq.cpp
        )

message(STATUS "PROTOBUF_LIBRARY: " ${PROTOBUF_LIBRARY})

target_link_libraries(cpp-service
                      proto
                      SimpleAmqpClient
                      ${PROTOBUF_LIBRARY}
                      ${CMAKE_THREAD_LIBS_INIT}
                     )

