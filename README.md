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

```bash
ansible-inventory -i example_fortigate.yaml --list
```

## Contributing
Pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)