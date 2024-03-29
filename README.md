# OpenAI Caching Proxy

This is an HTTP server that mimicks the OpenAI, proxies requests to OpenAI, and 
caches results. It uses the cache when possible. The running server stores the 
OpenAI API key, so clients do not need to store the key themselves.

*WARNING*: Running this program on the open Internet violates the OpenAI
terms of service.

1. Install PostgreSQL.
   
   ```
   sudo apt-get install postgresql
   ```
   
2. Create a database called `openai_cache` and ensure that the user that will
   run the server has access to the database.

   ```
   sudo -u postgres psql
   CREATE DATABASE openai_cache;
   CREATE USER <username>;
   ALTER DATABASE openai_cache OWNER TO <username>;
   ```
   
   Exit `psql` and `exit` to leave sudo.

2. Create a table called results that serves as the cache:

   ```
   psql openai_cache;
   CREATE TABLE results (
     id SERIAL PRIMARY KEY,
     engine character varying NOT NULL,
     prompt character varying NOT NULL,
     max_tokens integer NOT NULL,
     temperature double precision NOT NULL,
     top_p double precision NOT NULL,
     stop character varying[] NOT NULL,
     presence_penalty double precision NOT NULL,
     frequency_penalty double precision NOT NULL,
     completion character varying NOT NULL
   );
   ```
   
   Exit `psql`.

3. Build the package

   ```
   npm install
   npm run-script build
   ```

4. Ensure `OPENAI_API_KEY` is set in the environment.

5. Run `node ./target/index.js -p <port_number>`

## Using with supervisor

Modify this shell script:

```
#!/bin/bash
export OPENAI_API_KEY=<KEY>
export USER=<USERNAME>
export HOME=/home/<USERNAME>
cd /home/<USERNAME>/openai-caching-proxy
exec node ./target/index.js -p 9000
```

And save/modify this as `/etc/supervisor/conf.d/openai_caching_proxy.conf`:

```
[program:openai_caching_proxy]
user=<USERNAME>
command=/home/<USERNAME>/bin/openai_caching_proxy.sh
```
