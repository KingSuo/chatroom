# chatroom
Kubernetes v1.7.4安装过程

前言

目录
Kubernetes v1.7.4安装过程	1
修订记录Revision record	1
1、平台版本说明	3
2、平台环境规划	3
3、环境准备（所有主机）	3
3.1 内核升级	3
3.2 关闭firewall和SELINUX	4
3.3 修改主机名	5
3.4 确保所有主机安装iptables	5
3.5 NFS安装（可选）	5
3.6 所有主机安装docker-ce	6
4、Master环境安装	6
4.1 Master上docker image准备	6
4.2 Master上安装kubeadm / kubectl / kubelet / kubernetes-cni	7
4.3 Master上Kubernetes初始化	8
4.4 配置网路	8
4.5 配置dashboard(可选)	8
4.6 集成harbor	9
5、Node环境安装	9
5.1 Node上docker image准备	9
5.2 Node上安装kubeadm / kubectl / kubelet / kubernetes-cni	10
5.3 Node上将本节点加入到maser	10


 
1、平台版本说明
•	Centos7.2 OS （内核Linux 4.4.84-1.el7.elrepo.x86_64）
•	Kubernetes V1.7.4
•	docker-ce version 17.06.0-ce
•	etcd version 3.0.17
•	kubernetes-dashboard-amd64 v1.6.3
2、平台环境规划
角色	主机名	IP	环境说明
Master	k8s-master	192.168.33.71	Kubernetes / etcd / dashboard/dns/calico
Node	K8s-node7	192.168.33.72	Kubernetes / docker
Node	K8s-node1	192.168.33.73	Kubernetes / docker

3、环境准备（所有主机）
3.1 内核升级
CentOS 7.2 升级内核支持 Docker overlay2 网络模式。原内核: 3.10.0-327.el7.x86_64
1.	修改安装源

机房192网络的源地址：
#vim /etc/yum.repos.d/ql-oa-el7.repo
[ql]
name=QL
#baseurl=http://download.fedoraproject.org/pub/epel/6/$basearch
baseurl=http://mirrors.oa.ops/ql/7/
enabled=1
gpgcheck=0
IDC10网络源地：
#vim /etc/yum.repos.d/ql-idc-el7.repo
[ql]
name=QL
#baseurl=http://download.fedoraproject.org/pub/epel/6/$basearch
baseurl=http://mirrors.wgq.ops/ql/7/
enabled=1
gpgcheck=0

#####
yum install -y vim net-tools wget


2.	安装新内核
# yum list kernel* available              //查看可安装的内核
# yum clean all ;yum -y install kernel-lt-4.4.87  
# grub2-set-default 0                  //修改内核启动顺序，0表示最新内核
# reboot               
# uname -a                         //检查当前内核 
# yum -y autoremove kernel-3.10.0 kernel-headers-3.10.0 kernel-tools-libs-3.10.0 kernel-devel-3.10.0 kernel-tools-3.10.0  //删除依赖的旧内核插件
# yum -y install kernel-lt-tools kernel-lt-headers kernel-lt-devel kernel-lt-tools-libs-devel kernel-lt-tools-libs                  //安装新的内核插件
# rpm -qa|grep kernel               //检查内核,会发现全变成了4.4.87的新内核

3.	安装依赖组件（需要用到Centos-Base.repo源）
# yum -y install compat-glibc-headers.x86_64 compat-glibc.x86_64 cpp.x86_64 gcc-c++.x86_64 gcc-gfortran.x86_64 gcc.x86_64 glibc-devel.x86_64 glibc-headers.x86_64 libgfortran.x86_64 libmpc.x86_64 libquadmath-devel.x86_64 libquadmath.x86_64 libstdc++-devel.x86_64 libtool.x86_64 mokutil.x86_64 mpfr.x86_64 systemtap-client.x86_64 systemtap-devel.x86_64   systemtap.x86_64

