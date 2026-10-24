# How we measure

The rules every Spliced result follows. A note that breaks one says which, and why.

## 1. Say what was measured, and where

- Every energy figure names its measurement point: the chip, the GPU, the board's DC input, a battery's discharge, or a server at the wall. Figures measured at different points are never compared without saying so.
- Every note names the machine, the operating system, the runtime and its exact build, the model, the number format, and whether the machine was on AC or battery.
- Energy per token is mean power over a window divided by tokens per second over the same window. Prefill and decode are reported apart.

## 2. Windows long enough to trust

- A measurement window is long compared to the sensor that reads it: at least ten times the sensor's update interval, and at least fifteen seconds for whole-machine readings.
- The first quarter of every window is dropped for clock ramp and sensor lag.
- An idle baseline is taken before each session, after the machine has settled, so figures can be reported gross and net.

## 3. Repeat, and report the spread

- Every condition runs at least twice. The second pass runs in reverse order, so slow drift cannot line up with one condition.
- Every note reports how far the repeats agreed. Where they disagree beyond a few percent, the note reports ranges and makes only the claims that hold across all repeats.
- Conditions are compared within one session. Absolute values from different sessions are compared only with the drift between them stated.

## 4. Check for confounds

- A measurement error that grows with the variable being compared is a confound, not noise. When we find one, we drop the affected reading and say so.
- Bandwidth, byte counts and other inputs to a model are measured directly where possible, and checked against physical limits. A result that beats a physical limit means an input is wrong.

## 5. Models must make physical sense

- A fitted model is validated on data it was not fitted to (leave-one-out at least).
- A fitted coefficient that is physically impossible means the model cannot be identified from the data. We measure that term directly instead of reporting the fit.
- What a model cannot explain is reported as a finding, not hidden as error.

## 6. Publish everything

- The method, the scripts, every raw result file, including runs we discarded, and the reason, are public in [phase](https://github.com/splicedso/phase).
- Every number in a note can be traced to a results file. No number is stated that the results do not hold.
- Every figure on this site is drawn from those files at build time.

## 7. Keep the mistakes

- Wrong first attempts stay in the note, with what was wrong and how it was found. Corrections to earlier notes are made in the earlier note too, and say where they came from.

## 8. Credit where data comes from

- Data from others, such as MLPerf results, is cited to its source file, filtered by stated rules, and kept in our repository as extracted, so the selection can be checked.
