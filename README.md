# Ansible collection for Fortigate switch- and wifi controller inventory.

Ansible collection with a inventory plugin.

## Installation

**Note**: Python 3.8+ is required. Tested with ansible-core==2.13.5

Use [poetry](https://python-poetry.org/s) to setup environment.

```bash
portry add ansible
poetry add requests
```

**OR**

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
pip install ansible
pip install requests
```

Install the collection

```bash
ansible-galaxy collection install git+https://gitlab.com/evansible/fortigate-inventory-ansible.git
```

## Usage

Update "ansible.cfg".
```ini
[defaults]
force_valid_group_names = always

[inventory]
enable_plugins = evonck.fortigate.inventory, yaml, ini
```

Update "example_fortigate.yaml" with your values.
```yml
---
plugin: evonck.fortigate.inventory
api_host: 192.0.2.1 # Can also be set with FORTIGATE_URL environment variable.
token: tokengoeshere # Can also be set with FORTIGATE_TOKEN environment variable.
validate_certs: False
```

```bash
ansible-inventory -i example_fortigate.yaml --list
```

## Contributing
Pull requests are welcome.