from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    name: inventory
    author:
        - Emil Vonck
    short_description: Fortigate API inventory source.
    description:
        - Get switches and access points from Fortigate switch- and wifi controller via its API.
    options:
        plugin:
            description: token that ensures this is a source file for the 'fortigate' plugin.
            required: True
            choices: ['evonck.fortigate.inventory']
        api_host:
            description: Host of the Fortigate API.
            required: True
            env:
                - name: FORTIGATE_URL
        token:
            required: True
            description:
              - Fortigate API token to be able to read against Fortigate API.
            env:
                - name: FORTIGATE_TOKEN
        api_version:
            description: The version of the Fortigate REST API.
            required: False
        validate_certs:
            description:
                - Whether to validate SSL certificates. Set to False when certificates are not trusted.
            default: True
            type: boolean
"""
from ansible.plugins.inventory import BaseInventoryPlugin
from sys import version as python_version
from ansible.module_utils.ansible_release import __version__ as ansible_version
import requests
import urllib3


class InventoryModule(BaseInventoryPlugin):

    NAME = "evonck.fortigate.inventory"

    def verify_file(self, path):
        """return true/false if this is possibly a valid file for this plugin to consume"""
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(("fortigate.yaml", "fortigate.yml")):
                valid = True
        return valid

    def get_devices(self) -> dict:
        enpoint_mapping = {
            "switch": "api/v2/monitor/switch-controller/managed-switch/status",
            "access_point": "api/v2/monitor/wifi/managed_ap",
        }
        results = {}
        for k, v in enpoint_mapping.items():
            results.update(
                {
                    k: requests.get(
                        f"https://{self.get_option('api_host')}/{v}?access_token={self.get_option('token')}",
                        headers=self.headers,
                        verify=self.get_option("validate_certs"),
                    ).json()["results"]
                }
            )

        return results

    def parse(self, inventory, loader, path, cache=True):

        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path=path)

        self.headers = {
            "User-Agent": f"ansible {ansible_version} Python {python_version.split(' ', maxsplit=1)[0]}",
            "Content-type": "application/json",
        }

        if not self.get_option("validate_certs"):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Parse data and cerate inventory objects
        for _, hosts in self.get_devices().items():
            for host in hosts:
                hostname = host["name"]
                self.inventory.add_host(host=hostname)
                self.inventory.set_variable(
                    host["name"], "ansible_host", host.get("connecting_from")
                )
