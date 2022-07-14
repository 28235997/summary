
## 1
### 第一个cmake demo
#include <stdio.h>
int main()
{
printf(“Hello World from t1 Main!\n”);
return 0;
}

CmakeLists.txt 文件内容：
PROJECT (HELLO)
SET(SRC_LIST main.c)
MESSAGE(STATUS "This is BINARY dir " ${HELLO_BINARY_DIR})
MESSAGE(STATUS "This is SOURCE dir "${HELLO_SOURCE_DIR})
ADD_EXECUTABLE(hello SRC_LIST)


### project指令的用法：
PROJECT(projectname [CXX] [C] [Java])
默认支持所有语言，这句隐式定义了两个变量BINARY_DIR和 SOURCE_DIR

### ADD_SUBDIRECTORY指令
指定当前工程添加存放源文件的子目录：
ADD_SUBDIRECTORY(source_dir [binary_dir] [EXCLUDE_FROM_ALL])
[binary_dir]二进制存放目录，如果不指定 会在你当前执行cmake命令路径下生成source_dir同名目录


指定目标二进制或者共享库的最终存放位置，在哪里加？  ADD_EXECUTABLE在哪里就在那里
SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
SET(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)

指定安装路径
CMAKE_INSTALL_PREFIX变量
cmake -DCMAKE_INSTALL_PREFIX=/tmp/t2/usr ..

### INSTALL指令
1.
INSTALL(TARGETS targets...
 [[ARCHIVE|LIBRARY|RUNTIME]
 [DESTINATION <dir>]
 [PERMISSIONS permissions...]
 [CONFIGURATIONS
 [Debug|Release|...]]
 [COMPONENT <component>]
 [OPTIONAL]
 ] [...])
 TARGETS就是可执行二进制文件，动态库，静态库
2.INSTALL(FILES files... DESTINATION <dir>
 [PERMISSIONS permissions...]
 [CONFIGURATIONS [Debug|Release|...]]
 [COMPONENT <component>]
 [RENAME <name>] [OPTIONAL])
 FILES安装一般文件，并可以指定访问权限，不指定则644

## 2

### ADD_LIBRARY指令
ADD_LIBRARY(libname [SHARED|STATIC|MODULE]
 [EXCLUDE_FROM_ALL]
 source1 source2 ... sourceN)

如果需要生成名字相同的动态库和静态库，那么上述指令则无法实现，需要在使用一个新的指令
### SET_TARGET_PROPERTIES
SET_TARGET_PROPERTIES(target1 target2 ...
 PROPERTIES prop1 value1
 prop2 value2 ...)

动态库版本号
我们人仍然可以使用SET_TARGET_PROPERTIES
SET_TARGET_PROPERTIES(hello PROPERTIES VERSION 1.2 SOVERSION 1)

**小结：**
**如何通过 ADD_LIBRARY 指令构建动态库和静态库。
如何通过 SET_TARGET_PROPERTIES 同时构建同名的动态库和静态库。
如何通过 SET_TARGET_PROPERTIES 控制动态库版本
最终使用上一节谈到的 INSTALL 指令来安装头文件和动态、静态库。**

## 引用上一节的共享库和头文件
引用外部的头文件
为了能让我们的工程能够找到hello.h头文件，引入新的指令
### include_directories
INCLUDE_DIRECTORIES([AFTER|BEFORE] [SYSTEM] dir1 dir2 ...)
这条指令可以用来向工程添加多个特定的头文件搜索路径，路径之间用空格分割，如果路径
中包含了空格，可以使用双引号将它括起来，默认的行为是追加到当前的头文件搜索路径的
后面，你可以通过两种方式来进行控制搜索路径添加的方式：
１，CMAKE_INCLUDE_DIRECTORIES_BEFORE，通过 SET 这个 cmake 变量为 on，可以
 将添加的头文件搜索路径放在已有路径的前面。
 ２，通过 AFTER 或者 BEFORE 参数，也可以控制是追加还是置前。

 ### LINK_DIRECTORIES
 TARGET_LINK_LIBRARIES(target library1
 <debug | optimized> library2
 ...)
 这个指令非常简单，添加非标准的共享库搜索路径，比如，
 在工程内部同时存在共享库和可 执行二进制，在编译时就需要指定一下这些共享库的路径

 ### TARGET_LINK_LIBRARIES
 TARGET_LINK_LIBRARIES(target library1
 <debug | optimized> library2
 ...)
 该指令可以为target添加需要链接的共享库，例子中是一个可执行文件，同样可以

### add_dependencies



