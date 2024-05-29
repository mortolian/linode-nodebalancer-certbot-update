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
import sys
import os
import io
from dotenv import load_dotenv


def test_docker() -> None:
    """
    This is a simple method to test that this script was reachable in the Python docker container.
    :return:
    """
    print("TEST THE LETS ENCRYPT PROGRAM")


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


def update_linode(
        domain: str,
        api_token: str,
        node_balancer_id: str,
        config_id: str,
        execute_command: bool) -> None:
    """
    This will update Linode with the current certificate on the specified
    Linode LoadBalancer config.
    :param domain:
    :param api_token:
    :param node_balancer_id:
    :param config_id:
    :param execute_command:
    :return:
    """

    src_folder = './.docker/certbot/etc/letsencrypt/live/' + domain + '/'

    # grab the required ssl key file content
    with io.open(src_folder + 'privkey.pem', 'r') as key_file:
        ssl_key_content = key_file.read()
        print(ssl_key_content)
        key_file.close()

    # grab the required ssl key file content
    with io.open(src_folder + 'cert.pem', 'r') as cert_file:
        ssl_cert_content = cert_file.read()
        print(ssl_cert_content)
        cert_file.close()

    cmd_str = f'docker run --rm --tty -e LINODE_CLI_TOKEN=' \
              f'{api_token} ' \
              f'linode/cli:latest nodebalancers config-update ' \
              f'{node_balancer_id} {config_id} ' \
              f'--ssl_cert="{ssl_cert_content}" --ssl_key="{ssl_key_content}"'

    print(cmd_str, end='')

    if execute_command:
        os.system(cmd_str)


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

    # there has to be an API key
    config_str = config_str.replace('#dns_cloudflare_api_key =',
                                    'dns_cloudflare_api_key = ' + os.getenv('CF_API_KEY'))

    # this triggers the global API setup
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

    args = parser.parse_args()

    if args.test_output:
        test_docker()
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
        update_linode(
            domain=os.getenv('CERTBOT_DOMAIN'),
            api_token=os.getenv('LINODE_TOKEN'),
            node_balancer_id=os.getenv('LINODE_NODEBALANCER_ID'),
            config_id=os.getenv('LINODE_NODEBALANCER_CONFIG_ID'),
            execute_command=args.execute_command
        )

    return args


if __name__ == '__main__':
    load_dotenv()
    main()
