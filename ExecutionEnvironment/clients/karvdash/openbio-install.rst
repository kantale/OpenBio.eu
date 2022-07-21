OpenBio
--------


Add an application for OpenBio by going to https://139.91.210.46.nip.io/admin/oauth2_provider/application/. Set the redirect URI to https://openbio.139.91.210.46.nip.io/platform/complete/knot/.

Create a folder for the database::

    mkdir $HOME/knot/db/openbio

Install::

    git clone https://github.com/kantale/OpenBio.eu.git && cd OpenBio.eu
    kubectl create namespace openbio
    cat > oidc.py <<EOF
SECURE_PROXY_SSL_HEADER = ('HTTP_X_SCHEME', 'https')

from social_core.backends.open_id_connect import OpenIdConnectAuth

class KnotConnect(OpenIdConnectAuth):
    name = 'knot'
    OIDC_ENDPOINT = 'https://139.91.210.46.nip.io/oauth'
    EXTRA_DATA = OpenIdConnectAuth.EXTRA_DATA + ['knot_namespace', 'knot_ingress_url', 'knot_private_registry_url', 'knot_argo_workflows_url']

AUTHENTICATION_BACKENDS = ('OpenBio.obc_private.KnotConnect',) + AUTHENTICATION_BACKENDS

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_VERIFY_SSL = False
SOCIAL_AUTH_KNOT_KEY = 'XYZ'
SOCIAL_AUTH_KNOT_SECRET = 'XXYYZZ'

LOGIN_BACKEND = KnotConnect.name
EOF
    helm install openbio ./chart/openbio --namespace openbio \
        --set image="kantale/openbio:0.2.1b3" \
        --set openbio.databaseHostPath="$HOME/knot/db/openbio" \
        --set openbio.djangoSecret="zr14+4kz*d@f1ce\!sxzk*unwnhpvrwttxpizxu^r^c729gl4(a" \
        --set openbio.djangoDebug="1" \
        --set openbio.title="OpenBio" \
        --set openbio.serverURL="https://openbio.139.91.210.46.nip.io" \
        --set openbio.fromEmail="admin@139.91.210.46.nip.io" \
        --set openbio.adminEmail="admin@139.91.210.46.nip.io" \
        --set openbio.termsURL="" \
        --set openbio.privacyURL="" \
        --set openbio.showFundingLogos=false \
        --set openbio.ingressEnabled=true \
        --set openbio.ingressURL="https://openbio.139.91.210.46.nip.io" \
        --set-file openbio.extraSettings=oidc.py

Add a permissive cluster role binding::

    kubectl create clusterrolebinding openbio-cluster-admin --clusterrole=cluster-admin --serviceaccount=openbio:default


Change-Theme::
 
 cp -r dashboard/static/dashboard/theme db/


    cp:
    <li class="nav-item">
      <a class="nav-link" href="https://openbio.139.91.210.46.nip.io/platform" target="_blank">
        <i class="fa fa-flask" aria-hidden="true"></i> OpenBio
      </a>
    </li>

    db/theme/menu_pre.html 







