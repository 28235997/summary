# 背景：
代码统计脚本用flask做成了服务
# 问题
在执行了一个统计周期之后，当在执行下一个统计周期时，如果这两个统计周期有时间重叠，则无法被统计上，以及当两个人同时执行时，两个人的数据都不全
# 调查过程
打log日志，一步步跟踪，发现获取到所有commit是正常的，但是diff全部为空，定位到在过滤commit之间出了问题，于是看到了这段代码
`` if commit.id in _G_COMMIT:
     continue
     ...
     ...
   _G_COMMIT.append(commit.id)
``
_G_COMMIT是个全局变量，当时写这段代码的初衷是想过滤掉重复的commit，防止多算。

在用其他算法解决掉多算问题之后，这段代码按理说已经没什么用了，但是没有删掉，结果给自己挖了个坑。

这个全局变量不是成员变量，也不是函数变量，是直接定义在全局，当进程被加载到内存中，这个东西是在虚拟内存中的数据段.data段，要释放只有当进程退出的时候才释放，而且逻辑是当这个list里有，则跳过，这就导致了多个用户执行，或者时间重叠的执行，会不全

补充知识：
1. 在web服务里，针对java，一个请求进来会创建一个线程，
2. 成员变量在请求进来时会被初始化，当请求返回，所创建的对象就会被回收
3. 当页面返回了数据，与程序的交互就完成了，再次请求会另创建一个线程

for root, dirs, files in os.walk('.'):
    for i in files:
        full_path = os.path.join(os.getcwd(),i)
        if tarfile.is_tarfile(full_path):
          tar_obj = tarfile.open(full_path,mode='r')
            file = tar_obj.extractfile('nginx-1.20.2/src/stream/ngx_stream_limit_conn_module.c')
            for j in file:
                print(j.strip())
