from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    name: inventory
    author:
        - Emil Vonck
    short_description: Fortigate inventory source
    description:
        - Get devices from Fortigate
    options:
        plugin:
            description: token that ensures this is a source file for the 'fortigate' plugin.
            required: True
            choices: ['local.fortigate.inventory']
        api_host:
            description: Host of the Fortigate API.
            required: True
            env:
                - name: FORTIGATE_URL
        token:
            required: False
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
