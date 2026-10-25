# Why serving many people at once is cheap

Primer 4. Builds on primer 2.

A datacenter GPU can serve a token for a fraction of the energy a laptop needs. Most of that difference is not the chip. It is **batching**.

## The idea

Decode reads every weight for every token (primer 1), and the reading is the slow part (primer 2). If eight people are waiting for their next token at the same moment, you can read each weight **once** and use it for all eight. The memory traffic barely changes; the useful work goes up eight times.

In matrix terms, one user means a matrix times a vector. Eight users means a matrix times eight vectors, a small matrix. The same bytes, eight times the arithmetic. Batching raises arithmetic intensity, which pushes decode up the roofline.

## What we measured

On the M5 Pro ([note 1](../research/formats-and-batching/)), serving 8 sequences at once instead of 1 cut energy per token by **72%**. But the savings were uneven: the second sequence saved only 1%, because at batch 1 the GPU was mostly idle, waiting on memory, and adding a second sequence woke it up to full power. After that, extra sequences were nearly free.

On the RTX 5070 Ti Laptop GPU ([note 10](../research/batching-without-a-step/)), the GPU already ran at full power with one sequence, so the second sequence saved 43% straight away. The total saving at batch 8 was similar, by a different route. **How a chip manages its power decides where batching pays off.**

## In the datacenter

A datacenter server does this at a much larger scale. In [note 8](../research/tokens-per-megawatt-hour/), an 8-GPU B200 server produced over 100,000 tokens per second on a 70 billion parameter model. The roofline says that reading the weights once per token, it could manage at most about 1,760. So it must be serving **at least 58 sequences at once** for every pass over the weights. That is most of why a token from a 70 billion parameter model on that server used about a tenth of the energy of a token from a 7 billion parameter model on our laptop, despite the model being ten times larger.

## The catch: waiting

Batching needs several requests ready at the same time. A server either waits briefly to gather them, which adds latency, or handles requests as they come, which keeps batches smaller. Real serving systems balance the two continuously ("continuous batching"). A laptop serving one person has nobody to batch with, which is the main reason it can never match a datacenter on energy per token, however good its chip.

Measured in: [note 1](../research/formats-and-batching/), [note 8](../research/tokens-per-megawatt-hour/), [note 10](../research/batching-without-a-step/).
