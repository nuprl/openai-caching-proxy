# OpenAI Caching Proxy

*WARNING*: Running this program on the open Internet violates the OpenAI
terms of service.

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

3. Build the package

   ```
   npm install
   npm run-script build
   ```

4. Ensure `OPENAI_API_KEY` is set in the environment.

5. Run `node ./target/index.js -p 7000`
