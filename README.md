### Example Commands:

### how to run example::

> go to `examples/config.yaml`

> look at `load_balance.servers` and put tweak those values

### 1. start your servers 

```
- pipenv shell
- cd scripts 
```

#### Server 1:
`python server.py --host 127.0.0.1 --port 60001
`
#### Server 2:

`python server.py --host 127.0.0.1 --port 60002
`

#### Server 3:

`python server.py --host 127.0.0.1 --port 60003`


### 2. Once your servers are started, run

`
python -m stealth_paws.main --config examples/config.yaml --type yaml
`

