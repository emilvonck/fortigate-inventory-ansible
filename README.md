# Ansible collection for Fortigate switch- and wifi controller inventory.

Ansible collection with a inventory plugin.

## Installation

**Note**: Python 3.8+ is required.

### Python packages

```
ansible
requests
```

### Install the collection

```bash
ansible-galaxy collection install git+https://github.com/emilvonck/fortigate-inventory-ansible.git
```

## Usage

Update "ansible.cfg".
```bash
cat << 'EOF' > ansible.cfg
[inventory]
enable_plugins = evonck.fortigate.inventory, yaml, ini
EOF
```

Update "example_fortigate.yaml", replace with your values.
```bash
cat << 'EOF' > example_fortigate.yaml
---
plugin: evonck.fortigate.inventory
api_host: 192.0.2.1 # Can also be set with FORTIGATE_URL environment variable.
token: tokengoeshere # Can also be set with FORTIGATE_TOKEN environment variable.
validate_certs: False # Defaults to True
EOF
```
Run
```bash
ansible-inventory -i example_fortigate.yaml --list
```

## Contributing
Pull requests are welcome.
