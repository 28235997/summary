nginx当初遇到js无法加载的问题：
解决：在http块中加入 include mime.type;

## 参数解释
* 内核参数及其含义：/etc/sysctl.conf
fs.file-max = 999999 #进程同时打开的最大句柄数，也就是最大并发连接数
net.ipv4.tcp_tw_reuse = 1 #表示允许将TIME-WAIT状态的socket重新用于新的tcp连接，这对于服务器来说很有意义，因为服务器上总会有大量TIME-WAIT状态的连接
net.ipv4.tcp_keepalive_time = 600 #发送保活探测报文的时间间隔，小一点可以清理无效连接
net.ipv4.tcp_fin_timeout = 30 #表示当服务器主动关闭连接时，socket保持在FIN-WAIT-2状态的最大时间
net.ipv4.tcp_max_tw_buckets = 5000 #

* ./sbin/nginx -c tmpnginx.conf 指定配置文件启动nginx
* ./sbin/nginx -s stop 强制停止nginx
* ./sbin/nginx -s quit 优雅停止
* ./sbin/nginx -s reload 重读配置项


## nginx的配置
### 运行中的nginx进程间关系

* 一个master，多个worker，master用于管理worker进程，master需要拥有较高的权限，用来管理worker进程，当任意一个worker crash时，master会立刻拉起一个继续服务

* 当把worker进程数设置和cpu核心数相等时，效率最高，因为进程间的切换开销最小

### 配置
[根块中配置]
#### user nobody 
设置用master启动后，fork出的worker进程运行在那个用户下 ，默认是nobody，但是使用nobody之后则无法进行写磁盘操作 
#### include /usr/share/nginx/modules/*.conf;
把其他配置文件嵌入进来
#### worker_processes auto；
定义worker进程的个数
#### worker_cpu_affinity cpumask[cpumask...]
要对worker进行绑定，如果多个worker在抢同一个cpu，那么势必会影响性能，如果都独享，才能实现完全的并发
```shell
worker_processes 4;
worker_cpu_affinity 1000 0100 0010 0001;
```
#### worker_priority 0(-20--19)
和内核分配的时间片有关，越小优先级越高，时间片越长，worker优先级配置，内核进程是5，尽量不要比内核进程还小 [建议-10] 因为它需要有极高的优先权
[event块中的配置]
#### use poll|epoll|select
选择的事件处理模型
#### worker_connections number
每个worker处理最大连接数

### error_log
设置错误日志级别和路径，一般放到单独挂载的盘，error_log /var/log/error_log info;

* [http]
#### http块的基本结构
http{
    gzip on;
    upstream {
        ...
    }
    ...
    server{
        listen localhost:80;
        location /webstatic{
            if ...
        }
        location ~* .(jpg|jpeg|png|jpe|gif)$ {

        }
    }

    server{
        ...
    }
}
[server]
* 由于ip地址数量有限，经常会多个主机域名对应同一个ip，这时就可以按照server_name并通过server块来定义虚拟主机
#### listen监听端口
listen 80;
listen localhost:8000;
listen 443 default_server ssl backlog=1024;  
* default_server将所在的server块作为默认server块，如果没有找到任何匹配，就会走这个
* backlog=1024 表示tcp中backlog队列的大小，默认为-1，表示不设置，在tcp建立三次握手时，进程还没有开始处理监听句柄，这时backlog将会放置这些新连接，如果队列已满，则后来的会建立连接失败
#### server_name
默认server_name "";
server_name www.testweb.com,download.testweb.com;
* 当处理一个http请求时，nginx会取出头中的host，与每个server中的server_name进行匹配，如果比配多个，则根据优先级，全匹配>前通配(*.test.web.com)>后通配>正则匹配(~^\.testweb\.com$)
[location]
#### location[= |~|~*|^~|@]/uri/{...} 
1. = 把uri作为字符串，做完全匹配
2. ~表示匹配URI时是字母大小写敏感
3. ~*大小写不敏感
4. ^~表示前半部分匹配即可， ^~ images 则以images开头的都会匹配
5. 正则 ~* \.(gif|jpg|jpeg)$以这三种结尾，忽略大小写

