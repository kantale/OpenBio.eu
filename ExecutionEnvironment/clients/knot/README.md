### Installing

A helmfile is provided so to install OpenBio with [Knot](https://github.com/CARV-ICS-FORTH/knot). For testing on bare metal, follow the [deployment instructions](https://carv-ics-forth.github.io/knot/docs/deployment.html#bare-metal-setup), replacing the last `helmfile` command with:

```bash
# Create local dir for OpenBio database and use local helmfile
mkdir /mnt/state/openbio
helmfile \
  --state-values-set ingress.service.type=NodePort \
  --state-values-set ingress.service.externalIPs\[0\]=${IP_ADDRESS} \
  --state-values-set storage.stateVolume.hostPath=/mnt/state \
  --state-values-set storage.filesVolume.hostPath=/mnt/files \
  sync
```

### Running

Add the following parameters in OpenBio (Profile --> Execution Environment). Don't forget to change the IP.

These are automatically set when OpenBio runs with [Knot](https://github.com/CARV-ICS-FORTH/knot).

```json
{
    "type": "knot",
    "namespace": "knot-admin",
    "argo_url": "https://argo.192.168.1.7.nip.io",
    "image_registry": "192.168.1.7:5000",
    "work_path": "/private/openbio"
}
```
