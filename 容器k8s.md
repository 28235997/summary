## docker
### 容器的启动原理过程
- 启用 Linux Namespace 配置；
- 设置指定的 Cgroups 参数；
- 切换进程的根目录（Change Root）

### 联合挂载(UnionFS) p8
[挂载的原理：实际上是inode的替换过程，/home挂载到/test，其实是将/test目录的dentry重定向到/home的inode，所以，更改test其实是更改/home]
也就是docker的分层原理

* 也就是说，容器可以一分为二的看待
1. 一组联合挂载的rootfs，也就是挂载在/var/lib/docker/32fdbc686/diff下面的
2. 一个由namespace和cgroup构成的隔离环境，这部分我们成为容器运行时


## k8s
k8s:网关、水平扩展、监控、备份、灾难恢复
 
### 为什么要使用pod P13
- 这样一个场景：一个组件是一个进程组，比如rsyslogd，他需要三个进程，imklog imuxsock 和他的主进程，这三个必须在同一个节点，当不使用pod，在swarm调度时，调度两个之后发现第三个资源不够，则会启动失败，而用一个pod，里面有三个continer，则直接会选资源够的节点
- 再比如一个web应用需要war和tomcat，可以用init container来copy war包，然后tomcat容器启动

* pod只是一个逻辑概念，真正处理的是namespace和cgroup，pod本质上是共享了某些资源的容器，pod的实现有个中间容器Infra容器，在Infra 创建了一个network namespace后，用户容器就可以加入到里面来，于是，
同一个pod的容器有一下特性：
1. 直接可以使用localhost通信
2. 一个pod只有一个ip就是那个networknamespace的ip
3. pod的生命周期与Infra一致，与其他容器无关

* 以上这种特性是istio实现的一个基础:
` network namespace共享，可以在sidecar容器里面修改网络配置，接管流量，而不用管业务容器`
` 解耦`

### 深入理解pod镜像 P14 P15
那些参数是pod级别的：调度、网络、存储，以及安全相关的属性，基本上是 Pod 级别的

```
apiVersion: v1
kind: Pod
...
spec:
 nodeSelector:
   disktype: ssd
```
* 这样的配置意味着pod只能被调度到disktype:ssd标签的节点上，否则调度失败
```
spec:
  hostAliases:
  - ip: "10.1.2.3"
    hostnames:
    - "foo.remote"
    - "bar.remote"
```
* HostAliases：定义了 Pod 的 hosts 文件（比如 /etc/hosts）里的内容

```spec:
  shareProcessNamespace: true
  containers:
  - name: nginx
    image: nginx
```
* shareProcessNamespace: true 意味着共享PID namespace

* 凡是 Pod 中的容器要共享宿主机的 Namespace，也一定是 Pod 级别的定义 

* ImagePullPolicy 镜像拉去策略 默认是always

 ``` containers:
  - name: lifecycle-demo-container
    image: nginx
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c", "echo Hello from the postStart handler > /usr/share/message"]
      preStop:
        exec:
          command: ["/usr/sbin/nginx","-s","quit"]
```

*  lifecycle生命周期，在容器启动之前或者之后加入一些操作，例如初始化，优雅退出等

#### pod的几种状态
1. pending 调度不成功，可能是资源，或者其他
2. unknown 意味着kubelet不能持续汇报状态给api-server，可能是master与kubelet通信问题
3. running 已经创建成功调度成功，但有可能无法提供服务，可能问题
    - 代码问题，出现500了
    - 程序死循环
    - 服务不是容器的主启动进程
    - 资源问题，进程卡死了

#### project volume
- Secret；
- ConfigMap；
- Downward API；
- ServiceAccountToken
```
spec:
  containers:
  - name: test-secret-volume
    image: busybox
    args:
    - sleep
    - "86400"
    volumeMounts:
    - name: mysql-cred
      mountPath: "/projected-volume"
      readOnly: true
volumes:
  - name: mysql-cred
    projected:
      sources:
      - secret:
          name: user
      - secret:
          name: pass
```
* 这样容器的用户名密码就以文件的形式被挂载到/projected-volume目录下，如果修改，则会自动更新，由k8s维护
#### Service Account 服务账户
[当需要在容器里装一个k8sclient，首先要搞定认证问题]
#### 探针Probe
```
spec:
  containers:
  - name: liveness
    image: busybox
    args:
    - /bin/sh
    - -c
    - touch /tmp/healthy; sleep 30; rm -rf /tmp/healthy; sleep 600
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy
      initialDelaySeconds: 5 #启动5s后开始执行
      periodSeconds: 5 #每5s执行一次
```
* 也可以使用tcp或者http探针
```
livenessProbe:
     httpGet:
       path: /healthz
       port: 8080
       httpHeaders:
       - name: X-Custom-Header
         value: Awesome
       initialDelaySeconds: 3
       periodSeconds: 3
```
```
livenessProbe:
      tcpSocket:
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 20
```

### 控制器模式 P16
k8s项目pkg/controller目录下包含所有的控制器对象，他们都采用一种通用的编排模式，即[控制循环(control-loop)]
deployment controller 会通过kubelet上报的信息，进行调谐，也就是循环检测期望状态和实际状态

