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
from typing import List, Dict
import requests
import urllib3
import re


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

    @property
    def variable_extractors(self):
        extractors = {
            "ansible_host": self.extract_connecting_from,
            "serial": self.extract_serial,
            "status": self.extract_status,
            "os_distribution": self.extract_os_distribution,
            # "ansible_distribution_version": self.extract_os_version,
        }

        return extractors

    def extract_connecting_from(self, host):
        return host.get("connecting_from", None)

    def extract_serial(self, host):
        return host.get("serial", None)

    def extract_status(self, host):
        return host.get("status", None)

    def extract_os_distribution(self, host):
        os_distribution_mapping = {
            "switch-controller": "FortiSwitchOS"
        }
        return os_distribution_mapping.get(host["path"])

    def extract_os_version(self, host):
        try:
            return re.search(r"^[^-]*-v([^-]*)", host["os_version"]).group(1)
        except Exception:
            return

    """ @property
    def group_extractors(self):
        extractors = {
            "ansible_distribution": self.extract_os_distribution,
            "ansible_distribution_version": self.extract_os_version,
        } """

    def _fill_host_variables(self, host, hostname):
        for attribute, extractor in self.variable_extractors.items():
            extracted_value = extractor(host)

            self.inventory.set_variable(hostname, attribute, extracted_value)

    def get_switches(self) -> List[Dict]:
        endpoint = "api/v2/monitor/switch-controller/managed-switch/status"

        return requests.get(
            f"https://{self.get_option('api_host')}/{endpoint}?access_token={self.get_option('token')}",
            headers=self.headers,
            verify=self.get_option("validate_certs"),
        ).json()["results"]

    def get_access_points(self) -> List[Dict]:
        endpoint = "api/v2/monitor/wifi/managed_ap"

        return requests.get(
            f"https://{self.get_option('api_host')}/{endpoint}?access_token={self.get_option('token')}",
            headers=self.headers,
            verify=self.get_option("validate_certs"),
        ).json()["results"]

    def get_devices(self) -> dict:
        enpoint_mapping = {
            "switch": self.get_switches(),
            "access_point": self.get_access_points(),
        }
        results = {}
        for k, v in enpoint_mapping.items():
            results.update({k: v})

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
                self._fill_host_variables(host=host, hostname=hostname)
