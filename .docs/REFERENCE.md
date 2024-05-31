# Linode Nodebalancer Let's Encrypt Autorenew

This is a small project meant to renew Linode's Nodebalancer SSL certificates with Let's Encrypt certificates when they are about to expire.

## TODO
1. Get a new certificate with a DNS-01 challenge on CloudFlare.
2. Create a set up script for all the secrets. (Also have links or instructions of getting API keys.)

## Future Todo
1. Package the python code with requirements.txt and adjust the container.
2. Create a discover feature to discover Linode NodeBalancers to include in the environment config.

## CloudFlare Documentation

Get a new API key from `https://dash.cloudflare.com/profile/api-tokens`. 
Do not use the Global tokens, create a specific DNS token for greater security.

```bash
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
    -H "Authorization: Bearer {API_KEY}" \
    -H "Content-Type:application/json"
```
Result

```json
{
    "result":
        {
            "id":"55c5a110c40c76b9944618491c42119c",
            "status":"active",
            "not_before":"2024-05-22T00:00:00Z",
            "expires_on":"2024-06-30T23:59:59Z"
        },
        "success":true,
        "errors":[],
        "messages":[
            {
                "code":10000,
                "message":"This API Token is valid and active",
                "type":null
            }
        ]
}
```

## Docker - Run Manually

Run Certbot commands mannually.

```bash
sudo docker run -it --rm --name certbot \
    --mount type=bind,source=$(pwd)/.docker/certbot/etc/letsencrypt,target=/etc/letsencrypt \
    --mount type=bind,source=$(pwd)/.docker/certbot/.secrets,target=/root/.secrets/certbot,readonly \
    certbot/dns-cloudflare certonly \
        --dns-cloudflare \
        --dns-cloudflare-credentials "/root/.secrets/certbot/cloudflare.ini" \
        --dns-cloudflare-propagation-seconds 60 \
        -d opdie.net \
        -m gideon@mortolio.com \
        -v \
        -n \
        --dry-run \
        --agree-tos \
        --no-eff-email
```

```text
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator dns-cloudflare, Installer None
Requesting a certificate for opdie.net
Performing the following challenges:
dns-01 challenge for opdie.net
Waiting 60 seconds for DNS changes to propagate
Waiting for verification...
Cleaning up challenges

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/opdie.net/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/opdie.net/privkey.pem
This certificate expires on 2024-08-20.
These files will be updated when the certificate renews.

NEXT STEPS:
- The certificate will need to be renewed before it expires. Certbot can automatically renew the certificate in the background, but you may need to take steps to enable that functionality. See https://certbot.org/renewal-setup for instructions.
```

```bash
sudo docker run -it --rm --name certbot \
    --mount type=bind,source=$(pwd)/.docker/certbot/etc/letsencrypt,target=/etc/letsencrypt \
    certbot/dns-cloudflare renew
```
```text
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Processing /etc/letsencrypt/renewal/opdie.net.conf
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Certificate not yet due for renewal

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
The following certificates are not due for renewal yet:
  /etc/letsencrypt/live/opdie.net/fullchain.pem expires on 2024-08-20 (skipped)
No renewals were attempted.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

### Renew A Single Certificate

```bash
sudo docker run -it --rm --name certbot \
    --mount type=bind,source=$(pwd)/.docker/certbot/etc/letsencrypt,target=/etc/letsencrypt \
    --mount type=bind,source=$(pwd)/.docker/certbot/.secrets,target=/root/.secrets/certbot,readonly \
    certbot/dns-cloudflare certonly \
        --dns-cloudflare \
        --dns-cloudflare-credentials "/root/.secrets/certbot/cloudflare.ini" \
        --dns-cloudflare-propagation-seconds 30 \
        -d opdie.net \
        -m gideon@mortolio.com \
        -v \
        -n \
        --test-cert \
        --agree-tos \
        --no-eff-email
```

## Linode Docker CLI

```bash
docker run --rm -it -e LINODE_CLI_TOKEN=315df3a6b28950d1fc21c3e91737a27f7bb69a0cf67b0b3bb5fa1b866b1d9dfd linode/cli:latest nodebalancers list
docker run --rm -it -e LINODE_CLI_TOKEN=315df3a6b28950d1fc21c3e91737a27f7bb69a0cf67b0b3bb5fa1b866b1d9dfd linode/cli:latest nodebalancers configs-list 679366
```

### Setup Config of NodeBalancer

```bash
linode_token: ""
linode_apikey: ""
linode_defaultimage: "linode/ubuntu20.04"
linode_region: "nl-ams"
linode_letsencrypt_sslcert: "/etc/letsencrypt/live/vc4a.com/fullchain.pem"
linode_letsencrypt_sslkey: "/etc/letsencrypt/live/vc4a.com/privkey.pem"
linode_nodebalancer_label: "eu-balancer"
```

```bash
#!/bin/bash

