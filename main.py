"""
Let's Encrypt Automation
----------------------------------------------------------------------
This is a simple CLI which helps to remove the complexities of
running docker commands while renewing and managing Let's Encrypt
certificates.
----------------------------------------------------------------------
LICENSE : GNU GPLv3
"""

import argparse
import os
import io
import requests
from dotenv import load_dotenv


def test_docker() -> None:
    """
    This is a simple method to test that this script was reachable in the Python docker container.
    :return:
    """
    print("TEST THE LETS ENCRYPT PROGRAM")


def validate_certificate(domain: str) -> None:
    """
    This will validate the installed SSL certificate on the configured domain.
    :param domain:
    :return:
    """
    print('VALIDATE SSL CERT')


def linode_get_nodebalancer_configs(key: str, nodebalancer_id: int) -> None:
    """
    This will find all the NodeBalancer configs based on the NodeBalancer ID.
    :param key:
    :param nodebalancer_id:
    :return:
    """
    headers = {
        'Authorization': f'Bearer {key}'
    }

    config_response = requests.request("GET",
                                       f'{linode_api_base_url}/nodebalancers/{nodebalancer_id}/configs/',
                                       headers=headers,
                                       data={})
    config_data = config_response.json()

    for config in config_data["data"]:
        print(f' |--> Config - {config["protocol"]}:{config["port"]} - ID: {config["id"]}')


def linode_get_nodebalancers(key: str) -> None:
    """
    This will get a list of all NodeBalancers.
    :param key:
    :return:
    """
    headers = {
        'Authorization': f'Bearer {key}'
    }

    balancer_response = requests.request("GET",
                                         f'{linode_api_base_url}/nodebalancers',
                                         headers=headers,
                                         data={})

    api_data = balancer_response.json()

    for nb in api_data["data"]:
        print(f'NodeBalancer - {nb["label"]} - ID: {nb["id"]}')
        linode_get_nodebalancer_configs(key=key, nodebalancer_id=nb["id"])


def linode_nodebalancer_config_update(key: str, nodebalancer_id: str, config_id: str, domain: str) -> None:
    """
    This updates the Linode NodeBalancer as configured.
    :param key:
    :param nodebalancer_id:
    :param config_id:
    :param domain:
    :return:
    """

    # Check to see if the deploy.state file exists. If it does, continue with the change, if it does not exit.

    deploy_state_file = './.docker/certbot/etc/letsencrypt/renewal-hooks/deploy.state'

    if not os.path.exists(deploy_state_file):
        raise Exception('DEPLOY.STATE FILE DOES NOT EXIST')

    with io.open(deploy_state_file, 'r') as state_file:
        state = state_file.read().split('=')[1].replace('\n', '')

    if state != 'true':
        print('NO UPDATE AVAILABLE. STATE FILE IS NOT SET TO UPDATE (STATE != TRUE).')
        exit(0)

    src_folder = './.docker/certbot/etc/letsencrypt/live/' + domain + '/'

    # grab the required ssl key file content
    with io.open(src_folder + 'privkey.pem', 'r') as key_file:
        ssl_key_content = key_file.read()
        ssl_key_content.replace('\n', '\\n')
        key_file.close()

    # grab the required ssl key file content
    with io.open(src_folder + 'cert.pem', 'r') as cert_file:
        ssl_cert_content = cert_file.read()
        ssl_cert_content.replace('\n', '\\n')
        cert_file.close()

    headers = {
        'Authorization': f'Bearer {key}'
    }

    data = {
        "ssl_cert": f"{ssl_cert_content}",
        "ssl_key": f"{ssl_key_content}",
    }

    balancer_response = requests.request("PUT",
                                         f'{linode_api_base_url}/nodebalancers/{nodebalancer_id}/configs/{config_id}',
                                         headers=headers,
                                         data=data)

    if balancer_response.status_code == 200:
        with io.open(deploy_state_file, 'w') as state_file:
            state = state_file.write('deploy=false')
        print('NODEBALANCER CONFIG SUCCESSFULLY UPDATED')


def new_certificate(
        domain: str,
        email: str,
        cloudflare_propagation_timeout: str,
        dry_run: str,
        execute_command: bool) -> None:
    """
    This will run the docker command to get a new certificate
    :param dry_run:
    :param cloudflare_propagation_timeout:
    :param domain:
    :param email:
    :param execute_command:
    :return:
    """

    cmd_str = f'docker run --tty --rm --name certbot ' \
              f'--mount type=bind,source=$(pwd)/.docker/certbot/etc/letsencrypt,target=/etc/letsencrypt ' \
              f'--mount type=bind,source=$(pwd)/.docker/certbot/var/log/letsencrypt,target=/var/log/letsencrypt ' \
              f'--mount type=bind,source=$(pwd)/.docker/certbot/.secrets,target=/root/.secrets/certbot,readonly ' \
              f'certbot/dns-cloudflare:latest certonly ' \
              f'--dns-cloudflare ' \
              f'--dns-cloudflare-credentials "/root/.secrets/certbot/cloudflare.ini" ' \
              f'--dns-cloudflare-propagation-seconds {cloudflare_propagation_timeout} ' \
              f'-d {domain} ' \
              f'-m {email} ' \
              f'-n ' \
              f'--agree-tos ' \
              f'--no-eff-email'

    if dry_run == 'yes':
        cmd_str = cmd_str + f' --dry-run '

    print(cmd_str, end='')

    if execute_command:
        os.system(cmd_str)


