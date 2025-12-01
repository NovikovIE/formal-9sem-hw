cmake_minimum_required(VERSION 3.14)
project(RegexLibTests)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/heads/main.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

FetchContent_Declare(
    json
    URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz
)
FetchContent_MakeAvailable(json)

add_executable(run_tests tests.cpp)
target_link_libraries(run_tests PRIVATE GTest::gtest_main nlohmann_json::nlohmann_json)

add_executable(main main.cpp)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/test_data.json ${CMAKE_CURRENT_BINARY_DIR}/test_data.json COPYONLY)

include(GoogleTest)
gtest_discover_tests(run_tests)