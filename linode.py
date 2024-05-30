import requests

linode_api_base_url = "https://api.linode.com/v4"


def linode_get_nodebalancer_configs(nodebalancer_id: int) -> None:
    headers = {
        f'Authorization': 'Bearer 315df3a6b28950d1fc21c3e91737a27f7bb69a0cf67b0b3bb5fa1b866b1d9dfd'
    }

    config_response = requests.request("GET",
                                       f'{linode_api_base_url}/nodebalancers/{nodebalancer_id}/configs/',
                                       headers=headers,
                                       data={})
    config_data = config_response.json()

    for config in config_data['data']:
        print(f' |--> Config - {config["protocol"]}:{config["port"]} - ID: {config["id"]}')


def linode_get_nodebalancers() -> None:
    headers = {
        f'Authorization': 'Bearer 315df3a6b28950d1fc21c3e91737a27f7bb69a0cf67b0b3bb5fa1b866b1d9dfd'
    }

    balancer_response = requests.request("GET",
                                         f'{linode_api_base_url}/nodebalancers',
                                         headers=headers,
                                         data={})

    api_data = balancer_response.json()

    for nb in api_data['data']:
        print(f'NodeBalancer - {nb["label"]} - ID: {nb["id"]}')
        linode_get_nodebalancer_configs(nb['id'])


if __name__ == '__main__':
    linode_get_nodebalancers()