# yum -y  update NetworkManager.x86_64 NetworkManager-libnm.x86_64 NetworkManager-team.x86_64 NetworkManager-tui.x86_64 bash.x86_64 bind-libs-lite.x86_64 bind-license.noarch ca-certificates.noarch chkconfig.x86_64 device-mapper.x86_64 device-mapper-event.x86_64 device-mapper-event-libs.x86_64 device-mapper-libs.x86_64 dmidecode.x86_64 dracut.x86_64 dracut-config-rescue.x86_64 dracut-network.x86_64 emacs-filesystem.noarch expat.x86_64 firewalld.noarch firewalld-filesystem.noarch gawk.x86_64 grubby.x86_64 initscripts.x86_64 irqbalance.x86_64 kpartx.x86_64 krb5-libs.x86_64 libblkid.x86_64 libgcrypt.x86_64 libmount.x86_64 libnetfilter_conntrack.x86_64 libnl3.x86_64 libnl3-cli.x86_64 libpciaccess.x86_64 libuuid.x86_64 lvm2.x86_64 lvm2-libs.x86_64 microcode_ctl.x86_64 nspr.x86_64 nss.x86_64 nss-sysinit.x86_64 nss-tools.x86_64 nss-util.x86_64 ntpdate.x86_64 openscap.x86_64 openscap-scanner.x86_64 openssh.x86_64 openssh-clients.x86_64 openssh-server.x86_64 openssl.x86_64 openssl-libs.x86_64 polkit.x86_64 python-dmidecode.x86_64 python-firewall.noarch rdma.noarch scap-security-guide.noarch sos.noarch sudo.x86_64 tuned.noarch tzdata.noarch util-linux.x86_64 vim-minimal.x86_64 wpa_supplicant.x86_64


3.2 关闭firewall和SELINUX
# systemctl disable firewalld
# systemctl stop firewalld
# setenforce 0

#vim /etc/selinux/config
将SELINUX的值设置为disabled

3.3 修改主机名
不同主机hostname不同， 分别为k8s-master/k8s-node1/k8s-node2/k8s-node3/k8s-node4/k8s-storage:
由于没有外部DNS支持，需手动修改/etc/hosts，加入类似以下记录：

# hostnamectl set-hostname k8s-master-71
# vi /etc/hosts
192.168.1.123  harbor.ql.corp
192.168.33.71    k8s-master-71    k8s-master-192-168-33-71   k8s-master1
192.168.33.72    k8s-node-72    k8s-master-192-168-33-72   k8s-node1
192.168.33.73    k8s-node-73    k8s-master-192-168-33-73   k8s-node2
# reboot  //重启

3.4 确保所有主机安装iptables
# yum remove -y iptables iptables-services
# yum install -y initscripts  iproute iptables iptables-services
# systemctl enable iptables; systemctl start iptables; systemctl reload iptables; systemctl stop iptables; systemctl disable iptables; 

3.5 NFS安装（可选）
配置NFS server（本例k8s-storage-36）: 
# yum install -y nfs-utils rpcbind
# systemctl daemon-reload; systemctl enable rpcbind; systemctl restart rpcbind;systemctl enable nfs; systemctl restart nfs;
# echo "/docker/nfs    10.40.0.0/16(rw, no_root_squash,no_all_squash,sync,anonuid=501,anongid=501)" >> /etc/exports
# exportfs -av; exportfs -r

配置NFS clients（本例k8s-master / k8s-node1 / k8s-node2 / k8s-node3 / k8s-node4）: 
# yum install -y nfs-utils
# echo "k8s-storage-36:/docker/nfs /docker/nfs             nfs     defaults        0 0" >> /etc/fstab
# mkdir /docker/nfs; 
# mount -a

3.6 所有主机安装docker-ce
安装：
到k8s正式环境节点上拿一个ql.repo文件下来用，直接安装docker-ce
# yum -y install docker-ce 
# yum install -y libseccomp libtool-ltdl libcgroup container-selinux
# vim /usr/lib/systemd/system/docker.service
	ExecStart=/usr/bin/dockerd --storage-driver=overlay2 --insecure-registry=harbor.ql.corp --data-root=/docker/docker_root

# systemctl daemon-reload; systemctl restart docker

4、Master环境安装
4.1 Master上docker image准备
Docker pull:

# docker login harbor.ql.corp
# docker pull harbor.ql.corp/kubernetes/google_containers/etcd-amd64:3.0.17;
# docker pull harbor.ql.corp/kubernetes/google_containers/k8s-dns-dnsmasq-nanny-amd64:1.14.4;
# docker pull harbor.ql.corp/kubernetes/google_containers/k8s-dns-kube-dns-amd64:1.14.4;
# docker pull harbor.ql.corp/kubernetes/google_containers/k8s-dns-sidecar-amd64:1.14.4;
# docker pull harbor.ql.corp/kubernetes/google_containers/kube-apiserver-amd64:v1.7.4;
# docker pull harbor.ql.corp/kubernetes/google_containers/kube-controller-manager-amd64:v1.7.4;
# docker pull harbor.ql.corp/kubernetes/google_containers/kube-proxy-amd64:v1.7.4;
# docker pull harbor.ql.corp/kubernetes/google_containers/kube-scheduler-amd64:v1.7.4;
# docker pull harbor.ql.corp/kubernetes/google_containers/kubernetes-dashboard-amd64:v1.6.1;
# docker pull harbor.ql.corp/kubernetes/google_containers/kubernetes-dashboard-amd64:v1.6.3;
# docker pull harbor.ql.corp/kubernetes/google_containers/pause-amd64:3.0;
# docker pull  harbor.ql.corp/kubernetes/calico/cni:v1.10.0
# docker pull  harbor.ql.corp/kubernetes/calico/kube-policy-controller:v0.7.0
# docker pull  harbor.ql.corp/kubernetes/calico/node:v2.5.1
# docker pull  harbor.ql.corp/kubernetes/coreos/etcd:v3.1.10
# docker pull harbor.ql.corp/kubernetes/weaveworks/scope:1.6.3;