#### root path  * http，server，location，if块都可以加
默认 root html
location /download/ {
    root opt;
}
当请求时/download/index/test.html，则会返回服务器上/opt/download/index/test.html的内容
#### alias 在location块
相当于 location后面的别名 
location conf{
    alias usr/local/nginx/conf;
}
访问conf/nginx.conf时则相当于访问 /usr/local/nginx/conf/nginx.conf
#### 根据请求状态码重定向页面 * http,server,location,if都可以加
error_page code
error_page 404 404.html;
error_page 502,503,504 50x.html;

* 如果想重定向到另一个location中进行处理，则
location / {
    error_page 404 @fallback;
    location @fallback {
        proxy_pass http://backend
    }
}

### 下一节


####  mime类型的设置
types{
    text/html   html; #html扩展名映射到text/html类型
    ...
}
定义MIMEtype到文件扩展名的映射，

* types_hash_max_size 使用散列表来找type，越大内存占用越大，但搜索速度越快

* default_type        application/octet-stream; 当找不到时默认


#### 按http方法名进行限制
limit_except method...{...} [location]块中
limit_except GET{
    allow 192.168.1.0/32;
    deny all;
}
表示禁止GET方法和HEAD方法

#### HTTP请求包体的最大值
client_max_body_size size; 默认1m [http,server,location]块中
http包头会有Content-Length字段，当用户试图上传一个10GB的文件，nginx在收完包头后，发现太大，就会返回413给客户端。
#### limit_rate speed 对请求限速 [http,server,location,if]块中
默认 limit_rate 0;不限速


#### sendfile系统调用 [http,server,location]
sendfile on|off;
默认： sendfile on;
启用sendfile系统调用，减少两次内核态到用户态的内存拷贝，提高发送文件效率
#### tcp_nopush on
打开之后 将会在发送响应时把整个响应报头放在一个TCP包中发送


#### ignore_invalid_headers on|off   [http,server]块中
如果将其设置为off，那么当出现不合法的http头时，会拒绝服务 返回400，on则忽略

#### log_not_found on|off 文件未找到时是否记录error日志 [http,server,location]块中


## 反向代理
* 当一些业务比较复杂时nginx不适合处理，则将其转发到上有服务器，不会立即转发，而是将http包体完整接收到硬盘或者内存，然后像上游服务器发起连接，进行转发，(如果一个请求上传1GB文件，那么在这时间内就需要长时间和上游服务器建立连接，而nginx则不用)
优点：降低上游服务器的负载，将压力放在nginx上
缺点：会增加处理时间，增加用于缓存请求内容的内存和磁盘空间

### upstream基本配置
upstream块
upstream backend{
    server backend1.example.com;
    server backend2.example.com;
    server backend3.example.com;
}
server {
    location /{
        proxy_pass http://backend;
    }
}
#### server [upstream]块中
- weight=number:设置权重
- max_fails=number:与fail_timeout配合使用，指在fail_timeout时间段内，转发失败次数超过number，则认为当前上游服务器不可用
- fail_timeout=time：fail_timeout时间段
- down：表示该服务器永久下线，只有在[使用ip_hash时才有用]
- backup: 在使用ip_hash时配置无效
#### ip_hash [upstream]块中
有些情况下，我们希望某一个用户的请求始终落在某个机器上，则使用他。与weight不可同时使用，在某个机器不可用时，必须标记为down，不能直接删除