docker run --rm -it -e LINODE_CLI_TOKEN=315df3a6b28950d1fc21c3e91737a27f7bb69a0cf67b0b3bb5fa1b866b1d9dfd linode/cli:latest nodebalancers config-update 679366 1105491 --ssl_cert="-----BEGIN CERTIFICATE-----
MIIDmzCCAyGgAwIBAgISK9wolZ0fyWwMLzVvKNsO302YMAoGCCqGSM49BAMDMFIx
CzAJBgNVBAYTAlVTMSAwHgYDVQQKExcoU1RBR0lORykgTGV0J3MgRW5jcnlwdDEh
MB8GA1UEAxMYKFNUQUdJTkcpIFBzZXVkbyBQbHVtIEU1MB4XDTI0MDUyMjEyNTc0
OVoXDTI0MDgyMDEyNTc0OFowFDESMBAGA1UEAxMJb3BkaWUubmV0MFkwEwYHKoZI
zj0CAQYIKoZIzj0DAQcDQgAEW+H8Iiw5QEqYosWW4KI06yYWQfSOVA2WRbb7fsR4
HayFMv7yzlk5/50TYJer/8zqkICw3/PbK86hpe/YdtyZRaOCAhMwggIPMA4GA1Ud
DwEB/wQEAwIHgDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0T
AQH/BAIwADAdBgNVHQ4EFgQUHHUUPPVI4uDSBNTRSaB71yRTt/8wHwYDVR0jBBgw
FoAU/EbRAUNfu3umPTBorhG64LxtydMwXQYIKwYBBQUHAQEEUTBPMCUGCCsGAQUF
BzABhhlodHRwOi8vc3RnLWU1Lm8ubGVuY3Iub3JnMCYGCCsGAQUFBzAChhpodHRw
Oi8vc3RnLWU1LmkubGVuY3Iub3JnLzAUBgNVHREEDTALgglvcGRpZS5uZXQwEwYD
VR0gBAwwCjAIBgZngQwBAgEwggEEBgorBgEEAdZ5AgQCBIH1BIHyAPAAdgCFG66O
7jPBuYc/xJx6fCdlZjtrgGMDBArspsERpavp1wAAAY+gmAjGAAAEAwBHMEUCIQDD
tV6e/wjdF3Tga/zaeDMZC7B5tJsUqlyULl1fqJCgogIgW3130gepUUM5/GO8AJwx
s3dB5jEj5MqEmxbdu6tgAjUAdgDdmTT8peckgMlWaH2BNJkISbJJ97Vp2Me8qz9c
wfNuZAAAAY+gmAjlAAAEAwBHMEUCIQD8nzaAeH7mvEUHX/qnjuD1rwZNoxJ3g2dJ
5pWaNtOXdQIgGG6tkxyPLuZqyZ/P+lwc6t1LvwPPXxFdNoFmMd+jVlgwCgYIKoZI
zj0EAwMDaAAwZQIwdizq79GICNKzxbZSwVUJYaw8Ym6ZEL2/aeKTmNZ8Xua0bSnO
MS3g+1iHbXhD6jx0AjEAtvuzrm8lvHHR5SYVPTeeVYLPYfv6k0ZBWXu5AJBVLiwL
7c3e2wTBmmCd0GwFQsow
-----END CERTIFICATE-----" --ssl_key="-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgIiK8jeBvvOxwc2NT
9B6lnFaGJULAqK3dvuBaV+OGH2OhRANCAARb4fwiLDlASpiixZbgojTrJhZB9I5U
DZZFtvt+xHgdrIUy/vLOWTn/nRNgl6v/zOqQgLDf89srzqGl79h23JlF
-----END PRIVATE KEY-----"
```

```bash
SSL_KEY=$(cat ./.docker/certbot/etc/letsencrypt/live/opdie.net/cert.pem)
SSL_CERT=$(cat ./.docker/certbot/etc/letsencrypt/live/opdie.net/privkey.pem)
```

### References

- https://www.linode.com/docs/api/nodebalancers/#config-update

#### Renewals
- https://eff-certbot.readthedocs.io/en/latest/using.html#setting-up-automated-renewal

#### General 
- https://eff-certbot.readthedocs.io/en/latest/install.html#running-with-docker
- https://eff-certbot.readthedocs.io/en/latest/using.html#dns-plugins
- https://eff-certbot.readthedocs.io/en/latest/using.html#hooks
- https://certbot-dns-cloudflare.readthedocs.io/en/stable/#credentials
- https://eff-certbot.readthedocs.io/en/latest/ciphers.html
- https://certbot.eff.org/instructions?ws=webproduct&os=sharedhost
- https://certbot.eff.org/hosting_providers/
- https://en.internet.nl/
- https://www.ssllabs.com/

#### Additional Research
- https://www.cyberciti.biz/faq/find-check-tls-ssl-certificate-expiry-date-from-linux-unix/
- https://www.howtogeek.com/devops/how-to-send-a-message-to-slack-from-a-bash-script/
- https://gist.github.com/gdoumergue/b8bb2a3faa2d6079deda
- https://api.slack.com/tutorials/tracks/posting-messages-with-curl

#### Docker HUB
- https://hub.docker.com/r/linode/cli
- https://hub.docker.com/r/certbot/dns-cloudflare