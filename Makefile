# Reference Sites:
# https://www.dinotools.de/en/2019/12/23/use-python-with-virtualenv-in-makefiles/
# https://earthly.dev/blog/python-makefile/
# https://ljvmiranda921.github.io/notebook/2021/05/12/how-to-manage-python-envs/

# Misc
.DEFAULT_GOAL=help

## ———————————————— General Let's Encrypt Automations 🖖 ————————————————

help: ## Outputs this help screen.
	@grep -E '(^[a-zA-Z0-9_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

setup: ## This will setup the project (Remember to configure your .env file first.)
	@docker build . --tag certbot-ssl
	@docker run -it --rm -v .:/app -t certbot-ssl -t
	@docker run -it --rm -v .:/app -t certbot-ssl --cf-setup

certbot-new: ## This will issue a new certificate or setup the Let's Encrypt environment with the current certificate.
	@docker run -it --rm -v .:/app -t certbot-ssl --new-certificate | /bin/sh 2> /dev/null

certbot-renew: ## This will attempt to renew the Let's Encrypt certificate.
	@docker run -it --rm -v .:/app -t certbot-ssl --renew-certificate | /bin/sh 2> /dev/null

linode-update: ## This updates the Linode NodeBalancer with the current available certificate.
	@docker run -it --rm -v .:/app -t certbot-ssl --update-nodebalancer | /bin/sh 2> /dev/null