## 打开测试
#打开测试功能
enable_testing()
#增加单元测试
add_test(
  NAME python_test_long
  COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test.py --executable $<TARGET_FILE:sum>
  )

 ## 编写自己的cmake模块
 cmake模块目的:找到library文件，找到库文件
 主工程目录下：
#PROJECT(HELLO)
#MESSAGE( "Found Hello: ${PROJECT_SOURCE_DIR}")
SET(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)  #定义cmake模块路径，让cmake找到.cmake文件
ADD_SUBDIRECTORY(src) #找到子CMakeLists.txt

vim cmake/FindHELLO.cmake

FIND_LIBRARY(HELLO_LIBRARY NAMES hello PATH /usr/lib /usr/local/lib)
IF (HELLO_LIBRARY)
 SET(HELLO_FOUND TRUE)
ENDIF (HELLO_LIBRARY)
IF (HELLO_FOUND)
 IF (NOT HELLO_FIND_QUIETLY)
 MESSAGE(STATUS "Found Hello: ${HELLO_LIBRARY}")
 ENDIF (NOT HELLO_FIND_QUIETLY)
ELSE (HELLO_FOUND)
 IF (HELLO_FIND_REQUIRED)
 MESSAGE(FATAL_ERROR "Could not find hello library")
 ENDIF (HELLO_FIND_REQUIRED)
ENDIF (HELLO_FOUND)

vim src/CMakeLists.txt

FIND_PACKAGE(HELLO REQUIRED)   #此指令会去CMAKE_MODULE_PATH下找FindHELLO.cmake文件
IF(HELLO_FOUND)
 ADD_EXECUTABLE(hello main.c)
 INCLUDE_DIRECTORIES(${HELLO_INCLUDE_DIR})  #找头文件  就是.h文件
 TARGET_LINK_LIBRARIES(hello ${HELLO_LIBRARY}) #把libhello.so链接到hello
ENDIF(HELLO_FOUND)


### add_custom_command

* 自定义输出

```
set(wrap_BLAS_LAPACK_sources
  ${CMAKE_CURRENT_BINARY_DIR}/wrap_BLAS_LAPACK/CxxBLAS.hpp
  ${CMAKE_CURRENT_BINARY_DIR}/wrap_BLAS_LAPACK/CxxBLAS.cpp
  ${CMAKE_CURRENT_BINARY_DIR}/wrap_BLAS_LAPACK/CxxLAPACK.hpp
  ${CMAKE_CURRENT_BINARY_DIR}/wrap_BLAS_LAPACK/CxxLAPACK.cpp
  )
```
```
add_custom_command(
  OUTPUT
      ${wrap_BLAS_LAPACK_sources}     #输出内容
  COMMAND
      ${CMAKE_COMMAND} -E tar xzf ${CMAKE_CURRENT_SOURCE_DIR}/wrap_BLAS_LAPACK.tar.gz  #通过执行命令生成输出
  COMMAND
      ${CMAKE_COMMAND} -E touch ${wrap_BLAS_LAPACK_sources}
  WORKING_DIRECTORY
      ${CMAKE_CURRENT_BINARY_DIR}   #命令的执行路径
  DEPENDS
      ${CMAKE_CURRENT_SOURCE_DIR}/wrap_BLAS_LAPACK.tar.gz #命令的依赖
  COMMENT
      "Unpacking C++ wrappers for BLAS/LAPACK"
  VERBATIM
  )
```

### add_custom_target
```
add_custom_target(BLAS_LAPACK_wrappers
  WORKING_DIRECTORY
      ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS
      ${MATH_SRCS}
  COMMENT
      "Intermediate BLAS_LAPACK_wrappers target"
  VERBATIM
  )
```

### add_dependencies(linear-algebra unpack)
项目较大的时候 依赖较多，为了保证被依赖的项目在依赖项目之前构建，引入这个指令

### target_include_directories
为目标添加头文件搜索路径
target_include_directories(linear-algebra
          PRIVATE
          ${CMAKE_CURRENT_SOURCE_DIR}/eigen-3.3.4)

### target_sources
add_library(math "")  #可以声明一个没有目标的源，然后用target_source来填充源
target_sources(math
  PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/wrap_BLAS_LAPACK/CxxBLAS.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/wrap_BLAS_LAPACK/CxxLAPACK.cpp
  PUBLIC
    ${CMAKE_CURRENT_BINARY_DIR}/wrap_BLAS_LAPACK/CxxBLAS.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/wrap_BLAS_LAPACK/CxxLAPACK.hpp
  )


### configure_file
* configure_file(print_info.c.in print_info.c @ONLY)
将print_info.c.in里面以@开头和结尾的值替换成设置的变量，并生成print_info.c文件

