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
- Docker Compose Version v2.24.6
- Python 3.11.x (Tested with Python 3.11.5)
- OS should be able to run Makefile

## Requirements for auto renewal via cron

- Linux or Unix machine with CRON installed.

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

To automatically check if a certificate should be renewed, you will have to set up a 
cron job.

Start the crontab editor

```bash
crontab -e
crontab -u [username] -e
```

Add the following line to it. Adjust the frequency of the checks to your preference.
The time set below will check daily at 1am based on the time and timezone set for
your host operating system.

`{path}` Should be set to the root folder where this utility resides.
`make linode-update` will only update the NodeBalancer if the certificate were
renewed.

```bash
#MIN HOUR DOM MON DOW CMD
* 1 * * * cd {path} && make certbot-renew && make linode-update 
```

This same method can be applied to other operating systems like MacOS (Automator) and Windows (Scheduled Tasks), but
I will leave that for you to figure out.

## Todo
- Let the renewal of the docker cert hook the update of Linode.
- Create a Discover feature to discover Linode NodeBalancers to include in the environment config.
- Make sure the correct number of options can be used with the `main.py` CLI utility. 
- Notification of some kind. (https://www.datacamp.com/tutorial/how-to-send-slack-messages-with-python)

## References
### Docker HUB
- https://hub.docker.com/r/linode/cli
- https://hub.docker.com/r/certbot/dns-cloudflare
- https://hub.docker.com/_/python

### General Research
- Makefile Manual: https://www.gnu.org/software/make/manual/make.html
- https://www.linode.com/docs/api/nodebalancers/#nodebalancers-list
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

### Windows Scheduled Tasks
- https://learn.microsoft.com/en-us/previous-versions/orphan-topics/ws.10/cc772785(v=ws.10)?redirectedfrom=MSDN

### MacOS Scheduled Tasks
- https://www.launchd.info/