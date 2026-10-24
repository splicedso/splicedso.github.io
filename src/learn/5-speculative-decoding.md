# How speculative decoding works

Primer 5. Builds on primers 1, 2 and 4.

A single user cannot batch with anyone else (primer 4). Speculative decoding is a way to get some of batching's benefit anyway, by batching your **own future tokens**.

## The idea

Keep two models: the large one you want answers from, and a small, fast **draft** model, say 15 times smaller. For each step:

1. The draft model quickly guesses the next few tokens, say 4.
2. The large model checks all 4 guesses in **one pass**, reading its weights once, the way it would for a batch.
3. It keeps the guesses it agrees with, up to the first one it would not have written, and adds one token of its own.

If the draft guessed 3 of 4 right, the large model produced 4 tokens for the price of one read of its weights. If it guessed none right, it produced 1 token, plus wasted work.

The output is identical to what the large model would have written alone. Speculative decoding changes the speed, never the answer.

## When it works

It depends on the **acceptance rate**: how often the large model agrees with the draft.

- Predictable text, like code or an edit that repeats most of its input, gets high acceptance. In [note 7](../research/speculative-decoding/), an edit task reached 97% to 100%.
- Open-ended prose gets low acceptance. The same note saw 14% with long drafts.

A variant needs no draft model at all: **n-gram drafting** guesses by copying text already in the prompt. For edits it was the best method we measured: 4.7 times faster than plain decoding at a third of the energy.

## Faster is not cheaper

Speculative decoding is sold as a speed-up, and it is measured that way. We measured energy too ([note 7](../research/speculative-decoding/)). It can be **faster and more expensive at the same time**: wrong guesses still cost the draft model's work and the large model's checking, and on a memory-bound chip that extra arithmetic hides in time but shows up in power. Drafting 16 tokens on prose cost almost four times the energy of plain decoding.

## The fix: stop guessing when unsure

The draft model knows how confident it is. A **threshold** (in llama.cpp, `--spec-draft-p-min`) makes it stop guessing when its confidence drops. In [note 9](../research/speculative-threshold/), a threshold around 0.5 removed the energy penalty on every task we tried, and made prose a free 1.3 times speed-up.

Measured in: [note 7](../research/speculative-decoding/), [note 9](../research/speculative-threshold/).
