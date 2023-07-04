import kopf
import kubernetes.client
from kubernetes.client.rest import ApiException
import util, datetime

frr_grp  = 'frrcontroller.nocsys.cn'
frr_ver  = 'v1alpha1'
frr_name = 'frrs'

name_cm_tmpl = '{}-frr-startup'

# patch k8s obj to make kopf's post_event happy
def to_dict_obj(k8s_obj):
    ret_dict = k8s_obj.to_dict()
    ret_dict['apiVersion'] = ret_dict['api_version']
    return ret_dict

@kopf.on.resume(frr_grp, frr_ver, frr_name)
@kopf.on.create(frr_grp, frr_ver, frr_name)
def create_or_resume(spec, name, body, patch, **kwargs):

    if 'availableReplicas' in body.status:
        # already processed b4, do nothing (from resume)
        return

    doc = util.get_ds_frr_yaml(spec, name)

    # make the doc the children of the cr object
    kopf.adopt(doc)

    cfg = util.create_cm_frr_cfg(spec, name_cm_tmpl.format(name), doc["metadata"]["ownerReferences"])

    # create an object by requesting the Kubernetes API.
    api = kubernetes.client.AppsV1Api()
    api_cfg = kubernetes.client.CoreV1Api()

    try:
        cm = api_cfg.create_namespaced_config_map(namespace=doc['metadata']['namespace'], body=cfg)

        ds = api.create_namespaced_daemon_set(namespace=doc['metadata']['namespace'], body=doc)

        # Update the parent's status.
        # required by crd
        patch.status["availableReplicas"] = 1

    except ApiException as e:
        print("Exception when calling k8s api: %s\n" % e)
        kopf.info(doc, reason='Error', message='Exception at create_fn')

# eq to "kubectl rollout restart ds/<ds_name> -n <namespace>"
def restart_ds(ds_name, namespace):
    now = datetime.datetime.utcnow()
    now = str(now.isoformat("T") + "Z")
    body = {
        'spec': {
            'template':{
                'metadata': {
                    'annotations': {
                        'kubectl.kubernetes.io/restartedAt': now
                    }
                }
            }
        }
    }

    v1_apps = kubernetes.client.AppsV1Api()

    try:
        ret_ds = v1_apps.patch_namespaced_daemon_set(ds_name, namespace, body, pretty='true')
    except ApiException as e:
        print("Exception when calling k8s api: %s\n" % e)

    kopf.info(to_dict_obj(ret_ds), reason='OK', message='Restart DS due to cfg is changed')

def replace_cfgmap(nspec, name, namespace):
    meta = {}
    kopf.adopt(meta)
    new_cfg = util.create_cm_frr_cfg(nspec, name_cm_tmpl.format(name), meta["metadata"]["ownerReferences"])

    v1_core = kubernetes.client.CoreV1Api()

    try:
        ret_cm = v1_core.replace_namespaced_config_map(name_cm_tmpl.format(name), namespace, body=new_cfg)
    except ApiException as e:
        print("Exception when calling k8s api: %s\n" % e)

    kopf.info(to_dict_obj(ret_cm), reason='OK', message='Apply new config')

@kopf.on.update(frr_grp, frr_ver, frr_name)
def update(name, namespace, spec, body, status, old, new, diff, **kwargs):
    # replace the cfgmap with new spec
    replace_cfgmap(new['spec'], name, namespace)

    # rollout restart the ds
    restart_ds(f"{name}-bgp-spkr", namespace)

    kopf.info(body, reason='Update', message='Restart DS due to CRO is changed')

@kopf.on.delete(frr_grp, frr_ver, frr_name)
def delete(body, meta, spec, status, **kwargs):
    pass
    # daemonset is defined as children of the cr object,
    # it is deleted with it.

@kopf.on.event(frr_grp, frr_ver, frr_name)
def event(event, **kwargs):
    pass
#    print("event")

