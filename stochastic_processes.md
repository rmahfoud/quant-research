---
header-includes:
  - \usepackage{graphicx}
---

# Stochastic Processes

### The definition, unpacked ingredient by ingredient

---

**How to read this document.** Sections 1–5 unpack the formal definition of a stochastic process: four objects and one condition, each taken in turn. Sections 6–8 cover the machinery that identifies a process (finite-dimensional distributions, the Kolmogorov extension theorem) and the filtration that almost every application adds on top. The appendix, Sections A–K, builds the measure-theoretic vocabulary from scratch — $\sigma$-algebras, measurable spaces, measures, probability spaces, random variables, integration — for readers who want the foundations rather than the summary.

**Notation.** $(\Omega, \mathcal{F}, \mathbb{P})$ is a probability space, $\omega \in \Omega$ an outcome, $T$ an index set, $(E, \mathcal{E})$ a measurable state space. $\mathcal{B}(\mathbb{R})$ is the Borel $\sigma$-algebra, $\lambda$ Lebesgue measure, $\mu_X$ the law of $X$. $\mathbb{1}_A$ is the indicator of $A$, and a.s. abbreviates *almost surely*.

---

## Table of contents

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

---

# Part I — The definition {#part-i}

## 1. The definition {#definition}

Let $(\Omega, \mathcal{F}, \mathbb{P})$ be a probability space, let $(E, \mathcal{E})$ be a measurable space, and let $T$ be a non-empty set. A **stochastic process** with index set $T$ and state space $(E, \mathcal{E})$ is a family

$$X = (X_t)_{t \in T}, \qquad X_t : \Omega \longrightarrow E$$

of maps such that each $X_t$ is $\mathcal{F}/\mathcal{E}$-measurable — that is,

$$X_t^{-1}(B) \in \mathcal{F} \quad \text{for every } B \in \mathcal{E} \text{ and every } t \in T.$$

Equivalently, and sometimes more usefully: a stochastic process is a single map $X : T \times \Omega \to E$ such that $X(t, \cdot)$ is measurable for each fixed $t$.

Four objects and one condition. The rest of Part I takes them one at a time.

---

## 2. Ingredient I: the probability space {#probability-space}

### $(\Omega, \mathcal{F}, \mathbb{P})$ — where the randomness lives, and it is drawn only once

Three objects, each with a distinct job.

| Object | Name | What it does |
|---|---|---|
| $\Omega$ | Sample space | A single point $\omega \in \Omega$ is one complete description of how everything turned out — the entire history, all at once, not the value at one moment. |
| $\mathcal{F}$ | $\sigma$-algebra | The collection of subsets of $\Omega$ we are allowed to call events. Contains $\Omega$, closed under complement and countable union. |
| $\mathbb{P}$ | Probability measure | A map $\mathcal{F} \to [0,1]$ with $\mathbb{P}(\Omega) = 1$, countably additive over disjoint events. |

