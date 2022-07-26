import * as pg from "pg";
import * as openai from "openai";
import { sleepInSeconds, fromPromise } from "@arjunguha/pervasives.js";
import { program } from "commander";
import * as express from "express";
import * as bodyParser from "body-parser";
import * as morgan from "morgan";

export async function completion(
    client: pg.Client,
    openaiClient: openai.OpenAIApi,
    engine: string,
    prompt: string,
    temperature: number = 1.0,
    max_tokens: number = 16,
    top_p: number = 1.0,
    stop: string[] = [],
    presence_penalty: number = 0.0,
    frequency_penalty: number = 0.0,
    n: number = 1,
    skipCache: boolean = false): Promise<string[]> {

    let existing = [ ];
    if (skipCache === false) {
        // Find existing results with the same parameters.
        const existingRows = await client.query(
            `SELECT completion FROM results WHERE
            engine = $1 AND
            prompt = $2 AND
            max_tokens = $3 AND
            temperature = $4 AND
            top_p = $5 AND
            stop = $6 AND
            presence_penalty = $7 AND
            frequency_penalty = $8`,
            [engine, prompt, max_tokens, temperature, top_p, stop, presence_penalty, frequency_penalty]);

        existing = existingRows.rows.map(row => row.completion);
        if (n <= existing.length) {
            return existing.slice(0, n);
        }
        n = n - existing.length;
    }

    // An easy hack to deal with the Codex rate limit. We sleep for
    // 60 / 20 + epsilon seconds, where 20 is the maximum number of requests
    // we can make in a minute.
    if (engine.includes("code") || engine.includes("codex")) {
        await sleepInSeconds(60 / 20 + 2);
    }

    for (let i = 0; i < 5; i++) {
        const newCompletionsResult = 
          (await fromPromise(openaiClient.createCompletion(
                { model: engine, prompt, temperature, max_tokens, top_p, stop, presence_penalty, frequency_penalty, n })))
            .map(response => response.data.choices?.map(choice => choice.text ?? "").filter(choice => choice.length > 0) ?? []);
        if (newCompletionsResult.ok === false) {
            console.error(`Error querying OpenAI API: ${JSON.stringify(newCompletionsResult)}`);
            await sleepInSeconds(1);
            continue;
        }
        const newCompletions = newCompletionsResult.expect("should not fail");
        for (const completion of newCompletions) {
            const response = 
                await fromPromise(client.query(
                    `INSERT INTO results (engine, prompt, max_tokens, temperature, top_p, stop, presence_penalty, frequency_penalty, completion)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
                    [engine, prompt, max_tokens, temperature, top_p, stop, presence_penalty, frequency_penalty, completion]));
            response.map(() => { return; }).recover(message => {
                // Ignore this error and proceed. It is hopefully transient,
                // and it will not affect the result, just the timing.
                console.error(`Error inserting into results: ${message}`);
            })
        }
        return existing.concat(newCompletions);
    }

    console.error(`Failed to query OpenAI API 5 times.`);
    return [];
}


async function server(port: number, bindAddress: string) {
    const db = new pg.Client("postgresql:///openai_cache?host=/var/run/postgresql");
    await db.connect();
    const conf = new openai.Configuration({ 
        apiKey: process.env.OPENAI_API_KEY,
    });
    const openAIClient = new openai.OpenAIApi(conf);    

    const app = express.default();

    app.use(morgan.default("combined"));
    app.use(bodyParser.json());

    app.post("/completion/:engine", async (req, res) => {
        const results = await completion(db,
            openAIClient, 
            req.params.engine,
             req.body.prompt,
             req.body.temperature,
             req.body.max_tokens,
             req.body.top_p,
             req.body.stop,
             req.body.presence_penalty,
             req.body.frequency_penalty,
             req.body.n,
             req.body.skipCache);

        res.json(results);
        
    });

    return new Promise((resolve, reject) => {
        app.listen(port, bindAddress, () => {
          console.log(`Server started on port ${port}`);
        });
      });
    
}

async function main() {
    await program
        .option("-p --port <PORT>", "port to run server on", parseInt)
        .option("-b --bind-address <BIND_ADDRESS>", "address to bind server to", "0.0.0.0")
        .action(async (options) => {
           await server(options.port, options.bindAddress);

        })
        .parseAsync();
}

  
main()
  .then(() => {
    process.exit(0);
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
