from flask import Flask, request
import json
import sqlalchemy
from sqlalchemy import MetaData, Table, Column, Integer, String, ARRAY, Float, cast
import argparse
import openai
from contextlib import closing
from typing import List

DB_STRING = 'postgresql:///openai_cache?host=/var/run/postgresql'

class State:

    def __init__(self):
        self.db = sqlalchemy.create_engine(DB_STRING)
        self.conn = self.db.connect()
        self.meta = MetaData(self.db)

        self.results = Table('results', self.meta,
            Column('id', Integer, primary_key=True),
            Column('engine', String, nullable=False),
            Column('prompt', String, nullable=False),
            Column('max_tokens', Integer, nullable=False),
            Column('temperature', Float, nullable=False),
            Column('top_p', Integer, nullable=False),
            Column('stop', ARRAY(String), nullable=False),
            Column('presence_penalty', Float, nullable=False),
            Column('frequency_penalty', Float, nullable=False),
            Column('completion', String, nullable=False),
        )

    
    def close(self):
        self.conn.close()

    def completion(
        self,
        engine: str,
        prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 16,
        top_p: float = 1.0,
        stop: List[str] = [],
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        n: int = 1
    ) -> List[str]:
        # Find existing results with the same parameters.
        select_existing = self.results.select().where(
            (self.results.c.engine == engine) &
            (self.results.c.prompt == prompt) &
            (self.results.c.max_tokens == max_tokens) &
            (self.results.c.temperature == temperature) &
            (self.results.c.top_p == top_p) &
            (self.results.c.stop == cast(stop, ARRAY(String))) &
            (self.results.c.presence_penalty == presence_penalty) &
            (self.results.c.frequency_penalty == frequency_penalty)
        )
        existing = [ row['completion'] for row in self.conn.execute(select_existing).fetchall() ]
        if n <= len(existing):
            return existing[:n]
        
        n = n - len(existing)

        
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop if len(stop) > 0 else None,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            n=n,
        )
        new_completions =  [ choice.text for choice in response.choices ]
        for completion in new_completions:
            self.results.insert().values(
                engine=engine,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                completion=completion
            ).execute()
        return existing + new_completions

def server(args):
    app = Flask('OpenAI Caching Proxy')
    openai.api_key = args.openai_api_key
    state = State()

    @app.route('/completion/<engine>', methods=['POST'])
    def completion(engine: str):
        resp = state.completion(engine, **json.loads(request.get_json()))
        return json.dumps(resp)
    
    app.run(host=args.host, port=args.port)

def completion(args):
    with (closing(State())) as state:
        for line in state.completion('text-curie-001', args.prompt, n=args.n):
            print(line)

def initdb(args):
    with (closing(State())) as state:
        state.meta.drop_all()
        state.results.create()

def main():
    parser = argparse.ArgumentParser(description='Run the OpenAI cache')
    subparsers = parser.add_subparsers()

    initdb_parser = subparsers.add_parser('initdb')
    initdb_parser.set_defaults(func=lambda: initdb(args))


    completion_parser = subparsers.add_parser('completion')
    completion_parser.add_argument('prompt', type=str)
    completion_parser.add_argument('-n', type=int, default=1)
    completion_parser.set_defaults(func=lambda: completion(args))

    server_parser = subparsers.add_parser('server')
    server_parser.add_argument('--host', type=str, default='192.168.50.7')
    server_parser.add_argument('--port', type=int, default=5000)
    server_parser.add_argument('--openai-api-key', type=str)
    server_parser.set_defaults(func=lambda: server(args))

    args = parser.parse_args()
    args.func()

if __name__ == '__main__':
    main()    
