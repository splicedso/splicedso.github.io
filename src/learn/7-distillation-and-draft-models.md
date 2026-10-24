# Distillation: teaching a small model to imitate a big one

Primer 7. Builds on primer 5.

Speculative decoding (primer 5) is only as good as its draft model's guesses. A draft that agrees with the big model 70% of the time saves energy; one that agrees 30% of the time wastes it ([note 7](../research/speculative-decoding/)). So the obvious question is: can you make a small model guess better? That is what **distillation** does, and it is how our first model, the Spliced drafter, is being built.

## How a model is trained, in one paragraph

A model starts with random weights. Training shows it text and asks it to predict each next token. When it is wrong, a little arithmetic called **gradient descent** nudges every weight in the direction that would have made the right token more likely. Repeat over billions of tokens and the weights come to encode language. **Fine-tuning** is the same process started from an already trained model, on a much smaller, more specific set of text, to change what it does.

## The idea of distillation

Normally a model learns from text written by people. In distillation, a small "student" model learns from text written by a big "teacher" model. The student is not trying to be right about the world; it is trying to **write what the teacher would write**.

For a draft model, that is exactly the goal. The draft does not need to be a good model in general. It needs to predict one particular big model, as often as possible. A stock small model was trained on human text and so guesses the way people write; a distilled one guesses the way its teacher writes.

## What we are doing

1. **Collect prompts.** 3,600 varied requests, chat and code, from two public datasets (UltraChat, MIT licence; CodeAlpaca, CC-BY-4.0).
2. **Let the teacher answer.** Qwen2.5 7B writes an answer to every prompt, greedily, so the answers are exactly what it would produce. This is called sequence-level distillation.
3. **Fine-tune the student.** Qwen2.5 0.5B, the same small model notes 7 to 11 used as a draft, is trained on those answers. The prompt itself is masked out of the training signal, so the student learns only to reproduce the teacher's answers.
4. **Measure, held out.** On 80 prompts the student never saw, we compare the stock and the distilled drafter: how many of their guesses the 7B accepts, how much faster decoding gets, and how much energy each token costs.

Both drafters go through exactly the same conversion and quantization, so the only difference between them is the training.

## What could go wrong

- **Over-fitting.** A student trained too long memorizes its training answers and guesses worse on new prompts. That is why the evaluation uses held-out prompts, and why 5% of the training set is kept aside to watch the validation loss.
- **Narrow gains.** It may help on chat and code, which it trained on, and not on edits, where copying from the prompt already works.
- **No gain at all.** The stock model and the teacher come from the same family and already agree often. If the student does not beat the stock draft, the note will say so.

## Why a small lab can do this

Training a large model from scratch takes thousands of GPUs. Distilling a 0.5 billion parameter drafter takes a few thousand prompts, an hour of the teacher's time and an hour or two of fine-tuning, on one laptop. It is a small model built for one job, and the job comes straight out of our measurements.

Related: [note 7](../research/speculative-decoding/), [note 9](../research/speculative-threshold/), [note 11](../research/speculative-second-tool/). The drafter's own note will follow when the measurement is done.
