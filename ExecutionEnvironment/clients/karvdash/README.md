
Add the following parameters in OpenBio (Profile --> Execution Environment). Don't forget to change the IP.


```json
{
    "type": "karvdash",
    "namespace": "karvdash-admin",
    "argo_url": "https://argo.192.168.1.7.nip.io",
    "image_registry": "192.168.1.7:5000",
    "image_cache_path": "/private/.imagecache",
    "work_path": "/private/openbio"
}
```


