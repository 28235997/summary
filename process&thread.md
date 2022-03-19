## 进程
- 当一个程序被装载到内存中，就被称作一个进程
- 当多进程并发执行，时间片轮转，单核的CPU每个时间点只能运行一个进程
- 进程三种状态 运行，就绪，
  阻塞，进程为等待事件而阻塞，比如IO，此时获得CPU执行权也无法执行
- 在虚拟内存管理的操作系统中，通常会把阻塞状态的进程物理空间移到磁盘(页换出)

### 进程的控制
- 进程控制块PCB，是进程存在的唯一标识

上下文切换：把上一个进程的CPU寄存器和程序计数器保存起来，然后切换到下一个进程

### 进程上下文切换包含
用户空间：虚拟内存，栈，全局变量
内核空间：内核堆栈，寄存器



## 线程
线程的出现解决进程执行代码时 ，假如有io读取，导致阻塞

同一进程的线程共享代码段，数据段，打开的文件等资源，虚拟内存，全局变量
每个线程有自己独立的寄存器和栈


### 线程的三种实现
用户线程：由用户管理的线程
1. 由用户级线程库函数来管理，os不参与
优点：
理论可以开无数个
速度快，因为不需要用户态与内核态切换
缺点：
一个阻塞导致整个进程阻塞
用户态线程没法打断正在运行的线程，只有内核态线程才有，但是用户态不受os管理
内核线程：由内核管理的线程
轻量级线程