### 作业副本与水平扩展
deployment控制器实际操纵的，是replicaset对象，而不是pod对象
* 在滚动更新的过程中，由deployment控制replicaset，在由replicaset通过自己的控制器replicaset controller来保证

* 查看版本历史
kubectl rollout history deployment/nginx-deployment

* 查看滚动更新的状态变化
kubectl rollout status deployment/nginx-deployment

* 设置deployment镜像
kubectl set image deployment/nginx-deployment nginx=nginx:1.91

* 回滚到上一个版本
kubectl rollout undo deployment/nginx-deployment

* 回滚到某个版本
kubectl rollout undo deployment/nginx-deployment --to-reversion=2 

- 这样更新会使每次更新都生成一个replicaset，有些多余，因此，k8s提供了多次更新只生成一个replicaset的指令

1. 先"暂停"更新，让kubectl进入暂停状态，
kubectl rollout pause deployment/nginx-deployment 
2. 在修改完成后，使用resume指令
kubectl rollout resume deployment/nginx-deployment
3. Deployment 对象有一个字段，叫作 spec.revisionHistoryLimit 控制replicaset数量

### statefulset
1. statefulSet的控制器直接管理的是pod
2. k8s通过Headless Service，为这些有编号的Pod，在DNS服务器中生成带有同样编号的DNS记录
3. StatefulSet还为每一个pod分配并创建一个同样编号的PVC


## 声明式API，CRD  P24
CRD，custom Resource Definition 
### 写一个CRD
先定义一个CRD的yaml文件，名字叫network.yaml
```

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: networks.samplecrd.k8s.io
spec:
  group: samplecrd.k8s.io
  version: v1
  names:
    kind: Network
    plural: networks
  scope: Namespaced   #定义属于namespace 类似pod对象
 
```

## PV,PVC,SC
```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs
spec:
  storageClassName: manual
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: 10.244.1.4
    path: "/"
```
定义一个PV，pvc通常由开发人员创建，或者作为statefulset模板的一部分，由statefuleset控制器创建

### storageclass
但是100个pvc就需要100个pv，那么手动创建太麻烦，于是有了 sc
手动创建pv被称为static Provisioning 静态供应
sc被称为Dynamic Provisioning动态供应
* 关键是这个字段：provisioner: ceph.rook.io/block 

### PV持久化宿主机目录的两阶段操作
1. 为虚拟机挂载远程磁盘，attach操作
2. 将远程磁盘挂载到宿主机目录的操作，mount操作



### 自定义控制器CRD
```
func main() {
	flag.Parse()

	// set up signals so we handle the first shutdown signal gracefully
	stopCh := signals.SetupSignalHandler()

	cfg, err := clientcmd.BuildConfigFromFlags(masterURL, kubeconfig)
	if err != nil {
		glog.Fatalf("Error building kubeconfig: %s", err.Error())
	}

	kubeClient, err := kubernetes.NewForConfig(cfg)
	if err != nil {
		glog.Fatalf("Error building kubernetes clientset: %s", err.Error())
	}

	networkClient, err := clientset.NewForConfig(cfg)
	if err != nil {
		glog.Fatalf("Error building example clientset: %s", err.Error())
	}

	networkInformerFactory := informers.NewSharedInformerFactory(networkClient, time.Second*30)

	controller := NewController(kubeClient, networkClient,
		networkInformerFactory.Samplecrd().V1().Networks())

	go networkInformerFactory.Start(stopCh)

	if err = controller.Run(2, stopCh); err != nil {
		glog.Fatalf("Error running controller: %s", err.Error())
	}
}

func init() {
	flag.StringVar(&kubeconfig, "kubeconfig", "", "Path to a kubeconfig. Only required if out-of-cluster.")
	flag.StringVar(&masterURL, "master", "", "The address of the Kubernetes API server. Overrides any value in kubeconfig. Only required if out-of-cluster.")
}
```
network CRD的main方法

```
func NewController(
  kubeclientset kubernetes.Interface,
  networkclientset clientset.Interface,
  networkInformer informers.NetworkInformer) *Controller {
  ...
  controller := &Controller{
    kubeclientset:    kubeclientset,
    networkclientset: networkclientset,
    networksLister:   networkInformer.Lister(),
    networksSynced:   networkInformer.Informer().HasSynced,
    workqueue:        workqueue.NewNamedRateLimitingQueue(...,  "Networks"),
    ...
  }
    networkInformer.Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
    AddFunc: controller.enqueueNetwork,
    UpdateFunc: func(old, new interface{}) {
      oldNetwork := old.(*samplecrdv1.Network)
      newNetwork := new.(*samplecrdv1.Network)
      if oldNetwork.ResourceVersion == newNetwork.ResourceVersion {
        return
      }
      controller.enqueueNetwork(new)
    },
    DeleteFunc: controller.enqueueNetworkForDelete,
 return controller
}
```

#### informer
自定义控制器的重要组件 informer，是一个带有本地缓存和索引机制的、可以注册 EventHandler 的 client，这里的EnventHandler包括delete，update，add

informer通过ListAndWatch ，获取和监视变化

手动实现一个crd

### operator
operator=CRD+controller+webhook