cmake_minimum_required(VERSION 3.12)
project(myapp VERSION 1.0.0 LANGUAGES CXX)

add_executable(myapp main.cpp)

enable_testing()
add_test(NAME run_myapp COMMAND myapp)
