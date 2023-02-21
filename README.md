# Containerinfo

Containerinfo is a service, implemented in Python, to know what containers are running in a K8s cluster, and what their resource requests and limits are. It is able to query the resource requests and limits for all the containers of pods with labels, specified by a query parameter, from all namespaces. The results are returned as JSON and are an array of records, containing the namespace, pod name, container name and the resources for each container of the matching pods.

E.g. when calling this service from another Pod of the cluster with the command

```
curl "http://containerinfo.default.svc.cluster.local:8000/container-resources?pod-label=app.kubernetes.io%2Fcomponent%3Djenkins-master"
```

the service returns the response:

```
[
  {
    "container_name": "jenkins-master",
    "pod_name": "master-845dd22346-ke251",
    "namespace": "Platform",
    "mem_req": "4096Mi",
    "mem_limit": "8192Mi",
    "cpu_req": "100m",
    "cpu_limit" "500m"
  },
...
]
```

## Usage and Installation

This section describes how to install and use the implemented service.

A final version of the container is already build and published on Docker Hub, see https://hub.docker.com/r/choeffer/containerinfo/tags.

First, clone the repo and `cd` into it

```
[choeffer@fedora]$ git clone git@github.com:choeffer/containerinfo.git && cd containerinfo
```

From here onwards, access to a K8s cluster is mandatory. For developing, minikube was used. Setting up minikube, or any alternative, is not covered here.

After starting e.g minikube, and setting the current-context properly, install the service via the provided Helm chart.

```
[choeffer@fedora containerinfo]$ helm install containerinfo ./containerinfo --wait
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /home/choeffer/.kube/config
WARNING: Kubernetes configuration file is world-readable. This is insecure. Location: /home/choeffer/.kube/config
NAME: containerinfo
LAST DEPLOYED: Tue Feb 14 10:57:38 2023
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=containerinfo,app.kubernetes.io/instance=containerinfo" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT
```

A test is included in the Helm chart to ensure that the installation was successful.

```
[choeffer@fedora containerinfo]$ helm test containerinfo
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /home/choeffer/.kube/config
WARNING: Kubernetes configuration file is world-readable. This is insecure. Location: /home/choeffer/.kube/config
NAME: containerinfo
LAST DEPLOYED: Tue Feb 14 10:57:38 2023
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE:     containerinfo-test-connection
Last Started:   Tue Feb 14 10:58:38 2023
Last Completed: Tue Feb 14 10:58:44 2023
Phase:          Succeeded
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=containerinfo,app.kubernetes.io/instance=containerinfo" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT
```

To test the service manually and see the response, start a Pod in the cluster and open an interactive shell. Take the `NAME` and `NAMESPACE` attribute from the output to access the service.

```
[choeffer@fedora containerinfo]$ kubectl run curl --image=radial/busyboxplus:curl -i --tty
If you don't see a command prompt, try pressing enter.
[ root@curl:/ ]$ export NAME=containerinfo
[ root@curl:/ ]$ export NAMESPACE=default
[ root@curl:/ ]$ curl http://${NAME}.${NAMESPACE}.svc.cluster.local:8000/container-resources?pod-label=app.kubernetes.io/name=containerinfo
[{"container_name": "containerinfo", "pod_name": "containerinfo-65f4c767bc-hm9g2", "namespace": "default", "mem_req": null, "mem_limit": null, "cpu_req": null, "cpu_limit": null}, {"container_name": "wget", "pod_name": "containerinfo-test-connection", "namespace": "default", "mem_req": null, "mem_limit": null, "cpu_req": null, "cpu_limit": null}]
```

As shown, the service can find itself if passing the corresponding labels. Replace `app.kubernetes.io/name=containerinfo` with e.g. `component=etcd,tier=control-plane` to find the etcd Pod.

```
[ root@curl:/ ]$ curl http://${NAME}.${NAMESPACE}.svc.cluster.local:8000/container-resources?pod-label=component=etcd,tier=control-plane
[{"container_name": "etcd", "pod_name": "etcd-minikube", "namespace": "kube-system", "mem_req": "100Mi", "mem_limit": null, "cpu_req": "100m", "cpu_limit": null}]
```

To clean up, exit the interactiv shell, delete the used Pod, and uninstall the Helm chart.

```
[choeffer@fedora containerinfo]$ kubectl delete pod curl
pod "curl" deleted
[choeffer@fedora containerinfo]$ helm uninstall containerinfo --wait
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /home/choeffer/.kube/config
WARNING: Kubernetes configuration file is world-readable. This is insecure. Location: /home/choeffer/.kube/config
release "containerinfo" uninstalled
```

