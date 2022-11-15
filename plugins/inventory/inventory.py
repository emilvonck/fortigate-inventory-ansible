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
from ansible.module_utils.ansible_release import __version__ as ansible_version
from ansible.errors import AnsibleError
from sys import version as python_version
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
            "device_serial": self.extract_serial,
            "device_vendor": self.extract_vendor,
            "ansible_distribution_release": self.extract_os_release,
        }

        return extractors

    def extract_connecting_from(self, host):
        value = host.get("connecting_from")

        try:
            return value.lower()
        except AttributeError:
            return value

    def extract_vendor(self, host):
        value = host.get("device_vendor")

        try:
            return value.lower()
        except AttributeError:
            return value

    def extract_serial(self, host):
        value = host.get("serial")

        try:
            return value.lower()
        except AttributeError:
            return value

    def extract_connection_status(self, host):
        value = host.get("status")

        try:
            return value.lower()
        except AttributeError:
            return value

    def extract_device_platform(self, host):
        value = host.get("device_platform")

        try:
            return value.lower()
        except AttributeError:
            return value

    def extract_os_version(self, host):
        value = re.search(r"^[^-]*-v([^-]*)", host.get("os_version"))

        if value:
            return value.group(1).lower()

        raise AnsibleError("Failed to extract_os_version")

    def extract_os_release(self, host):
        value = re.search(r"-.*-(.*)", host.get("os_version"))

        if value:
            return value.group(1).lower()

        raise AnsibleError("Failed to extract_os_version")

    @property
    def part_model_mapping(self):

        part_model_mapping = {
            "S548DF": "fs-548d-fpoe",
            "FS3E32": "fs-3032e",
            "FS1E48": "fs-1048e",
            "S108EF": "fs-108e-fpoe",
            "FP23JF": "fap-23jf",
        }

        return part_model_mapping

    def extract_device_type(self, host):
        part_number = re.search(r"^[^-]*", host["os_version"]).group(0)

        return self.part_model_mapping.get(part_number, None)

    def extract_poe_capable(self, host):
        ports = host.get("ports")

        poe_capable_port_list = [
            i.get("poe_capable") for i in ports if i.get("poe_capable")
        ]
        if poe_capable_port_list:
            return "poe_switch"

        return "no_poe_switch"

    @property
    def group_extractors(self):
        extractors = {
            "device_status": self.extract_connection_status,
            "ansible_distribution_version": self.extract_os_version,
            "device_platform": self.extract_device_platform,
            "device_type": self.extract_device_type,
            "poe_switch": self.extract_poe_capable,
        }

        return extractors

    def _fill_host_variables(self, host, hostname):
        for attribute, extractor in self.variable_extractors.items():
            extracted_value = extractor(host)

            self.inventory.set_variable(hostname, attribute, extracted_value)

    def _fill_host_group_variables(self, host, hostname):
        for attribute, extractor in self.group_extractors.items():
            extracted_value = extractor(host)

            self.inventory.set_variable(hostname, attribute, extracted_value)

            safe_group_name = self._generate_safe_group_name(extracted_value)
            self.inventory.add_group(group=safe_group_name)
            self.inventory.add_host(group=safe_group_name, host=hostname)

    def _generate_safe_group_name(self, group_name):

        # https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#creating-valid-variable-names

        first_char: str = group_name[0]
        if first_char.isdigit():
            group_name = f"_{group_name}"

        invalid_characters = [
            "-",
            ".",
            " ",
        ]

        for invalid_character in invalid_characters:
            group_name = group_name.replace(invalid_character, "_")

        return group_name

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
            "fortiswitch": self.get_switches(),
            "fortiap": self.get_access_points(),
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

        # Parse data and create inventory objects
        for endpoint, hosts in self.get_devices().items():
            for host in hosts:
                hostname = host["name"]
                self.inventory.add_host(host=hostname)
                self.inventory.set_variable(
                    hostname, "ansible_host", host.get("connecting_from")
                )
                host.update({"device_platform": endpoint})
                host.update({"device_vendor": "Fortinet"})
                self._fill_host_variables(host=host, hostname=hostname)
                self._fill_host_group_variables(host=host, hostname=hostname)
