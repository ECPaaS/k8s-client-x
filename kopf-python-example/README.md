# Development

### 1. build docker image for operator
```
  make build
```

### 2. edit deploy/helm/values.yaml
 - set dev.enabled to true
```
dev:
  enabled: true
```

### 3. install pod of operator
```
  kubectl create namespace <name-space>
  helm install <release-name> deploy/helm/ --set workdir=${PWD} -n <name-space>
```

When dev.enabled is true, ${PWD} will be mounted to /src of pod,  
and you can modify/debug the operator easily.

### 4. enter pod's shell
```
  kubectl exec -it <pod-name> -n <name-space> -- bash
```

### 5. execute operator in the pod
```
  cd /src

  kopf run controller/handler.py
  or
  kopf run --all-namespaces controller/handler.py
  or 
  kopf run -A controller/handler.py --verbose
```

### 6. create cro
```
  kubectl apply -f deploy/dev/obj.yaml
```

### 7. delete cro
```
  kubectl delete -f deploy/dev/obj.yaml
```

### 8. remove pod of operator
```
  helm uninstall <release-name> -n <name-space>
```

You can modify the source code, and test the behavior by create/delete cro.  
After the development is done, you can remove the pod.

### 9. run test

  * a) enter pod's shell as step 4.
  * b) copy kubectl into pod's /usr/local/bin/
  * c) cd /src
  * d) python3 -m unintest tests/test_oper.py

