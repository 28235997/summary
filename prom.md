## prometheus metrics的集中类型
1. Gauges：只有一个简单的返回值，叫瞬时状态


2. counter类型
持续增长的数值

3. Histogram类型
随机变化的数值

## promtheus 的两种获取数据方式
1. pull 一般表现为exporter，exporter装在被监控服务器
2. push 一般表现为pushgateway，可装在任意机器 被监控服务器开发小脚本，pushgateway推到prom server


查看内存
node_memory_MemFree_bytes


cpu使用率的定义：CPU各种状态中除了idle(空闲)这个状态外，其他所有的CPU状态累加/总cpu时间



### 常用函数
* increase()
在prom中，是用来针对Counter这种持续增长的数值，截取其中一段时间的增量
increase(node_cpu[1m]) => 这样就获取了cpu总使用时间在一分钟内的增量

* sum()
默认状况下是把所有数据不管什么内容全部进行家合
sum(increase(node_cpu[1m])) =》 可以计算出多个核的使用情况


* rate()
是专门配合counter类型数据的函数，平均每秒的增量


rate()和increase()函数区别： 
increase取得是一分钟内的增量总量
rate是一分钟内的增量除以60秒每秒数量

* topk()
取最大值，使用方法
topk(3,rate(node_network_receive_bytes_total[20m]))
20分钟 网卡收到网络包的最大值top3

* count()
把数值符合条件的输出数目进行加合


### 统计CPU使用率
* (1-((sum(increase(node_cpu_seconds_total{mode="idle"}[1m])) by (instance))/(sum(increase(node_cpu_seconds_total[1m])) by (instance)))) * 100
* (sum(increase(node_cpu_seconds_total{mode="iowait"}[1m])) by (increase)) /(sum(increase(node_cpu_seconds_total[1m])) by (increase)) *100


拆分此公式：
increase(node_cpu_seconds_total{mode="idle"}[1m]) {}代表过滤出空闲，[1m]代表一分钟内的增量
sum默认状况下是把所有数据不管什么内容全部进行加合，不光把一台机器多个核加合，还把所有机器CPU全都加到一起了，变成服务器集群总CPU平均值

### 统计内存使用率
可用内存计算方法：free+buffer+cache
(1-((node_memory_MemFree_bytes + node_memory_Buffers_bytes + node_memory_Cached_bytes) / node_memory_MemTotal_bytes)) *100

### count_netstat_wait_connections 
!node_exporter (TCP wait_connect数)  tcp连接等待的数

CPU是counter类型的数据，持续增长类型的，
而这里是gageage类型的数据，比CPU类型的数据容易使用，不用加过多函数

### 统计磁盘
((rate(node_disk_read_bytes_total[1m]) + rate(node_disk_written_bytes_total[1m]))/1024/1024)>0

### 统计网络传输
rate(node_network_transimit_bytes[1m]) /1024/1024

### 文件描述符
(node_filefd_allocated / node_filefd_maximum)*100

## pushgateway
安装：github中下载安装

### ⽤于抓取 TCP waiting_connection 瞬时数量
#!/bin/bash
instance_name=`hostname -f | cut -d'.' -f1` #本机机器名 变量⽤于之后的 标签
if [ $instance_name == "localhost" ];then # 要求机器名 不能是localhost 不然标签就没有区分了
echo "Must FQDN hostname"
exit 1
fi
#For waitting connections
label="count_netstat_wait_connections" # 定⼀个新的 key
count_netstat_wait_connections=`netstat -an | grep -i wait | wc -l`
#定义⼀个新的数值 netstat中 wait 的数量
echo "$label : $count_netstat_wait_connections"
echo "$label $count_netstat_wait_connections"  | curl --data-binary @- http://prometheus.server.com:9091/metrics/job/
pushgateway1/instance/$instance_name


promserver端关于pushgateway的配置
- job_name: 'pushgateway'
  static_configs:
    - targets: ['localhost:9091', 'localhost:9092']