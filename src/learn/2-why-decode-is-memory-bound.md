# Why decoding is limited by memory, not arithmetic

Primer 2. Builds on primer 1.

A modern chip can do trillions of multiplications per second. A small model needs only a few billion per token. So why does a laptop write tokens at "only" 200 per second? Because the chip spends most of its time waiting for numbers to arrive from memory.

## Two speeds that matter

Every chip has two speed limits:

- **Compute**: how many arithmetic operations it can do per second. On a modern GPU, tens to thousands of trillions.
- **Memory bandwidth**: how many bytes per second it can read from memory. On the M5 Pro we measured about 307 GB/s ([note 5](../research/kernel-energy/)). A datacenter B200 GPU has about 7,700 GB/s.

A calculation is limited by whichever runs out first.

## Arithmetic intensity

The useful question is: **how many operations do you get to do per byte you read?** This is called arithmetic intensity.

In decode, each weight is read once and used for one multiply and one add: two operations. At 16 bits, a weight is 2 bytes. So decode does about **one operation per byte**. The chip can do hundreds of operations per byte in the time it takes to read it. It finishes the arithmetic almost instantly, then waits for the next bytes.

That makes decode **memory bound**. Its speed is set by bandwidth, not compute:

    fastest possible tokens per second = memory bandwidth / bytes read per token

## The roofline

Plotting "operations per second achieved" against "operations per byte" gives a picture called a **roofline**: a sloped line where memory limits you, and a flat roof where compute does. Decode sits far down the slope. Prefill, which reuses each weight for many tokens, climbs toward the roof.

In [note 2](../research/roofline-and-energy-model/) we used this to check our own measurements. A 16-bit Qwen2.5 1.5B model reads about 3.1 GB per token. At about 307 GB/s, the ceiling is roughly 100 tokens per second; it measured 84. The fact that decode tracks this ceiling so closely is the evidence that it is memory bound.

## Why this explains so much

Once decode is memory bound, several things follow:

- **Smaller weights decode faster.** Store each weight in 4 bits instead of 16 and there are four times fewer bytes to read. This is quantization, primer 3.
- **Serving several users at once is almost free.** Read each weight once and use it for many users' tokens. This is batching, primer 4.
- **Guessing ahead can help.** If a cheap model guesses the next few tokens, the big model can check them all in one read of its weights. This is speculative decoding, primer 5.

Almost every trick in inference engineering is a way around the memory wall.

## A caution we learned the hard way

Our first roofline was wrong. We measured bandwidth with a simple test, and one format then appeared to run faster than physics allowed. The data was right; the test underestimated the real bandwidth, and we had also counted bytes the model never reads per token. Note 2 keeps both mistakes in. The roofline is a tool for catching your own errors, not just a chart.

Measured in: [note 2](../research/roofline-and-energy-model/), [note 5](../research/kernel-energy/), [note 8](../research/tokens-per-megawatt-hour/).