Docker tag:

# docker tag harbor.ql.corp/kubernetes/google_containers/etcd-amd64:3.0.17 gcr.io/google_containers/etcd-amd64:3.0.17;
# docker tag harbor.ql.corp/kubernetes/google_containers/k8s-dns-dnsmasq-nanny-amd64:1.14.4 gcr.io/google_containers/k8s-dns-dnsmasq-nanny-amd64:1.14.4;
# docker tag harbor.ql.corp/kubernetes/google_containers/k8s-dns-kube-dns-amd64:1.14.4 gcr.io/google_containers/k8s-dns-kube-dns-amd64:1.14.4;
# docker tag harbor.ql.corp/kubernetes/google_containers/k8s-dns-sidecar-amd64:1.14.4 gcr.io/google_containers/k8s-dns-sidecar-amd64:1.14.4;
# docker tag harbor.ql.corp/kubernetes/google_containers/kube-apiserver-amd64:v1.7.4 gcr.io/google_containers/kube-apiserver-amd64:v1.7.4;
# docker tag harbor.ql.corp/kubernetes/google_containers/kube-controller-manager-amd64:v1.7.4 gcr.io/google_containers/kube-controller-manager-amd64:v1.7.4;
# docker tag harbor.ql.corp/kubernetes/google_containers/kube-proxy-amd64:v1.7.4 gcr.io/google_containers/kube-proxy-amd64:v1.7.4;
# docker tag harbor.ql.corp/kubernetes/google_containers/kube-scheduler-amd64:v1.7.4 gcr.io/google_containers/kube-scheduler-amd64:v1.7.4;
# docker tag harbor.ql.corp/kubernetes/google_containers/kubernetes-dashboard-amd64:v1.6.1 gcr.io/google_containers/kubernetes-dashboard-amd64:v1.6.1;
# docker tag harbor.ql.corp/kubernetes/google_containers/kubernetes-dashboard-amd64:v1.6.3 gcr.io/google_containers/kubernetes-dashboard-amd64:v1.6.3;
# docker tag harbor.ql.corp/kubernetes/google_containers/pause-amd64:3.0 gcr.io/google_containers/pause-amd64:3.0;
# docker tag harbor.ql.corp/kubernetes/calico/cni:v1.10.0 quay.io/calico/cni:v1.10.0;
# docker tag harbor.ql.corp/kubernetes/calico/kube-policy-controller:v0.7.0 quay.io/calico/kube-policy-controller:v0.7.0;
# docker tag harbor.ql.corp/kubernetes/calico/node:v2.5.1 quay.io/calico/node:v2.5.1;
# docker tag harbor.ql.corp/kubernetes/coreos/etcd:v3.1.10 quay.io/coreos/etcd:v3.1.10;
# docker tag harbor.ql.corp/kubernetes/weaveworks/scope:1.6.3 weaveworks/scope:1.6.3;
4.2 Master上安装kubeadm / kubectl / kubelet / kubernetes-cni
# yum remove -y socat kubectl kubeadm kubelet kubernetes-cni
# yum install -y socat kubectl kubeadm kubelet kubernetes-cni
# vim /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
A.	添加环境变量
Environment="KUBELET_POD_INFRA_ARGS=--pod-infra-container-image=gcr.io/google_containers/pause-amd64:3.0"
B.	在ExecStar=/usr/bin/kubelet行尾加$KUBELET_POD_INFRA_ARGS
C.	将--cgroup-driver=systemd的替换为--cgroup-driver=cgroupfs

# systemctl daemon-reload; systemctl enable kubelet; systemctl restart kubelet
4.3 Master上Kubernetes初始化

