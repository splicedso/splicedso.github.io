# What quantization is, and what Q4_0 means

Primer 3. Builds on primer 2.

Decode is limited by how many bytes it reads (primer 2). The most direct way to read fewer bytes is to store each weight in fewer bits. That is **quantization**.

## From 16 bits to 4

Weights are trained as 16-bit (or 32-bit) numbers. A 16-bit number can hold about 65,000 different values. Most models still work well if each weight is rounded to one of only 16 values, which needs just **4 bits**. The model shrinks to a quarter of the size and decodes nearly four times faster.

The trick is choosing which 16 values. Weights in one part of a matrix might range from -0.02 to 0.02, and in another from -1 to 1. One fixed set of 16 values would waste most of them.

## Blocks and scales

So formats split each matrix into small **blocks** and store, for each block, a **scale**: one extra number saying how big the values in that block are. Each weight is then a small integer that gets multiplied by its block's scale when the model runs.

That multiplication is **unpacking**, or dequantization. It happens every time a weight is used, on the chip, while the weights stream in from memory.

## Reading the names

The formats in our notes come from llama.cpp:

- **F16**: no quantization. 16 bits per weight, nothing to unpack.
- **Q8_0**: 8-bit integers, blocks of 32 weights, one scale per block. About 8.5 bits per weight once the scale is counted.
- **Q4_0**: 4-bit integers, blocks of 32, one scale per block. About 4.5 bits per weight. The simplest 4-bit format.
- **Q4_K, Q5_K, Q6_K, Q3_K, Q2_K**: the "K-quants". Small sub-blocks (16 or 32 weights) grouped into super-blocks of 256, with the sub-block scales themselves quantized and stored compactly, and in some formats a second set of minimums. More accurate for the bits, but more work to unpack.
- **_M** (as in Q4_K_M): a mix. Most layers use the named format and some sensitive ones use a higher-precision one.

Lower bits mean fewer bytes, more rounding error, and usually more unpacking work per byte.

## Quality: perplexity

Rounding loses information. We measure how much with **perplexity**: roughly, how surprised the model is by real text it has not seen, where lower is better. In [note 1](../research/formats-and-batching/), Qwen2.5 1.5B scored 9.63 at full precision, 10.09 at Q4_0 and 15.90 at Q2_K. Going to 4 bits cost a little; going to 2 bits broke the model.

## The surprise: fewer bits is not fewer joules

You would expect the 4-bit model to use a quarter of the energy. It does not. Unpacking costs energy, and that cost differs by format:

- In [note 1](../research/formats-and-batching/), Q5_K_M cost more energy per token than Q6_K, despite fewer bits.
- In [note 5](../research/kernel-energy/), Q4_0 and Q4_K store exactly the same number of bytes and run at the same speed, yet Q4_K's unpacking used 40% more energy on the chip.
- Across every note and both machines, Q4_0, the simplest 4-bit format, was the cheapest useful one.

The format name tells you the bits. It does not tell you the cost.

Measured in: [note 1](../research/formats-and-batching/), [note 5](../research/kernel-energy/), [note 6](../research/model-width/).
