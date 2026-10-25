# When fewer bits pay, and when they do not

Primer 8. Builds on primer 3.

A 2-bit model reads half the bytes of a 4-bit one for every token. Reading bytes is most of what decoding costs (primer 2), so fewer bits should mean less energy per token. Our measurements say: sometimes. On a 1.5B model on a laptop chip a 2-bit token cost 13% more energy than a 4-bit one ([note 20](../research/lattice-v0/)). On a 7B it cost 18% more. On a 32B it cost 10% less, and the 2-bit model won per correct answer by 16% ([note 22](../research/lattice-large/)). This primer is about why the sign flips.

## Three costs in every token

A decoded token pays three bills. The chip reads every weight once, so the first bill is bytes moved from memory. The second is arithmetic: the weights are stored packed, and a 2-bit format has to be unpacked into numbers the math units can use, which is more work per weight than a 4-bit format needs ([note 5](../research/kernel-energy/) measured this unpacking cost directly). The third is everything the package draws regardless, the fans, the memory controller, the idle floor, charged per second and so per token.

Fewer bits shrink the first bill and grow the second. The third does not care about bits, only about time.

## Why the model's size decides

On a 1.5B model the weights are small. Reading them is quick, the unpacking is the same work per weight, and the fixed power ticks away either way. Halving a small bill while raising a larger one loses. On a 32B model the weights are twenty times bigger. Reading them is now most of the token, the unpacking is the same fraction it always was, and halving the big bill wins. Somewhere between 7B and 32B, on the machine we measured, the lines cross.

The machine matters too. A chip whose memory is fast relative to its arithmetic moves the crossover up; one that is memory-starved moves it down. That is why we measure instead of reasoning from a spec sheet.

## What it means in practice

For a small model on a laptop, 4 bits is the floor: going lower costs accuracy and saves nothing. For a large model, calibrated 2-bit is worth a measurement, because it may be cheaper per correct answer and not just per token. The accuracy half of that question is primer 3's: a calibrated 2-bit 32B lost nothing on our test, where a calibrated 2-bit 1.5B lost 24 points.

Related: [note 20](../research/lattice-v0/), [note 22](../research/lattice-large/), [note 5](../research/kernel-energy/). The models that come out of this are Lattice: [models](../models/).
