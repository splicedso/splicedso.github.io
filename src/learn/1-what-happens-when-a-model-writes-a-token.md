# What happens when a model writes a token

Primer 1. No background assumed.

A language model is a very large function. You give it a list of numbers, it gives back one prediction. Everything else in these notes follows from what that function is made of, and from the fact that it has to run once for every token it writes.

## Tokens

A model does not read letters or words. It reads **tokens**: pieces of text from a fixed vocabulary, usually tens of thousands of them. "inference" might be one token; "Spliced" is two, "Sp" and "liced". The headline on our home page is typed out one real token at a time, using the tokenizer of the model we measure, so you can see where the boundaries fall.

Each token is turned into a list of numbers, a vector, before the model does anything with it.

## Weights

The model's knowledge lives in its **weights**: billions of numbers fixed during training. Qwen2.5 1.5B has about 1.5 billion of them, Llama 2 70B about 70 billion. Most are arranged as large matrices, grids of numbers, stacked in **layers**: 28 layers in Qwen2.5 1.5B, each with several matrices.

Running the model means pushing the token's vector through every layer. At each layer, the vector is multiplied by the layer's matrices. A matrix times a vector is just many multiplications and additions, but it touches **every number in the matrix once**. So producing anything at all requires reading every weight once.

At 16 bits per weight, a 1.5 billion parameter model is about 3 GB. A 70 billion parameter model is about 140 GB. That is the amount of memory that has to be read, every time.

## Two phases: prefill and decode

When you send a prompt, the model works in two phases.

**Prefill** reads your whole prompt at once. If the prompt is 500 tokens, all 500 vectors go through the layers together. The weights are read once and used 500 times, which is efficient. Prefill ends with the model's first output token.

**Decode** writes the answer, **one token at a time**. Each new token depends on the one before it, so they cannot be computed together. For every single output token, the model reads all of its weights again and uses them once.

This is the most important fact in inference engineering. In note 1 we measured decode costing **20 to 35 times more energy per token than prefill** on the same machine, because prefill shares each read of the weights across many tokens and decode does not. Chat is mostly decode, so decode sets the bill.

## The KV cache

To write token 501, the model needs to look back at tokens 1 to 500 (that is what "attention" does). Recomputing all of them every time would be wasteful, so the model keeps a summary of each past token, the **key-value cache**, in memory. It grows with every token. For long conversations it can become as large as a small model's weights, and reading it costs memory traffic too.

## What to take from this

- A model is mostly large matrices of weights, and running it means multiplying through all of them.
- Prefill handles the prompt in one pass; decode writes the answer one token at a time and re-reads every weight for each token.
- That re-reading is why decode is slow and expensive, which is the subject of the next primer.

Measured in: [note 1](../research/formats-and-batching/) (prefill against decode).
