import logging
import argparse
import base64
import yaml
import boto3
import botocore

import kubernetes.client
import kubernetes.config

from urllib.parse import urlparse


class KubernetesClient(object):
    def __init__(self, namespace):
        self.namespace = namespace

        try:
            kubernetes.config.load_kube_config()
        except:
            kubernetes.config.load_incluster_config()
        self._core_api = kubernetes.client.CoreV1Api()

    def list_config_maps(self, label_selector=None):
        return self._core_api.list_namespaced_config_map(namespace=self.namespace, label_selector=label_selector).items

    def list_secrets(self, label_selector=None):
        return self._core_api.list_namespaced_secret(namespace=self.namespace, label_selector=label_selector).items

    def create_config_map(self, name, data, labels={}, annotations={}):
        metadata = kubernetes.client.V1ObjectMeta(name=name, labels=labels, annotations=annotations, namespace=self.namespace)
        body = kubernetes.client.V1ConfigMap(api_version='v1', kind='ConfigMap', metadata=metadata, data=data)
        self._core_api.create_namespaced_config_map(namespace=self.namespace, body=body)

    def create_secret(self, name, data, labels={}, annotations={}):
        metadata = kubernetes.client.V1ObjectMeta(name=name, labels=labels, annotations=annotations, namespace=self.namespace)
        body = kubernetes.client.V1Secret(api_version='v1', kind='Secret', metadata=metadata, data=data)
        self._core_api.create_namespaced_secret(namespace=self.namespace, body=body)

    def delete_config_map(self, name):
        self._core_api.delete_namespaced_config_map(name, namespace=self.namespace)

    def delete_secret(self, name):
        self._core_api.delete_namespaced_secret(name, namespace=self.namespace)

class S3Client(object):
    def __init__(self, url):
        self._url = urlparse(url)
        if self._url.scheme not in ('s3'):
            raise ValueError('Unsupported URL')

        # Start an S3 session.
        configuration = {'aws_access_key_id': self.username,
                         'aws_secret_access_key': self.password}
        configuration['endpoint_url'] = 'http://%s' % (self.endpoint)
        configuration['config'] = botocore.client.Config(signature_version='s3v4')
        self._s3 = boto3.resource('s3', **configuration)

        self._bucket_object = self._s3.Bucket(self.bucket)
        if not self._bucket_object.creation_date:
            self._s3.create_bucket(Bucket=self.bucket)

    @property
    def username(self):
        return self._url.username

    @property
    def password(self):
        return self._url.password

    @property
    def bucket(self):
        return self._url.path.strip('/')

    @property
    def endpoint(self):
        return '%s:%s' % (self._url.hostname, self._url.port)

    def upload(self, name, data):
        self._bucket_object.Object(name).put(Body=data)

class S3ArtifactRepository(object):
    def __init__(self, url, namespace):
        self._s3_client = S3Client(url)
        self._kubernetes_client = KubernetesClient(namespace)

        self._setup_secret()
        self._setup_config_map()

    @property
    def managed_by(self):
        return 'openbio'

    @property
    def secret(self):
        return 'openbio-artifact-repository'

    @property
    def config_map(self):
        return 'openbio-artifact-repository'

    def _setup_secret(self):
        s3_access_key = base64.b64encode(self._s3_client.username.encode()).decode()
        s3_secret_key = base64.b64encode(self._s3_client.password.encode()).decode()

        secrets = self._kubernetes_client.list_secrets(label_selector='app.kubernetes.io/managed-by=%s' % self.managed_by)
        existing_secret = next((s for s in secrets if s.metadata.name == self.secret), None)
        try:
            if existing_secret and \
               existing_secret.data['accesskey'] == s3_access_key and \
               existing_secret.data['secretkey'] == s3_secret_key:
                logging.debug('Found existing secret...')
                return
        except:
            pass

        if existing_secret:
            logging.debug('Deleting previous secret...')
            self._kubernetes_client.delete_secret(name=self.secret)

        logging.debug('Creating new secret...')
        self._kubernetes_client.create_secret(name=self.secret,
                                              data={'accesskey': s3_access_key,
                                                    'secretkey': s3_secret_key},
                                              labels={'app.kubernetes.io/managed-by': self.managed_by})

    def _setup_config_map(self):
        s3_repository_data = {'s3': {'bucket': self._s3_client.bucket,
                                     'endpoint': self._s3_client.endpoint,
                                     'insecure': True,
                                     'accessKeySecret': {'name': self.secret,
                                                         'key': 'accesskey'},
                                     'secretKeySecret': {'name': self.secret,
                                                         'key': 'secretkey'}}}

        config_maps = self._kubernetes_client.list_config_maps(label_selector='app.kubernetes.io/managed-by=%s' % self.managed_by)
        existing_config_map = next((c for c in config_maps if c.metadata.name == self.config_map), None)
        try:
            if existing_config_map:
                existing_s3_repository_data = yaml.safe_load(existing_config_map.data['s3-repository'])
                if existing_s3_repository_data['s3']['bucket'] == s3_repository_data['s3']['bucket'] and \
                   existing_s3_repository_data['s3']['endpoint'] == s3_repository_data['s3']['endpoint']:
                    logging.debug('Found existing config map...')
                    return
        except:
            pass

        if existing_config_map:
            logging.debug('Deleting previous config map...')
            self._kubernetes_client.delete_config_map(name=self.config_map)

        logging.debug('Creating new config map...')
        self._kubernetes_client.create_config_map(name=self.config_map,
                                                  data={'s3-repository': yaml.dump(s3_repository_data)},
                                                  labels={'app.kubernetes.io/managed-by': self.managed_by},
                                                  annotations={'workflows.argoproj.io/default-artifact-repository': 's3-repository'})

    def upload_data(self, name, data):
        self._s3_client.upload(name, data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Setup for using an artifact repository in Argo')
    parser.add_argument('artifact_repository_url', metavar='<artifact_repository_url>', type=str)
    args = parser.parse_args()

    artifact_repository = S3ArtifactRepository(args.artifact_repository_url, 'default')
    artifact_repository.upload_data('test.txt', 'this is sample content')
    artifact_repository.upload_data('dir/test.txt', 'this is sample content')
