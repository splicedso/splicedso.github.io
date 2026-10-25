# How to measure energy without fooling yourself

Primer 6. The method behind every note.

Most published energy figures for AI disagree with each other, and usually not because anyone lied. They measured different things, or measured the right thing badly. These are the rules we learned, most of them by getting it wrong first.

## Power, energy and energy per token

- **Power** is a rate, in watts: how fast energy is being used right now.
- **Energy** is an amount, in joules: power multiplied by time. One watt for one second is one joule.
- **Energy per token** is the energy used divided by the tokens produced. Equivalently, average power divided by tokens per second.

That last identity is the core of every measurement here: measure average watts over a window, measure tokens per second over the same window, divide.

## Where you put the probe decides what you count

A "chip" reading and a "whole machine" reading are different quantities:

- On Apple silicon, the chip reading covers the processor but **not the memory**. Memory is a large part of decode's cost, so chip-only figures understated full-precision models by half ([note 1](../research/formats-and-batching/)).
- On an NVIDIA GPU, the GPU reading **includes the card's own memory** ([note 4](../research/two-machines/)).
- A datacenter figure "at the wall" includes the whole server but not the building's cooling, which is a further 9% to 56% on top ([note 8](../research/tokens-per-megawatt-hour/)).

Always state which point you measured. Never compare across points without saying so.

## Sensors are slow, and slowness is not neutral

Power sensors average over time. Our Mac's whole-board reading updates about once a second; the RTX machine's battery reading every few seconds. Three rules follow:

1. **Make the window long compared to the sensor.** One-second kernel runs disagreed by 40% between repeats; fifteen-second runs agreed within 2% ([note 5](../research/kernel-energy/)).
2. **Drop the edges.** The first part of a run includes the chip ramping up and the sensor catching up; we discard the first quarter.
3. **Watch for bias that tracks your variable.** In [note 7](../research/speculative-decoding/), faster methods had shorter windows, so a slow sensor read them low, flattering exactly the methods we were testing. A measurement error that grows with the thing you compare is a confound, not noise. We dropped that reading.

## Repeat, reverse, and report the spread

- Run every condition at least twice, the second time **in reverse order**, so slow drift (heat, background work) does not line up with any one condition.
- Report how far the repeats agree. If they do not agree, say so and report a range, as we did for MLX in [note 3](../research/scale-and-runtime/).
- Compare conditions within one session. Plain decoding drifted 9% to 11% between two sessions ([note 9](../research/speculative-threshold/)), so we compare ratios inside a run, not absolute values across runs.

## Models must make physical sense

When we fitted a model of energy to our data, it reported idle power of 110 W and a negative cost for moving data ([note 2](../research/roofline-and-energy-model/)). The fit looked good by the usual score. Both numbers were impossible. Two inputs moved together, so the fit could not tell them apart. **A good fit with impossible coefficients is a broken model.** Measure what you can directly, and fit only what the data can identify.

## Keep the mistakes

Every note keeps its wrong first attempts. They are usually the most useful part, and they are the evidence that the final result was checked.

The full standard is on the [methods page](../methods/).
