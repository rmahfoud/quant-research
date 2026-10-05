---
pagetitle: "Stochastic Processes"
description: "The formal definition of a stochastic process unpacked ingredient by ingredient, with a measure-theoretic appendix built from σ-algebras up."
keywords: ["stochastic processes", "probability theory", "measure theory", "filtration", "Brownian motion"]
author: "Robert Mahfoud"
lang: en
---

# Stochastic Processes

### The definition, unpacked ingredient by ingredient

---

```{=html}
<aside class="eli5">
```

# ELI5 — the short version {#eli5}

```{=latex}
\begin{eli5}
```

**In one sentence.** A stochastic process is a *random function*: one random draw picks out an entire history of values, past and future together, rather than a single number.

**1. The picture to hold** ([§6](#readings)). Picture many wiggly lines fanning out from one starting point. Each line is one possible history of a price. The process is the whole fan, together with the rule for how likely each line is. The fan can be read two ways. A vertical cut at one moment shows the spread of values the price might take at that moment. Following one line from left to right gives a single history, which is an ordinary curve with nothing random left in it.

**2. The randomness happens once** ([§6](#readings)). A computer simulation builds a path step by step: take a step, roll the dice, take another step. The definition works differently. One draw fixes the entire path at once, and nothing is rolled again later. The step-by-step loop is a way to produce that draw, not the definition of the process.

**3. Four ingredients** ([§1](#definition)). The definition needs four things: a source of randomness, a set of labels for the moments (usually times, but they can be places on a map), a set where the values land, and a rule that every question about the values is one that probability can answer. Familiar properties, such as "the future depends only on the present," are extra assumptions added on top of this definition.

**4. Every moment reads the same draw** ([§2](#probability-space)). The values at all times come from one shared draw. The shared draw is what distinguishes a process from a pile of random numbers produced by unconnected experiments. Because every moment reads the same draw, a combined event such as "low today and high next month" has a probability, and the theory can describe how one moment relates to another.

**5. Probability measures collections, not single outcomes** ([Section A](#app-a)). Pick a random number between 0 and 1. Each individual number has probability zero, yet some number always comes up. So probability cannot work by giving each outcome a weight and adding the weights. Instead it assigns sizes to collections of outcomes: "somewhere in the first quarter" has probability one quarter. Assigning sizes to collections is the subject of measure theory. Length, area, mass, and probability are one mathematical idea, and probability is the version in which the whole space has size one. One complication remains: for a number picked evenly between 0 and 1, no consistent rule can size every possible collection, so the theory lists in advance the collections it will size.

**6. Every question must have an answer** ([§5](#measurability)). The definition contains a condition that readers tend to skip. Mathematicians call it *measurability*. It says that each question about the values, such as "which histories put the price below 90?", must pick out one of the collections the theory sizes. If the condition fails, the probability that the price is below 90 is undefined. It is not zero, and it is not unknown.

**7. Snapshots define the process** ([§7](#fdd)). Nobody writes down the space of all histories. A model describes how the values behave jointly at any handful of times. Provided the descriptions for different handfuls agree with one another, a theorem guarantees that a process with exactly that behavior exists. The standard model of a random path, Brownian motion, is specified this way: it starts at zero, separate stretches are independent, and each stretch is bell-shaped. Snapshots at single moments are not enough, because two processes can look identical at every moment and still move together differently. Snapshots also do not settle whether a path is smooth or jumpy. That question needs its own proof.

**8. Lookahead bias has a formal definition** ([§8](#filtrations)). A *filtration* is the list of what is known at each moment, and the list only grows. A process is *adapted* when its value at each moment is known at that moment. Adaptedness is the backtesting rule in mathematical form. A signal that uses information not yet available at its timestamp could not have been traded, however good its results look.

---

**If you remember three things:** a process is one random function, not a sequence of separate rolls; the single shared source of randomness is what lets the theory describe how different moments relate; and the measurability condition is what makes the probabilities exist.

```{=latex}
\end{eli5}
```

```{=html}
</aside>
```

---

**How to read this document.** Part I (Sections 1–9) is the main text. Sections 1–5 unpack the formal definition of a stochastic process. The definition has four ingredients, and each one gets a section. Sections 6–8 cover how the definition is used: the two ways to read a process, the finite-dimensional distributions that identify it, and the filtration that almost every application adds. Section 9 runs five standard processes through the definition and collects the equivalences between its objects. Part II, the appendix (Sections A–K), builds the measure-theoretic vocabulary from scratch: $\sigma$-algebras, measurable spaces, measures, probability spaces, random variables, integration, conditioning, and product spaces. A reader who knows measure theory can skip Part II. A reader who does not can read it first, or consult it whenever Part I uses an unfamiliar term.

**Objectives.** After this chapter, you should be able to:

- state the definition of a stochastic process and name the job of each ingredient;
- read a process two ways, as a random variable at each time and as a random function of time;
- explain why measurability decides whether a probability exists at all;
- say what the finite-dimensional distributions determine about a process, and what they leave open;
- express "no lookahead" as adaptedness to a filtration, and check a backtest signal against it.

**Epistemic tags.** The chapters in this collection flag claims by status:

- **[Fact]** — replicated across independent datasets or implementations; broad agreement.
- **[Contested]** — documented, but with live disagreement about magnitude, robustness, or cause.
- **[Hypothesis]** — a proposed mechanism, not decisively tested.
- **[Practice]** — practitioner convention; the evidence may be private or absent. A [Practice] claim is not a debunked one.

This chapter is mathematics. Its definitions and theorems are facts by construction, so they carry no tag. The one tag that appears is [Practice], on conventions that textbooks assume rather than prove.

**Notation.** The table lists every symbol that recurs in the chapter, with the section that defines it. Symbols used in a single example are defined where they appear.

| Symbol | Meaning | Defined in |
|---|---|---|
| $(\Omega, \mathcal{F}, \mathbb{P})$ | Probability space: sample space, $\sigma$-algebra of events, probability measure | [§2](#probability-space) |
| $\omega$ | An outcome, one element of $\Omega$: a complete realization of everything random | [§2](#probability-space) |
| $T$; $s, t$; $n$ | Index set; indices in it (times, with $s \le t$ when ordered); an index in discrete time, or the number of times $t_1, \dots, t_n$ in [§7](#fdd) | [§3](#index-set) |
| $(E, \mathcal{E})$ | State space: the set of possible values, with its $\sigma$-algebra | [§4](#state-space) |
| $X = (X_t)_{t \in T}$ | The stochastic process; $X_t : \Omega \to E$ is its value at index $t$ | [§1](#definition) |
| $A$, $B$, $A_n$ | Measurable sets; in Part I, $B$ is a set of values: a member of $\mathcal{E}$, or in [§7](#fdd) a measurable subset of $E^n$ | [§5](#measurability), [B](#app-b) |
| $X_t^{-1}(B)$ | Preimage: the outcomes $\omega$ with $X_t(\omega) \in B$ | [§5](#measurability) |
| $E^T$ | Path space: all functions from $T$ to $E$, with the product $\sigma$-algebra | [§7](#fdd), [K](#app-k) |
| $\mu_{t_1 \dots t_n}$ | Finite-dimensional distribution: the joint law of $(X_{t_1}, \dots, X_{t_n})$ | [§7](#fdd) |
| $\mathcal{N}(m, v)$ | Normal distribution with mean $m$ and variance $v$ | [§7](#fdd) |
| $W_t$; $N_t$ | Brownian motion; a counting process, such as the Poisson process | [§7](#fdd), [§4](#state-space) |
| $(\mathcal{F}_t)_{t \in T}$; $\mathcal{F}_t^X$ | Filtration; natural filtration of $X$ | [§8](#filtrations) |
| $(U, \mathcal{U}, \mu)$, $(V, \mathcal{V}, \nu)$ | Generic measurable spaces with measures, used in Part II | [B](#app-b), [E](#app-e) |
| $2^U$ | Power set: every subset of $U$ | [B](#app-b) |
| $\sigma(\mathcal{C})$; $\sigma(X)$ | $\sigma$-algebra generated by a collection of sets $\mathcal{C}$; by a random variable $X$, or by a family such as $(X_s)_{s \le t}$ | [C](#app-c) |
| $\mathcal{B}(\mathbb{R})$ | Borel $\sigma$-algebra: generated by the open subsets of $\mathbb{R}$ | [C](#app-c) |
| $\lambda$; $\delta_x$ | Lebesgue measure (length); Dirac measure at the point $x$ | [E](#app-e) |
| a.s. | Almost surely: outside a set of probability zero | [F](#app-f) |
| $f$, $g$ | Generic measurable functions; in [H](#app-h), $f$ is a density | [G](#app-g) |
| $\mu_X$; $F_X$ | Law of $X$; its cumulative distribution function | [H](#app-h) |
| $\mu \ll \nu$ | $\mu$ is absolutely continuous with respect to $\nu$ | [H](#app-h) |
| $\mathbb{1}_A$; $\mathbb{1}\{\cdot\}$ | Indicator of $A$: equal to 1 on $A$ and 0 elsewhere; indicator of the condition in braces | [§7](#fdd), [I](#app-i) |
| $\mathbb{E}[X]$; $\mathbb{E}[X \mid \mathcal{G}]$ | Expectation; conditional expectation given a $\sigma$-algebra $\mathcal{G}$ | [I](#app-i), [J](#app-j) |
| $\mathbb{N}$; $\mathbb{N}_0$; $\mathbb{Z}$ | $\{1, 2, \dots\}$; $\{0, 1, 2, \dots\}$; the integers | — |

Two symbols need a warning. In this chapter, $\sigma$ appears only in the names "$\sigma$-algebra" and "$\sigma$-finite" and in the operator $\sigma(\cdot)$. It never denotes volatility, which this chapter does not use. And $\mathbb{E}$, in blackboard bold, is expectation, while the italic $E$ is the state space.

---

## Table of contents

- [ELI5 — the short version](#eli5)

**Part I — The definition**

1. [The definition](#definition)
2. [Ingredient I: the probability space $(\Omega, \mathcal{F}, \mathbb{P})$](#probability-space)
3. [Ingredient II: the index set $T$](#index-set)
4. [Ingredient III: the state space $(E, \mathcal{E})$](#state-space)
5. [Ingredient IV: measurability](#measurability)
6. [Two readings: slices and paths](#readings)
7. [Finite-dimensional distributions](#fdd)
8. [Filtrations and adaptedness](#filtrations)
9. [Instantiated](#instantiated)

**Part II — Appendix: the measure-theoretic vocabulary**

- [A. Why probability is a theory of sets](#app-a)
- [B. $\sigma$-algebras](#app-b)
- [C. Generation and Borel sets](#app-c)
- [D. Measurable space](#app-d)
- [E. Measure](#app-e)
- [F. Probability space](#app-f)
- [G. Measurable functions and random variables](#app-g)
- [H. Distributions](#app-h)
- [I. Integration and expectation](#app-i)
- [J. Independence and conditioning](#app-j)
- [K. Product spaces](#app-k)
- [Glossary](#glossary)
- [Further reading](#further-reading)

---

# Part I — The definition {#part-i}

## 1. The definition {#definition}

A stochastic process is a collection of random quantities, one for each index, all driven by the same source of randomness. The formal definition makes each part of that sentence precise.

Let $(\Omega, \mathcal{F}, \mathbb{P})$ be a probability space, let $(E, \mathcal{E})$ be a measurable space, and let $T$ be a non-empty set. A **stochastic process** with index set $T$ and state space $(E, \mathcal{E})$ is a family of maps

$$X = (X_t)_{t \in T}, \qquad X_t : \Omega \longrightarrow E,$$

such that each $X_t$ is $\mathcal{F}/\mathcal{E}$-measurable:

$$X_t^{-1}(B) \in \mathcal{F} \quad \text{for every } B \in \mathcal{E} \text{ and every } t \in T.$$

In words, each $X_t$ turns an outcome $\omega$ into a value in $E$. The measurability condition says that for every set of values $B$ the theory admits, the outcomes that land in $B$ form an event, so they have a probability.

An equivalent form is often more convenient. A stochastic process is a single map $X : T \times \Omega \to E$ such that $X(t, \cdot)$ is measurable for each fixed $t$. Fixing the first argument at $t$ recovers the map $X_t$ above.

The definition has four ingredients: three spaces and one condition on the maps between them. Sections 2–5 take them in order.

| Ingredient | Symbol | Job | Section |
|---|---|---|---|
| Probability space | $(\Omega, \mathcal{F}, \mathbb{P})$ | Holds the randomness | [§2](#probability-space) |
| Index set | $T$ | Labels the members of the family, usually by time | [§3](#index-set) |
| State space | $(E, \mathcal{E})$ | Holds the values, and fixes which sets of values can be asked about | [§4](#state-space) |
| Measurability | $X_t^{-1}(B) \in \mathcal{F}$ | Makes every probability about $X_t$ defined | [§5](#measurability) |

Three ideas run through the rest of the chapter, and every section returns to them:

1. **One draw fixes the whole path.** A single outcome $\omega$ determines $X_t(\omega)$ for every $t$ at once. A process is a random function, not a sequence of separate random draws.
2. **Every $X_t$ reads the same $\Omega$.** Because all the $X_t$ share one probability space, a joint event across times, such as "low today and high next month," has a probability. Dependence across time is defined through it.
3. **A $\sigma$-algebra is a list of answerable questions, and also a body of information.** Measurability makes $\mathbb{P}(X_t \in B)$ defined. A filtration, a growing family of $\sigma$-algebras, records what is known at each time.

---

## 2. Ingredient I: the probability space {#probability-space}

### $(\Omega, \mathcal{F}, \mathbb{P})$: where the randomness lives, drawn once

The probability space has three parts, and each has its own job.

| Object | Name | What it does |
|---|---|---|
| $\Omega$ | Sample space | The set of all possible outcomes. One outcome $\omega \in \Omega$ describes how everything turned out: the entire history, not the value at one moment. |
| $\mathcal{F}$ | $\sigma$-algebra | The subsets of $\Omega$ that count as events, meaning the subsets that receive a probability. It contains $\Omega$ and is closed under complement and countable union. |
| $\mathbb{P}$ | Probability measure | Assigns each event a number in $[0,1]$, with $\mathbb{P}(\Omega) = 1$. The probabilities of countably many disjoint events add up. |

$\mathcal{F}$ usually cannot contain every subset of $\Omega$. The uniform probability on $[0,1]$ shows why. It gives a set the same probability after the set is shifted along $[0,1]$, and no countably additive extension of it to every subset of $[0,1]$ keeps that property ([Section A](#app-a)). So $\mathcal{F}$ is deliberately smaller than the set of all subsets, and $\mathbb{P}$ answers questions only about members of $\mathcal{F}$.

> **Every $X_t$ is defined on the same $(\Omega, \mathcal{F}, \mathbb{P})$.** The shared space distinguishes a stochastic process from a collection of random variables defined on separate spaces.

Because the space is shared, a joint event such as $\{X_1 \le 3\} \cap \{X_5 > 7\}$ is a subset of the same $\Omega$. Each of the two sets is an event, because $X_1$ and $X_5$ are measurable ([§5](#measurability)), and $\mathcal{F}$ is closed under intersection. So the joint event belongs to $\mathcal{F}$ and has a probability. Dependence across time lives here. The correlation between $X_1$ and $X_5$, or the probability that a price falls and then recovers, describes how events in a single $\Omega$ overlap.

**Example: coin flips.** Let $\Omega = \{0, 1\}^{\mathbb{N}}$ be the set of all infinite sequences of coin flips, with 1 for heads and 0 for tails. Let $\mathbb{P}$ make the flips fair and independent. One outcome $\omega$ is an entire infinite sequence. Define $X_n(\omega)$ as the number of heads among the first $n$ flips of $\omega$. Nothing further is drawn. $X_{10}$ and $X_{11}$ are correlated because both read the same $\omega$ and share its first ten flips. Their correlation is $\sqrt{10/11} \approx 0.95$.

> ### §2 Key takeaways
>
> 1. One outcome $\omega$ is one complete history. Drawing $\omega$ once fixes the value of the process at every time.
> 2. All the $X_t$ live on the same probability space. Joint events across times are therefore events with probabilities, and dependence across time can be measured.
> 3. The $\sigma$-algebra $\mathcal{F}$ lists the subsets of $\Omega$ that receive a probability. In continuous models it is smaller than the set of all subsets, because some subsets cannot be given a consistent probability.

---

## 3. Ingredient II: the index set $T$ {#index-set}

### Usually time, but the definition never says so

$T$ is any set that labels the members of the family. The axioms say nothing about order, continuity, or time. Applications add those properties because the index is usually a clock.

The table lists the common choices.

| $T$ | Regime | Examples |
|---|---|---|
| $\{0, 1, 2, \dots\}$ | Discrete time | Daily closing prices, the steps of a Markov chain, the terms of a time series |
| $[0, \infty)$ | Continuous time | Brownian motion, the Poisson process, a diffusion |
| $\mathbb{R}^2$ or $\mathbb{Z}^2$ | Random field | Ore grade across a deposit, pixel noise, temperature over a map; the index is a location, not a time |
| $\{1, \dots, d\}$ | Finite | A random vector with $d$ components. A random vector *is* a stochastic process, and the general definition only widens $T$. |

> Most of the technical difficulty in the subject grows with the size of $T$. With $T$ countable, the definition causes no trouble. A statement about the whole path, such as "the path stays below 5," is a countable intersection of statements about single times, and $\sigma$-algebras are closed under countable operations. With $T$ uncountable, a statement such as "the path is continuous" constrains uncountably many values at once. Such a statement need not define an event, and continuous-time theory needs extra machinery to handle it ([§7](#fdd), [Section K](#app-k)).

> ### §3 Key takeaways
>
> 1. The index set $T$ can be any set. Time, order, and continuity come from the application, not from the definition.
> 2. A random vector is a process with a finite index set, and a random field is a process indexed by location.
> 3. A countable $T$ keeps every statement about the path inside the $\sigma$-algebra. An uncountable $T$ does not, and that gap drives most of the continuous-time machinery.

---

## 4. Ingredient III: the state space {#state-space}

### $(E, \mathcal{E})$: where the values land, and which sets of values can be asked about

The state space holds the values of the process. It must be a *measurable* space, not just a set. The $\sigma$-algebra $\mathcal{E}$ lists the sets of values $B$ for which "is $X_t$ in $B$?" is a question probability can answer.

The table lists the common choices.

| $(E, \mathcal{E})$ | Use |
|---|---|
| $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$ | The default: a real-valued process with the Borel $\sigma$-algebra, such as a price, a temperature, or a residual. |
| $(\mathbb{R}^d, \mathcal{B}(\mathbb{R}^d))$ | Vector-valued: a particle's position, or the yields at $d$ fixed maturities observed at one instant. |
| $(\{\text{sun}, \text{rain}\}, 2^E)$ | A finite state space with the power set, as in a two-state weather Markov chain. Because $E$ is finite, every subset can be measured and no subtlety arises. |
| $(\mathbb{N}_0, 2^{\mathbb{N}_0})$ | Counting processes: $N_t$ is the number of arrivals by time $t$. |

$E$ need not be numeric. It can be a space of functions, graphs, or measures, which gives function-valued or measure-valued processes. A whole yield curve that evolves over time is a function-valued process. The definition asks nothing of $E$ beyond the existence of $\mathcal{E}$.

> ### §4 Key takeaways
>
> 1. The state space must carry a $\sigma$-algebra. $\mathcal{E}$ fixes which sets of values a question about $X_t$ can name.
> 2. Real values default to the Borel $\sigma$-algebra; finite or countable values use the power set.
> 3. Values need not be numbers. A curve, a graph, or a measure works, provided $\mathcal{E}$ exists.

---

## 5. Ingredient IV: measurability {#measurability}

### The condition that makes the probabilities exist

Measurability says that every question about the value of $X_t$ translates into an event:

$$X_t^{-1}(B) = \{\, \omega \in \Omega : X_t(\omega) \in B \,\} \in \mathcal{F} \qquad \text{for all } B \in \mathcal{E}.$$

The left side is the **preimage** of $B$: the set of outcomes $\omega$ for which $X_t$ lands in $B$. The condition requires that set to be an event.

The condition matters because $\mathbb{P}$ is defined only on $\mathcal{F}$. The expression $\mathbb{P}(X_t \in B)$ is shorthand for $\mathbb{P}\big(X_t^{-1}(B)\big)$. If the preimage is not in $\mathcal{F}$, $\mathbb{P}$ has no value there, and $\mathbb{P}(X_t \in B)$ is undefined. It is not zero, and it is not unknown.

Measurability translates between two kinds of question. A question about values, such as "is the price below 90?", becomes a question about outcomes: "which $\omega$ produce a price below 90?" Measurability guarantees that $\mathbb{P}$ answers the second question.

**Measurable at each $t$ versus jointly measurable.** The definition requires each $X_t$ to be measurable on its own. That does not make the map $(t, \omega) \mapsto X_t(\omega)$ measurable on $T \times \Omega$. Joint measurability is a strictly stronger property. For an example, take $T = [0,1]$, let $V \subseteq [0,1]$ be a set that has no length ([Section A](#app-a)), and set $X_t(\omega) = 1$ if $t \in V$ and 0 otherwise. Each $X_t$ is constant in $\omega$, so it is measurable, yet no path can be integrated in $t$. A path integral such as $\int_0^1 X_t \, dt$ relies on the joint version, which makes every path a measurable function of $t$ and makes the integral a random variable. [Practice] Continuous-time texts usually assume joint measurability rather than derive it. A common route is to assume right-continuous paths, which imply it. [Section K](#app-k) defines the $\sigma$-algebra on $T \times \Omega$.

> ### §5 Key takeaways
>
> 1. $\mathbb{P}(X_t \in B)$ means $\mathbb{P}$ of the preimage $X_t^{-1}(B)$. Measurability guarantees the preimage is an event; without it, the probability is undefined.
> 2. Measurability is a precondition for every probability statement about the process, not a technicality.
> 3. Measurability at each $t$ is weaker than joint measurability in $(t, \omega)$. Integrals along a path rely on the joint version, which makes them random variables.

---

## 6. Two readings: slices and paths {#readings}

A process $X_t(\omega)$ has two arguments, $t$ and $\omega$. Fixing either one gives a different object, and both views are standard.

- **Fix $t$, vary $\omega$.** The result is $X_t(\cdot)$, a single random variable. It describes the value at time $t$ across all possible outcomes, and it has a distribution, a mean, and a variance. This chapter calls it the **slice** at $t$.
- **Fix $\omega$, vary $t$.** The result is $t \mapsto X_t(\omega)$, a **sample path**, or **path** for short. A path is an ordinary deterministic function of time.

> **A stochastic process is a random function.** $\Omega$ indexes the functions you might receive. $\mathcal{F}$ and $\mathbb{P}$ say how likely each collection of them is. Drawing one $\omega$ delivers one path, complete for all times at once.

Both readings appear in practice. A Monte Carlo simulation draws many outcomes and generates one path for each. A risk measure at a fixed horizon, such as a 10-day value at risk, reads a slice. A rule that depends on the route the price takes, such as a stop-loss, a drawdown limit, or a barrier option, reads whole paths.

The figure below shows both readings for a **simple random walk**: the walk starts at 0 and moves up or down by 1 at each step, with equal probability and independently across steps. Each faint line is one path, produced by one $\omega$ from the same $\Omega$. A vertical cut at a fixed $t$ crosses every path, and the spread of the crossing points is the distribution of the single random variable $X_t$, also called the **marginal** distribution at $t$. That spread has standard deviation $\sqrt{t}$. After 100 steps, the standard deviation is 10 steps, not 100.

```{=html}
<style>
.rw-fig {
  --rw-ink: #10171B; --rw-rose: #A63D62; --rw-teal: #0B6E75;
  --rw-faint: #8A979D; --rw-rule: #DCE4E6; --rw-muted: #58666E;
  margin: 1.6rem 0; padding: 1.2rem 0;
  border-top: 1px solid var(--rw-rule); border-bottom: 1px solid var(--rw-rule);
  display: flex; flex-direction: column; gap: 0.8rem;
}
@media (prefers-color-scheme: dark) {
  .rw-fig {
    --rw-ink: #E4ECEE; --rw-rose: #E895B0; --rw-teal: #5FCBD0;
    --rw-faint: #6C7C83; --rw-rule: #222E34; --rw-muted: #97A7AE;
  }
}
.rw-fig canvas { display: block; width: 100%; height: auto; }
.rw-controls {
  display: flex; flex-wrap: wrap; align-items: center; gap: 0.7rem 1.2rem;
  font-size: 0.8rem; color: var(--rw-muted);
}
.rw-controls label { display: flex; align-items: center; gap: 0.55rem; }
.rw-val { font-variant-numeric: tabular-nums; color: var(--rw-teal); font-weight: 700; min-width: 3.6rem; }
.rw-fig input[type="range"] {
  -webkit-appearance: none; appearance: none;
  width: clamp(7rem, 30vw, 13rem); height: 2px;
  background: var(--rw-rule); border-radius: 2px; outline: none;
}
.rw-fig input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none; width: 14px; height: 14px;
  border-radius: 50%; background: var(--rw-teal); cursor: pointer; border: none;
}
.rw-fig input[type="range"]::-moz-range-thumb {
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--rw-teal); cursor: pointer; border: none;
}
.rw-fig input[type="range"]:focus-visible { outline: 2px solid var(--rw-teal); outline-offset: 4px; }
.rw-fig button {
  font: inherit; font-size: 0.76rem; font-weight: 600;
  color: inherit; background: transparent;
  border: 1px solid var(--rw-rule); border-radius: 2px;
  padding: 0.35rem 0.7rem; cursor: pointer;
}
.rw-fig button:hover { border-color: var(--rw-rose); }
.rw-fig button:focus-visible { outline: 2px solid var(--rw-rose); outline-offset: 3px; }
.rw-legend { display: flex; flex-wrap: wrap; gap: 0.35rem 1.3rem; font-size: 0.76rem; color: var(--rw-muted); }
.rw-legend span { display: flex; align-items: center; gap: 0.45rem; }
.rw-legend i { width: 1.1rem; height: 2px; border-radius: 2px; display: inline-block; }
.rw-cap { font-size: 0.85rem; color: var(--rw-muted); max-width: 42em; }
</style>

<figure class="rw-fig">
  <div><canvas id="rw-canvas" aria-label="An ensemble of random-walk sample paths with a movable time slice showing the marginal distribution at that time."></canvas></div>
  <div class="rw-controls">
    <label for="rw-slider">Slice at t</label>
    <input id="rw-slider" type="range" min="4" max="180" value="96" step="1">
    <span class="rw-val" id="rw-val">t = 96</span>
    <button id="rw-reseed" type="button">Draw a new ensemble</button>
  </div>
  <div class="rw-legend">
    <span><i style="background:var(--rw-rose)"></i> one &omega; &mdash; a single sample path</span>
    <span><i style="background:var(--rw-teal)"></i> one t &mdash; the marginal of X<sub>t</sub></span>
    <span><i style="background:var(--rw-faint)"></i> &plusmn; &radic;t (one standard deviation)</span>
  </div>
  <figcaption class="rw-cap">A random walk on T = {0, 1, &hellip;, 180}. Every faint line is one &omega; from the same &Omega;. Move the slice to read the process the other way: the histogram is the distribution of the single random variable X<sub>t</sub>, spreading as &radic;t.</figcaption>
</figure>

<script>
(function () {
  var fig = document.querySelector(".rw-fig");
  var canvas = document.getElementById("rw-canvas");
  var ctx = canvas.getContext("2d");
  var slider = document.getElementById("rw-slider");
  var valOut = document.getElementById("rw-val");
  var STEPS = 180, NPATHS = 140, seed = 20260801, paths = [];

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function build(s) {
    var rnd = mulberry32(s);
    paths = [];
    for (var i = 0; i < NPATHS; i++) {
      var w = new Float64Array(STEPS + 1), v = 0;
      for (var n = 1; n <= STEPS; n++) { v += rnd() < 0.5 ? -1 : 1; w[n] = v; }
      paths.push(w);
    }
  }

  function cssVar(name) { return getComputedStyle(fig).getPropertyValue(name).trim(); }

  function draw() {
    var cssW = canvas.parentElement.clientWidth;
    if (!cssW) return;
    var cssH = Math.max(230, Math.min(340, Math.round(cssW * 0.44)));
    var dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssH * dpr);
    canvas.style.height = cssH + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cssW, cssH);

    var ink = cssVar("--rw-ink"), rose = cssVar("--rw-rose"), teal = cssVar("--rw-teal");
    var faint = cssVar("--rw-faint"), rule = cssVar("--rw-rule");
    var padL = 10, padR = 10, padT = 14, padB = 22;
    var plotW = cssW - padL - padR, plotH = cssH - padT - padB;
    var yMid = padT + plotH / 2;
    var yScale = (plotH / 2) / (3.5 * Math.sqrt(STEPS));
    var X = function (n) { return padL + (n / STEPS) * plotW; };
    var Y = function (v) { return yMid - v * yScale; };

    ctx.strokeStyle = rule; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(padL, yMid); ctx.lineTo(padL + plotW, yMid); ctx.stroke();

    ctx.strokeStyle = faint; ctx.globalAlpha = 0.6; ctx.setLineDash([3, 4]);
    [1, -1].forEach(function (sgn) {
      ctx.beginPath();
      for (var n = 0; n <= STEPS; n++) {
        var y = Y(sgn * Math.sqrt(n));
        if (n === 0) ctx.moveTo(X(n), y); else ctx.lineTo(X(n), y);
      }
      ctx.stroke();
    });
    ctx.setLineDash([]); ctx.globalAlpha = 1;

    ctx.strokeStyle = ink; ctx.lineWidth = 1; ctx.globalAlpha = 0.085;
    for (var i = 1; i < paths.length; i++) {
      ctx.beginPath();
      for (var n2 = 0; n2 <= STEPS; n2++) {
        var yy = Y(paths[i][n2]);
        if (n2 === 0) ctx.moveTo(X(n2), yy); else ctx.lineTo(X(n2), yy);
      }
      ctx.stroke();
    }
    ctx.globalAlpha = 1;

    var tSel = parseInt(slider.value, 10), xSel = X(tSel);
    var vals = paths.map(function (p) { return p[tSel]; });
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    var bins = 22, span = Math.max(hi - lo, 1), counts = new Array(bins).fill(0);
    vals.forEach(function (v) {
      counts[Math.min(bins - 1, Math.floor(((v - lo) / span) * bins))]++;
    });
    var maxC = Math.max.apply(null, counts);
    var histW = Math.min(78, plotW * 0.2), barH = (span * yScale) / bins;

    ctx.fillStyle = teal; ctx.globalAlpha = 0.28;
    for (var b = 0; b < bins; b++) {
      if (!counts[b]) continue;
      ctx.fillRect(xSel + 1, Y(lo + ((b + 1) / bins) * span), (counts[b] / maxC) * histW, Math.max(barH, 1.2));
    }
    ctx.globalAlpha = 1;

    ctx.strokeStyle = teal; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(xSel, padT); ctx.lineTo(xSel, padT + plotH); ctx.stroke();

    ctx.strokeStyle = rose; ctx.lineWidth = 1.9; ctx.lineJoin = "round";
    ctx.beginPath();
    for (var n3 = 0; n3 <= STEPS; n3++) {
      var y3 = Y(paths[0][n3]);
      if (n3 === 0) ctx.moveTo(X(n3), y3); else ctx.lineTo(X(n3), y3);
    }
    ctx.stroke();

    ctx.fillStyle = rose;
    ctx.beginPath(); ctx.arc(xSel, Y(paths[0][tSel]), 3.4, 0, Math.PI * 2); ctx.fill();

    ctx.fillStyle = faint; ctx.font = "11px system-ui, -apple-system, Helvetica, Arial, sans-serif";
    ctx.textAlign = "left"; ctx.fillText("t = 0", padL, cssH - 7);
    ctx.textAlign = "right"; ctx.fillText("t = " + STEPS, padL + plotW, cssH - 7);
  }

  slider.addEventListener("input", function () {
    valOut.textContent = "t = " + slider.value;
    draw();
  });
  document.getElementById("rw-reseed").addEventListener("click", function () {
    seed = (seed + 8677) | 0; build(seed); draw();
  });

  var lastW = -1;
  function onResize() {
    var w = canvas.parentElement.clientWidth;
    if (w === lastW) return;
    lastW = w; draw();
  }
  if (window.ResizeObserver) new ResizeObserver(onResize).observe(canvas.parentElement);
  else window.addEventListener("resize", onResize);

  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  if (mq.addEventListener) mq.addEventListener("change", draw);

  build(seed);
  draw();
})();
</script>
```

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/random_walk_ensemble.pdf}
\end{center}
```

> ### §6 Key takeaways
>
> 1. Fixing the time gives a random variable, the slice. Fixing the outcome gives a deterministic function of time, the path.
> 2. A process is a random function: one $\omega$ delivers one complete path.
> 3. Risk at a fixed horizon reads slices. Path-dependent rules and payoffs read paths, and a model can match every slice while getting the joint behavior across times wrong ([§7](#fdd)).

---

## 7. Finite-dimensional distributions {#fdd}

A process is identified by its **law**: the probability measure it induces on the **path space** $E^T$, the set of all functions from $T$ to $E$, equipped with the product $\sigma$-algebra of [Section K](#app-k). Formally, the law is the pushforward of $\mathbb{P}$ through the map $\omega \mapsto (X_t(\omega))_{t \in T}$, which sends each outcome to its path ([Section H](#app-h) defines pushforwards). In practice nobody specifies the law directly. A model instead states the joint distribution of the process at every finite set of distinct times $t_1, \dots, t_n \in T$:

$$\mu_{t_1 \dots t_n}(B) = \mathbb{P}\big((X_{t_1}, \dots, X_{t_n}) \in B\big) \qquad \text{for measurable } B \subseteq E^n.$$

Each $\mu_{t_1 \dots t_n}$ is an ordinary probability distribution on $E^n$: the joint distribution of $n$ snapshots of the process. The family of all of them, over every finite choice of times, is the process's **finite-dimensional distributions**.

The **Kolmogorov extension theorem** ([Kallenberg, 2021](https://doi.org/10.1007/978-3-030-61871-1){target="_blank"}) runs the other way. Start from a family of finite-dimensional distributions that is *consistent*, which means two things. First, dropping a time gives the smaller distribution:

$$\mu_{t_1 \dots t_n}(B \times E) = \mu_{t_1 \dots t_{n-1}}(B) \qquad \text{for measurable } B \subseteq E^{n-1}.$$

The left side places no condition on the value at $t_n$, so it must equal the distribution of the first $n - 1$ values. Second, listing the same times in a different order permutes the coordinates of the measure to match. Every process satisfies both conditions automatically, because all of its finite-dimensional distributions come from the same random variables. The theorem says the conditions are also sufficient. For state spaces such as $\mathbb{R}^d$, and more generally any complete separable metric space with its Borel $\sigma$-algebra, it guarantees a probability space and a process with exactly those finite-dimensional distributions.

The theorem is why Brownian motion can be defined by three properties, without ever writing down $\Omega$: $W_0 = 0$; increments over non-overlapping time intervals are independent; and $W_t - W_s \sim \mathcal{N}(0, t - s)$ for $s \le t$. These properties fix every finite-dimensional distribution. For times $t_1 < \dots < t_n$, each $W_{t_k}$ is a sum of independent normal increments, so the vector $(W_{t_1}, \dots, W_{t_n})$ is jointly normal with mean zero and covariance $\operatorname{Cov}(W_s, W_t) = \min(s, t)$. The resulting family is consistent, and the theorem supplies a process.

**Distributions at single times are not enough.** The finite-dimensional distributions include joint distributions across times, not only the distribution at each single time. To see the difference, let $Z$ be one standard normal draw and set $Y_t = \sqrt{t}\, Z$. At every $t$, $Y_t \sim \mathcal{N}(0, t)$, the same distribution as $W_t$. But every path of $Y$ is the same curve rescaled by one draw, so the correlation between $Y_1$ and $Y_4$ is 1. For Brownian motion, the covariance formula above gives a correlation between $W_1$ and $W_4$ of $1 / \sqrt{1 \cdot 4} = 0.5$. The two processes agree at every single time and disagree about every pair of distinct positive times. Derivatives pricing has the same gap. Vanilla option prices across all strikes at each expiry pin down the risk-neutral distribution of the asset price at that expiry, one expiry at a time. A barrier or forward-start option depends on the joint distribution across dates, so two models calibrated to the same vanilla prices can still disagree about its price.

**The finite-dimensional distributions do not determine path properties.** Two processes can share every finite-dimensional distribution while one has continuous paths and the other does not. For an example, let $T = [0,1]$, let $\tau$ be uniform on $[0,1]$, and compare the zero process with $J_t = \mathbb{1}\{t = \tau\}$, which equals 1 when $t = \tau$ and 0 otherwise. At each fixed $t$, $J_t$ differs from 0 only when $\tau = t$, which has probability zero. At any $n$ fixed times, the probability that $J$ is non-zero at one of them is at most a sum of $n$ zeros. So the two processes have the same finite-dimensional distributions. Yet every path of the zero process is continuous, and every path of $J$ jumps to 1 at the time $\tau$.

Processes that agree at each fixed $t$ with probability one are called **modifications** of each other. They can still differ in a property that involves uncountably many times at once, such as continuity of the path. A continuous modification therefore needs a separate argument, such as the Kolmogorov–Chentsov criterion, which produces one when the increments $X_t - X_s$ shrink fast enough, on average, as $s$ approaches $t$ ([Kallenberg, 2021](https://doi.org/10.1007/978-3-030-61871-1){target="_blank"}; [Çınlar, 2011](https://doi.org/10.1007/978-0-387-87859-1){target="_blank"}). [Section K](#app-k) explains why the finite-dimensional distributions cannot see path properties.

> ### §7 Key takeaways
>
> 1. A model specifies a process through its finite-dimensional distributions, the joint laws at every finite set of times. The Kolmogorov extension theorem turns a consistent family into a process.
> 2. Distributions at single times do not determine the finite-dimensional distributions. $\sqrt{t}\,Z$ and Brownian motion agree at every time and differ at every pair of distinct positive times.
> 3. The finite-dimensional distributions do not determine path properties such as continuity. Path regularity needs its own argument.

---

## 8. Filtrations and adaptedness {#filtrations}

The bare definition has no notion of information arriving over time. Almost every application adds one through a filtration.

When the index set $T$ is ordered, a **filtration** is a family of $\sigma$-algebras $(\mathcal{F}_t)_{t \in T}$ inside $\mathcal{F}$ that grows with time:

$$\mathcal{F}_s \subseteq \mathcal{F}_t \subseteq \mathcal{F} \qquad \text{for all } s \le t.$$

Read $\mathcal{F}_t$ as the events whose truth is settled by time $t$. The inclusion says that information is never lost: an event settled at time $s$ stays settled at every later time $t$. A probability space together with a filtration, $(\Omega, \mathcal{F}, (\mathcal{F}_t)_{t \in T}, \mathbb{P})$, is a **filtered probability space**. [Section B](#app-b) works through a small filtration in full.

A process is **adapted** to the filtration if $X_t$ is $\mathcal{F}_t$-measurable for every $t$, meaning $X_t^{-1}(B) \in \mathcal{F}_t$ for every $B \in \mathcal{E}$. Every question about the value at time $t$ is then settled by time $t$, so the value is known by time $t$. Every process is adapted to its own **natural filtration** $\mathcal{F}_t^X = \sigma(X_s : s \le t)$, the information revealed by observing $X$ up to time $t$. Here $\sigma(\cdot)$ denotes the smallest $\sigma$-algebra for which every listed random variable is measurable ([Section C](#app-c)). [Section G](#app-g) makes "known by time $t$" concrete: an $\mathcal{F}_t^X$-measurable quantity is a function of the observed values $X_s$ for $s \le t$.

Martingales, stopping times, and stochastic integrals are all built on adaptedness, because each one is a statement about not seeing the future. A **martingale** is an adapted process whose best forecast of any later value, given the information at time $s$, is its value at $s$ ([Section J](#app-j)). A **stopping time** is a random time whose arrival is known when it happens, such as the first time a price touches a barrier: the event that it has occurred by time $t$ belongs to $\mathcal{F}_t$. A **stochastic integral** accumulates the gains of a position that is chosen from the information available before each move of the price.

Adaptedness is also the formal version of the rule against lookahead bias in a backtest. A signal at time $t$ must be $\mathcal{F}_t$-measurable, where $\mathcal{F}_t$ is the information actually available at $t$. A signal computed from anything outside $\mathcal{F}_t$ could not have been known at time $t$, however good its backtest looks. Typical violations include a signal that uses a day's closing price to trade at that same close, fundamentals stamped with the fiscal period end rather than the release date, and a feature standardized with statistics from the full sample.

> ### §8 Key takeaways
>
> 1. A filtration is a growing family of $\sigma$-algebras. $\mathcal{F}_t$ holds the events settled by time $t$.
> 2. A process is adapted when its value at each time is known at that time. Martingales, stopping times, and stochastic integrals all require it.
> 3. Lookahead bias is a failure of adaptedness: a signal that is not measurable with respect to the information available at its timestamp.

```{=latex}
\newpage
```

## 9. Instantiated {#instantiated}

The table runs five standard processes through the definition. Each row names the sample space, the index set, and the state space, then the property that characterizes the process.

| Process | $\Omega$ | $T$ | $(E, \mathcal{E})$ | Character |
|---|---|---|---|---|
| Simple random walk | $\{-1, +1\}^{\mathbb{N}}$ | $\{0,1,2,\dots\}$ | $(\mathbb{Z}, 2^{\mathbb{Z}})$ | $X_n$ sums the first $n$ steps of $\omega$; increments independent |
| Brownian motion | $C([0,\infty), \mathbb{R})$ with Wiener measure | $[0,\infty)$ | $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$ | $W_0 = 0$; independent increments, $W_t - W_s \sim \mathcal{N}(0, t-s)$; continuous paths, almost surely nowhere differentiable |
| Poisson process | Increasing sequences of arrival times | $[0,\infty)$ | $(\mathbb{N}_0, 2^{\mathbb{N}_0})$ | $N_t$ counts arrivals; independent increments whose distribution depends only on the interval length; right-continuous paths, jumps of size 1 |
| Weather chain | $\{\text{sun},\text{rain}\}^{\mathbb{N}_0}$ | $\{0,1,2,\dots\}$ | $(\{\text{sun},\text{rain}\}, 2^E)$ | Markov: the next state depends only on the present state |
| i.i.d. noise | $\mathbb{R}^{\mathbb{Z}}$ with a product measure | $\mathbb{Z}$ | $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$ | No dependence at all, yet still a stochastic process |

In the Brownian row, $C([0,\infty), \mathbb{R})$ is the set of continuous functions from $[0,\infty)$ to $\mathbb{R}$, and Wiener measure is the law of Brownian motion on that set. In the last row, i.i.d. means independent and identically distributed.

The last row shows that the definition requires no dependence between the $X_t$. It also requires no common distribution and no meaningful order. Each named class of processes adds one such property, and its theorems follow from that addition: Markov chains add a rule for how the next state depends on the present one, and stationary processes add invariance under shifts in time.

### Equivalences

Several objects in this chapter have more than one description, and a few pairs that look alike are different. The table collects both kinds.

| Objects | Relationship | Section |
|---|---|---|
| A family $(X_t)_{t \in T}$; a single map on $T \times \Omega$; a random element of $E^T$ with the product $\sigma$-algebra | One process, three descriptions | [§1](#definition), [§7](#fdd), [K](#app-k) |
| A random vector in $\mathbb{R}^d$; a process with $T = \{1, \dots, d\}$ | The same object | [§3](#index-set) |
| A $\sigma$-algebra on a finite set; a partition of that set | Same information | [B](#app-b) |
| A $\sigma$-algebra; a list of answerable questions; an observer's information | One object, three readings | [B](#app-b) |
| $Y$ is $\sigma(X)$-measurable; $Y = g(X)$ for a measurable $g$ | Equivalent for real-valued $Y$ (Doob–Dynkin) | [G](#app-g) |
| Adapted to the available information; free of lookahead | Equivalent | [§8](#filtrations) |
| Law; distribution | Two names for $\mathbb{P} \circ X^{-1}$ | [H](#app-h) |
| Probability density function; probability mass function | One Radon–Nikodym density, against Lebesgue measure or against counting measure on a countable set | [H](#app-h) |
| $\mathbb{E}[X \mid \mathcal{G}]$ for square-integrable $X$; orthogonal projection onto square-integrable $\mathcal{G}$-measurable variables | Equal, up to a null set | [J](#app-j) |
| Measurable at each $t$; jointly measurable in $(t, \omega)$ | Different: joint is strictly stronger | [§5](#measurability) |
| Same distribution at each time; same finite-dimensional distributions | Different: the second is strictly stronger | [§7](#fdd) |
| Same finite-dimensional distributions; same path properties | Different: the first does not imply the second | [§7](#fdd), [K](#app-k) |

> ### Part I key takeaways
>
> 1. A process is a family of functions on $\Omega$, not a sequence of numbers. Numbers appear only after an outcome $\omega$ is drawn.
> 2. Randomness is resolved once. "Step forward, draw a shock, step again" is how a simulation constructs a path. In the definition, one $\omega$ fixes the whole path.
> 3. The shared probability space turns joint statements across times into events. Random variables on separate spaces have no joint distribution, so dependence between them is undefined.
> 4. Measurability decides whether $\mathbb{P}(X_t \in B)$ is defined at all.
> 5. The finite-dimensional distributions identify the law but not the path properties. Information enters through a filtration, and adaptedness is the formal ban on lookahead.

```{=latex}
\newpage
```

# Part II — Appendix: the measure-theoretic vocabulary {#part-ii}

Part II builds the vocabulary that Part I uses, starting from bare sets. Sections A–F build the container in steps: sets, $\sigma$-algebras, measurable spaces, measures, and probability spaces. Sections G–I describe what goes inside it: measurable functions, distributions, and expectation. Sections J and K cover independence, conditioning, and product spaces. A glossary follows.

Each entry starts with the idea in words, gives the formal definition, and then points back to the place in Part I that relies on it. For proofs, [Further reading](#further-reading) lists the standard texts in order of difficulty.

Part II uses $(U, \mathcal{U})$ and $(V, \mathcal{V})$ for generic measurable spaces, so that $X$ stays reserved for random variables and processes.

---

## A. Why probability is a theory of sets, not of points {#app-a}

The elementary definition of probability, favorable outcomes divided by total outcomes, needs finitely many equally likely outcomes. Its natural extension gives each outcome a weight and adds the weights, which works whenever the outcomes can be listed one by one. Both fail on a continuum. Drop a point uniformly on $[0,1]$. Each individual point has probability zero, yet the total probability is one, and no sum of zeros reaches one.

The fix assigns numbers to *sets* of outcomes. The event "the point lands in $[0, \tfrac14]$" has probability $\tfrac14$, with no contradiction. Assigning sizes to sets is the subject of measure theory, which studies consistent notions of size for the subsets of a space.

> Length, area, volume, mass, and probability are all **measures**. They differ only in normalization and interpretation. Probability is a measure with one extra requirement: the whole space has size 1. Every theorem about measures, integrals, and limits therefore applies to probability unchanged.

The complication is that sizes cannot be assigned to every subset. Vitali's construction produces subsets of $[0,1]$ that cannot be given a length: no countably additive, translation-invariant measure that gives $[0,1]$ length 1 extends to them. Translation-invariant means that shifting a set does not change its size.

The construction runs as follows. Call two numbers in $[0,1)$ equivalent when their difference is rational. The construction uses the axiom of choice to pick one number from each equivalence class. Shifting the chosen set by each rational in $[0,1)$, wrapping around at 1, gives countably many disjoint copies that together fill $[0,1)$. Translation invariance forces every copy to have the same length, and countable additivity then makes the total either 0 or infinite, never 1.

The theory keeps countable additivity, because limits depend on it, and gives up measuring every set. It fixes in advance a collection of sets it promises to measure. That collection is a $\sigma$-algebra ([Section B](#app-b)).

[§2](#probability-space) relies on this restriction: in continuous models, $\mathcal{F}$ is smaller than the set of all subsets.

---

## B. $\sigma$-algebras: the catalog of answerable questions {#app-b}

A $\sigma$-algebra is the list of subsets that a theory agrees to measure. The list must be closed under the operations that combine questions, so that combining answerable questions never produces an unanswerable one.

**Definition.** Let $U$ be a set. A collection $\mathcal{U}$ of subsets of $U$ is a **$\sigma$-algebra** on $U$ if:

  (i) $U \in \mathcal{U}$;
  (ii) $A \in \mathcal{U} \implies U \setminus A \in \mathcal{U}$ (closed under complement);
  (iii) $A_1, A_2, \dots \in \mathcal{U} \implies \bigcup_n A_n \in \mathcal{U}$ (closed under *countable* union).

Members of $\mathcal{U}$ are called **measurable sets**, and in probability they are called **events**. The $\sigma$ signals countability.

The three axioms imply more. Axioms (i) and (ii) give $\emptyset \in \mathcal{U}$. De Morgan's laws turn countable unions into countable intersections, so $\mathcal{U}$ is also closed under countable intersection and under set difference. The axioms are a minimal list: together they say that $\mathcal{U}$ is closed under every operation built from countably many of its sets.

### Reading one: the questions you can ask

Identify each subset $A \subseteq U$ with the yes-or-no question "is the outcome in $A$?" The axioms then become rules about questions. If $A$ can be asked, so can "not $A$." If $A_1, A_2, \dots$ can be asked, so can "at least one of them." A $\sigma$-algebra is a catalog of questions closed under these logical operations: any question built from countably many admissible questions is admissible.

The restriction to *countable* unions matters. Suppose the axioms allowed arbitrary unions, and suppose every single point is measurable, as it is in any reasonable model of a continuum. Every subset is the union of its points, so $\mathcal{U}$ would contain every subset. That is the power set, which [Section A](#app-a) showed cannot carry length. Countable unions are enough to take limits and few enough to exclude the pathological sets.

### Reading two: information

The second reading explains filtrations. Treat $\mathcal{U}$ as the resolving power of an observer: the collection of events whose truth the observer can determine. A coarse $\sigma$-algebra describes an observer who knows little, and a fine one describes an observer who knows more.

- $\{\emptyset, U\}$, the **trivial** $\sigma$-algebra, describes an observer who knows only that some outcome occurred. Every real-valued random variable measurable with respect to it is constant.
- $2^U$, the **power set**, describes total knowledge. It works for a countable $U$. On a continuum it is too large to carry length ([Section A](#app-a)).
- **The $\sigma$-algebra of a partition.** Split $U$ into blocks, and take all unions of blocks. The observer can tell which block occurred, but not which point inside the block. Every finite $\sigma$-algebra has this form, so on a finite set a $\sigma$-algebra and a partition carry the same information.

**Worked example: two coin flips.** Let $\Omega = \{\mathrm{HH}, \mathrm{HT}, \mathrm{TH}, \mathrm{TT}\}$. Before any flip, the observer cannot tell any outcomes apart. After the first flip, the observer knows which half contains the outcome. After the second flip, the observer knows the outcome.

```
F0    [ HH  HT  TH  TT ]                 knows nothing
F1    [ HH  HT ][ TH  TT ]               knows the first flip
F2    [ HH ][ HT ][ TH ][ TT ]           knows everything
```

The partition gets finer and the $\sigma$-algebra grows: $\mathcal{F}_0 \subset \mathcal{F}_1 \subset \mathcal{F}_2$. $\mathcal{F}_0$ contains two events, $\mathcal{F}_1$ contains four, and $\mathcal{F}_2$ contains all 16 subsets of $\Omega$. That increasing chain is a filtration ([§8](#filtrations)).

Part I uses both readings. The $\mathcal{F}$ of [§2](#probability-space) and the $\mathcal{E}$ of [§4](#state-space) are catalogs of answerable questions, and the filtration of [§8](#filtrations) is the information reading.

---

## C. Generation and Borel sets {#app-c}

On a continuum, nobody can list the measurable sets one by one. Instead, one names a few sets that must be measurable and takes the smallest $\sigma$-algebra that contains them.

**Definition: generated $\sigma$-algebra.** For any collection $\mathcal{C}$ of subsets of $U$, $\sigma(\mathcal{C})$ is the smallest $\sigma$-algebra that contains $\mathcal{C}$. Equivalently, it is the intersection of all $\sigma$-algebras that contain $\mathcal{C}$.

Two facts make the definition work. The power set is a $\sigma$-algebra that contains $\mathcal{C}$, so at least one such $\sigma$-algebra exists. And any intersection of $\sigma$-algebras is again a $\sigma$-algebra, because each axiom survives intersection. So the smallest one exists and is unique.

**Definition: Borel $\sigma$-algebra.** $\mathcal{B}(\mathbb{R}) = \sigma(\{\text{open subsets of } \mathbb{R}\})$. The open intervals generate the same $\sigma$-algebra, and so do the rays $(-\infty, a]$ with $a \in \mathbb{Q}$. The same construction defines the Borel $\sigma$-algebra of any topological space.

The Borel sets are the default answer to the question of which subsets of $\mathbb{R}$ to measure. They include every interval, every open set, every closed set, every countable set, and every set built from these by countable operations. Nearly every set that arises in modeling is Borel. Even so, the Borel sets are a small part of the power set. $\mathcal{B}(\mathbb{R})$ has the cardinality of the continuum, while $2^{\mathbb{R}}$ is strictly larger, so most subsets of $\mathbb{R}$ are not Borel.

> Generation also gives "information" a formal definition. For a random variable $X$ with values in $(E, \mathcal{E})$, the $\sigma$-algebra $\sigma(X) = \{X^{-1}(B) : B \in \mathcal{E}\}$ is the information carried by knowing $X$. The preimages already form a $\sigma$-algebra ([Section G](#app-g) shows why), and it is the smallest $\sigma$-algebra on $\Omega$ for which $X$ is measurable. For a family of random variables, the preimages of all of them together need not form a $\sigma$-algebra, so $\sigma(X_s : s \le t)$ is the $\sigma$-algebra they generate: the smallest one for which every $X_s$ with $s \le t$ is measurable. The natural filtration $\mathcal{F}_t^X = \sigma(X_s : s \le t)$ is the information gathered by observing the process up to time $t$ ([§8](#filtrations)).

The default state space of [§4](#state-space), $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$, uses the Borel $\sigma$-algebra.

---

## D. Measurable space: structure without numbers {#app-d}

A measurable space is a set together with its list of measurable subsets, before any sizes are assigned.

**Definition.** A **measurable space** is a pair $(U, \mathcal{U})$, where $U$ is a set and $\mathcal{U}$ is a $\sigma$-algebra on $U$.

The definition contains no numbers, sizes, or probabilities. A measurable space only declares which questions are legal. It plays the role of a type signature in code. It fixes the domain in advance, so that a measure added later knows exactly which sets it must evaluate.

Topology offers a useful parallel. A topological space is a set plus a chosen family of subsets, the open sets, which makes continuity expressible. A measurable space is a set plus a chosen family of subsets, the measurable sets, which makes measurement expressible. The construction is the same; the closure axioms and the purpose differ.

For this reason the definition of a stochastic process requires the state space to be a measurable space $(E, \mathcal{E})$ rather than a bare set $E$ ([§4](#state-space)). Without $\mathcal{E}$, there is no list of sets $B$ for which "$X_t \in B$" is a valid question.

---

## E. Measure: a consistent notion of size {#app-e}

A measure assigns a size to each measurable set, and the sizes of disjoint pieces add up to the size of the whole.

**Definition.** Given a measurable space $(U, \mathcal{U})$, a **measure** is a function $\mu : \mathcal{U} \to [0, \infty]$ with

  (i) $\mu(\emptyset) = 0$;
  (ii) $\mu\big(\bigcup_n A_n\big) = \sum_n \mu(A_n)$ for every sequence of *pairwise disjoint* $A_n \in \mathcal{U}$ (**countable additivity**).

The triple $(U, \mathcal{U}, \mu)$ is a **measure space**.

Countable additivity is the axiom that matters. Finite additivity, under which the sizes of finitely many disjoint pieces add up, is the obvious axiom, but it is too weak. Countable additivity gives **continuity of measure**: if $A_1 \subseteq A_2 \subseteq \cdots$ increase to $A$, then $\mu(A_n) \uparrow \mu(A)$. In words, the size of a limit is the limit of the sizes. The laws of large numbers, martingale convergence, and the construction of the integral all rest on this property.

Two consequences follow at once. **Monotonicity:** $A \subseteq B$ implies $\mu(A) \le \mu(B)$. **Countable subadditivity:** $\mu(\bigcup_n A_n) \le \sum_n \mu(A_n)$, with no disjointness required. Continuity also holds for decreasing sequences of sets, provided the first set has finite measure. Without that proviso it can fail: the rays $[n, \infty)$ all have infinite length, yet they decrease to the empty set.

The table lists four standard measures.

| Measure | Definition | Role |
|---|---|---|
| Counting measure | $\mu(A) = \#A$, the number of elements of $A$ | Turns integration into summation |
| Lebesgue $\lambda$ | On $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$, the unique translation-invariant measure with $\lambda([0,1]) = 1$ | Formalizes length; in $\mathbb{R}^d$, volume |
| Dirac $\delta_x$ | $\delta_x(A) = 1$ if $x \in A$, and 0 otherwise | Puts all the mass at one point |
| Probability | Any measure with $\mu(U) = 1$ | Normalization is its only distinguishing feature |

The probability measure $\mathbb{P}$ of [§2](#probability-space) is a measure of this kind.

---

## F. Probability space: a measure normalized to one {#app-f}

A probability space is a measure space whose total size is one, with the sizes read as probabilities.

**Definition.** A **probability space** is a measure space $(\Omega, \mathcal{F}, \mathbb{P})$ with $\mathbb{P}(\Omega) = 1$. In modern form, these are the axioms of [Kolmogorov (1933)](https://archive.org/details/kolmogorov_202112){target="_blank"}, who stated finite additivity plus a continuity axiom that together amount to countable additivity: $\mathbb{P}(A) \ge 0$ for all $A \in \mathcal{F}$; $\mathbb{P}(\Omega) = 1$; and $\mathbb{P}$ is countably additive over disjoint sequences.

The specialization adds a vocabulary and nothing else:

| Symbol | Name | Meaning |
|---|---|---|
| $\Omega$ | Sample space | The set of all possible complete outcomes |
| $\omega \in \Omega$ | Outcome | One fully specified way the world could turn out |
| $A \in \mathcal{F}$ | Event | A set of outcomes that receives a probability |
| $\mathbb{P}(A)$ | Probability | A number in $[0,1]$, by monotonicity and normalization |

Two terms follow directly and appear constantly. A **null set** is an event $A$ with $\mathbb{P}(A) = 0$. A statement holds **almost surely** (a.s.) if the outcomes where it fails lie inside a null set. In continuous models nearly every theorem is an almost-sure statement, because exceptional outcomes usually exist. The space of continuous paths that carries Brownian motion ([§9](#instantiated)) contains smooth paths, such as the constant path at zero. The theorem that Brownian paths are nowhere differentiable therefore cannot hold for every outcome. It shows instead that the outcomes where it fails, taken together, form a null set.

A related technicality concerns completeness. A measure space is **complete** if every subset of a null set is measurable, with measure zero. Nothing in the axioms forces completeness, but subsets of null sets are negligible for every practical purpose. [Practice] Probability spaces are conventionally completed. Continuous-time texts usually also assume that $\mathcal{F}_0$ contains every null set and that the filtration is right-continuous, meaning $\mathcal{F}_t = \bigcap_{u > t} \mathcal{F}_u$. Together these two assumptions are called the **usual conditions**. They ensure, for example, that changing an adapted process on a null set, as passing to a modification does ([§7](#fdd)), leaves it adapted.

### The build-up, in one table

The table summarizes the steps from a bare set to a probability space.

| Object | Name | What it adds |
|---|---|---|
| $U$ | A set | No structure. It says which elements exist and nothing else. |
| $(U, \mathcal{U})$ | Measurable space | A $\sigma$-algebra: which subsets are legal to ask about. Still no numbers. |
| $(U, \mathcal{U}, \mu)$ | Measure space | Sizes. Each legal subset gets a number in $[0,\infty]$, and the sizes add up consistently. |
| $(\Omega, \mathcal{F}, \mathbb{P})$, $\mathbb{P}(\Omega)=1$ | Probability space | The same structure, normalized. "Size" now reads as "how likely." |

Each step adds one thing and revises none of the earlier structure. Read upward, the table says that probability theory is a special case of measure theory, so every result about measures applies to it unchanged. The probability space is Ingredient I of the definition ([§2](#probability-space)).

---

## G. Measurable functions, and what a random variable actually is {#app-g}

A measurable function turns every legal question about its output into a legal question about its input. A random variable is such a function on a probability space.

**Definition.** A function $f : (U, \mathcal{U}) \to (V, \mathcal{V})$ is **measurable** if $f^{-1}(B) \in \mathcal{U}$ for every $B \in \mathcal{V}$. A **random variable** is a measurable function on a probability space.

A common first question is why the condition uses preimages rather than images. Preimages respect every set operation, and images do not. The identities

$$f^{-1}(B^c) = \big(f^{-1}(B)\big)^c, \qquad f^{-1}\Big(\bigcup_n B_n\Big) = \bigcup_n f^{-1}(B_n)$$

hold for every function $f$. The image version of the first one fails unless $f$ is both one-to-one and onto. If $f$ is constant, for example, the image of any non-empty set is the same single point, so the image of a complement is not the complement of the image. As a result, pulling a $\sigma$-algebra back through a function always gives a $\sigma$-algebra, while pushing one forward need not. Measurability is stated in the direction that preserves the structure.

The same fact gives a practical test. The collection $\{B \subseteq V : f^{-1}(B) \in \mathcal{U}\}$ is itself a $\sigma$-algebra. If it contains a generating family, it contains the whole $\sigma$-algebra that family generates. For a real-valued function, the rays generate $\mathcal{B}(\mathbb{R})$ ([Section C](#app-c)), so it is enough to check

$$\{f \le a\} = f^{-1}\big((-\infty, a]\big) \in \mathcal{U} \qquad \text{for every } a \in \mathbb{R}.$$

Borel measurability then follows. In practice, measurability rarely gets in the way. Every continuous function is Borel measurable. Measurable functions stay measurable under sums, products, composition with measurable maps, countable suprema and infima, and pointwise limits. Anything built by ordinary means stays measurable.

> The name *random variable* is historical and misleading. A random variable is a fixed, deterministic function $X : \Omega \to E$. The randomness lies entirely in which outcome $\omega$ is drawn. The name predates the measure-theoretic foundation, and it causes much of the early confusion in the subject.

**Doob–Dynkin lemma: information as computability.** [Section C](#app-c) called $\sigma(X)$ the information in $X$. The Doob–Dynkin lemma makes that statement exact. For a random variable $X$ with values in any measurable space $(E, \mathcal{E})$ and a real-valued $Y$, $Y$ is $\sigma(X)$-measurable if and only if $Y = g(X)$ for some measurable function $g : E \to \mathbb{R}$ ([Kallenberg, 2021](https://doi.org/10.1007/978-3-030-61871-1){target="_blank"}). Measurability with respect to the $\sigma$-algebra generated by $X$ means exactly "computable from $X$." To apply the lemma to the natural filtration, take $X$ to be the whole observed stretch of path $(X_s)_{s \le t}$. It is a random element of a path space, and the $\sigma$-algebra it generates is $\mathcal{F}_t^X$ ([Section K](#app-k)). So a real-valued $\mathcal{F}_t^X$-measurable quantity is a function of the observed values $X_s$ for $s \le t$. That is the precise sense of "known at time $t$" in [§8](#filtrations).

Part I treats each $X_t$ as a random variable in this sense ([§1](#definition), [§5](#measurability)).

---

## H. Distributions: pushing $\mathbb{P}$ forward, and forgetting $\Omega$ {#app-h}

A random variable carries the probability measure from $\Omega$ over to the state space.

**Definition: law, or pushforward.** The **law** of $X$, also called its **distribution**, is the measure $\mu_X = \mathbb{P} \circ X^{-1}$ on $(E, \mathcal{E})$:

$$\mu_X(B) = \mathbb{P}\big(X^{-1}(B)\big) = \mathbb{P}(X \in B).$$

The law gives each set of values $B$ the probability of the outcomes that land in it. Measurability of $X$ makes this well defined, and $\mu_X$ is again a probability measure.

The law discards everything about $\Omega$. Two random variables on completely different probability spaces can have the same law, and no statement about distributions can tell them apart. For example, a fair coin can be modeled on $\{0, 1\}$, or on $[0,1]$ with Lebesgue measure as $\mathbb{1}\{\omega \le \tfrac12\}$. The two models have the same law and serve every purpose that depends only on the law. Models rarely specify $\Omega$ explicitly for this reason. [§7](#fdd) applies the same idea to a whole process, whose law is a measure on the path space $E^T$.

On $\mathbb{R}$, the **cumulative distribution function** $F_X(a) = \mu_X((-\infty, a])$ encodes the law. The rays $(-\infty, a]$ generate $\mathcal{B}(\mathbb{R})$, and the intersection of two rays is again a ray; a family closed under intersection in this way is a **$\pi$-system**. A uniqueness theorem says that two probability measures that agree on a $\pi$-system agree on the whole $\sigma$-algebra it generates. So the CDF determines the law.

A density describes a law relative to a reference measure $\nu$ on $E$. Suppose $\nu$ is **$\sigma$-finite**, meaning $E$ is a countable union of sets of finite $\nu$-measure. Suppose also that $\mu_X$ is **absolutely continuous** with respect to $\nu$, written $\mu_X \ll \nu$: every $\nu$-null set is also $\mu_X$-null. The **Radon–Nikodym theorem** then supplies a density $f$ with

$$\mu_X(B) = \int_B f \, d\nu \qquad \text{for every } B \in \mathcal{E}.$$

The density converts the reference measure into the law, one set at a time ([Section I](#app-i) defines the integral). With $\nu$ equal to Lebesgue measure, $f$ is the probability density function. With $\nu$ equal to counting measure on a countable $E$, $f$ is the probability mass function. The countability matters, because counting measure is $\sigma$-finite only on a countable set. The textbook split between continuous and discrete random variables is a choice of reference measure, and the two theories are one theory with different $\nu$.

---

## I. Integration and expectation {#app-i}

The integral averages a function against a measure, and expectation is the integral against a probability measure. The Lebesgue integral is built in four stages. Each stage extends the previous one to a larger class of functions.

1. **Indicators.** The indicator $\mathbb{1}_A$ of a measurable set $A$ equals 1 on $A$ and 0 elsewhere, and $\int \mathbb{1}_A \, d\mu = \mu(A)$. Integrating an indicator returns the measure of its set.
2. **Simple functions.** A simple function is a finite combination $\varphi = \sum_i c_i \mathbb{1}_{A_i}$ of indicators of measurable sets $A_i$, with constants $c_i \ge 0$, and its integral is $\sum_i c_i \mu(A_i)$. One checks that the value does not depend on how $\varphi$ is written.
3. **Non-negative measurable $f$.** $\int f \, d\mu = \sup\{\int \varphi \, d\mu : \varphi \text{ simple}, \, 0 \le \varphi \le f\}$. The integral is the best approximation from below by simple functions, and it may be $+\infty$.
4. **General $f$.** Split $f = f^+ - f^-$ into its positive and negative parts, $f^+ = \max(f, 0)$ and $f^- = \max(-f, 0)$, and set $\int f \, d\mu = \int f^+ \, d\mu - \int f^- \, d\mu$. Both parts must be finite, which holds exactly when $\int |f| \, d\mu < \infty$.

An integral over a measurable set $A$ restricts the function to that set: $\int_A f \, d\mu = \int f \mathbb{1}_A \, d\mu$. [Section H](#app-h) and [Section J](#app-j) use this form.

**Expectation** is this integral with $\mu = \mathbb{P}$:

$$\mathbb{E}[X] = \int_\Omega X(\omega) \, \mathbb{P}(d\omega).$$

The expectation averages $X$ over outcomes, with $\mathbb{P}$ supplying the weights. As [Section A](#app-a) requires, the weights attach to sets of outcomes, through the simple functions of stage 2, rather than to single outcomes. The **change-of-variables formula** moves the computation from $\Omega$ to the state space, where the law lives:

$$\int_\Omega g(X) \, d\mathbb{P} = \int_E g \, d\mu_X.$$

It holds for every measurable $g : E \to \mathbb{R}$ that is non-negative or satisfies $\mathbb{E}|g(X)| < \infty$. The formula is why $\mathbb{E}[g(X)]$ can be computed from a density or a mass function alone, without reference to $\Omega$. When $\mu_X$ has density $f$ with respect to $\nu$ ([Section H](#app-h)), the right side becomes $\int_E g f \, d\nu$: the familiar $\int g(x) f(x) \, dx$ for Lebesgue measure, and the sum $\sum_x g(x) f(x)$ for counting measure. A Monte Carlo estimate approximates the left side directly: it averages $g(X(\omega))$ over many simulated outcomes. The mean of a slice in [§6](#readings) is an expectation in this sense.

> Lebesgue integration replaced Riemann integration because of limits. A pointwise limit of Riemann-integrable functions need not be Riemann integrable. The indicator of the rationals in $[0,1]$ is the pointwise limit of indicators of finite sets, each with Riemann integral zero, yet it has no Riemann integral; its Lebesgue integral is zero. Lebesgue's theory provides monotone convergence, for non-negative functions that increase to a limit, and dominated convergence, for functions bounded in absolute value by one integrable function. Each lets a limit and an integral be exchanged. Fatou's lemma covers other non-negative sequences with an inequality: the integral of the limit inferior is at most the limit inferior of the integrals. Probability works mostly with limits of sequences of random variables, and these theorems are the main reason its foundation moved to measure theory.

---

## J. Independence and conditioning {#app-j}

Independence says that learning one event does not change the probability of another. Conditioning says how to update an estimate when partial information arrives.

Events $A$ and $B$ are **independent** when $\mathbb{P}(A \cap B) = \mathbb{P}(A)\mathbb{P}(B)$. Two sub-$\sigma$-algebras $\mathcal{G}, \mathcal{H} \subseteq \mathcal{F}$ are independent when this holds for every $A \in \mathcal{G}$ and $B \in \mathcal{H}$. Random variables are independent when the $\sigma$-algebras they generate are independent.

Independence is a property of the measure, not of the sets. The same two events can be independent under one $\mathbb{P}$ and dependent under another. "The first flip is heads" and "the second flip is heads" are independent for fair, independent coins, and dependent under a measure in which the second flip tends to repeat the first.

Conditioning uses the information reading of $\sigma$-algebras ([Section B](#app-b)). Conditional expectation given a single event $A$ with $\mathbb{P}(A) > 0$ is elementary: $\mathbb{E}[X \mid A] = \mathbb{E}[X \mathbb{1}_A] / \mathbb{P}(A)$, the average of $X$ over $A$. The theory uses conditional expectation given a $\sigma$-algebra, which applies that idea to every event the $\sigma$-algebra resolves at once.

**Definition: conditional expectation.** For an integrable $X$ and a sub-$\sigma$-algebra $\mathcal{G} \subseteq \mathcal{F}$, $\mathbb{E}[X \mid \mathcal{G}]$ is *any* random variable $Z$ that is

  (i) $\mathcal{G}$-measurable, and
  (ii) satisfies $\int_G Z \, d\mathbb{P} = \int_G X \, d\mathbb{P}$ for every $G \in \mathcal{G}$.

Such a $Z$ exists and is unique up to a null set. The Radon–Nikodym theorem ([Section H](#app-h)) supplies it. For non-negative $X$, the map $G \mapsto \int_G X \, d\mathbb{P}$ is a measure on $\mathcal{G}$ that is absolutely continuous with respect to $\mathbb{P}$ restricted to $\mathcal{G}$. Its density is $\mathcal{G}$-measurable and satisfies clause (ii), so it is $Z$. A general $X$ is handled through its positive and negative parts.

The two clauses have plain meanings. Clause (i) says the answer may use only the information in $\mathcal{G}$. Clause (ii) says that on every event $\mathcal{G}$ can resolve, the answer has the same integral as $X$, so it gets the averages right at the available resolution. Together they make $\mathbb{E}[X \mid \mathcal{G}]$ the best estimate of $X$ that uses only what $\mathcal{G}$ knows. For a square-integrable $X$, meaning $\mathbb{E}[X^2] < \infty$, "best" has an exact meaning. Take the inner product of two square-integrable random variables to be the expectation of their product. $\mathbb{E}[X \mid \mathcal{G}]$ is then the orthogonal projection of $X$ onto the square-integrable $\mathcal{G}$-measurable random variables, so it has the smallest mean squared error among them.

In the two-coin example of [Section B](#app-b), let the flips be fair and independent, so each outcome has probability $\tfrac14$. Let $X$ be the number of heads and take $\mathcal{G} = \mathcal{F}_1$. On the block $\{\mathrm{HH}, \mathrm{HT}\}$, $X$ equals 2 or 1 with equal probability, so its average there is 1.5. On $\{\mathrm{TH}, \mathrm{TT}\}$ the average is 0.5. So $\mathbb{E}[X \mid \mathcal{F}_1]$ equals 1.5 on the outcomes where the first flip is heads and 0.5 where it is tails.

$\mathbb{E}[X \mid \mathcal{G}]$ is a random variable, not a number. It still depends on $\omega$, at the coarser resolution of $\mathcal{G}$; in the example, it takes one value on each block of the partition. That property lets the **martingale** condition describe a process. An adapted, integrable process is a martingale when

$$\mathbb{E}[X_t \mid \mathcal{F}_s] = X_s \qquad \text{for all } s \le t.$$

In words: given everything known at time $s$, the best forecast of the value at time $t$ is the value at time $s$. [§8](#filtrations) names martingales among the objects built on adaptedness.

---

## K. Product spaces {#app-k}

A product space puts two measurable spaces side by side. Given $(U, \mathcal{U}, \mu)$ and $(V, \mathcal{V}, \nu)$, the **product $\sigma$-algebra** $\mathcal{U} \otimes \mathcal{V}$ is the $\sigma$-algebra on $U \times V$ generated by the rectangles $A \times B$ with $A \in \mathcal{U}$ and $B \in \mathcal{V}$. When $\mu$ and $\nu$ are $\sigma$-finite, exactly one **product measure** $\mu \otimes \nu$ satisfies $(\mu \otimes \nu)(A \times B) = \mu(A)\nu(B)$. The **Fubini–Tonelli theorem** then permits swapping the order of a double integral: always for non-negative integrands, and for general integrands once the absolute value is integrable.

Part I relied on this construction in two places.

- **Joint measurability ([§5](#measurability)).** To call $(t, \omega) \mapsto X_t(\omega)$ measurable, $T \times \Omega$ needs a $\sigma$-algebra. The standard choice is the product of the Borel $\sigma$-algebra on $T$ with $\mathcal{F}$. Joint measurability lets Fubini–Tonelli exchange a time integral with an expectation, as in $\mathbb{E}\big[\int_0^1 X_t \, dt\big] = \int_0^1 \mathbb{E}[X_t] \, dt$, for non-negative $X$ or when $\mathbb{E}\big[\int_0^1 |X_t| \, dt\big] < \infty$. Occupation-time arguments, which measure how long a path spends in a set of values, need it. Stochastic integration needs it too, in a stronger form that also respects the filtration.
- **Path space ([§7](#fdd)).** The law of the whole process lives on $E^T$ with the product $\sigma$-algebra. This $\sigma$-algebra is generated by the **cylinder sets**: sets of paths that constrain the value at finitely many indices only, such as $\{x \in E^T : x(t_1) \in B_1, \dots, x(t_n) \in B_n\}$. A cylinder set is a finite intersection of sets of the form $\{x : x(t) \in B\}$, so the product $\sigma$-algebra is also the smallest one for which every coordinate map $x \mapsto x(t)$ is measurable. Two consequences follow. The map $\omega \mapsto (X_t(\omega))_{t \in T}$ is measurable exactly when every $X_t$ is, so a process is the same thing as a random element of $E^T$. And the $\sigma$-algebra that random element generates is $\sigma(X_t : t \in T)$.

> This construction explains both results of [§7](#fdd). The finite-dimensional distributions are exactly the probabilities of cylinder sets, and the cylinder sets generate the product $\sigma$-algebra. The intersection of two cylinder sets is again a cylinder set, so the cylinder sets form a $\pi$-system. By the uniqueness theorem of [Section H](#app-h), the finite-dimensional distributions therefore determine the law.
>
> Path properties escape for a related reason. Every event in the product $\sigma$-algebra depends on the path at only countably many indices. The sets with that property form a $\sigma$-algebra, because a countable union of countable index sets is countable, and that $\sigma$-algebra contains every cylinder set. So it contains the whole product $\sigma$-algebra. When $T$ is an interval, no countable set of indices can decide continuity: any countable set of values is consistent with both a continuous path and a discontinuous one. So the set of continuous paths is not in the product $\sigma$-algebra. "The process has continuous paths" is therefore not an event there. Continuity has to come from choosing a good modification, not from computing a probability.

```{=latex}
\newpage
```

## Glossary {#glossary}

| Symbol | Name | Read it as |
|---|---|---|
| $\Omega$ | Sample space | The set of complete outcomes; one $\omega$ is one whole history |
| $\mathcal{F}$ | $\sigma$-algebra | The events that receive a probability; equivalently, the information available |
| $\mathbb{P}$ | Probability measure | A countably additive size on $\mathcal{F}$, normalized so that $\mathbb{P}(\Omega) = 1$ |
| $(U, \mathcal{U})$ | Measurable space | A set plus its legal subsets; no numbers yet |
| $(U, \mathcal{U}, \mu)$ | Measure space | A measurable space plus sizes in $[0, \infty]$ |
| $\mathcal{B}(\mathbb{R})$ | Borel $\sigma$-algebra | Generated by the open sets; the default measurable subsets of $\mathbb{R}$ |
| $\sigma(\mathcal{C})$ | Generated $\sigma$-algebra | The smallest $\sigma$-algebra containing $\mathcal{C}$ |
| $\sigma(X)$ | $\sigma$-algebra of $X$ | $\{X^{-1}(B) : B \in \mathcal{E}\}$; the events settled by observing $X$ |
| $X : \Omega \to E$ | Random variable | A measurable function; deterministic, with $\omega$ the only thing that varies |
| $\mu_X = \mathbb{P} \circ X^{-1}$ | Law, or distribution | $\mathbb{P}$ pushed onto the state space; forgets $\Omega$ entirely |
| $\mathbb{E}[X] = \int X \, d\mathbb{P}$ | Expectation | The average over outcomes, weighted by probability |
| $\mathbb{E}[X \mid \mathcal{G}]$ | Conditional expectation | The best estimate of $X$ using only what $\mathcal{G}$ resolves; itself random |
| $(\mathcal{F}_t)_{t \in T}$ | Filtration | Information growing with time; $\mathcal{F}_s \subseteq \mathcal{F}_t$ for $s \le t$ |
| a.s. | Almost surely | True outside a set of probability zero |
| $\mu \ll \nu$ | Absolute continuity | Every $\nu$-null set is $\mu$-null; for $\sigma$-finite $\nu$, the condition for a density to exist |

---

## Further reading {#further-reading}

All of the material in this chapter is standard. The texts below supply the proofs, ordered roughly by how much measure theory they assume.

**The measure-theoretic foundation.**

- **Williams, D. (1991).** [*Probability with Martingales.*](https://doi.org/10.1017/CBO9780511813658) Cambridge University Press. — The gentlest serious entry point, and the one to read if Part II moved too fast. It builds $\sigma$-algebras, measure, integration, and conditional expectation in about a hundred pages, then spends the rest on discrete-time martingales.
- **Billingsley, P. (2012).** [*Probability and Measure*, Anniversary ed.](https://www.wiley.com/en-us/Probability+and+Measure,+Anniversary+Edition-p-9781118122372) Wiley. [[paywalled]] — The standard graduate reference for the measure theory itself. Slower and more complete than Williams, and the place to look for a construction rather than a statement.
- **Durrett, R. (2019).** [*Probability: Theory and Examples*, 5th ed.](https://sites.math.duke.edu/~rtd/PTE/pte.html) Cambridge University Press. — Covers the same ground, then continues into Brownian motion and martingales. The author posts the full text free, which makes it the most practical of the three to keep open while reading.

**Processes proper.**

- **Çınlar, E. (2011).** [*Probability and Stochastics.*](https://doi.org/10.1007/978-0-387-87859-1) Springer, Graduate Texts in Mathematics 261. [[paywalled]] — Written from the point of view of processes from the first page, rather than reaching processes after a measure-theory course. The closest match to how this chapter frames the definition.
- **Kallenberg, O. (2021).** [*Foundations of Modern Probability*, 3rd ed.](https://doi.org/10.1007/978-3-030-61871-1) Springer. [[paywalled]] — The comprehensive reference. Too terse for a first reading, and the right place to find the Kolmogorov extension theorem ([§7](#fdd)), the Kolmogorov–Chentsov continuity criterion, and the Doob–Dynkin lemma ([Section G](#app-g)) in their general forms.
- **Øksendal, B. (2003).** [*Stochastic Differential Equations: An Introduction with Applications*, 6th ed.](https://doi.org/10.1007/978-3-642-14394-6) Springer. [[paywalled]] — The next step once the objects here are in place: the Itô calculus built on them. Deliberately light on measure-theoretic detail, which suits a reader who has finished Part II.

**The historical source.**

- **Kolmogorov, A. N. (1933).** [*Grundbegriffe der Wahrscheinlichkeitsrechnung*](https://archive.org/details/kolmogorov_202112) (trans. *Foundations of the Theory of Probability*, Chelsea, 1956). Springer. — The monograph that made probability a branch of measure theory, and the source of the axioms in [Section F](#app-f). Short, and more readable than its reputation suggests.

**If you only read these.** Recommendation: [Williams (1991)](https://doi.org/10.1017/CBO9780511813658){target="_blank"} for the foundation, then [Çınlar (2011)](https://doi.org/10.1007/978-0-387-87859-1){target="_blank"} for processes. [Durrett (2019)](https://sites.math.duke.edu/~rtd/PTE/pte.html){target="_blank"} is the free alternative to both.

---

These documents were generated in whole or in part with the help of a large language model.
Dedicated to the public domain under the [CC0 1.0 Universal Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).

[Index](index.html) · [Source](https://github.com/rmahfoud/quant-research)
