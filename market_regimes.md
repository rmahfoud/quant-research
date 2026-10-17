---
pagetitle: "Market Regimes and Hidden Markov Models"
description: "Hidden Markov and other regime models: why they find volatility states, not return states, how to fit them honestly, and how to use them for sizing and risk."
keywords: ["market regimes", "hidden Markov models", "regime switching", "volatility", "Markov-switching models", "Student-t emissions"]
author: "Robert Mahfoud"
lang: en
---

# Market Regimes and Hidden Markov Models

### What a regime model actually estimates, how to fit a hidden Markov model honestly, and where its output belongs

---

```{=html}
<aside class="abstract">
```

# Abstract {#abstract}

```{=latex}
\begin{chapterabstract}
```

A market regime is an output of a model the analyst chooses, not a property of the market. The standard regime model, the hidden Markov model, separates calm periods from turbulent ones well. It does not separate rising markets from falling ones. A century of US stock returns confirms this. The model's value is in setting risk, not in choosing direction.

A regime model returns state probabilities, not a single label. Collapsing the probabilities to the most likely state discards the model's uncertainty and is the most common implementation error. The model can predict only because states persist, and the decay of that persistence limits how far ahead it can help. Clustering, jump models and mixture models are special cases of the hidden Markov model with a restriction added or removed. One statistical fact governs the field. More observations sharpen the estimate of each state's volatility, but each state's mean return improves only with more calendar time. With 10 years of daily data and a correctly specified model, the estimated return gap between two states has the wrong sign about one time in six. The volatility gap from the same fit is 16 times more precise.

Fitted in real time on US stocks, a two-state model finds a calm state with about 10% annual volatility and a turbulent state with about 28%. In hindsight the turbulent state seems to lose about 40 points a year relative to the calm state. Out of sample that gap disappears. Days flagged as turbulent in advance were more than twice as volatile and earned no less. Several software packages report smoothed, look-ahead probabilities by default. A good fit is not evidence of regimes. Data with smoothly drifting volatility and no regimes fits regime models well, and a fat-tailed running volatility estimate forecast the return distribution better than the regime model did.

Over 80 years of US data, cutting exposure when the model expected turbulence raised the Sharpe ratio from about 0.52 to about 0.6, within the margin of error. It reduced the maximum drawdown from 59% to about 40%. The overlay breaks even at about 13 basis points of one-way cost. In forecasting models, dividing the target by trailing volatility matters more than any regime feature. The chapter recommends using regimes for risk rather than direction, keeping filtered probabilities, and normalising forecast targets by trailing volatility.

```{=latex}
\end{chapterabstract}
```

```{=html}
</aside>
```

---

**What this is.** "Regime" has more meanings than any other word in systematic
trading. It names a latent Markov state, a VIX threshold, a business-cycle phase,
a correlation cluster, and the vague feeling that this year differs from last
year. This chapter separates these meanings. It defines what a regime model *is*
mathematically. It states what sixty years of literature have established and
which results hold on out-of-sample data. It shows how to fit the central model
of the field, the hidden Markov model, honestly. It shows how to use the model's
output for sizing, risk and forecasting without fooling yourself or wasting the
effort.

**How to read it.** Part I (§1–§8) covers the models. It explains what a regime
is and why one might exist. It traces how the field arrived here. It presents the
formal models, the hidden Markov model in practice, and the taxonomy that reduces
the formal models to one small design space. It ends with an honest scorecard of
what works. Part II (§9–§13) covers use. It gives the statistical framing that
tells you *which* scheme your problem calls for when a forecasting model consumes
the regime. It then presents the schemes themselves, the research and evaluation
protocol, and what to do in live trading.

Appendix A defines every concept the main text uses without explaining. It orders
the concepts so that each builds on the earlier ones, rather than as a glossary.
§5, §6 and §10 rely on it most.

Read three sections first. **§8.1** shows why regime models identify volatility
and not returns, with the simulation. **§6.11** gives the same result on a century
of US equity returns, fitted walk-forward with Student-t emissions. **§11.2** lists
the eight ways regime research leaks. If you are implementing, §6, §10 and §11 are
the working sections and the rest is reference.

**What you will be able to do.** After this chapter you should be able to:

1. Say what a regime model estimates, and compute from a fitted transition matrix
   the horizon beyond which it cannot help.
2. Fit a hidden Markov model by EM with heavy-tailed emissions, a persistence
   prior and walk-forward parameters, and check it with pseudo-residuals.
3. Explain why the data identify state volatilities but not state means, and
   design around it.
4. Choose among threshold rules, continuous indices, jump models and HMMs for a
   given decision.
5. Feed a regime estimate into a position rule, a risk model or a forecasting
   model without look-ahead, and evaluate the result with episode-counted
   standard errors.

**Relationship to the other notes.** [Trend-Following in Financial
Markets](trend_following.html) derives what a trend rule earns. Several of its
results reappear here, because a trend filter is a two-state regime classifier
with the states named "up" and "down". [Momentum in Financial
Markets](momentum_deep_dive.html) covers signal measurement, and [Simple and Log
Returns](log_returns.html) covers the return conventions used throughout. Each
stands alone.

**Epistemic tags.** A tag marks the status of each claim:

- **[Fact]** — replicated across independent datasets or implementations, with
  broad agreement among people who have looked.
- **[Contested]** — documented, but with live disagreement about magnitude,
  robustness, or cause.
- **[Hypothesis]** — a proposed mechanism, not decisively tested.
- **[Practice]** — practitioner convention. It may be right, but the evidence is
  private or absent.

Untagged sentences are definitions, derivations, or arithmetic. Several results
come from simulations run for this chapter. The chapter labels them **[Simulated]**.
The worked example of §6.11 uses real data. The repository holds the generating
code for both, alongside this document, in
[`figures/`](https://github.com/rmahfoud/quant-research/tree/master/figures){target="_blank"}. You can change the parameters and rerun it.

---

**Notation.** $r_t$ is the return of the traded asset over bar $t$, in log returns
unless noted. $A$ is the number of bars per year (252 for daily data).
$\mathcal{F}_t$ is the information set available at the *end* of bar $t$.

$s_t \in \{1, \dots, K\}$ is the **regime**, a latent discrete state. $K$ is the
number of regimes. The asset price $S_t$ of the other notes does not appear in
this chapter. $\mathbf{P}$ is the $K \times K$ transition matrix with
entries $p_{jk} = \Pr(s_{t+1} = k \mid s_t = j)$. $\boldsymbol{\pi}$ is its
stationary distribution, and $\lambda_2$ is its second-largest eigenvalue in
modulus. $\psi$ collects the parameters of the state process. In §6.6 the vectors
$\psi_{jk}$ are the coefficients that tie transitions to lagged covariates
$z_{t-1}$. $\theta_k$ collects the parameters of the observation (emission) distribution in
state $k$. For Gaussian emissions these are the mean $\mu_k$ and standard deviation
$\sigma_k$. For Student-t emissions (§6.3) they are the location $\mu_k$, the scale
$\sigma_k$ and the degrees of freedom $\nu_k$. $D_k$ is the length of a visit
to state $k$ (§6.5).

Three different state beliefs recur throughout. They are never interchangeable:

$$
\underbrace{\xi_{t|t-1}}_{\text{predicted}} = \Pr(s_t \mid \mathcal{F}_{t-1}),
\qquad
\underbrace{\xi_{t|t}}_{\text{filtered}} = \Pr(s_t \mid \mathcal{F}_{t}),
\qquad
\underbrace{\xi_{t|T}}_{\text{smoothed}} = \Pr(s_t \mid \mathcal{F}_{T}).
$$

Each is a $K$-vector of probabilities, and $\xi_{t|t}^{(k)}$ denotes its $k$-th
component. $T$ is the last observation in the sample. Confusing these three
objects is the single largest source of false results in this field. §5.1 treats
the distinction in full. The pairwise smoothed probability of a transition,
$\xi_{t-1,t|T}^{(jk)} = \Pr(s_{t-1} = j, s_t = k \mid \mathcal{F}_T)$, appears in
estimation (§6.1).

On the forecasting side, $x_t \in \mathbb{R}^d$ is the feature vector known
at $t$, $y_t$ is the prediction target realised over $(t, t+h]$, and $h$ is the
forecast horizon in bars. In §5 and §6, the HMM's observation is not a
forecasting target. There $y_t$ is simply the observation at $t$ (usually $r_t$).
$f(\cdot)$ is the fitted model, and $m(x) = \mathbb{E}[y \mid x]$ is the true
conditional mean. When $f$ carries a parameter argument — $f(\cdot \mid
\theta_k)$ — it means the state-$k$ observation density instead; the argument is
what distinguishes the two. $p(x)$, $p(y \mid x)$ and $p(x, y)$ denote the
feature, conditional, and joint distributions. Subscripting them by $k$ (as in
$p_k(y \mid x)$) means "conditional on regime $k$". $w_t$ is a training sample
weight, $g(\cdot)$ is a gating function, and $\hat\sigma_t$ is an
$\mathcal{F}_t$-measurable estimate of return volatility.

Two symbols have a fixed meaning. $\sigma$ is always a return volatility or
scale, never a significance level or a sigmoid. $K$ is always the number of
regimes, never a kernel or a Kalman gain.

Matrices and constant vectors are bold: $\mathbf{P}$, $\boldsymbol{\pi}$, and
$\mathbf{1}$, the vector of ones. Every other vector ($\xi$, $x_t$, $z_t$,
$\theta_k$) is plain, and the context says which it is. The one bold exception is
the cross-asset return vector $\mathbf{r}_t$ of §5.9. The text defines symbols that
belong to a single model ($\beta$, $\omega$, $c$, $\gamma$ and similar) where the
model appears. A few letters change meaning between models. Watch $\lambda$ in
particular. It is the second eigenvalue ($\lambda_2$), the jump penalty (§5.7, §7.2)
or an exponential decay factor (§6.8, §6.11, §10.3), and each use says which.
In §12 and A.45–A.46 a plain $\pi_t$ is a position size. It is not a component of the
stationary distribution, which is always $\boldsymbol{\pi}$ or $\pi_k$, indexed by state.

---

## Table of contents

- [Abstract](#abstract)

**Part I — What a regime is, and what is known about it**

1. [What a market regime is](#1-what-a-market-regime-is)
2. [Why regimes could exist](#2-why-regimes-could-exist)
3. [How the field evolved](#3-how-the-field-evolved)
4. [Foundational references](#4-foundational-references)
5. [The formal models](#5-the-formal-models)
6. [Hidden Markov models in practice](#6-hidden-markov-models-in-practice)
7. [Taxonomy and equivalences](#7-taxonomy-and-equivalences)
8. [What is known to work, and what is not](#8-what-is-known-to-work-and-what-is-not)

**Part II — Using a regime model**

9. [Which shift do you have?](#9-which-shift-do-you-have)
10. [Conditioning a forecasting model on the regime](#10-conditioning-a-forecasting-model)
11. [Research and evaluation](#11-research-and-evaluation)
12. [Trading a regime-aware model](#12-trading-a-regime-aware-model)
13. [Synthesis](#13-synthesis)

**Appendix**

- [A. Concepts and prerequisites](#appendix-a-concepts-and-prerequisites) — every
  advanced idea the main text leans on, built from first principles and ordered by
  dependency. Start here if a term in §5, §6 or §10 is unfamiliar.

---

# 1. What a market regime is {#1-what-a-market-regime-is}

## 1.1 The wrong intuition

A portfolio manager asked what regime the market is in gives an answer: risk-on,
late-cycle, a high-inflation regime, a dispersion regime. The answer takes the
form of a statement about the world, like "the S&P is at 5,400". That form
assumes the regime is a fact about the market. It assumes you could in principle
observe the regime and might currently misjudge it. This assumption is the
problem.

The regime is not such a fact. You observe a sequence of returns. A discrete-state
process that switches between distributions can represent any such sequence, in
infinitely many ways. A two-state Gaussian mixture gives a calm state and a
turbulent state. Four states give something like crash, slow growth, bull, and
recovery. This is what [Guidolin and Timmermann (2007)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=940652){target="_blank"} report
for joint stock and bond returns, because they fitted four states. A twelve-state
fit also works, because the likelihood assigns some role to every state. The data
cannot show that any of these fits is more correct than the others. A
$K$-component mixture is a universal approximator for densities. With enough
components it fits any distribution to any tolerance, and with enough states it
fits any path.

The statement "this market has regimes" becomes a claim about the world only when
you fix $K$, fix the state dynamics, and commit to out-of-sample evaluation. On
its own it claims nothing. Everything hard about this field follows from this.
The standard test for "how many regimes are there" has no standard distribution
(§8.2). This is the central difficulty of the field, not a technical footnote.

## 1.2 The right starting point: a conditional density with a discrete bottleneck

A regime model asserts that the one-step-ahead predictive density of returns is a
finite mixture. The chapter states the mixture here once and uses it throughout:

$$
p(r_t \mid \mathcal{F}_{t-1})
  = \sum_{k=1}^{K} \underbrace{\xi_{t|t-1}^{(k)}}_{\text{weight}}
    \cdot \underbrace{f(r_t \mid \theta_k)}_{\text{component}} ,
$$

where $\xi_{t|t-1}^{(k)} = \Pr(s_t = k \mid \mathcal{F}_{t-1})$ is your predicted
probability of being in state $k$, and $f(\cdot \mid \theta_k)$ is the return
distribution that state implies. Three points follow:

- **The regime is never observed.** The mixture generates the data, and the state
  is a latent index. You can compute a *posterior over states*. You can never
  compute the state itself.
- **The predictive density is the object, not the state label.** Collapsing
  $\xi_{t|t-1}$ to its argmax and treating that label as data discards the
  confidence the model itself reports. This is the most common practitioner error
  in the field. §10.1 says what to use instead.
- **The model is worth using only if it beats the alternatives.** The alternatives
  are a single distribution ($K = 1$) and a continuously varying parameter
  (stochastic volatility, GARCH). The model often does not beat them (§8.7).

The key term is the **discrete bottleneck**. Asserting $K$ regimes asserts that
everything relevant about the conditional distribution of returns reduces to which
of $K$ states holds. This reduction gains statistical efficiency, because every
observation assigned to state $k$ helps estimate the single parameter vector
$\theta_k$. It loses fidelity, because the world need not consist of a fixed number of discrete states.
Whether the trade-off is worth making is an empirical question. The answer is
usually yes for volatility and usually no for expected returns. §8 explains why.

## 1.3 Persistence is the entire forecasting content

This subsection covers one consequence of §1.2. It is quantitative, practice
routinely violates it, and it takes three lines to derive.

Suppose $s_t$ is independent across $t$, so the mixture has no memory. Then
$\Pr(s_t = k \mid \mathcal{F}_{t-1}) = \pi_k$ for every history. The predictive
density equals the *unconditional* mixture $\sum_k \pi_k f(\cdot \mid
\theta_k)$, and the model forecasts nothing. It has told you that returns are
fat-tailed and heteroskedastic on average. That fact is real, but it gives no
signal.

All forecasting content therefore comes from the gap between the transition matrix
$\mathbf{P}$ and the no-memory matrix $\mathbf{1}\boldsymbol{\pi}^{\top}$. The
second-largest eigenvalue of $\mathbf{P}$ governs that gap. Write the
eigendecomposition of an ergodic chain: $\lambda_1 = 1$ with left eigenvector
$\boldsymbol{\pi}$, and the remaining eigenvalues $|\lambda_2| \ge \dots \ge
|\lambda_K|$ control the transient. Then

$$
\mathbf{P}^{h} = \mathbf{1}\boldsymbol{\pi}^{\top} + O(|\lambda_2|^{h}),
$$

so an $h$-step-ahead state forecast reverts to the unconditional distribution
geometrically, at rate $|\lambda_2|$. A two-state chain has a closed form:

$$
\lambda_2 = p_{11} + p_{22} - 1 ,
\qquad
\text{half-life} = \frac{\ln 2}{-\ln |\lambda_2|} \ \text{bars.}
$$

The absolute value matters only in the anti-persistent case
$p_{11} + p_{22} < 1$. There $\lambda_2 < 0$, and the state belief alternates in
sign as it decays. Fitted financial chains are persistent, with $\lambda_2$ close
to one.

**The second eigenvalue sets a hard ceiling on the horizon at which a regime
model can help.** You can compute the ceiling from the fitted transition matrix
before you run a single backtest. Take the calibration used throughout this
document. It has $p_{11} = 0.99$ for a calm state with expected duration 100
days, and $p_{22} = 0.96$ for a turbulent state with expected duration 25 days.
Then $\lambda_2 = 0.95$ and the half-life is 13.5 days. At a 60-day horizon
$\lambda_2^{60} = 0.046$, so **more than 95% of the state information is gone.**
A model fitted on daily data with these dynamics cannot inform a quarterly
asset-allocation decision, however convincing its in-sample regime plot looks. A
quarterly rebalance needs a state process whose half-life is measured in
quarters. That is a different model with different data requirements. Sampling
the same model less often does not provide it.

> **Diagnostic.** **[Practice]** Compute $|\lambda_2|$ and its half-life the
> moment you fit a transition matrix, and compare it to your rebalancing horizon.
> If the half-life is shorter than the horizon, the regime model adds no
> information at that horizon.

## 1.4 The master form

Generalising §1.2 to cover everything in §5, a regime model has two parts. One is
a state process. The other is a state-conditional observation model:

$$
\begin{aligned}
s_t &\sim q\!\left(s_t \mid s_{t-1},\, z_{t-1};\, \psi\right)
   && \text{(state dynamics)} \\[2pt]
y_t \mid s_t = k &\sim f\!\left(\cdot \mid x_t;\, \theta_k\right)
   && \text{(regime-conditional observation model)}
\end{aligned}
$$

Here $\psi$ collects the parameters of the state process. $z_{t-1}$ is any
observable that may drive transitions, and $x_t$ is any observable that may drive
the observation. Four slots vary. Every model in §5 makes one choice for each
slot:

| Slot | Question | Range of choices |
|---|---|---|
| **What varies** | Which parameters depend on $k$? | mean only; variance only; mean and variance; full covariance; the whole regression function; the noise distribution |
| **State dynamics** | How does $s_t$ move? | Markov; semi-Markov with explicit durations; threshold on observable $z$; i.i.d. mixture; single permanent break |
| **State driver** | What determines the transition? | endogenous (past $y$); exogenous ($z$); free (latent only) |
| **Inference and use** | What do you condition on, and what consumes it? | predicted / filtered / smoothed; hard label or posterior; feeds parameters, weights, features, or a gate |

Two points follow. First, the *inference and use* slot belongs to the research
protocol, not to the model. Yet its effect on measured performance is larger than
the effect of the other three slots. Second, most of the literature varies slots 1
and 2 and holds slots 3 and 4 fixed. This is why the set of models in §5 looks
larger than the design space of §7 turns out to be.

## 1.5 What a regime is not

The table below lists the objects most often confused with a regime and states how
each differs.

| Object | What it is | How it differs from a regime |
|---|---|---|
| **Trend** | a signed conditional mean, $\mathbb{E}[r_t \mid \mathcal{F}_{t-1}]$ | continuous-valued and *ordered*. Regimes are categorical and unordered |
| **Structural break** | a one-time permanent parameter change | non-recurrent: the old state never returns, so history offers nothing to estimate about the new state |
| **Stochastic volatility** | a continuous latent scale $\sigma_t$ | no discrete bottleneck. $\sigma_t$ takes a continuum of values |
| **GARCH** | $\sigma_t^2$ as a deterministic function of past returns | no latent state: $\sigma_t$ is $\mathcal{F}_{t-1}$-measurable, so no state needs filtering |
| **Conditioning variable** | an observable such as the dividend yield or the VIX | observable and continuous, so you can regress on it directly |
| **Business-cycle phase** | an economic classification (e.g. NBER dates) | published with a 6–18 month lag and revised. It is not $\mathcal{F}_t$-measurable, so a live signal cannot use it † |
| **Microstructure state** | order-book condition (wide/tight, toxic/benign) | different time scale by five orders of magnitude, and a different object |
| **Cross-sectional cluster** | a partition of *assets* | a regime is a partition of *time*. The two are often confused because both use $k$-means |

† **[Fact]** The NBER Business Cycle Dating Committee's announcements are the
standard example of a variable that is informative and widely cited, yet
untradable at the dates it labels. Any backtest that conditions on NBER
recession dates without lagging them by the actual announcement delay reports
results that no trader could have earned.

The GARCH row deserves attention. **The most common alternative to a regime model
is a continuous-state model rather than "no model". The continuous model usually
wins.** A regime model offers interpretability and a natural basis for discrete
decisions. It pays for these with a coarse approximation to a state variable
that, on the evidence, is continuous. §8.7 puts numbers on the trade-off.

> ### §1 Key takeaways
>
> 1. A regime is a property of a model, not of the market. The question "what
>    regime are we in" is well posed only after you fix $K$ and the state
>    dynamics.
> 2. A regime model produces a predictive *density*
>    $\sum_k \xi_{t|t-1}^{(k)} f(\cdot \mid \theta_k)$, not a label. Collapsing the
>    density to the argmax label discards the model's own uncertainty. This is the
>    most common implementation error in the field.
> 3. All forecasting content comes from the persistence of the state. An i.i.d.
>    mixture predicts nothing beyond the unconditional distribution.
> 4. The second eigenvalue of the transition matrix sets a hard ceiling on the
>    useful forecast horizon. Compute its half-life before you backtest. If the
>    half-life is shorter than your rebalancing interval, stop.
> 5. Regimes are categorical partitions of *time*. Trends, stochastic volatility,
>    GARCH, conditioning variables, and cross-sectional clusters are all
>    different objects, and three of them are usually better tools.
> 6. Publishers release NBER-style economic regime labels with a lag and revise
>    them. Using them unlagged is a look-ahead, not a modelling choice.

---

# 2. Why regimes could exist {#2-why-regimes-could-exist}

Before fitting anything, ask what would have to be true of the world for a
*discrete* state model to describe it correctly. Most proposed mechanisms predict
*continuous* variation in conditional moments. A discrete model fitted to a
continuous mechanism produces unstable, sample-dependent state estimates, which
§8 documents.

Only one mechanism family genuinely predicts discreteness, and it is not the one
usually cited.

## 2.1 Family A — occasionally binding constraints

The strongest microfoundation for discreteness is an inequality constraint that
sometimes binds and sometimes does not. Intermediaries face leverage limits,
margin requirements, VaR budgets, and redemption thresholds. Each is a constraint
of the form $c(\text{state}) \le \bar{c}$, and the associated Lagrange multiplier
is exactly zero when the constraint is slack and strictly positive when it binds.
**The multiplier is a discrete state**, not an approximation to one. It arises
from the complementary-slackness condition of an optimisation problem.

The consequences are asymmetric and fast. Brunnermeier and Pedersen (2009) model
the feedback between market liquidity and funding liquidity. A shock that
tightens funding forces deleveraging. Deleveraging widens spreads, and wider
spreads tighten funding further. He and Krishnamurthy (2013) and Adrian, Etula
and Muir (2014) develop the asset-pricing consequences. Intermediary net worth is
a priced state variable, and its effect on risk premia is strongly nonlinear near
the constraint. **[Contested]** — the mechanism is well formalised, and the
intermediary-capital factor prices assets in-sample. Whether the
constraint-binding indicator is *measurable in real time* well enough to trade is
a different and much weaker claim.

This family predicts things the others do not, so it is the most falsifiable. It
makes three predictions. State transitions should be **fast in one direction and
slow in the other**, because constraints bind abruptly and relax gradually.
Correlations should *rise* in the constrained state, as everyone liquidates the
same assets. The state should be visible in funding-market observables (repo
spreads, cross-
currency basis, dealer balance sheets) before it is visible in returns.

## 2.2 Family B — policy and institutional regimes

Central-bank reaction functions really do change, discretely, when the committee
or the mandate changes. Sims and Zha (2006) fit a multivariate regime-switching
model to U.S. monetary policy and find three coefficient regimes roughly matching
the periods that narrative accounts identify. Their headline result is more
informative than the existence of the regimes, and it recurs throughout this
document. **The best-fitting specification allowed time variation in
disturbance variances only.** When they allowed coefficients to switch as well,
the improvement was modest. The regime differences were too small to explain
the inflation of the 1970s–80s. **[Fact]**

Regulatory changes (Reg NMS, Basel III, the Volcker Rule), index-methodology
changes, and market-structure changes (decimalisation, the rise of ETFs) are the
same kind of event. Each is genuinely discrete, dated and externally observable.
If the regime is externally observable, you should condition on the observable
directly rather than infer a latent state from returns (§5.5, §7.4).

## 2.3 Family C — the leverage cycle and multiple equilibria

Geanakoplos's leverage cycle and the limits-to-arbitrage literature (Shleifer and
Vishny, 1997) describe positive feedback. Falling prices reduce collateral value.
Lower collateral value forces sales, and the sales lower prices further. Positive
feedback loops admit multiple equilibria, and multiple equilibria are discrete by
construction. **[Hypothesis]**
— the theory is well developed. No published study has convincingly separated
"the system jumped between equilibria" from "a large shock hit a continuous
system" using return data alone.

## 2.4 Family D — investor composition and beliefs

Barberis, Shleifer and Vishny (1998) model investor sentiment *as* a
regime-switching process. In their model the representative investor believes
earnings follow either a mean-reverting regime or a trending regime. Bayesian
updating between the two regimes generates under- and over-reaction. This is a
rare case where the regime model is the economic theory, not a statistical
convenience. Flow-driven versions make the same argument about who is trading
rather than what investors believe. These versions include retail participation,
systematic-strategy crowding and dealer gamma positioning. **[Contested]**

## 2.5 Family E — the business cycle

Expected returns vary with business conditions. Fama and French (1989) show that
dividend yields and term spreads forecast returns with cyclical patterns.
Cochrane's (2011) survey argues that essentially all of the variation in asset
prices is discount-rate variation, which is cyclical. Henkel, Martin and Nardari
(2011) turn this into a regime statement: **short-horizon return predictability
is concentrated in recessions and close to zero in expansions.**
[Farmer, Schmidt and Timmermann (2023)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3152386){target="_blank"} find the same pattern without imposing a
cycle. Predictability appears in short, localised "pockets".

This is the strongest economic case for regime-conditional *return* models, and
it has two caveats. First, business-cycle phases are long. A model with
cycle-length persistence has perhaps 10–15 independent observations in a
post-war sample. This is the identification problem of §8.1 in its most acute
form. Second, Cakici and co-authors challenged the pockets result. Their
replication, published in the *Journal of Finance* in 2025, disputes the
out-of-sample economic significance. **[Contested]**

## 2.6 Family F — there are no regimes

State the null as forcefully as the alternatives. It is the hypothesis most
consistent with the evidence and the one most rarely tested.

A single process with persistent stochastic volatility and heavy tails has no
discrete states anywhere. A regime model still describes its sample paths with two
to four states, convincing-looking state plots and a significant-looking
likelihood improvement. [Diebold and Inoue (2001)](https://www.nber.org/papers/t0264){target="_blank"} prove a
version of this analytically: **stochastic regime switching and long memory are
easily confused, even asymptotically**. A process with occasional breaks
generates estimated long-memory parameters. A long-memory process generates
apparent breaks. Granger and Hyung (2004) demonstrate the same confusion
empirically on S&P 500 absolute returns. Perron (1989) set the precedent. He
showed that a trend-stationary series with one break is nearly indistinguishable
from a unit root.

In practice, **a likelihood improvement from adding regimes does not show that
regimes exist.** It shows that your single-state model was misspecified, which you
already knew. A mixture is a flexible way to absorb misspecification. **[Fact]**

## 2.7 Telling the families apart

Most of the time you cannot tell the families apart, and pretending otherwise is
a common cause of failed research programmes. The families do make different
predictions, and you can test a few of them on data you already have.

| Prediction | Constraints (A) | Policy (B) | Leverage cycle (C) | Business cycle (E) | No regimes (F) |
|---|---|---|---|---|---|
| Transition asymmetry | fast in, slow out | either | fast in, slow out | symmetric | none expected |
| Correlations rise in bad state | strongly yes | no | yes | mildly | mildly † |
| State visible in non-return data | yes (funding) | yes (dated) | partly | yes (macro) | no |
| Optimal $K$ stable across samples | yes | yes | — | — | **no** |
| Beaten by a continuous-vol model | no | no | — | — | **yes** |

† A stochastic-volatility null generates correlation increases in high-volatility
periods. The cause is purely mechanical. Correlations estimated over
high-variance windows are biased upward when the common factor's variance rises
faster than the idiosyncratic variance. [Forbes and Rigobon (2002)](https://www.nber.org/papers/w7267){target="_blank"} made this point
about "contagion", and it applies here unchanged: **an increase in measured
correlation during a crisis is partly an artefact of the volatility increase. It
is not independent evidence of a regime.**

The last two rows are the most actionable. They yield two concrete experiments you
can run in an afternoon:

1. **Stability of $K$.** Fit $K = 2, 3, 4, 5$ on disjoint halves of your sample
   and on bootstrapped resamples. If the selected $K$ and the fitted $\theta_k$
   vary across fits, the model fits misspecification, not structure.
2. **The continuous-model comparison.** Fit a GARCH or stochastic-volatility
   model and a regime model, and compare *out-of-sample predictive
   log-likelihood*, not in-sample fit. In most published comparisons, and in the
   worked example of §6.11, the continuous model wins on volatility and the two
   are hard to separate on everything else. **[Practice]**

A third test is worth more than both: **make the state predict something it was
not fitted on.** A state extracted from equity returns may also match credit
spreads, funding costs or realised dispersion. Such a state is more likely to be
real than a state that explains only the series used to estimate it.

> ### §2 Key takeaways
>
> 1. Occasionally binding constraints are the only mechanism family that predicts
>    genuine discreteness rather than continuous variation, because a
>    complementary-slackness condition literally *is* a two-state system.
> 2. Policy regimes are real, dated and externally observable. This favours
>    conditioning on the observable over filtering a latent state.
> 3. Sims and Zha's result generalises. When you let both means and variances
>    switch, variance switching accounts for nearly all of the effect. This
>    pattern recurs at every level of this document.
> 4. Return predictability is concentrated in bad times. This is the best economic
>    case for regime-conditional alpha. But bad times are rare, so the sample is
>    tiny, and the finding is contested.
> 5. A stochastic-volatility process with no regimes anywhere produces data that
>    regime models fit very well. A likelihood improvement from adding states does
>    not show that states exist.
> 6. Two cheap tests discriminate between the families. Check whether the selected
>    $K$ is stable across subsamples. Check whether a continuous-state model beats
>    the discrete one out of sample. Run both before building anything.
> 7. Rising correlations in crises are partly a mechanical artefact of rising
>    volatility ([Forbes and Rigobon, 2002](https://www.nber.org/papers/w7267){target="_blank"}), not independent evidence of a regime.

---

# 3. How the field evolved {#3-how-the-field-evolved}

The history explains the current literature. It explains why the econometrics is
deep and the trading evidence is thin. It also explains why the
speech-recognition and machine-learning communities developed the same objects
under different names.

```mermaid
timeline
    title Regime modelling, seven eras
    1900-1957 : One distribution : Bachelier, Gaussian random walk
    1963-1972 : Fat tails noticed : Mandelbrot stable laws : Fama
    1958-1988 : Switching regressions : Quandt : Goldfeld-Quandt : mixtures, no dynamics
    1989      : The Hamilton filter : recursive state posterior : ML becomes tractable
    1989-2002 : Financial adoption : SWARCH : MS-GARCH : asymmetric correlations
    2002-2012 : Allocation era : multivariate switching : turbulence indices : practitioners
    2012-     : Machine learning : jump models : deep state space : latent state absorbed
```

## 3.1 Era I — One distribution (1900–1957)

**Contribution.** Bachelier's 1900 thesis modelled prices as Brownian motion. The
mid-century finance literature adopted the Gaussian random walk as the baseline.

**What changed.** The idea took hold that price changes are draws from a *fixed*
distribution. Every later era has argued against this null.

**Limitations.** The model is empirically wrong in the second and fourth moments,
as the next era established.

**Lasting influence.** The influence is enormous, mostly as a baseline to argue
against. Every regime paper's introduction varies the claim that "returns are not
i.i.d. Gaussian".

## 3.2 Era II — Fat tails, and the first alternative to regimes (1963–1972)

**Contribution.** Mandelbrot (1963) documented that speculative price changes
have far heavier tails than the Gaussian and proposed stable Paretian
distributions. Fama (1965) confirmed and extended the evidence for U.S. stocks.

**What changed.** The field accepted non-normality. **The first explanation
offered was a single heavy-tailed distribution, not regimes.** Mandelbrot's
alternative was a single law with infinite variance, rather than two laws that
alternate.

**Limitations.** Stable laws with $\alpha < 2$ imply infinite variance. This is
awkward for portfolio theory and, on the evidence of later work, does not match
the data. The tails are heavy, but the variance appears finite.

**Lasting influence.** The important legacy is an unresolved question. Returns
may come from one fat-tailed process or from two thin-tailed processes that take
turns. The profession never settled which. It moved on to models that do not need
an answer. §2.6 and §8.7 address the question, which is still open.

## 3.3 Era III — Switching regressions (1958–1988)

**Contribution.** Quandt (1958) estimated a linear regression obeying two
separate regimes with an unknown switch point. Goldfeld and Quandt (1973)
introduced a Markov model for switching regressions.

**What changed.** Regimes became estimable objects rather than narrative
descriptions.

**Limitations.** The estimation was awkward. In the mixture versions the state
carried no persistence, so the models had no forecasting content (§1.3). No
efficient recursion existed for the state posterior. This made likelihood
evaluation expensive and multivariate extensions impractical.

**Lasting influence.** The influence is direct. Hamilton's paper explicitly solves
the computational problem this era posed.

## 3.4 Era IV — The Hamilton filter (1989)

**Contribution.** [Hamilton (1989)](https://www.econometricsociety.org/publications/econometrica/1989/03/01/new-approach-economic-analysis-nonstationary-time-series-and){target="_blank"} gave a recursive algorithm for the state posterior
in a Markov-switching autoregression. The algorithm needs one forward pass. It
made maximum likelihood estimation tractable. It also made the distinction
between filtered and smoothed inference explicit and computable. [Kim (1994)](<https://doi.org/10.1016/0304-4076(94)90036-1>){target="_blank"}
supplied the efficient backward smoother that completes the pair.

**What changed.** Almost everything. This is the founding moment of the modern
field, and every implementation still runs the filter. Its structure is
identical to the Kalman filter with a discrete state space: predict, then update
on the new observation. This is why the machine-learning literature's
forward-backward algorithm for HMMs ([Baum et al., 1970](https://doi.org/10.1214/aoms/1177697196){target="_blank"}; [Rabiner, 1989](https://doi.org/10.1109/5.18626){target="_blank"}) is the
same algorithm, discovered a generation earlier in a different community.

**Limitations.** Hamilton's own application was to U.S. GNP growth, a
low-frequency, low-noise series. Financial returns are high-frequency and
high-noise. The transfer to finance succeeded less than the enthusiasm of the
following decade suggested.

**Lasting influence.** The influence is total. Any regime model fitted today runs
Hamilton's recursion.

## 3.5 Era V — Financial adoption, and the discovery that it is about variance (1989–2002)

**Contribution.** [Turner, Startz and Nelson (1989)](https://www.nber.org/papers/w2818){target="_blank"} applied switching to stock
returns. [Hamilton and Susmel (1994)](<https://doi.org/10.1016/0304-4076(94)90067-1>){target="_blank"} combined switching with ARCH (SWARCH). [Gray
(1996)](<https://doi.org/10.1016/0304-405X(96)00875-6>){target="_blank"} and [Haas, Mittnik and Paolella (2004)](https://doi.org/10.1093/jjfinec/nbh020){target="_blank"} solved the path-dependence problem
that makes naive MS-GARCH inestimable. [Ang and Bekaert (2002)](https://business.columbia.edu/sites/default/files-efs/pubfiles/1971/1137.pdf){target="_blank"} built the
international asset-allocation application. Longin and Solnik (2001) and [Ang and
Chen (2002)](https://doi.org/10.1016/S0304-405X(02)00068-5){target="_blank"} documented that correlations rise in down markets.

**What changed.** Two things changed, in opposite directions. Positively, the
field established that **regime models describe second moments well**, because
volatility states are large, persistent and estimable. Negatively, critiques
arrived and nobody answered them. [Hansen (1992)](https://users.ssc.wisc.edu/~behansen/papers/jae_92.html){target="_blank"} showed that the likelihood-ratio test for
the number of regimes has no standard distribution, because the
transition probabilities are unidentified under the null. Applying his bound to
Hamilton's own GNP model, **the switching specification could not reject a plain
AR(4)**. [Dacco and Satchell (1999)](<https://onlinelibrary.wiley.com/doi/abs/10.1002/(SICI)1099-131X(199901)18:1%3C1::AID-FOR685%3E3.0.CO;2-B>){target="_blank"} showed that regime-switching models fit
exchange rates very well in sample and lose to a random walk out of sample. They
also explained *why*, a part that readers usually forget. The loss function is
asymmetric in the state-classification error. So even a model with correctly
estimated parameters forecasts worse than a constant if it misclassifies the
state often enough.

**Limitations.** The era's applied work systematically reported smoothed state
probabilities and in-sample fit.

**Lasting influence.** The second-moment result is the durable one. The
first-moment results from this era have mostly not replicated.

## 3.6 Era VI — Multivariate models and the allocation application (2002–2012)

**Contribution.** [Guidolin and Timmermann (2007)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=940652){target="_blank"} fitted four-state models to
joint stock and bond returns and solved the resulting dynamic portfolio problem.
Pelletier (2006) built regime-switching dynamic correlations. Kritzman and Li
(2010) introduced the Mahalanobis "turbulence" index. [Kritzman, Page and
Turkington (2012)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2066848){target="_blank"} built the practitioner framework on it. [Bulla and co-authors
(2011)](https://mpra.ub.uni-muenchen.de/21154/){target="_blank"} ran the honest out-of-sample test of a Markov-switching allocation rule,
including transaction costs.

**What changed.** The application shifted from *predicting returns* to *managing
risk*, which is where the evidence supports regime models. Kritzman, Page and
Turkington framed the value as avoiding large losses, not picking direction. This
is the correct reading of the previous era's results.

**Limitations.** Much of the practitioner work in this era comes from firms that
sell regime-based products. That does not make it wrong, because these authors
have data and implementation experience that academics lack. But the backtests
are prone to selection bias, and the reported improvements typically do not
adjust for the number of specifications tried.

**Lasting influence.** The influence is high. Most institutional allocators still
use this era's framing.

## 3.7 Era VII — Machine learning, and the disappearing regime (2012–present)

**Contribution.** Several strands developed at once. Unsupervised methods
replaced likelihood-based HMMs where the emission model was the weakest part.
These methods include Gaussian mixtures, $k$-means on engineered features, and
Wasserstein clustering of correlation matrices. Statistical jump models ([Bemporad et al., 2018](https://arxiv.org/abs/1711.09220){target="_blank"}; [Nystrup, Kolm
and Lindström, 2020](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3594875){target="_blank"}) replaced the probabilistic state process with an explicit
jump *penalty*. This gives three things. Dynamic programming solves the state
assignment of the objective exactly (§5.7). Persistence has a tunable parameter.
And, by the authors' simulations, classification accuracy is better than a
correctly specified maximum-likelihood HMM. Deep latent-variable models (recurrent
switching linear dynamical systems, deep state-space models) brought
neural-network emissions to the same graphical structure.

**What changed.** The most consequential change is negative. **The dominant
machine-learning approach to asset pricing uses no explicit regime model.** [Gu, Kelly and Xiu (2020)](https://www.nber.org/papers/w25398){target="_blank"} handle time variation by interacting stock
characteristics with a small set of observable macro predictors. The function
approximator then finds whatever conditional structure exists. [Chen, Pelger
and Zhu (2024)](https://arxiv.org/abs/1904.00745){target="_blank"} learn a latent macro state with a recurrent network as part of an
end-to-end asset-pricing objective, rather than fitting it separately. The latent
state remains, but the approximator absorbs it. The approximator estimates the
state jointly with the quantity of interest. It does not receive the state from a
separately fitted model with its own errors.

Meanwhile the likelihood-based HMM kept improving. This period refined
several extensions and brought them to financial returns (§6; several have older
roots, §4). The extensions are Student-t emissions, semi-Markov durations,
covariate-driven transitions, Bayesian estimation with persistence priors, and
adaptive estimation with forgetting. Each addresses a specific failure of the
1989 model. The era leaves a
practical choice. **The regime can be a separate model whose output you use
directly or feed in, or a structure that a forecasting model discovers for
itself.** §6.10 covers direct use. §9 and §10 cover the choice between the two,
and the answer is that it depends on which distribution is shifting. §10.9 ranks
the options.

**Limitations.** The ML era has largely not engaged with the identification
critiques of Era V. A deep switching model has all of Hamilton's identification
problems plus its own, and the papers rarely report the diagnostics of §2.7
and §8.2.

> ### §3 Key takeaways
>
> 1. [Hamilton (1989)](https://www.econometricsociety.org/publications/econometrica/1989/03/01/new-approach-economic-analysis-nonstationary-time-series-and){target="_blank"} is the founding technical contribution. Every implementation
>    since runs his recursion. The recursion is the discrete-state Kalman filter
>    and the same object as the HMM forward algorithm from speech recognition.
> 2. The first proposed explanation for non-normal returns was one heavy-tailed
>    distribution, not two alternating ones. Nobody settled that debate. The field
>    bypassed it, and it is still the live null.
> 3. The critiques arrived early, and nobody answered them. [Hansen (1992)](https://users.ssc.wisc.edu/~behansen/papers/jae_92.html){target="_blank"} showed the
>    number-of-regimes test is non-standard and that Hamilton's own model could
>    not reject an AR(4). [Dacco and Satchell (1999)](<https://onlinelibrary.wiley.com/doi/abs/10.1002/(SICI)1099-131X(199901)18:1%3C1::AID-FOR685%3E3.0.CO;2-B>){target="_blank"} showed out-of-sample failure
>    and explained the mechanism.
> 4. The durable empirical finding across every era is that regimes describe
>    second moments well and first moments badly.
> 5. The 2002–2012 practitioner era got the framing right: use regimes for risk,
>    not direction. But interested parties produce most of its evidence base.
> 6. The modern machine-learning answer is usually to skip the explicit regime
>    model and let the approximator learn the conditioning. Whether that is right
>    depends on which distribution is shifting (§9). The HMM meanwhile gained
>    refinements that address its original failures (§6): heavy tails, durations,
>    covariates and priors.

---

# 4. Foundational references {#4-foundational-references}

The list groups entries by kind, because readers use each kind differently. Each
entry says why it matters. Where a free copy exists, the title links to it.
The list marks entries available only behind a paywall.

## 4.1 The founding econometrics

- **Quandt, R. E. (1958).** "The Estimation of the Parameters of a Linear
  Regression System Obeying Two Separate Regimes." *Journal of the American
  Statistical Association* 53(284), 873–880. — The origin. Two regimes, one
  unknown switch point, no state process.
- **Goldfeld, S. M. & Quandt, R. E. (1973).** "A Markov Model for Switching
  Regressions." *Journal of Econometrics* 1(1), 3–15. — Adds the Markov chain.
  The model exists, but the estimation is still impractical.
- **Hamilton, J. D. (1989).** ["A New Approach to the Economic Analysis of
  Nonstationary Time Series and the Business
  Cycle."](https://www.econometricsociety.org/publications/econometrica/1989/03/01/new-approach-economic-analysis-nonstationary-time-series-and)
  *Econometrica* 57(2), 357–384. — **The** paper. It gives the recursive filter that makes
  everything else computable. Read §2–3 of it even if you read nothing else in
  this list.
- **Hamilton, J. D. (1990).** ["Analysis of Time Series Subject to Changes in
  Regime."](https://doi.org/10.1016/0304-4076(90)90093-9) *Journal of
  Econometrics* 45(1–2), 39–70. [publisher — paywalled] — The EM algorithm for
  Markov-switching models, in the notation econometricians use (§6.1).
- **Hamilton, J. D. (1994).** *Time Series Analysis.* Princeton University Press,
  chapter 22. — The textbook treatment of the filter, the smoother, and the
  EM algorithm, worked in full. This is the reference you will actually
  implement from.
- **Kim, C.-J. (1994).** ["Dynamic Linear Models with
  Markov-Switching."](https://doi.org/10.1016/0304-4076(94)90036-1) *Journal of Econometrics* 60(1–2), 1–22. — The efficient backward smoother.
  Necessary for estimation, but dangerous if you use its output as a signal (§5.1).
- **Kim, C.-J. & Nelson, C. R. (1999).** [*State-Space Models with Regime
  Switching.*](https://doi.org/10.7551/mitpress/6444.001.0001) MIT Press. — The systematic treatment, including the Bayesian
  versions and the approximations that make multivariate models tractable.
- **Diebold, F. X., Lee, J.-H. & Weinbach, G. C. (1994).** ["Regime Switching
  with Time-Varying Transition
  Probabilities."](https://doi.org/10.1093/oso/9780198773917.003.0010) In C. P.
  Hargreaves, ed., *Nonstationary Time Series Analysis and Cointegration*, Oxford
  University Press, 283–302. [publisher — paywalled] — Transition probabilities
  that depend on observables, with an EM algorithm. The origin of §6.6.
- **Filardo, A. J. (1994).** ["Business-Cycle Phases and Their Transitional
  Dynamics."](https://doi.org/10.1080/07350015.1994.10524545) *Journal of
  Business & Economic Statistics* 12(3), 299–308. [publisher — paywalled] —
  Time-varying transitions driven by leading indicators. It is the standard applied
  template.
- **Durland, J. M. & McCurdy, T. H. (1994).** ["Duration-Dependent Transitions in
  a Markov Model of U.S. GNP
  Growth."](https://doi.org/10.1080/07350015.1994.10524543) *Journal of
  Business & Economic Statistics* 12(3), 279–288. [publisher — paywalled] —
  Transition probabilities that depend on how long the state has lasted (§6.5).
- **Hamilton, J. D. (2016).** ["Macroeconomic Regimes and Regime
  Shifts."](https://www.nber.org/papers/w21863) In J. B. Taylor & H. Uhlig,
  eds., *Handbook of Macroeconomics* vol. 2A, Elsevier, 163–201. — The founder's
  own retrospective: what the models have and have not delivered in
  macroeconomics.

## 4.2 Inference methods from the other community

The speech-recognition and machine-learning literature developed the same
algorithms independently, and its expositions are often clearer.

- **Baum, L. E., Petrie, T., Soules, G. & Weiss, N. (1970).** ["A Maximization
  Technique Occurring in the Statistical Analysis of Probabilistic Functions of
  Markov Chains."](https://doi.org/10.1214/aoms/1177697196) *Annals of Mathematical Statistics* 41(1), 164–171. — The EM
  algorithm for HMMs, nineteen years before Hamilton and in a different field.
- **Rabiner, L. R. (1989).** ["A Tutorial on Hidden Markov Models and Selected
  Applications in Speech Recognition."](https://doi.org/10.1109/5.18626) *Proceedings of the IEEE* 77(2), 257–286.
  — Still the best single exposition of forward-backward, Viterbi, and
  Baum-Welch. If Hamilton's notation is hard to follow, read this instead.
- **Zucchini, W., MacDonald, I. L. & Langrock, R. (2016).** [*Hidden Markov Models
  for Time Series: An Introduction Using R*](https://doi.org/10.1201/b20790), 2nd ed. Chapman & Hall/CRC. — The
  practical book. Numerical stability, scaling, label switching, model checking.
- **Frühwirth-Schnatter, S. (2006).** [*Finite Mixture and Markov Switching
  Models.*](https://doi.org/10.1007/978-0-387-35768-3) Springer. — The Bayesian reference, and the best treatment of the
  label-switching and identification problems.
- **Cappé, O., Moulines, E. & Rydén, T. (2005).** [*Inference in Hidden Markov
  Models.*](https://doi.org/10.1007/0-387-28982-8) Springer. — The theory: consistency, asymptotics, and which quantities
  the data can and cannot identify.
- **Fox, E. B., Sudderth, E. B., Jordan, M. I. & Willsky, A. S. (2011).**
  ["A Sticky HDP-HMM with Application to Speaker
  Diarization."](https://arxiv.org/abs/0905.2592) *Annals of Applied Statistics*
  5(2A), 1020–1056. — Nonparametric $K$ plus an explicit persistence prior. The
  right answer to "how many regimes" if you insist on a Bayesian one, and the
  origin of the "stickiness" idea that jump models later made explicit.
- **Albert, J. H. & Chib, S. (1993).** ["Bayes Inference via Gibbs Sampling of
  Autoregressive Time Series Subject to Markov Mean and Variance
  Shifts."](https://doi.org/10.1080/07350015.1993.10509929) *Journal of
  Business & Economic Statistics* 11(1), 1–15. [publisher — paywalled] — The
  first Gibbs sampler for Markov-switching models, drawing one state at a time.
- **Carter, C. K. & Kohn, R. (1994).** ["On Gibbs Sampling for State Space
  Models."](https://doi.org/10.1093/biomet/81.3.541) *Biometrika* 81(3),
  541–553. [publisher — paywalled] — Forward filtering, backward sampling: draw
  the whole latent path at once.
- **Chib, S. (1996).** ["Calculating Posterior Distributions and Modal Estimates
  in Markov Mixture Models."](https://doi.org/10.1016/0304-4076(95)01770-4)
  *Journal of Econometrics* 75(1), 79–97. [publisher — paywalled] — The
  joint-path sampler for HMMs, which mixes far better than single-site sampling
  (§6.7).
- **Stephens, M. (2000).** ["Dealing with Label Switching in Mixture
  Models."](https://doi.org/10.1111/1467-9868.00265) *Journal of the Royal
  Statistical Society: Series B* 62(4), 795–809. [publisher — paywalled] —
  Relabelling MCMC draws after the fact.
- **Frühwirth-Schnatter, S. (2001).** ["Markov Chain Monte Carlo Estimation of
  Classical and Dynamic Switching and Mixture
  Models."](https://doi.org/10.1198/016214501750333063) *Journal of the
  American Statistical Association* 96(453), 194–209. [publisher — paywalled] —
  The random permutation sampler, and identification by ordering constraints.
- **Scott, S. L. (2002).** ["Bayesian Methods for Hidden Markov Models: Recursive
  Computing in the 21st Century."](https://doi.org/10.1198/016214502753479464)
  *Journal of the American Statistical Association* 97(457), 337–351.
  [publisher — paywalled] — The clearest review of the recursions behind Bayesian
  HMM computation.
- **Celeux, G. & Durand, J.-B. (2008).** ["Selecting Hidden Markov Model State
  Number with Cross-Validated
  Likelihood."](https://doi.org/10.1007/s00180-007-0097-1) *Computational
  Statistics* 23(4), 541–564. [publisher — paywalled] — Choosing $K$ by held-out
  likelihood rather than by an information criterion.
- **Langrock, R. & Zucchini, W. (2011).** ["Hidden Markov Models with Arbitrary
  State Dwell-Time Distributions."](https://doi.org/10.1016/j.csda.2010.06.015)
  *Computational Statistics & Data Analysis* 55(1), 715–724. [publisher —
  paywalled] — Semi-Markov durations approximated by an ordinary HMM with
  expanded states, so the standard algorithms still apply (§6.5).
- **Cappé, O. (2011).** ["Online EM Algorithm for Hidden Markov
  Models."](https://arxiv.org/abs/0908.2359) *Journal of Computational and
  Graphical Statistics* 20(3), 728–749. — Recursive updating of HMM parameters as
  data arrive (§6.8).
- **Pohle, J., Langrock, R., van Beest, F. M. & Schmidt, N. M. (2017).**
  ["Selecting the Number of States in Hidden Markov Models: Pragmatic Solutions
  Illustrated Using Animal Movement."](https://arxiv.org/abs/1701.08673)
  *Journal of Agricultural, Biological and Environmental Statistics* 22(3),
  270–293. — Why information criteria over-select states, and a practical
  procedure. The application is ecology, but the argument is general.
- **Software.** **Visser, I. & Speekenbrink, M. (2010)**, ["depmixS4: An R
  Package for Hidden Markov Models"](https://doi.org/10.18637/jss.v036.i07),
  *Journal of Statistical Software* 36(7); **O'Connell, J. & Højsgaard, S.
  (2011)**, ["Hidden Semi Markov Models for Multiple Observation Sequences: The
  mhsmm Package for R"](https://doi.org/10.18637/jss.v039.i04), *Journal of
  Statistical Software* 39(4); and **Ardia, D., Bluteau, K., Boudt, K., Catania,
  L. & Trottier, D.-A. (2019)**, ["Markov-Switching GARCH Models in R: The
  MSGARCH Package"](https://doi.org/10.18637/jss.v091.i04), *Journal of
  Statistical Software* 91(4). — The packages of §6.12.

## 4.3 Regime models in finance — the empirical case

- **Turner, C. M., Startz, R. & Nelson, C. R. (1989).** ["A Markov Model of
  Heteroskedasticity, Risk, and Learning in the Stock
  Market."](https://www.nber.org/papers/w2818) *Journal of
  Financial Economics* 25(1), 3–22. — The first serious equity application.
- **Hamilton, J. D. & Susmel, R. (1994).** ["Autoregressive Conditional
  Heteroskedasticity and Changes in
  Regime."](https://doi.org/10.1016/0304-4076(94)90067-1) *Journal of Econometrics* 64(1–2),
  307–333. — SWARCH: switching plus ARCH. It shows that most of what
  looks like ARCH persistence is regime persistence.
- **Gray, S. F. (1996).** ["Modeling the Conditional Distribution of Interest
  Rates as a Regime-Switching Process."](https://doi.org/10.1016/0304-405X(96)00875-6)
  *Journal of Financial Economics* 42(1), 27–62. [publisher — paywalled] — Solves
  the path-dependence problem that makes naive MS-GARCH impossible to estimate.
- **Haas, M., Mittnik, S. & Paolella, M. S. (2004).** ["A New Approach to
  Markov-Switching GARCH Models."](https://doi.org/10.1093/jjfinec/nbh020) *Journal of Financial Econometrics* 2(4),
  493–530. — The cleaner solution, and the one now generally used.
- **Ang, A. & Bekaert, G. (2002).** ["International Asset Allocation With Regime
  Shifts."](https://business.columbia.edu/sites/default/files-efs/pubfiles/1971/1137.pdf)
  *Review of Financial Studies* 15(4), 1137–1187. — The canonical allocation
  application: correlations and volatilities rise together in the bad state, and
  what that does to optimal portfolios.
- **Longin, F. & Solnik, B. (2001).** "Extreme Correlation of International
  Equity Markets." *Journal of Finance* 56(2), 649–676. — Correlation varies
  in the tails. The paper establishes this with extreme-value theory rather than by
  splitting the sample.
- **Ang, A. & Chen, J. (2002).** "Asymmetric Correlations of Equity Portfolios."
  *Journal of Financial Economics* 63(3), 443–494. — The same asymmetry
  domestically, with a statistic designed to avoid the conditioning bias.
- **Guidolin, M. & Timmermann, A. (2007).** ["Asset Allocation under Multivariate
  Regime Switching."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=940652)
  *Journal of Economic Dynamics and Control* 31(11), 3503–3544. — Four states for
  stocks and bonds jointly, and the dynamic programme that uses them.
- **Ang, A. & Timmermann, A. (2012).** ["Regime Changes and Financial
  Markets."](https://www.nber.org/papers/w17182) *Annual Review of Financial
  Economics* 4, 313–337. — **The single best entry point.** Balanced, current
  enough, and honest about what the models do not deliver.
- **Sims, C. A. & Zha, T. (2006).** "Were There Regime Switches in U.S. Monetary
  Policy?" *American Economic Review* 96(1), 54–81. — Rigorous multivariate
  switching applied to policy, with the recurring result: variances switch,
  and coefficients barely do. [publisher — paywalled]
- **Henkel, S. J., Martin, J. S. & Nardari, F. (2011).** "Time-Varying
  Short-Horizon Predictability." *Journal of Financial Economics* 99(3), 560–580.
  — Return predictability concentrated in recessions. The strongest published
  case for regime-conditional expected returns.
- **Schaller, H. & van Norden, S. (1997).** ["Regime Switching in Stock Market
  Returns."](https://doi.org/10.1080/096031097333745) *Applied Financial
  Economics* 7(2), 177–191. [publisher — paywalled] — Stock-market regimes whose
  transitions depend on deviations from fundamentals.
- **Rydén, T., Teräsvirta, T. & Åsbrink, S. (1998).** ["Stylized Facts of Daily
  Return Series and the Hidden Markov
  Model."](https://doi.org/10.1002/(SICI)1099-1255(199805/06)13:3%3C217::AID-JAE476%3E3.0.CO;2-V)
  *Journal of Applied Econometrics* 13(3), 217–244. [publisher — paywalled] —
  What a Gaussian HMM reproduces in daily returns, and the one fact it misses:
  the slow decay of autocorrelation in absolute returns.
- **Maheu, J. M. & McCurdy, T. H. (2000).** ["Identifying Bull and Bear Markets in
  Stock Returns."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=146531)
  *Journal of Business & Economic Statistics* 18(1), 100–112. — Duration-dependent
  switching on 160 years of monthly data. Bull markets have a declining hazard.
- **Perez-Quiros, G. & Timmermann, A. (2000).** ["Firm Size and Cyclical
  Variations in Stock Returns."](https://doi.org/10.1111/0022-1082.00246)
  *Journal of Finance* 55(3), 1229–1262. [publisher — paywalled] — Time-varying
  transitions driven by monetary indicators, with small firms most exposed to the
  recession state.
- **Hardy, M. R. (2001).** ["A Regime-Switching Model of Long-Term Stock
  Returns."](https://doi.org/10.1080/10920277.2001.10595984) *North American
  Actuarial Journal* 5(2), 41–53. [publisher — paywalled] — The two-state
  regime-switching lognormal model, used for long-dated equity guarantees (§6.10).
- **Lunde, A. & Timmermann, A. (2004).** ["Duration Dependence in Stock Prices:
  An Analysis of Bull and Bear
  Markets."](https://doi.org/10.1198/073500104000000136) *Journal of Business &
  Economic Statistics* 22(3), 253–273. [publisher — paywalled] — Duration
  dependence in bull and bear markets dated by price rules.
- **Bulla, J. & Bulla, I. (2006).** ["Stylized Facts of Financial Time Series and
  Hidden Semi-Markov
  Models."](https://ideas.repec.org/a/eee/csdana/v51y2006i4p2192-2209.html)
  *Computational Statistics & Data Analysis* 51(4), 2192–2209. — Negative
  binomial sojourns reproduce the autocorrelation of squared returns better than
  geometric ones.
- **Kim, C.-J., Piger, J. & Startz, R. (2008).** ["Estimation of Markov
  Regime-Switching Regression Models with Endogenous
  Switching."](https://ideas.repec.org/p/fip/fedlwp/2003-015.html) *Journal of
  Econometrics* 143(2), 263–273. — What changes when the state is correlated
  with the shocks, and how to test for it.
- **Bulla, J. (2011).** ["Hidden Markov Models with t Components. Increased
  Persistence and Other Aspects."](https://doi.org/10.1080/14697681003685563)
  *Quantitative Finance* 11(3), 459–475. [publisher — paywalled] — Student-t
  emissions make the fitted states more persistent. The most useful single
  refinement for daily data (§6.3).
- **Guidolin, M. (2011).** ["Markov Switching Models in Empirical
  Finance."](https://doi.org/10.1108/S0731-9053(2011)000027B004) *Advances in
  Econometrics* 27B, 1–86. [publisher — paywalled] — A long survey of the
  applications, model by model.
- **Nystrup, P., Madsen, H. & Lindström, E. (2015).** ["Stylised Facts of
  Financial Time Series and Hidden Markov Models in Continuous
  Time."](https://ideas.repec.org/a/taf/quantf/v15y2015i9p1531-1541.html)
  *Quantitative Finance* 15(9), 1531–1541. — Documents how fitted HMM parameters
  drift through time.
- **Nystrup, P., Madsen, H. & Lindström, E. (2017).** ["Long Memory of Financial
  Time Series and Hidden Markov Models with Time-Varying
  Parameters."](https://orbit.dtu.dk/en/publications/long-memory-of-financial-time-series-and-hidden-markov-models-wit-2/)
  *Journal of Forecasting* 36(8), 989–1002. — Adaptive estimation with
  exponential forgetting. Time-varying parameters reproduce long memory and
  improve density forecasts (§6.8).
- **Kole, E. & van Dijk, D. (2017).** ["How to Identify and Forecast Bull and
  Bear Markets?"](https://doi.org/10.1002/jae.2511) *Journal of Applied
  Econometrics* 32(1), 120–139. [publisher — paywalled] — Price rules date
  regimes better in sample. Regime-switching models forecast better.
- **Farmer, L. E., Schmidt, L. & Timmermann, A. (2023).** ["Pockets of
  Predictability."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3152386)
  *Journal of Finance* 78(3), 1279–1341. — Predictability arrives in short local
  episodes rather than as a stable relationship. Read with the replication in
  §4.4.

## 4.4 The critiques — read these next to §4.3

A bibliography that lists only a field's successes gives a one-sided view. These
papers limit what you should believe.

- **Hansen, B. E. (1992).** ["The Likelihood Ratio Test under Nonstandard
  Conditions: Testing the Markov Switching Model of
  GNP."](https://users.ssc.wisc.edu/~behansen/papers/jae_92.html) *Journal of
  Applied Econometrics* 7(S1), S61–S82. — A standard LR test cannot test
  the number of regimes, because the transition probabilities are unidentified
  under the null. Applying a valid bound, **Hamilton's own model does not reject
  a plain AR(4)**. This is the most important critique in the field and the least
  cited relative to its importance.
- **Garcia, R. (1998).** ["Asymptotic Null Distribution of the Likelihood Ratio
  Test in Markov Switching Models."](https://doi.org/10.2307/2527399) *International Economic Review* 39(3),
  763–788. — Works out the correct asymptotics in specific cases.
- **Cho, J. S. & White, H. (2007).** ["Testing for Regime
  Switching."](https://doi.org/10.1111/j.1468-0262.2007.00809.x) *Econometrica* 75(6), 1671–1720. — The modern treatment of the same problem.
- **Dacco, R. & Satchell, S. (1999).** ["Why Do Regime-Switching Models Forecast
  So Badly?"](https://onlinelibrary.wiley.com/doi/abs/10.1002/(SICI)1099-131X(199901)18:1%3C1::AID-FOR685%3E3.0.CO;2-B)
  *Journal of Forecasting* 18(1), 1–16. — The models fit excellently in sample and forecast
  worse than a random walk out of sample. The paper analyses *why*: state misclassification
  costs more than correct state parameters gain. [publisher — paywalled]
- **Diebold, F. X. & Inoue, A. (2001).** ["Long Memory and Regime
  Switching."](https://www.nber.org/papers/t0264) *Journal of Econometrics*
  105(1), 131–159. — Regime switching and long memory are analytically confusable
  even asymptotically. The observational-equivalence problem stated precisely.
- **Granger, C. W. J. & Hyung, N. (2004).** "Occasional Structural Breaks and
  Long Memory with an Application to the S&P 500 Absolute Stock Returns."
  *Journal of Empirical Finance* 11(3), 399–421. — The same confusion,
  demonstrated on real data.
- **Perron, P. (1989).** "The Great Crash, the Oil Price Shock, and the Unit Root
  Hypothesis." *Econometrica* 57(6), 1361–1401. — The precedent from a different
  literature: breaks and persistence are nearly indistinguishable in finite
  samples. The lesson generalises.
- **Forbes, K. J. & Rigobon, R. (2002).** ["No Contagion, Only Interdependence:
  Measuring Stock Market Comovements."](https://www.nber.org/papers/w7267)
  *Journal of Finance* 57(5), 2223–2261. — Correlation measured on
  high-volatility subsamples is biased upward for mechanical reasons. Correct for
  it before claiming a correlation regime.
- **Psaradakis, Z. & Spagnolo, N. (2003).** ["On the Determination of the Number
  of Regimes in Markov-Switching Autoregressive
  Models."](https://doi.org/10.1111/1467-9892.00305) *Journal of Time Series
  Analysis* 24(2), 237–252. — Information criteria for $K$, and how badly they
  behave.
- **Cakici, N. et al. (2025).** ["Pockets of Predictability: A
  Replication."](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.13484)
  *Journal of Finance* 80(6), 3771–3790. — Disputes the economic significance of the Farmer et al.
  result. Cite the original and this together or neither.

## 4.5 Structural breaks and change-point detection

Structural breaks are a different object from regimes. The literature is adjacent and frequently supplies the better tool (§5.6).

- **Chow, G. C. (1960).** "Tests of Equality Between Sets of Coefficients in Two
  Linear Regressions." *Econometrica* 28(3), 591–605. — The break test everyone
  learns first. It requires a known break date, which you never have.
- **Andrews, D. W. K. (1993).** "Tests for Parameter Instability and Structural
  Change with Unknown Change Point." *Econometrica* 61(4), 821–856. — The
  sup-Wald test that fixes that.
- **Bai, J. & Perron, P. (1998).** "Estimating and Testing Linear Models with
  Multiple Structural Changes." *Econometrica* 66(1), 47–78. — Multiple unknown
  breaks, with a dynamic programme to locate them.
- **Adams, R. P. & MacKay, D. J. C. (2007).** ["Bayesian Online Changepoint
  Detection."](https://arxiv.org/abs/0710.3742) arXiv:0710.3742. — It is online and exact.
  The run-length posterior it produces is a useful
  real-time quantity. The recommended default when the question is "did something just change"
  rather than "which of $K$ states are we in".
- **Killick, R., Fearnhead, P. & Eckley, I. A. (2012).** ["Optimal Detection of
  Changepoints with a Linear Computational
  Cost."](https://arxiv.org/abs/1101.1438) *Journal of the American Statistical
  Association* 107(500), 1590–1598. — PELT. Exact segmentation in
  linear time. It is the standard tool for offline analysis.
- **Truong, C., Oudre, L. & Vayatis, N. (2020).** "Selective Review of Offline
  Change Point Detection Methods." *Signal Processing* 167, 107299. — The survey,
  and the paper behind the `ruptures` package.

## 4.6 Practitioner and allocation work

This material is often the most directly usable, and its authors often sell the
product it describes. The entries note these interests.

- **Chow, G., Jacquier, E., Kritzman, M. & Lowry, K. (1999).** "Optimal
  Portfolios in Good Times and Bad." *Financial Analysts Journal* 55(3), 65–73. —
  The original "split the sample by turbulence and optimise separately" idea.
- **Kritzman, M. & Li, Y. (2010).** "Skulls, Financial Turbulence, and Risk
  Management." *Financial Analysts Journal* 66(5), 30–41. — The Mahalanobis
  turbulence index: a single scalar regime indicator with no latent state and no
  estimation problem. Underrated because it is simple.
- **Kritzman, M., Page, S. & Turkington, D. (2012).** ["Regime Shifts:
  Implications for Dynamic
  Strategies."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2066848)
  *Financial Analysts Journal* 68(3), 22–39. — The practitioner framework.
  **[Contested]** — the authors' firm sells regime-based analytics, and the
  backtests do not adjust for specification search.
- **Kritzman, M., Li, Y., Page, S. & Rigobon, R. (2011).** "Principal Components
  as a Measure of Systemic Risk." *Journal of Portfolio Management* 37(4),
  112–126. — The absorption ratio. A regime indicator built from the eigenvalue
  concentration of the correlation matrix rather than from returns.
- **Bulla, J., Mergner, S., Bulla, I., Sesboüé, A. & Chesneau, C. (2011).**
  ["Markov-Switching Asset Allocation: Do Profitable Strategies
  Exist?"](https://mpra.ub.uni-muenchen.de/21154/) *Journal of Asset Management*
  12(5), 310–321. — An honest out-of-sample test with transaction costs across
  three markets and forty years. The answer is a qualified yes, and the mechanism
  is volatility avoidance, not return prediction.
- **Ang, A. & Bekaert, G. (2004).** ["How Regimes Affect Asset
  Allocation."](https://www.nber.org/papers/w10080) *Financial Analysts Journal*
  60(2), 86–99. — The practitioner version of their 2002 paper: regime-switching
  allocation with a risk-free asset available.
- **Nystrup, P., Hansen, B. W., Madsen, H. & Lindström, E. (2015).**
  ["Regime-Based Versus Static Asset Allocation: Letting the Data
  Speak."](https://doi.org/10.3905/jpm.2015.42.1.103) *Journal of Portfolio
  Management* 42(1), 103–109. [publisher — paywalled] — Two-state regime
  inference driving allocation, against a static benchmark.
- **Nystrup, P., Madsen, H. & Lindström, E. (2018).** "Dynamic Portfolio
  Optimization Across Hidden Market Regimes." *Quantitative Finance* 18(1),
  83–95. — Careful work on the allocation problem with adaptive estimation.
  [publisher — paywalled]
- **Nystrup, P., Kolm, P. N. & Lindström, E. (2020).** ["Greedy Online
  Classification of Persistent Market States Using Realized Intraday Volatility
  Features."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3594875)
  *Journal of Financial Data Science* 2(3), 25–39. — The statistical jump model
  applied online, with the striking claim that it beats a correctly specified
  maximum-likelihood HMM on classification accuracy. **[Contested]**, and worth
  replicating yourself. The likely source of the advantage is that a jump
  penalty is a better-conditioned way to impose persistence than a transition
  matrix estimated from few transitions (§7.2).
- **Bemporad, A., Breschi, V., Piga, D. & Boyd, S. (2018).** ["Fitting Jump
  Models."](https://arxiv.org/abs/1711.09220) *Automatica* 96, 11–21. — The
  method itself, from the control literature. Read this before the finance
  applications.
- **Asness, C., Ilmanen, A. & Maloney, T. (2017).** "Market Timing: Sin a
  Little." *Journal of Investment Management* 15(3), 23–40. — The best statement
  of the sceptical practitioner position on conditioning: timing works a bit,
  and much less than it appears to. **[Contested]** — AQR sells the strategies
  that do not require timing.

## 4.7 Dataset shift, conditioning, and learned states

- **Quiñonero-Candela, J., Sugiyama, M., Schwaighofer, A. & Lawrence, N. D., eds.
  (2009).** *Dataset Shift in Machine Learning.* MIT Press. — The source of the
  covariate-shift and concept-drift terms that §9 uses.
- **Shimodaira, H. (2000).** "Improving Predictive Inference under Covariate
  Shift by Weighting the Log-Likelihood Function." *Journal of Statistical
  Planning and Inference* 90(2), 227–244. — Importance weighting, and the precise
  conditions under which it helps. It helps less often than people assume.
- **Gama, J., Žliobaitė, I., Bifet, A., Pechenizkiy, M. & Bouchachia, A. (2014).**
  ["A Survey on Concept Drift
  Adaptation."](https://mpechen.win.tue.nl/publications/pubs/Gama_ACMCS_AdaptationCD_accepted.pdf)
  *ACM Computing Surveys* 46(4), article 44. — The taxonomy of drift types and
  adaptation strategies. Almost everything finance calls "regime handling" is in
  here under another name, usually with more careful evaluation.
- **Jacobs, R. A., Jordan, M. I., Nowlan, S. J. & Hinton, G. E. (1991).**
  "Adaptive Mixtures of Local Experts." *Neural Computation* 3(1), 79–87. — The
  original mixture of experts. A gated regime model in everything but name, and
  thirty years older than the finance papers that reinvent it.
- **Peters, J., Bühlmann, P. & Meinshausen, N. (2016).** ["Causal Inference by
  Using Invariant Prediction: Identification and Confidence
  Intervals."](https://web.math.ku.dk/~peters/jonas_files/InvariantCausalPrediction.pdf)
  *Journal of the Royal Statistical Society: Series B* 78(5), 947–1012. — The
  inverse of regime modelling. Instead of adapting to each regime, it finds the
  relationship that is *invariant* across them. §9.6 argues that practitioners underuse it,
  and §10.6 rates it the best-value scheme for a model meant to run for years.
- **Arjovsky, M., Bottou, L., Gulrajani, I. & Lopez-Paz, D. (2019).**
  ["Invariant Risk Minimization."](https://arxiv.org/abs/1907.02893)
  arXiv:1907.02893. — The deep-learning version. Read with Rosenfeld,
  Ravikumar and Risteski, ["The Risks of Invariant Risk
  Minimization"](https://arxiv.org/abs/2010.05761) (ICLR 2021), which shows it
  can fail badly outside its assumptions.
- **Grinsztajn, L., Oyallon, E. & Varoquaux, G. (2022).** ["Why Do Tree-Based
  Models Still Outperform Deep Learning on Typical Tabular
  Data?"](https://arxiv.org/abs/2207.08815) NeurIPS Datasets and Benchmarks. —
  Why tree ensembles beat networks on tabular data, mechanistically: trees handle
  irregular target functions and tolerate uninformative features. Both properties
  matter for regime features (§10.8).
- **Gu, S., Kelly, B. & Xiu, D. (2020).** ["Empirical Asset Pricing via Machine
  Learning."](https://www.nber.org/papers/w25398) *Review of Financial Studies*
  33(5), 2223–2273. — The benchmark ML asset-pricing study. It handles
  regimes by interacting characteristics with eight observable macro predictors
  and letting trees and networks find the structure. It uses no latent state model.
- **Chen, L., Pelger, M. & Zhu, J. (2024).** ["Deep Learning in Asset
  Pricing."](https://arxiv.org/abs/1904.00745) *Management Science* 70(2),
  714–750. — Learns a latent macroeconomic state with an LSTM as part of an
  end-to-end no-arbitrage objective. The most sophisticated published example of
  the "let the network find the regime" approach.
- **Kelly, B., Malamud, S. & Zhou, K. (2024).** ["The Virtue of Complexity in
  Return Prediction."](https://www.nber.org/papers/w30217) *Journal of Finance*
  79(1), 459–503. — Argues against the instinct that instability demands simple
  models. Heavily overparameterised models with strong shrinkage do better than
  parsimonious ones, even in short samples. **[Contested]** and directly relevant
  to whether you should be subsetting your data by regime at all (§10.4).
- **Linderman, S. et al. (2017).** ["Bayesian Learning and Inference in Recurrent
  Switching Linear Dynamical
  Systems."](https://proceedings.mlr.press/v54/linderman17a.html) AISTATS. —
  Latent discrete states whose transitions depend on the continuous state.
  The most natural modern generalisation of Hamilton's model, from neuroscience.
- **Perez, E., Strub, F., de Vries, H., Dumoulin, V. & Courville, A. (2018).**
  ["FiLM: Visual Reasoning with a General Conditioning
  Layer."](https://ojs.aaai.org/index.php/AAAI/article/view/11671) *AAAI*. —
  Feature-wise linear modulation: conditioning information produces a per-channel
  scale and shift on hidden activations. The correct way to inject a regime into
  a network (§10.8), from a completely unrelated field.
- **Shazeer, N. et al. (2017).** ["Outrageously Large Neural Networks: The
  Sparsely-Gated Mixture-of-Experts Layer."](https://arxiv.org/abs/1701.06538)
  ICLR. — Mixture of experts at scale, with the load-balancing and
  expert-collapse problems that §10.5 warns about, solved at a much larger
  scale.
- **Gibbs, I. & Candès, E. (2021).** ["Adaptive Conformal Inference Under
  Distribution Shift."](https://arxiv.org/abs/2106.00170) NeurIPS. — Prediction
  intervals with coverage guarantees that survive distribution shift. A stronger
  guarantee than anything else in this document, and directly usable for sizing.

## 4.8 Evaluation and backtesting

- **Diebold, F. X. & Mariano, R. S. (1995).** "Comparing Predictive Accuracy."
  *Journal of Business & Economic Statistics* 13(3), 253–263. — The base test.
- **Diebold, F. X., Gunther, T. A. & Tay, A. S. (1998).** ["Evaluating Density
  Forecasts with Applications to Financial Risk
  Management."](https://www.nber.org/papers/t0215) *International Economic
  Review* 39(4), 863–883. — The probability integral transform as a check of a
  whole predictive density. It is the basis of HMM pseudo-residuals (§6.9).
- **Giacomini, R. & White, H. (2006).** "Tests of Conditional Predictive
  Ability." *Econometrica* 74(6), 1545–1578. — Tests whether model A beats model
  B *given the current state*, which is exactly the regime question. Should be
  standard in this literature and is not.
- **Giacomini, R. & Rossi, B. (2010).** ["Forecast Comparisons in Unstable
  Environments."](https://ideas.repec.org/p/duk/dukeec/08-4.html) *Journal of
  Applied Econometrics* 25(4), 595–620. — The fluctuation test, which asks whether the relative
  performance of two models changes over time. The single most useful diagnostic
  in this whole document (§11.6).
- **White, H. (2000).** "A Reality Check for Data Snooping." *Econometrica*
  68(5), 1097–1126. — And **Hansen, P. R. (2005)**, "A Test for Superior
  Predictive Ability," *JBES* 23(4), 365–380, which fixes its power problem.
- **Bailey, D. H. & López de Prado, M. (2014).** ["The Deflated Sharpe
  Ratio."](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) *Journal
  of Portfolio Management* 40(5), 94–107. — Adjusts a Sharpe ratio for the number
  of trials and for non-normality. Essential once you start slicing by regime,
  which multiplies trials fast (§11.6).
- **Harvey, C. R., Liu, Y. & Zhu, H. (2016).** "…and the Cross-Section of
  Expected Returns." *Review of Financial Studies* 29(1), 5–68. — The multiple-
  testing problem in finance, with the recommended $t > 3$ threshold.
- **Pesaran, M. H. & Timmermann, A. (2007).** ["Selection of Estimation Window in
  the Presence of
  Breaks."](https://rady.ucsd.edu/_files/faculty-research/timmermann/estimation-window.pdf)
  *Journal of Econometrics* 137(1), 134–161. — How much history to train on when
  the data-generating process changes. The formal version of the question every
  practitioner answers by guessing.
- **López de Prado, M. (2018).** *Advances in Financial Machine Learning.*
  Wiley. — Purged and embargoed cross-validation, combinatorial purged CV,
  triple-barrier labelling. **[Contested]** in places, because the book
  asserts several claims without demonstrating them. But the cross-validation methods in chapters 7 and 12
  are correct, necessary, and not available elsewhere in one place.
- **Arnott, R., Harvey, C. R. & Markowitz, H. (2019).** "A Backtesting Protocol
  in the Era of Machine Learning." *Journal of Financial Data Science* 1(1),
  64–74. — A short checklist worth rereading annually.

## 4.9 If you only read eight things

In this order:

1. **[Ang & Timmermann (2012)](https://www.nber.org/papers/w17182){target="_blank"}** — the survey. Two hours, and you will have an
   overview of the field.
2. **[Hamilton (1989)](https://www.econometricsociety.org/publications/econometrica/1989/03/01/new-approach-economic-analysis-nonstationary-time-series-and){target="_blank"}, §2–3** — the filter, from the source.
3. **[Zucchini, MacDonald & Langrock (2016)](https://doi.org/10.1201/b20790){target="_blank"}** — the practical HMM book:
   estimation, model checking, and the extensions of §6, worked in code.
4. **[Hansen (1992)](https://users.ssc.wisc.edu/~behansen/papers/jae_92.html){target="_blank"}** — why you cannot test what you want to test.
5. **[Dacco & Satchell (1999)](<https://onlinelibrary.wiley.com/doi/abs/10.1002/(SICI)1099-131X(199901)18:1%3C1::AID-FOR685%3E3.0.CO;2-B>){target="_blank"}** — why in-sample fit does not transfer.
6. **[Diebold & Inoue (2001)](https://www.nber.org/papers/t0264){target="_blank"}** — why you might not have regimes at all.
7. **[Gama et al. (2014)](https://mpechen.win.tue.nl/publications/pubs/Gama_ACMCS_AdaptationCD_accepted.pdf){target="_blank"}** — the machine-learning terms for the same problem,
   with better evaluation discipline.
8. **[Bulla et al. (2011)](https://mpra.ub.uni-muenchen.de/21154/){target="_blank"}** — what an honest out-of-sample regime backtest looks
   like, and how modest the answer is.

Items 4, 5, and 6 are the ones that will change what you build. Read them before
you write code, not after your backtest looks good.

---

# 5. The formal models {#5-the-formal-models}

§5 presents the formal models. §7 reduces them to a four-slot design space, so
read §5 for the mechanics and §7 for the overview. The hidden Markov model of §5.2
and §5.3 is the central model, and §6 treats it in depth. §6 covers how to
estimate it, which refinements improve results, and how to use its output.

One rule governs all of the models, and it comes before them.

## 5.1 The filtration ladder

Every regime model produces a belief about the state. **The information set that this belief conditions on is the single largest determinant of measured performance. Choosing it is a research-protocol decision, not a modelling decision.** Getting it wrong invalidates more regime research than all modelling errors combined.

The ladder has five rungs. Results look best at rung 1 and are most realistic at rung 5:

```
  Rung                                          Uses                        Tradable?
  ───────────────────────────────────────────────────────────────────────────────────
  1  Oracle     s_t                             the truth                   never
     └─ upper bound only; the number you can never reach

  2  Smoothed   xi(t|T)   with theta-hat(all)   all data, both directions   never
     └─ what every regime plot in every paper shows

  3  Filtered   xi(t|t)   with theta-hat(all)   all data, one direction     never
     └─ the leak that survives careful-looking pipelines

  4  Filtered   xi(t|t)   with theta-hat(1..t)  data through t              partly
     └─ honest, but r_t is in the conditioning set

  5  Predicted  xi(t|t-1) with theta-hat(..t-1) data through t-1            yes
     └─ the only object you can actually trade at the open of bar t
```

Four distinctions matter, and each has a precise statement:

**Smoothed versus filtered.** $\xi_{t|T} = \Pr(s_t \mid \mathcal{F}_T)$ uses the *entire sample*, including everything that happened after $t$. It is the right object for describing history and the wrong object for every other purpose. The smoother produces the clean, decisive regime plots that appear in papers and pitch decks. These plots teach a false intuition about how sharply regimes can be identified in real time.

**Filtered versus predicted.** $\xi_{t|t}$ conditions on $r_t$. You must set the position for bar $t$ before observing $r_t$. So $\xi_{t|t}$ is unavailable, and you need $\xi_{t|t-1} = \mathbf{P}^{\top}
\xi_{t-1|t-1}$. The gap is one application of the transition matrix, which sounds
trivial but is large. §8.3 measures it at roughly a quarter of the Sharpe ratio in a well-specified simulation where the states are easy to tell apart.

**Parameter leakage.** This leak survives the move to predicted probabilities. Suppose you carefully use only $\xi_{t|t-1}$, but you estimated $\theta$ and $\mathbf{P}$ by maximum likelihood on the whole sample. Then $\xi_{t|t-1}$ depends on the future through $\hat\theta$, and the dependence is large. The fitted state means and variances *define* what "the turbulent state" means. The fit chose them using every turbulent episode in the sample. A model that "discovers" a crash state has therefore used the dates of the crashes.

**Label leakage.** This leak is related to parameter leakage and is worse. State $k$ has no intrinsic identity, because the likelihood is invariant to permuting the labels. Researchers routinely resolve this by sorting states by their fitted mean and calling the low-mean state "bear". Sorting on the full sample and then using the labels in a backtest is look-ahead. This look-ahead produces unrealistically good equity curves. Sort by a monotone, stable quantity, usually realised volatility. Do the sorting inside the expanding window.

> **The protocol.** Label every reported number with its rung. Report rung 5 as the headline. Also report rung 2, as a *diagnostic*. The ratio between the two measures how much of your result is look-ahead. Suppose rung 2 looks strong and rung 5 looks like noise. Then you have found that the regime is identifiable only in hindsight. That is a valid finding. **[Practice]**

## 5.2 The Hamilton filter

The recursion has two lines. Writing them out makes the whole filter clear.

Let $\xi_{t|t}$ be the $K$-vector of filtered state probabilities. Let
$\eta_t$ be the $K$-vector of conditional observation densities,
$\eta_t^{(k)} = f(y_t \mid s_t = k, \mathcal{F}_{t-1}; \theta_k)$. Then:

$$
\begin{aligned}
\text{Predict:} \quad & \xi_{t|t-1} = \mathbf{P}^{\top} \xi_{t-1|t-1} \\[4pt]
\text{Update:} \quad & \xi_{t|t}
   = \frac{\xi_{t|t-1} \odot \eta_t}{\mathbf{1}^{\top}(\xi_{t|t-1} \odot \eta_t)}
\end{aligned}
$$

Here $\odot$ is elementwise multiplication. Start the recursion at $\xi_{0|0} = \boldsymbol{\pi}$ (the stationary distribution) or at a diffuse $1/K$ for each state. The filter has two steps. First it propagates the belief forward through the chain. Then it reweights the belief by how well each state explains the new observation. This is the Kalman filter with a discrete state space. It is also the forward pass of the HMM forward-backward algorithm.

Expand the denominator:

$$
\mathbf{1}^{\top}(\xi_{t|t-1} \odot \eta_t)
  = \sum_{k=1}^{K} \Pr(s_t = k \mid \mathcal{F}_{t-1}) \, f(y_t \mid s_t = k)
  = p(y_t \mid \mathcal{F}_{t-1}),
$$

which is exactly the predictive density of §1.2. So the log-likelihood is

$$
\ell(\theta, \mathbf{P}) = \sum_{t=1}^{T} \ln p(y_t \mid \mathcal{F}_{t-1}),
$$

the sum of one-step-ahead predictive log-densities. **Maximum likelihood for a regime model therefore optimises one-step-ahead density forecasting and nothing else.** Suppose your decision problem is $h$-step-ahead, or asymmetric in the cost of state errors, or depends on a functional of the distribution rather than the whole density. Then maximum likelihood optimises the wrong objective. [Dacco and Satchell (1999)](<https://onlinelibrary.wiley.com/doi/abs/10.1002/(SICI)1099-131X(199901)18:1%3C1::AID-FOR685%3E3.0.CO;2-B>){target="_blank"} identified this mechanism as the reason these models forecast badly. §8.5 returns to this.

**Smoothing.** At the last date, filtered and smoothed probabilities coincide. The [Kim (1994)](<https://doi.org/10.1016/0304-4076(94)90036-1>){target="_blank"} backward recursion starts from $\xi_{T|T}$ and runs from $t = T-1$ down:

$$
\xi_{t|T}^{(j)} = \xi_{t|t}^{(j)} \sum_{k=1}^{K}
  \frac{p_{jk} \, \xi_{t+1|T}^{(k)}}{\xi_{t+1|t}^{(k)}} .
$$

The formula reweights the filtered belief at $t$ by how much the future supported each of the states that $t$ could have led to.

**Numerical practice.** Three numerical problems arise. (i) The elementwise products underflow for long series. Either rescale $\xi$ to sum to one at every step, as written above, or work in log space with `logsumexp`. Rescaling loses nothing. The log of each denominator is the term $\ln p(y_t \mid \mathcal{F}_{t-1})$ of $\ell$, so the log-likelihood is the running sum of those logs. (ii) The likelihood is multimodal, and EM converges to a local optimum. Restart from many initialisations and keep the best. (iii) Any state can collapse onto a single observation with $\sigma_k \to 0$ and likelihood $\to \infty$. This is the classic degeneracy of Gaussian mixtures. Bound $\sigma_k$ from below or put a prior on it. On daily financial returns with $K \ge 3$ this happens routinely.

## 5.3 Markov-switching regressions {#53-markov-switching-regressions}

**Intuition.** The data follow $K$ different relationships, and a hidden Markov chain selects which one is active. This is the hidden Markov model with regressions as its emissions. §6 covers estimation and the practical refinements.

**Definition.** For a regression target $y_t$ and predictors $x_t$,

$$
y_t = x_t^{\top}\beta_{s_t} + \sigma_{s_t}\varepsilon_t, \qquad
\varepsilon_t \sim \mathcal{N}(0,1), \qquad
\Pr(s_t = k \mid s_{t-1} = j) = p_{jk}.
$$

Three special cases follow. $x_t = 1$ gives switching means. $x_t = (1, y_{t-1}, \dots)$ gives the Markov-switching autoregression of [Hamilton (1989)](https://www.econometricsociety.org/publications/econometrica/1989/03/01/new-approach-economic-analysis-nonstationary-time-series-and){target="_blank"}. A vector $y_t$ gives MS-VAR.

**Assumptions.** Four assumptions apply. The chain is first-order and homogeneous, meaning the transition probabilities are constant through time. The state is independent of the innovation given the past. $K$ is known. The emission family is correctly specified. The first and third assumptions are the ones that fail. Time-varying transition probabilities are the rule, not the exception. §6.6 solves the problem within this framework by letting the transition probabilities depend on lagged observables. §5.5 avoids it by dropping the latent Markov chain. It uses a state that is an explicit function of an observable $z$.

**Strengths.** The model is interpretable and likelihood-based. It gives a full predictive density, and the filter is exact. It handles the idea of a different relationship in different conditions directly, rather than through interactions.

**Weaknesses.** The parameter count grows as $K$ times (the number of regression coefficients, plus one for $\sigma_k$), plus $K^2$ transition parameters. Strictly, only $K(K-1)$ of the transition parameters are free, because every row of $\mathbf{P}$ sums to one. This chapter uses "$K^2$" as shorthand. Identification is weak (§8.1). Standard methods cannot test the number of states (§8.2).

**Cost.** A likelihood evaluation costs $O(TK^2)$. EM with $I$ iterations costs $O(TK^2 I)$ (§6.1). This is trivial for $K \le 5$ and $T$ in the tens of thousands.

**Failure modes.** (i) A state collapses onto outliers and becomes a "crash detector" that signals once and never generalises. (ii) With $K \ge 3$ and Gaussian emissions on financial data, the extra states almost always split the volatility dimension further. They do not find new mean behaviour. Check this before interpreting them. (iii) Estimated transition probabilities near 1 produce near-absorbing states. The model then fits a one-time break rather than a recurrent regime, and the out-of-sample state belief stays in one state.

**When preferred.** Use this model under three conditions. You have a real economic reason to expect a small number of discrete relationship regimes. You want a density forecast rather than a point forecast. And $K \le 3$. For daily returns, start from the variance-only version with Student-t emissions (§6.3).

```{=latex}
\newpage
```

## 5.4 Switching volatility: SWARCH and MS-GARCH

**Intuition.** Volatility clusters *and* jumps between levels. GARCH captures the clustering. A regime captures the level shifts. Combining the two is natural but technically difficult.

**Definition.** The naive combination is

$$
\sigma_t^2 = \omega_{s_t} + \alpha_{s_t}a_{t-1}^2 + \beta_{s_t}\sigma_{t-1}^2,
$$

Here $a_t = \sigma_t\varepsilon_t$ is the unstandardised innovation, and $\omega$, $\alpha$ and $\beta$ are GARCH coefficients. This $\beta$ is not the regression coefficient of §5.3. The model is **inestimable**. $\sigma_{t-1}^2$ depends on $s_{t-1}$ and on $\sigma_{t-2}^2$. That term depends on $s_{t-2}$ and on $\sigma_{t-3}^2$, and so on back to the start of the sample. Evaluating the likelihood at time $t$ therefore requires summing over all $K^t$ state paths. This path dependence made MS-GARCH hard to estimate for a decade. [Gray (1996)](<https://doi.org/10.1016/0304-405X(96)00875-6>){target="_blank"} solves it by collapsing the conditional variance across states at each step. [Haas, Mittnik and Paolella (2004)](https://doi.org/10.1093/jjfinec/nbh020){target="_blank"} solve it more cleanly. They run $K$ *parallel*, non-interacting GARCH recursions and let the state select which one is observed.

**Assumptions.** The assumptions of §5.3 apply, plus a GARCH functional form within each state.

**Strengths.** [Hamilton and Susmel's (1994)](<https://doi.org/10.1016/0304-4076(94)90067-1>){target="_blank"} central finding is that **a large part of what a single-regime GARCH interprets as extreme volatility persistence is actually regime persistence.** Fit GARCH to a series with two volatility levels, and you get $\alpha + \beta \approx 0.99$. This is an integrated process, and its forecasts revert far too slowly. Allowing the level to switch returns the within-regime persistence to plausible values.

**Weaknesses.** The model has many parameters ($K$ GARCH triples plus $K^2$ transitions), and the estimation is badly conditioned. **[Contested]** In head-to-head out-of-sample volatility forecasting, simple alternatives such as HAR on realised volatility or an EWMA are hard to beat. The published comparisons are sensitive to the loss function and the sample.

**Cost.** The Haas et al. formulation costs $O(TK^2)$. The Gray formulation costs about the same but uses a collapsing approximation.

**Failure modes.** (i) The high-volatility state absorbs a handful of crisis days, so its GARCH parameters are estimated from almost no data. (ii) With $K = 3$ the middle state is frequently uninterpretable and unstable. (iii) The model's volatility forecast jumps discontinuously at a transition. This produces large discrete position changes in a vol-targeted strategy. The changes are a costly artefact of the discretisation, not a feature.

**When preferred.** Use this model when you need a *density* forecast whose shape changes with the state, not just a variance forecast. If you need only the variance, use HAR or EWMA. They are simpler. **[Practice]**

## 5.5 Observable-threshold models: TAR, SETAR, STAR

**Intuition.** Treat the state as observable. Define it as a function of a quantity you can see.

**Definition.** A threshold autoregression makes the regime a deterministic
function of an observable $z_{t-\kappa}$:

$$
y_t = \begin{cases}
x_t^{\top}\beta_1 + \sigma_1\varepsilon_t & \text{if } z_{t-\kappa} \le c \\
x_t^{\top}\beta_2 + \sigma_2\varepsilon_t & \text{if } z_{t-\kappa} > c
\end{cases}
$$

The model has threshold $c$ and delay $\kappa \ge 1$, so the regime is known before bar $t$ opens. A grid search over the likelihood estimates both. When $z$ is a lag of $y$ itself, this is a *self-exciting* TAR (SETAR; Tong, 1983). The *smooth
transition* version (STAR; Teräsvirta, 1994) replaces the indicator with a logistic or exponential function of $(z_{t-\kappa} - c)$. This gives a continuous blend between the two regimes:

$$
y_t = \big(1 - G(z_{t-\kappa}; \gamma, c)\big) \, x_t^{\top}\beta_1
    + G(z_{t-\kappa}; \gamma, c) \, x_t^{\top}\beta_2 + \sigma\varepsilon_t,
\qquad
G(z;\gamma,c) = \frac{1}{1 + e^{-\gamma(z - c)}} .
$$

The weight $G$ rises from 0 to 1 as $z$ crosses $c$, and $\gamma > 0$ sets how fast. As $\gamma \to \infty$, the weight becomes the indicator $\mathbb{1}[z > c]$, and the model reduces to the threshold model above. As $\gamma \to 0$, the weight flattens to $\tfrac12$, and the model reduces to a single regression.

**Assumptions.** The correct conditioning variable is observable and known. The whole model depends on this assumption.

**Strengths.** The model needs no filtering and no latent state. The state estimate has no look-ahead, because the regime at time $t$ is a function of data you had before $t$. Estimation is a grid search over $(c, \kappa)$ with OLS inside. It is fast and has no local-optimum problem worth worrying about. **This advantage is much larger than the literature's relative neglect of these models suggests.** It also explains why practitioner "regime" definitions are threshold models, whether or not anyone says so. Examples are VIX above 25, price below the 200-day average and an inverted yield curve.

**Weaknesses.** You must choose $z$. If the true state driver is not in your candidate set, the model cannot find it. An HMM can find it in principle. Profiling the likelihood estimates the threshold $c$, which is a multiple-testing exercise. Searching 100 thresholds and reporting the best fit without adjustment is a specification search.

**Cost.** The cost is $O(T \cdot |C| \cdot |L|)$ for a grid $C$ of thresholds and a grid $L$ of delays. This is cheap.

**Failure modes.** (i) The threshold is unstable. Refit on a new sample and $c$ moves, so the historical labelling changes retroactively. Fix $c$ at a round number chosen a priori, and you lose fit but keep the other advantages of the model. (ii) A threshold on a *non-stationary* $z$, such as a price level or an unnormalised spread, gives a regime definition that drifts out of range. Always threshold a normalised quantity. (iii) The hard-indicator version produces one-day round trips when $z$ stays at the threshold. See hysteresis in §12.2.

**When preferred.** **This model should be your default.** If you can name the observable that defines your regime, a threshold or smooth-transition model gives you 80% of what an HMM gives with a tenth of the fragility. The smooth version also removes the choppiness at no extra cost. Use a latent-state model only after you have tried this model and found that the observable is unavailable. **[Practice]**

## 5.6 Structural breaks and change-point detection

**Intuition.** This method asks a different question. It asks "did the process change, and when", not "which of $K$ recurring states are we in".

**Definition.** Offline, the multiple-break model of Bai and Perron (1998)
partitions $1..T$ into $m+1$ segments with constant parameters within each.
It chooses break dates by dynamic programming to minimise the sum of segment
residual sums of squares plus a penalty. PELT ([Killick et al., 2012](https://arxiv.org/abs/1101.1438){target="_blank"}) does the
same in $O(T)$. It prunes candidate break dates that can never be optimal, under a
mild condition on the segment cost. Online, Bayesian online
changepoint detection ([Adams & MacKay, 2007](https://arxiv.org/abs/0710.3742){target="_blank"}) maintains a posterior over the *run
length* $\rho_t$, which is the time since the last change. It uses a message-passing
recursion. It gives $p(y_{t+1} \mid y_{1:t})$ as a run-length-weighted mixture.

**Assumptions.** Breaks are permanent, not recurrent. Segments are independent
given the break structure.

**Strengths.** BOCPD in particular produces an output that a regime model does not. It gives an explicit, calibrated answer to "how confident am I that the world just changed". The answer is available in real time and needs no specification of $K$. Its run-length posterior is a useful input to a sizing rule (§12.1).

**Weaknesses.** Non-recurrence is the fundamental limitation. After a break, you
have no data on the new regime. Any model that
needs $\theta_{\text{new}}$ must start from scratch. [Pesaran and Timmermann
(2007)](https://rady.ucsd.edu/_files/faculty-research/timmermann/estimation-window.pdf){target="_blank"} show an important consequence: **it can be optimal to
include pre-break data in estimation**. The bias from the old regime is
sometimes smaller than the variance from a short post-break sample.

**Cost.** Bai-Perron costs $O(T^2)$. PELT costs $O(T)$ amortised. BOCPD with run-length truncation costs $O(1)$ per step and $O(T)$ in total. Without truncation it costs $O(t)$ per step and $O(T^2)$ in total.

**Failure modes.** (i) Every change-point method detects volatility changes and almost never detects mean changes. This is the same asymmetry as in §8.1, for the same reason. (ii) The penalty parameter directly controls how many breaks you find, and researchers nearly always tune it by eye. (iii) Detection of end-of-sample breaks is delayed by construction. Those are the breaks you most need to detect.

**When preferred.** Use change-point detection when the question is "has something changed", not "which state are we in". Examples are model monitoring, deciding when to retrain (§12.6) and detecting that a strategy has stopped working. For these jobs it clearly beats an HMM.

## 5.7 Statistical jump models

**Intuition.** Keep the discrete state and the persistence, and drop the probability model. Penalise switching directly instead of using a transition matrix.

**Definition.** The features are $u_t \in \mathbb{R}^d$, typically volatility, downside deviation and trend measures computed over several windows. Fit $K$ centroids $\{c_k\}$ and a state path $\{s_t\}$ that minimise

$$
\min_{\{c_k\}, \{s_t\}} \ \sum_{t=1}^{T} \lVert u_t - c_{s_t} \rVert^2
  \; + \; \lambda \sum_{t=2}^{T} \mathbb{1}[s_t \ne s_{t-1}] .
$$

The first term is $k$-means. The second term is a **jump penalty** with a single
tunable $\lambda$ that controls persistence. The optimisation alternates between two steps. The first step assigns states by dynamic programming given the centroids. This step is exact and costs $O(TK^2)$, and it is a Viterbi-style recursion. The second step updates each centroid to the mean of the observations assigned to it. The
recursion carries $V_t(k)$, the lowest cost of any path that ends in state $k$ at
$t$:
$V_t(k) = \lVert u_t - c_k \rVert^2 + \min\{V_{t-1}(k),\ \min_{j \ne k} V_{t-1}(j) + \lambda\}$.
Staying has no cost, and switching costs $\lambda$. [Bemporad
et al. (2018)](https://arxiv.org/abs/1711.09220){target="_blank"} develop the general form. [Nystrup, Kolm and Lindström (2020)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3594875){target="_blank"} apply
it online to market states.

**Assumptions.** The regime is characterised by the *location* of a feature vector. A single scalar can impose persistence, in place of a $K \times K$ matrix.

**Strengths.** The model has three strengths. (i) **It uses one persistence parameter instead of $K^2$.** A validation objective estimates it, not the handful of observed transitions. This is the specific fix for the small-sample problem of §6.1. (ii) It makes no explicit distributional assumption on returns. §7.2 shows the implicit assumption. So it has no Gaussian-mixture degeneracy and no sensitivity to fat tails. (iii) You choose the feature space. You can put realised volatility, drawdown and dispersion in directly, instead of hoping that a Gaussian mixture on returns recovers them. **[Contested]** Nystrup et al. report that the jump model beats a *correctly specified* maximum-likelihood HMM on classification accuracy in simulation. This is a strong claim from an interested source. The mechanism is plausible, and §7.2 shows why it should hold.

**Weaknesses.** The model has no predictive density, no likelihood, no principled way to compare $K$ and no probabilistic state. It gives a hard label unless you build a soft variant. Feature scaling matters a great deal, and it is an easily overlooked researcher degree of freedom.

**Cost.** Each sweep costs $O\!\left(TK(K+d)\right)$. Scoring every observation against every centroid costs $O(TKd)$, and the dynamic programme costs $O(TK^2)$. The method needs a handful of sweeps. It is fast enough to refit daily on decades of data.

**Failure modes.** (i) Features on different scales silently determine the clustering. Standardise inside the training window. (ii) Tuning $\lambda$ on the same data used to evaluate is a leak. The leak is powerful because $\lambda$ controls turnover and therefore costs. (iii) The state path solves a global optimisation, so the *offline* fitted path is smoothed. Using it directly is rung 2 of §5.1. The online variant avoids this problem, so use it.

**When preferred.** Use the jump model as the default latent-state method for trading applications that need a hard label. It gives up the density forecast. In return it protects against two problems that cause freely estimated HMMs to fail in practice: transition estimation from few events, and emission misspecification. A regularised HMM with Student-t emissions and a sticky prior (§6.3, §6.7) provides much of the same protection and keeps the probabilities. **[Practice]**

## 5.8 Clustering-based regimes

**Intuition.** Regimes are groups of similar days. Cluster the days.

**Definition.** Build a feature vector $u_t$ per period, then apply an unsupervised method. Options are a Gaussian mixture (an HMM with no transition structure), $k$-means, agglomerative clustering and HDBSCAN. For correlation-structure regimes, cluster the sequence of estimated correlation matrices under a suitable metric.

**Assumptions.** Temporal order does not matter for defining the states. It does matter for using them.

**Strengths.** The method is very simple, needs no likelihood and accepts arbitrary features. It avoids the emission-specification problem entirely.

**Weaknesses.** **The method has no persistence.** A plain clustering of days produces a state sequence that switches state back and forth, because the objective gives no reward for staying in a state. Practitioners then smooth the labels post hoc. Smoothing over a centred window is look-ahead. Smoothing over a trailing window gives a slow-moving feature that you could have built directly. The statistical jump model is this method *with* a persistence term, which is why it dominates.

**Cost.** Trivial.

**Failure modes.** (i) Post-hoc label smoothing uses future data. (ii) Clustering on full-sample-standardised features is a leak. (iii) Cluster identity is not stable across refits, so "regime 2" means something different each month.

**When preferred.** Use clustering as an exploratory tool, before committing to a model, to test whether your feature space has any group structure. It is rarely suitable as the production state estimator. Add the persistence term and the method becomes §5.7.

## 5.9 Scalar regime indices

**Intuition.** Skip the state. Build one number that rises in bad times, and condition on it.

**Definition.** Three scalar indices are worth knowing:

- **Financial turbulence** (Kritzman & Li, 2010): the squared Mahalanobis distance of today's cross-asset return vector $\mathbf{r}_t$ from its historical mean, $d_t = (\mathbf{r}_t - \mu)^{\top}\Sigma^{-1}(\mathbf{r}_t - \mu)$. This return vector is not the scalar $r_t$ of the notation block. A trailing window estimates $\mu$ and $\Sigma$. The index is large when returns are individually extreme *or* when the cross-sectional pattern is unusual. The unusual pattern is the informative case. A day where every asset moves a normal amount but in the wrong relative directions scores high.
- **Absorption ratio** (Kritzman, Li, Page & Rigobon, 2011): the fraction of total cross-sectional variance explained by the first $n$ principal components. High absorption means few factors drive the market. It indicates fragility.
- **Implied volatility level and term structure**: VIX, and the sign of the VIX futures basis. These measures are crude and observable, and they are hard to beat.

**Assumptions.** A scalar suffices, and its trailing normalisation is adequate.

**Strengths.** The indices need no latent state, no $K$, no filtering and no label switching. Every value is $\mathcal{F}_t$-measurable by construction if you compute the moments on a trailing window. As a *feature* for a forecasting model (Part II), this class is far more useful than a fitted state posterior. It is continuous and monotone, and it has no identification problem.

**Weaknesses.** The indices have no model behind them. So they give no density forecast and no probability, and they cannot say what the state implies for returns beyond what you fit downstream.

**Failure modes.** (i) Computing $\mu, \Sigma$ on the full sample is the standard mistake. It matters most at the crisis dates you care about. (ii) $\Sigma^{-1}$ is unstable when the number of assets approaches the window length. Shrink it. (iii) Turbulence and realised volatility are highly correlated. So the incremental information over "vol is high" is smaller than the framing suggests. Test the increment explicitly.

**When preferred.** Use a scalar index first, and often last. If a scalar turbulence index gives 90% of the benefit of a four-state MS-VAR, and it usually does, the MS-VAR is a research project rather than a trading edge. **[Practice]**

## 5.10 Deep latent-state models

**Intuition.** Keep the graphical structure of the HMM, a latent state and observations that depend on it. Let neural networks parameterise its components.

**Definition.** Four variants belong to this class:

- **HMM with neural emissions.** $f(y_t \mid s_t = k)$ becomes a network. The filter is unchanged. This is rarely worth the cost, because a Student-t usually fixes emission misspecification more cheaply (§6.3).
- **Recurrent switching linear dynamical systems** ([Linderman et al., 2017](https://proceedings.mlr.press/v54/linderman17a.html){target="_blank"}). A
  discrete state selects a linear dynamical system for a continuous latent
  state $h_t$ (a hidden state, not the forecast horizon $h$). The discrete
  transitions depend on that state: $\Pr(s_t \mid s_{t-1}, h_{t-1})$. This generalises Hamilton's model in the
  direction of §6.6, with a latent covariate.
- **Deep state-space models** (deep Kalman filters, structured inference
  networks). These models have a continuous latent state with amortised variational inference.
  They are not regime models in the discrete sense, but they serve the same purpose.
- **A learned state inside a task network** ([Chen, Pelger & Zhu, 2024](https://arxiv.org/abs/1904.00745){target="_blank"}). A
  recurrent network compresses macro series into a low-dimensional state. The state
  feeds an asset-pricing objective, and the whole network trains end to end. No separate regime model
  exists. The state takes whatever form serves the task (§10.7).

**Strengths.** The models are expressive and allow state-dependent transitions. In the end-to-end case, training optimises the state for the decision, not for one-step density forecasting (§5.2).

**Weaknesses.** These models have all of the identification problems of §8, plus variational approximation error, plus many more hyperparameters. The samples support none of this. The financial applications rarely report the stability diagnostics of §2.7.

**Failure modes.** (i) Posterior collapse. The model ignores the latent state and becomes a plain autoregression, and the loss shows no symptom. (ii) The learned state is a noisy proxy for realised volatility. Regress it on volatility before claiming anything else. (iii) The specification search is large and unadjusted.

**When preferred.** Use the end-to-end form when you have a large panel and a clear downstream objective. As a standalone state estimator for a single series, essentially never use these models, because the data do not support them.

## 5.11 Supervised regime labels

**Intuition.** Define the regime by what happened next, then train a classifier
to predict it.

**Definition.** Construct a label from forward information. Three examples follow. A volatility label is "the next 20 days had realised volatility above the 80th percentile". A trend-scanning label fits a line over a forward window and takes the sign of its $t$-statistic. A triple-barrier label (López de Prado, 2018) records which of a profit-taking, stop-loss or time barrier the path hit first. Then train a supervised model to predict that label from $\mathcal{F}_t$ features.

**Strengths.** The method makes the target explicit and decision-relevant. This is a real advantage over unsupervised states, whose meaning is whatever the likelihood found. It also converts the problem into standard supervised learning, which brings standard evaluation tools.

**Weaknesses and the central problem.** The label spans $(t, t+h]$ while the features stop at $t$. So **adjacent training examples share outcome data and are massively dependent**. Standard $k$-fold cross-validation on such a dataset is meaningless, not merely slightly optimistic, because a fold boundary at $t$ puts overlapping labels on both sides. Purging and embargo solve this problem (§11.3). It is *the* reason financial ML papers with 0.9 AUC fail on live data.

**Failure modes.** (i) Unpurged CV, as above. (ii) Labels defined with full-sample percentile thresholds, such as "the top quintile of forward volatility". The threshold itself is look-ahead, so use an expanding-window quantile. (iii) Class balance shifts across time, so the classifier learns the base rate of the training era rather than the signal.

**When preferred.** Use supervised labels when you want a regime for a specific decision and can state that decision as a forward-looking event. In trading this is most of the time. **Recommendation:** when the regime feeds one decision that can be stated as a forward event, prefer a supervised, purged formulation to an unsupervised state posterior. **[Practice]**

```{=latex}
\newpage
```

## 5.12 Comparison

The ratings are this chapter's assessment. They are not measured quantities. "Real-time" means the state estimate at $t$ uses only $\mathcal{F}_t$ without additional computation. The table lists the three HMM refinements of §6 with the other methods, because they change the attributes that distinguish the methods.

| Method | State type | Persistence | Real-time | Params | Density forecast | Main failure |
|---|---|---|---|---|---|---|
| MS regression (§5.3) | latent, soft | Markov | filter needed | $K(d+1) + K^2$ | yes | weak identification |
| HMM, Student-t, sticky prior (§6.3, §6.7) | latent, soft | Markov, regularised | filter needed | $3K + K^2$ | yes | constant hazard |
| Hidden semi-Markov (§6.5) | latent, soft | explicit durations | filter needed | $4K + K^2$ | yes | few spells to fit durations |
| HMM with TVTP (§6.6) | latent, soft | Markov, driven by $z$ | filter needed | $2K + K^2\dim(z)$ | yes | overfits transitions |
| MS-GARCH (§5.4) | latent, soft | Markov | filter needed | $3K + K^2$ | yes | over-parameterised |
| Threshold / STAR (§5.5) | observed | via $z$ | **yes** | $2d + 4$ | yes | must choose $z$ |
| Change-point (§5.6) | run length | by construction | yes (BOCPD) | few | yes (BOCPD) | non-recurrent |
| Jump model (§5.7) | latent, hard | jump penalty | yes (online) | $Kd + 1$ | no | no likelihood |
| Clustering (§5.8) | latent, hard | **none** | yes | $Kd$ | no | switches back and forth |
| Scalar index (§5.9) | observed | via window | **yes** | 0–2 | no | not a model |
| Deep latent (§5.10) | latent, soft | learned | filter needed | many | yes | needs much data |
| Supervised label (§5.11) | defined | by label span | yes | model-dep. | no | CV leakage |

Parameter counts assume Gaussian emissions unless the row says Student-t. They count $K^2$ for the transition matrix, which is the shorthand of §5.3.

> ### §5 Key takeaways
>
> 1. The filtration ladder has five rungs: oracle, smoothed, filtered with leaked parameters, filtered and predicted. The rung determines your measured performance more than your model choice does. Label every reported number with its rung.
> 2. The Hamilton filter has two steps. It propagates the belief through the chain, then reweights it by the observation likelihood. Its normalising constant is the predictive density. So maximum likelihood optimises one-step density forecasting and nothing else.
> 3. The hidden Markov model, known in econometrics as the Markov-switching regression, is the central method among those compared. §6 covers how to fit and use it.
> 4. The estimation of transition probabilities depends on the number of *transitions*, not on the number of observations. Twenty years of daily data may contain forty regime changes. For this reason every useful refinement adds persistence cheaply.
> 5. If you can name the observable that defines your regime, use a threshold or smooth-transition model. It gives most of the benefit without the fragility of a latent-state model. Practitioner regime definitions are already threshold models.
> 6. Two defaults exist for a latent state. A statistical jump model gives a hard label from one persistence parameter, with no distributional assumption. A regularised HMM, with Student-t emissions and a sticky prior, gives calibrated probabilities and a predictive density. Both beat a freely estimated Gaussian HMM.
> 7. Change-point detection answers a different and often better question: "did something just change". BOCPD's run-length posterior is directly usable as a sizing input.
> 8. Supervised regime labels are the natural formulation when the regime serves one forward-looking decision. They have one severe problem: overlapping labels make standard cross-validation meaningless.

---

# 6. Hidden Markov models in practice {#6-hidden-markov-models-in-practice}

§5.2 and §5.3 defined the hidden Markov model and its filter. This section covers how to fit one and use it. The topics, in order, are estimation, the choice among the four state beliefs, the emission model, and the number of states. They continue with how long states last, transitions that respond to observables, and Bayesian and adaptive estimation. The last topics are model checking, direct use for forecasting and allocation, a worked example on a century of US equity returns, and software.

Two terms need definition first. A **hidden Markov model** (HMM) is any model with a latent Markov chain $s_t$ and an observation density that depends on the current state. A **Markov-switching model** is the econometric name for the same object, usually with regressions as the state-conditional densities (§5.3). §7.2 shows the identity is exact. This section says HMM throughout.

Three ideas organise the section. Every refinement below serves one of them:

1. **Transitions are scarce.** A twenty-year daily sample holds a few dozen visits to the rarer regime, so it holds a few dozen exits from each regime. Every parameter that governs the state process is estimated from those few dozen events. The useful refinements are the ones that add persistence and stability cheaply: heavy-tailed emissions, priors and restrictions.
2. **State variances are identified, and state means are not.** §8.1 makes this precise. Restrict the parameters you cannot estimate, and use the model's free parameters on volatility.
3. **Only the predicted belief, computed with parameters estimated on past data,
   is tradable** (§5.1). Several standard software functions return a different
   object by default.

## 6.1 Estimation by EM, and what goes wrong

**The algorithm.** Maximum likelihood for an HMM is almost always computed by the
expectation–maximisation algorithm in its HMM form. This form is **Baum–Welch** ([Baum et al.,
1970](https://doi.org/10.1214/aoms/1177697196){target="_blank"}; [Hamilton, 1990](https://doi.org/10.1016/0304-4076(90)90093-9){target="_blank"}, for the econometric version). Each iteration has two steps.

The **E-step** runs the forward filter of §5.2 and the backward smoother. Under the current parameters, it obtains two sets of posteriors. The first set is the smoothed state probabilities $\xi_{t|T}^{(k)} = \Pr(s_t = k \mid \mathcal{F}_T)$. The second set is the pairwise probabilities of each transition,

$$
\xi_{t-1,t|T}^{(jk)} = \Pr(s_{t-1} = j,\ s_t = k \mid \mathcal{F}_T)
  = \frac{\xi_{t-1|t-1}^{(j)}\, p_{jk}\, f(y_t \mid \theta_k)\, b_t^{(k)}}
         {\sum_{j',k'} \xi_{t-1|t-1}^{(j')}\, p_{j'k'}\, f(y_t \mid \theta_{k'})\, b_t^{(k')}} ,
$$

Here $b_t^{(k)}$ is the backward variable, proportional to $p(y_{t+1:T} \mid s_t = k)$. The probability that the chain moved from $j$ to $k$ at $t$ is a product of four factors. They are the belief in $j$ just before, the chance of the move, how well state $k$ explains $y_t$, and how well it explains everything after. These four factors are the pieces of the joint density of $s_{t-1} = j$, $s_t = k$ and the data from $t$ on, given the past. The denominator rescales them to sum to one. So $b_t$ only needs to be proportional. Summing the pairwise probabilities over $k$ returns the smoothed probability, $\sum_k \xi_{t-1,t|T}^{(jk)} = \xi_{t-1|T}^{(j)}$.

The **M-step** treats those posteriors as if they were observed fractional
counts. For Gaussian emissions the updates are weighted moments:

$$
\hat p_{jk} = \frac{\sum_{t=2}^{T} \xi_{t-1,t|T}^{(jk)}}{\sum_{t=2}^{T} \xi_{t-1|T}^{(j)}} ,
\qquad
\hat\mu_k = \frac{\sum_t \xi_{t|T}^{(k)}\, y_t}{\sum_t \xi_{t|T}^{(k)}} ,
\qquad
\hat\sigma_k^2 = \frac{\sum_t \xi_{t|T}^{(k)}\, (y_t - \hat\mu_k)^2}{\sum_t \xi_{t|T}^{(k)}} .
$$

The transition estimate is the expected number of $j \to k$ moves divided by the expected number of days spent in $j$ that have a following day. These are days $1$ to $T-1$. That ratio is the clearest statement of the small-sample problem below. No iteration lowers the likelihood. The sequence converges, but only to a local optimum.

**The four things that go wrong.**

1. **Local optima.** The likelihood is multimodal in $(\theta, \mathbf{P})$. Use at least fifty random restarts.
2. **Label switching.** The likelihood is invariant under permutation of state labels, so the mapping from "state 1" to "the calm state" is arbitrary and can change between refits. Impose an identifying restriction and apply it *inside* every window (§5.1). Sorting by $\sigma_k$ is the standard restriction and the most stable one.
3. **Degeneracy.** The likelihood is unbounded as $\sigma_k \to 0$. One state can collapse onto a single observation. Constrain $\sigma_k$ from below or put a prior on it (§6.7).
4. **Small effective sample.** This problem matters most. The information about $\theta_k$ comes only from observations assigned to state $k$. The information about $p_{jk}$ comes only from observed *transitions*. A 20-year daily sample with a 25-day turbulent state entered twice a year contains about 40 turbulent spells, so 40 entries and 40 exits. **You are estimating a transition probability from forty events, not from five thousand observations.** The standard error scales accordingly.

The fourth problem needs a number. Take a turbulent state occupied for 1,000 days, which is 40 spells of 25 days, with $p_{22} = 0.96$. This gives 1,000 stay-or-leave trials. So $\hat p_{22}$ has a standard error of roughly $\sqrt{0.96 \times 0.04 / 1{,}000} = 0.0062$. The expected spell length $1/(1 - p_{22}) = 25$ days is a smooth function of $p_{22}$. The standard error of a smooth function is its derivative times the standard error of its argument (the delta method). The derivative is $1/(1-p_{22})^2 = 625$. So the standard error is about $625 \times 0.0062 \approx 3.9$ days, or 16% of its value. The spells give the same answer directly. A geometric spell has a standard deviation close to its mean (24.5 against 25 days). So the average of 40 spells has a standard error of about $24.5/\sqrt{40} \approx 3.9$ days. That is the *best* case, with the state path known. With the path inferred, the error is larger, and the half-life of §1.3 carries all of that error.

**Initialisation.** [Practice] Start the volatilities at quantiles of $|y_t|$, spread across the range. Start the means near the sample mean. Start the transition matrix sticky, with $p_{kk}$ between 0.95 and 0.98. Run many random perturbations of that start, and add one start from a cheap clustering of a trailing-volatility feature. Keep the best likelihood, then look at the spread of the others. Several distinct optima within a few log-likelihood points of each other mean the data do not identify the model, so no single fit should be trusted.

**Direct maximisation as the alternative.** The log-likelihood is the sum of
log predictive densities that the filter already computes (§5.2), so you can
pass it directly to a quasi-Newton optimiser after reparameterising. Use logits for
each transition row and logs for the scales. EM is robust far from the optimum and
slow near it. Quasi-Newton is slow far from the optimum and fast near it. The usual combination is EM to get
close, then a few Newton steps to finish ([Zucchini, MacDonald & Langrock, 2016](https://doi.org/10.1201/b20790){target="_blank"}).
Direct maximisation is also the easy route for the extensions of §6.5 and §6.6,
whose M-steps have no closed form. **[Practice]**

**Standard errors.** The cheap route is the inverse of the negative of the numerically differentiated Hessian of the log-likelihood at the optimum. This is the inverse of the observed information. It is unreliable when $\hat p_{kk}$ is near 1, because the parameter is near the boundary of its space. In that case, report standard errors for the logit of $p_{kk}$, not for $p_{kk}$ itself. Alternatively, use the parametric bootstrap, which simulates from the fitted model, refits, and measures the spread of the estimates. The bootstrap is the safer default. It is the same method §8.2 recommends for testing $K$.

**Cost.** Each E-step costs $O(TK^2)$, so the full fit costs $O(TK^2 I R)$ for $I$ iterations and $R$ restarts. For $K \le 3$ and decades of daily data, this takes seconds in compiled code. A walk-forward study refits the model once per period, which multiplies the cost by the number of refits. Warm-starting each refit from the previous parameters cuts the iterations to a handful.

## 6.2 Which state belief for which job

An HMM can report four different things about the state. They answer different questions. The table puts them side by side. The first three are the $\xi$ objects of the notation block.

| Object | Definition | Conditions on | Use | Tradable at the open of bar $t$? |
|---|---|---|---|---|
| Predicted | $\xi_{t\|t-1} = \mathbf{P}^{\top}\xi_{t-1\|t-1}$ | $\mathcal{F}_{t-1}$ | positions, forecasts | yes |
| Filtered | $\xi_{t\|t}$ (§5.2) | $\mathcal{F}_{t}$ | end-of-bar reporting | no; it uses $y_t$ |
| Smoothed | $\xi_{t\|T}$ (§5.2) | $\mathcal{F}_{T}$ | describing history, EM | never |
| Viterbi path | $\arg\max_{s_{1:T}} \Pr(s_{1:T} \mid \mathcal{F}_T)$ | $\mathcal{F}_{T}$ | labelling episodes | never |

The **Viterbi path** is the single most probable *sequence* of states. The forward recursion with $\max$ in place of $\sum$ computes it:

$$
\delta_t(k) = f(y_t \mid \theta_k)\, \max_{j}\, \delta_{t-1}(j)\, p_{jk} ,
$$

Here $\delta_t(k)$ is the probability of the best path that ends in state $k$ at $t$, together with the data through $t$. The recursion starts at $\delta_1(k) = \pi_k f(y_1 \mid \theta_k)$. Tracing back the maximising $j$ from the best final state then recovers the path. The path is not the same as taking the most probable state at each date from $\xi_{t|T}$. The two can differ for long stretches, because the path must be coherent as a whole. For example, the path can omit a one-day visit to a state that the marginal probabilities favour for that day alone. The visit costs two transitions, and no single path containing it need be the most probable one. Like the smoother, the Viterbi path is revised as data arrive. Its value at $t$ computed with data through $T > t$ is look-ahead. Its *terminal* value, recomputed each day with data through that day, is $\mathcal{F}_t$-measurable. But it is a hard label with the defects §1.2 describes.

**The software default.** [Fact] Common libraries return the smoothed or Viterbi object by default, because speech recognition and bioinformatics need those objects. In `hmmlearn`, `predict` returns the Viterbi path and `predict_proba` returns smoothed posteriors over whatever array you pass. Passing the full history and taking the value at $t$ is rung 2 of the filtration ladder. In `statsmodels`, a fitted Markov-switching model exposes `predicted_marginal_probabilities`, `filtered_marginal_probabilities` and `smoothed_marginal_probabilities` as separate attributes. Only the first is tradable, and only with parameters estimated on data before $t$. Writing the forward filter yourself takes twenty lines (§5.2) and removes the ambiguity. §6.12 lists the packages.

## 6.3 Choosing the emission model

The emission density $f(y_t \mid \theta_k)$ defines what a state *is*. Three choices matter. They are the distribution family, which observables enter $y_t$, and which parameters switch.

**Gaussian emissions.** Gaussian emissions are the default, and they cause two practical problems. First, a Gaussian calm state assigns a tiny density to a single large return. One outlier can therefore push the filter into the turbulent state for a day and out again. The model then reports a switch where nothing persistent happened. Second, with $K \ge 3$ the likelihood often assigns a state to a handful of outliers. This is the degeneracy of §6.1 in a milder form.

**Student-t emissions.** They fix both problems. Within state $k$,

$$
f(y_t \mid \theta_k) = \frac{\Gamma\!\left(\frac{\nu_k+1}{2}\right)}{\Gamma\!\left(\frac{\nu_k}{2}\right)\sqrt{\nu_k\pi}\,\sigma_k}
  \left(1 + \frac{(y_t - \mu_k)^2}{\nu_k \sigma_k^2}\right)^{-\frac{\nu_k + 1}{2}} ,
$$

The parameters are location $\mu_k$, scale $\sigma_k$ and degrees of freedom $\nu_k$. Here $\sigma_k$ is a *scale*, not a standard deviation. The state's volatility is $\sigma_k\sqrt{\nu_k/(\nu_k - 2)}$ for $\nu_k > 2$. The density has polynomial tails rather than exponential tails. So a single large return is plausible in either state and no longer forces a switch.

Estimation stays within EM because the Student-t is a scale mixture of normals ([the Student-t distribution](#a9)). The mixture is $y_t = \mu_k + \sigma_k \varepsilon_t /
\sqrt{\omega_t}$, with $\varepsilon_t \sim \mathcal{N}(0,1)$ and a latent
precision $\omega_t$. The precision is drawn from a gamma distribution with shape and rate both $\nu_k/2$, so its mean is 1. Given $\omega_t$ the observation is Gaussian, so EM treats $\omega_t$ as missing data. The E-step adds one quantity, the expected precision of each observation in each state,

$$
\omega_{tk} = \frac{\nu_k + 1}{\nu_k + (y_t - \mu_k)^2 / \sigma_k^2} ,
$$

which is below 1 for any return more than one scale $\sigma_k$ from $\mu_k$ and falls towards 0 for outliers. The M-step uses $\xi_{t|T}^{(k)}\omega_{tk}$ as the weight in the mean and in the numerator of the scale update. The scale update still divides by $\sum_t \xi_{t|T}^{(k)}$. The M-step maximises over $\nu_k$ numerically. In effect, the M-step computes each state's moments with outliers automatically downweighted.

**[Fact]** [Bulla (2011)](https://doi.org/10.1080/14697681003685563){target="_blank"} documents the consequence on daily index returns. Student-t components
make the fitted states markedly more persistent, because the transitions that
Gaussian components used on outliers disappear. The worked example of
§6.11 reproduces this result on US data from 1926 to 2025. Moving from Gaussian to
Student-t emissions roughly doubles both expected spell lengths. The calm state rises from 71 to 144 days, and the turbulent state rises from 23 to 56 days. It also halves the number of regime switches in the
smoothed path, from 4.6 to 2.1 a year. §1.3 says persistence carries all
the forecasting content. §12.3 says turnover decides whether a
strategy is profitable. **Recommendation: use Student-t emissions for daily returns.** The
cost is one parameter per state.

**Which observables enter $y_t$.** A univariate HMM on returns can define states only by the distribution of returns. A multivariate emission on a feature vector defines states by joint behaviour. The choice of features *is* the choice of what a regime means. Four rules apply. First, include what you want the state to track. Log realised volatility from intraday data sharpens the identification of volatility states far beyond what daily returns allow. This is part of why the jump-model applications of §5.7 use realised-volatility features. Second, transform features toward symmetry, for example log volatility and changes in spreads rather than levels. Then a Gaussian or Student-t emission is not grossly wrong. Third, standardise inside the training window, never on the full sample (§11.2, leak 4). Fourth, watch the parameter count. A full covariance per state costs $K\,d(d+1)/2$ parameters for $d$ features. Beyond three or four features, use a diagonal or factor covariance.

**Which parameters switch.** Every parameter allowed to vary by state is estimated from that state's observations alone. §8.1 shows that state means are estimated with an error larger than the differences you hope to find. State variances are estimated precisely. Two consequences follow. First, a model with a common mean, $\mu_k = \mu$, loses little likelihood and removes $K - 1$ noisy parameters. Second, the in-sample mean spread that a free-mean model reports is not a forecast. The worked example of §6.11 finds a 42-point annualised gap between the Student-t states' fitted means. The realised gap between the days the walk-forward model *predicted* to be calm and turbulent is $-2.5$ points, with standard error 5.3. **Recommendation: start with variance-only switching.** Allow the means to switch only if the out-of-sample log score improves.

**Autoregressive emissions.** Hamilton's original model lets the autoregressive coefficients switch. For daily returns the autoregressive terms are negligible, and they add parameters with no benefit. For macroeconomic growth rates and realised volatility they matter. §5.3 covers them.

## 6.4 How many states

The likelihood-ratio test for $K$ versus $K+1$ does not have a $\chi^2$
distribution. Under the null, the extra state's parameters are
unidentified, and the transition probabilities involving it lie on the boundary
([Hansen, 1992](https://users.ssc.wisc.edu/~behansen/papers/jae_92.html){target="_blank"}; [Garcia, 1998](https://doi.org/10.2307/2527399){target="_blank"}; [Cho & White, 2007](https://doi.org/10.1111/j.1468-0262.2007.00809.x){target="_blank"}; §8.2). Researchers routinely use information criteria instead.
These criteria are known to over-select in this setting ([Psaradakis
& Spagnolo, 2003](https://doi.org/10.1111/1467-9892.00305){target="_blank"}). [Pohle et al. (2017)](https://arxiv.org/abs/1701.08673){target="_blank"} explain why in general terms. Any
misspecification of the emission or the dynamics appears as extra structure,
and an additional state is the cheapest way for the likelihood to absorb it.
**[Fact]**

The worked example shows the pattern. On a century of daily US returns, BIC improves from the two-state Gaussian model to the two-state Student-t model, then to the three-state Gaussian, then to the three-state Student-t. Nothing indicates that it would stop improving there. The three-state Gaussian model finds no new kind of market. It splits the volatility axis into three levels, 8.1%, 16.5% and 41.5% annualised (§6.11).

The recommended procedure, in order of preference:

1. **Fix $K$ a priori from the decision problem.** If the portfolio has two settings, $K = 2$. This approach is legitimate, because $K$ is a modelling choice (§1.1) and the decision problem supplies a reason for choosing it.
2. **Out-of-sample predictive log-likelihood** on a walk-forward split, or
   cross-validated likelihood over blocks of the sample ([Celeux and Durand,
   2008](https://doi.org/10.1007/s00180-007-0097-1){target="_blank"}). It is slow, but it evaluates out of sample and is directly relevant.
3. **Stability across subsamples.** If $K = 3$ is right, fitting it on halves should give recognisably the same three states. If it does not, the model is using $K$ to absorb misspecification.
4. **Inspect the states, then choose pragmatically.** [Pohle et al. (2017)](https://arxiv.org/abs/1701.08673){target="_blank"}
   recommend fitting a range of $K$, checking each model's states and residuals
   (§6.9), and reporting more than one model when no choice is clearly better.
5. **Nonparametric $K$** via a sticky HDP-HMM ([Fox et al., 2011](https://arxiv.org/abs/0905.2592){target="_blank"}). It puts a
   prior over $K$ and a separate prior on persistence. It is principled and expensive,
   and it tends to return more states than a trading decision can use.

## 6.5 How long states last: durations and semi-Markov models

**The problem.** A first-order Markov chain implies *geometric* sojourn times. The probability of remaining in state $k$ for exactly $d$ periods is $p_{kk}^{d-1}(1-p_{kk})$. So the modal duration is always 1, and the hazard of leaving is constant ([sojourn times](#a6)). Under the model, a crisis that has lasted six months is exactly as likely to end tomorrow as one that started yesterday.

**The evidence.** [Rydén, Teräsvirta and Åsbrink (1998)](https://doi.org/10.1002/(SICI)1099-1255(199805/06)13:3%3C217::AID-JAE476%3E3.0.CO;2-V){target="_blank"} found that Gaussian HMMs
reproduce most stylised facts of daily returns. They do not reproduce the slow decay of the
autocorrelation of absolute returns. This failure concerns durations, because a
geometric sojourn decays too fast. [Bulla and Bulla (2006)](https://ideas.repec.org/a/eee/csdana/v51y2006i4p2192-2209.html){target="_blank"} show that
hidden semi-Markov models with negative binomial sojourns reproduce that
autocorrelation better. Direct tests of duration dependence point the same way.
[Durland and McCurdy (1994)](https://doi.org/10.1080/07350015.1994.10524543){target="_blank"} test GNP growth. [Maheu and McCurdy (2000)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=146531){target="_blank"}
find that bull markets have a declining hazard in over 160 years of monthly
US returns. [Lunde and Timmermann (2004)](https://doi.org/10.1198/073500104000000136){target="_blank"} test bull and bear markets
defined by price rules. **[Fact]** The constant hazard is rejected.
**[Contested]** The shape of the hazard is disputed, since each study measures it on a few
dozen spells.

**The semi-Markov model.** A hidden semi-Markov model (HSMM) separates the two jobs of a transition matrix. A duration distribution $\Pr(D_k = d)$ gives the length of a visit to state $k$. An embedded chain with zero diagonal gives the destination when the visit ends. The standard duration family is the shifted negative binomial,

$$
\Pr(D_k = d) = \binom{d + m_k - 2}{d - 1}\, q_k^{\,m_k} (1 - q_k)^{d-1},
\qquad d = 1, 2, \dots ,
$$

Here $m_k > 0$ is the shape and $q_k \in (0, 1)$ is the success probability. At $m_k = 1$ the distribution is geometric with $q_k = 1 - p_{kk}$, so the HMM is nested. For $m_k > 1$ the hazard rises with duration: the longer the spell, the likelier it ends. For $m_k < 1$ the hazard falls, as in Maheu and McCurdy's bull markets. For integer $m_k$, $D_k - 1$ is the sum of $m_k$ independent geometric waiting times. So the spell must pass through $m_k$ stages in sequence and rarely ends early. With $m_k = 2$ and $q_k = 0.5$, the hazard at $d = 1, 2, 3, 4$ is $0.25, 0.33, 0.375,
0.40$. It climbs towards $q_k$ from below. The mean duration is $1 + m_k(1 - q_k)/q_k$, which is $1/q_k$ at $m_k = 1$.

**Estimation.** Two routes are available. The explicit-duration forward recursion tracks the
pair (state, time in state). It costs $O(TK D_{\max})$ for a maximum duration
$D_{\max}$, which must be long enough to cover the longest plausible spell.
The cheaper route is due to [Langrock and Zucchini (2011)](https://doi.org/10.1016/j.csda.2010.06.015){target="_blank"}. It represents state
$k$ by a block of $M_k$ sub-states that the chain moves through in order. The
block's internal transitions reproduce any duration distribution exactly up to
$M_k$ periods, with a geometric tail beyond. The result is an ordinary HMM with
$\sum_k M_k$ states. So the filter, the predicted probabilities and direct
likelihood maximisation all work unchanged. Summing the sub-state probabilities
recovers the probability of each regime.

**Duration-dependent switching** ([Durland & McCurdy, 1994](https://doi.org/10.1080/07350015.1994.10524543){target="_blank"}; [Maheu & McCurdy,
2000](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=146531){target="_blank"}) is a closely related model. It keeps the Markov chain but lets $p_{kk}$
depend on the current spell length through a logistic function. The
filter handles this by augmenting the state with a duration counter up to a cap.

**Failure modes.** (i) The duration shape is estimated from the number of *spells*, a few dozen at best. So $m_k$ is weakly identified, and its confidence interval routinely spans 1. (ii) The current spell is right-censored in real time. You know how long it has lasted but not how long it will last, and the duration model is meant to supply exactly that quantity. (iii) Setting $D_{\max}$ too short forces long spells to end.

**Cheaper ways to add persistence.** Student-t emissions (§6.3) remove the outlier-driven switches that make spells look short. A stickiness prior on the diagonal of $\mathbf{P}$ (§6.7) or a jump penalty (§5.7) raises self-transition probabilities without modelling duration. You can also give a downstream model the time since the last transition as a feature (§10.1). This supplies the duration information directly.

**Recommendation.** If the fitted state path flickers, check the geometric-duration assumption first. **Naive HMMs produce implausibly choppy state sequences, and that choppiness destroys a trading strategy through turnover (§12.2).** Try Student-t emissions and a stickiness prior first. Fit an HSMM only if those leave a measurable gap in out-of-sample log score. Judge the HSMM on that score rather than on the likelihood. **[Practice]**

## 6.6 Transitions that respond to observables

§5.3 lists constant transition probabilities among the assumptions that fail in
practice. The direct fix is to let them depend on lagged observables.

**Definition.** With a vector of $\mathcal{F}_{t-1}$-measurable covariates
$z_{t-1}$ (including a constant), a **time-varying transition probability**
(TVTP) model sets each row of the transition matrix by a multinomial logit,

$$
p_{jk,t} = \Pr(s_t = k \mid s_{t-1} = j,\ z_{t-1})
  = \frac{\exp\!\left(z_{t-1}^{\top}\psi_{jk}\right)}{\sum_{l=1}^{K}\exp\!\left(z_{t-1}^{\top}\psi_{jl}\right)} ,
\qquad \psi_{jj} = 0 ,
$$

Here the coefficient vectors $\psi_{jk}$ are the state-process parameters $\psi$ of the master form (§1.4), now driven by a covariate. Setting $\psi_{jj} = 0$ makes staying the baseline, because adding the same number to every score in a row would leave the probabilities unchanged. For $K = 2$ each row has a single free coefficient vector, $\psi_j \equiv \psi_{jk}$ for the one $k \ne j$, and the multinomial logit reduces to a logistic function. The probability of leaving state $j$ is $1/(1 + \exp(-z_{t-1}^{\top}\psi_j))$, so the probability of staying is $p_{jj,t} = 1/(1 + \exp(z_{t-1}^{\top}\psi_j))$. A positive coefficient raises the chance of leaving. Flip its sign to parameterise persistence directly. With $z_{t-1}$ equal to a constant alone, this is the constant-$\mathbf{P}$ model. The filter is unchanged except that $\mathbf{P}$ becomes $\mathbf{P}_t$:
$\xi_{t|t-1} = \mathbf{P}_t^{\top}\xi_{t-1|t-1}$.

[Diebold, Lee and Weinbach (1994)](https://doi.org/10.1093/oso/9780198773917.003.0010){target="_blank"} introduced the model with an EM algorithm.
[Filardo (1994)](https://doi.org/10.1080/07350015.1994.10524545){target="_blank"} applied it to business-cycle phases driven by leading
indicators. In finance, [Schaller and van Norden (1997)](https://doi.org/10.1080/096031097333745){target="_blank"} let stock-market
transitions depend on deviations of prices from fundamentals.
[Perez-Quiros and Timmermann (2000)](https://doi.org/10.1111/0022-1082.00246){target="_blank"} used interest rates and money growth to
drive recession probabilities in small- and large-firm returns.

**Estimation.** The E-step is unchanged. The M-step for $\psi$ becomes a weighted
multinomial logistic regression of the pairwise posteriors
$\xi_{t-1,t|T}^{(jk)}$ on $z_{t-1}$ and has no closed form. Direct maximisation of
the likelihood (§6.1) is usually simpler.

**What it buys.** TVTP connects the latent and observable branches of §7.1. The filter still estimates the state from the data, so the model can find a regime that the covariate does not name. The regime's dynamics now respond to something you can see. In one limit the two branches coincide. Suppose the transition probabilities do not depend on the current state, so $p_{jk,t} = g_k(z_{t-1})$ for every $j$. Then $\Pr(s_t = k \mid \mathcal{F}_{t-1})
= g_k(z_{t-1})$, and the model is a mixture of experts with an observable gate (§7.2).

**Choosing $z$.** Use few covariates, lagged and normalised. Examples are a trailing volatility rank, the slope of the VIX futures curve, a credit spread change, and the term spread for macro regimes. Every covariate must be $\mathcal{F}_{t-1}$-measurable. Macroeconomic covariates must come from real-time vintages (§11.2, leak 8). Every covariate must also be stationary, because a logit of a trending level drifts toward 0 or 1.

**Failure modes.**

1. **Parameter count against forty transitions.** TVTP has $K(K-1)\dim(z)$ transition parameters, against $K(K-1)$ for a constant $\mathbf{P}$. All are estimated from the few transitions in the sample. Overfitting is the default outcome. Penalise $\psi$ with a ridge term in the likelihood, or put a prior on it.
2. **A covariate that measures the state rather than predicting it.** A lagged
   VIX level predicts that the turbulent state will persist, because high
   implied volatility *is* turbulence. It does not predict entries before they
   start. Check whether the covariate improves the forecast of transitions *into*
   the turbulent state, not just of staying there.
3. **Degeneration into a threshold rule.** If the fitted logit is steep, the latent state becomes a near-deterministic function of $z$. Then the threshold or smooth-transition model of §5.5 is the accurate description, and it is simpler.
4. **Endogenous switching.** If the covariate responds to the same shocks that
   drive the state, the standard likelihood is misspecified. [Kim, Piger and
   Startz (2008)](https://ideas.repec.org/p/fip/fedlwp/2003-015.html){target="_blank"} develop the estimator that allows for it.

**The evidence.** In-sample improvements from TVTP are common and large.
Out-of-sample improvements are rarer. [Kole and van Dijk (2017)](https://doi.org/10.1002/jae.2511){target="_blank"} compare
rule-based and regime-switching identification of bull and bear markets.
They find that rules date states better in sample. They find that regime-switching models,
including versions with predictors, forecast better. **[Contested]**

**Recommendation.** Use one or two normalised covariates and a ridge penalty on $\psi$. Judge the model by out-of-sample log score against the constant-$\mathbf{P}$ model. §8.6 scores "predict regime transitions ahead of time" as not working. TVTP is the principled attempt at this task. That verdict stands unless your own out-of-sample evidence overturns it.

## 6.7 Bayesian estimation

**Why.** A Bayesian treatment addresses the failures of §6.1 in three ways. A prior on each $\sigma_k^2$ removes the degeneracy. A prior on each row of $\mathbf{P}$ regularises transition probabilities estimated from forty events and encodes the belief that regimes persist. The posterior over parameters lets the predictive density integrate over parameter uncertainty instead of plugging in point estimates. This matters most for the poorly determined parameters: the state means and the transition probabilities.

**The priors.** Conjugate choices keep the algebra closed. Each transition row
gets a Dirichlet prior, $(p_{j1}, \dots, p_{jK}) \sim \mathrm{Dirichlet}(a_{j1},
\dots, a_{jK})$, whose parameters act as **pseudo-counts**: the prior behaves as
if $a_{jk}$ extra $j \to k$ transitions had been observed. Given a state path
with $n_{jk}$ observed transitions, the posterior is
$\mathrm{Dirichlet}(a_{j1} + n_{j1}, \dots, a_{jK} + n_{jK})$. A sticky prior puts
large pseudo-counts on the diagonal. For $K = 2$, $a_{kk} = 49$ and $a_{kj} = 1$
give a prior-mean persistence of 0.98, held with the weight of fifty days of data.
Means and variances get normal and inverse-gamma priors.

**The Gibbs sampler.** Bayesian HMMs are estimated by Markov chain Monte Carlo,
alternating three draws:

1. **The whole state path at once, by forward filtering, backward sampling**
   (FFBS). Run the filter of §5.2 forward. Draw $s_T$ from $\xi_{T|T}$. Then, for
   $t = T-1$ down to 1, draw $s_t$ from
   $\Pr(s_t = j \mid s_{t+1}, \mathcal{F}_t) \propto \xi_{t|t}^{(j)}\, p_{j s_{t+1}}$.
   [Carter and Kohn (1994)](https://doi.org/10.1093/biomet/81.3.541){target="_blank"} introduced the idea for state-space models and
   [Chib (1996)](https://doi.org/10.1016/0304-4076(95)01770-4){target="_blank"} for Markov mixtures.
2. **Each transition row** from its Dirichlet posterior, using the transition
   counts of the sampled path.
3. **Each state's emission parameters** from their conjugate posteriors, using
   the observations the sampled path assigns to that state.

Drawing the path jointly matters. The earlier single-site sampler of [Albert and
Chib (1993)](https://doi.org/10.1080/07350015.1993.10509929){target="_blank"} draws each $s_t$ given its neighbours. With persistent states
it mixes very slowly. With its neighbours held fixed, a day inside a spell almost
always keeps its state. So a spell can change length only at its edges, one day at
a time. [Scott (2002)](https://doi.org/10.1198/016214502753479464){target="_blank"} reviews the recursions and
recommends the forward–backward sampler. **[Fact]**

**Label switching, again.** Under a symmetric prior the posterior is invariant to relabelling the states. So the sampler can swap labels between sweeps, and posterior means of "state 1" average two different states. Three remedies exist. The first is to impose the ordering $\sigma_1 < \dots < \sigma_K$ inside the sampler. The second is the random permutation sampler of [Frühwirth-Schnatter (2001)](https://doi.org/10.1198/016214501750333063){target="_blank"}, which permutes labels deliberately and then post-processes. The third is to relabel the draws afterwards ([Stephens, 2000](https://doi.org/10.1111/1467-9868.00265){target="_blank"}).

**The cheap version.** EM computes the posterior *mode* under these priors with one change to the M-step: add the prior pseudo-counts to the expected counts. The mode of a Dirichlet distribution with parameters $b_1, \dots, b_K$ is $(b_k - 1)/(\sum_l b_l - K)$. So the pseudo-counts that enter are $a_{jk} - 1$, one fewer than the prior's parameters. The formula needs $a_{jk} \ge 1$. The transition update becomes

$$
\hat p_{jk} = \frac{\sum_{t} \xi_{t-1,t|T}^{(jk)} + a_{jk} - 1}{\sum_{t} \xi_{t-1|T}^{(j)} + \sum_{l}(a_{jl} - 1)} ,
$$

so the sticky prior above adds 48 stays and no exits to the expected counts. The variance update gains a floor from the inverse-gamma prior. **Recommendation: use this penalised EM, with a weak sticky prior and a variance prior, as the default fitting routine.** It adds no cost and fixes degeneracy and erratic transitions. Reserve full MCMC for cases where the predictive distribution must carry parameter uncertainty, as in allocation (§6.10). **[Practice]**

**Failure modes.** (i) The prior dominates any rarely visited state, and that state is often the one you care about. Report how much the posterior moved from the prior. (ii) MCMC convergence is not guaranteed and must be checked across chains. (iii) A walk-forward study needs a full MCMC run per refit. Researchers tend to fit once on the full sample because the repeated runs are expensive. That fit is leak 2 of §11.2.

## 6.8 Adaptive and online estimation

**The problem.** HMM parameters fitted to financial returns drift. [Rydén,
Teräsvirta and Åsbrink (1998)](https://doi.org/10.1002/(SICI)1099-1255(199805/06)13:3%3C217::AID-JAE476%3E3.0.CO;2-V){target="_blank"} found different parameters across
subperiods of the same index. An expanding-window refit gives the 1930s the
same weight as last year. Three responses follow, in increasing order of continuity:

- **Rolling windows.** Refit on the last $W$ observations. This is simple, but parameters jump when a large observation leaves the window.
- **Exponential forgetting.** Maximise a weighted log-likelihood in which the
  contribution of observation $t$ is discounted by $\lambda^{T-t}$ for a
  forgetting factor $\lambda < 1$. The weights sum to $1/(1 - \lambda)$, which is
  the effective memory in observations ($\lambda = 0.998$ gives 500).
  [Nystrup, Madsen and Lindström (2017)](https://orbit.dtu.dk/en/publications/long-memory-of-financial-time-series-and-hidden-markov-models-wit-2/){target="_blank"}
  estimate a two-state Gaussian HMM this way. They find that the time-varying
  parameters reproduce the long memory of squared daily returns. Constant-parameter HMMs fail to reproduce this
  stylised fact (§6.5). The time-varying parameters also improve one-step density
  forecasts. [Nystrup, Madsen and Lindström (2015)](https://ideas.repec.org/a/taf/quantf/v15y2015i9p1531-1541.html){target="_blank"} document the
  parameter drift that motivates it.
- **Online EM.** Update the expected sufficient statistics recursively as each
  observation arrives, with a step size that shrinks over time or stays constant
  ([Cappé, 2011](https://arxiv.org/abs/0908.2359){target="_blank"}). A constant step size is exponential forgetting in
  recursive form.

**The trade-off repeats the identification asymmetry.** Forgetting reduces the effective sample. §8.1 says that volatilities survive a small sample, and means and transition probabilities do not. A memory of 500 days with a turbulent state occupying 20% of the time contains about 100 turbulent days and perhaps four spells, hence four entries and four exits. The state volatilities are estimable from that. The transition probabilities are not. **Recommendation: forget fast for the emission scales, and forget slowly, or use a prior, for the transition matrix and the means.** **[Practice]**

**Failure modes.** (i) The forgetting factor is a hyperparameter. Tuning it on the evaluation period is leak 7 of §11.2. (ii) Short memories make label switching between refits more likely. Track the state identity across refits (§12.6). (iii) Parameters that jump between refits make positions jump. §7.2 records that exponential weighting is approximately a break model with the break date integrated out, so the same smoothing logic applies.

## 6.9 Model checking

A good likelihood does not show that a model is adequate. §2.6 shows how a model with no regimes can fit well. Four checks test adequacy.

**1. Pseudo-residuals.** If the model is correct, the probability integral
transform of each observation under its one-step predictive distribution,

$$
\mathrm{PIT}_t = \Pr(y \le y_t \mid \mathcal{F}_{t-1})
  = \sum_{k=1}^{K} \xi_{t|t-1}^{(k)}\, F(y_t \mid \theta_k) ,
$$

is independent and uniform on $[0, 1]$ ([Diebold, Gunther & Tay, 1998](https://www.nber.org/papers/t0215){target="_blank"}),
where $F(\cdot \mid \theta_k)$ is the state-$k$ distribution function. The
**pseudo-residual** $e_t = \Phi^{-1}(\mathrm{PIT}_t)$, with $\Phi$ the standard
normal distribution function, should then be independent standard normal
([Zucchini, MacDonald & Langrock, 2016](https://doi.org/10.1201/b20790){target="_blank"}). Three diagnostics apply. The first is a
quantile–quantile plot of $e_t$ against the normal. Wrong tails mean the
emission family is wrong. The second is the autocorrelation of $e_t^2$ or $|e_t|$. Remaining
volatility clustering means the state process is too simple, with too few states,
the wrong durations or constant transitions. The third is the same statistics by
subperiod, which reveal parameter drift (§6.8). Compute them from predicted probabilities and
walk-forward parameters, so that the check is itself out of sample.

**2. Benchmark comparison.** Compare the average one-step log predictive density out of sample against continuous benchmarks. The benchmarks are an EWMA volatility with normal and Student-t innovations, and a GARCH. Test the difference with a Diebold–Mariano statistic and a HAC standard error (§11.6). §2.7 recommends this experiment, and the worked example runs it.

**3. Stability across refits.** Track each parameter across walk-forward refits against its bootstrap interval. Also track the correlation of overlapping state paths between consecutive refits (§12.6).

**4. The decoded history.** Count switches per year and look at the spell lengths. A state that the model repeatedly enters and leaves within days is flicker, not a regime. §6.3 and §6.5 say what to change.

## 6.10 Using the model directly: forecasts and allocation

An HMM is a complete predictive model, and it can drive decisions without any
downstream learner.

**Forecasting $h$ steps ahead.** The state forecast is $\xi_{t+h|t} = (\mathbf{P}^{\top})^{h}\xi_{t|t}$, which decays toward $\boldsymbol{\pi}$ at the rate $|\lambda_2|$ of §1.3. The predictive density of $y_{t+h}$ is the mixture $\sum_k \xi_{t+h|t}^{(k)} f(\cdot \mid \theta_k)$. Consider the cumulative return over the next $h$ bars, $R_{t,h} = \sum_{i=1}^{h} y_{t+i}$. Suppose the observations are independent given the state path, with no autoregressive terms. Conditioning on the path and applying the law of total variance, the variance decomposes as

$$
\operatorname{Var}(R_{t,h} \mid \mathcal{F}_t)
  = \sum_{i=1}^{h} \mathbb{E}\!\left[\sigma_{s_{t+i}}^2 \mid \mathcal{F}_t\right]
  + \operatorname{Var}\!\left(\sum_{i=1}^{h} \mu_{s_{t+i}} \,\Big|\, \mathcal{F}_t\right) .
$$

The first term is the expected within-state variance along the path. Given the path, the returns are independent, so their variances add. The second term is the uncertainty about which means the path will visit. It includes covariances between dates, because a persistent chain that is in the bad state on one day is likely to be there the next. §12.1 shows that for single-asset daily data the second term is negligible until the horizon reaches years. An HMM forecasts the variance term well.

**Sizing a single asset.** §12.1 derives the mean-variance position from the mixture's first two moments and shows that it de-risks smoothly as the turbulent probability rises. This is the HMM used directly. On the worked example it is the best of the four strategies tested, but the sample cannot distinguish the margin (§6.11).

**Multi-asset allocation.** With a vector of returns, each state has its own mean
vector and covariance matrix. The allocation problem conditions on the predicted state probabilities. [Ang and Bekaert (2002)](https://business.columbia.edu/sites/default/files-efs/pubfiles/1971/1137.pdf){target="_blank"} fit this to
international equity returns and find a bear state with higher volatilities and
higher correlations. Their allocation result is the useful one. The cost of
ignoring regimes is small for an all-equity portfolio, because diversification
still helps in both states. The cost is large when a risk-free asset can be held, because
the model then moves into cash in the bad state. [Ang and Bekaert (2004)](https://www.nber.org/papers/w10080){target="_blank"}
give the practitioner version. [Guidolin and Timmermann (2007)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=940652){target="_blank"} solve the
dynamic problem with four states for stocks and bonds. They find optimal weights
that depend strongly on the current state and on the investment horizon, because
the state forecast reverts to $\boldsymbol{\pi}$ as the horizon lengthens.
**[Contested]** [Nystrup, Hansen, Madsen and Lindström (2015)](https://doi.org/10.3905/jpm.2015.42.1.103){target="_blank"} report that regime-based
allocation adds value over a static benchmark out of sample. The backtests in the allocation literature share the specification-search problem of
§3.6.

**Long-horizon tail risk.** Actuaries use the HMM for a different job. The
two-state regime-switching lognormal model of [Hardy (2001)](https://doi.org/10.1080/10920277.2001.10595984){target="_blank"} prices long-dated equity guarantees. For these guarantees the left tail of cumulative
returns over ten years or more matters most. A persistent high-volatility state makes that
tail heavier than a single lognormal does. The model became standard in actuarial
work on such guarantees. **[Practice]** This application uses exactly
what the HMM estimates well: the volatility states and their persistence. It uses
none of what the HMM estimates badly.

**Parameter uncertainty.** Plug-in allocations treat $\hat\mu_k$ as known, and §8.1 shows that the estimates are noise. Two remedies exist. The first is to integrate over the posterior (§6.7). The second is to apply the pooling rule of §9.5, which sets the state means equal while letting the covariance matrices switch. **Recommendation: in allocation, switch the covariance and pool the mean** unless out-of-sample evidence supports switching means.

## 6.11 A worked example: a century of US equity returns

The example fits the models of this section to daily returns on the US stock
market. It fits them as a researcher would have fitted them in real time. It
reports every number the earlier sections cite.

**Setup.** The data are daily value-weighted US market returns from the Kenneth
French data library, July 1926 to December 2025. They give 26,151 days of log
returns with an annualised volatility of 17.1%. The models are fitted to total
returns. The out-of-sample return tables use returns in excess of the risk-free
rate. Four models are fitted to the full sample for description. They use
Gaussian and Student-t emissions, with two and three states, and all have
freely switching means and variances. For the out-of-sample work, the two-state
Gaussian and Student-t models are refitted at the start of every year from 1946
on. Each refit uses an expanding window of all earlier data and is warm-started
from the previous one. States are sorted by volatility inside every fit. Every
out-of-sample number uses only the predicted probability $\xi_{t|t-1}$ computed
with that year's parameters. That is rung 5 of §5.1, over 20,337 days. The
script [`figures/regime_hmm_worked.py`](https://github.com/rmahfoud/quant-research/blob/master/figures/regime_hmm_worked.py){target="_blank"} prints every number. It implements the EM of §6.1
with the Student-t extension of §6.3 in numpy. It uses plain EM with a variance
floor and no priors (§6.7). For each full-sample fit it keeps the best of eight
random starts, fewer than §6.1 advises, to keep the run to a few minutes.

```{=latex}
\newpage
```

**The full-sample fits.** **[Fact]** for this sample. These are rung-2 numbers
and describe history only.

| Model | Volatility by state | Mean by state | Expected spell (days) | Half-life of $\lambda_2$ | Smoothed switches per year | BIC |
|---|---|---|---|---|---|---|
| Gaussian, $K=2$ | 9.7%, 30.0% | +21.8%, −29.1% | 71, 23 | 11.7 days | 4.63 | −175,095 |
| Student-t, $K=2$ | 10.1%, 28.1% | +23.8%, −18.1% | 144, 56 | 27.6 days | 2.06 | −176,562 |
| Gaussian, $K=3$ | 8.1%, 16.5%, 41.5% | +26.1%, −3.0%, −39.9% | 41, 23, 27 | 19.8 days | 1.35 | −177,008 |
| Student-t, $K=3$ | 8.2%, 14.2%, 35.0% | +26.0%, +12.4%, −37.6% | 71, 46, 51 | 37.7 days | 1.19 | −177,531 |

Volatilities and means are annualised, from total log returns. The expected spell
is $1/(1 - p_{kk})$. A smoothed switch is a crossing of one half by the
smoothed probability of the most volatile state. BIC is $-2\ln L + n_{\text{par}}\ln T$ for $n_{\text{par}}$ free parameters
(counting $K(K-1)$ for the transition matrix). Lower BIC is better. In the two-state model the Student-t degrees of freedom are 5.5 (calm) and 4.1
(turbulent). So returns are heavy-tailed *within* each
state, not only across them.

```{=html}
<style>
/* Figures for this document. Prefix "mdd-", shared with the momentum and
   trend notes; distinct from the reading widget's "rdw-". Narrow viewports
   reclaim the body's side padding so the figure gets the full width. */
.mdd-fig {
  display: block; width: 100%; height: auto;
  max-width: 660px; margin: 1.6rem auto;
  /* the reading widget adds a light plate (padding) in dark mode */
  box-sizing: border-box;
}
@media (max-width: 760px) {
  .mdd-fig { width: calc(100% + 64px); max-width: none; margin-left: -32px; margin-right: -32px; }
}
@media (max-width: 600px) { /* pandoc's own stylesheet drops body padding to 12px here */
  .mdd-fig { width: calc(100% + 24px); margin-left: -12px; margin-right: -12px; }
}
</style>
```

```{=html}
<img class="mdd-fig" src="quant-research/figures/regime_hmm_worked.svg"
     alt="Top: growth of one dollar in the US stock market from 1926 to 2025 on a log scale, shaded on the days from 1946 onward when the walk-forward two-state Student-t HMM predicted a turbulent-state probability above one half; the shading clusters in 1973-75, 1987, 1998-2003, 2008-2011 and 2020-2022. Bottom: 2007 to 2009 in detail, comparing the full-sample smoothed turbulent probability, which moves in clean blocks, with the walk-forward predicted probabilities from Gaussian and Student-t emissions, which track it with frequent dips, the Gaussian version flickering more.">
```

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/regime_hmm_worked.pdf}
\end{center}
```

**Out of sample, 1946 to 2025.** First comes the density forecast, the average
one-step log predictive density. Each model is compared with an EWMA volatility
($\lambda = 0.94$) with normal innovations, using Newey–West standard errors.

| Model | Average log score per day | Difference from EWMA normal (se) |
|---|---|---|
| EWMA, normal | 3.4131 | — |
| EWMA, Student-t ($\nu = 5.1$) | 3.4477 | +0.0346 (0.0081) |
| HMM, Gaussian | 3.4059 | −0.0073 (0.0093) |
| HMM, Student-t | 3.4318 | +0.0187 (0.0090) |

Second, the table splits realised *excess* returns by the predicted state. The
split is whether the walk-forward Student-t model put the turbulent probability
above one half before the day began.

| Predicted state | Share of days | Annualised mean (se) | Annualised volatility |
|---|---|---|---|
| Calm | 76.2% | +7.4% (1.6) | 10.8% |
| Turbulent | 23.8% | +9.9% (5.0) | 24.5% |

Third, four ways to hold the market, all set from information through the
previous close. The first is buy and hold. The second is a gate that stays out of
the market whenever the predicted turbulent probability exceeds one half. The
other two are volatility targets aiming at 15% a year with leverage capped at 2.
One uses the EWMA volatility and the other uses the HMM's predictive variance
(§12.1).

| Strategy | Return | Volatility | Sharpe | Max drawdown | Turnover per year |
|---|---|---|---|---|---|
| Buy and hold | 8.0% | 15.3% | 0.52 | 59.2% | 0.0 |
| HMM gate (Student-t) | 5.6% | 9.5% | 0.60 | 37.7% | 9.5 |
| EWMA volatility target | 8.8% | 15.5% | 0.57 | 62.5% | 8.7 |
| HMM volatility target (Student-t) | 8.4% | 13.5% | 0.62 | 44.3% | 14.2 |

Returns and volatilities are annualised excess returns. Average exposure is 1.00,
0.76, 1.33 and 1.12 respectively. The standard error of a Sharpe ratio near 0.5
over 81 years is about 0.12.

**[Fact]** for this sample. The findings follow in order of importance:

1. **The volatility levels are large and stable.** Calm volatility near 10% and
   turbulent volatility near 28–30% appear in every two-state fit. The last
   walk-forward refit (data through 2024) gives 10.0% and 28.1%, matching the
   full-sample Student-t fit. The predicted state separates realised volatility
   by a factor of 2.3 out of sample. That shows the volatility levels are real.
   It does not show that they are discrete, and §2.6 says return data alone
   cannot settle that.
2. **The mean spread is an in-sample artefact.** The Student-t states' fitted
   means differ by 42 percentage points a year. Out of sample, the days predicted
   turbulent earned *more* on average than the days predicted calm. The
   difference, −2.5 points with a standard error of 5.3, is noise. The in-sample
   spread arises because the smoother and the filter use $y_t$ itself to classify
   day $t$. Large negative returns arrive with rising volatility (the leverage
   effect), so the models assign them to the turbulent state *after the fact*. A
   prediction made before the day cannot use that association. These results are
   §8.1 and §8.4 on real data.
3. **The emission family changes the dynamics, not just the tails.** Student-t
   emissions double the expected spells and halve the smoothed switching rate
   (§6.3).
4. **BIC keeps favouring larger models.** Each larger model wins, and the third
   state subdivides the volatility axis (§6.4).
5. **The continuous model wins the density forecast.** An EWMA volatility with
   Student-t innovations beats the Student-t HMM by 0.016 log points a day, with a
   standard error of 0.003. Heavy tails matter more than regimes here. Student-t
   innovations add 0.035 to the EWMA and 0.026 to the HMM. The regime structure
   adds nothing. The Gaussian HMM trails the Gaussian EWMA by 0.007, and the
   Student-t HMM trails the Student-t EWMA by 0.016. §2.7 and §8.7 predict this
   result.
6. **Every overlay helps a little, and the sample cannot rank them.** All three
   overlays raise the Sharpe ratio from 0.52 to between 0.57 and 0.62. That is a
   gain of at most one standard error. The overlays differ in drawdown. The gate
   and the HMM volatility target cut the worst loss from 59% to 38% and 44%. The
   EWMA target's drawdown is the worst of all, and its timing differs. Buy and
   hold's worst loss ran from 2000 to 2009. The EWMA target's worst loss ran from
   1968 to 1974, a slow decline in which trailing volatility stayed moderate and
   the strategy stayed levered all the way down. Volatility targeting protects
   against fast crashes, not slow ones.
7. **The predicted probability crosses one half often. The smoothed one rarely
   does.** The walk-forward Student-t probability crosses one half 9.5 times a
   year. The smoothed path crosses 2.1 times a year, and the Gaussian predicted
   path crosses 15.5 times. The bottom panel of the figure shows why. The smoother
   sees the whole crisis and draws one block. The filter re-decides every day.
   These crossings set the gate's turnover of 9.5 a year, one full position change
   per crossing. They also carry into the HMM volatility target's turnover of
   14.2, against 8.7 for the EWMA target. §12.2 and §12.3 say what to do about it.
   In February 2020 the predicted probability crossed one half on the 25th, four
   trading days after the market's peak on the 19th.

The caveats are the ones §11.5 stresses. The example covers one market and one
history, with perhaps a few dozen independent turbulent episodes in the
out-of-sample period. The target volatility, the leverage cap and the refit
schedule were set once and not tuned. But someone who knew the history set them.

## 6.12 Software and an implementation checklist

| Package | Language | Models | State beliefs exposed | Watch for |
|---|---|---|---|---|
| `statsmodels` (`MarkovRegression`, `MarkovAutoregression`) | Python | Gaussian switching regressions and autoregressions, switching variance, TVTP through `exog_tvtp` | predicted, filtered, smoothed, as separate attributes | Gaussian only. It fits once on what you pass, so you write the walk-forward loop yourself |
| `hmmlearn` | Python | Gaussian, Gaussian-mixture and discrete emissions | smoothed (`predict_proba`), Viterbi (`predict`) | no filtered or predicted output. Both defaults look ahead |
| `depmixS4` ([Visser & Speekenbrink, 2010](https://doi.org/10.18637/jss.v036.i07){target="_blank"}) | R | GLM emissions, covariates on transitions and emissions | filtered and smoothed | covariate-driven transitions overfit easily |
| `MSGARCH` ([Ardia et al., 2019](https://doi.org/10.18637/jss.v091.i04){target="_blank"}) | R | Markov-switching GARCH (§5.4), Student-t and skewed emissions, ML and MCMC | filtered, smoothed, predictive | many parameters per state |
| `mhsmm` ([O'Connell & Højsgaard, 2011](https://doi.org/10.18637/jss.v039.i04){target="_blank"}) | R | hidden semi-Markov models (§6.5) | smoothed | duration distributions need many spells |

None of them runs a walk-forward study, sorts states inside each window, or
refuses to return a smoothed probability. The forward filter is short enough to
write yourself. Test it against a library on the same parameters. The script of
§6.11 is a numpy reference implementation.

**The checklist.**

1. Write down the decision the state will serve and fix $K$ from it (§6.4).
2. Compute the half-life of the fitted $|\lambda_2|$ and compare it to the
   holding period (§1.3).
3. Use Student-t emissions on daily returns. Start with variance-only switching
   (§6.3).
4. Fit by penalised EM with a weak sticky prior and a variance floor, from many
   starts. Keep the best and inspect the spread of the rest (§6.1, §6.7).
5. Sort states by volatility inside every estimation window (§6.1).
6. Refit on an expanding or exponentially weighted window. Never use
   full-sample parameters out of sample (§6.8, §11.2).
7. Emit $\xi_{t|t-1}$ only, and label every reported number with its rung
   (§5.1, §6.2).
8. Check pseudo-residuals from the walk-forward fit (§6.9).
9. Compare the model with an EWMA with Student-t innovations on out-of-sample
   log score (§6.9).
10. Count switches per year and turnover before costing anything (§6.11,
    §12.3).
11. Add durations (§6.5) or covariates (§6.6) only when the simple model fails a
    specific check, and judge them out of sample.

> ### §6 Key takeaways
>
> 1. An HMM estimates its transition probabilities from the transitions in the
>    data, a few dozen in twenty years of daily data. The expected spell length
>    of a turbulent state has a standard error of about 16% even with the state
>    path known.
> 2. An HMM gives four state beliefs: predicted, filtered, smoothed and Viterbi.
>    Only the predicted belief is tradable. Popular libraries return the smoothed
>    or Viterbi output by default.
> 3. Student-t emissions are the most valuable refinement for daily returns. On a
>    century of US data they double the expected spell lengths and halve the
>    switching rate, because single outliers no longer force switches.
> 4. Let variances switch and pool the means. On US data the fitted states'
>    means differ by 42 points a year in sample. The predicted states' realised
>    means differ by −2.5 points, with a standard error of 5.3.
> 5. Information criteria keep adding states, and the extra states subdivide
>    volatility. Fix $K$ from the decision.
> 6. The data reject constant hazards. Semi-Markov models fix this at a cost.
>    Heavy tails and sticky priors give most of the persistence more cheaply.
> 7. Covariate-driven transitions link latent and observable regimes. They
>    overfit forty transitions easily. Regularise them and judge them out of
>    sample.
> 8. Penalised EM with Dirichlet and inverse-gamma priors is the default fitter.
>    It removes degeneracy and stabilises the transition estimates at no cost.
> 9. Adaptive estimation should use a short memory for volatilities and a long
>    memory for transitions and means, because only the volatilities can be
>    estimated from a short window.
> 10. Check the model with pseudo-residuals and an out-of-sample comparison
>     against an EWMA with Student-t innovations. On US equities the EWMA wins the
>     density forecast. The HMM's value comes from sizing and drawdown, not from
>     forecasting returns.

---


# 7. Taxonomy and equivalences {#7-taxonomy-and-equivalences}

§5 listed nine families. This section argues three points. The families are one
model with four slots (§1.4). Several of them are provably identical. One slot,
inference and use, matters far more than the other three. §7.4 splits the four
slots into seven finer design choices and ranks them.

## 7.1 The design space is a product, not a tree

Recall the master form of §1.4. Filling in the first three slots for each
family gives a coordinate table, not a taxonomy. The fourth slot, inference and
use, is orthogonal to family choice. The end of this section treats it
separately. The empty cells are the most useful part of the table, because they
are combinations nobody has tried.

| Family | What varies | State dynamics | Driver | Typical use |
|---|---|---|---|---|
| MS regression / HMM | $\beta_k, \sigma_k$ | Markov | latent | density forecast |
| HMM with TVTP | $\beta_k, \sigma_k$ | Markov, covariate-driven | **latent and observable** | density forecast |
| Hidden semi-Markov | $\beta_k, \sigma_k$ | **explicit durations** | latent | density forecast |
| MS-GARCH | $\omega,\alpha,\beta$ per state | Markov | latent | vol forecast |
| Threshold / STAR | $\beta_k, \sigma_k$ | indicator or logistic | **observable** | conditional regression |
| Change point | everything | single break / run length | latent | monitoring |
| Jump model | centroid $c_k$ | **jump penalty** | latent | classification |
| Clustering | centroid $c_k$ | **none** | latent | exploration |
| Scalar index | nothing (no states) | trailing window | **observable** | feature |
| Deep latent | network weights | learned, state-dependent | latent or both | end-to-end |
| Supervised label | label definition | label span | **defined** | classification |

The table shows two structural features. First, the "driver" column is close to
binary in practice. The state is either a function of something you can see, or
it is inferred from the series itself. The observable branch is systematically
underused relative to how well it performs (§5.5). Second, the persistence
mechanism varies more than the literature acknowledges. A Markov chain, a jump
penalty, a run-length prior and a trailing window each impose the assumption
that the state does not change every day. Their statistical costs differ widely.

```{=latex}
\newpage
```

```mermaid
flowchart TD
    ROOT["Regime model"] --> OBS["State driver"]
    OBS --> O1["Observable z<br/>threshold, STAR, scalar index"]
    OBS --> O2["Latent<br/>HMM, jump model, clustering"]
    O1 --> P1["Persistence via<br/>smoothing of z"]
    O2 --> P2["Persistence mechanism"]
    P2 --> M1["Transition matrix<br/>K-squared params"]
    P2 --> M2["Jump penalty<br/>1 param"]
    P2 --> M3["Run-length prior<br/>1-2 params"]
    P2 --> M4["None<br/>flickers"]
    style O1 fill:#0b6e4f,color:#fff
    style M2 fill:#0b6e4f,color:#fff
    style M4 fill:#8b1a1a,color:#fff
```

The green nodes are the recommended choices. The red node is plain clustering,
which has no persistence mechanism and so needs a persistence term added.

Two modifiers are genuinely *orthogonal*. They are not branches of this tree,
and they apply to every leaf. They are **(a)** the information set the state
estimate conditions on (§5.1), and **(b)** whether the downstream consumer
receives a hard label or a full posterior. Both are protocol choices. Both apply
to every model. Both matter more than the choice of leaf.

## 7.2 Equivalences

This is the most valuable table in the document. It lists methods that look
different and are the same. It marks an identity **exact** where it holds
without approximation.

| Claim | Status | Why |
|---|---|---|
| Hamilton filter $=$ HMM forward algorithm $=$ discrete-state Bayes filter | **exact** | Identical recursion. Three literatures (econometrics, speech, control) named it separately |
| Kim smoother $=$ HMM forward-backward posterior | **exact** (discrete state only) | Both compute $\Pr(s_t \mid \mathcal{F}_T)$ with a different factorisation and the same number. With a continuous state as well, Kim's smoother collapses mixtures and is approximate |
| Gaussian mixture model $=$ HMM with $\mathbf{P} = \mathbf{1}\boldsymbol{\pi}^{\top}$ | **exact** | A mixture is an HMM with no memory, so it forecasts nothing (§1.3) |
| **Jump model $=$ MAP state path of a restricted HMM** | **exact** for the path given the centroids | Derived below. This is the important one |
| HSMM with geometric durations $=$ HMM | **exact** | The geometric is the semi-Markov duration with constant hazard (§6.5) |
| HSMM $\approx$ HMM on an expanded state space | approximate | Exact up to $M_k$ periods of duration, geometric beyond ([Langrock & Zucchini, 2011](https://doi.org/10.1016/j.csda.2010.06.015){target="_blank"}) |
| TVTP HMM whose transitions ignore the current state $=$ mixture of experts gated on $z$ | **exact** | If $p_{jk,t} = g_k(z_{t-1})$ for every $j$, then $\Pr(s_t = k \mid \mathcal{F}_{t-1}) = g_k(z_{t-1})$ (§6.6) |
| Student-t emission $=$ Gaussian emission with a gamma-distributed latent precision | **exact** | The scale-mixture representation that makes EM work (§6.3) |
| Penalised EM with Dirichlet transition priors $=$ posterior-mode Bayesian HMM | **exact** | The prior pseudo-counts are added to the expected counts (§6.7) |
| STAR with logistic transition $=$ two-expert mixture of experts with a logistic gate on one input | **exact** for the conditional mean | Same blended point forecast, proposed independently twice (§10.5). The densities differ. STAR is one Gaussian with a blended mean. A density mixture of experts is a two-component mixture |
| Regime dummy interacted with every feature $=$ separate models per regime | **exact** for least squares, approximate for a deep tree | Least squares with the full set of interactions returns the per-regime coefficients. A deep tree can represent the same pair of fits and does so if it splits on the dummy first (§9.3, §10.4) |
| Vol-targeted position sizing $=$ regime conditioning with $K = \infty$ and a $1/\hat\sigma$ response | interpretation | Every vol-targeted strategy is already regime-conditional |
| $K=2$ HMM differing only in variance $\Rightarrow$ unconditional return distribution is a scale mixture of normals | **exact** | So the distribution is symmetric, leptokurtic, and indistinguishable from a fat-tailed i.i.d. law on unconditional moments alone (§2.6) |
| Single GARCH with near-unit persistence $\approx$ MS-GARCH with lower within-regime persistence plus level shifts | approximate | [Hamilton & Susmel (1994)](<https://doi.org/10.1016/0304-4076(94)90067-1>){target="_blank"} show that apparent IGARCH is partly unmodelled regime switching |
| Markov-switching volatility with large $K$ $\approx$ discretised stochastic volatility | approximate | The chain converges to a discretisation of the continuous latent scale |
| Long memory $\approx$ occasional regime switching | approximate | [Diebold & Inoue (2001)](https://www.nber.org/papers/t0264){target="_blank"}. The two are mutually confusable even asymptotically |
| Exponentially decayed sample weights $\approx$ a break model with an unknown break date integrated out | approximate | Both downweight the past geometrically. With a constant per-bar break hazard, the chance that no break occurred in the last $s$ bars is $\lambda^s$ with $\lambda = 1 - \text{hazard}$ |
| BOCPD predictive density $\approx$ automatic estimation-window selection | approximate | Its forecast is a run-length-weighted mixture of fixed-window estimators |

**The jump-model identity, derived.** Take an HMM with isotropic Gaussian
emissions of common variance $\sigma^2$ around centroids $c_k$. The common
variance is the spread of the feature vector around its centroid, not a return
volatility. The emission density is

$$
f(u_t \mid s_t = k) = (2\pi\sigma^2)^{-d/2}
  \exp\!\left(-\frac{\lVert u_t - c_k \rVert^2}{2\sigma^2}\right) ,
$$

The transition matrix is symmetric, with $p_{kk} = p$ and $p_{jk} = (1-p)/(K-1)$
for $j \ne k$. The MAP (maximum a posteriori) state path maximises the joint
log-density of path and data,
$\ln \pi_{s_1} + \sum_{t \ge 2} \ln p_{s_{t-1} s_t} + \sum_t \ln f(u_t \mid s_t)$.
The first two of those terms simplify. A symmetric chain has a uniform
stationary distribution, so $\ln \pi_{s_1} = -\ln K$ whichever state the path
starts in. The transition term takes only two values, so it equals a constant
plus an indicator:

$$
\ln p_{s_{t-1} s_t}
  = \ln p \;-\; \mathbb{1}[s_t \ne s_{t-1}] \, \ln\!\frac{p\,(K-1)}{1-p} .
$$

Check both branches. When $s_t = s_{t-1}$, the indicator vanishes and the
expression equals $\ln p$. Otherwise it equals $\ln p - \ln p - \ln(K-1) + \ln(1-p) =
\ln\frac{1-p}{K-1}$, as required. Sweeping every path-independent piece — the
$-\ln K$, the $(T-1)\ln p$, and the per-observation Gaussian normaliser
$-\tfrac{d}{2}\ln(2\pi\sigma^2)$ — into a constant leaves

$$
\sum_{t} \ln f(u_t \mid s_t) + \sum_{t \ge 2} \ln p_{s_{t-1} s_t}
= -\sum_{t} \frac{\lVert u_t - c_{s_t}\rVert^2}{2\sigma^2}
  - \ln\!\frac{p(K-1)}{1-p} \sum_{t \ge 2} \mathbb{1}[s_t \ne s_{t-1}]
  + \text{const} .
$$

Multiplying by $2\sigma^2$ and flipping the sign turns this maximisation into the
minimisation of §5.7, with

$$
\boxed{\ \lambda = 2\sigma^2 \ln\!\frac{p\,(K-1)}{1-p} \ }
$$

Two limits check the result. $\lambda > 0$ exactly when $p > 1/K$. That is
exactly when the chain is *sticky*, meaning it is more likely to stay in a state
than an independent uniform draw would be. At $p = 1/K$ the states are i.i.d.,
$\lambda = 0$, and the objective is plain $k$-means, with the frequent switching
of §5.8. As $p \to 1$, $\lambda \to \infty$ and no switch is ever worth its
penalty, which leaves one state for the whole path.

So the statistical jump model is the Viterbi decode of an HMM whose emissions
are constrained to be isotropic with equal variance and whose transitions are
constrained to be symmetric. It is not an *alternative* to the HMM. The identity
is exact for the path given the centroids and $\lambda$. The jump model also
chooses the centroids by minimising the same objective over path and centroids
together. Maximum likelihood for the HMM sums over paths instead, so the two
fitted centroids can differ. This changes how to read the jump model's empirical
advantage (§5.7). **The jump model wins by imposing restrictions on the
probabilistic framework, not by escaping it.** It replaces $K^2$ transition
parameters, estimated from a few dozen observed transitions, with one penalty
tuned on a validation objective. This is a bias-variance trade made in the right
direction for the sample sizes available in finance. It is a much better reason
to use the jump model than "clustering is simpler than likelihood".

## 7.3 Same name, different thing

This table is the inverse of the last. It lists terms that authors use for
different things, which is a common source of miscommunication.

| Term | Sense A | Sense B | Why it matters |
|---|---|---|---|
| **Regime** | macro state (inflationary, tightening); horizon: years | volatility state (calm, turbulent); horizon: weeks | Differ by two orders of magnitude in persistence. A model fitted for one cannot serve the other (§1.3) |
| **Regime detection** | "which of $K$ states are we in now" | "did the process just change" | Different questions; §5.6 answers the second much better than §5.3 does |
| **Clustering into regimes** | partition of *time* | partition of *assets* | Both use $k$-means. Only the first is a regime |
| **Bull / bear market** | a latent state | a $\pm 20\%$ drawdown rule | The drawdown rule is assigned retroactively and is a look-ahead by construction |
| **Regime probability** | $\xi_{t\|t-1}$, tradable | $\xi_{t\|T}$, historical | The two differ by the entire value of the research (§5.1) |
| **Turbulence** | squared Mahalanobis distance of the return vector | realised volatility | Correlated at 0.7–0.9 in most samples. Test the increment before claiming novelty |
| **Regime-switching model** | states switch parameters | states switch *the model itself* (gating) | Statistically similar, computationally and organisationally very different (§10.5) |

## 7.4 Which design choice actually matters

This is the practical result of the taxonomy. The list ranks the design
choices in descending order of effect on realised out-of-sample performance. The
effect is the amount measured results move when the choice changes:

1. **The information set (§5.1).** **[Practice]**, held with high confidence.
   This choice dominates. The difference between rung 2 and rung 5 is routinely
   larger than the difference between the best and worst model in §5.12. Once you
   measure both, the difference is arithmetic, not opinion.
2. **Whether variance switches.** **[Fact]** Variance switches in every published
   study and in the worked example of §6.11. This is the one thing regime models
   reliably find.
3. **Whether the driver is observable.** An observable driver removes the
   filtering problem, the label-switching problem, and most of the estimation
   error. When one exists, use it.
4. **The persistence mechanism.** A jump penalty, a sticky prior or a run-length
   prior beats a freely estimated transition matrix at realistic sample sizes,
   for the parameter-counting reason in §7.2.
5. **Whether the mean switches.** Assume it does not (§8.1). If you must, demand
   out-of-sample evidence at the standard of §11, not a likelihood improvement.
6. **The number of states.** This matters less than every choice above it, which
   surprises people. **[Practice]** Beyond $K = 2$ or $3$, additional states
   almost always subdivide the volatility axis. Their marginal decision value is
   near zero.
7. **The emission family.** This matters least for *where* the states sit.
   Gaussian and Student-t fits agree on the state volatilities to within two
   points on US data (§6.11). It matters a great deal for *persistence*, which
   places it inside choice 4. Heavy tails stop single outliers from forcing
   switches and halve the switching rate. Use Student-t emissions for that
   reason, not for the density.

> ### §7 Key takeaways
>
> 1. The model families form a four-slot product space, not a taxonomy. The empty
>    cells are combinations nobody has tried, and some of them are good.
> 2. The statistical jump model is *exactly* the MAP path of an HMM with
>    isotropic equal-variance emissions and symmetric transitions, with
>    $\lambda = 2\sigma^2\ln[p(K-1)/(1-p)]$. Its advantage comes from restricting
>    parameters. It does not escape the probabilistic framework.
> 3. A Gaussian mixture is an HMM with no memory and therefore forecasts nothing
>    beyond the unconditional distribution.
> 4. Every volatility-targeted strategy is already a regime-conditional strategy
>    with a continuum of states. Many people who say they do not use regime
>    models are using the most reliable one.
> 5. Long memory, stochastic volatility, and regime switching are mutually
>    confusable. Do not treat a likelihood improvement as evidence for one over
>    the others.
> 6. The ranking by effect on out-of-sample performance is: information set $\gg$
>    variance switching $>$ observable driver $>$ persistence mechanism $>$ mean
>    switching $>$ number of states $>$ emission family. One exception: a
>    heavy-tailed emission is itself a persistence mechanism.
> 7. The HMM is the reference model of the equivalence table. A mixture, a jump
>    model, a semi-Markov model, a covariate-driven model and a Student-t
>    emission are each an HMM with one restriction or one extension, so the HMM's
>    diagnostics and failure modes carry over to all of them.

---

# 8. What is known to work, and what is not {#8-what-is-known-to-work-and-what-is-not}

This section should change what you build. Almost all of it follows from one
asymmetry, which comes first.

## 8.1 The identification asymmetry

**The claim.** Regime models estimate state *variances* precisely. They do not
estimate state *means* at all. This is a mathematical property of the estimation
problem. It is not a defect of any particular implementation.

**The mechanism**, in three lines. Suppose you observe $n$ i.i.d. draws from
$\mathcal{N}(\mu, \sigma^2)$ over a fixed calendar span $\tau$, at spacing
$\Delta$, so that $n = \tau/\Delta$. Here $\mu$ and $\sigma$ are *per bar*. The
annualised quantities are $\mu_{\text{ann}} = \mu/\Delta$ and
$\sigma_{\text{ann}} = \sigma/\sqrt{\Delta}$. Then

$$
\operatorname{sd}(\hat\mu_{\text{ann}})
= \underbrace{\frac{\sigma}{\sqrt{n}}}_{\text{per bar}}
\cdot \underbrace{\frac{1}{\Delta}}_{\text{annualise}}
= \frac{\sigma}{\Delta\sqrt{n}}
\overset{\sigma \,=\, \sigma_{\text{ann}}\sqrt{\Delta}}{=}
\frac{\sigma_{\text{ann}}}{\sqrt{n\Delta}}
= \frac{\sigma_{\text{ann}}}{\sqrt{\tau}},
\qquad
\frac{\operatorname{sd}(\hat\sigma^2)}{\sigma^2} \approx \sqrt{\frac{2}{n}} .
$$

Sampling faster shrinks $\Delta$ and raises $n$, and leaves $\tau = n\Delta$
unchanged. The standard error of the mean therefore depends only on the
*calendar span* $\tau$. Going from daily to five-minute data does not reduce it
at all. The *relative* error of the variance shrinks with the *number of
observations*, so higher frequency reduces it directly. This is Merton's (1980)
observation. Courses do not teach it first, yet it is the most important fact in
quantitative finance. For regimes, a state occupied for two years' worth of days gives
thousands of observations to estimate $\sigma_k$ and two years of calendar time
to estimate $\mu_k$.

**The measurement.** A simulation drew 400 independent ten-year daily samples
from a two-state Gaussian HMM and fitted a correctly specified $K = 2$ model to
each by EM. The simulation used *generous* parameters. The calm state has $+10\%$ drift and
$12\%$ volatility. The turbulent state has $-15\%$ drift and $32\%$ volatility.
Expected durations are 100 and 25 days. The fitted model has the right number of
states, the right emission family and the right state dynamics. It matches the
true process exactly.

```{=html}
<img class="mdd-fig" src="quant-research/figures/regime_identification.svg"
     alt="Sampling distributions of the estimated state volatilities and state means from a correctly specified two-state Gaussian HMM fitted to 400 independent ten-year daily samples. The volatility estimates are tightly clustered on their true values; the mean estimates overlap heavily and the turbulent-state mean spans a range far wider than its true value.">
```

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/regime_identification.pdf}
\end{center}
```

**[Simulated]** The table gives the numbers, with a 30-year arm added for scale.
[`figures/regime_identification.py`](https://github.com/rmahfoud/quant-research/blob/master/figures/regime_identification.py){target="_blank"} prints both arms.

| Quantity | True | 10 years: mean (sd) | 30 years: mean (sd) |
|---|---|---|---|
| Calm volatility | 12.0% | 12.0% (0.20 pp) | 12.0% (0.11 pp) |
| Turbulent volatility | 32.0% | 31.9% (1.17 pp) | 32.0% (0.65 pp) |
| Calm mean | +10.0% | +10.0% (4.6 pp) | +10.1% (2.5 pp) |
| Turbulent mean | −15.0% | −15.1% (**24.7 pp**) | −13.5% (**13.2 pp**) |
| Mean spread, calm − turbulent | +25.0 pp | +25.1 (sd 25.1), **wrong sign in 16.3% of samples**, s/n **1.00** | +23.6 (sd 13.4), wrong sign in 4.0%, s/n 1.76 |
| Volatility ratio, turbulent / calm | 2.67 | 2.66 (sd 0.11), s/n **15.8** | 2.67 (sd 0.06), s/n 28.5 |

Consider the fifth row. **With ten years of daily data and a perfectly specified
model, the estimated spread has the wrong sign one time in six.** The true mean
spread is 25 percentage points a year. Its signal-to-noise ratio is 1.00,
so the fit gives in effect a single noisy observation of it. The volatility ratio
in the same fit has a signal-to-noise ratio of 15.8.

That factor of sixteen is the central result for this field. Tripling the sample
to thirty years raises the mean spread's signal-to-noise ratio only to 1.76.
Thirty years is more daily history than most instruments have. The ratio improves
as $\sqrt{\tau}$, and $\sqrt{3} = 1.73$. No realistically obtainable amount of
data fixes this.

**Why the two states differ so much in mean precision.** The turbulent state
holds 20% of the sample and has 2.67 times the volatility. Its mean standard
error is therefore larger by $2.67 \times \sqrt{0.8/0.2} = 5.3$. The measured
ratio is 5.4. **The state whose mean you most want to know, the bad one, is the
state whose mean you can least estimate**, because it is rare and volatile. This
is structural, and data engineering does not fix it.

## 8.2 You cannot test how many regimes there are

The likelihood-ratio statistic for $K$ versus $K+1$ regimes does not have a
$\chi^2$ null distribution. Two problems arise together. Under the null that
state $K+1$ does not exist, its parameters $\theta_{K+1}$ are completely
unidentified, since any value gives the same likelihood. The transition
probabilities into that state also lie on the boundary of the parameter space.
Standard asymptotics assume that neither problem occurs.
[Hansen (1992)](https://users.ssc.wisc.edu/~behansen/papers/jae_92.html){target="_blank"} developed a valid bound
using empirical-process theory and applied it to Hamilton's own GNP model.
**[Fact]** **The switching specification did not reject a plain AR(4).**

The practical consequences:

- **A likelihood improvement means nothing on its own.** Adding a state always
  raises the likelihood. The relevant question is how much it raises it relative
  to a correct null, and you generally cannot compute that.
- **AIC and BIC over-select.** They assume the regularity conditions that fail
  here. [Psaradakis and Spagnolo (2003)](https://doi.org/10.1111/1467-9892.00305){target="_blank"} document the behaviour.
- **Parametric bootstrap is the practical route.** Simulate from the fitted
  $K$-state model, refit $K$ and $K+1$, and build the null distribution of the LR
  statistic empirically. The method is expensive and correct, and almost nobody
  uses it. If you are going to publish a claim about $K$, do this.
- **Or make $K$ a decision, not an inference** (§6.4). This is the recommended
  route. $K$ is a modelling choice (§1.1), so choose it for the decision it
  serves and validate the whole pipeline out of sample.

## 8.3 What the filtration ladder costs

This analysis uses the same simulation with the **true parameters known**, so it
measures only the information-set effect and not estimation error. It reports
what each rung of §5.1 is worth. The strategy is deliberately crude. It is long
when the predicted state is calm and flat when it is turbulent.

```{=html}
<img class="mdd-fig" src="quant-research/figures/regime_filtration.svg"
     alt="Top: a simulated price path with the true turbulent state shaded. Middle: the smoothed, filtered and predicted probabilities of the turbulent state, which track each other closely but differ at transitions. Bottom: the annualised Sharpe ratio achieved using each of those beliefs, showing that the predicted belief loses about a quarter of the edge available to the filtered one.">
```

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/regime_filtration.pdf}
\end{center}
```

**[Simulated]** Three findings follow, one of them unexpected:

1. **Smoothing costs less than expected when the states are far apart.**
   Smoothed and filtered probabilities give the same Sharpe ratio to two decimals
   (0.71 versus 0.71). The regime is defined by a 2.67$\times$ volatility
   difference, and a single large return is nearly conclusive evidence. So the
   filter identifies the state within a day or two of a transition. The **median
   detection lag is 1.7 days**, against an expected turbulent spell of 25 days.
   Hindsight adds little when the present is already informative.
2. **Predicting costs a lot.** Going from $\xi_{t|t}$ to $\xi_{t|t-1}$ applies
   the transition matrix once. It is the difference between knowing today was
   turbulent and having to decide before seeing today. It drops the Sharpe ratio
   from 0.71 to 0.54, about **a quarter of the edge**. This cost of
   tradability is real. No engineering removes it, and researchers routinely omit it.
3. **The oracle does not beat the filter.** Perfect knowledge of the true state
   gives 0.70, against 0.71 filtered. The two are within Monte Carlo error of
   each other. When separation is strong, inference costs almost nothing. The
   binding constraint is the one-step-ahead prediction, not the filtering.

**A fourth finding, on parameter leakage.** Repeat the exercise with the
parameters *estimated* rather than given. Compare a full-sample EM fit with an
expanding-window refit that uses no future data. Both use predicted probabilities:

**[Simulated]** 30 runs of 20 years, states identified by fitted volatility
inside each fit.

| Calibration | Buy & hold | Full sample, smoothed | Full sample, predicted | Expanding window, predicted |
|---|---|---|---|---|
| Volatility and mean | 0.20 | 0.66 | 0.54 | **0.53** |
| Mean only | 0.50 | 0.02 | −0.02 | **−0.00** |

The table supports two readings. First, in the top row **parameter leakage costs
essentially nothing**. The Sharpe ratio is 0.54 with the whole sample in hand and
0.53 without, with standard errors around 0.03. The reason is §8.1 again. The
parameters that drive this strategy are the state volatilities. The data
determine them within a couple of years, so knowing the rest of the sample adds
nothing. Parameter leakage matters where the fitted parameters are poorly
determined. So it matters most in the specifications that were never going to
work.

Second, the bottom row shows the main risk. **A pipeline applied to a mean-only
regime turns a 0.50 Sharpe buy-and-hold into zero.** The full-sample smoothed
version, the one every paper plots, does no better. The mechanism is label
switching (§6.1). Identifying states by fitted volatility is the correct
convention. But when the states do not differ in volatility, the sort order is
arbitrary. "State 1" then means something different in each refit, and the
position series is close to random. A regime pipeline can be much worse than no
pipeline, and label switching is how.

The generalisation matters more than any of the four findings: **the gap between
smoothed and filtered grows as state separation shrinks.** Strong separation
makes smoothing unnecessary. Weak separation makes the gap enormous and makes the
whole exercise futile anyway. §8.4 gives the central table.

```{=latex}
\newpage
```

## 8.4 When does knowing the regime help at all?

This analysis uses the same simulation, with true parameters known throughout,
200 runs of 15 years, and four calibrations. The calibrations differ in *what
separates the states*.

**[Simulated]**

| States separated by | Buy & hold | Oracle | Smoothed | Filtered | **Predicted** | Accuracy † | Lag ‡ |
|---|---|---|---|---|---|---|---|
| Volatility **and** mean (12/32% vol, +10/−15% mean) | 0.26 | 0.70 | 0.71 | 0.71 | **0.54** | 0.932 | 1.7 |
| Volatility only (12/32% vol, +5/+5% mean) | 0.26 | 0.33 | 0.33 | 0.33 | **0.29** | 0.932 | 1.7 |
| Mild volatility (15/22% vol, +12/−10% mean) | 0.42 | 0.67 | 0.69 | 0.70 | **0.50** | 0.852 | 7.7 |
| Mean only (20/20% vol, +20/−20% mean) | 0.55 | 0.84 | 0.61 | 0.56 | **0.55** | 0.794 | 25.4 |

† Accuracy of the *predicted* state label. The turbulent state occupies 20% of
the sample in every row, so a classifier that always says "calm" scores 0.800.
‡ Median days from a true transition into the turbulent state until the filtered
probability first exceeds one half. The expected turbulent spell is 25 days.

Four readings follow, in order of importance:

**(a) When the states differ only in volatility, knowing the state perfectly is
worth almost nothing to a directional strategy.** In row 2 the oracle earns 0.33
against 0.26 for buy and hold, and the tradable version earns 0.29. Perfect
foresight of a 2.67$\times$ volatility regime adds three hundredths of a Sharpe
ratio. The entire gain is the mechanical one of avoiding high-variance periods
that have the same mean. That is a *sizing* effect, not a timing effect, and
§12.1 shows that sizing captures it more cheaply.

**(b) When the states differ only in the mean, you cannot find them.** In row 4
the oracle earns 0.84, a large edge, and the tradable version earns 0.55,
exactly the buy-and-hold figure. The predicted-state classifier scores 0.794
against a base rate of 0.800, so **it is worse than a constant that always says
"calm."** Its median detection lag is 25.4 days against a 25-day expected spell.
By the time the filter detects a regime, the regime is over. Even the smoothed
version, with the entire sample in hand, only reaches 0.61. A 40-percentage-point
annual mean difference is not visible in daily returns, because it amounts to
0.16% per day against a 1.26% daily standard deviation.

**(c) Rows (a) and (b) together show that the detectable states do not pay.** You
cannot detect the states that would pay. Every real regime strategy sits in
row 1 or row 3. There the mean difference accompanies the volatility difference,
so you detect the state through volatility and earn the return through the mean.
That is a real effect. Daniel and Moskowitz's (2016) momentum crashes are an
example. But the edge then depends entirely on the mean-volatility association
continuing to hold, and §8.1 says you cannot measure that association.

**(d) Row 3 is the realistic case, and its value is 0.08 Sharpe.** A 15% versus
22% volatility split with a mild mean difference is roughly what equity index
regimes look like. Perfect foresight of the state is worth 0.25 Sharpe over buy
and hold. The tradable version is worth 0.08. That figure is before costs, with
the true parameters known, in a correctly specified simulation, with the right
$K$. The detection lag is 7.7 days against a 25-day spell, so you spend the first
third of every regime without knowing you are in it. **Whatever you build will do
worse than 0.08.** Use 0.08 as the benchmark when you evaluate a regime backtest
that adds 0.5 Sharpe.

## 8.5 The out-of-sample forecasting record

**[Fact]** Regime-switching models fit well in sample and forecast badly. This
has been the finding since [Dacco and Satchell (1999)](<https://onlinelibrary.wiley.com/doi/abs/10.1002/(SICI)1099-131X(199901)18:1%3C1::AID-FOR685%3E3.0.CO;2-B>){target="_blank"}, and later work has
not overturned it. Their diagnosis is the most useful part. The loss from
misclassifying the state exceeds the gain from having the right parameters
conditional on classifying correctly. So a model can have every parameter right
and still lose to a constant forecast.

Formally, suppose the model predicts $\hat\mu_{s_t}$ and misclassifies with
probability $q$. Then the mean squared error gains a term of order $q(1-q)(\mu_1 -
\mu_2)^2$. Since $(\mu_1 - \mu_2)^2$ is exactly what you were hoping to exploit,
the misclassification penalty scales with the size of the opportunity. **The
bigger the regime effect you try to capture, the more a classification error
costs.** A model that gets the state right 80% of the time when the base rate is
80% (row 4 above) has $q \approx 0.2$. It captures none of the mean spread and
pays the full variance penalty.

The following results *have* replicated:

- **Volatility forecasting improves.** Regime models beat single-regime GARCH on
  volatility, mostly by fixing the spurious near-integration (§5.4). **[Fact]**
  HAR and realised-volatility models beat both. **[Contested]**
- **Density and tail forecasts improve** over a constant-parameter model. The
  mixture helps when you need the shape of the conditional distribution, for
  options, for VaR or for a utility-based allocation. **[Fact]** It does not help
  against a continuous volatility model with heavy-tailed innovations. On US
  equities the EWMA with Student-t innovations wins the density forecast
  (§6.11).
- **Correlation and co-movement structure improves** ([Ang and Bekaert (2002)](https://business.columbia.edu/sites/default/files-efs/pubfiles/1971/1137.pdf){target="_blank"},
  Longin and Solnik (2001)). The bad state has higher correlations, and modelling
  that changes optimal portfolios materially. **[Fact]**, with the Forbes-Rigobon
  caveat that part of the effect is a volatility artefact.
- **Drawdown reduction is real. Return improvement is not.** **[Fact]**
  [Bulla et al. (2011)](https://mpra.ub.uni-muenchen.de/21154/){target="_blank"}
  find volatility down 41% on average with modest excess returns, across three
  markets and forty years, after costs. This summarises the entire applied
  literature.

**[Fact]** Regime-conditional expected-return prediction as a standalone source of
alpha has not replicated.

## 8.6 The scorecard

The table gives this chapter's assessment of each claimed use, with the evidence
status.

| Use | Verdict | Status |
|---|---|---|
| Forecast volatility level shifts | **Works.** Large, persistent, estimable | [Fact] |
| Forecast correlation regime shifts | **Works**, partly artefactual | [Fact] / [Contested] |
| Improve density and tail forecasts | **Works** | [Fact] |
| Reduce drawdown and realised volatility | **Works.** This is the main benefit | [Fact] |
| Decide *when to retrain* a model | **Works**, and is underused | [Practice] |
| Size positions (risk targeting) | **Works.** A continuous vol model does about as well (§6.11) | [Fact] |
| Time direction from a latent state | **Does not work** standalone | [Fact] |
| Predict regime *transitions* ahead of time | **Does not work** | [Fact] |
| Select among strategies by regime | **Contested.** The claim is plausible, and the evidence is mostly in-sample | [Contested] |
| Improve a forecasting model's conditional mean | **Contested.** The result depends entirely on §9 | [Contested] |
| Explain history | Works, and is worth doing for its own sake | — |

## 8.7 Should you use a discrete model at all?

Almost nobody runs this comparison. Before building a regime model, fit the two
obvious continuous alternatives. Then check whether the discrete model adds
anything. The alternatives are:

1. **EWMA or GARCH volatility**, with the position scaled by $1/\hat\sigma_t$.
2. **A continuous conditioning variable** such as realised volatility, the VIX or a
   turbulence index, entered directly as a regressor or feature.

The evidence, including the worked example of §6.11, gives two results. **For
volatility, the continuous model wins. For decisions that are genuinely
discrete, the regime model wins.** The second result is the case for regime
models, and it is narrower than usually presented. Genuinely discrete decisions
exist: turn a strategy on or off, switch a hedge, change a rebalancing
frequency, or escalate to a human. For those decisions a calibrated state
probability is the right input, because the decision cannot use a continuous
number anyway.

The corollary is the most useful sentence in this section: **if your downstream
consumer can take a continuous input, give it one.** Discretising a variable and
then feeding the result to a downstream model that could have used the underlying
continuous variable loses information for no reason. §10.1 says what to feed
instead.

> ### §8 Key takeaways
>
> 1. The identification asymmetry follows from arithmetic. The standard error of
>    a mean depends on calendar span. The standard error of a variance depends on
>    the number of observations. Regime models therefore find volatility states,
>    not return states.
> 2. With ten years of daily data and a perfectly specified model, the estimated
>    mean spread between two states with a true 25-point annual gap has the wrong
>    sign in one sample out of six. The volatility ratio in the same fit has a
>    signal-to-noise ratio of 16.
> 3. You cannot test the number of regimes with a standard likelihood-ratio test.
>    Use a parametric bootstrap, or choose $K$ from the decision and validate the
>    pipeline out of sample.
> 4. Smoothing's look-ahead advantage is small when states are well separated and
>    large when they are not. The step from filtered to predicted costs about a
>    quarter of the Sharpe ratio even in the easy case, and that cost is real.
> 5. If the states differ only in volatility, perfect knowledge of the state is
>    worth about 0.03 Sharpe to a directional strategy. If they differ only in
>    the mean, the filter is worse than a constant guess and detects the regime
>    only after it has ended. Real strategies sit in the middle, where the mean
>    difference accompanies the volatility difference. There the tradable edge is
>    roughly 0.08 Sharpe under ideal conditions.
> 6. Misclassification cost scales with the square of the mean spread you try to
>    exploit. Bigger apparent opportunities are therefore not easier to capture.
> 7. The replicated benefits are volatility, correlation, density, and drawdown.
>    The unreplicated one is directional timing. Design accordingly.
> 8. If the downstream consumer can take a continuous input, do not discretise.

---

# 9. Which shift do you have? {#9-which-shift-do-you-have}

Part I covered estimating a regime. Part II covers using one. A regime estimate
has three possible consumers: a position rule, a risk model, and a forecasting
model that predicts returns or some other target. §6.10 showed an HMM driving
the first two on its own, and §12 returns to them. This section and the next
cover the third consumer. They apply to any forecasting model, such as a linear
regression, a regularised regression with interactions, a tree ensemble or a
network. §10.8 collects the few points that depend on the model family.

This section first identifies **which distribution is actually changing**.
Almost nobody asks this, and it determines everything downstream. The answer
picks the integration scheme. A wrong answer leads to work that cannot help. The
most common example is adding a regime feature to address a problem that a
feature cannot address.

## 9.1 The three shifts, and what each demands

Write the joint distribution of features and target as
$p(x, y) = p(x)\,p(y \mid x)$. It can change over time in three ways, and the
three are not interchangeable.

**Covariate shift.** $p(x)$ changes, and $p(y \mid x)$ is unchanged. The market
moves into a region of feature space you have seen little of. For example,
volatility is at levels last seen in 2008, or spreads are wider than in your
training data. The *relationship* between features and returns is the same as
before.

**Conditional-scale drift.** $\mathbb{E}[y \mid x]$ is unchanged, and
$\operatorname{Var}(y \mid x)$ changes. Your signal predicts the same quantity,
and the noise around it is three times larger. This is technically a special
case of the next category. It demands a completely different remedy and is by
far the most common shift in financial data, so it has its own name here.

**Concept drift.** $\mathbb{E}[y \mid x]$ changes. The machine-learning
literature uses the term for any change in $p(y \mid x)$. Here it is reserved for
the mean. Momentum predicts positive returns in calm markets and negative ones
after a crash. The function you are trying to learn is different in different
regimes. This is the shift everybody means by "regime", and it is the rarest of
the three.

The remedies do not overlap:

| Shift | What changes | Right response | Common wrong response |
|---|---|---|---|
| **Covariate** | $p(x)$ | Usually **nothing**. Ensure feature coverage and consider more capacity | Importance weighting, which adds variance for no bias reduction |
| **Conditional-scale** | $\operatorname{Var}(y \mid x)$ | Normalise the target by conditional scale, **or** weight by $1/\hat\sigma^2$ (they are different: §9.4) | Add a volatility feature and hope the model figures it out |
| **Concept** | $\mathbb{E}[y \mid x]$ | Condition: interactions, gating, separate models, or a shorter window | Add a regime dummy (§9.3) |

**The covariate-shift row is the counterintuitive one.** Suppose
$p(y \mid x)$ is unchanged and your model class contains the truth. Then
covariate shift causes no loss asymptotically, because the model learns the same
function whatever the input distribution. **[Fact]** Shimodaira's (2000) result
is that importance weighting helps *only* under misspecification or in finite
samples. It always costs variance. The effective sample size falls to
$\left(\sum_i w_i\right)^2 / \sum_i w_i^2$, which for realistic financial weights
is often less than half the nominal sample.

Every model you fit is misspecified. So weighting under covariate shift trades a
small bias reduction for a large variance increase. In the sample sizes
available in finance the trade is usually bad. Diagnose the shift before
reaching for the remedy.

## 9.2 Six places regime information can enter

Regime information can enter a forecasting model at exactly six points. They are not
substitutes.

```mermaid
flowchart LR
    D["Raw data"] --> W["1. Data<br/>subset / window"]
    W --> F["2. Input<br/>regime feature"]
    F --> M["4. Model<br/>gate, per-regime, MoE"]
    T["Target y"] --> N["3. Target<br/>scale normalisation"]
    N --> M
    L["5. Loss<br/>sample weights"] --> M
    M --> O["6. Output<br/>post-hoc scaling"]
    O --> P["Position"]
    style N fill:#0b6e4f,color:#fff
    style F fill:#5a6578,color:#fff
    style M fill:#a8452b,color:#fff
```

| # | Channel | Addresses | Cost | Recommended order |
|---|---|---|---|---|
| 3 | **Target normalisation** | conditional-scale drift | near zero | **do this first, always** |
| 6 | **Output scaling** (position sizing) | conditional-scale drift | near zero | do this second |
| 2 | **Input feature** | concept drift, weakly | near zero | cheap, usually ineffective (§9.3) |
| 5 | **Sample weights** | covariate shift, scale drift | variance | situational |
| 1 | **Data subsetting / window** | concept drift, strongly | large variance cost | only with strong evidence |
| 4 | **Model structure** (gating, MoE) | concept drift, strongly | complexity, overfitting | last, and only if subsetting (channel 1) works |

The ordering is the practical content of this document's second half. The two
channels that reliably help address *scale*, which you can measure (§8.1). The
channels that address the conditional *mean* are ranked last. The evidence that
the conditional mean changes is weak, and acting on a false positive is costly.

## 9.3 Why adding a regime dummy usually does nothing

This section gives the mechanism, because every practitioner observes the effect
and is surprised by it independently.

Suppose you fit a flexible forecasting model with features $x$, such as a
regression with interactions, a tree ensemble or a network, and add a regime
indicator $\hat s_t$. Four things limit its usefulness:

**(a) The label is a coarsening of a feature you already have.** Your regime
label was derived from volatility, or from something highly correlated with
volatility. Realised volatility should already be in $x$. Then the label carries
almost no incremental information. A flexible learner also prefers the
continuous variable the label came from. The binary label is one particular
threshold on that variable, and the learner can choose a better function of it.
A tree places its own threshold. A spline or a network fits a smooth curve.
**The predictable consequence is that your regime feature has near-zero
importance while volatility has high importance. This is correct behaviour, not
a bug.**

**(b) A mean-function feature cannot express a variance change.** If the regime
changes only $\operatorname{Var}(y \mid x)$, then by construction
$\mathbb{E}[y \mid x, s] = \mathbb{E}[y \mid x]$, and the optimal predictor
ignores $s$ entirely. Nothing you do at the input can fix a problem in the loss.
This is the most common category error in applied regime work.

**(c) The interaction may be unlearnable.** To use the regime, the model must
build an interaction, which is a different slope on a signal in each state.
Whatever the learner, it estimates that interaction from the rare-regime
observations alone. In a regression the interaction is one coefficient per
signal, fitted on the turbulent subsample. In a tree it needs a split on the
state followed by splits on the signal inside each branch, with enough samples in
the rare-regime leaves. Only 20% of observations are in the turbulent state. An
interaction of any depth inside that state therefore has an effective sample of
at most a few hundred observations per leaf or coefficient. These observations
are also serially correlated, so the effective number of independent observations is far
smaller still.

**(d) The label is one bit.** A hard $K = 2$ label carries at most one bit per
observation, and a posterior probability carries not much more. Against a target
with a signal-to-noise ratio around 0.05, one bit carries little information.

**What actually helps**, in descending order:

1. **Give the model the continuous variable the label was made from.** Examples
   are realised volatility, the turbulence index and the term-structure slope.
   Such a variable is continuous and monotone, has no identification problem, and
   has no look-ahead if computed on a trailing window.
2. **Give it the posterior, not the label**, if you insist on the state
   ($\xi_{t|t-1}^{(k)}$ as a real number in $[0,1]$).
3. **Build the interaction explicitly** as a feature $x_j \cdot \xi^{(k)}$,
   rather than hoping the model discovers it. [Gu, Kelly and Xiu
   (2020)](https://www.nber.org/papers/w25398){target="_blank"} do this
   with their macro predictors, and this is why their approach works without any
   latent state.

## 9.4 Normalisation is not weighting

Two ways to handle conditional-scale drift look interchangeable. They assume
different things about the world. Using the wrong one silently changes what you
estimate.

**Model A — constant expected return.** The edge is a fixed number of basis
points regardless of the volatility environment:

$$
y_t = m(x_t) + \sigma_t \varepsilon_t .
$$

Here $\mathbb{E}[y \mid x]$ does not depend on $\sigma_t$. The efficient
estimator is **weighted least squares with $w_t = 1/\sigma_t^2$**, which
downweights noisy periods. Normalising the target would be *wrong*. It would
make the target function $m(x)/\sigma_t$, which depends on $\sigma_t$. That would
create concept drift where there was none.

**Model B — constant Sharpe.** The edge scales with volatility, so the
information ratio is stable:

$$
y_t = \sigma_t\, m(x_t) + \sigma_t \varepsilon_t
\qquad\Longleftrightarrow\qquad
\frac{y_t}{\sigma_t} = m(x_t) + \varepsilon_t .
$$

Here **normalising the target is exactly right**, because it recovers a
homoskedastic problem with a stable target function. Weighting is wrong, because
after normalisation the noise is already homoskedastic and weighting would
distort it.

The two models prescribe opposite actions, so you have to decide between them.
**The diagnostic.** Fit one model $\hat m$ on all the data, bucket the held-out
observations by $\hat\sigma_t$, and regress realised $y$ on $\hat m(x)$ within
each bucket. Under Model A the slope is the same in every bucket. Under Model B
it rises in proportion to $\sigma$. Fitting a separate model per bucket would
give a slope of one in both cases, because each fit absorbs its own bucket's
scale. Run the diagnostic on your own data. The answer differs by signal and by
asset class, and the published evidence is divided. **[Contested]** Moreira and
Muir, 2017, argue that risk and return are *not* proportional, which favours
Model A for the market factor. Cederburg et al., 2020, dispute the out-of-sample
implementability.

**Regardless of which model holds, normalise anyway**, for a reason independent
of both. An unweighted squared loss on raw returns implicitly weights each
observation by its conditional variance. Take the calibration from §8: 80% of
days at 12% volatility and 20% at 32%. The turbulent days contribute this share
of total squared error:

$$
\frac{0.2 \times 0.32^2}{0.8 \times 0.12^2 + 0.2 \times 0.32^2}
= \frac{0.0205}{0.0320} = 64\% .
$$

**Twenty percent of your sample supplies sixty-four percent of the signal your
loss function responds to.** Your model is fitted predominantly to crises
whether you intend that or not. No hyperparameter search reveals this, because
every configuration has the same problem. Normalising the target by a trailing
volatility estimate, $\tilde y_t = y_t / \hat\sigma_t$, removes the implicit
reweighting. **[Practice]**, held strongly. In practice, this is the most
valuable single change available in a financial forecasting pipeline.

## 9.5 Pooling: the identification asymmetry, restated as a decision rule

§8.1 gives a rule here that you can act on.

Suppose the true parameter in regime $k$ is $\beta_k = \beta + \delta_k$ with
$\operatorname{Var}(\delta_k) = \tau^2$, so $\tau^2$ measures how much regimes
differ. Suppose your per-regime estimate has sampling variance
$v = \sigma^2/n_k$. The optimal shrinkage of the per-regime estimate toward the
pooled one uses the standard hierarchical weight

$$
\hat\beta_k^{\text{opt}} = w\,\hat\beta_k^{\text{(regime)}} + (1-w)\,\hat\beta^{\text{(pooled)}},
\qquad
w = \frac{\tau^2}{\tau^2 + v} .
$$

Fitting separate models per regime sets $w = 1$. Ignoring regimes entirely sets
$w = 0$. Adding a regime feature to a regularised model sets $w$ somewhere in
between, implicitly through the regularisation. **The right value of $w$ depends
on the ratio of between-regime variation to estimation noise.** §8.1 gives that
ratio directly:

- **For means**, $\tau^2$ is no larger than $v$ for the rare, volatile state
  whose mean matters most. Even in the generous simulation of §8.1, the mean
  spread has a signal-to-noise ratio of 1 in a decade of data, and real spreads
  are smaller. So $w$ is small. **Pool. Do not fit separate mean models per
  regime.**
- **For variances and covariances**, $\tau^2$ is large relative to $v$. The
  volatility ratio has a signal-to-noise ratio near 16. So $w \approx 1$.
  **Subset. Estimate the risk model per regime.**

This conclusion is clear, actionable and slightly surprising. It explains a
pattern in practitioner behaviour that otherwise looks inconsistent. Firms that
use regimes successfully use them in the risk model and not in the alpha model.
Those firms follow the arithmetic above.

## 9.6 The inverse framing: invariance instead of adaptation

Every scheme so far adapts the model to the regime. An opposite strategy exists,
and it is underused.

Treat each regime as an **environment**. Look for the predictor whose
conditional distribution $p(y \mid x_{\mathcal{S}})$ is the *same* in every
environment. [Peters, Bühlmann and Meinshausen's (2016)](https://web.math.ku.dk/~peters/jonas_files/InvariantCausalPrediction.pdf){target="_blank"} invariant causal
prediction formalises this. Under assumptions, the features that appear in every
invariant set are, with a stated confidence, direct causes. They are a
conservative subset of the direct causes, since a cause can go undetected. A
model built on them generalises to environments you have never seen, including
future regimes that do not resemble any past one.

The practical version needs no causal theory. Fit the model separately in each
regime. Keep the features whose effect has a consistent sign and comparable
magnitude in all of them. Refit on pooled data with only those features. §10.6
gives the procedure and its failure modes.

**[Practice]** This approach uses the regime decomposition as a *robustness
filter* rather than as a conditioning variable. That matches what regime
estimates can support far better. It also answers §8's scorecard. You cannot
reliably predict which regime you will be in, so prefer a model that does not
depend on the regime. The caveat is the usual one for induction. A feature that
is stable across the regimes *in your sample* may not be stable across the next
one.

> ### §9 Key takeaways
>
> 1. Diagnose the shift before choosing the remedy. Covariate shift, conditional-
>    scale drift, and concept drift demand different and non-overlapping actions.
> 2. Pure covariate shift usually needs no response at all. Importance weighting
>    reduces effective sample size for a bias correction you often do not need.
> 3. A regime feature cannot fix a variance problem, because the variance is not
>    part of the mean function. This is the most common category error in the
>    field.
> 4. Your regime feature will have near-zero importance next to the continuous
>    variable it was derived from. That is correct behaviour. A flexible learner
>    can pick a better threshold, or a smooth curve, than you did.
> 5. Without target normalisation, twenty percent of your days supply sixty-four
>    percent of the squared error your loss responds to. You are fitting crises
>    whether you meant to or not.
> 6. Normalising the target and weighting by inverse variance are different
>    models: constant Sharpe versus constant expected return. Test which one your
>    data supports. The answer varies by signal.
> 7. The identification asymmetry gives a pooling rule. Pool the mean model
>    across regimes and subset the risk model by regime. Firms that use regimes
>    successfully do exactly this.
> 8. Consider inverting the problem. Use regimes as environments to find the
>    features that are *invariant*, and build a model that does not depend on the
>    regime at all.

---

# 10. Conditioning a forecasting model on the regime {#10-conditioning-a-forecasting-model}

This section describes seven schemes. Each has the same fields: what it does,
how to build it, which shift it addresses, what it costs, how it fails, and a
verdict. The first six apply to any forecasting model. The seventh collects the
variants that only a network can implement. §10.8 lists what changes with the
model family, and §10.9 ranks everything.

Throughout, $\hat\xi_t$ is the regime posterior available when the forecast is
made at the end of bar $t$ for a target over $(t, t+h]$. It is the filtered
$\xi_{t|t}$, or equivalently the predicted belief $\xi_{t+1|t}$ for the first bar
of the target, computed with expanding-window parameters (§5.1). Anything that
uses data after $t$, in the state belief or in the parameters, is a leak. This
section does not repeat the warning.

## 10.1 Scheme 1 — regime as a feature

**What it does.** The scheme adds regime information to $x_t$ and lets the
learner use it.

**How.** Use one of four encodings, in increasing order of usefulness:

1. **Hard label.** The label is $\hat s_t = \arg\max_k \hat\xi_t^{(k)}$,
   integer-coded (use native categorical support where the library has it) or
   one-hot. It discards the posterior.
2. **Posterior.** Pass $\hat\xi_t^{(1)}, \dots, \hat\xi_t^{(K-1)}$ as floats.
   This is strictly more informative at no extra cost.
3. **The continuous source variable.** This is the variable your regime was
   derived from, such as trailing realised volatility, the turbulence index or
   the VIX term-structure slope. It usually beats both of the above (§9.3).
4. **Explicit interactions.** Use $x_j \cdot \hat\xi_t^{(k)}$ for the signals
   $x_j$ you believe are regime-dependent. [Gu, Kelly and Xiu
   (2020)](https://www.nber.org/papers/w25398){target="_blank"} do this with macro
   predictors, and this is why their models capture conditional structure without
   any latent state.

Two features are more useful than the state itself and are almost never
included:

- **Time since the last transition**, $t - \max\{u \le t : \hat s_u \ne \hat s_{u-1}\}$.
  This carries the duration information that the geometric-sojourn assumption
  (§6.5) discards. The feature is continuous and lets the model learn that early
  and late in a regime behave differently. **[Practice]**
- **Posterior entropy**, $-\sum_k \hat\xi_t^{(k)} \ln \hat\xi_t^{(k)}$. This
  directly measures how uncertain the model is about the state, which is exactly
  the condition under which you want to reduce risk. It feeds naturally into
  §12.1.

**Addresses.** Concept drift, weakly.

**Cost.** Negligible. One to three columns.

**Failure modes.** (i) Near-zero feature importance next to the continuous
source variable. This is expected and not a bug (§9.3). (ii) Look-ahead through
the state estimate, which is the default unless you built rung 5. (iii) The
label's *meaning* changes between refits (label switching), so the same column
encodes different things at different times. This silently corrupts the model,
and no standard diagnostic reveals it.

**Verdict.** The scheme is cheap, so use it, but expect little. Include the
posterior and the time since the last transition. Skip the hard label.

## 10.2 Scheme 2 — regime-conditional target normalisation

**What it does.** The scheme divides the target by a conditional scale estimate,
so the loss weights every period equally.

**How.**

$$
\tilde y_t = \frac{y_t}{\hat\sigma_t}, \qquad
\hat\sigma_t^2 = \text{EWMA of } r^2 \text{ through } t,
\quad\text{or}\quad
\hat\sigma_t^2 = \sum_k \hat\xi_t^{(k)} \sigma_k^2 ,
$$

The second form is the regime model's own predictive variance. Train on
$\tilde y$. The model now forecasts a **Sharpe ratio**, not a return. To size a
position from the forecast, divide by $\hat\sigma_t$ again. The normalisation
appears twice, once in training and once in sizing, and both are correct.

**Addresses.** Conditional-scale drift. Directly and completely.

**Cost.** One column and one division. This is the cheapest high-value change in
the whole document.

**Failure modes.** The scheme has one failure mode, and it is fatal.
**$\hat\sigma_t$ must be $\mathcal{F}_t$-measurable.** Normalising by realised
volatility computed over the label window $[t, t+h]$ leaks the answer. This is
the natural thing to write, and it looks identical in code. The denominator
contains how volatile the period you are predicting turned out to be. The leak
produces spectacular backtests. Use a trailing estimator and lag it explicitly.

**Verdict.** **Do this first, before anything else in this section.** If you take
one thing from Part II, take this.

## 10.3 Scheme 3 — sample weighting and window selection

**What it does.** The scheme changes how much each historical observation counts,
so the fit reflects conditions resembling the present.

**How.** Three variants:

- **Exponential decay.** $w_t = \lambda^{T-t}$. Choose the half-life, not
  $\lambda$. **[Practice]** A half-life of 3–5 years is typical for daily equity
  data.
- **Regime-similarity weighting.** $w_t = \hat\xi_t^{\top} \hat\xi_T$. This
  weights each historical observation by how much its regime posterior resembles
  today's. **[Practice]** It is a *soft* version of subsetting (§10.4) and
  behaves strictly better, because it degrades continuously instead of
  discarding 80% of the sample at a threshold.
- **Window selection.** [Pesaran and Timmermann (2007)](https://rady.ucsd.edu/_files/faculty-research/timmermann/estimation-window.pdf){target="_blank"} give the formal treatment.
  The optimal window trades the bias from including pre-break data against the
  variance from a short post-break sample. The useful result is that
  **including some pre-break data is often optimal.** Discarding everything
  before the last regime change is usually wrong.

**Addresses.** Covariate shift (weakly, see §9.1), conditional-scale drift, and
concept drift under a slow-drift model.

**Cost.** The cost is variance. Always report the effective sample size

$$
n_{\text{eff}} = \frac{\left(\sum_t w_t\right)^2}{\sum_t w_t^2},
$$

and use $n_{\text{eff}}$, not $T$, as your sample size in every subsequent
calculation. A 5-year half-life on 20 years of daily data gives
$n_{\text{eff}} \approx 3,200$ out of 5,040. That discards over a third of the
information in your data. This may be the right choice, but make it a decision
and not a side effect.

**Failure modes.** (i) A collapse of $n_{\text{eff}}$ that goes unnoticed.
(ii) Tuning the half-life on the evaluation period. (iii) In tree models,
weights change the *split criterion* as well as the leaf values, so the effect
is larger and less predictable than in a linear model.

**Verdict.** Regime-similarity weighting is underused and worth trying.
Exponential decay is a reasonable default. Hard window truncation is usually
worse than both.

## 10.4 Scheme 4 — subsetting and per-regime models

**What it does.** Fits a separate model in each regime.

**How.** Partition the training data by $\hat s_t$ and fit $K$ models. A much
better option is **explicit partial pooling**:

1. Fit a pooled model $f_0$ on all data.
2. For each regime $k$, fit a *correction* $f_k$ on the residuals
   $y_t - f_0(x_t)$ restricted to regime $k$, with strong regularisation.
3. Predict $f_0(x) + \sum_k \hat\xi^{(k)} f_k(x)$.

Every model family has a cheap version. In a linear model, add regime-by-signal
interaction terms and put a ridge penalty on them alone. The penalty shrinks the per-regime slopes toward the pooled slope. In boosting, train the pooled model.
Then continue boosting per regime, starting from the pooled model's predictions as the
offset (`init_score` in LightGBM, `base_margin` in XGBoost). Use a small tree
budget and strong regularisation. In a network, the same structure is a shared
trunk with small per-regime heads and weight decay on the heads. Each version gives
hierarchical shrinkage by construction. The correction's regularisation sets the
shrinkage weight $w$ of §9.5, so you can see it and tune it.

**Addresses.** Concept drift, strongly.

**Cost.** The variance cost is severe and is the main cost. With $K$ regimes,
per-regime sample sizes fall by roughly $K$. They fall by more when regimes are unequal.
The rare regime, the one you care about, gets the smallest sample. §9.5 gives
the calculation. This scheme is worth it only when between-regime variation genuinely
exceeds estimation noise.

**Failure modes.** (i) You fit the rare-regime model on a few hundred
autocorrelated observations, and its output is noise. (ii) The regime assignment used for
partitioning is itself a fitted object with error. You are subsetting on a
noisy label, so errors compound. (iii) At inference the regime is uncertain, and you
must pick a model. Hard selection at a boundary produces large, discontinuous
changes in the prediction.

**Verdict.** **For risk models, yes.** Variances and correlations differ enough
between regimes to justify it (§9.5). **For alpha models, no**, unless you have
out-of-sample evidence at the standard of §11. If you use this scheme, use it as partial
pooling, never as hard subsetting.

## 10.5 Scheme 5 — gating and mixture of experts

**What it does.** Runs several models and blends their predictions by a
regime-dependent gate. It generalises §10.4 to soft assignment.

**How.** $\hat y = \sum_k g_k(z) f_k(x)$ with $\sum_k g_k = 1$. The gate $g$ can
take three forms. It can be the regime posterior itself ($g_k = \hat\xi^{(k)}$, no extra parameters).
It can be a learned logistic function of observables. In a network, it can be a learned softmax
trained end to end with the experts (Jacobs et al., 1991; sparsely-gated at scale
in Shazeer et al., 2017).

**Soft gating strictly dominates hard selection.** At a transition the posterior moves
continuously from one expert to another, so the
prediction path is continuous and the turnover is bounded. Hard selection jumps,
and the jump is largest when you are least sure. This is the same
argument as smooth-transition versus threshold models (§5.5), and it has the same
answer.

**Addresses.** Concept drift, strongly.

**Cost.** You must train, tune and monitor $K$ models. The cost is organisational,
not just computational.

**Failure modes.** (i) **Experts specialise on noise.** With a learned gate and
enough capacity, the model partitions the training data in whatever way minimises
training loss, which need not correspond to any real structure. Constrain the gate to a
small number of interpretable inputs. (ii) The gate memorises the training era's
regime sequence. Check this by evaluating gate outputs on a held-out period and
confirming that they still respond to the inputs rather than to the calendar.
(iii) Expert collapse: one expert takes all the weight and the rest contribute nothing.

**Verdict.** This scheme is worth it when you have genuinely different *strategies* to switch
between. An example is a trend model and a mean-reversion model. It is not worth it for genuinely
different parameters of one model. In the first case the gate performs
strategy allocation, which is a real problem with real evidence behind it. To add
capacity to a single model, use §10.1 interactions instead. They are cheaper and less
fragile.

## 10.6 Scheme 6 — invariance filtering

**What it does.** Inverts the objective. Instead of adapting the model to each
regime, it keeps only the relationships that do not change across regimes (§9.6).

**How.**

1. Partition history into regimes by any reasonable method. A scalar index
   (§5.9) or a two-state HMM (§6) is fine.
2. Fit the model separately in each regime.
3. Keep the features whose effect has a **consistent sign and comparable
   magnitude** in every regime. Measure the effect by a regression coefficient, a partial-dependence
   slope or a SHAP contribution. Discard the rest.
4. Refit on pooled data using only the surviving features.

Networks have two heavier versions. One is an adversarial head that makes the
regime unpredictable from the shared representation. The other is the invariant risk
minimisation penalty ([Arjovsky et al., 2019](https://arxiv.org/abs/1907.02893){target="_blank"}). Both need more environments
than finance supplies. Rosenfeld, Ravikumar and Risteski (2021) show that
invariant risk minimisation can select the wrong features when environments are
few. **[Contested]**

**Addresses.** All three shifts, because the retained relationships do not depend on the regime.

**Cost.** An afternoon for the filtering version.

**Failure modes.** (i) It may discard real, exploitable regime-specific signal.
Invariance is a robustness constraint and costs in-sample fit by construction.
(ii) Invariance across the regimes in your sample does not imply invariance across the
next one. (iii) With noisy per-regime estimates, "consistent sign" fails by
chance. Compare effects relative to their standard errors.

**Verdict.** This is the best-value idea in this section for any model meant to run for
years. It requires of the regime estimate only what §8 says it can deliver: a
rough partition of history into environments. **[Practice]**

## 10.7 Scheme 7 — representation-learning variants

Four schemes need a network's shared representation or its training loop. They
share a verdict: the methods are correct, but they need sample sizes that rarely exist.

- **Regime as an auxiliary task.** Add a second output head that predicts the
  regime. Train it jointly, with a weight $\alpha$ on its loss, and discard the head
  at inference. The auxiliary target may be the forward-looking regime label of
  §5.11. The model never uses this label at inference, so it creates no look-ahead in
  deployment. It only shapes the representation. This scheme is cheap and low-risk. If $\alpha$
  is too large, the trunk optimises for classifying regimes instead of
  predicting returns.
- **A learned latent state.** Feed the conditioning series to a recurrent or
  attention encoder. The encoder builds whatever state serves the objective
  ([Chen, Pelger & Zhu, 2024](https://arxiv.org/abs/1904.00745){target="_blank"}; §5.10). The encoder optimises the state for the decision
  rather than for one-step density forecasting, which is the appeal. The method needs a
  large cross-section. It can collapse into an unused latent with no symptom in
  the loss. The learned state is usually a noisy proxy for realised
  volatility. Ablate it and regress it on volatility before claiming novelty.
- **Adversarial invariance.** This is the opposite of the auxiliary task. Train the trunk
  so that a head *cannot* predict the regime (§10.6). Which of the two you want
  depends on whether you judge the regime-specific component to be signal or
  noise.
- **Meta-learning.** Train the model so that a few gradient steps on recent data adapt it.
  The adaptation set is tiny and noisy. Fast adaptation to a genuine
  break happens at the worst moment. Periodic retraining with exponentially
  decayed weights (§10.3) captures most of the benefit at a fraction of the
  risk.

**Verdict.** Try the auxiliary task before gating if you are already building a
network. Treat the rest as research projects. **[Practice]**

## 10.8 What changes with the model family

The schemes above are model-agnostic, but a few details depend on the model family.

**Linear and regularised regression.** You must build interactions explicitly,
which is an advantage. The term $x_j \cdot \hat\xi_t^{(k)}$ is one column with one
coefficient, visible and testable. Sample weights act exactly as weighted least
squares. A linear model extrapolates, so a feature outside its training range
still moves the prediction, sometimes too far. Clipping or ranking features
limits the error.

**Tree ensembles.**

- *A binary regime indicator derived from a feature already in the model is
  exactly redundant.* A tree can split at any threshold on a continuous feature
  $v$, so $\mathbb{1}[v > c]$ adds no representable function. The indicator can only change
  which function the greedy search finds, and the search generally prefers
  the continuous parent. A *latent* state posterior is not a monotone function of
  any single feature, so it is not redundant. This is the one solid argument for
  using a fitted regime model rather than a threshold rule as a tree input.
- *Trees cannot extrapolate, and a new regime is precisely an extrapolation.*
  Outside the training range of a feature, a tree returns the boundary leaf's
  value, constant beyond the boundary. If volatility reaches a level never seen in training,
  the model behaves as though volatility were at the training maximum. **This is
  the most serious regime-related weakness of tree models.** It is usually
  invisible in backtests, because the backtest contains the extremes that
  training lacks only at the very end. The fix is to make features
  **regime-stationary by construction**, so that the training range covers what
  the future can produce. Divide by a trailing scale ($x_j / \hat\sigma_t$), use
  trailing percentile ranks (bounded in $[0,1]$), or rank cross-sectionally
  within each date. People normally file this under feature scaling. It is the
  most effective regime adaptation available to a tree model. **[Practice]**,
  held strongly.
- *Sample weights change splits, not just leaf values*, so their effect is larger
  and less predictable than in a linear model. Inspect the trees, not just the
  loss.
- *Monotone constraints are a cheap robustness device.* If a feature's effect
  should have a stable sign across regimes, impose it (LightGBM and XGBoost both
  support per-feature constraints). This encodes the invariance of §10.6 without
  any extra components.

**Networks.**

- *Concatenating the regime to the input is the weakest way to inject it.* The stronger
  way is multiplicative. Let the regime posterior produce a scale and shift for
  hidden activations, $a^{(\ell)} \leftarrow \gamma^{(\ell)}(\hat\xi) \odot
  a^{(\ell)} + \beta^{(\ell)}(\hat\xi)$. This is feature-wise linear modulation
  ([FiLM](#a35); [Perez et al., 2018](https://ojs.aaai.org/index.php/AAAI/article/view/11671){target="_blank"}). The regime can then switch pathways
  instead of shifting a sum.
- *Batch normalisation is an easily overlooked shift hazard.* Its running statistics fit the
  training regime. Layer normalisation uses no cross-sample
  statistics and is safer.
- *Recurrent models can encode the calendar period.* A hidden state can encode "this is
  the 2013 low-volatility era". Evaluate on held-out episodes (§11.3) and ablate
  the recurrent state.
- *Cheap uncertainty is worth having.* Deep ensembles widen their spread in
  unfamiliar conditions, which is a regime-aware sizing input obtained without a
  regime model.

**For every family**, adaptive conformal prediction ([Gibbs & Candès, 2021](https://arxiv.org/abs/2106.00170){target="_blank"})
turns any point forecast into prediction intervals whose long-run coverage holds under
distribution shift. It is the only tool in this document whose guarantee holds
*under* shift. The interval's width is a direct sizing input (§12.1).

```{=latex}
\newpage
```

## 10.9 Comparison and effort ordering

| Scheme | Shift addressed | Effort | Data cost | Fragility | Verdict |
|---|---|---|---|---|---|
| 2. Target normalisation | scale | trivial | none | low | **do first** |
| 1. Feature (posterior, time since transition) | concept (weak) | trivial | none | low | do, expect little |
| 6. Invariance filtering | all | low | none | low | **high value** |
| 3. Sample weighting | scale, covariate | low | moderate | medium | situational |
| 4. Partial pooling | concept | medium | high | medium | risk models yes, alpha no |
| 5. Gating / mixture of experts | concept | high | high | high | only for strategy switching |
| 7. Representation-learning variants | concept | medium to very high | moderate to very high | high | auxiliary task worth a try, the rest rarely |

**The recommended ordering**, with the gate at each step:

1. **Normalise the target by trailing volatility** (§10.2). Gate: out-of-sample
   information coefficient improves. It almost always does.
2. **Make every feature regime-stationary** (§10.8) with trailing z-scores or ranks.
   Gate: performance in the most extreme out-of-sample period improves.
3. **Size positions by predicted volatility** (§12.1). Gate: the strategy's realised
   volatility stabilises.
4. **Add the continuous conditioning variables as features**: volatility,
   turbulence and term structure (§10.1, encoding 3). Gate: incremental out-of-sample
   information coefficient over step 1.
5. **Run the invariance filter** (§10.6). Gate: the reduced feature set holds
   up better in the worst out-of-sample regime.
6. **Only now**, add a fitted regime posterior and its interactions (§10.1,
   encodings 2 and 4). Gate: §11's ablation ladder, in full.
7. **Only if 6 clearly passes**, consider partial pooling or gating.

Steps 1–3 are not regime modelling, and they deliver most of the benefit that people
attribute to regime modelling. This summarises the section.

> ### §10 Key takeaways
>
> 1. Normalise the target by a trailing volatility estimate. It is the cheapest
>    change available, and it addresses the shift that dominates.
> 2. The denominator must be $\mathcal{F}_t$-measurable. Normalising by realised
>    volatility over the label window is the largest leak in this
>    document.
> 3. Feed the posterior and the time since the last transition, not the hard
>    label. Duration is information the Markov assumption discards.
> 4. Regime-similarity sample weighting is a strictly better-behaved version of
>    subsetting. Always report effective sample size.
> 5. If you fit per-regime models, use partial pooling from a pooled base, never
>    hard subsetting. Penalised interactions, boosting from an offset and shrunk
>    per-regime heads all do this.
> 6. Soft gating dominates hard selection. The prediction path stays continuous
>    where you are least certain.
> 7. Invariance filtering requires of the regime estimate only what it can deliver.
>    It is the best-value scheme for a model meant to last.
> 8. Trees cannot extrapolate, so a new regime causes a silent failure. Regime-stationary
>    features fix this. They use trailing normalisation or ranking, and people normally
>    label them feature scaling.
> 9. The first three steps of the recommended ordering are not regime modelling
>    at all, and they deliver most of the benefit.

---

# 11. Research and evaluation {#11-research-and-evaluation}

Regime research fails at evaluation more often than at modelling. The failures are
specific enough to enumerate. This section sets out a protocol.

## 11.1 The evaluation ladder

Apply cheap filters first. They reject most ideas before you have spent a week on them.

```
   0.  Persistence check          |lambda_2| half-life vs your horizon    minutes
   1.  Naive-null check           beat "yesterday's volatility"?          minutes
   2.  In-sample conditional fit  necessary, nowhere near sufficient      an hour
   3.  Purged walk-forward        rung-5 states only                      a day
   4.  Ablation ladder            each increment measured separately      days
   5.  Shuffled-regime control    is the gain from the regime at all?     hours
   6.  Regime-stratified report   with EPISODE counts, not day counts     hours
   7.  Formal tests               fluctuation test, DSR, conditional PA   hours
   8.  Shadow / paper trading     the only test that cannot be gamed      months
```

Steps 0 and 1 reject most ideas in under an hour, and almost everyone skips both. Step 0 is §1.3.
Compute the half-life implied by the fitted
transition matrix and compare it to your rebalancing horizon. Step 1 tests whether
your elaborate state estimate beats the single feature "trailing 20-day realised
volatility, ranked". If it does not, stop. It frequently does not.

## 11.2 The eight leaks

Every one of these leaks improves the backtest. This is why they persist.

| # | Leak | Where it occurs | Fix |
|---|---|---|---|
| 1 | **Smoothed states** | $\xi_{t\|T}$ used as a signal | Use $\xi_{t\|t-1}$ (§5.1) |
| 2 | **Full-sample parameters** | $\hat\theta$, $\hat{\mathbf{P}}$ fitted once on everything | Expanding-window refit |
| 3 | **Full-sample labelling** | states sorted by fitted mean or volatility over the whole sample | Sort inside each window, by a stable quantity |
| 4 | **Full-sample scaling** | feature z-scores, percentile thresholds, $K$, the jump penalty $\lambda$, the decay half-life | All chosen inside the training window |
| 5 | **Label-window normalisation** | $\hat\sigma_t$ computed over $[t, t+h]$ | Trailing estimator, explicitly lagged |
| 6 | **Overlapping labels in CV** | any $h > 1$ target with $k$-fold | Purge and embargo (§11.3) |
| 7 | **Tuning on the test period** | $K$, $\lambda$, half-life, thresholds | Nested validation, or pre-register |
| 8 | **Revised macro vintages** | GDP, payrolls, industrial production as regime inputs | Real-time vintage data |

Leak 8 is specific to this field, and regime models often use macro inputs, so it needs
elaboration. **Statistical agencies revise macroeconomic series, sometimes by more than
their own standard deviation, and the revisions can arrive years later.** A model
conditioned on final-vintage GDP growth uses numbers that did not
exist at the decision date. The Philadelphia Fed's real-time data set exists for this purpose.
If your regime is macro-driven, you need it. The NBER
recession indicator is the extreme case. The committee has announced turning
points more than a year after the fact (§1.5). **[Fact]**

Leak 3 is the subtlest, and it does real damage. State labels are exchangeable
under the likelihood, so you must impose an identification rule. Suppose you impose it
on the full sample, for example "state 2 is the one with the lower mean over 1990–2024".
Then you have used the whole history to decide which state is the bad one. The
fix is to sort by a quantity that is (a) stable and (b) computed inside the
window, such as fitted volatility, ascending. As §8.3 shows, when the states do not
differ in volatility, no rule works and the pipeline is worse than nothing.

## 11.3 Cross-validation design

Standard $k$-fold cross-validation is invalid here for three independent reasons.
Each one alone disqualifies it:

1. **Overlapping labels.** A target realised over $[t, t+h]$ shares data with the
   targets at $t+1, \dots, t+h-1$. A fold boundary in the middle of that window
   puts nearly identical observations on both sides.
2. **Serial correlation in features.** Trailing volatility at $t$ and $t+1$ are
   nearly the same number, so a training point adjacent to a test point is close
   to a copy of it.
3. **Regime blocks.** This reason is specific to regime research, and it is the worst.
   Regimes are persistent, so a random fold split places the *same regime* on
   both sides of every boundary. The evaluation then tests the model on regimes from its
   training data. That is the question you are trying to answer, and the split answers it
   in advance, in the affirmative.

Purging and embargoing fix the first two reasons.

```{=html}
<img class="mdd-fig" src="quant-research/figures/purged_split.svg"
     alt="A purged, embargoed train/test split: training observations whose label windows extend into the test block are purged before it, and those whose features overlap the test period's serial correlation are embargoed after it.">
```

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/purged_split.pdf}
\end{center}
```

The third reason needs a different remedy. This is where the interesting design choice
arises. The options are:

- **Walk-forward** is the correct default. Train on $[0, T_i]$, test on
  $(T_i, T_{i+1}]$, and roll forward. Every test period is genuinely in the future.
- **Combinatorial purged CV** (López de Prado, 2018) constructs many
  train/test path combinations from the same data and applies purging
  throughout. It gives a *distribution* of backtest outcomes rather than a single
  path. Use it to answer the question "was my walk-forward result luck". The implementation cost
  is worth paying.
- **Do not stratify folds by regime.** Many people want each fold to contain both regimes so the
  estimates are stable. Stratifying destroys the experiment,
  because it guarantees the model has seen the test regime.
- **Leave-one-episode-out** is the recommended test to run and report. Hold out
  one complete regime episode, such as the 2008 crisis, March 2020 or the 2022 rate shock.
  Train on everything else and evaluate on the held-out episode. One episode does not give clean
  inference. It is still the closest available approximation to
  the question you care about: "how will this behave in a bad
  period it has not seen".

## 11.4 The ablation ladder

The ablation ladder is a specific experiment sequence. Every rung uses the **same** purged
walk-forward split, the same test period and the same evaluation metric, so that
the increments are comparable. Report each increment with a standard error.

| Rung | Model | What it isolates |
|---|---|---|
| A0 | Unconditional constant | the null |
| A1 | Base model, raw target, raw features | your actual baseline |
| A2 | A1 + target volatility normalisation | conditional-scale drift (§10.2) |
| A3 | A2 + regime-stationary features (trailing ranks) | feature-range shift (§10.8) |
| A4 | A3 + continuous conditioning variables | observable state, no latent model |
| A5 | A4 + regime posterior as a feature | what the latent model adds |
| A6 | A5 + regime $\times$ signal interactions | explicit concept-drift conditioning |
| A7 | A6 + partial pooling or gating | separate functions per regime |
| **C1** | **A5 with a *shuffled* regime** | **whether the regime matters at all** |
| **C2** | **A5 with a regime fitted on a different asset** | whether the regime is asset-specific or generic |
| C3 | A5 with the regime replaced by trailing volatility rank | whether the latent model beats the obvious proxy |

**The two controls in bold decide whether you have anything.**

**C1, the shuffled-regime control**, is the most important experiment in this
document, and almost nobody runs it. Replace the fitted state path with a
synthetic path that has the *same marginal distribution and the same persistence*
but no relationship to the data. Use a block bootstrap of the state sequence, or a
simulated Markov chain with the fitted $\hat{\mathbf{P}}$. Refit everything. If
the shuffled version performs as well as the real one, your improvement came from
the extra model capacity and the extra column, not from the regime. You have then
learned something valuable for the cost of one rerun.

**C3 tests the latent model against a simple proxy.** If the latent-state posterior does not beat "the
percentile rank of trailing 20-day realised volatility", use the volatility rank.
The volatility rank has no identification problem, no label switching, no filtering, and no
$K$.

## 11.5 Report by regime — and count episodes, not days

Report any regime-conditional claim stratified by regime, with:

- performance within each regime,
- the number of **days** in each regime,
- and, separately and much more importantly, the number of **episodes**.

**The effective sample size for a regime-conditional claim is the number of
independent regime episodes, not the number of observations.** Consider twenty years of
daily data with a 25-day turbulent state that begins roughly twice a year. The data contain
about 40 episodes and about 1,000 turbulent days. The 40 governs your standard errors.

The standard error of an annualised Sharpe ratio
estimated over $y$ years is approximately $\sqrt{(1 + S^2/2)/y}$. Suppose the
turbulent regime occupies 20% of a 20-year sample, which is four years of turbulent
time. Then a within-regime Sharpe of 0.5 has a standard error of **0.53**.

> You cannot distinguish "this strategy has a Sharpe of 0 in crises" from "this
> strategy has a Sharpe of 1 in crises" with twenty years of daily data. Any
> claim about crisis-regime performance that does not acknowledge this is
> reporting noise.

The 0.53 is the *optimistic* figure, because the formula treats the four
years of turbulent days as independent observations. It answers "how precisely
have I measured performance in the crises I saw". The question you care
about is "will this work in the next crisis". The forty episodes govern that question,
not the thousand days, and its standard error is correspondingly worse. The two
numbers do not conflict. They limit the precision of different quantities, and the episode
count limits the one that matters.

This is the same identification problem as §8.1. It applies as strongly
to the *evaluation* of a regime strategy as to the *estimation* of a regime model.

## 11.6 Formal tests worth running

Four tests are worth running, in order of value per hour spent:

**Giacomini-Rossi fluctuation test (2010).** Compute the rolling relative
out-of-sample loss of model A versus model B. Compare its path against
critical values that account for looking at the maximum
over time. This directly answers "does my model's advantage come and go", which
is the regime question stated as a forecasting question. **If your regime-aware
model is genuinely better, its advantage should concentrate in the regime you
designed it for, and the fluctuation test will show you that.** If the advantage
varies with no relation to the regime, it has another source.

**Giacomini-White conditional predictive ability (2006).** This test checks whether A beats
B *conditional on the current state* rather than on average. This is the quantity of
interest, and it should be standard in this literature. It is not standard.

**Deflated Sharpe ratio (Bailey & López de Prado, 2014).** This adjusts an observed
Sharpe for the number of trials and for skew and kurtosis. It is necessary here because
**regime slicing multiplies trials fast**. The count is $K$ regimes $\times$ $M$
specifications $\times$ $W$ window choices, and each combination you looked at is
a trial whether or not you reported it. The expected maximum of
20 independent standard normal draws is about 1.87, and of 100 about 2.51. With
a within-regime Sharpe standard error of 0.53 (§11.5), **twenty honest trials
produce an expected best-of-sample crisis Sharpe of about 1.0 from pure noise.**
That Sharpe is higher than most published regime results report.

**Stationary bootstrap** (Politis & Romano, 1994) gives confidence intervals on
path-dependent statistics. Block length should exceed your regime persistence.
Otherwise the bootstrap destroys the structure you are testing. This error is subtle and common.
Resampling in blocks shorter than the regime half-life produces a null in
which regimes do not exist, and that null makes any regime strategy look better than it is.

## 11.7 Synthetic data: two tests, both essential

You have a generative model. Use it.

**Test 1 — recovery.** Simulate from a known regime process and run your entire
pipeline end to end. Check that it recovers the truth. Check that your reported
confidence intervals have the coverage they claim. Everything in §8 came from
this exercise, and every surprise in it was informative.

**Test 2 — the null.** Simulate from a process with **no regimes at all**, such as a
GARCH or stochastic-volatility model calibrated to the same unconditional moments.
Run the identical pipeline. **Your pipeline should report no edge.**
If it reports an edge, you have a bug or a leak, and you have found it before it cost
you money.

Almost nobody runs Test 2, and it catches more problems than any other single
check. It operationalises §2.6 directly. If a no-regime
process yields a regime strategy that appears to work, your positive result
on real data is uninformative.

## 11.8 The protocol, condensed

1. Fit the state model on the **training window only**. Refit on an expanding
   schedule. Never touch the test period.
2. Identify states by a rule computed inside the window (volatility, ascending).
3. Emit $\xi_{t|t-1}$ only. Store the rung with the number.
4. Normalise the target by a trailing volatility estimate. Verify by construction
   that the denominator uses no data after $t$.
5. Split with purging and embargo sized to your label horizon. Prefer walk-forward.
   Add combinatorial purged CV for a distribution.
6. Run the ablation ladder A0–A7 with identical splits and metrics.
7. Run controls C1 (shuffled regime), C2 (foreign regime), C3 (volatility rank).
   **If C1 matches A5, stop.**
8. Report stratified by regime, with episode counts and Sharpe standard errors.
9. Run the fluctuation test and the deflated Sharpe with an honest trial count.
10. Run the synthetic null. Confirm no edge.
11. Shadow-trade before sizing.

> ### §11 Key takeaways
>
> 1. Two checks that cost under an hour reject most regime ideas. They are the
>    transition-matrix half-life against your horizon, and beating trailing
>    volatility rank. Run them first.
> 2. Regime models have eight distinct, regime-specific leaks. Full-sample labelling and
>    revised macro vintages are the two that persist in otherwise careful pipelines.
> 3. $k$-fold CV fails here for three independent reasons. Purging does not fix
>    the regime-block reason.
> 4. Never stratify folds by regime. It guarantees the model has seen the test
>    regime and destroys the experiment.
> 5. The shuffled-regime control has the same marginal, the same persistence and no
>    relationship to the data. It is the single most informative experiment
>    available, and almost nobody runs it.
> 6. The effective sample size for a regime claim is the number of episodes, not
>    days. Four years of crisis time gives a Sharpe standard error above 0.5.
> 7. Twenty honest trials produce an expected best crisis Sharpe near 1.0 under
>    the null. Deflate accordingly.
> 8. Bootstrap block length must exceed regime persistence. Otherwise your null has no
>    regimes in it and every regime strategy looks good.
> 9. Simulate from a no-regime process and confirm your pipeline finds nothing.
>    This catches more than any other single check.

---

# 12. Trading a regime-aware model {#12-trading-a-regime-aware-model}

You have a state posterior, and perhaps a forecasting model that uses it. This
section covers trading it. This step loses most of the theoretical gain.

## 12.1 Do not gate. Size.

The instinctive use of a regime model is an on-off switch. In the risk-on state, the strategy holds its position. In the risk-off state, it goes flat.
A better use scales the position continuously. The *correct* use is neither:
feed the mixture's moments into the position rule and let the
arithmetic set the size.

**The correct object.** Your model gives a predictive mixture (§1.2). Its first
two moments are

$$
\begin{aligned}
\mathbb{E}[r_t \mid \mathcal{F}_{t-1}] &= \sum_k \xi_{t|t-1}^{(k)} \mu_k \;\equiv\; \bar\mu_t, \\[4pt]
\operatorname{Var}[r_t \mid \mathcal{F}_{t-1}] &=
   \underbrace{\sum_k \xi_{t|t-1}^{(k)} \sigma_k^2}_{\text{within-state risk}}
   + \underbrace{\sum_k \xi_{t|t-1}^{(k)} (\mu_k - \bar\mu_t)^2}_{\text{state uncertainty}} ,
\end{aligned}
$$

and the mean-variance position is $\pi_t = \bar\mu_t / (\gamma \operatorname{Var}[r_t \mid \mathcal{F}_{t-1}])$.

**The position shrinks by itself, through the first term.** As the posterior
shifts toward the turbulent state, the within-state term rises from
$\sigma_1^2$ to $\sigma_2^2$. With the §8 calibration, the predictive
volatility is 12.0%, 19.1%, 24.2%, 28.4% and 32.0% as $\xi^{(2)}_{t|t-1}$ goes
0, 0.25, 0.5, 0.75 and 1. Position scales as $1/\operatorname{Var}$, not
$1/\sigma$. So the mean-variance position at full turbulence is
$(12.0/32.0)^2 =$ **14.1% of its calm-state size**. This holds the mean fixed, so
only the within-state term acts. The rule needs no threshold, no hysteresis rule and no special
case. The de-risking follows from using the full mixture instead of
collapsing it to a label.

**The second term is real but small.** Both $\mu_k$
and $\sigma_k^2$ here are *per bar*. A mean difference enters squared while a
variance enters linearly, so the between-state term is smaller by a factor of
order $A$. At a 50/50 posterior between the $+10\%$ and $-15\%$
states, the between-state term contributes 0.79% of annualised volatility. The
within-state term contributes 24.2%. The between-state term is about one part in a thousand of the variance.
A common error is to write the dispersion of *annualised* means,
$(0.125)^2 = 1.6\%$, and conclude that state uncertainty dominates. That conclusion is wrong
by the factor $A = 252$. Suppose the state stayed put for $h$ bars. That
case favours the between-state term most. The squared gap between
cumulative means grows as $h^2$, while the cumulative variance grows only as $h$.
So the between-state term overtakes the within-state term only at a horizon of
roughly $4\sigma^2/(\Delta\mu)^2 \approx 940$ bars, about **3.7 years**. Here
$\sigma^2$ and $\Delta\mu$ are per bar, and the 4 is $1/[\xi(1-\xi)]$ at a 50/50
posterior. A state that mean-reverts, as these do, only pushes the crossover
later. This is the identification asymmetry (§8.1) again. Uncertainty about *which mean* you face is negligible next to
uncertainty about *how volatile* things are, until you hold for years.

This answers §1.2's warning about argmax labels in operational terms.
**Feed the moments, not the label.**

**The measurement.** The table below comes from the same simulation as §8.4. It compares a hard gate
(flat when the predicted state is turbulent), volatility sizing
(scale by $1/\sqrt{\operatorname{Var}}$) and the combination of the two.

**[Simulated]**

| States separated by | Buy & hold | Gate | Size | Both |
|---|---|---|---|---|
| Volatility and mean | 0.26 | 0.54 | 0.45 | **0.57** |
| Volatility only | 0.26 | 0.29 | 0.31 | **0.31** |
| Mild volatility | 0.42 | 0.50 | 0.45 | **0.51** |
| Mean only | 0.55 | 0.55 | 0.55 | 0.55 |

Gating beats sizing when the states genuinely differ in mean. Sizing beats gating
when they differ only in volatility. The combination wins or ties in every row. But
the more useful reading compares **what each column's
advantage depends on**, not which column is larger. Gating's edge depends entirely on $\mu_1 - \mu_2$, the
quantity §8.1 says you cannot estimate. Sizing's edge depends on
$\sigma_2/\sigma_1$, the quantity you can estimate to within a few percent.
**Under parameter uncertainty, which is the real world, sizing is the robust
choice, because its benefit does not depend on the number you cannot measure.**
The simulation above supplies both quantities to the strategy. Your
backtest will not supply them.

**On real data**, the worked example of §6.11 runs the same comparison on US
equities from 1946 to 2025, with walk-forward parameters. The gate earns a Sharpe
ratio of 0.60 and the HMM volatility target earns 0.62. Buy and hold earns 0.52.
The standard error is about 0.12, so the sample cannot rank the gate and the volatility target. They
differ where the arithmetic above says they should. The gate cut the maximum
drawdown further, to 38% against 44% for the volatility target. But it gave up 2.4
points of annual return against buy and hold, because the days it stayed flat had
the same average return as the days it held. The gate's gain came entirely from lower
volatility, which sizing captures without taking a position on the mean.

## 12.2 Hysteresis, buffering, and the cube-root rule

A hard threshold at $\xi = 0.5$ produces rapid switching whenever the posterior stays
near a half. This is when the evidence is weakest and trading is least
justified. Three fixes follow, in increasing order of quality:

1. **Two thresholds.** This is a Schmitt trigger, the electronics term for a switch
   whose turn-on and turn-off points differ. A noisy input near the
   boundary cannot make such a switch change state repeatedly. Enter the defensive state at
   $\xi > 0.7$ and leave it at $\xi < 0.3$. This is crude and effective, and it adds one extra parameter.
   It also introduces path dependence, which you must then model in the backtest.
2. **Continuous sizing** (§12.1). This produces no switching by construction, because the
   position is a continuous function of a continuous posterior. The cost moves
   from a few large trades to many small ones. In the §8.4 calibration that
   is a large saving, not a wash. Total annual turnover falls from 8.8
   units under the hard gate to 4.0 under continuous sizing. **[Simulated]**
3. **A no-trade band.** Trade only when the target position differs from the
   current one by more than a band $\delta$. Under proportional transaction
   costs $\varepsilon$ (Constantinides, 1986; and the continuous-time treatments that followed),
   the classical result is that the optimal no-trade
   half-width scales as

   $$\delta \propto \varepsilon^{1/3}.$$

   **The cube root matters most in practice.** A ten-fold increase in
   trading costs widens the optimal band by only $10^{1/3} \approx 2.15$. People
   consistently over-widen bands in response to cost estimates. The correct
   response is much milder than intuition suggests. Under *quadratic* costs the
   answer is different and equally clean. Gârleanu and Pedersen (2013) show that the optimal
   policy is to trade a constant fraction of the way toward an aim
   portfolio. The aim portfolio tilts toward slower-decaying signals. In their words: "aim in front of the
   target, and trade partially towards the aim". Regime signals decay fast
   (§1.3). Under this framework they get *less* weight in the aim than their
   raw strength suggests.

## 12.3 Does the overlay pay for itself?

Do this arithmetic before building anything. Use the numbers from §8.4 and the
turnover from the same simulation.

**[Simulated]** The mild-volatility calibration, which is the realistic one, gives a
gated strategy with a mean absolute daily position change of **0.0350**. Annual
position turnover is therefore $0.0350 \times 252 = 8.8$ units of $|\Delta \pi|$. Each
such unit is one unit traded in one direction, so the annual cost is
$8.8 \times c$ for a one-way cost $c$. The strategy runs at 15.0% annualised
volatility and beats buy-and-hold by 0.50 − 0.42 = 0.08 Sharpe. This is
$0.08 \times 0.150 \approx$ **118 basis points a year** gross. The figure is 118 rather than
the 120 the rounded factors suggest, because the underlying Sharpe gap is 0.0785,
not exactly 0.08. The script
[`figures/regime_filtration.py`](https://github.com/rmahfoud/quant-research/blob/master/figures/regime_filtration.py){target="_blank"} prints all four numbers.

| One-way cost | Annual cost | Net of 118 bp gross |
|---|---|---|
| 2 bp (index future) | 18 bp | **+100 bp** |
| 5 bp (liquid ETF) | 44 bp | **+74 bp** |
| 10 bp (single stock, in size) | 88 bp | +30 bp |
| 20 bp (less liquid) | 176 bp | **−58 bp** |

**The break-even one-way cost is $118/8.8 \approx 13$ basis points.** The overlay is comfortable
on futures and liquid ETFs, marginal on single stocks traded in size, and
negative beyond that. These figures also ignore that the 118 bp came from a simulation that
gave you the true parameters, the right $K$, and
the right emission family. This single table should determine whether you start
the project.

Three implications follow. First, regime overlays belong on the most liquid instruments
you have: index futures, major FX and rates. The CTA
industry applies them there, for the same reason. Second, if you must apply
an overlay to a less liquid book, apply it at the *portfolio* level, on
aggregate exposure rather than instrument by instrument. Then the book pays the turnover once, on the cheapest hedging instrument. Third, **continuous sizing turns over 4.0 units a year
against the hard gate's 8.8**, so its trading cost is 45% of the gate's. This is the cost argument
for §12.1's recommendation. Its
gross Sharpe in this calibration is lower (0.45 against 0.50, §12.1), but it does
not depend on the mean spread. The saving is not automatic. The order reverses on the real data of
§6.11. There the HMM volatility target turns over 14.2 units
a year against the gate's 9.5. Measure the turnover of your own sizing rule
before costing it.

## 12.4 Where regimes help most: the covariance matrix

For a multi-asset book, the regime-conditional *covariance* matters more than the
regime-conditional mean. Diversification weakens in crises, when it is most needed.
A covariance matrix estimated on a full sample understates crisis co-movement.

Practical approaches, in ascending order of ambition:

- **Two-state covariance blending.** Estimate $\Sigma_{\text{calm}}$ and
  $\Sigma_{\text{stress}}$ on turbulence-sorted subsamples (Chow, Jacquier,
  Kritzman & Lowry, 1999) and use
  $\Sigma_t = \xi^{(1)}_t \Sigma_{\text{calm}} + \xi^{(2)}_t \Sigma_{\text{stress}}$.
  This is cheap and captures most of the effect. It is §9.5's "subset the risk
  model" prescription made concrete.
- **Stress-weighted shrinkage.** Shrink the sample covariance toward the stress
  covariance rather than toward the identity or a constant-correlation target.
  This is a one-line change to a standard pipeline, and it gives a much better prior.
- **Regime-switching DCC** (Pelletier, 2006) gives a full dynamic model. It is more
  correct and considerably more complex.

**A caveat applies to this recommendation.** Part of the measured correlation
increase in crises is a mechanical artefact of the volatility increase ([Forbes &
Rigobon, 2002](https://www.nber.org/papers/w7267){target="_blank"}). Apply their correction before you conclude that correlations
genuinely rose. Otherwise you will double-count. Your volatility model already captured
the variance increase, and the "correlation regime" you then add on top partly repeats
the same effect.

## 12.5 Capacity, crowding, and reflexivity

Regime signals have one uncomfortable property: **they are public, and
they all give the same signal at the same time.** Realised volatility, the VIX,
the 200-day moving average and every fitted two-state HMM agree, because they
all measure the same underlying quantity (§7.2). The de-risking trade is
therefore among the most crowded trades in existence. It arrives as a
simultaneous, mechanical, price-insensitive flow.
simultaneous, mechanical, price-insensitive flow.

§2.1 implies a reflexive consequence: **your regime overlay is a
component of the mechanism that generates the regime.** Volatility rises. Volatility-targeting strategies
mechanically reduce exposure. The selling pushes prices down and volatility up.
The next round of de-risking follows. This is the fire-sale channel, with systematic strategies as the intermediary.
**[Hypothesis]** The mechanism is well specified and the flow estimates are
large, but researchers contest attributing specific episodes to it.

In practice:

- Assume your exits are correlated with everyone else's, and cost them at stress
  levels rather than at average levels. The cost table in §12.3 is optimistic for
  exactly the days when the overlay triggers.
- Prefer signals with idiosyncratic timing where you can find them. A slower or
  faster horizon than the industry standard is a real, if small, edge.
- Size for the possibility that you cannot exit at all.

## 12.6 Monitoring: what breaks, and how you would know

A deployed regime model has specific failure modes with specific detectors.

| What breaks | Detector | Trigger |
|---|---|---|
| The state definition drifts | $\hat\sigma_k$, $\hat{\mathbf{P}}$ tracked across refits | any parameter moving more than its bootstrap CI |
| Label switching between refits | correlation of the new state path with the old on overlapping data | correlation below ~0.8 |
| The model no longer describes the data | posterior entropy $-\sum_k \xi^{(k)}\ln\xi^{(k)}$ | sustained rise above its historical range |
| Occupancy drift | realised time in each state vs the stationary $\boldsymbol{\pi}$ | large or sustained divergence |
| Turnover surge | realised versus backtested turnover | ratio above ~1.5 |
| Feature extrapolation (trees) | share of predictions at a boundary leaf | any material rise (§10.8) |
| The strategy itself is failing | BOCPD run-length posterior on the **strategy's own returns** | run-length posterior collapsing |

Run the last row regardless of everything else in this document. A
change-point detector applied to your own P&L is the most direct available answer to
"has this stopped working". It is model-free. It is a much better use of
change-point methods than using them to detect market regimes (§5.6).

Set the response in advance and make it graduated. **Reduce size** on entropy or
occupancy alarms. **Retrain** on parameter drift. **Halt and escalate** on a
turnover surge or run-length collapse. Thresholds decided during a drawdown tend to get overridden.

## 12.7 A reference architecture

The diagram shows the pipeline with the filtration boundary drawn explicitly.
Everything to the left of it may use only $\mathcal{F}_{t-1}$.

```
   ╔═══ F(t-1) ═══ everything inside this box may use only past data ═══╗
   ║                                                                    ║
   ║  prices      ──▶ trailing volatility  ─┐                           ║
   ║  macro (RT)  ──▶ turbulence index     ─┼─▶ state model ─▶ xi(t|t-1)║
   ║  x-section   ──▶ dispersion, corr     ─┘   refit expanding    │    ║
   ║                                                               │    ║
   ║  features    ──▶ trailing rank / z-score ────────────┐        │    ║
   ║                                                      ▼        ▼    ║
   ║  target y    ──▶ divide by trailing sigma ──▶ ┌────────────────┐   ║
   ║                                              │ model f(x, xi) │   ║
   ║                                              │  any learner   │   ║
   ║                                              └────────────────┘   ║
   ╚═══════════════════════════════════════════════════════│═══════════╝
                                                           │ Sharpe forecast
                                                           ▼
                   mixture moments ──▶ position = mu_bar / (gamma * Var)
                                                           │
                                     no-trade band, cost model
                                                           ▼
                                                        orders
                                                           │
                          monitors ◀───────────────  realised P and L
```

This diagram has three properties. **The state model and the
feature scaling sit inside the same causal boundary.** Both must be refit on
expanding windows, and people forget the feature scaling. **The target
normalisation happens before the model, and the position scaling after it.**
So the volatility estimate appears twice, and both appearances are correct (§10.2).
**The posterior reaches the position rule as moments, not as a label.** So
state uncertainty automatically reduces size (§12.1).

> ### §12 Key takeaways
>
> 1. Feed the mixture's moments to the position rule, not the argmax label. State
>    uncertainty then inflates predictive variance and shrinks the position
>    automatically. No threshold or hysteresis rule is needed.
> 2. Gating's benefit depends on the mean spread, which you cannot estimate.
>    Sizing's benefit depends on the volatility ratio, which you can. Under parameter
>    uncertainty, size.
> 3. The optimal no-trade band widens as the *cube root* of transaction cost. A
>    tenfold cost increase roughly doubles the band. Do not over-widen.
> 4. Regime signals decay fast, so in a Gârleanu-Pedersen aim portfolio they
>    receive less weight than their raw strength suggests.
> 5. Run the cost arithmetic first. A regime overlay is worth about 118 bp gross
>    in the realistic calibration, and the break-even one-way cost is 13 bp. Those
>    numbers decide whether to start the project.
> 6. The genuine multi-asset benefit comes from the regime-conditional covariance,
>    not the regime-conditional mean. Blend a stress covariance in by posterior weight.
> 7. Correct correlation increases for the volatility artefact before modelling
>    them. Otherwise you count the same effect twice.
> 8. Everyone's regime signal triggers at once, and your overlay is part of the
>    mechanism that produces the regime. Cost your exits at stress levels.
> 9. Run a change-point detector on your own P&L. It is the best available answer
>    to "has this stopped working", and a better use of change-point methods than regime
>    detection.

---

# 13. Synthesis {#13-synthesis}

## 13.1 The framework in one loop

Six links generate everything in this document. Each link follows from the one before.

```mermaid
flowchart TD
    M["MECHANISM<br/>Constraints bind or they do not.<br/>Discreteness comes from<br/>complementary slackness"]
      --> O["OBSERVABLE SIGNATURE<br/>Volatility and correlation jump.<br/>Means barely move"]
    O --> E["WHAT IS ESTIMABLE<br/>Variance error falls with the number<br/>of observations. Mean error falls only<br/>with calendar span"]
    E --> U["WHAT THE MODEL IS FOR<br/>Sizing and covariance.<br/>Not direction"]
    U --> C["HOW IT IS USED<br/>Mixture moments into the position rule,<br/>a regime covariance, a normalised target.<br/>Not a regime dummy"]
    C --> V["WHAT TO VERIFY<br/>Predicted states only.<br/>Shuffled-regime control.<br/>Episode counts, not day counts"]
    V -.->|"if it fails here,<br/>the mechanism was not real"| M
    style E fill:#0b6e4f,color:#fff
    style C fill:#0b6e4f,color:#fff
```

The following passage states the whole document in compressed prose:

> A market regime is a discrete summary that you impose on a conditional density.
> It is not a property of the market. Its only forecasting content is the
> persistence of the state. The standard error of a variance falls with
> the number of observations. The standard error of a mean falls only with
> calendar span. So a regime model can identify volatility states precisely and
> cannot identify return states at all. Everything downstream follows. The model is worth
> having for sizing and for covariance, not for direction. It enters decisions
> through the position rule and the risk model, and a forecasting model uses it through
> the target rather than through a feature. Pool the means across regimes and
> let the variances switch. The refinements that pay are the ones that buy
> persistence from a few dozen transitions, such as heavy-tailed emissions and
> sticky priors. The only meaningful state estimate is the
> one-step-ahead prediction computed with parameters that have not seen the
> future.

```{=latex}
\newpage
```

## 13.2 Decision tree

The tree asks the four questions that change the answer. Each branch ends in a named choice.

```mermaid
flowchart TB
    Q0("Start: you want to<br/>condition on market state") --> Q1("Is the state's half-life<br/>longer than your<br/>rebalancing horizon?")
    Q1 -->|no| STOP["STOP. The model cannot<br/>inform this decision.<br/>Section 1.3"]
    Q1 -->|yes| Q2("Can you name the<br/>observable that defines<br/>your regime?")
    Q2 -->|yes| T1["Threshold or<br/>smooth-transition rule<br/>on that observable.<br/>Section 5.5"]
    Q2 -->|no| Q3("Is the downstream<br/>decision genuinely<br/>discrete?")
    Q3 -->|no| T2["Continuous state:<br/>trailing volatility,<br/>turbulence index, EWMA.<br/>Section 5.9"]
    Q3 -->|yes| Q4("Do you need calibrated<br/>probabilities or a<br/>predictive density?")
    Q4 -->|yes| T3["Regularised HMM:<br/>Student-t emissions,<br/>sticky prior.<br/>Section 6"]
    Q4 -->|no| T4["Statistical jump model,<br/>online variant.<br/>Section 5.7"]
    style STOP fill:#8b1a1a,color:#fff
    style T1 fill:#0b6e4f,color:#fff
    style T2 fill:#0b6e4f,color:#fff
```

Five steps apply on every branch. Normalise any forecasting target by trailing
volatility. Make features regime-stationary. Size from mixture moments, never
from a label. Use predicted states with expanding-window parameters only. Run
the shuffled-regime control.

The tree sends most people to a threshold rule on an observable or to a continuous state variable. You reach the latent-state branches only when you
genuinely cannot name the driver *and* your decision is genuinely discrete.
These situations are fewer than the volume of literature suggests. Of the two latent branches, take the HMM when the output
must be a probability. Examples are a position sized from mixture moments, a covariance
blended by state weight, or a decision that weighs the cost of being wrong.

## 13.3 A staged build, with gates

Each stage has a gate. Failing a gate means stopping, not tuning until it passes.

**Stage 0 — Infrastructure (two weeks).** This stage is not the interesting part.
Build point-in-time data with real-time macro vintages. Build a backtester that makes
look-ahead structurally impossible rather than merely discouraged. Features and
targets carry explicit timestamps, and an assertion checks that no feature timestamp
exceeds its decision timestamp. Use purged, embargoed splits. *Gate: reproduce a
known-null result. Run the whole pipeline on shuffled returns and confirm it
finds nothing.*

**Stage 1 — The baseline you must beat (one week).** Rank trailing volatility.
Size the position by inverse volatility. Use no regimes anywhere. *Gate: this is now
your benchmark. Measure every later stage against it, not against buy-and-hold.*

**Stage 2 — Target and feature normalisation (one week).** Vol-normalise the
target. Convert every feature to a trailing rank or z-score. *Gate: out-of-sample
information coefficient improves, and performance in the most extreme held-out
period improves. If not, something is wrong, because this almost always helps.*

**Stage 3 — Continuous conditioning (two weeks).** Add realised volatility,
turbulence, dispersion and term-structure slope as features and as explicit
interactions with your main signals. *Gate: incremental out-of-sample improvement
over Stage 2, with a standard error.*

**Stage 4 — A state model (three weeks).** Fit a two-state HMM with Student-t
emissions, variance-only switching and a sticky prior by penalised EM
(§6.3, §6.7). Alternatively, fit a statistical jump model on volatility features, online variant
(§5.7). Refit on an expanding window and identify states by fitted volatility. Emit
$\xi_{t|t-1}$. Check pseudo-residuals and compare the HMM against an EWMA with
Student-t innovations (§6.9). *Gate: the model beats Stage 3 and beats control C3, the
trailing volatility rank. Most projects should end here, having failed this
gate. That outcome is a success, because it saves the three weeks that Stage 5 would
have cost.*

**Stage 5 — Conditioning on the state (three weeks).** Add the posterior as a feature, with
time-since-transition and entropy. Add interactions with signals. Add a regime-conditional
covariance for the portfolio. If you use the HMM directly rather than through a
forecasting model, this stage is the direct use of §6.10. *Gate: the full ablation ladder of §11.4, including
the shuffled-regime control C1. If C1 matches, stop.*

**Stage 6 — Sizing and execution (two weeks).** Feed mixture moments into the position
rule. Set the no-trade band from the cube-root rule. Compute the cost table of §12.3
with your own costs. *Gate: net of realistic stressed costs, the overlay still
earns a positive return.*

**Stage 7 — Monitoring (one week, and never finished).** Use the table in §12.6, with
pre-agreed graduated responses.

Stages 0 through 2 are infrastructure and normalisation. They deliver the benefit. People skip them to get to the modelling.

## 13.4 Ten rules for someone starting today

1. **Compute the transition matrix's second eigenvalue before anything else.** If
   its half-life is shorter than your rebalancing horizon, the project is over.
   You have spent ten minutes.
2. **Normalise your target by trailing volatility.** It takes one line and
   addresses the shift that dominates. Without it, a fifth of your sample
   supplies two thirds of your loss.
3. **Assume the regime is volatility.** It nearly always is. Design for a
   volatility regime and you will be right. Design for a mean regime and the data will not support you.
4. **Never report a smoothed state probability without labelling it.** Never
   trade one.
5. **Sort states by fitted volatility, inside the estimation window.** Sorting by
   mean, or sorting on the full sample, creates a look-ahead that is hard to detect.
6. **Run the shuffled-regime control.** It takes one rerun. The result tells you whether the regime adds information, instead of leaving you to assume it does.
7. **Count episodes, not days.** Your sample size is forty crises, not five
   thousand observations. The standard errors follow from the forty.
8. **Do the cost arithmetic before building.** Do not start a project with 118 basis points gross against
   176 basis points of costs.
9. **Pool the means, switch the variances, and use heavy-tailed emissions.** The
   identification asymmetry says which parameters to let vary. Student-t
   emissions stop single outliers from triggering false regime changes.
10. **Try to falsify the regime rather than to find it.** Simulate from a
    no-regime process and confirm your pipeline reports nothing. If it reports
    something, everything else you have measured is uninterpretable.

## 13.5 What is known, what is not, and where the evidence points

**Known.** [Fact] Volatility stays at one level for long stretches. Models that represent this, whether discrete or continuous, forecast better than models that do not. Correlations rise in stressed periods. Part of the rise is mechanical and part is not. Regime-aware position sizing reliably reduces realised volatility and drawdown, across markets and decades. The likelihood-ratio test for the number of regimes is invalid. The standard errors on regime-conditional means are far larger than the literature's presentation implies.

**Not known.** The evidence does not settle whether financial "regimes" are genuinely discrete or a discretisation of a continuous latent process. The evidence is compatible with both. [Diebold and Inoue (2001)](https://www.nber.org/papers/t0264){target="_blank"} showed that the two are analytically confusable, so return data may never resolve the question. The evidence also does not settle whether regime-conditional expected returns exist in a form stable enough to trade. The recession-predictability results are real in sample and contested out of sample. Finally, nobody has demonstrated whether the crowding of systematic de-risking has changed the dynamics of the regimes themselves. The idea is plausible. **[Hypothesis]**

**Where the evidence points.** This is the chapter's assessment, not a settled result. Practitioners attribute most of the value to regime models, but that value comes from three things that are not regime models. These are volatility-normalised targets, volatility-scaled positions and regime-stationary features. When a fitted state model is worth using at all, use it to supply moments to a sizing rule and a covariance to a portfolio optimiser. Never use it to supply a label to a classifier. The worked example of §6.11 is consistent with all of this. On a century of US data, the HMM's states separate volatility by a factor of 2.3 out of sample and do not separate returns at all. The gain from using them is a modest Sharpe improvement and a large drawdown reduction. The highest-value unexploited idea in this space is the inverse one. **Use regimes as environments to find the relationships that do not change, rather than as conditions to adapt to.** A forty-episode sample supports invariance better than adaptation. Research time is best spent there.

**The largest open methodological problem** is the same one that afflicts trend-following. The long-history evidence that regime overlays add value comes disproportionately from firms that sell them. The academic evidence is dominated by in-sample fits and smoothed state probabilities. A study that ran the protocol of §11 across many markets and a century of data would settle more than any new model could. It would use rung-5 states, shuffled-regime controls, episode-counted standard errors and realistic stressed costs. Nobody has an incentive to publish it, which is why it would be worth reading.

The parts of this field that survive scrutiny are the parts you can verify yourself in an afternoon of simulation. They point in a consistent direction. Volatility is knowable and worth acting on. Direction is not knowable, in regimes as everywhere else.

---

# Appendix A. Concepts and prerequisites {#appendix-a-concepts-and-prerequisites}

This appendix covers the concepts the main text uses without explaining them. Entries follow dependency order, not alphabetical order. Later entries use earlier ones, so the appendix reads as a build-up rather than a dictionary. Each entry gives the idea in words, then the formal definition, then the reason it appears here, then a pointer to further reading.

**Index.** Where each concept is first used:

| Concept | First used | Concept | First used |
|---|---|---|---|
| [Filtration and measurability](#a1) | §1.2 | [Bayesian nonparametrics](#a24) | §6.4 |
| [Predictive density](#a2) | §1.2 | [Sharpe ratio and its error](#a25) | §5.1 |
| [PIT and pseudo-residuals](#a3) | §6.9 | [Risk premia and priced factors](#a26) | §2.1 |
| [Markov chains and mixing](#a4) | §1.3 | [Limits to arbitrage](#a27) | §2.3 |
| [Covariate-dependent transitions](#a5) | §6.6 | [Complementary slackness](#a28) | §2.1 |
| [Sojourn times and the constant hazard](#a6) | §6.5 | [Dataset shift](#a29) | §9.1 |
| [Mixture distributions](#a7) | §1.1 | [Importance weighting and ESS](#a30) | §9.1 |
| [Heavy tails and stable laws](#a8) | §3.2 | [Partial pooling and shrinkage](#a31) | §6.10 |
| [Student-t as a scale mixture](#a9) | §6.3 | [Invariant prediction](#a32) | §9.6 |
| [Latent variables and HMMs](#a10) | §1.2 | [Gradient boosting](#a33) | §9.3 |
| [Filtering, smoothing and Viterbi](#a11) | §5.1 | [Neural-network components](#a34) | §3.7 |
| [Maximum likelihood and EM](#a12) | §5.2 | [Conditioning a network](#a35) | §10.8 |
| [Standard errors for latent models](#a13) | §6.1 | [Mixture of experts](#a36) | §6.6 |
| [Online EM and forgetting](#a14) | §6.8 | [Variational inference](#a37) | §5.10 |
| [Identification and label switching](#a15) | §5.1 | [Posterior collapse](#a38) | §5.10 |
| [Bayesian computation for HMMs](#a16) | §6.7 | [Purging, embargo, CPCV](#a39) | §5.11 |
| [Non-standard LR tests](#a17) | §1.1 | [Multiple testing](#a40) | §3.6 |
| [ARCH, GARCH, realised vol](#a18) | §1.2 | [Block bootstrap](#a41) | §11.4 |
| [Long memory](#a19) | §2.6 | [Forecast-comparison tests](#a42) | §6.9 |
| [Unit roots and breaks](#a20) | §2.6 | [Conformal prediction](#a43) | §10.8 |
| [Change points and run length](#a21) | §5.6 | [Real-time data vintages](#a44) | §1.5 |
| [Clustering and distances](#a22) | §1.5 | [Mean-variance sizing](#a45) | §6.10 |
| [Mahalanobis distance and PCA](#a23) | §3.6 | [Transaction-cost models](#a46) | §12.2 |

---

## A.1 Filtration and measurability {#a1}
**The idea.** Time-series modelling needs a formal way to state "the information a decision-maker has at time $t$". With it, you can check whether a quantity was computable at that time. A *filtration* does this. It is a family of information sets, one per time point, and the sets only grow.

**Formally.** A filtration $\{\mathcal{F}_t\}_{t \ge 0}$ is an increasing family
of $\sigma$-algebras, $\mathcal{F}_s \subseteq \mathcal{F}_t$ for $s \le t$, on
the underlying probability space. A random variable $X$ is
**$\mathcal{F}_t$-measurable** if the information in $\mathcal{F}_t$ determines its value.
Equivalently, $\{X \le x\} \in \mathcal{F}_t$ for every $x$.
A process $\{X_t\}$ is **adapted** if $X_t$ is $\mathcal{F}_t$-measurable for
every $t$, and **predictable** if $X_t$ is $\mathcal{F}_{t-1}$-measurable.

**Why it appears here.** The entire filtration ladder of §5.1 states which $\sigma$-algebra each state estimate is measurable with respect to.
$\xi_{t|t-1}$ is $\mathcal{F}_{t-1}$-measurable, so it is tradable at the
open of bar $t$. $\xi_{t|t}$ is only $\mathcal{F}_t$-measurable. $\xi_{t|T}$ depends on
information that will not exist for years. "Look-ahead
bias" is the informal name for using a quantity that is not measurable with
respect to the information set the decision rule claims to use.

**Deeper.** Williams, *Probability with Martingales* (CUP, 1991), chapters 3 and
9. A companion note, [Stochastic Processes](stochastic_processes.html), builds
the measure-theoretic theory from $\sigma$-algebras up.

## A.2 Conditional distributions and the predictive density {#a2}
**The idea.** A probabilistic forecast is a distribution, not a single number. At each step, a probabilistic time-series model produces the distribution of the next observation given everything known so far.

**Formally.** The **one-step predictive density** is
$p(y_t \mid \mathcal{F}_{t-1})$. It is the conditional density of $y_t$ given the
information available at $t-1$. A point forecast is a functional of this density. The
conditional mean $\mathbb{E}[y_t \mid \mathcal{F}_{t-1}]$ minimises expected
squared error. The conditional median minimises expected absolute error. So choosing a point forecast
means choosing a loss function. It is not a modelling step.

A **scoring rule** measures the quality of a density forecast. The
**log score** is $\ln p(y_t \mid \mathcal{F}_{t-1})$ evaluated at the outcome
that occurred. Averaged over an out-of-sample period, a higher log score is better. The log score is
**proper**: reporting the true predictive
density maximises it in expectation, so a forecaster cannot gain by shading the forecast. Maximum likelihood
maximises the in-sample average log score.

**Why it appears here.** §1.2 defines a regime model *as* a predictive density with a particular structure. §5.2 shows that the normalising constant of the Hamilton filter's update step is exactly this density. So maximising
the likelihood maximises one-step predictive performance and nothing else. §6.4, §6.9 and §6.11 compare models by their out-of-sample average log score.

**Deeper.** Gneiting & Katzfuss, "Probabilistic Forecasting," *Annual Review of
Statistics and Its Application* 1 (2014), 125–151.

## A.3 The probability integral transform and pseudo-residuals {#a3}
**The idea.** If a forecast distribution is right, the probability it
assigned to "an outcome no larger than what happened" behaves like a fair
random number between 0 and 1 each day. Checking this tests the
whole predictive density, not just its mean.

**Formally.** For a continuous predictive distribution function
$F_t(y) = \Pr(y_t \le y \mid \mathcal{F}_{t-1})$, the **probability integral
transform** is $\mathrm{PIT}_t = F_t(y_t)$. If $F_t$ is the true conditional
distribution, the $\mathrm{PIT}_t$ are independent and uniform on $[0,1]$
([Diebold, Gunther & Tay, 1998](https://www.nber.org/papers/t0215){target="_blank"}). Applying the inverse standard normal
distribution function gives **pseudo-residuals** $e_t = \Phi^{-1}(\mathrm{PIT}_t)$.
These are then independent standard normal. Normal quantile plots and
autocorrelation functions of $e_t$, $e_t^2$ and $|e_t|$ test the tails and the
dynamics separately. For an HMM, $F_t$ is the mixture
$\sum_k \xi_{t|t-1}^{(k)} F(\cdot \mid \theta_k)$.

**Why it appears here.** §6.9 uses pseudo-residuals as the main model check for
an HMM. It computes them from predicted probabilities and walk-forward parameters, so the
check is itself out of sample.

**Deeper.** [Zucchini, MacDonald & Langrock (2016)](https://doi.org/10.1201/b20790){target="_blank"}, chapter 6, in §4.2.

## A.4 Markov chains, transition matrices, and the second eigenvalue {#a4}
**The idea.** A Markov chain is the simplest model of a system that moves between
a finite set of states and remembers only its current state. The eigenvalues of its transition matrix govern its long-run
behaviour. The largest eigenvalue is always 1 and describes the equilibrium. The second largest sets how fast
the chain forgets its starting state.

**Formally.** A time-homogeneous Markov chain on $\{1, \dots, K\}$ has transition
matrix $\mathbf{P}$ with $p_{jk} = \Pr(s_{t+1} = k \mid s_t = j)$, rows summing
to one. A **stationary distribution** $\boldsymbol{\pi}$ satisfies
$\boldsymbol{\pi}^{\top}\mathbf{P} = \boldsymbol{\pi}^{\top}$. For an irreducible
aperiodic (**ergodic**) chain it is unique and
$\mathbf{P}^h \to \mathbf{1}\boldsymbol{\pi}^{\top}$. Ordering the eigenvalues
$1 = \lambda_1 > |\lambda_2| \ge \dots \ge |\lambda_K|$, the convergence is
geometric at rate $|\lambda_2|$. The quantity $1 - |\lambda_2|$ is called the **spectral gap**
or the chain's **mixing rate**. For $K = 2$,
$\lambda_2 = p_{11} + p_{22} - 1$.

A state $k$ is **absorbing** if $p_{kk} = 1$. The chain never leaves an absorbing state once it enters.
Within any realistic sample, a fitted $\hat p_{kk}$ very close to 1 behaves almost the same way.

**Why it appears here.** §1.3 uses $|\lambda_2|$ to set an upper limit on the
horizon at which a regime model can inform a decision. Beyond a few multiples of
$\ln 2 / (-\ln|\lambda_2|)$ bars, the state forecast has reverted to the
unconditional distribution and carries no information. §5.3 warns that near-absorbing fitted states mean the model has found a break, not a recurring regime.

**Deeper.** Levin & Peres, *Markov Chains and Mixing Times*, 2nd ed. (AMS, 2017),
chapter 12 for the eigenvalue connection.

## A.5 Covariate-dependent transitions and the multinomial logit {#a5}
**The idea.** A covariate-dependent transition matrix has rows that change over time with an observed variable. Each row
is still a probability distribution over the next state. The
probabilities are now a smooth function of the observed variable.

**Formally.** The **multinomial logit** maps $K$ real scores $\zeta_1, \dots,
\zeta_K$ to probabilities $\exp(\zeta_k)/\sum_l \exp(\zeta_l)$, which are positive
and sum to one. Adding the same constant to every score changes nothing, so one
score per row is fixed at zero for identification. A **time-varying transition
probability** model sets the scores of row $j$ to $z_{t-1}^{\top}\psi_{jk}$, with
$\psi_{jj} = 0$. Then $p_{jk,t} = \exp(z_{t-1}^{\top}\psi_{jk}) /
\sum_l \exp(z_{t-1}^{\top}\psi_{jl})$. For two states each row reduces to the
logistic function $1/(1 + e^{-u})$ of one linear score. The chain is no longer
homogeneous, so the stationary distribution and the second eigenvalue of §1.3
become functions of $z$.

**Why it appears here.** §6.6 builds covariate-driven transitions this way,
and §7.2 records the limit in which they become a mixture of experts.

**Deeper.** [Diebold, Lee & Weinbach (1994)](https://doi.org/10.1093/oso/9780198773917.003.0010){target="_blank"} and [Filardo (1994)](https://doi.org/10.1080/07350015.1994.10524545){target="_blank"}, both in §4.1.

## A.6 Sojourn times and the constant hazard {#a6}
**The idea.** A Markov chain's self-transition probability alone determines how long it stays in a state before leaving. The resulting distribution is memoryless.
However long the chain has already been in a
state, the chance of leaving in the next step is unchanged.

**Formally.** The **sojourn time** in state $k$ is
$D_k = \min\{d \ge 1 : s_{t+d} \ne k \mid s_t = \dots = s_{t+d-1} = k\}$. For
a Markov chain, $\Pr(D_k = d) = p_{kk}^{\,d-1}(1 - p_{kk})$. This is a geometric
distribution with mean $1/(1 - p_{kk})$ and modal value 1. Its **hazard rate**,
$\Pr(D_k = d \mid D_k \ge d) = 1 - p_{kk}$, is constant in $d$, so the distribution
is memoryless. A **hidden semi-Markov model** replaces the geometric with an
arbitrary duration distribution. This restores duration dependence and adds
substantial complexity. The usual choice is the shifted **negative
binomial**, $\Pr(D_k = d) = \binom{d + m - 2}{d - 1} q^{m}(1-q)^{d-1}$. It equals
the geometric at $m = 1$. Its hazard rises for $m > 1$ and falls
for $m < 1$. An ordinary HMM can approximate any duration distribution by making
each regime a block of sub-states visited in sequence. The
approximation is exact up to the block length.

In real time the current spell is **right-censored**. You know it has lasted at
least $d$ periods, but not how long it will last. The relevant quantity is then the
conditional distribution $\Pr(D_k = d + u \mid D_k > d)$ of the remaining
duration. Under the geometric it is the same for every $d$. Under a
semi-Markov model it is not.

**Why it appears here.** §6.5 identifies the constant hazard as the reason fitted
regime paths switch back and forth. §12.2 shows that this switching destroys a strategy
through turnover. §10.1 recommends time-since-transition as a feature because it restores the duration information that the Markov assumption discards.

**Deeper.** Yu, "Hidden Semi-Markov Models," *Artificial Intelligence* 174 (2010),
215–243.

## A.7 Mixture distributions and scale mixtures of normals {#a7}
**The idea.** A mixture describes data that come from several different
distributions when you do not observe which distribution produced each point. Mixing normals with different
variances is the standard way to build a symmetric, fat-tailed distribution
from thin-tailed components.

**Formally.** A finite mixture has density
$p(y) = \sum_{k=1}^{K} \pi_k f(y \mid \theta_k)$ with weights $\pi_k \ge 0$
summing to one. A **scale mixture of normals** is the special case
$f(y \mid \theta_k) = \mathcal{N}(y; \mu, \sigma_k^2)$ with a common mean.
The result is symmetric about $\mu$. It has excess kurtosis
$3\left(\mathbb{E}[\sigma^4]/(\mathbb{E}[\sigma^2])^2 - 1\right) > 0$ whenever
the $\sigma_k$ differ. Finite mixtures of Gaussians are dense in the space of
densities, so with enough components they approximate any density.

**Why it appears here.** §1.1 uses the universal-approximation property to argue
that "the data have regimes" is not, on its own, a testable claim. §7.2 notes that
a two-state model that differs only in variance produces an unconditional
distribution that is a scale mixture of normals. Unconditional moments alone cannot distinguish this distribution from a
fat-tailed i.i.d. law. That law is §2.6's null.

**Deeper.** Frühwirth-Schnatter, *Finite Mixture and Markov Switching Models*
(Springer, 2006), chapters 1–3.

## A.8 Heavy tails, stable distributions, and infinite variance {#a8}
**The idea.** Financial returns have far more extreme observations than a normal
distribution allows. The first explanation offered was a single law with genuinely heavier tails, not two regimes that take turns.
The most radical version of that claim gives up finite variance altogether.

**Formally.** A distribution has **heavy tails** if
$\Pr(|X| > x) \sim c x^{-\alpha}$ for some tail index $\alpha > 0$. Moments of
order $\ge \alpha$ do not exist. **Excess kurtosis**
$\mathbb{E}[(X-\mu)^4]/\sigma^4 - 3$ is the standard finite-sample summary and is
positive for **leptokurtic** (fat-tailed, peaked) distributions. The **stable**
(or Lévy-stable) family is closed under convolution: sums of
independent stable variables are stable. Its parameter is
$\alpha \in (0, 2]$. The value $\alpha = 2$ gives the Gaussian, and $\alpha < 2$ implies
$\mathbb{E}[X^2] = \infty$.

**Why it appears here.** In §3.2, Mandelbrot's stable-Paretian proposal was the
field's first answer to non-normality. It is a *single-regime* answer.
§2.6 and §7.2 record that the debate was never settled. A two-state scale
mixture ([mixtures](#a7)) and a fat-tailed i.i.d. law produce the same
unconditional moments, so unconditional evidence cannot separate them.

**Deeper.** Nolan, *Univariate Stable Distributions* (Springer, 2020), chapter 1;
Cont, "Empirical Properties of Asset Returns," *Quantitative Finance* 1(2)
(2001), 223–236, for what the stylised facts actually are.

## A.9 The Student-t distribution as a scale mixture of normals {#a9}
**The idea.** A Student-t variable is a normal variable whose variance was
itself drawn at random from a distribution that occasionally produces a large
value. This gives it heavy tails. It also means you can estimate the Student-t with the
same tools as a normal.

**Formally.** With location $\mu$, scale $\sigma$ and degrees of freedom
$\nu > 0$, the density is
$\frac{\Gamma((\nu+1)/2)}{\Gamma(\nu/2)\sqrt{\nu\pi}\,\sigma}\left(1 + \frac{(y-\mu)^2}{\nu\sigma^2}\right)^{-(\nu+1)/2}$.
Its tails decay as $|y|^{-(\nu+1)}$, so moments of order $\nu$ and above do not
exist. The variance is $\sigma^2\nu/(\nu - 2)$ for $\nu > 2$. Letting $\nu \to \infty$
recovers the normal. The **scale-mixture representation** is
$y = \mu + \sigma\varepsilon/\sqrt{\omega}$ with $\varepsilon \sim
\mathcal{N}(0,1)$ and $\omega \sim \mathrm{Gamma}(\nu/2, \nu/2)$ (shape and rate) independent.
Given $y$, the latent precision has conditional mean
$\mathbb{E}[\omega \mid y] = (\nu + 1)/(\nu + (y - \mu)^2/\sigma^2)$. This mean is
small for outlying $y$. Treating $\omega$ as missing data turns maximum
likelihood for $\mu$ and $\sigma$ into an EM algorithm of weighted least
squares. The EM algorithm downweights the outliers.

**Why it appears here.** §6.3 recommends Student-t emissions for daily returns.
The weights $\omega_{tk}$ there are this conditional mean, state by state.
§7.2 lists the representation among the exact equivalences.

**Deeper.** Lange, Little & Taylor, "Robust Statistical Modeling Using the t
Distribution," *Journal of the American Statistical Association* 84(408)
(1989), 881–896; [Bulla (2011)](https://doi.org/10.1080/14697681003685563){target="_blank"} in §4.3 for HMMs.

## A.10 Latent variables and hidden Markov models {#a10}
**The idea.** A latent-variable model explains observed data with an unobserved
quantity. Knowing that quantity would make the observations simple. A hidden
Markov model is the version in which the unobserved quantity is a Markov chain.

**Formally.** An HMM specifies a latent chain $s_t$ with transition matrix
$\mathbf{P}$ and **emission** (observation) densities
$f(y_t \mid s_t = k; \theta_k)$. It makes two conditional independence
assumptions. The state $s_t$ depends on the past only through $s_{t-1}$. The
observation $y_t$ depends on everything else only through $s_t$. The joint
density of a path is
$p(y_{1:T}, s_{1:T}) = \pi_{s_1} f(y_1 \mid \theta_{s_1}) \prod_{t=2}^{T}
p_{s_{t-1}s_t} f(y_t \mid \theta_{s_t})$. The observed-data likelihood sums this
density over all $K^T$ paths. That sum is why the recursion of §5.2 matters.

**Why it appears here.** Every latent-state model in §5 is an HMM or a
generalisation of one. Hamilton's Markov-switching regression is an HMM whose
emissions are regressions.

**Deeper.** [Rabiner (1989)](https://doi.org/10.1109/5.18626){target="_blank"} gives the clearest exposition. [Zucchini, MacDonald &
Langrock (2016)](https://doi.org/10.1201/b20790){target="_blank"} cover practice. [Cappé, Moulines & Rydén (2005)](https://doi.org/10.1007/0-387-28982-8){target="_blank"} cover theory. All are in
§4.2.

## A.11 Bayes filtering, smoothing, and Viterbi decoding {#a11}
**The idea.** A latent state supports three different questions, each with its
own answer. Filtering gives the state now, given the data so far. Smoothing
gives the state at a past date, given all the data. Decoding gives the single
sequence of states that best explains the whole record.

**Formally.** Given observations $y_{1:T}$:

- **Filtering** computes $\Pr(s_t \mid y_{1:t})$ by the forward recursion of
  §5.2. The recursion predicts through the chain, then reweights by the new
  observation's likelihood. The cost is $O(TK^2)$.
- **Smoothing** computes $\Pr(s_t \mid y_{1:T})$ by combining the forward pass
  with a backward pass (Kim's recursion, or the $\alpha$–$\beta$ form). The cost
  is the same, but it requires the whole sample.
- **Viterbi decoding** computes $\arg\max_{s_{1:T}} \Pr(s_{1:T} \mid y_{1:T})$,
  the single most probable *path*. It uses dynamic programming with $\max$ in
  place of $\sum$. The Viterbi path is not the sequence of per-time-point
  marginal modes, and the two can differ substantially.

The Kalman filter gives the same three algorithms for a linear-Gaussian
continuous state. The discrete and continuous cases are instances of one
recursion.

The **backward variable** $b_t^{(k)} \propto p(y_{t+1:T} \mid s_t = k)$ starts
from $b_T^{(k)} = 1$ and follows the recursion
$b_t^{(j)} \propto \sum_k p_{jk}\, f(y_{t+1} \mid \theta_k)\, b_{t+1}^{(k)}$. The
smoothed probability is proportional to $\xi_{t|t}^{(k)} b_t^{(k)}$. This is the
"$\alpha$–$\beta$" form, with $\alpha$ the unnormalised forward variable. The
**pairwise** posterior $\Pr(s_{t-1} = j, s_t = k \mid \mathcal{F}_T)$ multiplies
the filtered belief at $t-1$, the transition probability, the emission density
at $t$ and the backward variable at $t$. Viterbi decoding, the jump model's state
assignment and offline change-point segmentation are all **dynamic
programmes**. Each finds the best path. For every state at every date, it keeps
only the best way of arriving there.

**Why it appears here.** §5.1's ladder is the distinction between filtering and
smoothing plus one extra step of prediction. §7.2 shows the statistical jump
model is a Viterbi decode of a restricted HMM. §6.1 uses the backward variable and the pairwise posteriors in the E-step. §6.2 compares the four state beliefs, including the Viterbi path. §5.6 and §5.7 rely on the same dynamic-programming idea.

**Deeper.** Särkkä & Svensson, *Bayesian Filtering and Smoothing*, 2nd ed. (CUP,
2023). The book is free online and presents the discrete and continuous cases
under one framework.

## A.12 Maximum likelihood and the EM algorithm {#a12}
**The idea.** With latent variables, the likelihood is a sum over all
unobserved configurations. Maximising it directly is awkward. EM alternates two
steps. It estimates the distribution of the latent variables, then maximises as
if that estimate were data.

**Formally.** The **E-step** computes
$Q(\theta \mid \theta^{(i)}) = \mathbb{E}_{s_{1:T} \mid y, \theta^{(i)}}[\ln p(y, s_{1:T} \mid \theta)]$.
The **M-step** sets $\theta^{(i+1)} = \arg\max_\theta Q(\theta \mid \theta^{(i)})$.
Each iteration weakly increases the observed-data likelihood. So the sequence
converges to a *local* optimum or a saddle point. The limit need not be the
global optimum. For HMMs the E-step is forward-backward and the M-step is
weighted moment matching. The pair is called **Baum-Welch**.

The alternative to EM is **direct numerical maximisation** of the
log-likelihood. First map the constrained parameters to unconstrained ones. Map
each transition row through a multinomial logit and each scale through its
logarithm. Then a **quasi-Newton** optimiser can search freely. A quasi-Newton
optimiser builds an approximation to the curvature from successive gradients.

**Why it appears here.** §6.1 lists the practical failures: local optima
(restart many times), degeneracy as $\sigma_k \to 0$ (the likelihood is
unbounded, so constrain or regularise), and the small effective sample for
transition probabilities. §6.1 recommends EM to get close to the optimum and quasi-Newton steps to finish.

**Deeper.** Dempster, Laird & Rubin, "Maximum Likelihood from Incomplete Data via
the EM Algorithm," *JRSS-B* 39(1) (1977), 1–38.

## A.13 Standard errors for latent-variable models {#a13}
**The idea.** The sharpness of the likelihood peak around a maximum-likelihood
estimate measures how precise the estimate is. The sharper the peak, the more
precisely the data determine the parameter. Two methods measure the sharpness.
One uses the curvature at the peak. The other uses the spread of estimates
across simulated samples.

**Formally.** The **observed information** is the negative Hessian of the
log-likelihood at the estimate, $\mathcal{J}(\hat\theta) = -\nabla^2
\ell(\hat\theta)$, and $\mathcal{J}(\hat\theta)^{-1}$ approximates the
covariance of $\hat\theta$. For an HMM, compute the Hessian numerically from
the filter's log-likelihood, or from the EM quantities by Louis's identity. The
approximation relies on two conditions: the estimate is interior, and the
likelihood is locally quadratic. Both fail for a transition probability near 1.
Working with $\operatorname{logit}(p_{kk})$ helps. The **parametric bootstrap**
avoids the approximation. Simulate many samples from the fitted model, refit
each, and take the standard error from the spread of the refitted parameters.

The **delta method** gives standard errors for a function of the parameters,
such as the expected spell length $1/(1 - p_{kk})$. For a smooth $g$,
$\operatorname{se}(g(\hat\theta)) \approx |g'(\hat\theta)|\,\operatorname{se}(\hat\theta)$.
For a vector $\theta$, use the gradient in place of the derivative.

**Why it appears here.** §6.1 recommends the bootstrap for HMM standard errors
and shows that a turbulent state's expected spell length is uncertain by about
16% even when the state path is known.

**Deeper.** Louis, "Finding the Observed Information Matrix When Using the EM
Algorithm," *Journal of the Royal Statistical Society: Series B* 44(2) (1982),
226–233. [Zucchini, MacDonald & Langrock (2016)](https://doi.org/10.1201/b20790){target="_blank"}, chapter 3, in §4.2.

## A.14 Online EM and exponential forgetting {#a14}
**The idea.** Online updating avoids refitting a model on the full history
whenever data arrive. It updates a running summary of the data and re-derives
the parameters from that summary. Discounting old observations in the summary
lets the parameters change with the market.

**Formally.** For many models, the HMM included, EM's M-step depends on the data
only through expected **sufficient statistics**: weighted counts, sums and sums
of squares. **Online EM** updates these statistics recursively,
$\hat S_t = (1 - \gamma_t)\hat S_{t-1} + \gamma_t\,\tilde S_t$. Here $\tilde S_t$ is
the new observation's expected contribution and $\gamma_t$ is a step size. Online
EM then recomputes the parameters from $\hat S_t$. A step size that shrinks like
$1/t$ converges to the batch estimate. A constant step size $\gamma$ weights the
observation from $u$ periods ago by $\gamma(1-\gamma)^u$. This is **exponential
forgetting** with factor $\lambda = 1 - \gamma$ and an effective memory of about
$1/\gamma$ observations. It is the same weighting as an EWMA.

**Why it appears here.** §6.8 uses forgetting to let HMM parameters change over
time. It recommends a shorter memory for volatilities than for transition
probabilities.

**Deeper.** [Cappé (2011)](https://arxiv.org/abs/0908.2359){target="_blank"} is in §4.2. [Nystrup, Madsen & Lindström (2017)](https://orbit.dtu.dk/en/publications/long-memory-of-financial-time-series-and-hidden-markov-models-wit-2/){target="_blank"}, in §4.3,
gives the financial application.

## A.15 Identification, label switching, and likelihood degeneracy {#a15}
**The idea.** A mixture-like model can fail to have a well-defined answer in
three ways. The parameters may not be recoverable even in principle. The labels
attached to components may be arbitrary. The likelihood may be infinite at
degenerate parameter values.

**Formally.** A model is **identified** if distinct parameter values imply
distinct distributions. Finite mixtures are identified only **up to permutation
of the components**, because the likelihood is invariant under relabelling. This
is **label switching**. Resolving it requires an ordering constraint (for example
$\sigma_1 < \sigma_2 < \dots$). The choice of constraint is a modelling decision
with consequences. Separately, a Gaussian mixture's likelihood is
**unbounded**. Placing one component's mean on a data point and letting its
variance go to zero sends the likelihood to infinity. So the maximum-likelihood
estimator does not exist without a constraint or a prior.

**Why it appears here.** §5.1's label leakage, §6.1 and §11.2's leak 3. Sorting states by fitted mean,
or sorting on the full sample, is a look-ahead. §8.3 measures what happens when
equal volatilities leave the identification rule no basis to order the states.
The sort order is then arbitrary, and the strategy built on it turns a 0.50
Sharpe into zero.

**Deeper.** [Frühwirth-Schnatter (2006)](https://doi.org/10.1007/978-0-387-35768-3){target="_blank"}, chapter 3, is the standard treatment of
both problems.

## A.16 Bayesian computation for HMMs: conjugate priors, Gibbs sampling and FFBS {#a16}
**The idea.** Bayesian estimation replaces "the best parameters" with a
distribution over plausible parameters. For an HMM that distribution has no
closed form. Simulation explores it by alternating two draws, repeated many
times. One draw is the hidden state path given the parameters. The other is the
parameters given the path.

**Formally.** A prior is **conjugate** when the posterior is in the same family.
The **Dirichlet** distribution on a probability vector $(p_1, \dots, p_K)$ has
density proportional to $\prod_k p_k^{a_k - 1}$. It is conjugate to counts. After
observing $n_k$ outcomes of each type, the posterior is
$\mathrm{Dirichlet}(a_1 + n_1, \dots, a_K + n_K)$. So the $a_k$ act as prior
pseudo-counts. The normal and inverse-gamma distributions are conjugate for a
mean and a variance. **Gibbs sampling** draws each block of unknowns from its
distribution conditional on the current values of the others. Repeated draws
converge to the joint posterior. For an HMM the blocks are the state path,
the transition rows and the emission parameters. **Forward filtering, backward
sampling** draws the whole path at once. Run the filter, draw $s_T$ from
$\xi_{T|T}$, then draw each $s_t$ from
$\Pr(s_t = j \mid s_{t+1}, \mathcal{F}_t) \propto \xi_{t|t}^{(j)} p_{j s_{t+1}}$,
going backwards. Label switching (the previous entry) reappears as draws that
swap state labels between sweeps.

Two practical notes. The posterior **mode** of a Dirichlet is
$(a_k - 1 + n_k)/\sum_l (a_l - 1 + n_l)$, so in penalised EM each prior
parameter contributes $a_k - 1$ pseudo-counts, not $a_k$. And a ridge penalty
$\tfrac{\rho}{2}\lVert\psi\rVert^2$ on regression-type coefficients is the
log of a Gaussian prior with variance $1/\rho$. So penalised maximum likelihood
is a posterior mode. Check MCMC output for **mixing**. Draws are
autocorrelated, and samplers that update one state at a time mix far more slowly
than block samplers such as FFBS. The minimum check is to run several chains
from dispersed starts and compare them.

**Why it appears here.** §6.7 uses these methods for priors that encode
persistence and remove degeneracy. It recommends their posterior-mode shortcut,
penalised EM, as the default fitting routine. §6.6 recommends a ridge penalty on the transition coefficients, which is the same idea.

**Deeper.** [Chib (1996)](https://doi.org/10.1016/0304-4076(95)01770-4){target="_blank"} and [Scott (2002)](https://doi.org/10.1198/016214502753479464){target="_blank"} in §4.2.
[Frühwirth-Schnatter (2006)](https://doi.org/10.1007/978-0-387-35768-3){target="_blank"}, chapters 11–13.

## A.17 Likelihood-ratio tests when the null is non-standard {#a17}
**The idea.** The usual $\chi^2$ null distribution for a likelihood-ratio test
requires the models to be nested in a well-behaved way. Testing for an extra
regime violates this requirement in two ways at once. The standard critical
values are then meaningless.

**Formally.** Under the null of $K$ regimes, testing against $K+1$ fails the
regularity conditions in two ways. First, the parameters $\theta_{K+1}$ of the
extra component are **unidentified under the null**. Any value gives the same
likelihood, so the information matrix is singular (the *Davies problem*).
Second, the transition probabilities into the extra state lie **on the
boundary** of the parameter space. There the asymptotic normality of the MLE
fails. [Hansen (1992)](https://users.ssc.wisc.edu/~behansen/papers/jae_92.html){target="_blank"} obtains a
valid bound by treating the likelihood ratio as an empirical process indexed by
the nuisance parameters and taking a supremum. [Cho and White (2007)](https://doi.org/10.1111/j.1468-0262.2007.00809.x){target="_blank"} derive the
limiting distribution under weaker conditions.

The test brings in two further terms. **Information criteria** penalise fit by
parameter count and are the usual fallback for choosing $K$. They are
$\mathrm{AIC} = -2\ell + 2k$
and $\mathrm{BIC} = -2\ell + k\ln n$ for $k$ parameters. Both assume the same
regularity conditions that fail here, so they over-select. A **parametric
bootstrap** avoids the theory entirely. Simulate
many samples *from the fitted $K$-state model* and refit both $K$ and $K+1$ to
each. The simulations give the null distribution of the likelihood-ratio
statistic directly, in place of an asymptotic formula.

**Why it appears here.** §1.1 and §3.5 state the problem. §8.2 works it through. In practice, likelihood
improvement is not evidence, information criteria over-select, and the parametric
bootstrap is the only routinely correct route. §6.4 applies them to choosing the number of states.

**Deeper.** Davies, "Hypothesis Testing When a Nuisance Parameter Is Present Only
Under the Alternative," *Biometrika* 74(1) (1987), 33–43. Then [Hansen (1992)](https://users.ssc.wisc.edu/~behansen/papers/jae_92.html){target="_blank"}, in
§4.4.

## A.18 ARCH, GARCH, stochastic volatility, and realised volatility {#a18}
**The idea.** Several models say that volatility varies over time. They differ
in whether the variance is a deterministic function of the past, a latent random
process, or a quantity measured directly from high-frequency data.

**Formally.** With $r_t = \sigma_t \varepsilon_t$ and
$\varepsilon_t \sim (0, 1)$ i.i.d.:

- **ARCH($q$)**: $\sigma_t^2 = \omega + \sum_{i=1}^{q}\alpha_i r_{t-i}^2$. The
  variance is $\mathcal{F}_{t-1}$-measurable, so nothing latent remains to
  filter.
- **GARCH(1,1)**: $\sigma_t^2 = \omega + \alpha r_{t-1}^2 + \beta \sigma_{t-1}^2$.
  The sum $\alpha + \beta$ measures persistence. Values near 1 imply that shocks
  to variance decay very slowly ("IGARCH").
- **Stochastic volatility**: $\ln \sigma_t^2$ follows its own latent
  autoregression driven by a separate innovation. Here the model has a latent
  state to filter, and the state is continuous.
- **DCC** (dynamic conditional correlation; Engle, 2002) extends GARCH to many
  assets. It models each series' variance separately. It then lets the
  *correlation* matrix follow its own GARCH-like recursion. DCC is the
  multivariate member of this family, and §12.4's regime-switching DCC extends it.
- **Realised volatility**: $\mathrm{RV}_t = \sum_{i} r_{t,i}^2$ summed over
  intraday returns. It is a direct estimate rather than a model. The **HAR**
  (heterogeneous autoregressive) model regresses future RV on its daily, weekly,
  and monthly averages. These three horizons stand in for three classes of trader.
- **EWMA**: $\hat\sigma_t^2 = (1-\lambda)r_{t-1}^2 + \lambda\hat\sigma_{t-1}^2$.
  This is GARCH(1,1) with $\omega = 0$ and $\alpha + \beta = 1$. It has one
  parameter and needs no estimation. The rest of this list has to beat this
  baseline. Its **half-life** is $\ln 2 / (-\ln\lambda)$ bars.

**Why it appears here.** §1.2 names GARCH and stochastic volatility as the continuous alternatives to a regime model. §1.5 distinguishes them from regimes. §5.4 notes
Hamilton and Susmel's finding that apparent IGARCH persistence is partly
unmodelled regime switching. §8.7 argues that the continuous models usually win.

**Deeper.** Andersen, Bollerslev, Christoffersen & Diebold, "Volatility and
Correlation Forecasting," *Handbook of Economic Forecasting* vol. 1 (2006).

## A.19 Long memory and fractional integration {#a19}
**The idea.** A process has long memory when its autocorrelations decay so
slowly that they are not summable. The past keeps mattering far longer than an
ARMA model can express. Long memory matters here because a process with
occasional regime changes looks exactly like a long-memory process.

**Formally.** A stationary process has **long memory** if its autocorrelation
satisfies $\rho_k \sim c k^{2d-1}$ as $k \to \infty$ for some $d \in (0, 1/2)$,
so that $\sum_k |\rho_k| = \infty$. Equivalently, its spectral density diverges
at the origin. The canonical model is **ARFIMA($p,d,q$)**, which applies the
fractional differencing operator $(1-L)^d$ with non-integer $d$.

**Why it appears here.** §2.6 and §7.2 use this result. [Diebold and Inoue (2001)](https://www.nber.org/papers/t0264){target="_blank"} prove that
stochastic regime switching generates estimated long memory and vice versa, even
asymptotically. The two are near-observationally-equivalent, so a
likelihood improvement from adding regimes is not evidence that regimes exist.

**Deeper.** Beran, Feng, Ghosh & Kulik, *Long-Memory Processes* (Springer, 2013),
chapter 1. Also [Diebold & Inoue (2001)](https://www.nber.org/papers/t0264){target="_blank"}, in §4.4.

## A.20 Unit roots, non-stationarity, and the break/persistence confusion {#a20}
**The idea.** A series can fail to return to any fixed level for one of two
reasons. Shocks to it may be permanent, or its level may occasionally jump to a
new value. In finite samples the two look almost identical. This confusion is
the direct precursor of §2.6's regime-versus-long-memory problem.

**Formally.** The process $y_t = \rho y_{t-1} + \varepsilon_t$ has a **unit
root** when $\rho = 1$. Then shocks are permanent, the variance grows without
bound, and the process is **non-stationary** (it has no time-invariant
distribution). Tests such as augmented Dickey-Fuller test $H_0: \rho = 1$. A
**trend-stationary with breaks** alternative instead has $\rho < 1$ around a
deterministic level that shifts at a few dates. Perron (1989) showed that
ignoring a genuine break makes the unit-root null very hard to reject, and
conversely.

**Why it appears here.** §2.6 and §4.4 use this literature as the precedent for
the document's central identification worry. In the unit-root literature
(Perron), the long-memory literature ([long memory](#a19); Diebold and Inoue)
and the regime literature alike, occasional breaks look like persistence, and
persistence looks like breaks. The same confusion appears three times.

**Deeper.** Hamilton, *Time Series Analysis* (Princeton, 1994), chapters 15–17.

## A.21 Change points, run length, and segmentation {#a21}
**The idea.** Change-point analysis asks a different question from "which state
are we in". It asks whether the data-generating process has changed, and when.
Offline, you segment a completed record. Online, you maintain a belief about how
long it has been since the last change.

**Formally.** Offline **multiple change-point detection** partitions
$\{1,\dots,T\}$ into $m+1$ segments minimising
$\sum_{i} \mathcal{C}(y_{\tau_i+1:\tau_{i+1}}) + \beta m$, where $\mathcal{C}$ is
a segment cost (often twice the negative log-likelihood) and $\beta$ penalises
segments. Dynamic programming solves this exactly. **PELT** does so in $O(T)$
amortised time by pruning candidates that can never be optimal. Online,
**Bayesian online change-point detection** maintains a posterior over the **run
length** $\rho_t$, the number of periods since the last change. The posterior
follows the recursion
$p(\rho_t, y_{1:t}) = \sum_{\rho_{t-1}} p(\rho_t \mid \rho_{t-1})\,
p(y_t \mid \rho_{t-1}, y^{(\rho)})\, p(\rho_{t-1}, y_{1:t-1})$.
The method forecasts by mixing over run lengths.

**Why it appears here.** §5.6 argues that change-point methods answer the "has it
changed" question better than regime models do. §12.6 recommends running one
on your own strategy returns as the cleanest available test of whether the
strategy has stopped working.

**Deeper.** Truong, Oudre & Vayatis (2020) is the offline survey. [Adams &
MacKay (2007)](https://arxiv.org/abs/0710.3742){target="_blank"} covers BOCPD. Both are in §4.5.

## A.22 Clustering: k-means, density-based methods, and distances between distributions {#a22}
**The idea.** Clustering groups observations without labels, and it requires a
definition of "similar". When the objects are themselves distributions or
covariance matrices rather than points, the definition must be a distance
between distributions or matrices.

**Formally.** **$k$-means** minimises
$\sum_t \lVert u_t - c_{z_t}\rVert^2$ over assignments $z$ and centroids $c$.
It alternates between assigning each point to its nearest centroid and
recomputing centroids as means. It assumes roughly spherical, equal-sized clusters and
requires $k$ in advance. **Density-based** methods (DBSCAN, HDBSCAN) instead
define clusters as connected regions of high density, need no $k$, produce
arbitrary shapes, and label sparse points as noise. **Agglomerative** methods
merge the closest pair repeatedly, producing a dendrogram. For distributions, the
**Wasserstein** (optimal-transport, "earth mover's") distance
$W_p(P,Q) = \left(\inf_{\gamma \in \Gamma(P,Q)} \mathbb{E}_{(x,y)\sim\gamma}\lVert x-y\rVert^p\right)^{1/p}$
measures the minimum cost of transporting one distribution onto the other.
Unlike a KL divergence, it is finite and well-behaved for distributions with
different supports.

**Why it appears here.** §1.5 separates regimes (partitions of time) from cross-sectional clusters. §3.7 and §5.8 treat clustering as one route to regime
definition. The document's objection is that plain clustering has no
persistence term. §5.7's jump penalty adds exactly that term.

**Deeper.** Campello, Moulavi & Sander, "Density-Based Clustering Based on
Hierarchical Density Estimates," PAKDD (2013), covers HDBSCAN. Peyré & Cuturi,
["Computational Optimal Transport"](https://arxiv.org/abs/1803.00567),
arXiv:1803.00567, covers Wasserstein distances.

## A.23 Mahalanobis distance, PCA, and the absorption ratio {#a23}
**The idea.** Two measures summarise a cross-section of returns in one number.
One measures how unusual today's pattern is relative to its historical shape.
The other measures how concentrated the market's risk currently is in a few
common factors.

**Formally.** The **Mahalanobis distance** of an observation
$r \in \mathbb{R}^N$ from a distribution with mean $\mu$ and covariance $\Sigma$
is $d = (r - \mu)^{\top}\Sigma^{-1}(r - \mu)$. It is scale-invariant and
accounts for correlation, so it is large both when individual moves are extreme
and when the *relative pattern* of moves is unusual. Under multivariate
normality, $d \sim \chi^2_N$. **Principal component analysis** diagonalises
$\Sigma = V \Lambda V^{\top}$ with eigenvalues
$\lambda_1 \ge \dots \ge \lambda_N$. The **absorption ratio** is
$\sum_{i=1}^{n} \lambda_i / \sum_{i=1}^{N} \lambda_i$ for a chosen $n$. It is the
share of total variance explained by the leading components.

**Why it appears here.** §3.6 introduces the turbulence index by name. §5.9 presents both measures as scalar regime indices that need no
latent state and no $K$. It says that if such an index captures most of
the benefit, the latent-state model is a research project rather than an edge.
§8.7 lists a turbulence index among the continuous alternatives to fit first.
$\Sigma^{-1}$ is unstable when $N$ approaches the estimation window
length, so shrink it.

**Deeper.** Kritzman & Li (2010) and Kritzman, Li, Page & Rigobon (2011), both in
§4.6. For the shrinkage, see Ledoit & Wolf, "Honey, I Shrunk the Sample Covariance Matrix," *Journal of
Portfolio Management* 30(4) (2004), 110–119.

## A.24 Bayesian nonparametrics: Dirichlet processes and the sticky HDP-HMM {#a24}
**The idea.** Instead of fixing the number of clusters or states in advance, put
a prior over models with *any* number of them. The posterior then decides the
number, which can grow as data accumulate.

**Formally.** A **Dirichlet process** $\mathrm{DP}(\alpha, H)$ is a distribution
over distributions. Its draws are discrete with probability one. The
stick-breaking
construction generates weights $\beta_k = \beta'_k\prod_{j<k}(1-\beta'_j)$ with
$\beta'_k \sim \mathrm{Beta}(1,\alpha)$. Using a DP as the prior on mixture
weights gives an infinite mixture. Its effective number of occupied components
grows like $\alpha \ln n$. A **hierarchical** DP shares one set of atoms across
several DPs. This lets every row of an HMM's transition matrix draw from the
same countable state set, which gives the **HDP-HMM**. The **sticky** variant
adds $\kappa$ to the self-transition weight. This encodes a prior belief in
persistence and prevents the rapid state-switching that plain HDP-HMMs tend to
produce.

**Why it appears here.** §6.4 offers this as the principled answer to "how many
regimes". §4.2 recommends [Fox et al. (2011)](https://arxiv.org/abs/0905.2592){target="_blank"}. The document's reservation is
practical rather than theoretical. The method returns more states than a trading
decision can use.

**Deeper.** Teh & Jordan, "Hierarchical Bayesian Nonparametric Models with
Applications," in *Bayesian Nonparametrics* (CUP, 2010). [Fox et al. (2011)](https://arxiv.org/abs/0905.2592){target="_blank"}, in
§4.2.

## A.25 The Sharpe ratio, the information coefficient, and their standard errors {#a25}
**The idea.** This entry covers the standard performance measures and, more
importantly here, how imprecise their estimates are. Almost every disagreement
about whether a regime strategy works is a disagreement about sampling error.

**Formally.** The **Sharpe ratio** is
$S = \mathbb{E}[r - r_f]/\operatorname{sd}(r)$, conventionally annualised by
multiplying a per-bar estimate by $\sqrt{A}$. For i.i.d. normal returns over $y$
years its estimator has approximate standard error

$$\operatorname{se}(\hat S) \approx \sqrt{\frac{1 + S^2/2}{y}},$$

The standard error depends on the **calendar span**, not the sampling frequency.
This is the same asymmetry as §8.1. Serial correlation and non-normality inflate
it further. The
**information coefficient** is the cross-sectional correlation between forecast
and realised return. The **fundamental law of active management** relates it to
the achievable information ratio as $\mathrm{IR} \approx \mathrm{IC}\sqrt{N}$ for
$N$ independent bets.

**Why it appears here.** §5.1 and §6.11 quote Sharpe ratios and their error first. §11.5 shows that four years of turbulent time gives
$\operatorname{se}(\hat S) \approx 0.53$, so within-regime performance claims are
mostly noise. §8.3 and §8.4 report Sharpe ratios throughout. §6.11 quotes the standard error of a Sharpe ratio over 81 years of data.

**Deeper.** Lo, "The Statistics of Sharpe Ratios," *Financial Analysts Journal*
58(4) (2002), 36–52. It includes the correction for serial correlation.

## A.26 Risk premia, priced factors, and discount-rate variation {#a26}
**The idea.** This entry defines the asset-pricing terms that the
economic-mechanism sections assume. An asset's expected return above the
risk-free rate compensates for bearing some risk. A variable is "priced" when
exposure to it earns compensation. Prices move either because expected cash
flows changed or because the rate that discounts them changed.

**Formally.** With stochastic discount factor $M_{t+1}$, no-arbitrage implies
$\mathbb{E}_t[M_{t+1}R_{t+1}] = 1$ for every gross return. For excess returns,
this rearranges to
$\mathbb{E}_t[R^e_{t+1}] = -\operatorname{Cov}_t(M_{t+1}, R^e_{t+1})/\mathbb{E}_t[M_{t+1}]$.
So **risk premia are compensation for covariance with bad
times**. A **factor** $f$ is **priced** if $M$ loads on it, so that assets with
higher exposure $\beta_f$ earn higher average returns. Campbell's return
decomposition splits unexpected returns into news about future cash flows and
news about future discount rates. The empirical finding is that most price
variation is **discount-rate variation**. So expected returns move a great deal
over time. That variation is what makes conditional and regime-based models worth
considering at all. A **no-arbitrage objective** in a machine-learning model (§5.10) means
training the model so that its implied $M$ prices the assets, rather than fitting
returns directly.

**Why it appears here.** §2.1 (intermediary net worth as a priced state
variable), §2.5 (Fama-French and Cochrane on cyclical expected returns), and
§5.10 (Chen, Pelger and Zhu's end-to-end objective).

**Deeper.** Cochrane, *Asset Pricing*, rev. ed. (Princeton, 2005), chapters 1
and 20. Cochrane, "Presidential Address: Discount Rates," *Journal of Finance*
66(4) (2011), 1047–1108.

## A.27 Limits to arbitrage and multiple equilibria {#a27}
**The idea.** Textbook arbitrage assumes that traders with unlimited capital and
unlimited patience correct mispricings. Real arbitrageurs manage other people's
money and face margin calls. They can be forced to liquidate exactly when the
opportunity is best. This can make mispricings self-reinforcing rather than
self-correcting.

**Formally.** Shleifer and Vishny (1997) model an arbitrageur whose capital
depends on past performance. An adverse price move causes withdrawals. The
withdrawals force liquidation, which moves the price further in the same adverse
direction. This feedback loop amplifies the price impact of a shock instead of
damping it. When the feedback is strong enough, the system admits **multiple
equilibria**. These are two or more self-consistent price levels for the same
fundamentals. Beliefs or history determine which one obtains, rather than
fundamentals. Formally, multiple equilibria arise when the excess-demand
function crosses zero more than once. This requires the positive feedback to
dominate locally.

**Why it appears here.** §2.3. Multiple equilibria are the cleanest theoretical
route to genuine *discreteness* other than binding constraints
([complementary slackness](#a28)), because distinct equilibria are distinct by
construction. The document tags the family **[Hypothesis]** because no one has
convincingly distinguished "the system jumped between equilibria" from "a large
shock hit a continuous system" using return data alone.

**Deeper.** Shleifer & Vishny, "The Limits of Arbitrage," *Journal of Finance*
52(1) (1997), 35–55. Gromb & Vayanos, "Limits of Arbitrage," *Annual Review of
Financial Economics* 2 (2010), 251–275.

## A.28 Complementary slackness and occasionally binding constraints {#a28}
**The idea.** At the optimum of a problem with an inequality constraint, exactly
one of two things holds. Either the constraint is slack and its shadow price is
zero, or it binds and its shadow price is positive. This "exactly one of two"
structure is a genuine discreteness. Optimisation produces it, and no assumption
imposes it.

**Formally.** For $\min f(x)$ subject to $g(x) \le 0$, the Karush-Kuhn-Tucker
conditions include **complementary slackness**: $\lambda \, g(x^\star) = 0$ with
$\lambda \ge 0$. So either $g(x^\star) < 0$ and $\lambda = 0$, or $g(x^\star) = 0$
and $\lambda \ge 0$. The multiplier $\lambda$ is the shadow price of the
constraint. It jumps from zero to positive as the constraint starts to bind. The
solution's local behaviour changes qualitatively at that point.

**Why it appears here.** §2.1 argues that this is the only mechanism family that
predicts genuine discreteness in markets rather than continuous variation.
Intermediaries' leverage limits, margin requirements, and VaR budgets are
inequality constraints. So "constrained" and "unconstrained" really are two
states.

**Deeper.** Boyd & Vandenberghe, *Convex Optimization* (CUP, 2004), section 5.5. Then
Brunnermeier & Pedersen (2009) for the financial mechanism.

## A.29 Dataset shift: covariate shift, concept drift, prior shift {#a29}
**The idea.** "The distribution changed" is too coarse to act on. Several
distinct things can change. They have different consequences and call for
different remedies.

**Formally.** Write training and deployment joints as $p_{\text{tr}}(x, y)$ and
$p_{\text{te}}(x, y)$, and factor $p(x, y) = p(x)\,p(y \mid x)$. Then:

- **Covariate shift**: $p_{\text{tr}}(x) \ne p_{\text{te}}(x)$ but
  $p(y \mid x)$ unchanged.
- **Concept drift** (*real* drift): $p(y \mid x)$ changes. Only this shift
  changes the function you are trying to learn.
- **Prior / label shift**: $p(y)$ changes with $p(x \mid y)$ fixed. This is the
  reverse factorisation, and the natural model for classification when class
  frequencies move.
- **Conditional-scale drift**: §9.1 coins this term, which is not standard
  terminology, for the
  case where $\mathbb{E}[y \mid x]$ is fixed but $\operatorname{Var}(y \mid x)$
  changes. Formally it is a kind of concept drift under a distributional loss.
  It leaves the conditional *mean* function untouched, and its remedy is
  entirely different. So the document separates it.

**Why it appears here.** §9.1 and §9.2 use this taxonomy as the decision rule for
choosing an integration scheme. §9.3 explains that a regime feature
addresses only concept drift, which is why it so often does nothing.

**Deeper.** Quiñonero-Candela et al. (2009) and [Gama et al. (2014)](https://mpechen.win.tue.nl/publications/pubs/Gama_ACMCS_AdaptationCD_accepted.pdf){target="_blank"}, both in §4.7.

## A.30 Importance weighting and effective sample size {#a30}
**The idea.** If the training distribution differs from the target distribution,
you can reweight training points to match the target. Reweighting is unbiased
but expensive. It concentrates the fit on fewer effective observations.

**Formally.** Under covariate shift with $p(y \mid x)$ unchanged, weighting each
training point by $w(x) = p_{\text{te}}(x)/p_{\text{tr}}(x)$ makes the weighted
training risk an unbiased estimate of the test risk (Shimodaira, 2000). The
variance of a weighted estimator grows with the dispersion of the weights. The
standard summary of that dispersion is the **effective sample size**

$$n_{\text{eff}} = \frac{\left(\sum_i w_i\right)^2}{\sum_i w_i^2} \le n ,$$

with equality only for uniform weights. If the model is **correctly
specified**, the unweighted MLE is already consistent under covariate shift.
Weighting then adds variance and brings no benefit. Weighting helps only under
misspecification or in finite samples.

**Why it appears here.** §9.1's counterintuitive row, and §10.3. In §10.3,
$n_{\text{eff}}$ is the number to quote in place of $T$ after any
weighting scheme. An exponential-decay half-life of 5 years on 20 years of daily
data leaves roughly 3,200 effective observations out of 5,040.

**Deeper.** Shimodaira (2000) in §4.7. Sugiyama, Krauledat & Müller, "Covariate
Shift Adaptation by Importance Weighted Cross Validation," *JMLR* 8 (2007),
985–1005.

## A.31 Partial pooling, shrinkage, and hierarchical models {#a31}
**The idea.** With several related groups, you can estimate each separately
(noisy), pool them all together (biased), or choose a compromise between the two.
How much the groups genuinely differ, relative to how noisily you measure each
one, determines the optimal compromise.

**Formally.** In the canonical normal hierarchical model, group $k$ has true
parameter $\beta_k = \beta + \delta_k$ with $\delta_k \sim (0, \tau^2)$, and the
per-group estimate $\hat\beta_k$ has sampling variance $v_k$. The posterior mean
(also the minimum-MSE linear combination) is

$$\hat\beta_k^{\text{opt}} = w_k \hat\beta_k + (1 - w_k)\hat\beta_{\text{pooled}},
\qquad w_k = \frac{\tau^2}{\tau^2 + v_k},$$

Then $w_k \to 1$ (no pooling) when between-group variation dominates, and
$w_k \to 0$ (complete pooling) when estimation noise dominates. This is the
James-Stein phenomenon in its interpretable form. Shrinkage toward a common mean
strictly improves total MSE when groups are numerous and individually noisy.

**Why it appears here.** §6.10 first applies a pooling rule (equal state means,
switching covariances). §9.5 turns the identification asymmetry into this
decision rule: pool the mean model across regimes ($\tau^2$ small against $v$),
and subset the risk model ($\tau^2 \gg v$). §10.4 gives methods (linear,
boosting, network) that implement partial pooling in practice.

**Deeper.** Gelman & Hill, *Data Analysis Using Regression and
Multilevel/Hierarchical Models* (CUP, 2007), chapter 12.

## A.32 Invariant prediction and invariant risk minimization {#a32}
**The idea.** Instead of adapting a model to each environment, look for the
relationship that is the *same* in every environment. Under assumptions, the
predictors that remain are causal (though not necessarily all of the causal
ones). A model built on them generalises to environments you have never seen.

**Formally.** Given data from environments $e \in \mathcal{E}$, **invariant
causal prediction** seeks the subsets $\mathcal{S}$ of predictors for which
$Y^e \mid X^e_{\mathcal{S}} = x$ has the same distribution for all $e$. [Peters,
Bühlmann and Meinshausen (2016)](https://web.math.ku.dk/~peters/jonas_files/InvariantCausalPrediction.pdf){target="_blank"} test this hypothesis for each candidate subset
and take the intersection of the accepted ones. This gives conservative
confidence sets for the causal predictors. **Invariant risk minimization** is the
gradient-based relaxation. It finds a representation $\Phi$ such that a single
classifier $w$ is simultaneously optimal when applied to $\Phi$ in every
environment. It enforces this by penalising $\sum_e \lVert \nabla_{w \mid w=1} R^e(w \cdot \Phi)\rVert^2$.

**Why it appears here.** §9.6 and §10.6 argue that this is the best-value
underused idea available. It uses regimes as *environments* to filter features
for robustness, not as conditions to adapt to. That use matches what a
forty-episode sample can support far better.

**Deeper.** [Peters, Bühlmann & Meinshausen (2016)](https://web.math.ku.dk/~peters/jonas_files/InvariantCausalPrediction.pdf){target="_blank"} and [Arjovsky et al. (2019)](https://arxiv.org/abs/1907.02893){target="_blank"},
both in §4.7. Rosenfeld, Ravikumar & Risteski (2021) cover IRM's failure
modes.

## A.33 Gradient boosting: what the model class can and cannot represent {#a33}
**The idea.** A boosted tree ensemble builds a prediction as a sum of small
decision trees, each fitted to the errors of the ones before it. Two structural
properties of that class drive everything in §10.8. Trees split on thresholds, so
they are invariant to monotone rescaling of features. Trees are piecewise
constant, so they cannot extrapolate.

**Formally.** Gradient boosting (Friedman, 2001) fits
$F_M(x) = F_0(x) + \nu\sum_{m=1}^{M} h_m(x)$, where each $h_m$ is a
regression tree fitted to the negative gradient of the loss at the current
prediction and $\nu$ is the learning rate. A tree of depth $d$ represents
interactions of order at most $d$. Because every split is a threshold test
$\mathbb{1}[x_j > c]$, the model is invariant to any strictly monotone
transformation of $x_j$. So an indicator $\mathbb{1}[x_j > c_0]$ that you
supply is exactly representable from $x_j$ alone and adds no function to the
class. Because leaves hold constants, the prediction for $x_j$ outside the
training range equals the boundary leaf's value at any distance beyond that range.

**Why it appears here.** §9.3 uses the tree's freedom to place its own threshold to explain why a regime dummy has little importance. §10.8 makes the redundancy of a threshold-derived
regime feature precise. It identifies the inability to extrapolate as the
most serious regime-related weakness of GBTs and prescribes trailing
normalisation or ranking as the fix. §10.4's `init_score` method uses the fact
that boosting starts from an arbitrary offset $F_0$.

**Deeper.** Friedman, "Greedy Function Approximation: A Gradient Boosting
Machine," *Annals of Statistics* 29(5) (2001), 1189–1232. [Grinsztajn et al.
(2022)](https://arxiv.org/abs/2207.08815){target="_blank"}, in §4.7, explains why trees keep performing best on tabular data.

## A.34 Neural-network components: recurrence, switching dynamics, and ensembles {#a34}
**The idea.** This entry covers the deep-learning components that §5.10 and
§10.7 name in passing. None is specific to finance.

**Formally.**

- **Recurrent networks and the LSTM.** A recurrent network carries a hidden state
  $h_t = \phi(h_{t-1}, u_t)$ along the sequence. So $h_t$ is a learned summary of
  the history, which acts as a continuous, learned regime variable. The **long
  short-term memory** cell adds gated paths and an additive cell state. Gradients
  then flow across long lags instead of vanishing.
- **Recurrent switching linear dynamical systems (rSLDS).** This is an HMM
  ([latent variables and HMMs](#a10)) whose discrete state indexes a *linear
  dynamical system* over a continuous latent state. Its discrete
  transitions depend on that continuous state: $\Pr(s_t \mid s_{t-1}, h_{t-1})$.
  Hamilton's model is the special case with no continuous state and
  state-independent transitions. The TVTP model of §6.6 is the case where the
  continuous driver is observed.
- **Deep ensembles and MC dropout.** Deep ensembles train several networks from
  different random initialisations and take the spread of their predictions as an
  uncertainty estimate. MC dropout keeps dropout active at inference and takes
  the spread over stochastic forward passes. Both widen in regions the training
  data did not cover.
- **Adversarial heads and meta-learning**, in one line each. A gradient-reversal
  layer trains a shared representation to make an auxiliary regime classifier
  *fail*, so the representation carries no regime information. Model-agnostic
  meta-learning trains parameters so that a few gradient steps on new data
  perform well, at the cost of a nested optimisation.

**Why it appears here.** §3.7 and §5.10 and §10.7 (learned and switching latent states,
adversarial invariance, meta-learning) and §10.8 (cheap uncertainty for sizing).
The chapter's verdict on all of them is the same. The methods are correct, but
the available sample size rarely supports them. Ensembling is a partial
exception because it is nearly free.

**Deeper.** Hochreiter & Schmidhuber, "Long Short-Term Memory," *Neural
Computation* 9(8) (1997), 1735–1780. [Linderman et al. (2017)](https://proceedings.mlr.press/v54/linderman17a.html){target="_blank"}, in §4.7.
Lakshminarayanan, Pritzel & Blundell, ["Simple and Scalable Predictive
Uncertainty Estimation Using Deep Ensembles"](https://arxiv.org/abs/1612.01474),
NeurIPS 2017.

## A.35 Conditioning a neural network: FiLM, and batch versus layer norm {#a35}
**The idea.** A network can use a side variable in a weak way or a strong way.
The weak way appends the variable to the input. The strong way lets the variable
*modulate* the network's internal activations multiplicatively.

**Formally.** **Feature-wise linear modulation** (FiLM) computes, from
conditioning information $c$, a per-channel scale and shift and applies them to a
hidden layer:
$a^{(\ell)} \leftarrow \gamma^{(\ell)}(c) \odot a^{(\ell)} + \beta^{(\ell)}(c)$, where
$a^{(\ell)}$ is the activation vector of layer $\ell$.
Because the scale is multiplicative, a single conditioning value can switch whole
pathways on or off. A concatenated input can achieve this only through learned
interactions. **Batch normalisation** standardises activations using statistics
computed across the mini-batch during training and a running average at
inference. **Layer normalisation** standardises across the features of a single
example. So it uses no cross-sample statistics and is unaffected by a shift in
the input distribution at inference.

**Why it appears here.** §10.8 argues that FiLM is the right injection point for
a regime posterior. Batch norm's running statistics are calibrated to the
training regime. This makes batch norm an easily overlooked source of
distribution-shift failure.

**Deeper.** [Perez et al. (2018)](https://ojs.aaai.org/index.php/AAAI/article/view/11671){target="_blank"}, in §4.7. Dumoulin et al., ["Feature-wise
Transformations"](https://distill.pub/2018/feature-wise-transformations/),
*Distill* (2018), for the unifying view.

## A.36 Mixture of experts and gating {#a36}
**The idea.** Instead of one model that must handle every situation, a mixture of
experts trains several specialists and a router. The router decides how much to
trust each specialist. When the router's input is a regime posterior, this is
regime switching expressed in machine-learning terms.

**Formally.** A mixture of experts predicts
$\hat y(x) = \sum_{k=1}^{K} g_k(z)\, f_k(x)$. The gate outputs $g_k(z) \ge 0$
sum to one and are typically a softmax of a learned function of gating inputs $z$.
When trained jointly, the gradient of the loss with respect to expert $k$ is
scaled by $g_k$. So experts specialise on the regions the gate assigns them.
**Sparse gating** keeps only the top few $g_k$ nonzero for efficiency. It then
needs an auxiliary load-balancing loss to prevent **expert collapse**, where the
gate routes everything to one expert.

**Why it appears here.** §10.5. Soft gating dominates hard selection. The
prediction path stays continuous through a
transition, so turnover is bounded exactly where confidence is lowest. §7.2
records that a smooth-transition model is exactly (for the conditional mean) a
two-expert MoE with a logistic gate on one observable. It also records that a covariate-driven HMM whose
transitions ignore the current state is an MoE too (§6.6).

**Deeper.** Jacobs, Jordan, Nowlan & Hinton (1991) and [Shazeer et al. (2017)](https://arxiv.org/abs/1701.06538){target="_blank"},
both in §4.7.

## A.37 Variational inference and the evidence lower bound {#a37}
**The idea.** Exact Bayesian inference over a latent variable requires an
integral that is usually intractable. Variational inference replaces the integral
with an optimisation. It picks a tractable family of approximate posteriors and
finds the member closest to the true posterior.

**Formally.** For latent $z$ and data $y$, the marginal likelihood
$\ln p(y) = \ln \int p(y \mid z)p(z)\,dz$ is intractable. Introducing any
distribution $q(z)$ gives the decomposition

$$\ln p(y) = \underbrace{\mathbb{E}_{q}[\ln p(y \mid z)] - \mathrm{KL}\!\left(q(z) \,\|\, p(z)\right)}_{\text{ELBO } \mathcal{L}(q)} \;+\; \mathrm{KL}\!\left(q(z) \,\|\, p(z \mid y)\right),$$

Since the final KL is non-negative, $\mathcal{L}(q)$ is an **evidence lower
bound**. Maximising it over $q$ tightens the bound and moves $q$
toward the true posterior at the same time. **Amortised** inference replaces a
per-datapoint
optimisation with a neural network $q_\phi(z \mid y)$ that outputs the approximate
posterior directly. This network is the "encoder" of a variational autoencoder.

**Why it appears here.** §5.10's deep state-space models are trained this way.
§5.10 warns that variational approximation error adds one more source of
uncertainty on top of every identification problem in §8. It is also the
setting in which [posterior collapse](#a38) occurs.

**Deeper.** Blei, Kucukelbir & McAuliffe, ["Variational Inference: A Review for
Statisticians"](https://arxiv.org/abs/1601.00670), *JASA* 112(518) (2017),
859–877.

## A.38 Posterior collapse {#a38}
**The idea.** A latent-variable model trained by variational inference can learn
to ignore its own latent variable entirely. It then becomes a plain conditional
model with an unused component. The training loss does not reveal this.

**Formally.** Take the ELBO of [variational inference](#a37),
$\mathbb{E}_{q(z \mid y)}[\ln p(y \mid z)] - \mathrm{KL}(q(z \mid y)\,\|\,p(z))$.
Suppose the decoder $p(y \mid z)$ is expressive enough to model $y$ without $z$,
as a powerful autoregressive decoder is. Then the optimiser can drive the KL
term to zero by setting $q(z \mid y) = p(z)$. At that point the latent carries no
information about the data, and the encoder ignores its input.
The loss does not signal this. The ELBO looks healthy throughout, because the
decoder alone explains the data.

**Why it appears here.** §5.10 lists it as the first failure mode of learned
latent-state models. §10.7 gives the diagnostic: ablate the latent and confirm that
performance actually degrades. In the financial setting the second diagnostic
matters just as much. Regress the learned state on realised volatility and check
whether it contains anything beyond a noisy volatility proxy.

**Deeper.** Bowman et al., ["Generating Sentences from a Continuous
Space"](https://arxiv.org/abs/1511.06349), CoNLL 2016. The paper first
characterised the phenomenon.

## A.39 Purging, embargo, and combinatorial purged cross-validation {#a39}
**The idea.** Financial ML targets are realised over a window, so nearby training
and test examples share outcome data. Standard cross-validation then measures how
well the model memorises overlapping labels. Purging and embargoing remove the
contaminated observations.

**Formally.** Let example $i$ have feature time $t_i$ and label window
$[t_i, t_i + h_i]$. **Purging** removes from the training set every $i$ whose
label window overlaps any test example's label window. **Embargo** additionally
removes training examples in a short interval immediately following the test
block, to break the serial correlation that survives purging via features rather
than labels. **Combinatorial purged cross-validation** forms many train/test
splits by choosing $k$ of $N$ contiguous groups as test blocks and applying
purging and embargo throughout. It thereby yields a *distribution* of backtest
paths rather than a single one.

**Why it appears here.** In §11.3, the third failure of $k$-fold is persistent
regimes appearing on both sides of every fold boundary. Purging does *not* fix
this failure. It requires walk-forward or leave-one-episode-out instead. §5.11 raises the overlapping-label problem first, for supervised regime labels.

**Deeper.** López de Prado (2018), chapters 7 and 12, in §4.8.

## A.40 Multiple testing, selection bias, and the deflated Sharpe ratio {#a40}
**The idea.** If you try many strategies and report the best, the best one looks
good partly because it is the best of many, not because it is good. Correcting
for that requires knowing how many things you tried.

**Formally.** The expected maximum of $n$ independent standard normal draws grows
roughly like $\sqrt{2\ln n}$. The value is about 1.87 for $n = 20$ and 2.51 for
$n = 100$. So if each trial's Sharpe estimate has standard error
$\operatorname{se}$, the *expected* best-of-$n$ estimate under a true Sharpe of
zero is about $1.87\operatorname{se}$ at $n = 20$. The **deflated Sharpe ratio**
computes the probability that an observed Sharpe exceeds what selection alone
would produce. It adjusts for the number of trials, the variance across trials,
the sample length, and the skewness and kurtosis of returns.

**Why it appears here.** §3.6 and §5.5 flag unadjusted specification search. §11.6 corrects for it. Regime work multiplies trials fast: $K$ regimes
times $M$ specifications times $W$ windows. §11.5's standard error of 0.53
for a four-year crisis sample means that twenty honest trials produce an expected best
crisis Sharpe near 1.0 from pure noise.

**Deeper.** [Bailey & López de Prado (2014)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf){target="_blank"} and Harvey, Liu & Zhu (2016), both in
§4.8.

## A.41 The block and stationary bootstrap {#a41}
**The idea.** Resampling observations independently destroys serial dependence.
A time-series null needs to preserve exactly that structure. Block methods
resample contiguous stretches instead.

**Formally.** The **moving block bootstrap** resamples blocks of fixed length
$\ell$ with replacement and concatenates them. The **stationary bootstrap**
(Politis & Romano, 1994) uses geometrically distributed block lengths with mean
$1/q$. This makes the resampled series stationary. Consistency requires
$\ell \to \infty$ with $\ell/T \to 0$. In practice $\ell$ must exceed the
dependence horizon you wish to preserve.

**Why it appears here.** §11.4's shuffled-regime control resamples the state path in blocks. §11.6 warns that if your block length is shorter than
the regime half-life, the bootstrap null contains no regimes, and any regime
strategy will look significant against it. The block length defines the
hypothesis being tested. It is not a nuisance parameter here.

**Deeper.** Politis & Romano, "The Stationary Bootstrap," *JASA* 89(428) (1994),
1303–1313; Lahiri, *Resampling Methods for Dependent Data* (Springer, 2003).

## A.42 Forecast-comparison tests under instability {#a42}
**The idea.** Comparing two forecasting models means comparing two sequences of
losses. The standard test asks whether one model is better *on average*. The
tests that matter here ask whether one model is better *right now*, and whether
the answer changes over time.

**Formally.** Let $d_t = L(y_t, \hat y_t^A) - L(y_t, \hat y_t^B)$ be the loss
differential.

- **Diebold-Mariano** tests $H_0: \mathbb{E}[d_t] = 0$ using
  $\bar d / \sqrt{\widehat{\operatorname{avar}}(\bar d)/T}$ with a HAC variance
  estimate.
- **Giacomini-White conditional predictive ability** tests
  $H_0: \mathbb{E}[d_{t+1} \mid \mathcal{F}_t] = 0$, which asks whether the models
  are equally good *given the current state*. The test checks whether $d_{t+1}$ is
  orthogonal to a chosen set of $\mathcal{F}_t$-measurable instruments.
- **The Giacomini-Rossi fluctuation test** computes a rolling Diebold-Mariano
  statistic over windows and compares its **maximum over time** against critical
  values that account for taking that maximum. So a statement such as "model A
  was better in the 2000s and worse in the 2010s" becomes testable rather than a
  visual impression.

A **HAC** (heteroskedasticity and autocorrelation consistent) variance
estimate adds down-weighted autocovariances of $d_t$, up to some lag, to its
variance. The **Newey–West** estimator is the standard example. The standard
error of $\bar d$ then remains valid when the loss differentials are
serially correlated, as daily ones are.

**Why it appears here.** §11.6 ranks the fluctuation test as the most useful
diagnostic in the document. A genuinely regime-aware model should have
its advantage *concentrated in the regime it was designed for*, and the test
shows whether it does. §6.9 and §6.11 compare density forecasts this way, with Newey–West standard errors.

**Deeper.** Giacomini & White (2006) and [Giacomini & Rossi (2010)](https://ideas.repec.org/p/duk/dukeec/08-4.html){target="_blank"}, both in §4.8.
Rossi, "Forecasting in the Presence of Instabilities," *Journal of Economic
Literature* 59(4) (2021), 1135–1190, is the survey.

## A.43 Conformal prediction under distribution shift {#a43}
**The idea.** Conformal prediction produces prediction intervals with a
guaranteed coverage rate. The guarantee does not depend on the model being
correct. An adaptive version keeps its guarantee when the distribution changes.

**Formally.** Split conformal prediction holds out a calibration set and computes
non-conformity scores $s_i = |y_i - \hat f(x_i)|$ on it. It forms the interval
$\hat f(x) \pm \hat q_{1-\alpha}$, where $\hat q_{1-\alpha}$ is the empirical
$(1-\alpha)$ quantile of the scores. Under exchangeability this has marginal
coverage at least $1 - \alpha$ regardless of the model. Exchangeability fails
under distribution shift. So **adaptive conformal inference** ([Gibbs & Candès,
2021](https://arxiv.org/abs/2106.00170){target="_blank"}) updates the nominal level online,
$\alpha_{t+1} = \alpha_t + \eta(\alpha - \mathbb{1}[y_t \notin C_t])$.
This recovers the long-run coverage rate without any distributional assumption.

**Why it appears here.** §10.8. It is the only tool in this document that
offers a guarantee holding *under* shift rather than a method that tries to
adapt to it. Its output is an interval that widens in unfamiliar conditions.
That interval is directly usable as a sizing input.

**Deeper.** Angelopoulos & Bates, ["A Gentle Introduction to Conformal Prediction
and Distribution-Free Uncertainty Quantification"](https://arxiv.org/abs/2107.07511),
arXiv:2107.07511; [Gibbs & Candès (2021)](https://arxiv.org/abs/2106.00170){target="_blank"} in §4.7.

## A.44 Real-time data vintages {#a44}
**The idea.** Macroeconomic statistics are estimates, published with a lag and
revised repeatedly afterwards. The number you can download today for a date in
1995 differs from the number anyone had in 1995.

**Formally.** A **vintage** is the complete set of values for a series as
published at one point in time. A real-time data set is therefore two-dimensional,
indexed by observation date *and* vintage date. A point-in-time query asks
for the value of period $s$ as known at date $v \ge s$. The Federal Reserve Bank
of Philadelphia maintains such a database for U.S. macro series. ALFRED
provides vintage-aware access to FRED. Revisions are frequently larger than the
series' own standard deviation. Statistical agencies revise initial releases of
quarterly GDP for years.

**Why it appears here.** §1.5's note on NBER recession dates, which are announced
6–18 months after the turning points they label. §6.6, which requires real-time
vintages for macro covariates. §11.2's leak 8. Any regime
model that conditions on macro data and does not use vintages is conditioning on
information that did not exist.

**Deeper.** Croushore & Stark, "A Real-Time Data Set for Macroeconomists,"
*Journal of Econometrics* 105(1) (2001), 111–130.

## A.45 Mean-variance sizing, Kelly, and volatility targeting {#a45}
**The idea.** This entry answers how large a position should be, given a forecast
of return and a forecast of risk. All the standard answers have the same form:
expected return over variance, scaled by risk appetite.

**Formally.** Maximising $\mathbb{E}[\pi r] - \tfrac{\gamma}{2}\operatorname{Var}[\pi r]$
over the position $\pi$ gives

$$\pi^\star = \frac{\mathbb{E}[r \mid \mathcal{F}_{t-1}]}{\gamma \operatorname{Var}[r \mid \mathcal{F}_{t-1}]},$$

The **Kelly** criterion is the special case $\gamma = 1$ (log utility).
**Volatility targeting** is the special case where the expected return is treated
as proportional to volatility, giving $\pi^\star \propto \sigma^\star/\hat\sigma_t$.
For a mixture predictive distribution the two moments are
$\bar\mu = \sum_k \xi^{(k)}\mu_k$ and
$\operatorname{Var} = \sum_k \xi^{(k)}\sigma_k^2 + \sum_k \xi^{(k)}(\mu_k - \bar\mu)^2$.
The variance is a within-state term plus a between-state term. The between-state
term reflects uncertainty about which state you are in.

**Why it appears here.** §12.1 argues that a regime posterior should feed these
moments, not an argmax label. §7.2 records the corollary that
every volatility-targeted strategy is already regime-conditional with a continuum
of states. §6.10 extends the two-moment decomposition, which is the law of total variance, to cumulative returns over $h$ bars.

**Deeper.** MacLean, Thorp & Ziemba, eds., *The Kelly Capital Growth Investment
Criterion* (World Scientific, 2011), part I.

## A.46 Transaction-cost models and no-trade bands {#a46}
**The idea.** The functional form of trading costs determines the form of the
optimal trading rule. Costs proportional to the amount traded produce a region
where you do nothing. Costs quadratic in the trading *rate* produce partial
adjustment toward a target.

**Formally.** Under **proportional** costs $\varepsilon |\Delta \pi|$, the
optimal policy for a Merton-style problem is a **no-trade band**. Do nothing
while the position lies inside an interval around the frictionless target. When
the position leaves the interval, trade only to its nearest edge. The classical
result is that the band's half-width scales as $\varepsilon^{1/3}$ for small
$\varepsilon$. So a tenfold cost increase widens the band only about
$2.15\times$. Under **quadratic**
costs $\tfrac{\lambda}{2}\Delta\pi^{\top}\Sigma\,\Delta\pi$, the optimal policy is
linear. Trade a constant fraction of the way toward an **aim portfolio**. The aim
portfolio is a weighted average of current and expected future frictionless
targets, and it overweights slowly decaying signals.

**Why it appears here.** §12.2. The cube-root scaling matters because people
consistently over-widen bands in response to cost estimates. The aim-portfolio
result matters because regime signals decay fast (§1.3). They therefore deserve
*less* weight in the aim than their raw strength suggests.

**Deeper.** Constantinides (1986) and Gârleanu & Pedersen (2013), both cited in
§12. Davis & Norman, "Portfolio Selection with Transaction Costs," *Mathematics
of Operations Research* 15(4) (1990), 676–713, covers the continuous-time band.

---

These documents were generated in whole or in part with the help of a large language model.
Dedicated to the public domain under the [CC0 1.0 Universal Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).

[Index](index.html) · [Source](https://github.com/rmahfoud/quant-research)