### 反向代理基本配置
proxy_pass基本配置
location /test/v1/ { 
 #替换 URL 的代理方式： /test/v1/ 会被替换为/abc/ 
 #如 /test/v1/xxx?a=1 到达后端就会变为 /abc/xxx?a=1 
 proxy_pass http://127.0.0.1:81/abc/; 
} 
location /aaa/ { 
 #替换 URL 的代理方式，和上面的/test/v1/功能一样，只是替换成了"/" 
 #刚开始使用代理时 常常会和下面 /abc 的代理混淆
 proxy_pass http://127.0.0.1:81/; 
} 
location /abc { 
 #什么都不会改变，直接传递原始的 URL 
 proxy_pass http://127.0.0.1:81; 
}

### upstream使用手册



### rewrite使用手册


## nginx内置变量
$arg_name 指 URL 请求中的参数，name 是参数的名字
$args 代表 URL 中所有请求的参数
$binary_remote_addr 客户端地址以二进制数据的形式出现，通常会和限速模块一起使用
$body_bytes_sent 发送给客户端的字节数，不包含响应头
$bytes_sent 发送给客户端的总字节数
$document_uri 设置$uri 的别名
$hostname 运行 Nginx 的服务器名
$http_referer 表示请求是从哪个页面链接过来的
$http_user_agent 客户端浏览器的相关信息
$remote_addr 客户端 IP 地址
$remote_port 客户端端口号
$remote_user 客户端用户名，通常在 Auth Basic 模块中使用
$request_filename 请求的文件路径，基于 root alias 指令和 URI 请求生成
$request_time 请求被 Nginx 接收后，一直到响应数据返回给客户端所用的时间
$request_uri 请求的 URI，带参数
$request 记录请求的 URL 和 HTTP 
$request_length 请求的长度，包括请求行、请求头和请求正文
$server_name 虚拟主机的 server_name 的值，通常是域名
$server_port 服务器端口号
$server_addr 服务器的 IP 地址
$request_method 请求的方式，如 POST 或 GET 
$scheme 请求协议，如 HTTP 或 HTTPS 
$sent_http_name 任意响应头，name 为响应头的名字，注意 name 要小写
$realip_remote_addr 保留原来的客户地址，在 real_ip 模块中使用
$server_protocol 请求采用的协议名称和版本号，常为 HTTP/1.0 或 HTTP/1.1 
$uri 当前请求的 URI，在请求过程中 URI 可能会被改变，例如在内部重定向或使用索引文件时
$nginx_version Nginx 的版本号
$pid worker 进程的 PID 
$pipe 如果请求是 HTTP 流水线（pipelined）发送的，pipe 值为"p"，否则为"." 
$connection_requests 当前通过一个连接获得的请求数量
$cookie_name name 即 Cookie 的名字，可得到 Cookie 的信息
$status HTTP 请求状态
$msec 日志写入时间。单位为秒，精度是毫秒
$time_local 在通用日志格式下的本地时间
$upstream_addr 请求反向代理到后端服务器的 IP 地址
$upstream_port 请求反向代理到后端服务器的端口号
$upstream_response_time 请求在后端服务器消耗的时间
$upstream_status 请求在后端服务器的 HTTP 响应状态
$geoip_city 城市名称，在 geoip 模块中使用




### 常见内置变量实战
$arg_name
```
location ／ { 
 if ($arg_at= ‘5') { 
 proxy_pass http://b; 
 } 
 proxy_pass http://a; 
}
```
* 默认到http://a,参数at=5则到b

* $uri 和$request_uri
uri是执行完一系列重定向最后到后端服务器的url(不包含$arg参数)，
request_uri 记录原始的url(包含arg参数) 不重定向，去掉参数和$uri一样

## 强化基础配置 
### 获取真实ip
一般ip会在$remote_addr中，但是一般公司生产环境会和CDN打交道，请求先到CDN代理才到nginx，所以需要安装 
--with-http_realip_module模块，

### 减少后端的网络开销
有许多请求之和url有关，和请求头和请求体无关，则可以禁用掉
- proxy_pass_request_body：确定是否向后端服务器发送 HTTP 请求体，支持配置的环境有 http、server、location。 
- proxy_pass_request_headers：确定是否向后端服务器发送 HTTP 请求头，支持的配置的环境有 http、server、location。



