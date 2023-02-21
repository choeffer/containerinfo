from kubernetes import client, config
import json
from flask import Flask, request

app = Flask(__name__)

@app.route("/container-resources")
def getcontainers():
    labels = request.args['pod-label']

    # https://github.com/kubernetes-client/python/blob/master/examples/in_cluster_config.py
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False,label_selector=labels)

    # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodList.md returned Python object
    containers = list()
    for i in ret.items:
        for j in i.spec.containers:
            item = dict()
            item['container_name'] = j.name
            item['pod_name'] = i.metadata.name
            item['namespace'] = i.metadata.namespace
            try:
                item['mem_req'] = j.resources.requests['memory']
            except:
                item['mem_req'] = None
            try:
                item['mem_limit'] = j.resources.limits['memory']
            except:
                item['mem_limit'] = None
            try:
                item['cpu_req'] = j.resources.requests['cpu']
            except:
                item['cpu_req'] = None
            try:
                item['cpu_limit'] = j.resources.limits['cpu']
            except:
                item['cpu_limit'] = None
            containers.append(item)

    return json.dumps(containers)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