The subtlety in $\mathcal{F}$ is that it usually cannot be *all* subsets of $\Omega$. Once $\Omega$ is uncountable — as it is for anything in continuous time — there exist subsets to which no translation-invariant measure can consistently assign a probability. So $\mathcal{F}$ is deliberately smaller than the power set, and $\mathbb{P}$ is only ever asked about members of $\mathcal{F}$. (See [Section A](#app-a).)

> **The load-bearing word in the definition is *one*.** Every $X_t$ is defined on the *same* $(\Omega, \mathcal{F}, \mathbb{P})$. That single shared space is the entire difference between a stochastic process and an unrelated pile of random variables.

Because the space is shared, joint events like $\{X_1 \le 3\} \cap \{X_5 > 7\}$ are subsets of the same $\Omega$, live in $\mathcal{F}$, and therefore have probabilities. Dependence across time is expressible — which is the only reason the theory is interesting.

**Concretely.** Take $\Omega = \{H, T\}^{\mathbb{N}}$, the set of all infinite coin-flip sequences, with $\mathbb{P}$ the fair-coin measure. One $\omega$ is an entire infinite sequence, fixed the moment it is drawn. Define $X_n(\omega)$ = number of heads in the first $n$ flips of $\omega$. Nothing further is randomized: $X_{10}$ and $X_{11}$ are correlated automatically, because they read the same $\omega$.

---

## 3. Ingredient II: the index set $T$ {#index-set}

### Usually time, but the definition never says so

$T$ is just a set that labels the family. Nothing about ordering, continuity, or time appears in the axioms; those are conventions we impose because the label is normally a clock.

| $T$ | Regime | Examples |
|---|---|---|
| $\{0, 1, 2, \dots\}$ | Discrete time | Daily closing prices, steps of a Markov chain, terms of a time series |
| $[0, \infty)$ | Continuous time | Brownian motion, the Poisson process, a diffusion |
| $\mathbb{R}^2$ or $\mathbb{Z}^2$ | Random field | Ore grade across a deposit, pixel noise, temperature over a map — the index is space, not time |
| $\{1, \dots, d\}$ | Finite | Exactly a random vector. A random vector *is* a stochastic process; the general definition only widens $T$. |

> Nearly all the technical difficulty in the subject is a function of how big $T$ is. With $T$ countable, the definition is almost free. With $T$ uncountable, statements like "the path is continuous" involve uncountably many conditions at once and need not be measurable — which is why continuous-time theory carries so much machinery.

---

## 4. Ingredient III: the state space {#state-space}

### $(E, \mathcal{E})$ — where the values land, and which subsets of it we can ask about

The target has to be a *measurable* space, not merely a set: we need a $\sigma$-algebra $\mathcal{E}$ of subsets of $E$ so that questions like "is the value in $B$?" are the kind of question probability can answer.

| $(E, \mathcal{E})$ | Use |
|---|---|
| $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$ | The default. Real-valued process with the Borel $\sigma$-algebra — a price, a temperature, a residual. |
| $(\mathbb{R}^d, \mathcal{B}(\mathbb{R}^d))$ | Vector-valued: a particle's position, a whole yield curve observed at one instant. |
| $(\{\text{sun}, \text{rain}\}, 2^E)$ | A finite state space with the power set — the weather Markov chain. No measure-theoretic subtlety at all here. |
| $(\mathbb{N}_0, 2^{\mathbb{N}_0})$ | Counting processes: $N_t$ = number of arrivals by time $t$. |

$E$ need not be numeric. It can be a space of functions, of graphs, or of measures — giving function-valued or measure-valued processes. The definition is indifferent; only $\mathcal{E}$ has to exist.

---

## 5. Ingredient IV: measurability {#measurability}

### The clause that makes the probabilities exist

$$X_t^{-1}(B) = \{\, \omega \in \Omega : X_t(\omega) \in B \,\} \in \mathcal{F} \qquad \text{for all } B \in \mathcal{E}$$

This is the one part people skim, and it is the part that makes the rest legal. $\mathbb{P}$ only accepts arguments from $\mathcal{F}$. Measurability says: the set of outcomes for which $X_t$ lands in $B$ is one of the sets $\mathbb{P}$ can measure. Without it, the expression $\mathbb{P}(X_t \in B)$ is not false — it is *undefined*.

Read it as a translation between two worlds. A question about *values* ("is the price below 90?") is pulled back into a question about *outcomes* ("which $\omega$ produce that?"), and measurability guarantees the pulled-back question is one we already agreed to answer.

**A distinction worth keeping.** The definition demands measurability of $X_t$ for each $t$ separately. It does *not* follow that the map $(t, \omega) \mapsto X_t(\omega)$ is jointly measurable on $T \times \Omega$. Joint measurability is a strictly stronger property, and it is what you need before integrating along a path — so in continuous time it is usually assumed on top, not derived. (See [Section K](#app-k).)

---

## 6. Two readings: slices and paths {#readings}

The object has two free arguments. Fixing either one gives a completely different — and equally standard — mental picture.

- **Fix $t$, let $\omega$ vary.** You get $X_t(\cdot)$, a single random variable: a snapshot across the ensemble, with a distribution, a mean, a variance. This is the vertical slice.
- **Fix $\omega$, let $t$ vary.** You get $t \mapsto X_t(\omega)$, a **sample path** — one ordinary, fully deterministic function. This is the horizontal read.

> Which is why the honest one-sentence summary is: **a stochastic process is a random function.** $\Omega$ is the set of functions you might have been handed, $\mathcal{F}$ and $\mathbb{P}$ say how likely each collection of them is, and drawing a single $\omega$ hands you exactly one path — all of it at once, past and future together.

The picture to hold is an ensemble of sample paths fanning out from a common origin. Every line is one $\omega$ drawn from the same $\Omega$. Cut vertically at a fixed $t$ and the spread of crossing points *is* the distribution of the single random variable $X_t$ — for a random walk, widening as $\sqrt{t}$.

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
\includegraphics[width=\linewidth]{docs/figures/random_walk_ensemble.pdf}
\end{center}
```

---

## 7. Finite-dimensional distributions {#fdd}

The **law** of the process is the pushforward of $\mathbb{P}$ onto the path space $E^T$. In practice we never specify it directly; we specify the family of finite-dimensional distributions, for every finite set of indices $t_1, \dots, t_n \in T$:

$$\mu_{t_1 \dots t_n}(B) = \mathbb{P}\big((X_{t_1}, \dots, X_{t_n}) \in B\big).$$

The **Kolmogorov extension theorem** says the converse holds: given any family of finite-dimensional distributions that is *consistent* — marginalizing one index out of $\mu_{t_1 \dots t_n}$ reproduces the smaller one, and permuting indices permutes the measure — there *exists* a probability space and a process realizing them.

That theorem is why you can define Brownian motion by saying "$W_0 = 0$, increments are independent, and $W_t - W_s \sim \mathcal{N}(0, t - s)$" and never exhibit $\Omega$. Existence is delegated.

**What the finite-dimensional distributions do not pin down: path properties.** Two processes can share every finite-dimensional distribution while one has continuous paths and the other does not — they are *modifications* of each other, agreeing at each fixed $t$ almost surely, yet differing on an event that involves uncountably many $t$ at once. Continuous versions have to be produced separately, e.g. by the Kolmogorov–Chentsov criterion. [Section K](#app-k) explains why this gap is structural rather than accidental.

---

## 8. Filtrations and adaptedness {#filtrations}

The bare definition has no notion of information accumulating. Almost every applied use adds one. A **filtration** is an increasing family of sub-$\sigma$-algebras

$$\mathcal{F}_s \subseteq \mathcal{F}_t \subseteq \mathcal{F} \qquad \text{for all } s \le t,$$

with $\mathcal{F}_t$ read as "the events whose truth is settled by time $t$." The quadruple $(\Omega, \mathcal{F}, (\mathcal{F}_t)_{t \in T}, \mathbb{P})$ is a *filtered* probability space. A process is **adapted** if $X_t$ is $\mathcal{F}_t$-measurable for every $t$ — its value is known once time $t$ arrives. The smallest such choice is the natural filtration $\mathcal{F}_t^X = \sigma(X_s : s \le t)$.

Adaptedness is what makes martingales, stopping times, and stochastic integration expressible, since each is a statement about not seeing the future. It is also the formal statement of lookahead bias: a quantity computed from data that is not $\mathcal{F}_t$-measurable is precisely one you could not have known at time $t$, however plausible the backtest looks.

```{=latex}
\newpage
```

## 9. Instantiated {#instantiated}

The same four objects, five times over.

| Process | $\Omega$ | $T$ | $(E, \mathcal{E})$ | Character |
|---|---|---|---|---|
| Simple random walk | $\{-1, +1\}^{\mathbb{N}}$ | $\{0,1,2,\dots\}$ | $(\mathbb{Z}, 2^{\mathbb{Z}})$ | $S_n$ sums the first $n$ steps of $\omega$; increments independent |
| Brownian motion | $C([0,\infty), \mathbb{R})$ with Wiener measure | $[0,\infty)$ | $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$ | $W_t \sim \mathcal{N}(0,t)$; continuous paths, nowhere differentiable |
| Poisson process | Increasing arrival-time sequences | $[0,\infty)$ | $(\mathbb{N}_0, 2^{\mathbb{N}_0})$ | $N_t$ counts arrivals; right-continuous, jumps of size 1 |
| Weather chain | $\{\text{sun},\text{rain}\}^{\mathbb{N}}$ | $\{0,1,2,\dots\}$ | $(\{\text{sun},\text{rain}\}, 2^E)$ | Markov: the next state depends on the present one only |
| i.i.d. noise | $\mathbb{R}^{\mathbb{Z}}$ with a product measure | $\mathbb{Z}$ | $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$ | No dependence whatsoever — still a stochastic process |

Note the last row. Nothing in the definition requires the $X_t$ to be dependent, or identically distributed, or ordered in any meaningful way. Those are extra structure, imposed to get theorems.

### Four things the definition quietly settles

- A process is not a sequence of numbers. It is a family of *functions on $\Omega$*. The numbers appear only after an $\omega$ is drawn.
- Randomness is resolved once, not repeatedly. "Step forward, draw a shock, step again" is a construction recipe; in the definition the whole path is already determined by a single $\omega$.
- The shared probability space is what makes dependence across $T$ even statable. Drop it and there is no process, only a collection.
- Measurability is not bookkeeping. It is the condition under which $\mathbb{P}(X_t \in B)$ denotes anything at all.

```{=latex}
\newpage
```

# Part II — Appendix: the measure-theoretic vocabulary {#part-ii}

Everything Part I leaned on, built from the ground up. Sections A–F build the container: sets $\to$ $\sigma$-algebras $\to$ measurable spaces $\to$ measures $\to$ probability spaces. Sections G–I put things inside it: measurable functions, distributions, expectation. Sections J–K cover independence, conditioning, and product spaces. A glossary closes it out.

---

## A. Why probability is a theory of sets, not of points {#app-a}

The elementary definition — probability equals favourable outcomes over total outcomes — works only while you can count. Move to a continuum and it collapses immediately. Drop a point uniformly on $[0,1]$: every individual point has probability zero, there are uncountably many of them, and yet the total is one. Zero cannot be summed into one, so probability simply cannot be a function on outcomes.

The repair is to assign numbers to *sets* of outcomes rather than to outcomes. "The point lands in $[0, \tfrac14]$" has probability $\tfrac14$ with no paradox. And once you are assigning sizes to sets, you have walked into a subject that already existed: measure theory, the general study of how to attach a consistent notion of size to subsets of something.

> Length, area, volume, mass, charge and probability are the same mathematical object — a **measure** — differing only in normalization and interpretation. Probability is measure theory with the extra requirement that the whole space has size 1. That single constraint is the entire specialization; every theorem about integration and limits comes along for free.

The awkward part is that you cannot hand out sizes to *every* subset. Assuming the axiom of choice, there exist subsets of $[0,1]$ — Vitali's construction — that no translation-invariant, countably additive measure can consistently size. Rather than abandon countable additivity (which is what makes limits work), the theory abandons universality: we declare in advance a restricted collection of sets we promise to measure, and refuse the rest. That collection is the $\sigma$-algebra.

---

## B. $\sigma$-algebras: the catalogue of answerable questions {#app-b}

**Definition.** Let $X$ be a set. A collection $\mathcal{A}$ of subsets of $X$ is a **$\sigma$-algebra** on $X$ if:

  (i) $X \in \mathcal{A}$;
  (ii) $A \in \mathcal{A} \implies X \setminus A \in \mathcal{A}$ (closed under complement);
  (iii) $A_1, A_2, \dots \in \mathcal{A} \implies \bigcup_n A_n \in \mathcal{A}$ (closed under *countable* union).

Members of $\mathcal{A}$ are called **measurable sets**; in a probability context, **events**. The $\sigma$ is for countability.

From these three, $\emptyset \in \mathcal{A}$ follows from (i) and (ii), and closure under countable intersection follows via De Morgan, as does closure under set difference. So the axioms are minimal, not restrictive: what looks like three rules is really "closed under everything you can do with countably many sets."

### Reading one: what you are allowed to ask

Identify a subset $A \subseteq X$ with the yes/no question "is the outcome in $A$?" The axioms then say something very natural. If you can ask $A$, you can ask *not*-$A$. If you can ask $A_1, A_2, \dots$, you can ask *at least one of them*. A $\sigma$-algebra is a catalogue of questions closed under the logical operations, so that any question you can build from countably many admissible questions is itself admissible.

The restriction to *countable* unions is the load-bearing choice. Allow arbitrary unions and the theory dies instantly: every subset is a union of its singletons, so closure under arbitrary unions of singletons forces $\mathcal{A}$ to be the full power set — the very thing that cannot be measured. Countability is precisely the amount of closure needed to take limits without admitting the pathological sets.

### Reading two: information

The second reading is the one that makes filtrations obvious. Think of $\mathcal{A}$ as the resolving power of an observer: the events they can determine the truth of. A coarse $\sigma$-algebra is an observer who knows little; a fine one is an observer who knows more.

- $\{\emptyset, X\}$, the **trivial** $\sigma$-algebra: an observer who knows only that *something* happened. Every random variable measurable with respect to it is constant.
- $2^X$, the **power set**: total knowledge. Fine for countable $X$, unusable on a continuum.
- **$\sigma$ of a partition**: given a partition of $X$ into blocks, the $\sigma$-algebra of all unions of blocks. The observer can tell which block occurred but cannot distinguish points inside a block. Every finite $\sigma$-algebra is of this form — so on finite spaces, "$\sigma$-algebra" and "partition" are the same idea.

**Worked example — two coin flips.** Let $\Omega = \{HH, HT, TH, TT\}$. Before any flip you cannot distinguish outcomes at all. After the first flip you know which half you are in. After the second, everything:

```
F0    [ HH  HT  TH  TT ]                 knows nothing
F1    [ HH  HT ][ TH  TT ]               knows the first flip
F2    [ HH ][ HT ][ TH ][ TT ]           knows everything
```

The partition *refines*, the $\sigma$-algebra *grows* — $\mathcal{F}_0 \subset \mathcal{F}_1 \subset \mathcal{F}_2$ — and that increasing chain is exactly a filtration ([Section 8](#filtrations)).

---

## C. Generation and Borel sets {#app-c}

On a continuum you can never enumerate the measurable sets. Instead you name a few you insist on having and take the closure.

**Definition — generated $\sigma$-algebra.** For any collection $\mathcal{C}$ of subsets of $X$, $\sigma(\mathcal{C})$ is the smallest $\sigma$-algebra containing $\mathcal{C}$ — equivalently, the intersection of all $\sigma$-algebras containing $\mathcal{C}$.

That definition is legitimate for two reasons: the power set is always a $\sigma$-algebra containing $\mathcal{C}$, so the family being intersected is non-empty; and an arbitrary intersection of $\sigma$-algebras is again a $\sigma$-algebra, since each axiom is preserved under intersection. So a smallest one exists and is unique.

**Definition — Borel $\sigma$-algebra.** $\mathcal{B}(\mathbb{R}) = \sigma(\{\text{open subsets of } \mathbb{R}\})$. Equivalently, generated by the open intervals, or by the rays $(-\infty, a]$ for $a \in \mathbb{Q}$. More generally $\mathcal{B}(S)$ is defined for any topological space $S$.

The Borel sets are the default answer to "which subsets of $\mathbb{R}$ are we willing to measure." They contain every interval, every open and closed set, every countable set, every countable intersection of opens and union of closeds, and essentially everything you will ever write down. They are nonetheless a vanishingly small part of the power set: $\mathcal{B}(\mathbb{R})$ has the cardinality of the continuum, while $2^{\mathbb{R}}$ is strictly larger. Almost every subset of $\mathbb{R}$ is non-Borel — you just cannot exhibit one without the axiom of choice.

> The generation idea is also what gives "information" a formal home. For a random variable $X$, the $\sigma$-algebra $\sigma(X) = X^{-1}(\mathcal{E})$ is *the information carried by knowing $X$*, and the natural filtration $\mathcal{F}_t^X = \sigma(X_s : s \le t)$ is the information accumulated by observing the process up to time $t$.

---

## D. Measurable space: structure without numbers {#app-d}

**Definition.** A **measurable space** is a pair $(X, \mathcal{A})$ where $X$ is a set and $\mathcal{A}$ is a $\sigma$-algebra on $X$.

That is the whole definition, and the notable thing is what is absent: no numbers, no sizes, no probabilities. A measurable space only declares *which questions are legal*. It is the type signature before the implementation — the domain of discourse fixed in advance, so that when a measure arrives later it knows exactly what it is expected to evaluate.

The analogy worth carrying is with topology. A topological space is a set plus a distinguished family of subsets (the opens) that makes continuity expressible. A measurable space is a set plus a distinguished family of subsets (the measurable sets) that makes measurement expressible. Same move, different closure axioms, different purpose.

This is why the definition of a stochastic process requires the state space to be a measurable space $(E, \mathcal{E})$ and not merely a set $E$. Without $\mathcal{E}$ there is no way to state what "the value lands in $B$" is even allowed to mean.

---

## E. Measure: a consistent notion of size {#app-e}

**Definition.** Given $(X, \mathcal{A})$, a **measure** is a function $\mu : \mathcal{A} \to [0, \infty]$ with

  (i) $\mu(\emptyset) = 0$;
  (ii) $\mu\big(\bigcup_n A_n\big) = \sum_n \mu(A_n)$ for every sequence of *pairwise disjoint* $A_n \in \mathcal{A}$ (**countable additivity**).

The triple $(X, \mathcal{A}, \mu)$ is a **measure space**.

Countable additivity does all the work. Finite additivity alone — disjoint pieces of a set have sizes that add — would be the obvious axiom, and it is not enough. What countable additivity buys is **continuity of measure**: if $A_1 \subseteq A_2 \subseteq \cdots$ increase to $A$, then $\mu(A_n) \uparrow \mu(A)$. Sizes respect limits. Every limit theorem downstream — laws of large numbers, martingale convergence, the construction of the integral itself — reduces to that property.

Immediate consequences: monotonicity ($A \subseteq B \implies \mu(A) \le \mu(B)$) and countable subadditivity ($\mu(\bigcup A_n) \le \sum \mu(A_n)$, with no disjointness needed). Continuity from above holds too, but only for sets of finite measure.

| Measure | Definition | Role |
|---|---|---|
| Counting measure | $\mu(A) = \#A$ | Makes integration into summation |
| Lebesgue $\lambda$ | On $(\mathbb{R}, \mathcal{B}(\mathbb{R}))$, the unique translation-invariant measure with $\lambda([0,1]) = 1$ | Formalizes length; in $\mathbb{R}^d$, volume |
| Dirac $\delta_x$ | $\delta_x(A) = \mathbb{1}\{x \in A\}$ | All the mass at one point |
| Probability | Any measure with $\mu(X) = 1$ | Nothing else distinguishes it |

---

## F. Probability space: a measure normalized to one {#app-f}

**Definition.** A **probability space** is a measure space $(\Omega, \mathcal{F}, \mathbb{P})$ with $\mathbb{P}(\Omega) = 1$. Explicitly, Kolmogorov's 1933 axioms: $\mathbb{P}(A) \ge 0$ for all $A \in \mathcal{F}$; $\mathbb{P}(\Omega) = 1$; and $\mathbb{P}$ is countably additive on disjoint sequences.

The renaming that comes with it is the only real content of the specialization:

| Symbol | Name | Meaning |
|---|---|---|
| $\Omega$ | Sample space | The set of all possible complete outcomes |
| $\omega \in \Omega$ | Outcome / sample point | One fully specified way the world could turn out |
| $A \in \mathcal{F}$ | Event | A set of outcomes whose probability we have agreed to define |
| $\mathbb{P}(A)$ | Probability | A number in $[0,1]$, by monotonicity and normalization |

Two pieces of vocabulary follow directly and are used constantly. A **null set** is an $N \in \mathcal{F}$ with $\mathbb{P}(N) = 0$. A statement holds **almost surely** (a.s.) if the set where it fails is null. In continuous settings almost every theorem is an a.s. statement, because individual outcomes routinely have probability zero and cannot be excluded individually.

A related technicality: a measure space is **complete** if every subset of a null set is itself measurable (necessarily with measure 0). Nothing forces this, but subsets of null sets are morally negligible, so probability spaces are conventionally completed — and continuous-time theory usually assumes the filtration is completed too, as part of the "usual conditions."

### The build-up, in one table

| Object | Name | What it adds |
|---|---|---|
| $X$ | A set | No structure at all. You can say which elements exist and nothing else. |
| $(X, \mathcal{A})$ | Measurable space | A $\sigma$-algebra: which subsets are legal to ask about. Still no numbers. |
| $(X, \mathcal{A}, \mu)$ | Measure space | Sizes. Each legal subset now has a number in $[0,\infty]$, consistently additive. |
| $(\Omega, \mathcal{F}, \mathbb{P})$, $\mathbb{P}(\Omega)=1$ | Probability space | The same thing, normalized. "Size" is now read as "how likely." |

Each step adds exactly one thing, and none of the earlier structure is revised. Reading upward is also useful: probability theory is a special case, and every general measure-theoretic result applies to it unchanged.

---

## G. Measurable functions, and what a random variable actually is {#app-g}

**Definition.** $f : (X, \mathcal{A}) \to (Y, \mathcal{B})$ is **measurable** if $f^{-1}(B) \in \mathcal{A}$ for every $B \in \mathcal{B}$. A **random variable** is a measurable function on a probability space.

The first question everyone has is why the condition is stated on preimages rather than images. The answer is structural: preimages commute with every set operation, and images do not.

$$f^{-1}(B^c) = \big(f^{-1}(B)\big)^c, \qquad f^{-1}\Big(\bigcup_n B_n\Big) = \bigcup_n f^{-1}(B_n)$$

always hold. For images both can fail. So pulling a $\sigma$-algebra back through a function yields a $\sigma$-algebra; pushing one forward does not. Measurability has to be phrased in the direction that preserves the structure.

That same fact gives the practical test. The collection $\{B \subseteq Y : f^{-1}(B) \in \mathcal{A}\}$ is itself a $\sigma$-algebra, so if it contains a generating family it contains everything generated. For a real-valued function you therefore only need

$$\{f \le a\} = f^{-1}\big((-\infty, a]\big) \in \mathcal{A} \qquad \text{for every } a \in \mathbb{R},$$

and Borel measurability follows. This is why measurability is almost never an obstacle in practice: every continuous function is Borel measurable, and the measurable functions are closed under sums, products, compositions with measurable maps, suprema and infima of countable families, and pointwise limits. The class is stable enough that anything you construct by ordinary means stays inside it.

> A random variable is not a variable and it does not vary. It is a deterministic function $X : \Omega \to E$, fixed once and for all. The only thing that varies is which $\omega$ was drawn. The name is a historical accident from before the measure-theoretic foundation, and it is responsible for a large share of the confusion beginners have with the subject.

**Doob–Dynkin: information, made concrete.** The claim that $\sigma(X)$ "is the information in $X$" is not a metaphor. For real-valued $X$ and $Y$, the random variable $Y$ is $\sigma(X)$-measurable *if and only if* $Y = g(X)$ for some measurable $g$. Being measurable with respect to the $\sigma$-algebra generated by $X$ is exactly the same as being computable from $X$. Applied to a filtration: adapted means each $X_t$ is a function of what has already been observed.

---

## H. Distributions: pushing $\mathbb{P}$ forward, and forgetting $\Omega$ {#app-h}

A random variable transports the probability measure from $\Omega$ over to the state space.

**Definition — law / pushforward.** The **law** (or distribution) of $X$ is the measure $\mu_X = \mathbb{P} \circ X^{-1}$ on $(E, \mathcal{E})$, that is

$$\mu_X(B) = \mathbb{P}\big(X^{-1}(B)\big) = \mathbb{P}(X \in B).$$

Measurability of $X$ is precisely what makes this well defined, and $\mu_X$ is again a probability measure.

Note what the law throws away: everything about $\Omega$. Two random variables defined on completely different probability spaces can have identical laws, and no statement phrased in terms of distributions can tell them apart. This is the practical reason nobody specifies $\Omega$ — a fair coin flip modelled on $\{H, T\}$ and one modelled on $[0,1]$ with Lebesgue measure are indistinguishable for every purpose that only involves the law.

On $\mathbb{R}$ the law is encoded by the **cumulative distribution function** $F(a) = \mu_X((-\infty, a])$. Because the rays generate $\mathcal{B}(\mathbb{R})$ and form a $\pi$-system, agreeing on them forces agreement everywhere: the CDF determines the law completely.

Densities are the same story told against a reference measure. If $\mu_X$ is absolutely continuous with respect to a $\sigma$-finite $\nu$ — meaning $\nu(B) = 0$ forces $\mu_X(B) = 0$, written $\mu_X \ll \nu$ — the **Radon–Nikodym theorem** supplies a density $f$ with

$$\mu_X(B) = \int_B f \, d\nu.$$

Take $\nu$ = Lebesgue and $f$ is the probability density function; take $\nu$ = counting measure and $f$ is the probability mass function. The textbook split between "continuous" and "discrete" random variables is nothing more than a choice of reference measure, which is why the two theories are word-for-word identical.

---

## I. Integration and expectation {#app-i}

The Lebesgue integral is built in four stages, each extending the previous one.

1. **Indicators.** $\int \mathbb{1}_A \, d\mu = \mu(A)$. The integral *is* the measure, restated.
2. **Simple functions** — finite combinations $\sum_i c_i \mathbb{1}_{A_i}$ — integrate to $\sum_i c_i \mu(A_i)$, and one checks this does not depend on the representation.
3. **Non-negative measurable $f$:** $\int f \, d\mu = \sup\{\int s \, d\mu : s \text{ simple}, \, 0 \le s \le f\}$, allowed to be $+\infty$.
4. **General $f$:** split $f = f^+ - f^-$ and subtract, provided both parts are finite — that is, provided $\int |f| \, d\mu < \infty$.

Expectation is this integral with $\mu = \mathbb{P}$:

$$\mathbb{E}[X] = \int_\Omega X(\omega) \, \mathbb{P}(d\omega)$$

— an average over outcomes, each weighted by its probability. And the **change-of-variables** formula moves the computation to where the data actually lives:

$$\int_\Omega g(X) \, d\mathbb{P} = \int_E g \, d\mu_X,$$

which is why you can evaluate $\mathbb{E}[g(X)]$ from a density or a mass function alone and never think about $\Omega$ again.

> The reason to prefer Lebesgue over Riemann is not exotic sets — it is limits. Riemann integration is not closed under pointwise limits: a pointwise limit of Riemann-integrable functions need not be Riemann integrable. Lebesgue's theory supports monotone convergence, Fatou's lemma, and dominated convergence, each letting you exchange a limit with an integral under weak hypotheses. Since probability is almost entirely about limits of sequences of random variables, this is not a refinement — it is the reason the foundation was rebuilt.

---

## J. Independence and conditioning {#app-j}

Events $A, B$ are **independent** when $\mathbb{P}(A \cap B) = \mathbb{P}(A)\mathbb{P}(B)$. Sub-$\sigma$-algebras $\mathcal{G}, \mathcal{H} \subseteq \mathcal{F}$ are independent when that holds for every $A \in \mathcal{G}$ and $B \in \mathcal{H}$, and random variables are independent when the $\sigma$-algebras they generate are. Note that independence is a property of the *measure*, not of the sets: the same two events can be independent under one $\mathbb{P}$ and dependent under another. It is a numerical coincidence promoted to a definition, not a structural feature.

Conditioning is where the information reading earns its keep. Conditional expectation given an event is elementary; conditional expectation given a $\sigma$-algebra is the object the theory actually uses.

**Definition — conditional expectation.** For integrable $X$ and a sub-$\sigma$-algebra $\mathcal{G} \subseteq \mathcal{F}$, $\mathbb{E}[X \mid \mathcal{G}]$ is *any* random variable $Z$ that is

  (i) $\mathcal{G}$-measurable, and
  (ii) satisfies $\int_G Z \, d\mathbb{P} = \int_G X \, d\mathbb{P}$ for every $G \in \mathcal{G}$.

Such a $Z$ exists and is unique up to a null set, by Radon–Nikodym.

Read the two clauses. The first says the answer may only use information available in $\mathcal{G}$ — you are not allowed to peek. The second says that on every set $\mathcal{G}$ can resolve, the answer has the same total mass as $X$ itself — it gets the averages right at the resolution available. Together: $\mathbb{E}[X \mid \mathcal{G}]$ is the best estimate of $X$ using only what $\mathcal{G}$ knows. For square-integrable $X$ this is literally an orthogonal projection onto the subspace of $\mathcal{G}$-measurable functions.

Note that $\mathbb{E}[X \mid \mathcal{G}]$ is a random variable, not a number — it still depends on $\omega$, just at coarser resolution. That is what makes the **martingale** condition

$$\mathbb{E}[X_t \mid \mathcal{F}_s] = X_s \qquad (s \le t)$$

a statement about processes: given everything known at time $s$, the best forecast of the future value is the present one.

---

## K. Product spaces {#app-k}

Given $(X, \mathcal{A}, \mu)$ and $(Y, \mathcal{B}, \nu)$, the **product $\sigma$-algebra** $\mathcal{A} \otimes \mathcal{B}$ is generated by the rectangles $A \times B$, and for $\sigma$-finite measures there is a unique product measure with $(\mu \otimes \nu)(A \times B) = \mu(A)\nu(B)$. **Fubini–Tonelli** then licenses swapping the order of a double integral — for non-negative integrands unconditionally, and in general once absolute integrability holds.

Two places in Part I quietly depended on this construction.

- **Joint measurability.** Saying $(t, \omega) \mapsto X_t(\omega)$ is measurable requires a $\sigma$-algebra on $T \times \Omega$, and the product $\sigma$-algebra is it. Only then can you integrate along a path, which is what stochastic integration and occupation-time arguments need.
- **Path space.** The law of the whole process lives on $E^T$ with the product $\sigma$-algebra, generated by **cylinder sets** — sets that constrain the path at finitely many indices only.

> This is the technical reason the finite-dimensional distributions determine the law: the fdds are exactly the measures of cylinder sets, and cylinders generate the product $\sigma$-algebra. It is also the reason path properties escape. The set of continuous paths constrains uncountably many coordinates at once and is *not* in the product $\sigma$-algebra — so "the process has continuous paths" is not an event there, and continuity has to be obtained by choosing a good modification rather than by computing a probability.

```{=latex}
\newpage
```

## Glossary {#glossary}

| Symbol | Name | Read it as |
|---|---|---|
| $\Omega$ | Sample space | The set of complete outcomes; one $\omega$ is one whole history |
| $\mathcal{F}$ | $\sigma$-algebra | The events we may assign probability to — equivalently, the information available |
| $\mathbb{P}$ | Probability measure | Countably additive size on $\mathcal{F}$, normalized so $\mathbb{P}(\Omega) = 1$ |
| $(X, \mathcal{A})$ | Measurable space | A set plus its legal subsets; no numbers yet |
| $(X, \mathcal{A}, \mu)$ | Measure space | The above, plus sizes in $[0, \infty]$ |
| $\mathcal{B}(\mathbb{R})$ | Borel $\sigma$-algebra | Generated by the open sets — the default measurable subsets of $\mathbb{R}$ |
| $\sigma(\mathcal{C})$ | Generated $\sigma$-algebra | Smallest $\sigma$-algebra containing $\mathcal{C}$ |
| $\sigma(X)$ | $\sigma$-algebra of $X$ | $X^{-1}(\mathcal{E})$ — everything computable from observing $X$ |
| $X : \Omega \to E$ | Random variable | A measurable function; deterministic, with $\omega$ the only thing that varies |
| $\mu_X = \mathbb{P} \circ X^{-1}$ | Law / distribution | $\mathbb{P}$ pushed onto the state space; forgets $\Omega$ entirely |
| $\mathbb{E}[X] = \int X \, d\mathbb{P}$ | Expectation | Average over outcomes weighted by probability |
| $\mathbb{E}[X \mid \mathcal{G}]$ | Conditional expectation | Best estimate of $X$ using only what $\mathcal{G}$ resolves; itself random |
| $(\mathcal{F}_t)_{t \in T}$ | Filtration | Information increasing with time; $\mathcal{F}_s \subseteq \mathcal{F}_t$ for $s \le t$ |
| a.s. | Almost surely | True outside a set of probability zero |
| $\mu \ll \nu$ | Absolute continuity | $\nu$-null implies $\mu$-null; the condition for a density to exist |
