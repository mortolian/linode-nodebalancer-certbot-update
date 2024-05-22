# Linode Nodebalancer Let's Encrypt Autorenew

This is a small project meant to renew Linode's Nodebalancer SSL certificates with Let's Encrypt certificates when they are about to expire.


## CloudFlare Documentation





1. Get a new certificate with a DNS-01 challenge on CloudFlare.


2. Create a set up script for all the secrets. (Also have links or instructions of getting API keys.)

```BASH
sudo docker run -it --rm --name certbot \
    -v "./.docker/certbot/etc/letsencrypt:/etc/letsencrypt" \
    -v "./.docker/certbot/var/lib/letsencrypt:/var/lib/letsencrypt" \
    -v "./.docker/certbot/.secrets/cloudflare.ini:/.secrets/certbot/cloudflare.ini" \
    certbot/dns-cloudflare certonly --dns-cloudflare --dns-cloudflare-credentials /.secrets/certbot/cloudflare.ini --dns-cloudflare-propagation-seconds 60 -d opdie.net -m gideon@mortolio.com -v -n --test-cert --agree-tos
```


### References
- https://eff-certbot.readthedocs.io/en/latest/install.html#running-with-docker
- https://eff-certbot.readthedocs.io/en/latest/using.html#dns-plugins
- https://eff-certbot.readthedocs.io/en/latest/using.html#hooks
- https://certbot-dns-cloudflare.readthedocs.io/en/stable/#credentials

- https://eff-certbot.readthedocs.io/en/latest/ciphers.html

- https://certbot.eff.org/instructions?ws=webproduct&os=sharedhost
- https://certbot.eff.org/hosting_providers/

- https://en.internet.nl/
- https://www.ssllabs.com/