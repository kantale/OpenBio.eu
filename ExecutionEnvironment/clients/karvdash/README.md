
Add the following parameters in OpenBio (Profile --> Execution Environment). Don't forget to change the IP.


``json
{
    "type": "karvdash",
    "ARGO_EXECUTION_ENVIRONMENT": true,
    "ARGO_BASE_URL": "https://argo.192.168.1.7.nip.io",
    "ARGO_NAMESPACE_PREFIX": "karvdash-",
    "ARGO_IMAGE_REGISTRY": "192.168.1.7:5000",
    "ARGO_IMAGE_CACHE_PATH": "/private/.imagecache",
    "ARGO_WORK_PATH": "/private/openbio"
}
```