####当多次执行了kubeadm init时需要用( kubeadm reset )####
# kubeadm init --pod-network-cidr=172.25.0.0/16 --kubernetes-version=v1.7.4 --apiserver-advertise-address=192.168.33.71 --service-cidr=10.96.0.0/16 --skip-preflight-checks
# mkdir -p $HOME/.kube
# sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
# sudo chown $(id -u):$(id -g) $HOME/.kube/config
# systemctl restart kubelet
# kubectl get nodes
kubeadm reset : 当多次执行了kubeadm init时，必须先用kubeadm reset清理后才能再次行执行init。 kubeadm init :
   
   --pod-network-cidr  //pod的地址范围
   --kubernetes-version //k8s 版本
   --apiserver-advertise-address  //监听主机，一般是master
   --service-cidr      //vip地址默认是10.96.0.0
4.4 配置网路
# wget https://docs.projectcalico.org/v2.5/getting-started/kubernetes/installation/hosted/kubeadm/1.6/calico.yaml
# vim calico.yaml
  sed -i 's/192.168.0.0/172.25.0.0/g' calico.yaml   
  文件中CALICO_IPV4POOL_CIDR默认是192.168.0.0/16，改成 kubeadm init初始化时pod的地址
# kubectl apply -f calico.yaml
# kubectl get services -n kube-system

4.5 配置dashboard(可选)
# kubectl apply –f kubernetes-dashboard.yaml [需要经见过的yaml，在NFS上，/docker/nfs/softwares/]
# kubectl get pods --all-namespaces
# kubectl get services –n kube-system

http://10.40.10.67:30080/

4.6 集成harbor
# kubectl create secret docker-registry harbor-registry --namespace=kube-system --docker-server=harbor.ql.corp --docker-username=***** --docker-password=********* --docker-email=admin@mobanker.com


--docker-username=***** --docker-password=**** //docker镜像仓库的用户名和密码，不知道的问配置管理同事。

5、Node环境安装

5.1 Node上docker image准备
# docker login harbor.ql.corp
# docker pull harbor.ql.corp/kubernetes/google_containers/kube-proxy-amd64:v1.7.4;
# docker pull harbor.ql.corp/kubernetes/google_containers/pause-amd64:3.0;
# docker pull harbor.ql.corp/kubernetes/calico/cni:v1.10.0
# docker pull harbor.ql.corp/kubernetes/calico/kube-policy-controller:v0.7.0
# docker pull harbor.ql.corp/kubernetes/calico/node:v2.5.1
# docker pull harbor.ql.corp/kubernetes/coreos/etcd:v3.1.10
-----
# docker tag harbor.ql.corp/kubernetes/google_containers/kube-proxy-amd64:v1.7.4  gcr.io/google_containers/kube-proxy-amd64:v1.7.4;
# docker tag harbor.ql.corp/kubernetes/google_containers/pause-amd64:3.0  gcr.io/google_containers/pause-amd64:3.0;
# docker tag harbor.ql.corp/kubernetes/calico/cni:v1.10.0 quay.io/calico/cni:v1.10.0; 
# docker tag harbor.ql.corp/kubernetes/calico/kube-policy-controller:v0.7.0 quay.io/calico/kube-policy-controller:v0.7.0;
# docker tag harbor.ql.corp/kubernetes/calico/node:v2.5.1 quay.io/calico/node:v2.5.1;
# docker tag harbor.ql.corp/kubernetes/coreos/etcd:v3.1.10 quay.io/coreos/etcd:v3.1.10;
5.2 Node上安装kubeadm / kubectl / kubelet / kubernets-cni
# yum install -y socat kubectl kubeadm kubelet kubernetes-cni
# vim /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
A. 添加环境变量
Environment="KUBELET_POD_INFRA_ARGS=--pod-infra-container-image=gcr.io/google_containers/pause-amd64:3.0"
B. 在ExecStar=/usr/bin/kubelet行尾加$KUBELET_POD_INFRA_ARGS
C. 将--cgroup-driver=systemd的替换为--cgroup-driver=cgroupfs
# systemctl daemon-reload; systemctl enable kubelet;  systemctl restart kubelet

5.3 Node上将本节点加入到maser
# kubeadm token list    //在master上查看token信息串
# kubeadm join --token c86999.316630198efbf872 192.168.33.71:6443 --skip-preflight-checks


##以下非必须, 仅供在Node节点查看资源
# mkdir /root/.kube; scp k8s-master:/etc/kubernetes/admin.conf /root/.kube/
# kubectl --kubeconfig /root/.kube/admin.conf get nodes
		

