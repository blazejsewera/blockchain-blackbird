# Blockchain Blackbird
A simple immutable database based on blockchain.

## Usage
- Create (or use an existing) Python venv. Use Python 3.10 and ensure that pip
  installed all the necessary dependencies from `requirements.txt`
  ```bash
  ./setup
  ```
- Start the Pyro NameServer
  ```bash
  ./ns/start
  ```
- Start the DB (Persistence microservice)
  ```bash
  ./db/start
  ```
- Start a couple of nodes
  ```bash
  ./node/start
  ```
- Make a transaction
  ```bash
  ./client/cli
  ```

## Development
There is a handy Pyro NameServer cli tool, available with:
```bash
pyro5-nsc <parameters>
```
Documentation on this tool is available
[here](https://pyro5.readthedocs.io/en/latest/nameserver.html#nameserver-nsc).
Make sure the NameServer is running and Python venv is activated (docs on venv
available [here](https://docs.python.org/3/library/venv.html#creating-virtual-environments)).
