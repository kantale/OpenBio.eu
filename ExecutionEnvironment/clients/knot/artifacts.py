import logging
import argparse
import base64
import yaml

import kubernetes.client
import kubernetes.config
import kubernetes.stream

from urllib.parse import urlparse


class KubernetesClient(object):
    def __init__(self):
        self._config_loaded = False
        self._core_client = None

    def _load_config(self):
        if self._config_loaded:
            return
        try:
            kubernetes.config.load_kube_config()
        except:
            kubernetes.config.load_incluster_config()
        self._config_loaded = True

    @property
    def core_client(self):
        if not self._core_client:
            self._load_config()
            self._core_client = kubernetes.client.CoreV1Api()
        return self._core_client

    def list_config_maps(self, namespace='default', label_selector=None):
        return self.core_client.list_namespaced_config_map(namespace=namespace, label_selector=label_selector).items

    def list_secrets(self, namespace='default', label_selector=None):
        return self.core_client.list_namespaced_secret(namespace=namespace, label_selector=label_selector).items

    def create_config_map(self, name, data, labels={}, annotations={}, namespace='default'):
        metadata = kubernetes.client.V1ObjectMeta(name=name, labels=labels, annotations=annotations, namespace=namespace)
        body = kubernetes.client.V1ConfigMap(api_version='v1', kind='ConfigMap', metadata=metadata, data=data)
        self.core_client.create_namespaced_config_map(namespace=namespace, body=body)

    def create_secret(self, name, data, labels={}, annotations={}, namespace='default'):
        metadata = kubernetes.client.V1ObjectMeta(name=name, labels=labels, annotations=annotations, namespace=namespace)
        body = kubernetes.client.V1Secret(api_version='v1', kind='Secret', metadata=metadata, data=data)
        self.core_client.create_namespaced_secret(namespace=namespace, body=body)

    def delete_config_map(self, name, namespace='default'):
        self.core_client.delete_namespaced_config_map(name, namespace=namespace)

    def delete_secret(self, name, namespace='default'):
        self.core_client.delete_namespaced_secret(name, namespace=namespace)

def setup_secret(kubernetes_client, artifacts_url, namespace):
    s3_access_key = base64.b64encode(artifacts_url.username.encode()).decode()
    s3_secret_key = base64.b64encode(artifacts_url.password.encode()).decode()

    secrets = kubernetes_client.list_secrets(namespace=namespace, label_selector='app.kubernetes.io/managed-by=openbio')
    existing_secret = next((s for s in secrets if s.metadata.name == 'openbio-artifact-repository'), None)
    try:
        if (existing_secret and
            existing_secret.data['accesskey'] == s3_access_key and
            existing_secret.data['secretkey'] == s3_secret_key):
            logging.debug('Found existing secret openbio-artifact-repository...')
            return
    except:
        pass

    if existing_secret:
        logging.debug('Deleting previous secret openbio-artifact-repository...')
        kubernetes_client.delete_secret(name='openbio-artifact-repository', namespace=namespace)

    logging.debug('Creating new secret openbio-artifact-repository...')
    kubernetes_client.create_secret(name='openbio-artifact-repository',
                                    data={'accesskey': s3_access_key,
                                          'secretkey': s3_secret_key},
                                    labels={'app.kubernetes.io/managed-by': 'openbio'},
                                    namespace=namespace)

def setup_config_map(kubernetes_client, artifacts_url, namespace):
    s3_repository_data = {'s3': {'bucket': artifacts_url.path.strip('/'),
                                 'endpoint': '%s:%s' % (artifacts_url.hostname, artifacts_url.port),
                                 'insecure': True,
                                 'accessKeySecret': {'name': 'openbio-artifact-repository',
                                                     'key': 'accesskey'},
                                 'secretKeySecret': {'name': 'openbio-artifact-repository',
                                                     'key': 'accesskey'}}}

    config_maps = kubernetes_client.list_config_maps(namespace=namespace, label_selector='app.kubernetes.io/managed-by=openbio')
    existing_config_map = next((c for c in config_maps if c.metadata.name == 'openbio-artifact-repository'), None)
    try:
        if existing_config_map:
            existing_s3_repository_data = yaml.safe_load(existing_config_map.data['s3-repository'])
            if (existing_s3_repository_data['s3']['bucket'] == s3_repository_data['s3']['bucket'] and
                existing_s3_repository_data['s3']['endpoint'] == s3_repository_data['s3']['endpoint']):
                logging.debug('Found existing config map openbio-artifact-repository...')
                return
    except:
        pass

    if existing_config_map:
        logging.debug('Deleting previous config map openbio-artifact-repository...')
        kubernetes_client.delete_config_map(name='openbio-artifact-repository', namespace=namespace)

    logging.debug('Creating new config map openbio-artifact-repository...')
    kubernetes_client.create_config_map(name='openbio-artifact-repository',
                                        data={'s3-repository': yaml.dump(s3_repository_data)},
                                        labels={'app.kubernetes.io/managed-by': 'openbio'},
                                        annotations={'workflows.argoproj.io/default-artifact-repository': 's3-repository'},
                                        namespace=namespace)

def setup_artifact_repository(artifact_repository_url, namespace):
    logging.debug('Setting up artifact repository...')
    kubernetes_client = KubernetesClient()

    artifacts_url = urlparse(artifact_repository_url)
    if artifacts_url.scheme != 's3':
        raise SystemError('Only S3 URLs are supported for artifacts')

    setup_secret(kubernetes_client, artifacts_url, namespace)
    setup_config_map(kubernetes_client, artifacts_url, namespace)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Setup for using an artifact repository in Argo')
    parser.add_argument('artifact_repository_url', metavar='<artifact_repository_url>', type=str)
    args = parser.parse_args()

    setup_artifact_repository(args.artifact_repository_url, 'default')
