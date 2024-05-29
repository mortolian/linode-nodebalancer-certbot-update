# Let's Encrypt Automation With Linode Utility

This is a small utility project meant to automate some tasks when working with Let's Encrypt, CloudFlare and Linode NodeBalancers.\
Easily renew a certificate for a Linode NodeBalancer with a DNS-01 challenge through CloudFlare.

One set up of this project will service one domain.

The project is created in such a way that everything runs in Docker containers to eliminate dependency problems\
and no additional software is required on the machine it is run on.\

Set it up on your local machine or a Docker machine to automate the renewal process.

## Version

1.0.0

## Requirements

- Docker version 25.0.3 (Tested with build 4debf41)
- Python 3.11.x (Tested with Python 3.11.5)

## Set up

To get going you will require an API Token for CloudFlare and a Linode CLI / API Token.

- https://cloud.linode.com/profile/tokens - Page to visit for a Linode Access Token.
- https://dash.cloudflare.com/profile/api-tokens - Page to visit for a CloudFlare API Token.

Note: At the time of writing this, global API tokens were still required for CloudFlare. \
It is however better to use new the API tokens with specific privileges where possible.

With these credentials, copy `.env.example` to `.env` and set up the `.env` file in the root of the project.

To get the NodeBalancer you would like to update with Let's Encrypt Certificates the following commands can \
be useful.

```bash
docker run --rm -it -e LINODE_CLI_TOKEN={TOKEN} linode/cli:latest nodebalancers list
docker run --rm -it -e LINODE_CLI_TOKEN={TOKEN} linode/cli:latest nodebalancers configs-list {NODEBALANCER_ID}
```

Once the `.env` file is completed, run the initial setup command.

```bash
make setup
```

A successful setup will have no errors and the below output.

```text
TEST THE LETS ENCRYPT PROGRAM
CLOUDFLARE SECRETS SETUP COMPLETE
```


For a full set of Makefile options, run `make help` or `make`.

## Get a New Certificate or Initial Certificate Retrieval

```bash
make certbot-new
```

Through Python on your host

```bash
python3 main.py --new-certificate --execute-command
```

## Renew a Certificate

```bash
make certbot-renew
```

Through Python on your host

```bash
python3 main.py --renew-certificate --execute-command
```

## Update Linode NodeBalancer Config

```bash
make linode-update
```

Through Python on your host

```bash
python3 main.py --update-nodebalancer --execute-command
```

## Auto Renewals

Set up a CRON for checking and renewing certificates.

```bash
make --file /Users/{user}/certbot-renewals/{domain}/Makefile
```
Makefile Manual: https://www.gnu.org/software/make/manual/make.html

```bash
docker run -it --rm --name certbot \
    --mount type=bind,source=$(pwd)/.docker/certbot/etc/letsencrypt,target=/etc/letsencrypt \
    certbot/dns-cloudflare renew --deploy-hook
```

## Todo
1. Let the renewal of the docker cert hook the update of Linode.
2. Package the python code with requirements.txt and adjust the container.
3. Create a Discover feature to discover Linode NodeBalancers to include in the environment config.
4. Create a set-up script for all the secrets. (Also have links or instructions of getting API keys.)
5. Make sure the correct number of options can be used with the `main.py` CLI utility.
6. Notification of some kind.

## References
### Docker HUB
- https://hub.docker.com/r/linode/cli
- https://hub.docker.com/r/certbot/dns-cloudflare
- https://hub.docker.com/_/python

### General Research
- https://www.linode.com/docs/api/nodebalancers/#config-update
- https://eff-certbot.readthedocs.io/en/latest/install.html#running-with-docker
- https://eff-certbot.readthedocs.io/en/latest/using.html#dns-plugins
- https://eff-certbot.readthedocs.io/en/latest/using.html#hooks
- https://certbot-dns-cloudflare.readthedocs.io/en/stable/#credentials
- https://eff-certbot.readthedocs.io/en/latest/ciphers.html
- https://certbot.eff.org/instructions?ws=webproduct&os=sharedhost
- https://certbot.eff.org/hosting_providers/
- https://en.internet.nl/
- https://www.ssllabs.com/
- https://www.cyberciti.biz/faq/find-check-tls-ssl-certificate-expiry-date-from-linux-unix/
- https://www.howtogeek.com/devops/how-to-send-a-message-to-slack-from-a-bash-script/
- https://gist.github.com/gdoumergue/b8bb2a3faa2d6079deda
- https://api.slack.com/tutorials/tracks/posting-messages-with-curl
- https://eff-certbot.readthedocs.io/en/latest/using.html#setting-up-automated-renewal