# Ansible collection for Fortigate switch- and wifi controller inventory.

Ansible collection with a inventory plugin.

## Installation

**Note**: Python 3.8+ is required.

Use poetry [poetry](https://python-poetry.org/s) to setup environment.

```bash
poetry install
```

Activate environment
```bash
poetry shell
```

**OR**

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
pip install -r requirements.txt
```

## Usage

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

## License
[MIT](https://choosealicense.com/licenses/mit/)