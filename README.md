# OpenAI Caching Proxy

*WARNING*: Running this program on the open Internet violates the OpenAI
terms of service.

## Installation

Checkout the repository and run `pip install .`.

## Server

1. Install PostgreSQL.
   
   ```
   sudo apt-get install postgresql-10  postgresql-server-dev-10
   ```
   
2. Create a database called `openai_cache` and ensure that the user that will run the
   server has access to the database.

   ```
   sudo -u postgres psql
   CREATE DATABASE openai_cache;
   CREATE USER <username>;
   GRANT ALL PRIVILEGES ON DATABASE codex_evaluation TO <username>;
   ```

3. Install the package:

   ```
   pip3 install .
   ```
   
4. Run `python3 -m openai_caching_proxy.server initdb`
5. Run `python3 -m openai_caching_proxy.server server --host IP --port=PORT --openai-api-key=KEY`

### For supervisord

```
[program:openai_caching_proxy]
user=arjun
command=/home/arjun/bin/openai_caching_server.sh
```

```
#!/bin/bash
conda activate
python3 -m openai_caching_proxy.server server \
        --host IP \
        --port PORT \
        --openai-api-key=KEY
```



## Client

```
>>> from openai_caching_proxy.client import completion, set_base_url
>>> set_base_url('http://IP:PORT')
>>> completion(engine='curie', prompt='Hello, cats!', n=2)
['”) and portability (the ability to descend into a cave should you', '\n\nBut don’t worry! I won’t take all']
```