def renew_certificate(
        domain: str,
        email: str,
        cloudflare_propagation_timeout: str,
        dry_run: str,
        execute_command: bool) -> None:
    """
    This will renew the present certificate.
    :param dry_run:
    :param cloudflare_propagation_timeout:
    :param domain:
    :param email:
    :param execute_command:
    :return:
    """

    new_certificate(
        domain=domain,
        email=email,
        dry_run=dry_run,
        cloudflare_propagation_timeout=cloudflare_propagation_timeout,
        execute_command=execute_command
    )


def cf_setup() -> None:
    """
    This will set up the secrets file for CloudFlare.
    :return:
    """

    src_folder = './.docker/certbot/.secrets/'

    with io.open(src_folder + 'cloudflare.ini.example', 'r') as src_file:
        config_str = src_file.read()
        src_file.close()

    if not os.getenv('CF_API_KEY'):
        raise Exception("API KEY Required for CloudFlare.")

    # There has to be an API key
    config_str = config_str.replace('#dns_cloudflare_api_key =',
                                    'dns_cloudflare_api_key = ' + os.getenv('CF_API_KEY'))

    # This triggers the global API setup
    if os.getenv('CF_ACCOUNT_EMAIL'):
        config_str = config_str.replace('#dns_cloudflare_email =',
                                        'dns_cloudflare_email = ' + os.getenv('CF_ACCOUNT_EMAIL'))

    with io.open(src_folder + 'cloudflare.ini', 'w') as dst_file:
        dst_file.write(config_str)
        dst_file.close()

    os.system(f'chmod 0600 {src_folder}cloudflare.ini')

    print("CLOUDFLARE SECRETS SETUP COMPLETE")


def main() -> argparse:
    parser = argparse.ArgumentParser(description='Let\'s Encrypt Management Tool')
    parser.add_argument('-n', '--new-certificate',
                        action='store_true',
                        default=False,
                        help='Generate CLI command to get a new certificate through a Docker container.')

    parser.add_argument('-r', '--renew-certificate',
                        action='store_true',
                        default=False,
                        help='Generate CLI command to renew a certificate through a Docker container.')

    parser.add_argument('-u', '--update-nodebalancer',
                        action='store_true',
                        default=False,
                        help='Generate CLI command to update your Linode NodeBalancer through a Docker container.')

    parser.add_argument('-s', '--cf-setup',
                        action='store_true',
                        default=False,
                        help='CloudFlare Setup of Secrets File.')

    parser.add_argument('-t', '--test-output',
                        action='store_true',
                        default=False,
                        help='Generate CLI command to Update Linode NodeBalancer through a Docker container.')

    parser.add_argument('-x', '--execute-command',
                        action='store_true',
                        default=False,
                        help='Execute the command instead of printing it out to the terminal. This is helpful'
                             'when running the script directly on the host and not through a Docker container.')

    parser.add_argument('-d', '--nodebalancer-discover',
                        action='store_true',
                        default=False,
                        help='Discover the Linode NodeBalancer infrastructure.')

    parser.add_argument('-v', '--validate-ssl-cert',
                        action='store_true',
                        default=False,
                        help='Validate the installed SSL certificate on the domain as configured.')

    args = parser.parse_args()

    if args.test_output:
        test_docker()
    if args.validate_ssl_cert:
        validate_certificate(domain=os.getenv('CERTBOT_DOMAIN'))
    if args.nodebalancer_discover:
        linode_get_nodebalancers(key=os.getenv("LINODE_TOKEN"))
    if args.cf_setup:
        cf_setup()
    if args.new_certificate:
        new_certificate(
            domain=os.getenv('CERTBOT_DOMAIN'),
            email=os.getenv('CERTBOT_EMAIL'),
            dry_run=os.getenv('CERTBOT_DRY_RUN'),
            cloudflare_propagation_timeout=os.getenv('CF_PROPAGATION_TIMEOUT'),
            execute_command=args.execute_command
        )
    if args.renew_certificate:
        renew_certificate(
            domain=os.getenv('CERTBOT_DOMAIN'),
            email=os.getenv('CERTBOT_EMAIL'),
            dry_run=os.getenv('CERTBOT_DRY_RUN'),
            cloudflare_propagation_timeout=os.getenv('CF_PROPAGATION_TIMEOUT'),
            execute_command=args.execute_command
        )
    if args.update_nodebalancer:
        linode_nodebalancer_config_update(
            key=os.getenv('LINODE_TOKEN'),
            nodebalancer_id=os.getenv('LINODE_NODEBALANCER_ID'),
            config_id=os.getenv('LINODE_NODEBALANCER_CONFIG_ID'),
            domain=os.getenv('CERTBOT_DOMAIN')
        )

        # update_linode(
        #     domain=os.getenv('CERTBOT_DOMAIN'),
        #     api_token=os.getenv('LINODE_TOKEN'),
        #     node_balancer_id=os.getenv('LINODE_NODEBALANCER_ID'),
        #     config_id=os.getenv('LINODE_NODEBALANCER_CONFIG_ID'),
        #     execute_command=args.execute_command
        # )

    return args


if __name__ == '__main__':
    linode_api_base_url = "https://api.linode.com/v4"
    load_dotenv()
    main()
