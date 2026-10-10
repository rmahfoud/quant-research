---
pagetitle: "Edge as Information: Sharpe, IR and IC"
description: "Sharpe ratio, information ratio, IC and breadth as one idea: signal-to-noise, information that adds and leaks, and how long it takes to prove an edge."
keywords: ["Sharpe ratio", "information ratio", "information coefficient", "fundamental law of active management", "breadth", "transfer coefficient", "Kelly criterion", "information theory", "mutual information", "track record"]
author: "Robert Mahfoud"
lang: en
---

# Edge as Information

### Sharpe, IR, IC and the fundamental law as one idea: how much a forecast knows, and how long it takes to prove it

---

```{=html}
<aside class="eli5">
```

# ELI5 — the short version {#eli5}

```{=latex}
\begin{eli5}
```

**In one sentence.** The Sharpe ratio, the information ratio and the information coefficient are not three different scores but one measurement, taken at different stages, of how much a strategy knows about the future.

**1. One thing, measured at four stages** ([§1](#1-what-an-edge-is)). A strategy makes a forecast, turns it into positions, earns profits and losses, and builds a track record. The information coefficient scores the forecast. The transfer coefficient scores the positions. The information ratio or Sharpe ratio scores the profits, and the t-statistic scores the record. Each stage can only lose what the forecast knew. No stage can add to it.

**2. Every ratio is signal over noise** ([§2](#2-signal-and-noise)). Each of these numbers divides a steady part by a random part. The steady part adds up bet by bet, while the noise grows only with the square root of the number of bets. So all the ratios grow with the square root of the number of independent bets. A strategy with a Sharpe ratio of one is good. It still loses money on 47.5% of days, and in about one year out of six.

**3. Good forecasts look like noise** ([§2](#2-signal-and-noise)). A forecast that picks the better of two stocks 51.6% of the time is a good one. Plotted point by point, it is invisible. It shows up only when hundreds of bets are averaged. Even 3,000 bets measure its quality only roughly.

**4. Edge is information, and it can be counted in bits** ([§3](#3-edge-as-information)). Information theory, the mathematics built for telephone lines, gives all these ratios a common unit. A good forecast carries about a five-hundredth of a coin toss of information per bet. In 1956 John Kelly showed that, at fair odds, money can grow exactly as fast as information arrives, and no faster. Each bit of information can at most double a gambler's wealth. A strategy with a Sharpe ratio of one learns less than one bit about the market in a year.

**5. Work in squares** ([§3](#3-edge-as-information)). Information from independent sources adds up. Information is measured by the square of these ratios, not by the ratios themselves. The well-known "fundamental law of active management" says no more than this: it is bookkeeping. It also explains why adding a second, unrelated strategy with a Sharpe ratio of a half lifts a portfolio from 0.5 to 0.71. That gain equals making the first strategy 41% better, and the second strategy is usually far easier to find.

**6. Information only leaks** ([§6](#6-using-it)). A ban on selling short, trading costs and slow execution each lose some of what the forecast knew. In the chapter's worked example, a forecast promised an information ratio of 3.1 plausibly delivers about 0.5. It keeps some 3% of the information it was sold on. The cheapest place to win some back is usually how faithfully the portfolio expresses the forecasts, not a cleverer forecast.

**7. The promise of breadth is mostly hollow** ([§7](#7-where-it-breaks)). The arithmetic treats 500 stocks as 500 independent bets. They are not. Stocks move together, and a signal that fails in a given month fails on all of them at once. So adding stocks stops helping long before the arithmetic says it should. The limit is set by how consistently the forecast works from month to month, not by the size of the universe.

**8. Proof takes years** ([§3](#3-edge-as-information)). The same squared number that measures information also measures evidence. To show at the usual standard that an edge is real, a strategy needs about four divided by its squared Sharpe ratio in years of live results. That is four years at a Sharpe ratio of one, and 16 at a half. Each doubling of the number of ideas tried before this one was chosen adds roughly one more bit of evidence to collect. Over three years, a top-quartile manager trails the benchmark about one time in five. A manager with no skill posts a top-quartile record just as often.

**9. Distrust numbers that look too good** ([§5](#5-the-ratio-zoo), [§7](#7-where-it-breaks)). Rival ratios such as Sortino and Calmar add nothing when returns behave normally, and they are noisier. Strategies that sell insurance look superb until the disaster they are paid to bear. A backtested Sharpe ratio above two is more often a mistake in the data than a discovery.

---

**If you do only three things:** compare and combine edges in squares, not ratios; before trusting a forecast's promise, count only truly independent bets and list every way the information leaks on its way to the profits; and before judging any track record, ask whether it has run for four divided by its squared Sharpe ratio in years, and longer if many ideas were tried.

```{=latex}
\end{eli5}
```

```{=html}
</aside>
```

A Sharpe ratio, an information ratio, an information coefficient and a t-statistic are usually taught as four scorecards, each with its own formula and its own folklore. They are one quantity, measured at different points on the path from a forecast to a track record. That quantity has a name in another field: **information**. This chapter builds that view from the ground up and then puts it to work. It covers how to read each ratio and what values to expect, and how signals and strategies combine. It covers how much of a forecast survives into the P&L, and how long a track record has to run before it says anything at all.

The emphasis is on intuition and on what practitioners actually compute. The mathematics is limited to what makes the intuition exact. Appendix A collects the underlying information theory, built from scratch, for readers who want it.

**How to read this chapter.** §1 is the whole argument in miniature, with one worked example carried from forecast to P&L. §2 presents the signal-to-noise view. It is the simpler of the two framings, and on its own it corrects most misreadings of a Sharpe ratio. §3 presents the information view, which is the spine of the chapter. §4 takes the core ratios one at a time in a fixed format. §5 places the wider family (Sortino, Calmar, Omega and the rest) on one grid. §6 is practice: turning a signal into an expected return, measuring and combining signals, counting breadth, raising the transfer coefficient, sizing, and judging a track record. §7 covers where the framework breaks, §8 gives a short history, §9 is the synthesis, and §10 lists the references.

Different readers can start in different places.

- Readers who want only the idea should read §1, §2.6, §3.3 and §3.6.
- Readers who build signals should read §2.2, §3.4 and §6.1 to §6.5.
- Readers who allocate money to strategies or managers should read §2.5, §3.6, §6.6, §6.7 and §7.3.

Appendix A covers the information theory: entropy, mutual information, relative entropy, channel capacity, the data-processing inequality and Kelly's horse race, each with the derivation the main text skips. Appendix B defines the remaining statistical and market vocabulary, built up in dependency order.

**Objectives.** After this chapter, you should be able to:

- explain why the IC, the transfer coefficient, the information ratio and the t-statistic measure one quantity at four stages;
- convert an IC into a hit rate, an amount of information per bet, and an expected return for each asset;
- combine signals and strategies in squared units, and count the independent bets a strategy really makes;
- list the leaks between forecast and P&L, and estimate what each one costs;
- size a strategy from its Sharpe ratio, and explain why practitioners run well below the growth-optimal leverage;
- compute how many years a track record needs before it is evidence, and how a search raises that number.

**Relationship to the other notes.** [Systematic Trading Strategies](systematic_strategies.html) uses the fundamental law to explain why diversified rules win. This chapter shows where the law comes from and where it breaks. [Momentum in Financial Markets](momentum_deep_dive.html) applies these metrics to one family of signals in its section on testing. [Simple and Log Returns](log_returns.html) derives the Kelly growth rate that §3.2 relies on. [Portfolio Construction and the Covariance Matrix](portfolio_construction.html) covers in detail how forecasts become weights, the step the transfer coefficient scores. [Foundations of Econometrics](econometrics_foundations.html) covers effective sample size and multiple testing in general. [Value at Risk](value_at_risk.html) covers the tail measures that appear in §5. Each note stands alone.

**Where the numbers come from.** Every number in the text is either arithmetic from a stated formula or the output of a seeded simulation on synthetic data. No market data is used. The scripts that produce the numbers are [`figures/ei_*.py`](https://github.com/rmahfoud/quant-research/tree/master/figures){target="_blank"} in the source repository. [`figures/ei_numbers.py`](https://github.com/rmahfoud/quant-research/blob/master/figures/ei_numbers.py){target="_blank"} prints the tables that have no figure. Synthetic data is a deliberate choice. The point is what the ratios mean, and only in a simulation is the true value known, so that the measured value can be compared with it.

**A warning about scope.** Nothing here is investment advice. The worked strategies are illustrations, chosen to make the arithmetic visible.

**Epistemic tags.** The chapters in this collection flag claims by status:

- **[Fact]** — replicated across independent datasets or implementations; broad agreement.
- **[Contested]** — documented, but with live disagreement about magnitude, robustness, or cause.
- **[Hypothesis]** — a proposed mechanism, not decisively tested.
- **[Practice]** — practitioner convention; the evidence may be private or absent. A [Practice] claim is not a debunked one.

Tags appear only where the status changes what a reader should do. A tag governs the sentence or clause it opens. Untagged sentences are definitions, derivations or arithmetic, true by construction rather than by evidence. Findings attributed in the sentence to a named study are also untagged, and their standing is that of the study.

---

**Notation.** The table lists every symbol that recurs in the chapter, with the section that defines or first uses it. Symbols used in only one section are defined where they appear. Returns are per period, and every ratio is **annualised** unless the text says otherwise.

| Symbol | Meaning | Defined in |
|---|---|---|
| $r_t$; $\mu$; $\sigma$ | A strategy's return in period $t$ in excess of cash; its mean; its standard deviation | §2.1, §4.1 |
| $\mathrm{SR} = \mu/\sigma$ | **Sharpe ratio** | §2.1, §4.1 |
| $q$ | Number of periods in a year: 12 for monthly data, 252 for daily | §2.3 |
| $r_B$; $\beta$ | The benchmark's excess return; a strategy's sensitivity to it | §4.2 |
| $\alpha$; $\omega$ | Mean **residual return** (the part the benchmark does not explain); its standard deviation, the **residual risk**, often loosely called the **tracking error** (§3.7 gives the difference) | §4.2 |
| $\mathrm{IR} = \alpha/\omega$ | **Information ratio** | §4.2 |
| $s$; $y$ | A forecast, or **signal**, standardised to mean zero and variance one; the outcome it forecasts, standardised the same way, usually an asset's next-period residual return divided by its residual volatility | §2.2, §6.1 |
| $\varepsilon$ | Noise with variance one, independent of the signal | §2.2 |
| $\mathrm{IC} = \operatorname{Corr}(s, y)$ | **Information coefficient** | §2.2, §4.3 |
| $\mathrm{IC}_t$; $\overline{\mathrm{IC}}$ | IC computed across assets in period $t$; its mean over time | §4.3 |
| $\sigma_{\mathrm{IC}}$; $\hat\sigma_{\mathrm{IC}}$ | Standard deviation of the genuine variation in how well a signal works from period to period; standard deviation of the measured $\mathrm{IC}_t$ series, with $\hat\sigma_{\mathrm{IC}}^2 \approx \sigma_{\mathrm{IC}}^2 + 1/N$ | §7.1, §4.3 |
| $R^2$ | Share of an outcome's variance a forecast explains | §2.2 |
| $\mathrm{SNR}$ | The engineer's signal-to-noise ratio: a ratio of variances, not of standard deviations | §2.2 |
| $n$ | Number of independent bets or observations being averaged | §2.3 |
| $N$ | Number of assets | §2.4, §4.4 |
| $\mathrm{BR}$ | **Breadth**: the number of independent bets per year | §2.3, §4.4 |
| $\mathrm{TC}$ | **Transfer coefficient**: the correlation between the positions a forecast calls for and the positions actually held | §3.5, §4.5 |
| $\rho$; $\rho_k$ | A correlation between two things named where it appears; the autocorrelation of returns at lag $k$ | §2.4 |
| $\tau$ | A horizon: in years in §2.5, and the forward-return window in §6.2 | §2.5, §6.2 |
| $T$ | Length of a track record, in years | §2.1, §3.6 |
| $t$ | **t-statistic** of a mean; written without a subscript so it cannot be confused with the time index | §2.1, §4.7 |
| $K$ | Number of strategies or variants tried before one was kept | §3.6 |
| $\Phi$ | Standard normal distribution function | §2.5 |
| $\mathcal{N}(\mu, \sigma^2)$ | Normal distribution with mean $\mu$ and variance $\sigma^2$ | §3.6 |
| $\alpha_i$; $\sigma_i$; $\Delta w_i$ | Asset $i$'s forecast residual return; its residual volatility; its active weight | §4.5, §6.1 |
| $\mathbf{ic}$; $\mathbf{C}$ | Vector of the ICs of several signals; correlation matrix of the signals (in §6.6, of strategy returns) | §6.3, §6.6 |
| $\gamma_3$; $\gamma_4$ | Skewness; kurtosis (3 for a normal distribution) | §4.1 |
| $\mathrm{SR}_0$ | Benchmark Sharpe ratio in the probabilistic and deflated Sharpe ratios | §4.7 |
| $H$ | Entropy | §3.1, A.1 |
| $I(X;Y)$ | **Mutual information** between $X$ and $Y$ | §2.6, A.3 |
| $D(P\,\Vert\,Q)$ | **Relative entropy** (Kullback–Leibler divergence) of $P$ from $Q$ | §3.6, A.5 |
| nats; bits | Units of information, with natural and base-two logarithms; one nat is $1/\ln 2 \approx 1.44$ bits | §3.1, A.2 |
| $g$; $g^\ast$ | Growth rate of log wealth in excess of cash; its growth-optimal value | §3.2 |
| $f$; $f^\ast$ | A fraction of wealth bet, or a leverage; the growth-optimal (Kelly) leverage | §3.6, §6.6 |
| $h$; $d$ | Half-life of a signal's IC; delay between forecast and trade | §3.5 |

Bold symbols are vectors and matrices. In §3.3 and Appendix B, $\Sigma$ is a covariance matrix.

---

## Table of contents

- [ELI5 — the short version](#eli5)

1. [What an edge is](#1-what-an-edge-is)
2. [Signal and noise](#2-signal-and-noise)
3. [Edge as information](#3-edge-as-information)
4. [The core ratios, one at a time](#4-the-core-ratios)
5. [Beyond the standard deviation: the ratio zoo](#5-the-ratio-zoo)
6. [Using it](#6-using-it)
7. [Where it breaks](#7-where-it-breaks)
8. [How the ideas evolved](#8-how-the-ideas-evolved)
9. [Synthesis](#9-synthesis)
10. [References](#10-references)

- [Appendix A. Information theory for investors](#appendix-a-information-theory)
- [Appendix B. Concepts and prerequisites](#appendix-b-concepts-and-prerequisites)

---

```{=latex}
\newpage
```

# 1. What an edge is {#1-what-an-edge-is}

## 1.1 The wrong intuition

Two common beliefs cause most misreadings of these ratios, and they err in opposite directions.

The first belief is that **the ratios are separate scorecards.** A quant reports an IC, a portfolio manager an information ratio, an allocator a Sharpe ratio, and a statistician a t-statistic. Each treats the others' numbers as different facts about the strategy. They are measurements of one fact. The IC measures how much a forecast knows about one bet. The information ratio measures how much of that knowledge reached the P&L in a year. The t-statistic measures how much of it a track record has revealed so far. The useful questions concern what happens to that one quantity at each stage between forecast and track record.

The second belief is that **small numbers mean small edges.** Consider a correlation of 0.05 between a forecast and the next month's return. It explains a quarter of one percent of the return's variance, and it gets the direction right 51.6% of the time. On a scatter plot it is indistinguishable from noise (§2.2), and most people who see it for the first time conclude that it is worthless. Yet applied once a month to 500 stocks whose surprises are independent, it would produce an information ratio of 3.9. Few investors have ever sustained a number that high. Real signals land between these two readings, and much of this chapter explains why the 3.9 is never reached (§1.4, §7.1). Even so, the belief that such a signal is worthless is wrong by an order of magnitude.

Both beliefs disappear once the ratios are read as measurements of one quantity. The rest of this section defines that quantity.

## 1.2 One pipeline, four ratios

An active strategy is a pipeline with four stages. A **forecast** says something about next period's returns. **Positions** are taken because of the forecast. The positions produce a **P&L**. The P&L accumulates into a **track record**, which the manager and every allocator use to judge whether the forecast was any good. Each stage has its own ratio, as the diagram shows.

```mermaid
flowchart LR
    F["<b>Forecast</b><br/>scored by the IC:<br/>how much one bet knows"]
    P["<b>Positions</b><br/>scored by the TC:<br/>how much was acted on"]
    L["<b>P&amp;L</b><br/>scored by the IR or Sharpe:<br/>how much a year earned"]
    R["<b>Track record</b><br/>scored by the t-statistic:<br/>how much has been proved"]
    F -- "constraints,<br/>risk model" --> P
    P -- "costs, delay,<br/>impact" --> L
    L -- "finite history,<br/>many trials" --> R
    style F fill:#0B6E75,color:#fff
    style P fill:#0B6E75,color:#fff
    style L fill:#0B6E75,color:#fff
    style R fill:#A8452B,color:#fff
```

- The **information coefficient** (IC) is the correlation between the forecast and the outcome, bet by bet (§4.3).
- The **transfer coefficient** (TC) is the correlation between the positions the forecast calls for and the positions actually held after constraints (§4.5).
- The **information ratio** (IR) is the annual residual return divided by its volatility. The **Sharpe ratio** is the same ratio measured against cash rather than against a benchmark (§4.1, §4.2).
- The **t-statistic** is the information ratio multiplied by the square root of the number of years observed (§4.7).

The arrow labels name what happens between stages, and each of those steps subtracts. Nothing that happens after the forecast is made can add to what the forecast knows. §3.5 states this fact precisely. It is why the realistic question about a strategy is "how much of the signal survives?" rather than "how good is the signal?"

## 1.3 Three ideas the rest hangs on

Three ideas and one corollary generate the rest of the chapter.

**Idea 1: every ratio is a signal-to-noise ratio** (§2). Sharpe, IR, IC and the t-statistic all take the form *systematic part divided by random part*. So they share a scaling law: averaging $n$ independent observations multiplies any of them by $\sqrt{n}$. Annualising a Sharpe ratio with $\sqrt{12}$ and the fundamental law's $\sqrt{\mathrm{BR}}$ are the same law, applied once across time and once across assets. The ratios also share a failure. The law holds only when the noise is independent, and in markets it rarely is.

**Idea 2: squares are information, and information adds** (§3). The square of an IC is, to a very good approximation, twice the information, in nats, that one bet carries about its outcome. Likewise, the square of an information ratio is twice the information that a year of bets carries. The fundamental law, $\mathrm{IR}^2 = \mathrm{IC}^2 \times \mathrm{BR}$, is therefore bookkeeping: each independent bet contributes its share, and the shares add. Squared Sharpe ratios of uncorrelated strategies add for the same reason. The ratios themselves are the wrong unit for reasoning, and their squares are the right one.

**Idea 3: information only leaks** (§3.5). Positions are computed from the forecast, and P&L comes from the positions. Processing can destroy information but cannot create it. The transfer coefficient measures the part of the leak that constraints cause, and its square is the share of the information that reaches the portfolio. Costs, delays and estimation error leak more. A realistic plan for a strategy is therefore an inventory of its leaks.

**The corollary: one number does three jobs** (§3.6). Half the squared Sharpe ratio, $\mathrm{SR}^2/2$, measures three things at once. It is the rate at which a growth-optimal investor's log wealth outgrows cash. It is the information the strategy extracts from the market each year. And it is the evidence an observer accumulates each year that the edge is real. The third reading gives the most useful rule of thumb in the chapter. A strategy with Sharpe ratio $\mathrm{SR}$ needs about $4 / \mathrm{SR}^2$ years of live returns before its t-statistic can be expected to reach two. That is four years at a Sharpe ratio of one and 16 years at one half, before any allowance for the other strategies that were tried and discarded.

## 1.4 A worked instance

The example below follows one signal through the pipeline. The signal is a monthly forecast of which of 500 stocks will beat the others over the next month. Its average information coefficient is 0.04, which practitioners regard as good (§4.3).

- **One bet.** An IC of 0.04 calls the direction of a stock's relative return correctly 51.3% of the time. Each bet carries about 0.0012 bits of information. So it takes some 860 bets to learn one bit, the information in a single fair coin toss (§3.1).
- **The promise.** The fundamental law counts $500 \times 12 = 6{,}000$ bets a year and promises $\mathrm{IR} = 0.04 \times \sqrt{6{,}000} = 3.10$.
- **Breadth that is really there.** The 500 bets in a month are not independent. The signal works better in some months than in others, so all 500 outcomes share a common component. Suppose the IC varies from month to month with a standard deviation of 0.08, a typical value, on top of the sampling noise that comes from having only 500 stocks. Then the attainable information ratio falls to 1.51 (§7.1 gives the formula). Three quarters of the information the law promised was never there.
- **Constraints.** A transfer coefficient of 0.6 cuts the information ratio to 0.91. That value is at the top of the usual long-only range and below a typical long-short one (§4.5).
- **Delay.** Stale data or slow execution that loses a tenth of the IC between forecast and trade leaves 0.82.
- **Costs.** Trading costs of 1.5% a year, against a tracking error of 5%, take 0.3 off the information ratio and leave 0.52.

The chart shows the information ratio at each of the five stages.

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/ei_leak.pdf}
\end{center}
```

```{=html}
<img class="mdd-fig" src="quant-research/figures/ei_leak.svg"
     alt="Bar chart of the information ratio of one signal at five stages, falling from 3.10 promised to 0.52 after costs">
```

In the units that add, squared information ratios, the strategy keeps 2.8% of what the fundamental law promised. Strictly, costs are not a loss of information but a deduction from the return. The chart shows them in the same units because what matters is what is left. The final 0.52 still describes a strategy most institutions would be pleased to run. But it needs $4 / 0.52^2 \approx 15$ years of live returns before its t-statistic reaches two. The 3.10 it was sold as would need five months. Most of the rest of this chapter concerns that gap between what a signal promises and what a track record can prove.

## 1.5 What this chapter is not

This chapter is not a guide to finding signals. Where forecasts come from is the subject of the strategy notes, and here a forecast is taken as given and scored. It is not a catalogue of performance ratios, although §5 places the common ones on a single grid. And it does not treat portfolio optimisation, which appears only through the transfer coefficient. The chapter is about measurement: what each number means, how the numbers relate, and how far each can be trusted.

> ### §1 Key takeaways
>
> 1. The IC, the transfer coefficient, the information ratio and the t-statistic score the four stages of one pipeline: forecast, positions, P&L and track record. All four follow one quantity through it.
> 2. Each of them is a signal-to-noise ratio. So each scales with the square root of the number of independent observations, and each breaks when the observations are not independent.
> 3. Reason in squares. Squared ratios are information, and information from independent sources adds. The fundamental law is that bookkeeping.
> 4. Information only leaks between stages. The realistic question is how much of a signal survives, not how good it is.
> 5. A good signal, with an IC of 0.04 on 500 stocks, is promised an information ratio of 3.1 and plausibly delivers about 0.5. It keeps some 3% of the promised information.
> 6. A strategy needs roughly $4/\mathrm{SR}^2$ years for its t-statistic to reach two: four years at a Sharpe ratio of one, 16 at one half.

```{=latex}
\newpage
```

# 2. Signal and noise {#2-signal-and-noise}

This section presents the simpler of the chapter's two framings. It needs only means, standard deviations and correlations. On its own, it corrects most of the common misreadings of a Sharpe ratio. §2.6 then shows that it is the information framing of §3 expressed in different units.

## 2.1 Every ratio is a mean over a standard deviation

Each of the core ratios divides a systematic part by a random part, as the table shows.

| Ratio | Signal (top) | Noise (bottom) | Measured per |
|---|---|---|---|
| Sharpe ratio | mean return over cash, $\mu$ | its standard deviation, $\sigma$ | year |
| Information ratio | mean residual return, $\alpha$ | residual risk, $\omega$ | year |
| Information coefficient | covariance of forecast and outcome | product of their standard deviations | bet |
| IC information ratio | mean IC, $\overline{\mathrm{IC}}$ | standard deviation of the measured IC over time, $\hat\sigma_{\mathrm{IC}}$ | period |
| t-statistic | sample mean | standard error of the sample mean | whole record |

Each ratio answers the same question: how many units of noise is the signal worth? A Sharpe ratio of 0.5 says that a year's expected excess return is half a standard deviation of a year's excess return. A t-statistic of 2 says that the average return over the whole record lies two standard errors from zero. The information coefficient looks different, but only on the surface. A correlation is the covariance of two standardised variables. So it, too, is a systematic part, the co-movement of forecast and outcome, measured in units of their noise.

Treating the ratios as one kind of object explains their arithmetic. A Sharpe ratio measured monthly and one measured annually differ by a factor of $\sqrt{12}$. A t-statistic is a Sharpe ratio times $\sqrt{T}$. Both facts have the same cause: each converts a signal-to-noise ratio for one period into one for many periods (§2.3).

## 2.2 Correlation as a signal fraction

Split the standardised outcome into a part the forecast explains and a part it does not:

$$
y \;=\; \mathrm{IC}\cdot s \;+\; \sqrt{1-\mathrm{IC}^2}\;\varepsilon ,
$$

where $s$ is the standardised forecast and $\varepsilon$ is noise with variance one, independent of $s$. The two parts have variances $\mathrm{IC}^2$ and $1-\mathrm{IC}^2$. So

$$
R^2 = \mathrm{IC}^2, \qquad
\mathrm{SNR} \;=\; \frac{\text{variance of the signal part}}{\text{variance of the noise part}} \;=\; \frac{\mathrm{IC}^2}{1-\mathrm{IC}^2}.
$$

Here $\mathrm{SNR}$ is the engineer's signal-to-noise ratio, a ratio of variances, or powers. The ratios of §2.1 are ratios of amplitudes, measured in standard deviations. For a small IC, the power ratio is close to the square of the amplitude ratio: $\mathrm{SNR} \approx \mathrm{IC}^2$. §2.6 depends on that square.

At an IC of 0.05, the signal part carries a quarter of one percent of the variance, and the noise variance is 400 times the signal's. The figure shows what such a forecast looks like.

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/ei_signal_cloud.pdf}
\end{center}
```

```{=html}
<img class="mdd-fig" src="quant-research/figures/ei_signal_cloud.svg"
     alt="Two scatter plots of 3,000 forecast and outcome pairs, at correlations 0.05 and 0.30, with the average outcome in twenty forecast bins">
```

The left panel shows a good signal. Bet by bet it is invisible: the grey cloud contains no pattern an eye could find. The signal appears only in averages. The 300 bets with the highest forecasts beat the 300 with the lowest by a fifth of a standard deviation. The right panel, with an IC of 0.30, matches what people imagine a working forecast looks like. In liquid markets, nobody keeps a forecast that good for long (§4.3).

The left panel also shows how hard an IC is to measure. The true value is 0.05, and 3,000 bets estimated it at 0.032. The standard error of a correlation estimated from $n$ independent pairs is close to $1/\sqrt{n}$, here 0.018. So even 3,000 bets pin the IC down only to within about $\pm 0.04$, two standard errors either side. A signal has to be used many times before anyone, its owner included, knows how good it is.

The **hit rate**, the share of bets whose direction is right, gives a third view of the same number. Suppose forecast and outcome are jointly normal with correlation $\mathrm{IC}$. Then the probability that they have the same sign is $\tfrac12 + \arcsin(\mathrm{IC})/\pi$:

| IC | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|---|---|---|---|---|---|
| Hit rate | 50.6% | 51.6% | 53.2% | 56.4% | 59.7% |

Below an IC of about 0.3, the hit rate is close to $\tfrac12 + \mathrm{IC}/\pi$. Each 0.01 of IC buys about a third of a percentage point of hit rate. These hit rates are not specific to one kind of forecast. Appendix A.8 shows that the information an IC of 0.05 carries caps the hit rate of any method at 52.5%. Hit rate is a coarse summary, because it ignores the size of the wins and losses. §4.6 explains when it misleads.

## 2.3 The square-root law

Add up $n$ independent bets, each with the same expected payoff $m$ and the same standard deviation $v$. The expected total is $n m$. The standard deviation of the total is $\sqrt{n}\, v$, because variances add while standard deviations do not. The signal-to-noise ratio of the total is therefore

$$
\frac{n\,m}{\sqrt{n}\,v} \;=\; \sqrt{n}\;\frac{m}{v}.
$$

Signal accumulates in proportion to the number of bets, and noise only in proportion to its square root. This one line drives every active strategy. It works in two directions.

- **In time.** A year is $q$ periods. So an annual Sharpe ratio is the per-period Sharpe ratio times $\sqrt{q}$, and a t-statistic over $T$ years is the annual Sharpe ratio times $\sqrt{T}$.
- **Across assets.** A year of a strategy is $\mathrm{BR}$ independent bets. Each bet has a signal-to-noise ratio close to $\mathrm{IC}$: a position proportional to the standardised forecast earns $s\,y$, whose mean is $\mathrm{IC}$ and whose standard deviation is $\sqrt{1+\mathrm{IC}^2}$, close to one. So the annual information ratio is $\mathrm{IC}\sqrt{\mathrm{BR}}$. This is Grinold's fundamental law of active management ([Grinold, 1989](https://doi.org/10.3905/jpm.1989.409211){target="_blank"}). It is the square-root law with bets in place of periods.

The law also explains why good strategies feel bad from the inside. A strategy with an annual Sharpe ratio of 1 has a daily Sharpe ratio of $1/\sqrt{252} = 0.063$. Day by day, it behaves like a coin that comes up heads 52.5% of the time. It loses money on 47.5% of days, 38.6% of months and 15.9% of years (§2.5). The edge is real, yet most of what the owner experiences is noise.

## 2.4 Where the square-root law fails

The law requires the noise in the bets to be independent. In markets it rarely is, and the failures come in three kinds.

**Noise shared across bets.** Suppose the surprises in $N$ bets have an average pairwise correlation $\rho$. Then the variance of their average equals that of $N/(1+(N-1)\rho)$ independent bets. This quantity is the **effective number of independent bets**. (It differs from the entropy-based "effective number of bets" of Appendix A.12.) It falls quickly as $\rho$ rises:

| Average correlation of the surprises, 500 bets | 0 | 0.002 | 0.005 | 0.01 | 0.02 | 0.05 |
|---|---|---|---|---|---|---|
| Effective number of independent bets | 500 | 250 | 143 | 84 | 46 | 19 |

A correlation of 0.01, far too small to see in any single pair of stocks, turns 500 bets into 84. This is why cross-sectional strategies neutralise their positions against market, sector and style factors. Shared factor exposure is a correlation between the surprises in different bets, and removing the exposure pushes $\rho$ toward zero.

**Noise shared across time.** If returns are autocorrelated, a year is not $q$ independent periods. [Lo (2002)](https://doi.org/10.2469/faj.v58.n4.2453){target="_blank"} gives the correct multiplier for annualising a Sharpe ratio:

$$
\eta(q) \;=\; \frac{q}{\sqrt{q + 2\sum_{k=1}^{q-1}(q-k)\,\rho_k}},
$$

where $\rho_k$ is the autocorrelation of returns at lag $k$. With no autocorrelation, the multiplier is $\sqrt{q}$. The table assumes monthly returns whose autocorrelation decays geometrically from its first-order value $\rho_1$, so that $\rho_k = \rho_1^k$.

| Monthly autocorrelation | −0.1 | 0 | 0.1 | 0.2 | 0.3 | 0.4 |
|---|---|---|---|---|---|---|
| Correct multiplier (vs $\sqrt{12} = 3.46$) | 3.80 | 3.46 | 3.16 | 2.88 | 2.61 | 2.36 |
| Overstatement from using $\sqrt{12}$ | −9% | 0% | +10% | +20% | +32% | +47% |

Positive autocorrelation is the signature of smoothed returns. Stale prices in illiquid assets produce it, and so does a manager who marks their own book. It makes $\sqrt{12}$ overstate the annual Sharpe ratio (§7.3). Negative autocorrelation, common in mean-reverting strategies, has the reverse effect.

**Noise that never averages.** Some noise is common to every bet in a period, however many bets there are. The most important case is variation in the IC itself from one period to the next. In a month when the signal does not work, it fails on all 500 stocks at once. That component does not shrink with breadth, so it puts a ceiling on the information ratio. It is the main reason the fundamental law overpromises, and §7.1 measures it.

## 2.5 What a Sharpe ratio feels like

A Sharpe ratio stays abstract until it is translated into outcomes an investor actually experiences. The table makes that translation for normal, independent returns.

| Sharpe | Losing month | Losing year | Losing 5 years | Worst 10-year drawdown, expected | P(drawdown > 2 vol) | Years to $t = 2$ |
|---|---|---|---|---|---|---|
| 0.25 | 47% | 40% | 29% | 3.0 × annual vol | 81% | 64 |
| 0.5 | 44% | 31% | 13% | 2.4 × | 64% | 16 |
| 0.75 | 41% | 23% | 4.7% | 2.1 × | 45% | 7.1 |
| 1.0 | 39% | 16% | 1.3% | 1.8 × | 27% | 4.0 |
| 1.5 | 33% | 6.7% | < 0.1% | 1.4 × | 7.5% | 1.8 |
| 2.0 | 28% | 2.3% | < 0.1% | 1.2 × | 1.7% | 1.0 |
| 3.0 | 19% | 0.1% | < 0.1% | 0.9 × | 0.1% | 0.4 |

The chance of losing money over a period of $\tau$ years is $\Phi(-\mathrm{SR}\sqrt{\tau})$. The last column is $4/\mathrm{SR}^2$ (§3.6). Drawdowns are in units of annual volatility, so "2 vol" means twice the annual volatility. They are measured on log wealth, from 4,000 simulated ten-year daily paths.

Three readings of the table are worth remembering.

- **Sharpe ratios below one are mostly noise at any horizon an investor watches.** A Sharpe-0.5 strategy loses money in almost a third of calendar years, and in one five-year stretch out of eight.
- **Large drawdowns are normal.** Take a Sharpe-0.5 strategy run at 10% volatility. Its expected worst drawdown in a decade is about 24% in log terms, roughly a fifth of peak wealth. It has a two-in-three chance of exceeding 20% in log terms, which is 18% of peak wealth. A rule that fires a manager at a drawdown of that size fires most good Sharpe-0.5 managers within 10 years. Real returns have fatter tails than these simulated ones, so real drawdowns are worse.
- **The last column is the hardest to accept.** It gives the years needed to prove the edge, and it is the subject of §3.6.

## 2.6 From signal-to-noise to information

Communication theory gives signal-to-noise ratios a natural unit. [Shannon (1948)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf){target="_blank"} showed that a channel that adds Gaussian noise to a signal, at signal-to-noise ratio $\mathrm{SNR}$, can carry at most

$$
C \;=\; \tfrac12 \log_2\!\left(1 + \mathrm{SNR}\right) \ \text{bits per use}.
$$

This is the capacity of the Gaussian channel. The Shannon–Hartley formula restates it per second (Appendix A.6). Now treat the forecast as a message the market sends about next period's return, with the noise of §2.2. Substituting $\mathrm{SNR} = \mathrm{IC}^2/(1-\mathrm{IC}^2)$, so that $1 + \mathrm{SNR} = 1/(1-\mathrm{IC}^2)$, gives

$$
C \;=\; -\tfrac12 \log_2\!\left(1 - \mathrm{IC}^2\right) \;\approx\; \frac{\mathrm{IC}^2}{2\ln 2}\ \text{bits} \;=\; \frac{\mathrm{IC}^2}{2}\ \text{nats}.
$$

A normally distributed input is the one that achieves this capacity. So the exact expression is also the **mutual information** between a forecast and an outcome that are jointly normal with correlation $\mathrm{IC}$ (Appendix A.4). Mutual information is the amount by which knowing the forecast reduces uncertainty about the outcome. The signal-to-noise view and the information view are therefore one view in two units. The square comes from the conversion between them: a ratio is an amplitude, and its square is information.

> ### §2 Key takeaways
>
> 1. Every core ratio is a signal-to-noise ratio: a systematic part divided by a random part, measured in units of noise.
> 2. An IC is a signal fraction. At 0.05, the signal carries 0.25% of the variance. It is invisible bet by bet and shows up only in averages.
> 3. An IC is hard to measure. From $n$ independent bets its standard error is about $1/\sqrt{n}$, so 3,000 bets pin it down only to $\pm 0.04$.
> 4. The square-root law says that signal grows with $n$ and noise with $\sqrt{n}$. It produces both the $\sqrt{12}$ of annualisation and the $\sqrt{\mathrm{BR}}$ of the fundamental law.
> 5. The law fails when noise is shared. A 0.01 correlation among surprises cuts 500 bets to 84. An autocorrelation of 0.2 makes $\sqrt{12}$ overstate a Sharpe ratio by 20%. Variation in the IC over time sets a ceiling that breadth cannot lift.
> 6. A strategy with a Sharpe ratio of 1 loses money on 47.5% of days and 16% of years. A strategy with a Sharpe ratio of 0.5 has a two-in-three chance of a drawdown above twice its annual volatility within a decade.
> 7. Shannon's capacity formula, applied to a forecast, turns a signal-to-noise ratio into information: about $\mathrm{IC}^2/2$ nats per bet.

```{=latex}
\newpage
```

# 3. Edge as information {#3-edge-as-information}

## 3.1 What information means here

Information, in Shannon's sense, is a reduction of uncertainty. It is measured by the number of yes-or-no questions it would settle. Learning the outcome of a fair coin toss is one **bit**. Learning which of eight equally likely outcomes occurred is three bits. A message that changes the odds without settling anything carries a fraction of a bit. The uncertainty of a random outcome before any message arrives is its **entropy**. The information a forecast carries about an outcome, its mutual information, is the fall in the outcome's entropy once the forecast is known (Appendix A.1 to A.3).

§2.6 gave the amount for a forecast and outcome that are jointly normal with correlation $\mathrm{IC}$: $-\tfrac12\log_2(1-\mathrm{IC}^2)$ bits per bet, close to $\mathrm{IC}^2/2$ nats. The table puts this in numbers.

| IC | 0.01 | 0.02 | 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|---|
| Bits per bet | 0.00007 | 0.0003 | 0.0018 | 0.0073 | 0.029 |
| Bets needed to learn one bit | 13,900 | 3,500 | 550 | 140 | 34 |

The table gives the clearest description of active management. A good signal reveals roughly a five-hundredth of a coin toss about each bet. The business is to collect those fractions of a bit thousands of times a year, at the lowest possible cost. Everything in §3.3 and §3.5 follows from taking that description literally.

One difference between the two measures matters later. Mutual information counts any dependence between forecast and outcome, linear or not. The IC counts only the linear part. For jointly normal variables the two agree. For a forecast whose payoff lies in the tails, or that works only for large signals, the IC understates what the forecast knows (§7.5).

## 3.2 Kelly: money grows at the rate information arrives

In 1956 John Kelly, a physicist at Bell Labs, asked what a private wire is worth to a gambler who receives tips on horse races over it. The wire is noisy, so the tips are sometimes wrong. His answer appeared in a paper titled *A New Interpretation of Information Rate* ([Kelly, 1956](https://www.princeton.edu/~wbialek/rome/refs/kelly_56.pdf){target="_blank"}). It connects information theory to money: **if the odds are fair, the fastest rate at which a gambler's wealth can grow is exactly the rate at which the wire carries information about the race.**

A two-horse race makes the result concrete. The horses are equally matched, each pays 2-for-1, which is fair, and the wire names the winner correctly 60% of the time. The growth-optimal gambler bets 60% of their wealth on the tipped horse and 40% on the other. When the tip is right, wealth multiplies by $0.6 \times 2 = 1.2$. When it is wrong, wealth multiplies by $0.8$. The expected growth of log wealth per race is

$$
0.6\log_2 1.2 + 0.4 \log_2 0.8 \;=\; 0.029 \ \text{bits}.
$$

The mutual information between tip and winner is $1 - H(0.6) = 0.029$ bits, where $H(0.6)$ is the entropy of a 60–40 coin. The two numbers are equal, and the identity is exact (Appendix A.10). Each bit of information doubles wealth. A gambler who receives 0.029 bits a race doubles their money every 34 races.

Markets are not horse races, but the identity survives to leading order. Take a strategy with Sharpe ratio $\mathrm{SR}$, rebalanced continuously at the growth-optimal leverage. Its log wealth outgrows cash at the rate

$$
g^\ast \;=\; \frac{\mathrm{SR}^2}{2} \ \text{per year}.
$$

[Simple and Log Returns](log_returns.html) derives this rate. The same calculation can be run bet by bet. Take a forecast with correlation $\mathrm{IC}$ to a zero-mean, normally distributed return, both standardised. Given the forecast $s$, the return has mean $\mathrm{IC}\cdot s$ and variance $1-\mathrm{IC}^2$ (§2.2). So that bet's Sharpe ratio is $\mathrm{IC}\cdot s/\sqrt{1-\mathrm{IC}^2}$. Sizing each bet at its growth-optimal leverage earns half that ratio squared. Averaging over forecasts, where the mean of $s^2$ is one, gives $\mathrm{IC}^2/(2(1-\mathrm{IC}^2))$ nats per bet. The table compares this growth with the mutual information $-\tfrac12\ln(1-\mathrm{IC}^2)$.

| IC | 0.05 | 0.10 | 0.20 | 0.30 | 0.50 |
|---|---|---|---|---|---|
| Growth ÷ information | 1.001 | 1.005 | 1.021 | 1.049 | 1.159 |

For every IC a practitioner will meet, growth and information agree to within a fraction of a percent. The small excess at large ICs is an artefact. The formula $\mathrm{SR}^2/2$ rests on a quadratic approximation to log growth, and that approximation overstates growth when a single bet's Sharpe ratio, given its forecast, is large. For general markets, [Barron & Cover (1988)](https://doi.org/10.1109/18.21241){target="_blank"} proved an inequality that needs no distributional assumption: side information can raise the growth rate of wealth by at most its mutual information with the market. A bit can at most double an investor's money.

Converted into information, the Sharpe ratios that practitioners discuss are small amounts:

| Annual Sharpe | 0.5 | 1.0 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|
| Nats a year, $\mathrm{SR}^2/2$ | 0.125 | 0.50 | 1.13 | 2.0 | 4.5 |
| Bits a year | 0.18 | 0.72 | 1.6 | 2.9 | 6.5 |

A Sharpe ratio of one is the level that gets a strategy funded. Such a strategy learns less than one bit about the market each year. This is not a paradox. It is the reason edges are hard to find, easy to lose, and slow to prove.

This chapter uses Kelly's growth-optimal bet as a yardstick, not as a recommendation. Whether anyone should actually maximise expected log wealth is a separate and contested question ([Samuelson, 1971](https://finance.martinsewell.com/money-management/Samuelson1971.pdf){target="_blank"}). §6.6 covers what practitioners do instead.

## 3.3 Squares add: the fundamental law as bookkeeping

Square both sides of the fundamental law and halve them:

$$
\underbrace{\frac{\mathrm{IR}^2}{2}}_{\text{information per year}} \;=\; \mathrm{BR} \;\times\; \underbrace{\frac{\mathrm{IC}^2}{2}}_{\text{information per bet}} .
$$

Read this way, the law is an accounting identity: a year of independent bets carries the sum of what each bet carries. The square root in $\mathrm{IC}\sqrt{\mathrm{BR}}$ appears only because the bookkeeping is done in squares and reported as a ratio. The table applies the identity to four cases.

| IC | Bets a year | IR | Nats a year | Years to $t = 2$ |
|---|---|---|---|---|
| 0.05 | 12 (one market, monthly) | 0.17 | 0.015 | 133 |
| 0.05 | 600 (50 markets, monthly) | 1.22 | 0.75 | 2.7 |
| 0.05 | 6,000 (500 independent stocks, monthly) | 3.87 | 7.5 | 0.3 |
| 0.10 | 250 (one market, daily) | 1.58 | 1.25 | 1.6 |

The first row is a market timer with a good signal. Its Sharpe ratio is too small to confirm in a lifetime. The third row shows what the same skill would earn if 500 stocks really were 500 independent bets, which they are not (§2.4, §7.1). The law is exact bookkeeping. The hard part is counting the bets.

The same rule governs every combination of independent sources of edge.

**Strategies.** Take a set of uncorrelated strategies, with risk allocated to each in proportion to its Sharpe ratio. The best such mix has a squared Sharpe ratio equal to the sum of the individual squared Sharpe ratios (§6.6). The reason is one line of mean-variance algebra. Let the strategies have mean excess returns $\mu$ (a vector) and covariance matrix $\Sigma$. The best attainable squared Sharpe ratio is $\mu^{\top}\Sigma^{-1}\mu$. When $\Sigma$ is diagonal, that equals $\sum_i \mu_i^2/\sigma_i^2 = \sum_i \mathrm{SR}_i^2$ (Appendix B.40). Two uncorrelated strategies with Sharpe ratio 0.5 combine to 0.71, and three combine to 0.87. For $n$ strategies of equal Sharpe ratio with pairwise correlation $\rho$, the combination's Sharpe ratio is $\mathrm{SR}\sqrt{n/(1+(n-1)\rho)}$. However many strategies are added, it can never exceed $\mathrm{SR}/\sqrt{\rho}$:

| Ten strategies of Sharpe 0.5, pairwise correlation | 0 | 0.1 | 0.3 | 0.5 |
|---|---|---|---|---|
| Combined Sharpe | 1.58 | 1.15 | 0.82 | 0.67 |

**Active bets on a benchmark.** [Treynor & Black (1973)](https://doi.org/10.1086/295508){target="_blank"} added active positions to a benchmark portfolio. Their model takes the residual returns of the active positions to be uncorrelated. They showed that the best achievable squared Sharpe ratio equals the benchmark's squared Sharpe ratio plus the sum of the squared **appraisal ratios** of the active positions. An appraisal ratio is residual return over residual risk. So information from security analysis adds to the market's.

**Timing.** [Campbell & Thompson (2008)](https://www.nber.org/papers/w11468){target="_blank"} considered a forecast of the market with predictive $R^2$. They showed that it lets an investor raise the Sharpe ratio $\mathrm{SR}$ of a buy-and-hold position to $\sqrt{(\mathrm{SR}^2 + R^2)/(1-R^2)}$, with the Sharpe ratio and $R^2$ both measured per period. Consider a market whose annual Sharpe ratio is 0.4, or 0.115 a month. Timing it with a monthly $R^2$ of 1% raises the annual Sharpe ratio to 0.53. An $R^2$ of 0.25% raises it to 0.44. An $R^2$ that any econometrics course would call negligible is worth a third more Sharpe ratio. Setting the market's own Sharpe ratio to zero recovers the fundamental law. The formula then gives $R/\sqrt{1-R^2}$, which is close to $R$, the timing forecast's IC. Each period is one bet with a Sharpe ratio of about the IC, so 12 bets a year give $\mathrm{IC}\sqrt{12}$, the fundamental law with a breadth of 12.

The bookkeeping has three working consequences.

- **Price improvements in squares.** Raising an IC by 10% raises information by 21%, and so does raising the transfer coefficient by 10%. Raising breadth by 10% raises information by only 10%. Effort should go wherever it buys the most squared ratio, and that is often the transfer coefficient (§6.5).
- **A second strategy beats a better first one.** Adding an uncorrelated Sharpe-0.5 strategy to an existing Sharpe-0.5 strategy lifts the total to 0.71. That equals a 41% improvement in the first strategy's Sharpe ratio, and the second strategy is usually far easier to find.
- **The correlation of the noise is what matters.** The combination formula depends on the correlation of the strategies' returns, and their noise dominates that correlation. Two strategies built on different ideas but exposed to the same factor count, for this purpose, as one strategy.

## 3.4 Redundancy: correlated signals carry overlapping information

When two signals are correlated, part of what one knows the other already knew. Take two standardised signals with ICs $a$ and $b$ and correlation $\rho$ between them. Their best linear combination has

$$
\mathrm{IC}_{\text{combined}}^2 \;=\; \frac{a^2 + b^2 - 2\rho\, a b}{1-\rho^2}.
$$

The table evaluates the formula for seven pairs of signals.

| IC of signal 1 | IC of signal 2 | Correlation between signals | Combined IC | Weight on signal 2, per unit of signal 1 |
|---|---|---|---|---|
| 0.04 | 0.04 | 0 | 0.057 | +1.0 |
| 0.04 | 0.04 | 0.3 | 0.050 | +1.0 |
| 0.04 | 0.04 | 0.5 | 0.046 | +1.0 |
| 0.04 | 0.04 | 0.8 | 0.042 | +1.0 |
| 0.04 | 0.02 | 0.5 | 0.040 | 0 |
| 0.04 | 0 | 0.5 | 0.046 | −0.5 |
| 0.04 | 0 | 0.8 | 0.067 | −0.8 |

The first four rows match intuition. Two equally good signals help less the more they overlap. At a correlation of 0.8, the second signal adds only 5%. The fifth row is a trap. A signal with half the IC of the first, correlated 0.5 with it, adds nothing at all. Everything it knows about returns, it knows through the first signal.

The last two rows are less intuitive. A signal with **no** predictive power of its own, but correlated with the first, raises the combined IC. At a correlation of 0.8 it raises the IC by two thirds. The second signal works by measuring part of the first signal's noise, so subtracting it leaves a cleaner forecast. Neutralising a signal against its industry, size or market beta works this way. Suppose a value signal is partly a bet on which sectors are cheap, and sector membership carries noise but little information about next month's relative returns. Then removing the sector component raises the IC. This does not contradict §3.5, because the second signal is a new input. Information about the noise is still information.

## 3.5 Information only leaks

Suppose the positions are connected to the outcome only through the forecast. The portfolio is built from the forecast plus constraints, costs and noise, none of which know anything more about the future. Then the positions cannot carry more information about the outcome than the forecast did. This is the **data-processing inequality** (Appendix A.7). It formalises a lesson practitioners learn from experience: nothing done to a signal after it is formed makes it smarter.

The **transfer coefficient** measures one leak exactly. [Clarke, de Silva & Thorley (2002)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=290916){target="_blank"} showed that the fundamental law becomes

$$
\mathrm{IR} \;=\; \mathrm{TC} \times \mathrm{IC} \times \sqrt{\mathrm{BR}}
\qquad\Longrightarrow\qquad
\mathrm{IR}^2 \;=\; \mathrm{TC}^2 \times \mathrm{IC}^2 \times \mathrm{BR},
$$

where $\mathrm{TC}$ is the correlation between the risk-adjusted positions the forecasts call for and the positions actually held. In squares, $\mathrm{TC}^2$ is the share of the forecast's information that survives into the portfolio:

| Transfer coefficient | 1.0 | 0.9 | 0.8 | 0.6 | 0.5 | 0.4 | 0.3 |
|---|---|---|---|---|---|---|---|
| Information kept | 100% | 81% | 64% | 36% | 25% | 16% | 9% |

[Practice] Constrained portfolios commonly run transfer coefficients between about 0.3 and 0.9. [Clarke, de Silva & Thorley (2002)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=290916){target="_blank"} find that the long-only constraint lowers the TC more than any other single restriction. A long-only manager with a TC of 0.4 discards five sixths of their information before making a single trade.

The other leaks work the same way.

- **Delay.** Forecasts decay. Suppose a signal's IC halves every $h$ days. A delay of $d$ days between forecast and trade multiplies the IC by $2^{-d/h}$, and the information by the square of that factor. A one-day delay on a signal with a five-day half-life keeps 87% of the IC and 76% of the information.
- **Estimation error.** The alphas fed to the optimiser are estimates. Error in them makes the portfolio partly a bet on the error, which carries no information about returns. [Zhou (2008)](https://www.pm-research.com/content/iijpormgmt/34/4/26){target="_blank"} shows that, left unchecked, estimation error can destroy most of what the fundamental law promises.
- **Risk model error.** A misestimated covariance matrix tilts the portfolio toward bets that look diversifying and are not. This is another way of overcounting breadth.
- **Costs and turnover limits.** Strictly, costs are deductions rather than lost information. A turnover limit, however, acts like a delay. The portfolio trails the forecast, and the gap between them is information not acted on.

## 3.6 One number, three meanings: growth, evidence, proof

Compare two hypotheses about a strategy's annual returns. Under the first, the strategy has skill, and its returns are distributed as $\mathcal{N}(\mu, \sigma^2)$. Under the second, it has none, and its returns are $\mathcal{N}(0, \sigma^2)$. The relative entropy between the two hypotheses is the expected log-likelihood ratio in favour of skill that one year of returns provides when skill is real. It equals (Appendix A.5)

$$
D\big(\mathcal{N}(\mu,\sigma^2)\,\big\|\,\mathcal{N}(0,\sigma^2)\big) \;=\; \frac{\mu^2}{2\sigma^2} \;=\; \frac{\mathrm{SR}^2}{2} \ \text{nats per year}.
$$

This is the same number as the Kelly growth rate of §3.2. One quantity, half the squared Sharpe ratio, measures three different things:

1. **Growth.** How fast a growth-optimal investor's log wealth outgrows cash.
2. **Information.** How much the strategy learns about the market each year.
3. **Evidence.** How fast an observer of the returns becomes convinced that the skill is real.

The third meaning is the practical one, because it converts directly into time. After $T$ years, the expected evidence is $T\,\mathrm{SR}^2/2$ nats. The t-statistic of the mean return is $t = \mathrm{SR}\sqrt{T}$, so the evidence is $t^2/2$, half the squared t-statistic. The conventional bar of $t = 2$ corresponds to 2 nats of evidence, a likelihood ratio of $e^2 \approx 7.4$ in favour of skill. A strategy reaches it after

$$
T \;=\; \frac{4}{\mathrm{SR}^2} \ \text{years}.
$$

This is when the *expected* t-statistic reaches two. The measured t-statistic scatters around it with a standard deviation of about one. So a strategy observed for exactly that long clears the bar only about half the time. To clear it four times in five, the expected t-statistic must be about 2.8. That takes $7.8/\mathrm{SR}^2$ years: nearly eight years at a Sharpe ratio of one, and 31 at a half (Appendix B.13).

The figure shows the same facts in two forms.

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/ei_track_record.pdf}
\end{center}
```

```{=html}
<img class="mdd-fig" src="quant-research/figures/ei_track_record.svg"
     alt="Left: the 95% range of a measured Sharpe ratio narrowing with track-record length for true Sharpe 0.5 and 1.0. Right: years needed for the t-statistic to clear a significance bar, against true Sharpe ratio, for 1, 10, 100 and 1,000 strategies tried">
```

The left panel shows the result as a confidence band. Measured from daily or monthly data, the standard error of an annualised Sharpe ratio is close to $1/\sqrt{T}$, almost whatever the true value. A Sharpe ratio of 1.0 measured over 10 years has a 95% range of 0.38 to 1.62. A Sharpe ratio of 0.5 over 10 years cannot be distinguished from zero. The ranges produced by 10 years of a true Sharpe ratio of 1.0 and 10 years of a true 0.5 overlap over most of their width.

The right panel adds the cost of searching. Suppose a researcher tried $K$ strategies and kept the best one. That strategy has to clear a higher bar, because the best of $K$ lucky draws looks better than any single draw. The simplest correction is Bonferroni's: test each of the $K$ strategies at a significance level of 5% divided by $K$, which holds the chance of any false discovery at 5%. Under that correction, the bar and the evidence it demands rise as follows:

| Strategies tried, $K$ | 1 | 10 | 100 | 1,000 | 10,000 |
|---|---|---|---|---|---|
| Bar for the t-statistic | 1.96 | 2.81 | 3.48 | 4.06 | 4.56 |
| Evidence needed, nats | 1.9 | 3.9 | 6.1 | 8.2 | 10.4 |
| Years at Sharpe 1.0 | 3.8 | 7.9 | 12.1 | 16.4 | 20.8 |

Each tenfold increase in the search adds a little over 2 nats to the evidence required, close to $\ln 10 = 2.3$. For large $K$, the evidence demanded grows like $\ln K$. Doubling the search therefore adds about $\ln 2$ nats, which is one bit. So beyond the first few trials, **each doubling of the search costs about one bit of evidence**. At a Sharpe ratio of one, evidence arrives at half a nat a year, so one bit, 0.69 nats, takes 1.4 years to collect. In the information view, the multiple-testing penalty is a debt in the same currency as the edge, and it is paid in years.

The identity has one more reading. In the normal model, a growth-optimal investor who knows $\mu$ and $\sigma$ holds leverage $f^\ast = \mu/\sigma^2$. Each return $r$ then changes their log wealth relative to cash by $f^\ast r - \tfrac12 (f^\ast)^2\sigma^2 = \mu r/\sigma^2 - \mu^2/(2\sigma^2)$ (Appendix A.11). The same return provides a log-likelihood ratio for "skill" against "no skill" equal to the log of the ratio of the two normal densities, $\big(r^2 - (r-\mu)^2\big)/(2\sigma^2)$. That expands to the same expression. Return by return, a Kelly investor's log wealth is a running tally of the evidence for their own edge.

## 3.7 Same name, different thing

Several communities built the vocabulary of this field without coordinating. The table lists the name collisions that cause real errors.

| Term | Meaning A | Meaning B | Why it matters |
|---|---|---|---|
| Information ratio | Residual return over residual risk, after removing the benchmark's beta (Grinold and Kahn) | Active return (portfolio minus benchmark) over tracking error, with no beta adjustment (common in consultants' reports) | A high-beta fund in a rising market has a high B and an unremarkable A |
| Appraisal ratio | Treynor and Black's residual return over residual risk for one security | Used interchangeably with meaning A of the information ratio | Same idea at different levels: one security, or the whole portfolio |
| Information coefficient | Cross-sectional correlation each period, then averaged | Time-series correlation of one asset's forecast and return | The cross-sectional version is what the fundamental law uses |
| IC (Pearson vs rank) | Correlation of raw forecasts and returns | Correlation of their ranks (Spearman) | Rank IC is robust to outliers; it is the usual report |
| Information | Shannon's information, measured in bits or nats | Informal "information" in "information ratio" and "information coefficient" | The names predate the connection; the connection is real, the naming is coincidence |
| Capacity | The maximum information rate of a channel (Shannon) | The amount of capital a strategy can run before costs erase its edge | Unrelated, though both are limits on how much edge can be extracted |
| Breadth | Number of assets in the universe | Number of independent bets per year | Only the second goes into the fundamental law |
| Sharpe ratio | Ex ante: expected excess return over expected volatility | Ex post: sample mean over sample standard deviation | The second is a noisy estimate of the first, with standard error near $1/\sqrt{T}$ |

> ### §3 Key takeaways
>
> 1. A forecast with an IC of 0.05 carries about 0.0018 bits per bet, or some 550 bets per bit. Active management is the business of collecting tiny fractions of a bit many times over.
> 2. With fair odds, wealth grows at exactly the rate information arrives (Kelly). In markets the identity holds to leading order: $g^\ast = \mathrm{SR}^2/2$, and a bit can at most double wealth.
> 3. A Sharpe ratio of one corresponds to less than one bit of information a year.
> 4. The fundamental law is bookkeeping in squares: information per year equals breadth times information per bet. Squared Sharpe ratios of uncorrelated strategies add for the same reason.
> 5. Correlated signals overlap. A weaker signal correlated with a stronger one can add nothing. A signal with no IC of its own can add a great deal if it measures the first signal's noise.
> 6. Information only leaks. $\mathrm{TC}^2$ is the share of a forecast's information that survives portfolio construction, and a long-only TC of 0.4 keeps 16%.
> 7. $\mathrm{SR}^2/2$ is also the evidence per year for skill. Proving an edge at $t = 2$ therefore takes $4/\mathrm{SR}^2$ years, and each doubling of the number of strategies tried costs about one more bit of evidence.

```{=latex}
\newpage
```

# 4. The core ratios, one at a time {#4-the-core-ratios}

Each ratio gets the same six fields, in the same order, so the ratios can be compared directly. The fields are the **intuition**, the **definition**, how the ratio is computed **in practice**, **what good looks like**, its **failure modes**, and **when to use** it. §4.8 closes with a comparison table.

## 4.1 The Sharpe ratio

**Intuition.** The Sharpe ratio is return per unit of total risk, measured against cash. It uses returns in excess of cash, so it does not change when a position is levered up or down: doubling the position doubles both the excess return and its volatility. This makes it the natural yardstick for strategies that will be scaled to a common risk level ([Sharpe, 1966](http://www.stat.ucla.edu/~nchristo/statistics_c183_c283/sharpe__mutual_fund_performance.pdf){target="_blank"}; [Sharpe, 1994](https://web.stanford.edu/~wfsharpe/art/sr/sr.htm){target="_blank"}).

**Definition.** $\mathrm{SR} = \mathbb{E}[r]/\sigma(r)$ for excess returns $r$. The sample version divides the sample mean by the sample standard deviation. When returns are independent over time, it is annualised by multiplying by $\sqrt{q}$.

**In practice.**

- Use the **arithmetic** mean of excess returns, over a period short enough that compounding within it does not matter. For a levered strategy, the "cash" rate is the rate at which the leverage is actually financed.
- Check the autocorrelation of returns before multiplying by $\sqrt{q}$. If it is material, use Lo's multiplier (§2.4).
- Report a standard error. For independent normal returns, the per-period Sharpe ratio estimated from $n$ periods has a standard error close to $\sqrt{(1 + \mathrm{SR}_{\text{per period}}^2/2)/n}$ ([Lo, 2002](https://doi.org/10.2469/faj.v58.n4.2453){target="_blank"}; Appendix A.9 derives it). Annualising multiplies it by $\sqrt{q}$. With $n = qT$ periods in $T$ years, the result is close to $1/\sqrt{T}$, because the per-period Sharpe ratio of monthly or daily data is too small for its square to matter.
- Allow for skew and fat tails. With skewness $\gamma_3$ and kurtosis $\gamma_4$ (3 for a normal distribution), the variance of the per-period estimate becomes $\big(1 - \gamma_3\,\mathrm{SR}_{\text{per period}} + \tfrac{\gamma_4 - 1}{4}\,\mathrm{SR}_{\text{per period}}^2\big)/n$ ([Opdyke, 2007](https://doi.org/10.1057/palgrave.jam.2250084){target="_blank"}). This reduces to the normal case at $\gamma_3 = 0$, $\gamma_4 = 3$. Negative skew widens the error bars on a positive Sharpe ratio. The correction matters for monthly data with strong skew and is negligible for daily data.

**What good looks like.** [Practice] The rough anchors below are all before fees, and all vary by period:

- a broad equity market: about 0.3 to 0.4 over the long run;
- a single well-known factor, such as value, momentum or carry: about 0.3 to 0.6;
- diversified trend-following: about 0.5 to 0.8 over long histories;
- a multi-strategy platform's target: well above 1;
- market making in its niche: far above 2, at a capacity measured in millions rather than billions.

A backtest above 2 on daily or slower data deserves suspicion before celebration (§7.4).

**Failure modes.** The Sharpe ratio treats upside and downside volatility alike, so it misses skew. Strategies that sell insurance show high Sharpe ratios until the event they are paid to bear (§5.3). Smoothed returns inflate it (§7.3). It assumes leverage is available at the cash rate, which is false for an individual or a constrained fund. It is a single number estimated with an error near $1/\sqrt{T}$. After a search across variants, it is biased upward (§4.7).

**When to use it.** Use it to compare strategies or funds that will be held standalone or levered to a common risk, to size positions (§6.6), and to combine uncorrelated strategies (§3.3).

## 4.2 The information ratio, and the appraisal ratio

**Intuition.** The information ratio is the Sharpe ratio of the bet against a benchmark. It measures how much return a manager adds per unit of risk taken by departing from the benchmark.

**Definition.** Regress the strategy's excess returns on the benchmark's excess returns $r_{B,t}$: $r_t = \alpha + \beta\, r_{B,t} + \varepsilon_t$. Here $\beta$ is the strategy's sensitivity to the benchmark and $\varepsilon_t$ is its residual return in period $t$. The residual risk is $\omega = \sigma(\varepsilon)$, and $\mathrm{IR} = \alpha/\omega$, annualised. This is the Grinold–Kahn definition, and the fundamental law uses it. The common alternative divides the mean active return, portfolio minus benchmark, by its standard deviation. Active return equals $\alpha + (\beta - 1)\,r_{B,t} + \varepsilon_t$, so the two definitions agree only when $\beta = 1$ (§3.7). Both denominators go by the name tracking error. Treynor and Black's **appraisal ratio** is the same residual quantity for a single security.

**In practice.** Use the benchmark the manager is actually paid against. If the question is skill beyond known factors, use a factor model instead. Report the IR with its t-statistic, $\mathrm{IR}\sqrt{T}$, since the two are the same estimate seen two ways. [Goodwin (1998)](https://doi.org/10.2469/faj.v54.n4.2196){target="_blank"} makes this point and compares the ways of annualising the IR. For a market-neutral strategy, the information ratio and the Sharpe ratio are nearly the same number.

**What good looks like.** [Practice] Grinold and Kahn's rule of thumb is that an IR of 0.5 is good, 0.75 very good and 1.0 exceptional. A top-quartile manager sits around 0.5 before fees. Studies of realised IRs over long windows find these levels harder to sustain than the rule suggests. Few long-only managers keep an IR above 0.5 over 10 years (Goodwin, 1998, reports distributions by style).

**Failure modes.** A misspecified benchmark turns a style tilt into apparent alpha. A small-cap fund measured against a large-cap index, for example, reports the small-cap premium as skill. Using active return without the beta adjustment rewards high-beta funds in rising markets. A very small tracking error makes the ratio fragile, because fees and small mismatches with the benchmark are then large relative to the denominator. Finally, like the Sharpe ratio, the IR is scale-free: it is the same at any level of active risk. On its own, it cannot say how much active risk to take. That decision also needs an aversion to active risk, and the answer is then proportional to the IR (§6.6).

**When to use it.** Use it to judge skill relative to a mandate and to allocate active-risk budgets across managers (§6.6).

## 4.3 The information coefficient

**Intuition.** The information coefficient is the correlation between a forecast and what followed, bet by bet. It scores a signal before any portfolio is built, which makes it the researcher's measure. [Ambachtsheer (1974)](https://doi.org/10.3905/jpm.1974.408485){target="_blank"} was an early user, describing forecasting skill with it.

**Definition.** For a cross-sectional signal, compute $\mathrm{IC}_t = \operatorname{Corr}_i\big(s_{i,t},\, y_{i,t+1}\big)$ across assets $i$ in each period $t$. The **rank IC** uses ranks instead of raw values, which makes it a Spearman correlation. The summary statistics are:

- the mean $\overline{\mathrm{IC}}$;
- the standard deviation of the measured series, $\hat\sigma_{\mathrm{IC}}$;
- the **IC information ratio**, $\overline{\mathrm{IC}}/\hat\sigma_{\mathrm{IC}}$;
- its t-statistic, which is the IC information ratio times the square root of the number of periods.

**In practice.** §6.2 gives the full checklist. In short: use residual returns and point-in-time data, choose a forward window that matches the holding period, and prefer ranks to raw values. Examine the whole $\mathrm{IC}_t$ series rather than only its mean, and track how the IC decays as the forward window lengthens.

**What good looks like.** [Practice] Grinold and Kahn's calibration is that 0.05 is good, 0.10 great and 0.15 world class. Monthly cross-sectional ICs for published equity factors are mostly 0.02 to 0.05. An IC above 0.15 sustained on a large, liquid universe is more likely a bug or a look-ahead than a discovery. The IC information ratio matters as much as the mean. A signal with mean 0.03 and standard deviation 0.05 is far better than one with mean 0.05 and standard deviation 0.20 (§7.1).

**Failure modes.**

- Look-ahead in the data.
- A universe padded with small, illiquid stocks, where the signal works on paper and cannot be traded.
- Outliers that drive a Pearson IC.
- Raw returns that let factor exposure pass for skill.
- Overlapping forward windows that inflate the t-statistic.
- A mean that hides how unreliable the signal is from month to month.

**When to use it.** Use it for signal research and comparison before portfolio construction, and to monitor the health of a live signal.

## 4.4 Breadth

**Intuition.** Breadth is the number of independent bets a strategy makes in a year. It is the $n$ of the square-root law.

**Definition.** Implicitly, breadth is the number that makes the fundamental law hold: $\mathrm{BR} = (\mathrm{IR}/\mathrm{IC})^2$, or $(\mathrm{IR}/(\mathrm{TC}\cdot\mathrm{IC}))^2$ once the transfer coefficient of §3.5 is counted. Explicitly, it is the number of assets times the number of independent forecast refreshes per year, discounted for the redundancy among them. For $N$ assets whose surprises have average correlation $\rho$, the divisor is the $1 + (N-1)\rho$ of §2.4. Breadth is not Meucci's entropy-based effective number of bets (Appendix A.12). That measure describes how evenly risk is spread, not how much information the bets carry.

**In practice.** Never count assets times rebalances. Count **independent** bets. Discount for correlation among the surprises (§2.4), for variation in the IC over time (§7.1), and for rebalances that bring no new information. Rebalancing a slow-moving signal daily makes 252 trades on one forecast, not 252 forecasts. [Buckle (2004)](https://link.springer.com/article/10.1057/palgrave.jam.2240118){target="_blank"} shows how correlation among forecasts enters the count. The most honest count works backwards from results: realised IR divided by the product of realised TC and IC, squared (§6.4).

**What good looks like.** [Practice] Implied breadth is usually one to two orders of magnitude below the naive count. The worked example of §1.4 applies only one of the discounts. Variation in the IC alone cuts 6,000 naive bets to about 1,400, before correlated surprises or slow-moving forecasts take their share.

**Failure modes.** Overcounting is the failure, and every mechanism above causes it. Counting assets on which the signal has no skill also inflates breadth. A bet with zero IC adds one to the count and nothing to the information.

**When to use it.** Use it for planning: choosing between a wider universe, faster trading and a better signal. Use it also to explain why a strategy's realised IR fell short of its promise.

## 4.5 The transfer coefficient

**Intuition.** The transfer coefficient measures how faithfully the portfolio expresses the forecasts.

**Definition.** The TC is the cross-sectional correlation between the risk-adjusted active positions the forecasts call for and the positions actually held ([Clarke, de Silva & Thorley, 2002](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=290916){target="_blank"}). With a diagonal risk model, it is the correlation across assets between two quantities:

- $\Delta w_i\,\sigma_i$: the active weight (portfolio weight minus benchmark weight) times the asset's residual volatility;
- $\alpha_i/\sigma_i$: the forecast alpha per unit of volatility, where $\alpha_i$ is the asset's expected residual return (§6.1).

The unconstrained mean-variance portfolio holds $\Delta w_i \propto \alpha_i/\sigma_i^2$. That makes the two quantities proportional and the TC exactly one. Constraints are what pull it below one. The later version, [Clarke, de Silva & Thorley (2006)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=934440){target="_blank"}, handles a full covariance matrix and makes $\mathrm{IR} = \mathrm{TC} \times \mathrm{IC} \times \sqrt{\mathrm{BR}}$ exact.

**In practice.** Compute the TC at each rebalance from the optimiser's unconstrained and constrained solutions, and track it over time. Its square is the share of the forecast's information that the portfolio keeps (§3.5).

**What good looks like.** [Practice] An unconstrained portfolio has a TC of 1. A long-short portfolio with ordinary position and factor limits typically runs 0.7 to 0.9. Long-only portfolios commonly sit between 0.3 and 0.6. The long-only constraint costs more than any other single restriction.

**Failure modes.** A high TC is only as good as the forecasts: expressing a wrong alpha perfectly means expressing an error perfectly. The TC ignores costs, so a portfolio can score well by trading too much. And the TC is measured against the model's idea of the ideal portfolio, so a bad risk model can make a poor portfolio look faithful.

**When to use it.** Use it to design constraints, to choose between long-only, extension (130/30) and long-short structures, and to diagnose why a good IC produced a poor IR.

## 4.6 Hit rate and payoff ratio

**Intuition.** The hit rate says how often a strategy is right. The payoff ratio compares what it makes when right with what it loses when wrong.

**Definition.** The hit rate $p$ is the share of bets with positive P&L. The payoff ratio $b$ is the average winning bet divided by the size of the average losing bet. The expected P&L per bet, in units of the average loss, is $p\,b - (1-p)$. It is zero at $p = 1/(1+b)$. So a strategy whose wins average twice its losses breaks even at a hit rate of one in three. Once $b$ is free, any hit rate is compatible with any edge. For jointly normal forecasts and outcomes, the arcsine rule of §2.2 links hit rate and IC.

**In practice.** [Practice] Trend-following strategies typically win on a minority of trades, often 35% to 45%, with average wins two or more times the average loss. Mean-reversion and liquidity-providing strategies show the opposite shape: high hit rates, small wins and occasional large losses.

**What good looks like.** No hit rate is good in isolation. What matters is the pair of numbers, and whether it matches the strategy's stated logic.

**Failure modes.** [Practice] A high hit rate is often the signature of a short tail position: selling insurance that pays a little most of the time. The Sharpe ratio misses the same case. Hit rates count trades rather than dollars, so a strategy can be right on most trades and still lose on the few large ones.

**When to use it.** Use it to diagnose the shape of a payoff, to check that the P&L is consistent with the IC, and to explain a strategy to someone who will not read a Sharpe ratio.

## 4.7 The t-statistic, and its corrected cousins

**Intuition.** The t-statistic measures how much evidence the track record provides that the mean return is not zero. In the units of §3.6, half its square is the evidence in nats.

**Definition.** $t = \mathrm{SR}\sqrt{T}$ for an annual Sharpe ratio over $T$ years. The t-statistic has two known blind spots, non-normality and selection, and three refinements correct for them:

- The **probabilistic Sharpe ratio** (PSR) is the probability that the true Sharpe ratio exceeds a benchmark level $\mathrm{SR}_0$. It uses the non-normal standard error of §4.1. Solving it for the number of observations instead gives the **minimum track-record length**: the number of observations needed for the PSR to reach a chosen confidence ([Bailey & López de Prado, 2012](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643){target="_blank"}).
- The **deflated Sharpe ratio** (DSR) sets $\mathrm{SR}_0$ to the Sharpe ratio that the best of $K$ skill-less trials would be expected to show. It therefore asks whether the winner beat what luck alone would have produced ([Bailey & López de Prado, 2014](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551){target="_blank"}).
- The **haircut Sharpe ratio** adjusts the strategy's p-value for multiple testing. It then converts the adjusted p-value back into the Sharpe ratio that would have that p-value on its own ([Harvey & Liu, 2015](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2345489){target="_blank"}). [Harvey, Liu & Zhu (2016)](https://www.nber.org/papers/w20592){target="_blank"} argue, from the number of factors the literature has tested, for a bar of $t > 3$ on new factors.

**In practice.** Report the t-statistic alongside an honest count of the variants tried, including the abandoned ones. Compute the DSR when that count is known. When it is not, compute the DSR from the known trials and treat the result as understating the problem. Prefer out-of-sample and live evidence, which no correction can replace.

**What good looks like.** [Practice] For a single pre-specified test, $t > 2$. After a search, the bar is the one in §3.6, which rises by about one bit of evidence per doubling of the search.

**Failure modes.** The number of trials is rarely known. Researchers do not count dead ends, and a published strategy is the survivor of a whole profession's search. Trials are correlated, so the effective $K$ is smaller than the raw count, and the corrections handle this only roughly. Finally, all of these tests assume the strategy's returns are stationary. After a regime change, a correct test can answer a question that no longer matters.

**When to use it.** Use it to decide whether a backtest or a track record counts as evidence at all, and how long to wait before judging.

## 4.8 Comparison

The table compares the ratios on the attributes that discriminate between them.

| Ratio | Scores which stage | Typical good value | Main failure | Use it for |
|---|---|---|---|---|
| IC | Forecast | 0.02–0.05 monthly; above 0.15 is suspicious | Look-ahead; factor exposure; hides month-to-month variation | Signal research |
| Breadth | Forecast | One to two orders below assets × rebalances | Overcounting | Planning |
| TC | Positions | 0.7–0.9 long-short; 0.3–0.6 long-only | Faithfully expressing a bad alpha | Constraint design |
| IR | P&L vs benchmark | 0.5 good; 1.0 exceptional | Wrong benchmark; beta confusion | Judging a mandate |
| Sharpe | P&L vs cash | 0.3–0.6 single factor; above 2 is suspicious | Blind to skew; inflated by smoothing | Comparing and sizing strategies |
| Hit rate | P&L, bet by bet | Meaningless alone | Hides payoff asymmetry | Diagnosing payoff shape |
| t, PSR, DSR | Track record | $t > 2$ alone; higher after a search | Unknown number of trials | Deciding what counts as evidence |

[Practice] The values are practitioner rules of thumb, and they vary by asset class, horizon and period.

> ### §4 Key takeaways
>
> 1. The Sharpe ratio is leverage-invariant, which makes it the yardstick for strategies that will be scaled. Its standard error is about $1/\sqrt{T}$.
> 2. The information ratio is the Sharpe ratio of the bet against a benchmark. Use the beta-adjusted residual version. The plain active-return version rewards high beta in rising markets.
> 3. Monthly ICs of 0.02 to 0.05 are normal for good equity signals. Above 0.15 on a liquid universe, look for the bug first.
> 4. Breadth counts independent bets, not assets times rebalances. Estimate it backwards, as $(\mathrm{IR}/(\mathrm{TC}\cdot\mathrm{IC}))^2$.
> 5. The square of the transfer coefficient is the share of information kept. Long-only portfolios typically keep a tenth to a third.
> 6. A hit rate means nothing without the payoff ratio, and a high hit rate is a warning sign of a short tail.
> 7. PSR, DSR and the haircut Sharpe ratio correct the t-statistic for non-normality and selection. None of them replaces out-of-sample evidence.

```{=latex}
\newpage
```

# 5. Beyond the standard deviation: the ratio zoo {#5-the-ratio-zoo}

Dozens of performance ratios exist. Most were invented to fix one thing the Sharpe ratio misses. They make more sense on one grid than as a list.

## 5.1 One grid: what goes on top, what goes below

Every ratio in the family puts a measure of reward over a measure of risk. The reward is excess return, residual return, or return above a target. The ratios differ mainly in the risk measure, as the table shows.

| Ratio | Reward | Risk measure | What it adds over Sharpe |
|---|---|---|---|
| Sharpe | Excess return | Standard deviation | — |
| Treynor | Excess return | Beta to the market | Charges only for market risk; right for one holding inside a diversified portfolio |
| Jensen's alpha | Intercept of the market regression | None: it is a return, not a ratio | Says how much, not how efficiently |
| M² (Modigliani) | Return the strategy would earn at the benchmark's volatility | Standard deviation, rescaled | Sharpe in percentage points, easier to communicate |
| Information ratio | Residual return | Residual risk | Benchmark-relative (§4.2) |
| Sortino | Return above a target | Downside deviation below the target | Ignores upside volatility |
| Calmar, MAR, Sterling | Annual return | Maximum (or average) drawdown | The path risk investors actually feel |
| Martin (Ulcer performance) | Excess return | Ulcer index: root-mean-square drawdown | Depth and duration of drawdowns |
| Omega | Expected gain above a threshold | Expected loss below it | Uses the whole distribution |
| STARR, conditional Sharpe | Excess return | Expected shortfall (CVaR) | Tail-sensitive denominator |
| Gain-to-pain | Sum of period returns | Sum of absolute losing-period returns | Simple and robust in short samples |

The original sources are Treynor (1965), [Jensen (1968)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=244153){target="_blank"}, [Modigliani & Modigliani (1997)](https://doi.org/10.3905/jpm.23.2.45){target="_blank"}, [Sortino & Price (1994)](https://doi.org/10.3905/joi.3.3.59){target="_blank"} and [Keating & Shadwick (2002)](https://people.duke.edu/~charvey/Teaching/BA453_2004/Keating_A_universal_performance.pdf){target="_blank"}. The drawdown-based ratios, gain-to-pain and the expected-shortfall ratio are practitioner conventions without a single canonical source. [Value at Risk](value_at_risk.html) treats expected shortfall at length.

## 5.2 Under normality, they are all the Sharpe ratio in disguise

If returns are normal and independent, the mean and standard deviation fix the whole distribution. Suppose also that any threshold sits at zero excess return. Then every total-risk measure in the table, from the downside deviation to the expected shortfall, equals the standard deviation times a factor that depends only on the Sharpe ratio and the horizon. Each of those ratios is then an increasing function of the Sharpe ratio alone. So **ranking strategies by any of them gives the same order as ranking by Sharpe.** Treynor's ratio, Jensen's alpha and the information ratio stand apart, because they measure risk against a market or a benchmark rather than in total. The relations are simple:

- **Sortino** with a zero target is about $\sqrt{2}$ times the Sharpe ratio for the small per-period means of real strategies. The reason is that the downside deviation of a zero-mean normal variable is $\sigma/\sqrt{2}$. The simulation of §5.4 gives a median Sortino ratio of 1.49 for a true Sharpe ratio of 1. This is a little above $\sqrt{2}$, because even a daily mean of 0.06 standard deviations trims the downside deviation by about 5%.
- **M²** is the Sharpe ratio times the benchmark's volatility, plus the cash rate.
- **Omega** with its threshold at zero excess return, the **conditional Sharpe ratio** and the expected **Calmar ratio** over a fixed horizon all rise monotonically with the Sharpe ratio.

So under normality these ratios add no information about skill. Everything they contribute comes from departures from normality, and everything they cost comes from noise.

## 5.3 What they add when returns are not normal

[Fact] Real returns are skewed and fat-tailed, and some strategies are built to have such returns. Selling options, providing liquidity and running carry trades all earn a steady premium and occasionally lose a large multiple of it. Their return distributions have a long left tail that a short sample may not contain. So the sample standard deviation understates the risk, and the Sharpe ratio overstates the skill. [Goetzmann, Ingersoll, Spiegel & Welch (2007)](https://www.ivo-welch.info/research/journalcopy/2007-rfs.pdf){target="_blank"} show that a manager with no skill can raise any measure built on means and variances by trading options to reshape the return distribution. They also derive the only family of measures that resists this manipulation: an average of a power utility of the returns, which they call the **manipulation-proof performance measure**.

The downside-based ratios help, but only partially. Sortino and Omega penalise a left tail if the sample contains one. Drawdown ratios penalise it after the event. The expected-shortfall ratio penalises it if the shortfall estimate captures it. None of them can see a tail that has not happened yet. That is a limit of the data, not of the formulas. The remedy is structural: identify what the strategy is paid for, and stress-test it for that event.

[Practice] **Recommendation: report the Sharpe ratio together with the skewness, the kurtosis, the worst month, the maximum drawdown and the longest time to recover.** Read a high hit rate combined with negative skew as a short-insurance position until shown otherwise.

## 5.4 What they cost: noise

The ratios that use less of the data are noisier. Allocators commonly judge a strategy on a three-year window. The table shows sampling distributions from simulated three-year daily returns at 10% volatility.

| True Sharpe | Ratio | Median | 10th to 90th percentile | (90th − 10th) ÷ median |
|---|---|---|---|---|
| 1.0 | Sharpe | 1.00 | 0.26 to 1.75 | 1.5 |
| 1.0 | Sortino | 1.49 | 0.37 to 2.72 | 1.6 |
| 1.0 | Calmar | 0.88 | 0.14 to 2.23 | 2.4 |
| 0.5 | Sharpe | 0.52 | −0.25 to 1.27 | 2.9 |
| 0.5 | Sortino | 0.75 | −0.34 to 1.91 | 3.0 |
| 0.5 | Calmar | 0.36 | −0.15 to 1.29 | 4.0 |

Noise dominates all three ratios over three years. The Calmar ratio is the worst, because it rests on a single path event, the largest drawdown. Sortino is about as noisy as Sharpe relative to its level, and for normal returns it says nothing that Sharpe does not. A Calmar ratio of 0.88 and one of 2.2 are both consistent with the same true Sharpe ratio of 1.

A practical ordering follows. Use the Sharpe ratio as the scale, because it is the least noisy and the rest of the framework is built on it. Use Sortino, Omega and the tail ratios as diagnostics of skew, not as rival measures of skill. Treat the maximum drawdown and the Calmar ratio as tools for communication and for risk limits, which is how investors use them, and not as estimates of anything.

> ### §5 Key takeaways
>
> 1. Every ratio in the family is reward over risk. They differ almost entirely in the risk measure.
> 2. For normal returns, the total-risk ratios all rank strategies in the same order as the Sharpe ratio. Their only extra information concerns non-normality.
> 3. Strategies that sell insurance show high Sharpe ratios and high hit rates until the event. Downside ratios catch the tail only if the sample contains it.
> 4. Drawdown-based ratios are the noisiest. Over three years, a strategy with a true Sharpe ratio of 1 can show a Calmar ratio anywhere from 0.14 to 2.2, and that is only the middle 80% of outcomes.
> 5. Report the Sharpe ratio with skewness, kurtosis, worst month, maximum drawdown and recovery time. Use the other ratios as diagnostics, not verdicts.

```{=latex}
\newpage
```

# 6. Using it {#6-using-it}

This section is the working core of the chapter. It covers what practitioners compute, in the order they compute it, from a raw signal to a sized allocation and a judgement about the result.

## 6.1 Turning a signal into an alpha: volatility × IC × score

A signal is a ranking or a score, not an expected return. The step that converts one into the other is the most important line of arithmetic in quantitative equity management, and it comes straight from §2.2. Suppose the standardised outcome is $y = \mathrm{IC}\cdot s + \text{noise}$. Then the best linear forecast of $y$ given the signal is $\mathrm{IC}\cdot s$. This is the regression slope of $y$ on $s$, which for two standardised variables equals their correlation. An asset's residual return is its residual volatility times its standardised outcome. Converting from standard deviations back to returns therefore gives

$$
\alpha_i \;=\; \sigma_i \times \mathrm{IC} \times s_i ,
$$

where $\alpha_i$ is asset $i$'s forecast residual return over the horizon, $\sigma_i$ is its residual volatility over the same horizon, and $s_i$ is its standardised score ([Grinold, 1994](https://doi.org/10.3905/jpm.1994.409482){target="_blank"}). Here $\alpha_i$ is a per-asset forecast, unlike the strategy-level $\alpha$ of §4.2. The table applies the rule to a stock with 25% annual residual volatility.

| Residual volatility | IC | Score | Monthly alpha | Annualised |
|---|---|---|---|---|
| 25% a year (7.2% a month) | 0.03 | +1 | 0.22% | 2.6% |
| 25% a year | 0.03 | +2 | 0.43% | 5.2% |
| 25% a year | 0.05 | +1 | 0.36% | 4.3% |
| 25% a year | 0.05 | +2 | 0.72% | 8.7% |

Three consequences matter in practice.

- **The IC shrinks the score.** Take a stock two standard deviations above average on a signal with an IC of 0.05. It is expected to beat its peers by a tenth of a standard deviation, not by two. Feeding raw scores to an optimiser as if they were expected returns overstates confidence by a factor of $1/\mathrm{IC}$, which is 20 at an IC of 0.05. The optimiser will then lever the overstatement.
- **Volatility scales the alpha, and the optimiser then divides it back out.** Expected return is proportional to volatility. A mean-variance position, however, is proportional to expected return divided by variance: $\Delta w_i \propto \alpha_i/\sigma_i^2 = \mathrm{IC}\cdot s_i/\sigma_i$. So the risk-adjusted active position $\Delta w_i\,\sigma_i$ ends up proportional to $\mathrm{IC}\cdot s_i$. A good rule produces positions whose risk is proportional to the score.
- **The horizons must match.** The IC and the volatility must be measured over the same horizon as the forecast. A monthly IC multiplied by an annual volatility gives $\sqrt{12}$ times the monthly alpha it is meant to produce.

In the information view, the rule extracts exactly what the forecast knows and no more. It expresses the forecast's information in units of return.

## 6.2 Measuring an IC properly

Most bad signals are not bad ideas but bad measurements. The checklist below is ordered roughly by how often each item causes the problem.

1. **Point-in-time data.** Use data as it was known on the forecast date, with realistic reporting lags. Revised fundamentals and today's index membership are the most common sources of a too-good IC.
2. **Residual outcomes.** Measure the IC against returns net of the risk model's factors: market, sector, size, beta, and the styles the strategy is not meant to bet on. Otherwise a value signal in a value rally reports factor returns as skill.
3. **A tradable universe.** Apply the liquidity and price filters the live strategy will use, and report the IC by size bucket. Many signals live in stocks that cannot be traded in size.
4. **Ranks first.** Report the rank IC, and compute the Pearson IC as a check. A large gap between them means a few outliers carry the result.
5. **The whole series.** Compute $\mathrm{IC}_t$ every period. Report its mean, standard deviation, IC information ratio and t-statistic. Plot its cumulative sum, which reads like an equity curve. Regimes, decay and breaks show up there before they show up anywhere else.
6. **Non-overlapping windows.** Suppose the forward window is longer than the sampling interval, as with a 21-day forward return sampled daily. Then consecutive ICs share most of their data. Use non-overlapping windows or autocorrelation-robust standard errors ([Newey & West, 1987](https://www.jstor.org/stable/1913610){target="_blank"}). Otherwise the t-statistic will be several times too large.
7. **The decay curve.** Compute the IC against forward returns over several horizons $\tau$, from a day to a quarter. The way the IC changes with $\tau$ shows how the signal's information arrives. The IC over $\tau$ is roughly the return the signal predicts over that horizon divided by the noise over it, and the noise grows like $\sqrt{\tau}$. Two cases follow.
   - If the IC grows like $\sqrt{\tau}$, the predicted return grows in proportion to $\tau$. The return accrues steadily, and the signal is slow. Trading it faster adds turnover, not information.
   - If the IC falls like $1/\sqrt{\tau}$, the predicted return does not grow at all. It arrives near the start, and the signal is fast. Delay is then expensive (§3.5), and so is holding past the half-life.
8. **Stability.** Break the IC down by sector, by year and by volatility regime. A signal whose IC is moderate everywhere is worth more than one whose IC is high on average but concentrated in one sector or one decade.
9. **The trial count.** Record every variant tried (§4.7).

Two numbers summarise the result. The standard error of the mean IC over $n$ periods is $\hat\sigma_{\mathrm{IC}}/\sqrt{n}$. And the IC information ratio times $\sqrt{q}$ is, by the arithmetic of §7.1, the information ratio the signal would earn with a transfer coefficient of one and no costs. This is the ceiling from which every later stage of the pipeline subtracts. Because $\hat\sigma_{\mathrm{IC}}$ contains the sampling noise that §7.1 separates out, this ceiling applies at the current universe size. It is not §7.1's limit as $N$ grows.

## 6.3 Combining signals

With several signals, the combined IC generalises §3.4. Collect the ICs in a vector $\mathbf{ic}$, and the correlations between the signals in a matrix $\mathbf{C}$. The best linear combination weights the standardised signals in proportion to $\mathbf{C}^{-1}\mathbf{ic}$, and it achieves

$$
\mathrm{IC}_{\text{combined}}^2 \;=\; \mathbf{ic}^{\top}\,\mathbf{C}^{-1}\,\mathbf{ic}.
$$

The combined IC then carries information exactly as a single IC does (Appendix A.4). This calculation is mean-variance optimisation, with ICs in place of expected returns and signal correlations in place of the covariance matrix. It inherits the same weakness. The ICs are estimated with large error (§2.2), and $\mathbf{C}^{-1}$ amplifies that error. [Portfolio Construction and the Covariance Matrix](portfolio_construction.html) explains the mechanism.

[Practice] Practitioners therefore rarely use the formula raw. Without long histories, an equal-weighted average of standardised, neutralised signals is a hard benchmark to beat. IC weighting that ignores correlations is the usual next step. Full $\mathbf{C}^{-1}$ weighting is shrunk heavily toward one of those two. Two diagnostics are worth more than the weights themselves:

- **Marginal IC.** Regress a candidate signal on the existing composite, and measure the IC of the residual. That residual IC is the new information the signal brings: its square is exactly what the candidate adds to the composite's squared IC. It is often a small fraction of the candidate's standalone IC.
- **Correlation with the existing composite.** Suppose a candidate is correlated $\rho$ with a composite whose IC is $a$. The candidate adds nothing if its own IC is exactly $\rho a$, which is the boundary case in the fifth row of the table in §3.4. At a correlation of 0.7, a candidate exactly as good as the composite raises the combined IC by only 8.5%. A highly correlated signal earns its place only if its IC is far from $\rho a$. Either its IC is well above the composite's, or it is near zero, so that the signal measures the composite's noise (§3.4).

Weights that change with market conditions are tempting and usually overfit. [Contested] Some practitioners report gains from timing signal weights, but the evidence that such gains survive out of sample is thin.

## 6.4 Counting breadth honestly

Of the factors in the fundamental law, breadth is the one most often overstated and least often measured. Three habits keep the count honest.

- **Neutralise, then count.** Strip out factor exposures before treating the stocks as separate bets, and estimate the residual correlation of the surprises. A residual correlation of 0.01 is the difference between 500 bets and 84 (§2.4).
- **Count new information, not trades.** Rebalancing a slow signal more often makes more bets, but each bet carries less. If the expected return accrues evenly, a monthly IC is the annual IC divided by $\sqrt{12}$. So 12 monthly bets carry the same information as one annual bet. Faster trading adds breadth only when the signal itself refreshes faster.
- **Estimate it backwards.** Once a live or out-of-sample record exists, compute the implied breadth $(\mathrm{IR}/(\mathrm{TC}\cdot\mathrm{IC}))^2$ and compare it with the planned count. A large gap is the clearest diagnostic available.

Breadth also has a cost. Bets in more assets, or more often, mean more trading, and costs do not shrink when the horizon does. A short-horizon strategy earns an edge per trade proportional to the IC times the volatility over the holding period. That volatility shrinks like the square root of the horizon, while costs per trade stay fixed. [Intraday Momentum](intraday_momentum.html) works through this limit for one family of strategies.

## 6.5 Raising the transfer coefficient

The transfer coefficient enters the law squared, so it is often the cheapest place to find information. Raising it from 0.5 to 0.6 is worth as much as raising the IC by a fifth. The first is an engineering decision, while the second requires research.

The following constraints lower the TC, roughly in order of cost:

- **The long-only constraint.** An underweight can be no larger than the stock's benchmark weight, and most stocks in a cap-weighted index have tiny weights. So most negative views, which make up half of any symmetric signal, are barely expressed.
- **Position limits.** They cap the strongest views, which is where most of the alpha is.
- **Turnover limits and minimum trade sizes.** They make the portfolio trail the forecast.
- **Factor and sector constraints that fight the signal.** If a signal is partly a sector bet and the portfolio must be sector-neutral, the optimiser spends effort undoing the alpha.

The following measures raise it:

- **Relax the long-only constraint** where the mandate allows. Extension (130/30) structures exist mainly to raise the transfer coefficient.
- **Neutralise the signal, not the portfolio.** If unwanted exposures are removed from the forecast before optimisation (§3.4), the constraints no longer fight it.
- **Trade toward an aim portfolio.** Instead of capping turnover, follow the result of [Gârleanu & Pedersen (2013)](https://nbgarleanu.github.io/DynTrad.pdf){target="_blank"}. They show that the optimal policy under trading costs moves partway each period toward a target that blends current and expected future alphas. For the same cost, it keeps the portfolio closer to the forecast.
- **Prefer penalties to hard bounds.** A penalty lets the optimiser trade a constraint off against information rather than treating it as absolute.

## 6.6 Sizing: from Sharpe ratio to leverage

Consider a strategy with excess return $\mu$ and volatility $\sigma$. Its growth-optimal (Kelly) leverage is $f^\ast = \mu/\sigma^2$, and that leverage delivers the growth rate $\mathrm{SR}^2/2$ of §3.2. [Simple and Log Returns](log_returns.html) derives both results. Multiplying the leverage by the volatility gives the volatility of the growth-optimal position:

$$
f^\ast \sigma \;=\; \frac{\mu}{\sigma} \;=\; \mathrm{SR}.
$$

**The growth-optimal volatility equals the Sharpe ratio.** On this criterion, a strategy with a Sharpe ratio of one should run at 100% annual volatility, or at 50% at half Kelly. Almost nobody does, for three reasons.

- **Overbetting is far worse than underbetting.** At a fraction $c$ of the Kelly leverage, growth is $(2c - c^2)\,\mathrm{SR}^2/2$. Missing by the same factor costs very different amounts on the two sides. Half Kelly keeps 75% of the growth with half the volatility. Double Kelly earns nothing, and anything beyond it loses money in the long run.
- **The Sharpe ratio is an estimate.** Its standard error is near $1/\sqrt{T}$, so a 10-year record with a Sharpe ratio of 1.0 is consistent with a true value of 0.4. Sizing at the estimate means overbetting in a large share of the worlds consistent with the data, and overbetting is the expensive side.
- **Returns are not normal.** Fat left tails make the true growth-optimal leverage lower than the formula says.

[Practice] Practitioners who use Kelly at all use a quarter to a half of it. Most institutions run 10% to 20% volatility on strategies they believe have Sharpe ratios near one, which is a small fraction of Kelly. Read in information terms, that choice says how little they trust their own estimate.

**Allocating risk across strategies** follows the bookkeeping of §3.3. For uncorrelated strategies, the combination with the highest Sharpe ratio allocates risk in proportion to each strategy's Sharpe ratio, and its squared Sharpe ratio is the sum of theirs. With correlations, the risk allocation is proportional to $\mathbf{C}^{-1}$ times the vector of Sharpe ratios, where $\mathbf{C}$ is now the correlation matrix of the strategies' returns. This is the same formula as for signals in §6.3. It has the same estimation problem, and the same remedy: shrink toward equal risk. Grinold and Kahn give the single-manager version. The optimal active risk is proportional to the information ratio. So a manager with twice the IR should take twice the tracking error, and should therefore expect four times the alpha.

## 6.7 Judging a track record

Combining §3.6 with base rates makes the arithmetic of manager selection uncomfortable. Suppose one manager in ten has real skill. Consider a record that reaches $t = 2$, credited with the full likelihood ratio of 7.4 that §3.6 assigns it. That record turns prior odds of one to nine into posterior odds of $7.4/9 \approx 0.82$. This is a 45% chance of skill, worse than a coin toss (Appendix B.14). The table shows how often a manager with real skill still underperforms.

| True IR | Chance of a negative residual return over 1 year | 3 years | 5 years | 10 years |
|---|---|---|---|---|
| 0.3 | 38% | 30% | 25% | 17% |
| 0.5 | 31% | 19% | 13% | 5.7% |
| 1.0 | 16% | 4.2% | 1.3% | 0.1% |

The same problem appears from the other side. A manager with no skill at all shows a measured IR above 0.5 over three years 19% of the time. That is exactly as often as a top-quartile manager with a true IR of 0.5 shows a negative one. A three-year review cannot tell them apart. The problem is not hypothetical. [Goyal & Wahal (2008)](https://doi.org/10.1111/j.1540-6261.2008.01375.x){target="_blank"} studied the hiring and firing decisions of about 3,400 plan sponsors. Sponsors hired managers after strong returns and fired them after weak ones. The managers they hired then did no better than the fired managers would have.

The following evidence supplements the P&L, or can replace it:

- **The record at the bet level.** The P&L is the end of the pipeline. A record of forecasts, positions and trades shows each stage separately. It shows whether the IC was stable, how much the transfer coefficient and costs took, and whether a poor year came from the forecasts or from implementation. It can distinguish a skilled forecaster with poor implementation from a lucky one, which the P&L alone cannot.
- **Consistency with the stated logic.** A strategy that claims to follow trends should show the payoff shape of §4.6. A strategy that claims to be market-neutral should show neutrality in its beta. Mismatches carry information long before the Sharpe ratio does.
- **The honest trial count.** For a backtest, ask how many variants were tried. For a manager, remember that the managers on view are the survivors (§4.7).
- **Out-of-sample time.** Count only the years since the strategy was fixed. In information terms, a backtest's in-sample years are worth far less than live years, because the search has already spent their evidence.
- **Capacity and costs.** A strategy that worked at a hundred million may not work at a billion. The information is the same, but the rate at which it converts into money is not.

> ### §6 Key takeaways
>
> 1. Turn scores into alphas with $\alpha_i = \sigma_i \times \mathrm{IC} \times s_i$. Raw scores overstate confidence by $1/\mathrm{IC}$, and optimisers lever the overstatement.
> 2. Measure ICs point-in-time, on residual returns, in a tradable universe, with ranks, as a full time series, without overlapping windows, across horizons, and with the trial count recorded.
> 3. The IC decay curve shows how fast a signal's information arrives. It therefore sets how fast to trade the signal and how much delay costs.
> 4. Combine signals by their marginal information. Equal-weighting standardised signals is a strong benchmark, and full $\mathbf{C}^{-1}$ weighting needs heavy shrinkage.
> 5. Trading a slow signal faster adds trades, not information. Estimate breadth backwards from realised IR, TC and IC.
> 6. The transfer coefficient is often the cheapest source of information. Relax long-only, neutralise the signal rather than the portfolio, and trade toward an aim portfolio.
> 7. The growth-optimal volatility equals the Sharpe ratio. Practitioners run a small fraction of it, because overbetting is expensive and the Sharpe ratio is uncertain.
> 8. Over three years, a top-quartile manager trails the benchmark, after adjusting for beta, one time in five. A manager with no skill posts a top-quartile IR equally often. Judge the process at the bet level, not the three-year P&L.

```{=latex}
\newpage
```

# 7. Where it breaks {#7-where-it-breaks}

## 7.1 The fundamental law overpromises

[Fact] Realised information ratios fall far short of $\mathrm{IC}\sqrt{N q}$, computed from the number of assets $N$ and the number of rebalances a year $q$. This section asks why. Its answer is the one §2.4 previewed: the IC varies over time. The view taken here is that this variation is the largest single cause of the shortfall.

[Qian & Hua (2004)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=569281){target="_blank"} made the point precisely. In a given period, the realised IC of a signal across $N$ stocks differs from its long-run mean $\overline{\mathrm{IC}}$ for two reasons:

- sampling noise, with variance about $1/N$, which is the $1/\sqrt{n}$ standard error of §2.2 with one pair per stock;
- genuine variation in how well the signal works that period, with standard deviation $\sigma_{\mathrm{IC}}$.

The measured $\mathrm{IC}_t$ series therefore has variance $\hat\sigma_{\mathrm{IC}}^2 \approx \sigma_{\mathrm{IC}}^2 + 1/N$. With positions proportional to the scores (§6.1), a period's P&L is roughly proportional to its realised IC. So the information ratio is the mean of the realised IC over its standard deviation, annualised:

$$
\mathrm{IR} \;\approx\; \sqrt{q}\;\frac{\overline{\mathrm{IC}}}{\sqrt{\sigma_{\mathrm{IC}}^2 + 1/N}}
\;\;\xrightarrow{\;N\to\infty\;}\;\; \sqrt{q}\;\frac{\overline{\mathrm{IC}}}{\sigma_{\mathrm{IC}}} .
$$

The first expression is the IC information ratio of §4.3, $\overline{\mathrm{IC}}/\hat\sigma_{\mathrm{IC}}$, times $\sqrt{q}$. Splitting its denominator in two shows where breadth stops working. With $\sigma_{\mathrm{IC}} = 0$, the expression equals $\sqrt{q}\,\overline{\mathrm{IC}}\sqrt{N} = \overline{\mathrm{IC}}\sqrt{Nq}$, which is Grinold's law with $\mathrm{BR} = Nq$. With any variation at all, breadth stops helping once $1/N$ is small next to $\sigma_{\mathrm{IC}}^2$. The information ratio then approaches a ceiling set by the signal's consistency rather than by its universe. Qian and Hua call the extra variance **strategy risk**. They note its practical symptom: realised tracking error persistently exceeds what the risk model predicted. The risk model knows about the stocks' volatility, but not about the signal's.

The figure shows the ceiling for an average IC of 0.05.

```{=latex}
\begin{center}
\includegraphics[width=\linewidth]{quant-research/figures/ei_breadth.pdf}
\end{center}
```

```{=html}
<img class="mdd-fig" src="quant-research/figures/ei_breadth.svg"
     alt="Annualised information ratio against number of stocks for an average IC of 0.05, for constant IC and for month-to-month IC standard deviations of 0.05 and 0.10, with simulated points and ceilings">
```

With an average monthly IC of 0.05, a standard deviation of 0.10 caps the information ratio at $\sqrt{12} \times 0.05/0.10 = 1.73$, however many stocks are added. Three hundred stocks already reach 1.50. [Practice] Genuine month-to-month variation of 0.05 to 0.15 in the IC is common for equity signals. So for most signals, the ceiling binds before the size of the universe does.

The other critiques sharpen the same point.

- [Ding & Martin (2017)](https://pdfs.semanticscholar.org/9cee/6ab8aaefee12ec74487798e04df91033f356.pdf){target="_blank"} rebuild the law with the IC as a random factor return in a cross-sectional model. With standardised signals and outcomes, the slope of each period's cross-sectional regression of outcomes on the signal is that period's IC. They find the same mechanism at work. A random IC is a component common to every bet in a period, and it makes the bets dependent across stocks (§2.4).
- [Clarke, de Silva & Thorley (2006)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=934440){target="_blank"} give an exact version with a full covariance matrix. In it, the approximation errors of the original disappear and the role of correlation is explicit.
- [Zhou (2008)](https://www.pm-research.com/content/iijpormgmt/34/4/26){target="_blank"} shows that error in the estimated alphas, left unmanaged, can consume most of the promised value. Scaling the active portfolio down recovers much of it.
- [Buckle (2004)](https://link.springer.com/article/10.1057/palgrave.jam.2240118){target="_blank"} pulls the other way in one respect. In his model, correlation among forecasts can help when it is used rather than ignored. So the effect of correlation on breadth depends on what is correlated with what.

[Contested] The split of the typical gap between IC variation, constraints and costs is not settled, and it varies by strategy. The view taken here is that IC variation dominates for diversified equity signals and costs dominate at short horizons. Neither answer changes the planning rule. [Practice] **Recommendation: treat the measured IC information ratio (§4.3) as the input, and treat the asset count as an upper bound on breadth rather than an estimate of it.**

## 7.2 Breadth, miscounted

Three ways of overstating breadth have appeared already: shared factor exposure (§2.4), rebalancing a slow signal (§6.4) and IC variation (§7.1). Two more are worth naming. **Adding universes where the signal has no skill**, the zero-IC bets of §4.4, raises the count of bets and dilutes the IC. At best it leaves the information unchanged. And **pairs and spreads** are one bet, not two. A long and a short position in two highly correlated stocks carry one forecast about their relative performance.

## 7.3 Sharpe ratios that lie

A measured Sharpe ratio can be high for reasons that have nothing to do with information.

- **Smoothing.** Illiquid assets are marked with stale or appraised prices, which spread a single economic shock over several reporting periods. Measured volatility falls, and returns become positively autocorrelated. [Getmansky, Lo & Makarov (2004)](https://www.nber.org/papers/w9571){target="_blank"} show that this effect explains much of the serial correlation in hedge fund returns, and they give a corrected Sharpe ratio. The table in §2.4 shows how large the overstatement can be.
- **Selling the tail.** A strategy that sells out-of-the-money options earns a premium most months and occasionally loses many months' worth at once. Over a calm sample, its Sharpe ratio is high and meaningless (§5.3).
- **Unavailable leverage.** The Sharpe ratio assumes the strategy can be scaled at the cash rate. Consider an investor who cannot borrow, or who faces margin limits. For that investor, a low-volatility strategy with a high Sharpe ratio may deliver less return than a higher-volatility strategy with a lower ratio.
- **Gross of everything.** Fees, financing spreads, borrow costs for shorts and market impact all come off the numerator. Backtests routinely omit some of them.
- **Survivors.** Fund databases and published strategies contain the survivors. The average measured Sharpe ratio of survivors overstates the average of the population they were drawn from.

## 7.4 Too good to be true: how high can a Sharpe ratio be?

Asset-pricing theory puts an upper bound on Sharpe ratios. [Hansen & Jagannathan (1991)](https://doi.org/10.1086/261749){target="_blank"} showed that no portfolio's Sharpe ratio can exceed the volatility of the **stochastic discount factor** $M$ divided by its mean. $M$ is the random variable that prices every payoff: a payoff's price today is $\mathbb{E}[M \times \text{payoff}]$. The bound takes one line to derive. An excess return $R^e$ costs nothing to hold, so $0 = \mathbb{E}[M R^e] = \mathbb{E}[M]\,\mathbb{E}[R^e] + \operatorname{Cov}(M, R^e)$. A covariance is never larger in size than the product of the two standard deviations. Hence $\mathbb{E}[R^e]/\sigma(R^e) \le \sigma(M)/\mathbb{E}[M]$.

A Sharpe ratio far above the market's therefore implies one of two things. Either the discount factor is far more volatile than economic models can justify, or the deal should not survive competition. [Cochrane & Saá-Requejo (2000)](https://www.johnhcochrane.com/research-all/beyond-arbitrage-good-deal-asset-price-bounds-in-incomplete-markets){target="_blank"} turned this idea into **good-deal bounds**. Ruling out arbitrage excludes only deals with an infinite Sharpe ratio. Ruling out Sharpe ratios above a chosen multiple of the market's is a stronger assumption, though far weaker than committing to a full pricing model. It narrows the range of prices a model allows.

For a practitioner, the bound translates into a prior. [Practice] High Sharpe ratios exist, but almost always in one of three places:

- where capacity is small, as in market making and short-horizon arbitrage;
- where the strategy is paid for providing a service, such as liquidity or insurance;
- where the risk is hidden, as in a short tail that has not yet appeared.

A daily or slower strategy that backtests above 2 at meaningful scale is far more likely to contain a mistake than a discovery. The usual mistakes are:

- look-ahead in the data;
- survivorship in the universe;
- fills at prices that could not be traded, such as the close that generated the signal;
- unmodelled borrow costs;
- stale prices in illiquid instruments;
- overlapping returns counted as independent.

## 7.5 Where the information analogy breaks

The information view is a lens, and it distorts at the edges.

- **The growth–information identity is exact only in Kelly's setting:** fair odds, a complete set of bets, and all wealth wagered. In markets it holds to leading order for small ICs (§3.2), and as an inequality in general ([Barron & Cover, 1988](https://doi.org/10.1109/18.21241){target="_blank"}).
- **Mutual information is hard to measure.** Simple estimators that bin the data are biased upward. The bias is large next to the thousandths of a bit per bet that real signals carry: 0.0003 to 0.007 bits for ICs of 0.02 to 0.10 (§3.1; A.13 puts numbers on the bias). Nearest-neighbour estimators ([Kraskov, Stögbauer & Grassberger, 2004](https://arxiv.org/abs/cond-mat/0305641){target="_blank"}) are much better, but they still need very large samples at these levels. The view taken here is that mutual information is the right unit for thinking and a poor statistic for measuring. Two statistics are more practical for detecting non-linear predictability. A quantile spread is the average outcome of the top bucket of forecasts minus that of the bottom bucket. A tail IC is the IC computed on the most extreme forecasts only.
- **Information is not edge.** Costs, market impact and capacity convert information into money at a loss, and the exchange rate worsens with size.
- **Information decays.** Other participants learn it. [McLean & Pontiff (2016)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2156623){target="_blank"} find that the returns to published equity anomalies are 26% lower out of sample and 58% lower after publication. Evidence accumulates about a target that moves.
- **Growth-optimality is not a recommendation.** Kelly's criterion is a yardstick for comparing information and growth. Whether to maximise expected log wealth is a question about preferences, and the mathematics does not answer it.

> ### §7 Key takeaways
>
> 1. Realised information ratios fall far short of the IC times the square root of assets times rebalances. The view taken here is that variation in the IC from period to period is the largest single reason. Constraints and costs make up the rest.
> 2. With IC variation, the information ratio approaches a ceiling of $\sqrt{q}\,\overline{\mathrm{IC}}/\sigma_{\mathrm{IC}}$. At a mean of 0.05 and a standard deviation of 0.10, that ceiling is 1.73 with monthly rebalancing, however many stocks are added.
> 3. Plan with the measured ratio of the mean IC to its standard deviation, and treat the asset count as an upper bound on breadth.
> 4. Smoothing, tail selling, unavailable leverage, omitted costs and survivorship all raise measured Sharpe ratios without adding information.
> 5. Asset pricing bounds Sharpe ratios. A daily or slower backtest above 2 at scale is more likely a bug, a niche or a hidden tail than a discovery.
> 6. The information analogy is exact only in Kelly's horse race. Mutual information is a poor statistic at real-world signal strengths, and the information in a signal decays as others learn it.

```{=latex}
\newpage
```

# 8. How the ideas evolved {#8-how-the-ideas-evolved}

The ideas in this chapter came from four communities that mostly worked apart: communication engineers, academic students of fund performance, practitioners of quantitative active management, and statisticians of backtests. The history is short enough for one timeline.

| Year | Milestone |
|---|---|
| 1948 | Shannon: information, entropy and channel capacity |
| 1956 | Kelly: the growth rate of wealth equals the information rate |
| 1965–68 | Treynor, Sharpe and Jensen: risk-adjusted performance |
| 1973 | Treynor and Black: squared appraisal ratios add |
| 1974 | Ambachtsheer: the information coefficient |
| 1988 | Barron and Cover: a bit at most doubles wealth |
| 1989–94 | Grinold: the fundamental law, and alpha as volatility times IC times score |
| 2002 | Clarke, de Silva and Thorley: the transfer coefficient; Lo: the statistics of Sharpe ratios |
| 2004 | Qian and Hua: variation in the IC as strategy risk |
| 2012–16 | Bailey and López de Prado, Harvey and Liu: Sharpe ratios corrected for selection |

The second table summarises each community's contribution and its limits.

| Community | Contribution | What changed | Limitation | What lasts |
|---|---|---|---|---|
| Communication engineers (Shannon, Kelly, Cover) | Information as a measurable quantity; growth of wealth as an information rate | Betting and investing could be analysed as channels | Built for fair odds and stationary sources; little contact with practitioners | The units, and the growth–information identity |
| Performance measurement (Treynor, Sharpe, Jensen, Treynor–Black) | Return per unit of risk; residual return; the appraisal ratio | Performance became risk-adjusted and benchmark-relative | Assumed normal returns and a known benchmark | The Sharpe and information ratios, and the additivity of squared ratios |
| Quantitative active management (Ambachtsheer, Grinold, Kahn, Clarke and colleagues, Qian) | The IC, the fundamental law, the alpha rule, the transfer coefficient | Forecasting skill, breadth and implementation could be priced against each other | The law's breadth term overstates independent bets | The planning framework of §6, with the corrections of §7.1 |
| Statistics of skill (Lo, Bailey and López de Prado, Harvey and Liu) | Standard errors, selection corrections, minimum track records | Backtests were recognised as searches, and Sharpe ratios as estimates | The number of trials is rarely known | The habit of asking how much evidence a record contains |

The communities rarely connected their results. Kelly's paper is about information rate, Grinold's about breadth, and Lo's about standard errors, and each community cites the others sparingly. The reading offered here is that the information view mostly consists of noticing that they were computing the same quantity in different units. §3 makes that observation explicit.

> ### §8 Key takeaways
>
> 1. The information-theoretic thread (Shannon, Kelly, Barron and Cover) predates most of performance measurement and runs parallel to it.
> 2. Practitioners built the framework of IC, breadth and transfer coefficient between 1974 and 2002. In the 2000s it was corrected for IC variation and estimation error.
> 3. The statistics of skill are the most recent layer and the most urgent in practice. They say how much of any of the other numbers is real.

```{=latex}
\newpage
```

# 9. Synthesis {#9-synthesis}

## 9.1 The framework on one page

One spine runs through the chapter. Every ratio is a signal-to-noise ratio, half its square is information, and that information only leaks on its way from forecast to proof. The table collects the relations that follow, with the status of each.

| Relation | Formula | Status |
|---|---|---|
| Signal fraction | $R^2 = \mathrm{IC}^2$; $\ \mathrm{SNR} = \mathrm{IC}^2/(1-\mathrm{IC}^2)$ | Exact (linear model) |
| Hit rate | $\tfrac12 + \arcsin(\mathrm{IC})/\pi$ | Exact (jointly normal) |
| Information per bet | $-\tfrac12\ln(1-\mathrm{IC}^2) \approx \mathrm{IC}^2/2$ nats | Exact (jointly normal); approximation for small IC |
| Fundamental law, in squares | $\mathrm{IR}^2 = \mathrm{TC}^2 \times \mathrm{IC}^2 \times \mathrm{BR}$ | Exact to leading order in IC, given independent bets (Clarke, de Silva and Thorley's 2006 version is exact); BR is the hard part |
| Ceiling from IC variation | $\mathrm{IR} \le \sqrt{q}\;\overline{\mathrm{IC}}/\sigma_{\mathrm{IC}}$, with $\sigma_{\mathrm{IC}}$ the genuine variation | Approximate |
| Uncorrelated strategies | $\mathrm{SR}_{\text{combined}}^2 = \sum_i \mathrm{SR}_i^2$ | Exact (optimal risk weights) |
| Correlated signals | $\mathrm{IC}_{\text{combined}}^2 = \mathbf{ic}^{\top}\mathbf{C}^{-1}\mathbf{ic}$ | Exact (linear combination) |
| Alpha | $\alpha_i = \sigma_i \times \mathrm{IC} \times s_i$ | Exact (best linear forecast) |
| Growth | $g^\ast = \mathrm{SR}^2/2$; growth-optimal volatility $= \mathrm{SR}$ | Exact with continuous rebalancing and normal returns; approximate otherwise |
| Growth vs information | $g^\ast$ = information rate; in general $\le$ | Exact in Kelly's horse race; inequality in general |
| Evidence | $t^2/2 = T\,\mathrm{SR}^2/2$ nats | Exact (normal returns) |
| Time to proof | $T = 4/\mathrm{SR}^2$ years for the expected $t$ to reach 2 | Exact (normal returns) |
| Cost of searching | about 1 bit of extra evidence per doubling of trials | Approximation (Bonferroni, large $K$) |

The diagram traces the same quantity from forecast to proof.

```mermaid
flowchart TB
    M["Next period's returns"] --> F["Forecast<br/>IC squared / 2 nats per bet"]
    F -- "times independent bets" --> B["Information per year<br/>BR x IC squared / 2"]
    B -- "times TC squared,<br/>minus costs and delay" --> P["P&amp;L<br/>IR squared / 2 nats per year"]
    P --> G["Growth<br/>log wealth over cash at SR squared / 2"]
    P --> E["Evidence<br/>t squared / 2 = T x SR squared / 2"]
    E -- "minus the cost of the search" --> T["Proof<br/>about 4 / SR squared years, more after a search"]
    style F fill:#0B6E75,color:#fff
    style B fill:#0B6E75,color:#fff
    style P fill:#0B6E75,color:#fff
    style G fill:#58666E,color:#fff
    style E fill:#58666E,color:#fff
    style T fill:#A8452B,color:#fff
```

## 9.2 A decision tree

Four questions cover most uses of the framework. Each row says what to compute and what to do with the result.

| Decision | Compute | Then |
|---|---|---|
| Is this signal worth building? | Rank IC on residual returns, point-in-time, in a tradable universe; its mean, standard deviation and decay curve; its marginal IC against the existing signals | Expect an information ratio no better than $\sqrt{q}$ times the mean IC over its standard deviation, before construction and costs; build only if what survives the leaks clears the hurdle |
| How should forecasts become a portfolio? | Alphas as volatility × IC × score; the transfer coefficient of the constrained portfolio; costs per unit of active risk | Maximise $\mathrm{TC}^2$ times the information, net of costs: neutralise the signal rather than the portfolio, and trade toward an aim portfolio |
| Is this strategy or manager skilled? | Years observed against $4/\mathrm{SR}^2$; the number of variants tried; the deflated Sharpe ratio; the bet-level record | Wait, deflate, and judge the process; do not judge the three-year P&L |
| How much risk should it get? | Sharpe ratios and their correlations across strategies; the uncertainty in each estimate | Risk in proportion to Sharpe ratio, shrunk toward equal risk; a fraction of Kelly, with volatility well below the Sharpe ratio |

Four habits apply whatever the question: reason in squares, count only independent bets, list the leaks between forecast and P&L, and treat a Sharpe ratio above two as a question rather than an answer.

## 9.3 Advice for someone starting today

1. **Square every ratio before reasoning with it.** Squares are information, and information adds. Ratios do not add.
2. **Expect small ICs.** A monthly IC of 0.03 is a real signal. An IC above 0.15 on a liquid universe is a bug until proven otherwise.
3. **Never use a raw score as an expected return.** Multiply it by volatility and the IC first.
4. **Measure the IC's standard deviation, not just its mean.** The ratio of the two, times $\sqrt{q}$, is the information ratio before construction and costs. It is the ceiling on everything downstream.
5. **Count independent bets, not stocks.** Neutralise first. Estimate breadth backwards from realised results as soon as they exist.
6. **Look for information in the transfer coefficient.** It enters squared, and raising it is engineering rather than research.
7. **A second uncorrelated strategy usually beats a better first one.** The arithmetic of squares favours diversification over refinement.
8. **Run well below Kelly.** The growth-optimal volatility equals the Sharpe ratio, and no estimate of the Sharpe ratio is good enough to justify it.
9. **Divide four by the squared Sharpe ratio before judging anything.** The result is the number of years the record needs. Add one bit of evidence for every doubling of the search.
10. **Treat a high Sharpe ratio as a question.** Ask what service is being sold, what tail is hidden, or what bug is in the data.

## 9.4 What is known, and what is not

**Known.** The identities of §9.1 are mathematics, not empirics: given their assumptions, they hold. The scale of real-world skill is well documented. ICs are a few hundredths, good managers have information ratios of a half to one, and Sharpe ratios take years to confirm. Many studies document that realised information ratios fall far short of what asset counts promise. The main mechanism, variation in the IC from period to period, is understood. Its share of the gap, relative to constraints and costs, is not (§7.1).

**Not known.**

- The true breadth of any particular strategy. It can only be estimated after the fact, and with noise.
- The true number of trials behind any published result or live fund. Without it, every correction for selection is a guess.
- How much information remains in markets that many participants search with the same tools, and how fast that information decays after it is found.
- Whether non-linear measures of predictability, which the information view naturally suggests, add much in practice at the signal strengths real markets allow. [Hypothesis] The view taken here is that they add little except in the tails.

The framework's main value is that it makes these unknowns visible and expresses them in one currency. A strategy is an information budget. It has so many bits per bet and so many bets per year. It keeps so much through construction and pays so much in costs. And it needs so many years before anyone, including its owner, can tell whether it works.

> ### §9 Key takeaways
>
> 1. One currency, half a squared ratio in nats, connects every stage from forecast to proof.
> 2. The identities are exact under their stated assumptions. The uncertainty lies in the assumptions about breadth and about the number of trials.
> 3. Plan with measured IC consistency, a realistic transfer coefficient and realistic costs. Judge with years observed against $4/\mathrm{SR}^2$ and an honest trial count.

```{=latex}
\newpage
```

# 10. References {#10-references}

The references are grouped by kind, because each kind is read differently. Each entry says why the work matters. Where a free copy exists, the link points to it. Paywalled-only entries are marked. Entries without a link have no stable copy that could be found.

## 10.1 Information theory and growth

- **Shannon, C. E. (1948).** ["A Mathematical Theory of Communication."](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf) *Bell System Technical Journal* 27, 379–423 and 623–656. [[DOI]](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x) — Entropy, mutual information and channel capacity, including the Gaussian-channel formula of §2.6.
- **Kelly, J. L., Jr. (1956).** ["A New Interpretation of Information Rate."](https://www.princeton.edu/~wbialek/rome/refs/kelly_56.pdf) *Bell System Technical Journal* 35(4), 917–926. — The growth of a gambler's wealth equals the information rate of their tips (§3.2). It is an information-theory paper, not a finance paper.
- **Barron, A. R. & Cover, T. M. (1988).** ["A Bound on the Financial Value of Information."](https://doi.org/10.1109/18.21241) *IEEE Transactions on Information Theory* 34(5), 1097–1100. *Paywalled.* — Side information raises the growth rate of wealth by at most its mutual information with the market, so a bit can at most double wealth.
- **Cover, T. M. & Thomas, J. A. (2006).** [*Elements of Information Theory*, 2nd ed.](https://www.wiley.com/en-us/Elements+of+Information+Theory,+2nd+Edition-p-9780471241959) Wiley. — The standard text. Chapters 2, 7, 8, 9 and 11 cover Appendix A. Chapters 6 and 16 cover gambling and portfolio theory.
- **Thorp, E. O. (2006).** ["The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market."](https://gwern.net/doc/statistics/decision/2006-thorp.pdf) In *Handbook of Asset and Liability Management*, Vol. 1, 385–428. North-Holland. — The practitioner's case for fractional Kelly (§6.6).
- **Kraskov, A., Stögbauer, H. & Grassberger, P. (2004).** ["Estimating Mutual Information."](https://arxiv.org/abs/cond-mat/0305641) *Physical Review E* 69, 066138. — The nearest-neighbour estimator of mutual information (§7.5, A.13).
- **Paninski, L. (2003).** ["Estimation of Entropy and Mutual Information."](https://www.cns.nyu.edu/pub/lcv/paninski-infoEst-2003.pdf) *Neural Computation* 15(6), 1191–1253. — Why simple estimators of mutual information are biased, and by how much (A.13).

## 10.2 Performance measurement

- **Treynor, J. L. (1965).** "How to Rate Management of Investment Funds." *Harvard Business Review* 43(1), 63–75. — Excess return per unit of beta (§5.1).
- **Sharpe, W. F. (1966).** ["Mutual Fund Performance."](http://www.stat.ucla.edu/~nchristo/statistics_c183_c283/sharpe__mutual_fund_performance.pdf) *Journal of Business* 39(1), 119–138. [[DOI]](https://doi.org/10.1086/294846) — The reward-to-variability ratio, introduced to rank mutual funds.
- **Jensen, M. C. (1968).** ["The Performance of Mutual Funds in the Period 1945–1964."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=244153) *Journal of Finance* 23(2), 389–416. [[DOI]](https://doi.org/10.1111/j.1540-6261.1968.tb00815.x) — Alpha as the intercept of the market regression.
- **Treynor, J. L. & Black, F. (1973).** ["How to Use Security Analysis to Improve Portfolio Selection."](https://doi.org/10.1086/295508) *Journal of Business* 46(1), 66–86. *Paywalled.* — The appraisal ratio, and the result that squared appraisal ratios add to the market's squared Sharpe ratio (§3.3).
- **Sharpe, W. F. (1994).** ["The Sharpe Ratio."](https://web.stanford.edu/~wfsharpe/art/sr/sr.htm) *Journal of Portfolio Management* 21(1), 49–58. [[DOI]](https://doi.org/10.3905/jpm.1994.409501) — The ratio, defined by its author, with the differential-return interpretation that makes it leverage-invariant.
- **Sortino, F. A. & Price, L. N. (1994).** ["Performance Measurement in a Downside Risk Framework."](https://doi.org/10.3905/joi.3.3.59) *Journal of Investing* 3(3). *Paywalled.* — Downside deviation in place of standard deviation.
- **Modigliani, F. & Modigliani, L. (1997).** ["Risk-Adjusted Performance."](https://doi.org/10.3905/jpm.23.2.45) *Journal of Portfolio Management* 23(2), 45–54. *Paywalled.* — M², the Sharpe ratio restated as a return at the benchmark's risk.
- **Goodwin, T. H. (1998).** ["The Information Ratio."](https://doi.org/10.2469/faj.v54.n4.2196) *Financial Analysts Journal* 54(4), 34–43. *Paywalled.* — The information ratio and its t-statistic, methods of annualising it, and empirical distributions by style (§4.2).
- **Keating, C. & Shadwick, W. F. (2002).** ["A Universal Performance Measure."](https://people.duke.edu/~charvey/Teaching/BA453_2004/Keating_A_universal_performance.pdf) *Journal of Performance Measurement* 6(3), 59–84. — The Omega function.

## 10.3 Active management and the fundamental law

- **Ambachtsheer, K. P. (1974).** ["Profit Potential in an 'Almost Efficient' Market."](https://doi.org/10.3905/jpm.1974.408485) *Journal of Portfolio Management* 1(1), 84–87. *Paywalled.* — An early use of the information coefficient to describe forecasting skill.
- **Grinold, R. C. (1989).** ["The Fundamental Law of Active Management."](https://doi.org/10.3905/jpm.1989.409211) *Journal of Portfolio Management* 15(3), 30–37. *Paywalled.* — IR equals IC times the square root of breadth.
- **Grinold, R. C. (1994).** ["Alpha is Volatility Times IC Times Score."](https://doi.org/10.3905/jpm.1994.409482) *Journal of Portfolio Management* 20(4), 9–16. *Paywalled.* — The rule for turning scores into expected returns (§6.1).
- **Clarke, R., de Silva, H. & Thorley, S. (2002).** ["Portfolio Constraints and the Fundamental Law of Active Management."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=290916) *Financial Analysts Journal* 58(5), 48–66. [[DOI]](https://doi.org/10.2469/faj.v58.n5.2468) — The transfer coefficient, and the finding that the long-only constraint costs more than any other.
- **Clarke, R., de Silva, H. & Thorley, S. (2006).** ["The Fundamental Law of Active Portfolio Management."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=934440) *Journal of Investment Management* 4(3). — The exact version with a full covariance matrix.
- **Campbell, J. Y. & Thompson, S. B. (2008).** ["Predicting Excess Stock Returns Out of Sample: Can Anything Beat the Historical Average?"](https://www.nber.org/papers/w11468) *Review of Financial Studies* 21(4), 1509–1531. [[DOI]](https://doi.org/10.1093/rfs/hhm055) — How a small predictive $R^2$ becomes a large improvement in Sharpe ratio (§3.3).
- **Gârleanu, N. & Pedersen, L. H. (2013).** ["Dynamic Trading with Predictable Returns and Transaction Costs."](https://nbgarleanu.github.io/DynTrad.pdf) *Journal of Finance* 68(6), 2309–2340. — Trading partway toward an aim portfolio (§6.5).
- **Meucci, A. (2009).** ["Managing Diversification."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1358533) *Risk* 22(5), 74–79. — The effective number of bets as the exponential of an entropy (A.12).

## 10.4 The statistics of skill

- **Newey, W. K. & West, K. D. (1987).** ["A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix."](https://www.jstor.org/stable/1913610) *Econometrica* 55(3), 703–708. *Paywalled.* — Standard errors for overlapping windows (§6.2).
- **Efron, B. & Morris, C. (1977).** ["Stein's Paradox in Statistics."](https://doi.org/10.1038/scientificamerican0577-119) *Scientific American* 236(5), 119–127. *Paywalled.* — Why shrinking noisy estimates toward a common value beats using them raw (Appendix B.21).
- **Jagannathan, R. & Ma, T. (2003).** ["Risk Reduction in Large Portfolios: Why Imposing the Wrong Constraints Helps."](https://www.nber.org/papers/w8922) *Journal of Finance* 58(4), 1651–1684. — Portfolio constraints act as shrinkage on the covariance matrix (Appendix B.41).
- **Lo, A. W. (2002).** ["The Statistics of Sharpe Ratios."](https://doi.org/10.2469/faj.v58.n4.2453) *Financial Analysts Journal* 58(4), 36–52. *Paywalled.* — The standard error of a Sharpe ratio, and the autocorrelation-corrected annualisation of §2.4.
- **Opdyke, J. D. (2007).** ["Comparing Sharpe Ratios: So Where Are the p-Values?"](https://doi.org/10.1057/palgrave.jam.2250084) *Journal of Asset Management* 8(5), 308–336. *Paywalled.* — The standard error under skewness and kurtosis (§4.1).
- **Goyal, A. & Wahal, S. (2008).** ["The Selection and Termination of Investment Management Firms by Plan Sponsors."](https://doi.org/10.1111/j.1540-6261.2008.01375.x) *Journal of Finance* 63(4), 1805–1847. *Paywalled.* — Hiring on past returns does not deliver future returns (§6.7).
- **Bailey, D. H. & López de Prado, M. (2012).** ["The Sharpe Ratio Efficient Frontier."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643) *Journal of Risk* 15(2), 3–44. [[DOI]](https://doi.org/10.21314/jor.2012.255) — The probabilistic Sharpe ratio and the minimum track-record length.
- **Bailey, D. H. & López de Prado, M. (2014).** ["The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551) *Journal of Portfolio Management* 40(5), 94–107. — The Sharpe ratio corrected for the number of trials.
- **Harvey, C. R. & Liu, Y. (2015).** ["Backtesting."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2345489) *Journal of Portfolio Management* 42(1), 13–28. [[DOI]](https://doi.org/10.3905/jpm.2015.42.1.013) — Haircutting Sharpe ratios for multiple testing.
- **Harvey, C. R., Liu, Y. & Zhu, H. (2016).** ["…and the Cross-Section of Expected Returns."](https://www.nber.org/papers/w20592) *Review of Financial Studies* 29(1), 5–68. — The multiple-testing problem in factor research, and the case for $t > 3$.

## 10.5 Critiques and failure modes

- **Hansen, L. P. & Jagannathan, R. (1991).** ["Implications of Security Market Data for Models of Dynamic Economies."](https://doi.org/10.1086/261749) *Journal of Political Economy* 99(2), 225–262. *Paywalled.* — The volatility of the discount factor bounds every Sharpe ratio (§7.4).
- **Cochrane, J. H. & Saá-Requejo, J. (2000).** ["Beyond Arbitrage: Good-Deal Asset Price Bounds in Incomplete Markets."](https://www.johnhcochrane.com/research-all/beyond-arbitrage-good-deal-asset-price-bounds-in-incomplete-markets) *Journal of Political Economy* 108(1), 79–119. [[DOI]](https://doi.org/10.1086/262112) — Ruling out Sharpe ratios that are too good.
- **Qian, E. & Hua, R. (2004).** ["Active Risk and Information Ratio."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=569281) *Journal of Investment Management* 2(3). — Variation in the IC as a source of risk the risk model does not see, and the ceiling it puts on the information ratio (§7.1).
- **Buckle, D. (2004).** ["How to Calculate Breadth: An Evolution of the Fundamental Law of Active Portfolio Management."](https://link.springer.com/article/10.1057/palgrave.jam.2240118) *Journal of Asset Management* 4(6), 393–405. *Paywalled.* — Correlation among forecasts in the breadth term.
- **Getmansky, M., Lo, A. W. & Makarov, I. (2004).** ["An Econometric Model of Serial Correlation and Illiquidity in Hedge Fund Returns."](https://www.nber.org/papers/w9571) *Journal of Financial Economics* 74(3), 529–609. — Smoothed returns, and the Sharpe ratios they inflate (§7.3).
- **Goetzmann, W., Ingersoll, J., Spiegel, M. & Welch, I. (2007).** ["Portfolio Performance Manipulation and Manipulation-Proof Performance Measures."](https://www.ivo-welch.info/research/journalcopy/2007-rfs.pdf) *Review of Financial Studies* 20(5), 1503–1546. — Any mean-variance measure can be gamed with options; this paper derives the measure that cannot (§5.3).
- **Zhou, G. (2008).** ["On the Fundamental Law of Active Portfolio Management: What Happens If Our Estimates Are Wrong?"](https://www.pm-research.com/content/iijpormgmt/34/4/26) *Journal of Portfolio Management* 34(4), 26–33. *Paywalled.* — Estimation error in alphas, and how scaling recovers value.
- **McLean, R. D. & Pontiff, J. (2016).** ["Does Academic Research Destroy Stock Return Predictability?"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2156623) *Journal of Finance* 71(1), 5–32. [[DOI]](https://doi.org/10.1111/jofi.12365) — Information decays after publication (§7.5).
- **Ding, Z. & Martin, R. D. (2017).** ["The Fundamental Law of Active Management: Redux."](https://pdfs.semanticscholar.org/9cee/6ab8aaefee12ec74487798e04df91033f356.pdf) *Journal of Empirical Finance* 43, 91–114. — The law rebuilt with a random IC in a cross-sectional factor model.
- **Samuelson, P. A. (1971).** ["The 'Fallacy' of Maximizing the Geometric Mean in Long Sequences of Investing or Gambling."](https://finance.martinsewell.com/money-management/Samuelson1971.pdf) *Proceedings of the National Academy of Sciences* 68, 2493–2496. — Why growth optimality is not a utility recommendation.

## 10.6 Books

- **Grinold, R. C. & Kahn, R. N. (1999).** [*Active Portfolio Management*, 2nd ed.](https://archive.org/details/activeportfoliom0000grin) McGraw-Hill. — The practitioner's framework: IC, breadth, the fundamental law, the alpha rule, and the calibration of what good looks like.
- **Pav, S. E. (2021).** [*The Sharpe Ratio: Statistics and Applications*.](https://www.routledge.com/The-Sharpe-Ratio-Statistics-and-Applications/Pav/p/book/9781032019307) Chapman & Hall/CRC. — The sampling distribution of the Sharpe ratio, treated in full in one place.
- **Isichenko, M. (2021).** [*Quantitative Portfolio Management: The Art and Science of Statistical Arbitrage*.](https://www.wiley.com/en-us/Quantitative+Portfolio+Management:+The+Art+and+Science+of+Statistical+Arbitrage-p-9781119821328) Wiley. — A practitioner's account of forecasting, combining forecasts and trading them, including the costs.
- **Paleologo, G. A. (2021).** [*Advanced Portfolio Management: A Quant's Guide for Fundamental Investors*.](https://openlibrary.org/books/OL33824468M/Advanced_Portfolio_Management) Wiley. — Factor models, risk and sizing for discretionary managers, with the same arithmetic in plainer language.
- **Cover, T. M. & Thomas, J. A. (2006).** *Elements of Information Theory*, listed in §10.1.

## 10.7 Further sources cited in the appendices

- **Fama, E. F. & MacBeth, J. D. (1973).** ["Risk, Return, and Equilibrium: Empirical Tests."](https://doi.org/10.1086/260061) *Journal of Political Economy* 81(3), 607–636. *Paywalled.* — Cross-sectional regressions period by period, whose slopes are the ICs of standardised signals (B.38).
- **Glosten, L. R. & Milgrom, P. R. (1985).** ["Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders."](https://milgrom.people.stanford.edu/wp-content/uploads/1984/09/Bid-Ask-and-Transaction-Prices.pdf) *Journal of Financial Economics* 14(1), 71–100. — Why a market maker's spread exists (B.51).
- **Berk, J. B. & Green, R. C. (2004).** ["Mutual Fund Flows and Performance in Rational Markets."](https://www.nber.org/papers/w9275) *Journal of Political Economy* 112(6), 1269–1295. — Decreasing returns to scale in active management, and why capacity caps what skill earns (B.46).
- **Cochrane, J. H. (2005).** [*Asset Pricing*, revised ed.](https://press.princeton.edu/books/hardcover/9780691121376/asset-pricing) Princeton University Press. — The stochastic discount factor, and the bounds it puts on Sharpe ratios (B.52).
- **Brunnermeier, M. K., Nagel, S. & Pedersen, L. H. (2008).** ["Carry Trades and Currency Crashes."](https://www.nber.org/papers/w14473) *NBER Macroeconomics Annual* 23, 313–347. — The crash risk behind a carry strategy's smooth returns (B.50).
- **Asness, C. S., Moskowitz, T. J. & Pedersen, L. H. (2013).** ["Value and Momentum Everywhere."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2174501) *Journal of Finance* 68(3), 929–985. — Value and momentum across asset classes (B.36).
- **Frazzini, A., Israel, R. & Moskowitz, T. J. (2018).** ["Trading Costs."](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3229719) Working paper, SSRN 3229719. — Costs measured on a large manager's own trades. [Contested] as evidence on capacity, because the authors' firm runs these strategies (B.43, B.46).
- **Sheppard, W. F. (1899).** "On the Application of the Theory of Error to Cases of Normal Distribution and Normal Correlation." *Philosophical Transactions of the Royal Society A*. — The arcsine formula for the probability that two correlated normal variables share a sign (B.4).

## 10.8 If you only read six things

1. **[Grinold & Kahn (1999)](https://archive.org/details/activeportfoliom0000grin){target="_blank"}**, the chapters on the fundamental law and on forecasting: the framework this chapter reinterprets.
2. **[Kelly (1956)](https://www.princeton.edu/~wbialek/rome/refs/kelly_56.pdf){target="_blank"}**: 10 pages that connect information to money.
3. **[Qian & Hua (2004)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=569281){target="_blank"}**: why the fundamental law overpromises, and what to plan with instead.
4. **[Clarke, de Silva & Thorley (2002)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=290916){target="_blank"}**: the transfer coefficient, the cheapest source of information, which most portfolios ignore.
5. **[Lo (2002)](https://doi.org/10.2469/faj.v58.n4.2453){target="_blank"}** with **[Bailey & López de Prado (2014)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551){target="_blank"}**: how much a Sharpe ratio is worth as evidence, before and after a search.
6. **[Cover & Thomas (2006)](https://www.wiley.com/en-us/Elements+of+Information+Theory,+2nd+Edition-p-9780471241959){target="_blank"}**, chapters 2 and 6: entropy, mutual information and the horse race, for a reader who wants Appendix A done properly.

```{=latex}
\newpage
```

# Appendix A. Information theory for investors {#appendix-a-information-theory}

The main text uses a handful of results from information theory and states them without proof. This appendix builds them from scratch, in dependency order. It is written for a reader who is at home with probability but has not met the subject. Each entry gives the idea in words first, then the formal statement, then why the main text needs it. A few entries end with where to go deeper. Unless another source is given, [Cover & Thomas (2006)](https://www.wiley.com/en-us/Elements+of+Information+Theory,+2nd+Edition-p-9780471241959){target="_blank"} is the reference for all of it. The table lists the entries and the sections that use them.

| Entry | Used in | Entry | Used in |
|---|---|---|---|
| [A.1 Surprise and entropy](#a1) | §3.1 | [A.8 Fano's inequality](#a8) | §2.2 |
| [A.2 Bits and nats](#a2) | §2.6, §3.1 | [A.9 Fisher information](#a9) | §3.6, §4.1 |
| [A.3 Mutual information](#a3) | §2.6, §3.1 | [A.10 Kelly's horse race](#a10) | §3.2 |
| [A.4 The Gaussian pair](#a4) | §2.6, §3.1, §3.3, §6.3 | [A.11 Kelly in continuous markets](#a11) | §3.2, §3.6, §6.6 |
| [A.5 Relative entropy](#a5) | §3.6 | [A.12 Entropy as a count of bets](#a12) | §2.4, §4.4 |
| [A.6 Channel capacity](#a6) | §2.6 | [A.13 Estimating mutual information](#a13) | §7.5 |
| [A.7 Data processing](#a7) | §3.5 | | |

## A.1 Surprise and entropy {#a1}

**The idea.** An unlikely event is more informative than a likely one. Learning that the sun rose says nothing new. Learning that a 1-in-1,000 stock tripled says a lot. Shannon measured the information in observing an outcome by its **surprise**: the logarithm of one over its probability. The logarithm makes information from independent events add. The probabilities of two independent events multiply, so their surprises add. **Entropy** is the average surprise, the expected amount learned when the outcome is revealed. It therefore measures how uncertain the outcome was beforehand.

**Formally.** For a discrete random variable $X$ with probabilities $p(x)$, the surprise of outcome $x$ is $-\log p(x)$, and the entropy is

$$
H(X) \;=\; -\sum_x p(x)\log p(x) \;=\; \mathbb{E}\big[-\log p(X)\big].
$$

A fair coin has entropy $\log_2 2 = 1$ bit. A coin that lands heads 60% of the time has $H(0.6) = 0.971$ bits. A certain outcome has zero entropy. Among distributions on $m$ outcomes, the uniform one has the largest entropy, $\log m$. For a continuous variable with density $p(x)$, the analogue is the **differential entropy** $h(X) = -\int p(x)\log p(x)\,dx$. For a normal variable with variance $\sigma^2$, it is $\tfrac12\log(2\pi e\,\sigma^2)$. Differential entropy depends on the units of $X$ and can be negative, so on its own it is not an amount of information. The differences between differential entropies used below are amounts of information.

**Why it appears here.** §3.1 describes a forecast as a fraction of a coin toss.

**Deeper.** [Shannon (1948)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf){target="_blank"}, Part I; Cover & Thomas, chapter 2.

## A.2 Bits and nats {#a2}

**The idea.** The base of the logarithm sets the unit. Base two gives bits, the number of yes-or-no questions. Base $e$ gives nats, which make calculus cleaner. Finance uses nats implicitly, because log returns are natural logarithms.

**Formally.** One nat is $1/\ln 2 \approx 1.443$ bits, and one bit is $\ln 2 \approx 0.693$ nats. A growth rate of log wealth of $g$ per year, in natural-log units, is $g$ nats per year in the units of A.10. Wealth doubles once per $\ln 2$ nats, which is once per bit.

**Why it appears here.** Every conversion in §3 uses it. For example, $\mathrm{SR}^2/2$ nats a year is $\mathrm{SR}^2/(2\ln 2)$ bits a year.

## A.3 Conditional entropy and mutual information {#a3}

**The idea.** Knowing the forecast leaves less uncertainty about the outcome. The uncertainty that remains is the **conditional entropy**. The reduction is the **mutual information**: how much one variable reveals about the other. Mutual information is symmetric: the forecast reveals as much about the outcome as the outcome reveals about the forecast. It is never negative, and it is zero exactly when the two variables are independent.

**Formally.**

$$
H(Y \mid X) = -\mathbb{E}\big[\log p(Y \mid X)\big], \qquad
I(X;Y) = H(Y) - H(Y \mid X) = H(X) + H(Y) - H(X,Y).
$$

For continuous variables, the same formulas hold with differential entropies. The units cancel, so mutual information is a genuine amount of information. Two properties matter here. First, mutual information is unchanged by any one-to-one transformation of either variable, so replacing a forecast by its rank does not change it. Second, it counts every kind of dependence, not only the linear kind that a correlation measures.

**Why it appears here.** §2.6 and §3.1 use it to define the information a forecast carries. §3.1 also notes that the IC can understate a non-linear forecast.

## A.4 The Gaussian pair {#a4}

**The idea.** For a forecast and outcome that are jointly normal, all the dependence lies in the correlation. So the mutual information must be a function of the correlation alone. It is, and the function is simple.

**Formally.** Let $(X, Y)$ be jointly normal with unit variances and correlation $\rho$. For a forecast and its outcome, $\rho$ is the IC. Given $X$, $Y$ is normal with variance $1-\rho^2$, so

$$
I(X;Y) = h(Y) - h(Y\mid X)
= \tfrac12\ln(2\pi e) - \tfrac12\ln\!\big(2\pi e\,(1-\rho^2)\big)
= -\tfrac12 \ln\!\left(1-\rho^2\right)\ \text{nats}.
$$

Expanding the logarithm gives $I = \rho^2/2 + \rho^4/4 + \dots$. So for the correlations of real forecasts, $I \approx \rho^2/2$ nats, with an error under 0.2% at $\rho = 0.05$. The same calculation for a vector of forecasts, combined linearly, gives $-\tfrac12\ln(1-R^2)$, where $R^2$ is the squared multiple correlation. The combined IC of §6.3 therefore enters the information in exactly the same way as a single IC.

**Why it appears here.** §2.6 uses it to connect signal-to-noise with information. §3.1 uses it for the table of bits per bet, §3.3 for information per bet as $\mathrm{IC}^2/2$, and §6.3 for the combined IC of several signals.

## A.5 Relative entropy {#a5}

**The idea.** Suppose the data come from distribution $P$, and an alternative $Q$ is under consideration. Each observation provides some evidence for $P$ over $Q$: the logarithm of the ratio of their likelihoods. The **relative entropy**, or Kullback–Leibler divergence, is the average of that evidence per observation when $P$ is true. It is the rate at which an observer learns that the world is $P$ and not $Q$.

**Formally.**

$$
D(P\,\|\,Q) = \mathbb{E}_P\!\left[\log\frac{p(X)}{q(X)}\right] \ \ge\ 0,
$$

with equality only when $P = Q$. Relative entropy is not symmetric. For two normal distributions with the same variance, $D\big(\mathcal{N}(\mu_1,\sigma^2)\,\|\,\mathcal{N}(\mu_2,\sigma^2)\big) = (\mu_1-\mu_2)^2/(2\sigma^2)$. Mutual information is a special case: $I(X;Y) = D\big(P_{XY}\,\|\,P_X P_Y\big)$, the evidence that $X$ and $Y$ are dependent. The **Chernoff–Stein lemma** makes the "rate of learning" precise. Test $P$ against $Q$ with $n$ observations, and hold fixed the chance of wrongly rejecting $P$. Then the best achievable chance of wrongly accepting $P$ when $Q$ is true falls like $e^{-nD(P\|Q)}$.

**Why it appears here.** §3.6 uses it for the evidence a year of returns provides for skill: $D\big(\mathcal{N}(\mu,\sigma^2)\,\|\,\mathcal{N}(0,\sigma^2)\big) = \mathrm{SR}^2/2$, the same number as the Kelly growth rate. In Chernoff–Stein's terms, hold fixed the chance of dismissing a manager who really has skill. Then the chance of backing one who has none falls like $e^{-T\,\mathrm{SR}^2/2}$ over $T$ years.

## A.6 Channel capacity and the Shannon–Hartley formula {#a6}

**The idea.** A **channel** takes an input and returns a noisy version of it. Its **capacity** is the most information per use that can pass through it, with the input distribution chosen as cleverly as possible. Shannon's central theorem says that information can be sent essentially without error at any rate below capacity, and at no rate above it.

**Formally.** The capacity is $C = \max_{p(x)} I(X;Y)$. Consider the additive Gaussian channel $Y = X + Z$, with input power (variance) limited to $\sigma_X^2$ and Gaussian noise $Z$ of variance $\sigma_Z^2$. The maximising input is itself Gaussian, and

$$
C = \tfrac12\log_2\!\left(1 + \frac{\sigma_X^2}{\sigma_Z^2}\right) \ \text{bits per use}.
$$

A channel used $2B$ times a second, with bandwidth $B$, carries $B\log_2(1 + \sigma_X^2/\sigma_Z^2)$ bits a second. That is the Shannon–Hartley formula in its engineering form. §2.6 uses the per-use form above.

**Why it appears here.** §2.6 uses it. In the model of §2.2, the input is $X = \mathrm{IC}\cdot s$ and the noise is $Z = \sqrt{1-\mathrm{IC}^2}\,\varepsilon$. So the signal-to-noise ratio is $\mathrm{IC}^2/(1-\mathrm{IC}^2)$, and the capacity is $-\tfrac12\log_2(1-\mathrm{IC}^2)$, the Gaussian mutual information of A.4. In forecasting, no one chooses the input. The formula matters only because, in the normal case, signal-to-noise and information are the same quantity in different units.

## A.7 The data-processing inequality {#a7}

**The idea.** Suppose $Z$ is computed from $Y$, perhaps with extra randomness, but without looking at $X$ again. Then $Z$ cannot know more about $X$ than $Y$ did. Processing can lose information about the source but can never gain it.

**Formally.** If $X \to Y \to Z$ is a Markov chain, meaning that given $Y$, $Z$ is independent of $X$, then

$$
I(X;Z) \;\le\; I(X;Y).
$$

Equality holds when $Z$ retains everything in $Y$ that is relevant to $X$, that is, when $Z$ is a **sufficient statistic** for $X$. The proof takes two lines. The chain rule splits what a pair of variables reveals about $X$ into two parts: what one of them reveals, plus what the other adds once the first is known. The second part is the **conditional mutual information**, such as $I(X;Z\mid Y)$, which, like mutual information, is never negative. Splitting in both orders gives $I(X; Y, Z) = I(X;Y) + I(X; Z \mid Y) = I(X;Z) + I(X;Y\mid Z)$. The Markov property makes $I(X;Z\mid Y) = 0$, so $I(X;Z) = I(X;Y) - I(X;Y\mid Z) \le I(X;Y)$.

**Why it appears here.** §3.5 relies on it. Returns, forecast and positions form such a chain whenever the positions are built from the forecast and from inputs that carry no further information about returns. The positions then cannot know more than the forecast. The result of §3.4, in which a zero-IC signal raises the combined IC, is not a violation. The second signal is a new input about the noise, so the chain differs from the one the inequality describes.

## A.8 Fano's inequality {#a8}

**The idea.** If a forecast carries little information about a yes-or-no outcome, it cannot call that outcome correctly much more than half the time. Fano's inequality turns that intuition into a bound.

**Formally.** Let $\hat Y$ be a guess of a discrete outcome $Y$ made from $X$, with error probability $P_e$. Then $H_b(P_e) + P_e\log(m - 1) \ge H(Y \mid X)$, where $m$ is the number of possible outcomes and $H_b$ is the entropy of a coin with bias $P_e$. For a fair binary outcome, $m = 2$ and $H(Y\mid X) = 1 - I$ bits, so $H_b(P_e) \ge 1 - I$. The table evaluates the bound.

| IC | 0.02 | 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|
| Information about the direction, at most (bits) | 0.0003 | 0.0018 | 0.0073 | 0.029 |
| Best hit rate Fano allows | 51.0% | 52.5% | 55.0% | 60.1% |
| Hit rate of the Gaussian forecast (§2.2) | 50.6% | 51.6% | 53.2% | 56.4% |

The first row uses the Gaussian mutual information as a bound. The direction of an outcome carries no more information than the outcome itself, so the bound applies to the direction too.

**Why it appears here.** §2.2 gives hit rates, and this inequality shows that information caps them. With 0.0018 bits per bet, no forecasting method, however clever, can call the direction of a fair outcome correctly more than 52.5% of the time.

## A.9 Fisher information and the Cramér–Rao bound {#a9}

**The idea.** Relative entropy measures how distinguishable two distributions are. When the two differ only slightly in one parameter, the relative entropy is proportional to the squared difference. The constant of proportionality is half the **Fisher information**, which measures how sharply the data respond to the parameter. The more sharply they respond, the more precisely the parameter can be estimated. The Cramér–Rao bound makes that statement exact.

**Formally.** For a family of densities $p(x;\theta)$, the Fisher information per observation is $\mathcal{I}(\theta) = \mathbb{E}\big[(\partial_\theta \ln p(X;\theta))^2\big]$, and $D\big(p_\theta \,\|\, p_{\theta+\delta}\big) \approx \tfrac12\,\mathcal{I}(\theta)\,\delta^2$. Any unbiased estimator from $n$ independent observations has variance at least $1/\big(n\,\mathcal{I}(\theta)\big)$. Maximum likelihood attains the bound in large samples. For normal returns with unknown mean and variance, the per-period Sharpe ratio $\mathrm{SR}$ has inverse Fisher information $1 + \mathrm{SR}^2/2$. This is the source of the standard error $\sqrt{(1+\mathrm{SR}^2/2)/n}$ of §4.1. The estimate's variance from the mean is $1/n$, and from the standard deviation it is $\mathrm{SR}^2/(2n)$.

**Why it appears here.** §3.6 and §4.1 use it. The standard error of a Sharpe ratio is the Cramér–Rao bound, so no estimator that uses returns alone can do much better.

## A.10 Kelly's horse race {#a10}

**The idea.** A gambler bets on repeated races and wants wealth to grow as fast as possible. Wealth multiplies from race to race, so the right objective is the expected logarithm of the multiplier. The optimal strategy then bets on each horse in proportion to the probability that it wins. With private information, the probabilities are the conditional ones, and the gain in growth rate is exactly the mutual information.

**Formally.** Horse $x$ wins with probability $p(x)$ and pays $o(x)$ for each unit bet on it. The gambler spreads all their wealth across horses in fractions $b(x)$. After a race won by $X$, wealth is multiplied by $b(X)\,o(X)$, so the growth rate is

$$
g(b) = \sum_x p(x)\log\big(b(x)\,o(x)\big)
= \sum_x p(x)\log o(x) - H(X) - D(p\,\|\,b).
$$

The relative entropy term is never negative, and it vanishes at $b = p$. So proportional betting is optimal, and $g^\ast = \sum_x p(x)\log o(x) - H(X)$. With side information $Y$, the gambler bets $b(x\mid y) = p(x\mid y)$ and earns $g^\ast_Y = \sum_x p(x)\log o(x) - H(X\mid Y)$. The difference is

$$
g^\ast_Y - g^\ast = H(X) - H(X \mid Y) = I(X;Y),
$$

whatever the odds. With fair odds, $o(x) = 1/p(x)$, the first sum equals $H(X)$, and $g^\ast = 0$. Without information the gambler can only break even. With information, the growth rate itself equals the mutual information, which is the statement in §3.2. The two-horse example of §3.2 is this case with $o = 2$, $p = \tfrac12$ and a tip that is right 60% of the time.

**Why it appears here.** §3.2 relies on it, together with the corollary that a bit of information can at most double wealth.

**Deeper.** [Kelly (1956)](https://www.princeton.edu/~wbialek/rome/refs/kelly_56.pdf){target="_blank"}; Cover & Thomas, chapter 6.

## A.11 Kelly in continuous markets {#a11}

**The idea.** In a market with continuous trading and normally distributed returns, the horse race becomes a choice of leverage, and the growth rate has a simple closed form.

**Formally.** Hold a fraction $f$ of wealth in a strategy with excess return $\mu$ and volatility $\sigma$, rebalanced continuously. Log wealth grows in excess of cash at $g(f) = f\mu - \tfrac12 f^2\sigma^2$. The growth rate is maximised at $f^\ast = \mu/\sigma^2$, where $g^\ast = \mu^2/(2\sigma^2) = \mathrm{SR}^2/2$. At a fraction $c$ of the optimal leverage, $g = (2c - c^2)\,g^\ast$.

Now suppose the strategy's expected return is not fixed but given by a forecast. Write the standardised return as $y = \rho s + \sqrt{1-\rho^2}\,\varepsilon$, as in §2.2, with $s$ a standardised normal forecast and $\rho$ its correlation with a zero-mean return. Given $s$, the return has mean $\rho s$ and variance $1-\rho^2$. So the growth-optimal bettor earns the conditional $\mathrm{SR}^2/2$, which is $\rho^2 s^2/\big(2(1-\rho^2)\big)$. Averaging over $s$, whose mean square is one, gives $\rho^2/\big(2(1-\rho^2)\big) = \rho^2/2 + \rho^4/2 + \dots$ per bet. The mutual information of A.4 is $\rho^2/2 + \rho^4/4 + \dots$, so the two agree to leading order (the table in §3.2 compares them). In general markets, the gain from side information is at most its mutual information ([Barron & Cover, 1988](https://doi.org/10.1109/18.21241){target="_blank"}).

**Why it appears here.** §3.2 and §6.6 use it for the growth rate, the growth-optimal volatility of $\mathrm{SR}$, and the cost of overbetting.

**Deeper.** [Simple and Log Returns](log_returns.html) derives the growth rate from the log-return identities. [Thorp (2006)](https://gwern.net/doc/statistics/decision/2006-thorp.pdf){target="_blank"} covers practice.

## A.12 Entropy as a count of bets {#a12}

**The idea.** The exponential of an entropy is an **effective number** of equally likely outcomes. A fair die has entropy $\ln 6$, and $e^{\ln 6} = 6$. A loaded die that almost always shows six has entropy near zero and an effective number near one. The same device counts how many independent bets a portfolio really holds.

**Formally.** Decompose a portfolio's risk into contributions $p_j$ from $J$ uncorrelated sources, with $p_j \ge 0$ and $\sum_j p_j = 1$. The **effective number of bets** is $\exp\!\big(-\sum_j p_j \ln p_j\big)$. It equals $J$ when risk is spread evenly, and one when risk is concentrated in a single source ([Meucci, 2009](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1358533){target="_blank"}).

**Why it appears here.** §4.4 distinguishes it from breadth. Meucci's count measures how evenly risk is spread over independent sources. The breadth of the fundamental law counts independent bets, weighted by the information each carries. The two answer different questions. Both are smaller, usually much smaller, than the number of positions.

## A.13 Estimating mutual information from data {#a13}

**The idea.** Mutual information is defined from the true joint distribution, which is unknown. Estimating it from a sample is harder than estimating a correlation, because the simple estimators are biased upward. Any finite sample shows some apparent dependence, even between independent variables.

**Formally.** The plug-in estimator bins both variables and computes the mutual information of the empirical cell frequencies. With $B_X \times B_Y$ bins and $n$ observations, it is biased upward by roughly $(B_X - 1)(B_Y - 1)/(2n)$ nats ([Paninski, 2003](https://www.cns.nyu.edu/pub/lcv/paninski-infoEst-2003.pdf){target="_blank"}). With 10 bins on each axis, the bias equals the 0.00125 nats of an IC-0.05 forecast at about 32,000 observations. It falls to a tenth of that only at about 320,000 observations. Nearest-neighbour estimators ([Kraskov, Stögbauer & Grassberger, 2004](https://arxiv.org/abs/cond-mat/0305641){target="_blank"}) avoid binning and have much smaller bias. At these signal strengths, however, they too need very large samples.

**Why it appears here.** §7.5 concludes that mutual information is the right unit for reasoning about edge and a poor statistic for measuring it. For a signal that is close to Gaussian, the IC is a far more efficient estimate of the same quantity, through A.4.

```{=latex}
\newpage
```

# Appendix B. Concepts and prerequisites {#appendix-b-concepts-and-prerequisites}

The main text assumes a reader who is comfortable with means, standard deviations and correlations. It leaves the rest of its statistical and market vocabulary to context. This appendix defines that vocabulary for a reader who is technically strong but new to one side of it: a statistician who has never sat near a trading desk, or a practitioner whose statistics have gone rusty. None of it is needed to follow the argument. Much of it is needed to check the argument, or to use it.

The entries are ordered by dependency, so each relies only on those before it. They are grouped into four parts. Each entry gives the idea in words first, then the formal statement, then why the main text needs it. Where a canonical source exists, the entry ends with where to go deeper. Notation follows the main text's notation table, and each entry defines the symbols it alone uses. Where an entry needs information theory, it points to Appendix A rather than repeating it. Epistemic tags appear only on the few empirical claims. The table lists the entries and the sections that use them.

| Entry | Used in | Entry | Used in |
|---|---|---|---|
| [B.1 Standardisation](#b1) | Notation, §2.2 | [B.28 Drawdowns](#b28) | §2.5, §5.1 |
| [B.2 Pearson and rank correlation](#b2) | §3.7, §4.3 | [B.29 Downside deviation and Omega](#b29) | §5.1 |
| [B.3 The bivariate normal](#b3) | §2.2 | [B.30 Value at risk and expected shortfall](#b30) | §5.1 |
| [B.4 The arcsine formula](#b4) | §2.2 | [B.31 Expected utility](#b31) | §3.2, §5.3 |
| [B.5 Variance of a sum](#b5) | §2.3 | [B.32 Benchmarks and active weights](#b32) | §1.2, §4.2 |
| [B.6 Effective number of observations](#b6) | §2.4, §3.3 | [B.33 Beta, alpha and residual risk](#b33) | §4.2 |
| [B.7 Autocorrelation](#b7) | §2.4 | [B.34 The covariance matrix](#b34) | §3.5, §4.5 |
| [B.8 Skewness and kurtosis](#b8) | §4.1, §5.3 | [B.35 Factor risk models](#b35) | §2.4, §7.1 |
| [B.9 Standard errors](#b9) | §2.2 | [B.36 Factor premia](#b36) | §4.1 |
| [B.10 The delta method](#b10) | §4.1 | [B.37 Neutralising a signal](#b37) | §2.4, §3.4 |
| [B.11 Likelihood and bias](#b11) | §3.6, §4.1 | [B.38 Cross-sectional and time-series](#b38) | §1.4, §3.7 |
| [B.12 Hypothesis tests](#b12) | §3.6 | [B.39 Long-only and long-short](#b39) | §1.4, §3.5 |
| [B.13 Power](#b13) | §3.6 | [B.40 Mean-variance optimisation](#b40) | §3.3, §4.5 |
| [B.14 Likelihood ratios and base rates](#b14) | §3.6, §6.7 | [B.41 Portfolio constraints](#b41) | §1.2, §6.5 |
| [B.15 Multiple testing](#b15) | §3.6, §4.7 | [B.42 Risk budgeting](#b42) | §6.6 |
| [B.16 The expected maximum of $K$ trials](#b16) | §4.7 | [B.43 Transaction costs](#b43) | §1.4, §3.5 |
| [B.17 PSR and minimum track record](#b17) | §4.7 | [B.44 Signal decay](#b44) | §1.4, §3.5 |
| [B.18 Overlap and HAC standard errors](#b18) | §6.2 | [B.45 The aim portfolio](#b45) | §6.5 |
| [B.19 Regression and $R^2$](#b19) | §2.2, §3.3 | [B.46 Capacity](#b46) | §3.7, §4.1 |
| [B.20 Combining predictors](#b20) | §3.4, §6.3 | [B.47 Data biases](#b47) | §4.3, §6.2 |
| [B.21 Estimation error and shrinkage](#b21) | §3.5, §6.3 | [B.48 Universes and quantiles](#b48) | §2.2, §6.2 |
| [B.22 Backtests and overfitting](#b22) | §1.3, §4.7 | [B.49 Return smoothing](#b49) | §2.4, §7.3 |
| [B.23 Stationarity and regimes](#b23) | §4.7 | [B.50 Options and short tails](#b50) | §4.6, §5.3 |
| [B.24 Excess return](#b24) | Notation, §4.1 | [B.51 Market making](#b51) | §4.1 |
| [B.25 Volatility and annualisation](#b25) | §2.3, §2.5 | [B.52 The stochastic discount factor](#b52) | §7.4 |
| [B.26 Leverage](#b26) | §4.1 | [B.53 Anomalies and decay](#b53) | §7.5 |
| [B.27 Log returns and growth](#b27) | §3.2 | [B.54 The institutional landscape](#b54) | §4.2, §6.7 |

---

**Part I — Statistics and estimation.** Every number in the main text is an estimate, and most of its arguments concern how good an estimate it is. These entries build the machinery in order. They start with standardised variables and correlation and the normal model behind the IC. They continue with how variances add and what correlation does to them, then standard errors and how to propagate them. Tests, evidence and the cost of searching come next. The part ends with regression, and with what happens when estimated inputs are handed to an optimiser.

## B.1 Standardisation and cross-sectional z-scores {#b1}

**The idea.** A raw signal arrives in whatever units its inputs had, such as a price-to-book ratio or a count of analyst upgrades. Before signals can be compared, combined or turned into positions, they need a common scale. Standardising provides one. Subtract the mean and divide by the standard deviation. Every signal, in every period, then has mean zero and variance one, and a score of $+2$ means two standard deviations above average, whatever was measured. In a cross-sectional strategy, the mean and standard deviation are both taken across assets on each date. This also strips out anything common to every asset on that day.

**Formally.** For signal values $x_{i,t}$ on $N$ assets at date $t$, the cross-sectional **z-score** is

$$
s_{i,t} = \frac{x_{i,t} - \bar x_t}{\operatorname{sd}_t(x)}, \qquad \bar x_t = \frac1N\sum_{i=1}^N x_{i,t},
$$

where $\operatorname{sd}_t$ is the standard deviation across assets at $t$. For standardised variables, covariance and correlation coincide: $\operatorname{Corr}(x,y) = \mathbb{E}[s_x s_y]$. So the IC is also the average payoff of a position equal to the score (§2.3). The outcome can be standardised the same way. Alternatively, as in §6.1, it can be standardised asset by asset: $y_i$ is the residual return divided by the residual volatility $\sigma_i$. That choice is what lets $\alpha_i = \sigma_i \times \mathrm{IC} \times s_i$ convert back into returns. [Practice] Extreme scores are usually clipped (winsorised), often at about $\pm 3$, so that one bad data point cannot dominate a portfolio.

**Why it appears here.** The notation table defines $s$ and $y$ as standardised. The model of §2.2 and the alpha rule of §6.1 depend on it, and §6.3 combines signals only after standardising them.

## B.2 Correlation: Pearson and rank {#b2}

**The idea.** A correlation measures, on a scale from $-1$ to $+1$, how closely two quantities move together once their units are removed. The ordinary (Pearson) correlation uses the values themselves. So one extreme observation, such as a stock that quadruples on a takeover bid, can dominate it. The rank (Spearman) correlation replaces each value by its position in the sorted list, which bounds how much any one observation can contribute. It asks only whether higher forecasts go with higher outcomes, not by how much.

**Formally.** For $n$ pairs,

$$
r = \frac{\sum_i (x_i - \bar x)(y_i - \bar y)}{\sqrt{\sum_i (x_i - \bar x)^2\,\sum_i (y_i - \bar y)^2}},
$$

which is the sample version of $\operatorname{Cov}(X,Y)/(\sigma_X\sigma_Y)$. Spearman's $r_s$ applies the same formula to the ranks. With no ties, it equals $1 - 6\sum_i d_i^2/\big(n(n^2-1)\big)$, where $d_i$ is the difference between the two ranks of pair $i$. Because it works with ranks, the rank IC is unchanged by any increasing transformation of the signal, a property it shares with mutual information ([A.3](#a3)). For jointly normal variables with correlation $\rho$, the population Spearman correlation is $(6/\pi)\arcsin(\rho/2) \approx 0.955\,\rho$. On well-behaved data, a rank IC therefore runs about 5% below the Pearson IC. A much larger gap between the two points to outliers.

**Why it appears here.** §3.7 and §4.3 present the rank IC as the usual report. The checklist of §6.2 puts ranks first and uses Pearson as a check.

## B.3 The bivariate normal distribution {#b3}

**The idea.** Two quantities that are each normally distributed and linearly related are described completely by their means, their standard deviations and one correlation. This is the model behind most of §2 and §3. Once forecast and outcome are jointly normal, the hit rate, the information and the best forecast are all functions of the IC alone. The model's most useful property is what conditioning does. Learning one variable shifts the other's mean in proportion to the correlation and shrinks its variance. The shrinkage is the same whatever value was observed.

**Formally.** $(X, Y)$ is standard bivariate normal with correlation $\rho$ if each variable is $\mathcal{N}(0,1)$ and the joint density is

$$
p(x,y) = \frac{1}{2\pi\sqrt{1-\rho^2}}\,\exp\!\left(-\frac{x^2 - 2\rho xy + y^2}{2(1-\rho^2)}\right).
$$

Then $Y$ given $X = x$ is $\mathcal{N}(\rho x,\ 1-\rho^2)$. Equivalently, $Y = \rho X + \sqrt{1-\rho^2}\,\varepsilon$, with $\varepsilon \sim \mathcal{N}(0,1)$ independent of $X$. This is the model of §2.2 with $X = s$ and $\rho = \mathrm{IC}$. On its own, that linear model needs only noise uncorrelated with the signal. Joint normality is the extra assumption behind the hit-rate rule of §2.2 and the information formula of [A.4](#a4). $\Phi(z) = P(X \le z)$ is the standard normal distribution function.

**Why it appears here.** §2.2 uses it, and so does §3.2, where a bet's conditional mean $\mathrm{IC}\cdot s$ and variance $1 - \mathrm{IC}^2$ set its growth-optimal size.

## B.4 Sheppard's arcsine formula {#b4}

**The idea.** How often does a forecast call the direction right, if forecast and outcome are jointly normal ([B.3](#b3)) with correlation $\rho$? A picture answers the question. Any such pair can be written as the projections of one random point in the plane onto two fixed axes at an angle $\theta$ to each other, with $\cos\theta = \rho$. The two projections have opposite signs exactly when the point falls in one of two opposite wedges, each of angle $\theta$. That happens with probability $\theta/\pi$. Uncorrelated variables sit at right angles and agree half the time. Perfectly correlated variables share an axis and always agree.

**Formally.** Let $Z$ be a standard normal vector in the plane, and let $u$ and $v$ be unit vectors at angle $\theta = \arccos\rho$. Set $X = u^\top Z$ and $Y = v^\top Z$. Then $(X, Y)$ is standard bivariate normal with correlation $\rho$, and

$$
P(XY > 0) = 1 - \frac{\arccos\rho}{\pi} = \frac12 + \frac{\arcsin\rho}{\pi},
$$

using $\arccos\rho = \pi/2 - \arcsin\rho$. For small $\rho$, $\arcsin\rho \approx \rho$, and the hit rate is close to $\tfrac12 + \rho/\pi$.

**Why it appears here.** The hit-rate table of §2.2 and the discussion in §4.6 use it to link hit rate and IC for jointly normal forecasts. [A.8](#a8) bounds the hit rate of any method from the information alone.

**Deeper.** Sheppard, W. F. (1899), "On the Application of the Theory of Error to Cases of Normal Distribution and Normal Correlation", *Philosophical Transactions of the Royal Society A*.

## B.5 Variance of a sum, and the central limit theorem {#b5}

**The idea.** When independent random quantities are added, their means add and so do their variances. Standard deviations therefore add only "in quadrature", like the sides of a right-angled triangle. Ten independent bets of equal size have 10 times the expected profit and only $\sqrt{10}$ times the standard deviation. Correlation breaks this rule: positively correlated terms add extra variance through every pair. The central limit theorem adds a second fact. A sum of many independent terms with finite variance is close to normal, whatever each term's own distribution. That is why annual returns, average ICs and t-statistics are routinely treated as normal even when daily returns are not.

**Formally.** For any random variables,

$$
\operatorname{Var}\Big(\sum_{i=1}^n X_i\Big) = \sum_{i=1}^n \operatorname{Var}(X_i) + 2\sum_{i<j}\operatorname{Cov}(X_i, X_j).
$$

With independent terms of standard deviation $v$, the sum has standard deviation $\sqrt n\,v$, and the average has standard deviation $v/\sqrt n$. If the $X_i$ are independent and identically distributed with mean $m$, then $\sqrt n\,(\bar X - m)/v$ approaches $\mathcal{N}(0,1)$ as $n$ grows. Convergence is slower when the terms are skewed or fat-tailed. Versions of the theorem exist for terms whose dependence fades with distance.

**Why it appears here.** The square-root law of §2.3 rests on it. So do §2.1 and §2.5, where the t-statistic and the chance of a losing period, $\Phi(-\mathrm{SR}\sqrt{\tau})$, rely on normal sums.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), section 2.4, on the two limit theorems and what they require.

## B.6 Equicorrelation and the effective number of observations {#b6}

**The idea.** Picture each of $N$ bets as a private surprise plus a share of one common surprise. Averaging across bets washes out the private parts but never the common one. So beyond some point, adding bets stops reducing risk. The **effective number** of independent bets is the number of truly independent bets that would give the same variance of the average. A tiny average correlation is enough to make it collapse. It can never exceed one over that correlation.

**Formally.** Let $X_1, \dots, X_N$ have common variance $v^2$ and pairwise correlation $\rho$. By [B.5](#b5),

$$
\operatorname{Var}(\bar X) = \frac{v^2}{N}\big(1 + (N-1)\rho\big), \qquad N_{\text{eff}} = \frac{N}{1+(N-1)\rho} \;\xrightarrow{\;N\to\infty\;}\; \frac1\rho .
$$

For $\rho \ge 0$, this is the one-factor picture made exact: $X_i = v\big(\sqrt\rho\,F + \sqrt{1-\rho}\,e_i\big)$, with $F$ and the $e_i$ independent and of unit variance. The same algebra sizes a combination of $n$ strategies with equal Sharpe ratio, equal risk and pairwise correlation $\rho$. The mean of the sum grows like $n$, and its standard deviation like $\sqrt{n(1+(n-1)\rho)}$. So

$$
\mathrm{SR}_{\text{combined}} = \mathrm{SR}\sqrt{\frac{n}{1+(n-1)\rho}} \;<\; \frac{\mathrm{SR}}{\sqrt\rho}.
$$

**Why it appears here.** §2.4 uses it to show that 500 bets correlated 0.01 count as 84. §3.3 uses it for the ceiling on combined Sharpe ratios, and §4.4 and §6.4 for the breadth divisor. Genuine variation in the IC (§7.1) acts as exactly such a common component.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), section 2.5, on effective sample size.

## B.7 Autocorrelation and the AR(1) process {#b7}

**The idea.** Autocorrelation is a series' correlation with its own past. Suppose this month's return tends to be followed by one of the same sign. Then shocks persist, months are not independent draws, and a year holds fewer than 12 independent observations. Annual variance is more than 12 times monthly variance, and multiplying a monthly Sharpe ratio by $\sqrt{12}$ overstates the annual one. Negative autocorrelation does the reverse. The simplest model of persistence is the first-order autoregression. In it, each period inherits a fixed fraction of the previous period's deviation from the mean.

**Formally.** The lag-$k$ autocorrelation is $\rho_k = \operatorname{Corr}(r_t, r_{t-k})$. For a stationary series with variance $\sigma^2$, [B.5](#b5) gives

$$
\operatorname{Var}\Big(\sum_{t=1}^{q} r_t\Big) = \sigma^2\Big(q + 2\sum_{k=1}^{q-1}(q-k)\,\rho_k\Big),
$$

because a lag of $k$ occurs $q-k$ times within a window of $q$ periods. The sum has mean $q\mu$. So the annual Sharpe ratio is the per-period one times $q/\sqrt{q + 2\sum_k (q-k)\rho_k}$, which is Lo's multiplier $\eta(q)$ of §2.4. The **AR(1)** process is $r_t - \mu = \phi\,(r_{t-1} - \mu) + e_t$, with $\lvert\phi\rvert < 1$ and independent noise $e_t$. It has $\rho_k = \phi^k$, the geometric decay assumed in the table of §2.4.

**Why it appears here.** §2.4 uses it, and so does §4.1's advice to check autocorrelation before annualising. In §7.3, smoothed marks produce it.

**Deeper.** [Lo (2002)](https://doi.org/10.2469/faj.v58.n4.2453){target="_blank"}; [Foundations of Econometrics](econometrics_foundations.html), section 8.2.

## B.8 Skewness, kurtosis and fat tails {#b8}

**The idea.** A mean and a standard deviation fix a distribution's centre and width. For a normal distribution, nothing more is needed. **Skewness** measures asymmetry. Negative skew is the shape of many small gains and occasional large losses, the signature of selling insurance. **Kurtosis** measures how much of the variance comes from rare, extreme outcomes. High kurtosis means fat tails: moves of five or 10 standard deviations are far more common than a normal distribution allows. Both quantities are estimated badly, because the few largest observations dominate them. A sample that happens to contain no crash shows neither.

**Formally.** For returns with mean $\mu$ and standard deviation $\sigma$,

$$
\gamma_3 = \frac{\mathbb{E}\big[(r-\mu)^3\big]}{\sigma^3}, \qquad \gamma_4 = \frac{\mathbb{E}\big[(r-\mu)^4\big]}{\sigma^4}.
$$

A normal distribution has $\gamma_3 = 0$ and $\gamma_4 = 3$. Many sources report **excess kurtosis**, $\gamma_4 - 3$, which is zero for the normal. The main text, like Opdyke's formula in §4.1, uses raw kurtosis. [Fact] Daily returns of most financial assets have kurtosis well above 3.

**Why it appears here.** §4.1 uses it for the non-normal standard error of a Sharpe ratio, and §5.3 for what the ratio zoo adds when returns are not normal. In §2.5 and §6.6, fat tails make drawdowns worse and the growth-optimal leverage lower.

**Deeper.** [Simple and Log Returns](log_returns.html), section 4.3, on what return distributions actually look like.

## B.9 Standard errors and sampling distributions {#b9}

**The idea.** A statistic computed from data is itself a random variable. If history were rerun with fresh noise, the sample mean, the Sharpe ratio or the IC would come out different. Its spread across those imagined reruns is its **sampling distribution**, and the standard deviation of that distribution is the **standard error**. The standard error is the honest unit for any measured number. An IC of 0.03 with a standard error of 0.02 says far less than its value suggests.

**Formally.** The mean of $n$ independent observations with standard deviation $\sigma$ has standard error $\sigma/\sqrt n$ ([B.5](#b5)). A sample correlation from $n$ independent pairs, drawn from a bivariate normal with correlation $\rho$, has

$$
\operatorname{se}(r) \approx \frac{1-\rho^2}{\sqrt n},
$$

which is close to $1/\sqrt n$ at the ICs of real signals. The distribution of $r$ is skewed when $\rho$ is large. So intervals for correlations are usually built on **Fisher's transformation**, $z = \operatorname{artanh} r = \tfrac12\ln\big((1+r)/(1-r)\big)$, which is close to normal with standard error $1/\sqrt{n-3}$ whatever $\rho$ is. The mean of an IC series over $P$ periods has standard error $\hat\sigma_{\mathrm{IC}}/\sqrt P$. Once the IC varies from period to period, the periods, not the individual bets, are the independent observations.

**Why it appears here.** §2.2 uses it to show that 3,000 bets pin an IC down only to about $\pm 0.04$. §6.2 uses it for the standard error of the mean IC, and §7.1 for the $1/N$ sampling variance of one period's IC.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), sections 2.3 and 4.1.

## B.10 The delta method {#b10}

**The idea.** Many statistics are smooth functions of simpler ones. A Sharpe ratio, for example, is a mean divided by a standard deviation. Suppose the simpler statistics are approximately normal with known standard errors. A first-order Taylor expansion then turns their errors into the error of the function. Close to the true values, every smooth function looks linear, and the variance of a linear combination follows from [B.5](#b5).

**Formally.** Suppose $\hat\theta$ is approximately normal with mean $\theta$ and covariance matrix $\mathbf{V}/n$. Then for a smooth function $g$ with gradient $\nabla g$,

$$
\operatorname{Var}\big(g(\hat\theta)\big) \approx \frac1n\,\nabla g(\theta)^{\top}\,\mathbf{V}\,\nabla g(\theta).
$$

For the per-period Sharpe ratio, $g = \mu/\sigma$ with $\theta = (\mu, \sigma^2)$. So $\partial g/\partial\mu = 1/\sigma$ and $\partial g/\partial\sigma^2 = -\mu/(2\sigma^3)$. The sample mean and variance have $\operatorname{Var}(\hat\mu) = \sigma^2/n$, $\operatorname{Var}(\hat\sigma^2) \approx (\gamma_4 - 1)\sigma^4/n$ and $\operatorname{Cov}(\hat\mu, \hat\sigma^2) \approx \gamma_3\sigma^3/n$, with $\gamma_3$ and $\gamma_4$ as in [B.8](#b8). Substituting gives

$$
\operatorname{Var}\big(\widehat{\mathrm{SR}}\big) \approx \frac{1 - \gamma_3\,\mathrm{SR} + \tfrac{\gamma_4-1}{4}\,\mathrm{SR}^2}{n}.
$$

This is the non-normal formula of §4.1. At $\gamma_3 = 0$ and $\gamma_4 = 3$, it reduces to the normal $(1 + \mathrm{SR}^2/2)/n$. [A.9](#a9) reaches the normal case from the Fisher information.

**Why it appears here.** §4.1 gives two standard errors for a Sharpe ratio, and the probabilistic Sharpe ratio of §4.7 uses them.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), section 2.6; [Opdyke (2007)](https://doi.org/10.1057/palgrave.jam.2250084){target="_blank"}.

## B.11 Likelihood, maximum likelihood, bias and efficiency {#b11}

**The idea.** The **likelihood** turns a probability model around. A probability model asks how probable the data are for given parameters. The likelihood holds the observed data fixed and asks which parameter values make them most probable. **Maximum likelihood** picks the value that does. Two properties judge any estimator. **Bias** is a systematic tendency to miss in one direction. **Efficiency** is how small the estimator's random error is compared with the best achievable. Selection creates bias out of unbiased ingredients. Each backtest's Sharpe ratio may be an unbiased estimate, but the best of many is not.

**Formally.** For independent observations $x_1, \dots, x_n$ from a density $p(x;\theta)$, the log-likelihood is $\ell(\theta) = \sum_i \ln p(x_i;\theta)$. The maximum-likelihood estimate is the $\hat\theta$ that maximises it. An estimator's bias is $\mathbb{E}[\hat\theta] - \theta$, and its mean squared error is the squared bias plus its variance. Under regularity conditions, maximum likelihood is consistent and asymptotically normal with variance $1/\big(n\,\mathcal{I}(\theta)\big)$. That variance is the Cramér–Rao bound of [A.9](#a9), so no other well-behaved estimator does better in large samples. For normal returns, the maximum-likelihood estimates of $\mu$ and $\sigma^2$ are the sample mean and the sample variance with divisor $n$.

**Why it appears here.** [A.9](#a9) and [A.13](#a13) refer to attaining the bound and to upward bias. In §4.1, a Sharpe ratio kept after a search is biased upward. §3.6 reads evidence as a log-likelihood ratio.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), section 5.4.

## B.12 Hypothesis tests, p-values and confidence intervals {#b12}

**The idea.** A test asks whether the data would be surprising if nothing were going on. The **null hypothesis** is the uninteresting explanation, such as no edge or a true mean of zero. The test statistic measures how far the estimate sits from the null, in standard errors ([B.9](#b9)). The null is rejected when so large a distance would be rare under it. Rejecting a true null is a **type I error**, a false discovery, and the **significance level** caps its probability. A **p-value** is the probability, if the null were true, of a result at least as extreme as the one observed. It is not the probability that the null is true. That probability also depends on how plausible the null was beforehand.

**Formally.** For an estimate $\hat\theta$ with standard error $\operatorname{se}$, the t-statistic for the null $\theta = 0$ is $t = \hat\theta/\operatorname{se}$. For a mean return over $T$ years, it equals $\mathrm{SR}\sqrt T$. Under the null and the central limit theorem ([B.5](#b5)), $t$ is approximately $\mathcal{N}(0,1)$. A two-sided 5% test rejects when $\lvert t\rvert > 1.96$, which is the source of the "$t > 2$" convention. A one-sided test of a positive edge rejects when $t > 1.645$. The two-sided p-value is $2\,\Phi(-\lvert t\rvert)$. A 95% **confidence interval**, $\hat\theta \pm 1.96\,\operatorname{se}$, is the set of null values the test would not reject.

**Why it appears here.** §3.6 uses the bar of $t = 2$, and the 95% range of 0.38 to 1.62 for a Sharpe ratio of 1.0 measured over 10 years. That range is $1 \pm 1.96/\sqrt{10}$. Every correction in §4.7 adjusts this test.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), section 4.6.

## B.13 Power, and the expected versus the realised t-statistic {#b13}

**The idea.** A test can fail in two ways. [B.12](#b12) controls the first, a false discovery. The second, a **type II error**, is missing a real effect. The probability of avoiding it is the test's **power**. For a strategy with a genuine edge, the t-statistic after $T$ years is a noisy number centred on $\mathrm{SR}\sqrt T$, with a standard deviation of about one. So at the moment its expected value reaches 2, it is as likely to be below the bar as above it. Low power has a second cost, the **winner's curse**. Among strategies that clear the bar, measured Sharpe ratios overstate true ones, because clearing the bar took luck.

**Formally.** With true annual Sharpe ratio $\mathrm{SR}$, the realised $t$ is approximately $\mathcal{N}(\mathrm{SR}\sqrt T, 1)$. So the chance of clearing a bar $c$ is

$$
P(t > c) \approx \Phi\big(\mathrm{SR}\sqrt T - c\big).
$$

At $T = 4/\mathrm{SR}^2$, the expected $t$ is 2, and the power against $c = 2$ is one half. Power of 80% against $c = 1.96$ needs $\mathrm{SR}\sqrt T = 1.96 + 0.84 = 2.80$. That takes $T \approx 7.8/\mathrm{SR}^2$ years, nearly twice the rule of thumb.

**Why it appears here.** In §3.6, a strategy observed for exactly $4/\mathrm{SR}^2$ years clears $t = 2$ only about half the time. In §6.6, the uncertainty in an estimated Sharpe ratio argues for betting well below Kelly.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), section 4.7, on power and the winner's curse.

## B.14 Likelihood ratios, prior odds and base rates {#b14}

**The idea.** A significance test ([B.12](#b12)) asks how surprising the data are under one hypothesis. A **likelihood ratio** compares two hypotheses: how much more probable the data are if the manager is skilled than if not. It is the cleanest measure of evidence. Bayes's rule says exactly what it does to belief: it multiplies the odds held beforehand. So evidence alone cannot say how likely skill is. That probability also depends on the **base rate**, the share of skilled managers among those under consideration. When skill is rare, even strong evidence leaves the odds modest.

**Formally.** For hypotheses $H_1$ and $H_0$ and data $D$,

$$
\underbrace{\frac{P(H_1 \mid D)}{P(H_0 \mid D)}}_{\text{posterior odds}} \;=\; \underbrace{\frac{P(D \mid H_1)}{P(D \mid H_0)}}_{\text{likelihood ratio}} \;\times\; \underbrace{\frac{P(H_1)}{P(H_0)}}_{\text{prior odds}} .
$$

Log-likelihood ratios ([B.11](#b11)) from independent observations add. That is why evidence is counted in nats ([A.5](#a5)). When a hypothesis has free parameters, averaging its likelihood over a prior on them gives the **Bayes factor**. Suppose one manager in ten is skilled, so the prior odds are 1 to 9. A record with likelihood ratio $e^2 \approx 7.4$ moves the odds to 7.4 to 9, a probability of skill of 45%. Setting the alternative's mean at the observed estimate gives the largest likelihood ratio any alternative can achieve, $e^{t^2/2}$. Against an alternative fixed in advance, the ratio is smaller.

**Why it appears here.** §3.6 reads $t = 2$ as a likelihood ratio of 7.4, and §6.7 combines that evidence with base rates.

**Deeper.** Harvey, C. R. (2017), "Presidential Address: The Scientific Outlook in Financial Economics", *Journal of Finance*, on reading p-values through prior odds.

## B.15 Multiple testing {#b15}

**The idea.** Test one useless strategy at the 5% level, and the chance of a false discovery is 5%. Test 100, and the chance of at least one false discovery exceeds 99%. A researcher who reports only the best result has hidden the denominator. Corrections come in two strengths. The stricter kind controls the chance of even one false discovery in the whole family. The less strict kind controls the expected share of false discoveries among the results declared significant. **Data snooping** is the same problem spread across time and people. When one dataset is searched again and again, the honest trial count includes every researcher's trials.

**Formally.** Among $K$ tests, the **family-wise error rate** is the probability of at least one false rejection. **Bonferroni** tests each hypothesis at level $\alpha/K$. The probability of a union is at most the sum of the probabilities, so this holds the family-wise rate at or below $\alpha$, whatever the dependence. When the tests are correlated, it is conservative. The **false discovery rate** is the expected share of false rejections among all rejections. The **Benjamini–Hochberg** procedure controls it at $\alpha$ for independent or positively dependent tests. Sort the p-values $p_{(1)} \le \dots \le p_{(K)}$, and reject the $k$ smallest, where $k$ is the largest index with $p_{(k)} \le k\alpha/K$. For large $K$, the Bonferroni bar on $t$ grows like $\sqrt{2\ln K}$. So the evidence it demands, $t^2/2$, grows like $\ln K$.

**Why it appears here.** §3.6 tabulates the bars and derives the rule of one bit of evidence per doubling of the search. §4.7 uses it for the haircut Sharpe ratio and the $t > 3$ bar for new factors.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), sections 4.8 and 9.6; [Benjamini & Hochberg (1995)](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x){target="_blank"}; [Harvey, Liu & Zhu (2016)](https://www.nber.org/papers/w20592){target="_blank"}.

## B.16 The expected maximum of $K$ trials {#b16}

**The idea.** Backtest $K$ strategies with no skill at all, and keep the best. Its Sharpe ratio will not be zero. It will be about as large as the luckiest of $K$ draws of noise. That number grows with $K$, but slowly: roughly like the square root of its logarithm. The bar a genuine discovery has to clear is therefore not zero. It is the best result that luck could have produced with the same number of tries ([B.15](#b15)).

**Formally.** For $K$ independent standard normal variables,

$$
\mathbb{E}\Big[\max_{k \le K} Z_k\Big] \;\approx\; (1-\gamma)\,\Phi^{-1}\!\Big(1 - \frac1K\Big) + \gamma\,\Phi^{-1}\!\Big(1 - \frac{1}{Ke}\Big),
$$

where $\gamma \approx 0.5772$ is the Euler–Mascheroni constant. The form comes from extreme-value theory. Suitably rescaled, the maximum of many independent normals approaches a Gumbel distribution, whose mean involves $\gamma$. For $K = 100$, the formula gives 2.53. The deflated Sharpe ratio sets its benchmark $\mathrm{SR}_0$ to this value times the standard deviation of the Sharpe ratios across the trials. Over 10 years, a Sharpe ratio's standard error is about $1/\sqrt{10} = 0.32$. So the best of 100 skill-less strategies is expected to show a Sharpe ratio of about 0.8.

**Why it appears here.** §4.7 uses it for the deflated Sharpe ratio, and §3.6 for "the best of $K$ lucky draws".

**Deeper.** [Bailey & López de Prado (2014)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551){target="_blank"}.

## B.17 The probabilistic Sharpe ratio and minimum track-record length {#b17}

**The idea.** The probabilistic Sharpe ratio converts a measured Sharpe ratio into a confidence. It gives the probability that the true Sharpe ratio exceeds a benchmark, given the length of the record and the skewness and fat tails of the returns. Turned around, it says how long a record must be before that confidence reaches a chosen level. It is the test of [B.12](#b12), with the non-normal standard error of [B.10](#b10) in the denominator.

**Formally.** Let $\widehat{\mathrm{SR}}$ be a per-period Sharpe ratio measured from $n$ returns with skewness $\gamma_3$ and kurtosis $\gamma_4$, and let $\mathrm{SR}_0$ be a benchmark in the same units. Then

$$
\mathrm{PSR}(\mathrm{SR}_0) = \Phi\!\left(\frac{(\widehat{\mathrm{SR}} - \mathrm{SR}_0)\sqrt{n-1}}{\sqrt{1 - \gamma_3\widehat{\mathrm{SR}} + \tfrac{\gamma_4-1}{4}\widehat{\mathrm{SR}}^2}}\right).
$$

Set the PSR equal to a confidence level whose normal quantile is $z$, and solve for $n$. The result is the **minimum track-record length**:

$$
n_{\min} = 1 + \Big(1 - \gamma_3\widehat{\mathrm{SR}} + \tfrac{\gamma_4-1}{4}\widehat{\mathrm{SR}}^2\Big)\left(\frac{z}{\widehat{\mathrm{SR}} - \mathrm{SR}_0}\right)^2 .
$$

Take normal returns, a small per-period Sharpe ratio and $\mathrm{SR}_0 = 0$. Converting to years and annual Sharpe ratios then gives about $z^2/\mathrm{SR}^2$ years. At $z = 1.96$, that is $3.8/\mathrm{SR}^2$, the main text's $4/\mathrm{SR}^2$. The deflated Sharpe ratio is the PSR with $\mathrm{SR}_0$ taken from [B.16](#b16).

**Why it appears here.** §4.7 uses it for the PSR, the minimum track-record length and the deflated Sharpe ratio.

**Deeper.** [Bailey & López de Prado (2012)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643){target="_blank"}.

## B.18 Overlapping observations and HAC standard errors {#b18}

**The idea.** Measure a signal's IC against 21-day forward returns every day. Consecutive measurements then share 20 of their 21 days. They are nearly the same observation counted again. So a year of daily ICs holds about as much independent information as 12 monthly ones, and treating them as independent makes the standard error far too small. There are two fixes. The first samples only non-overlapping windows. The second estimates the standard error in a way that allows for the correlation. **HAC** (heteroskedasticity- and autocorrelation-consistent) standard errors do the latter, and Newey–West is the standard version.

**Formally.** A forward window of $h$ periods, sampled every period, induces autocorrelation of about $1 - k/h$ at lags $k < h$. The formula of [B.7](#b7) then multiplies the variance of the mean by about $h$. A t-statistic computed as if the data were independent is too large by about $\sqrt h$, which is more than four for $h = 21$. Newey–West estimates the long-run variance from the sample autocovariances $\hat\gamma_k$:

$$
\hat S = \hat\gamma_0 + 2\sum_{k=1}^{L}\Big(1 - \frac{k}{L+1}\Big)\hat\gamma_k .
$$

It then uses $\sqrt{\hat S/n}$ as the standard error of the mean ([B.9](#b9)). The declining weights keep $\hat S$ positive. For overlapping windows, the lag $L$ should be at least $h - 1$.

**Why it appears here.** The sixth item of §6.2 and the failure modes of §4.3 warn about overlapping forward windows that inflate the t-statistic. §7.4 lists overlapping returns counted as independent among the usual backtest mistakes.

**Deeper.** [Newey & West (1987)](https://www.jstor.org/stable/1913610){target="_blank"}; [Foundations of Econometrics](econometrics_foundations.html), section 4.5.

## B.19 Linear regression and $R^2$ {#b19}

**The idea.** A regression finds the straight line that best predicts one variable from another, where "best" means the smallest average squared error. The slope says how far the prediction moves per unit of the predictor. $R^2$ says what share of the outcome's variance the line explains. For standardised variables ([B.1](#b1)), the slope is the correlation ([B.2](#b2)). So the best forecast of the outcome is the score times the IC. An extreme score predicts a much less extreme outcome, which is regression toward the mean. Out of sample, a forecast is judged against the squared errors of a naive forecast that could have been used instead.

**Formally.** The regression $y = a + b\,x + e$, fitted by **ordinary least squares** (OLS), minimises $\sum_i e_i^2$. This gives $\hat b = \widehat{\operatorname{Cov}}(x,y)/\widehat{\operatorname{Var}}(x)$ and $\hat a = \bar y - \hat b\,\bar x$, with residuals uncorrelated with $x$ by construction. $R^2 = 1 - \operatorname{Var}(e)/\operatorname{Var}(y)$. With one predictor, it equals $\operatorname{Corr}(x,y)^2$. With several, it is the squared correlation between $y$ and its fitted value, the **squared multiple correlation**. Campbell and Thompson's **out-of-sample** $R^2$ compares a forecast $\hat y_t$, made only with data available at the time, with the historical average $\bar y_t$ known then:

$$
R^2_{\text{OS}} = 1 - \frac{\sum_t (y_t - \hat y_t)^2}{\sum_t (y_t - \bar y_t)^2}.
$$

It is negative when the forecast does worse than the average.

**Why it appears here.** §2.2 uses $R^2 = \mathrm{IC}^2$. In §3.3, a predictive $R^2$ of 1% raises a Sharpe ratio by a third. §6.1 reads the alpha rule as a regression slope, and §6.3 measures the marginal IC on a regression residual.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), sections 3.2, 3.3 and 3.8; [Campbell & Thompson (2008)](https://www.nber.org/papers/w11468){target="_blank"}.

## B.20 Combining predictors, and suppressors {#b20}

**The idea.** With several correlated signals, the best linear forecast weights each signal by what it adds beyond the others, not by its own IC. Two consequences are counterintuitive. First, a decent signal can deserve zero weight, when everything it knows reaches the outcome through a better signal it is correlated with. Second, a signal with no IC of its own can deserve a large negative weight, when it is correlated with a good signal's noise. Subtracting it then cleans the good signal. Statisticians call such a variable a **suppressor**.

**Formally.** Collect the standardised signals' ICs in a vector $\mathbf{ic}$, and their correlations in a matrix $\mathbf{C}$. The inverse $\mathbf{C}^{-1}$ is the matrix that undoes $\mathbf{C}$, so that $\mathbf{C}^{-1}\mathbf{C}$ is the identity. The best linear forecast ([B.19](#b19)) weights the signals by $\mathbf{w} = \mathbf{C}^{-1}\mathbf{ic}$. Its squared correlation with the outcome, the combined IC squared, is the quadratic form $\mathbf{ic}^\top\mathbf{C}^{-1}\mathbf{ic}$. For two signals with ICs $a$ and $b$ and correlation $\rho$,

$$
\begin{aligned}
w_1 &= \frac{a - \rho b}{1-\rho^2}, \qquad w_2 = \frac{b - \rho a}{1-\rho^2}, \\
\mathrm{IC}_{\text{combined}}^2 &= a^2 + \frac{(b - \rho a)^2}{1-\rho^2} = \frac{a^2 + b^2 - 2\rho ab}{1-\rho^2}.
\end{aligned}
$$

The middle form is the marginal-IC decomposition. The quantity $(b - \rho a)/\sqrt{1-\rho^2}$ is the IC of the second signal after the first has been regressed out of it. The second signal adds nothing when $b = \rho a$. When $b = 0$, its weight is $-\rho$ times the first signal's weight.

**Why it appears here.** §3.4 uses it for its table and for the zero-IC case. §6.3 uses it for the general formula and the marginal-IC diagnostic.

**Deeper.** [Grinold & Kahn (1999)](https://archive.org/details/activeportfoliom0000grin){target="_blank"}, the chapters on forecasting.

## B.21 Estimation error, ill-conditioning and shrinkage {#b21}

**The idea.** Formulas such as $\mathbf{C}^{-1}\mathbf{ic}$ treat their inputs as known, but the inputs are estimates. A matrix inverse is most sensitive exactly where the inputs are least reliable. Inverting divides by the matrix's eigenvalues. The small eigenvalues belong to combinations of signals, or assets, that look nearly redundant or nearly riskless. A small error there becomes a large weight, and the optimiser bets on the errors. **Shrinkage** is the standard defence. It pulls each estimate part of the way toward a simple, stable target, accepting a little bias in exchange for a large cut in variance.

**Formally.** A symmetric matrix with eigenvalues $\lambda_1 \ge \dots \ge \lambda_n > 0$ has an inverse with eigenvalues $1/\lambda_j$. Its **condition number** $\lambda_1/\lambda_n$ bounds how far relative errors in the inputs can be amplified. Two signals correlated 0.8 have eigenvalues 1.8 and 0.2, a condition number of 9. Their weights carry the factor $1/(1-\rho^2) = 2.8$ of [B.20](#b20). With ICs of 0.04 each, the weights are 0.022. An error of 0.01 in one IC, the standard error from 10,000 bets, moves its weight by 0.028, which is more than the weight itself. A shrinkage estimator is $\tilde\theta = (1-\delta)\,\hat\theta + \delta\,\theta_0$, with target $\theta_0$ and intensity $0 \le \delta \le 1$. Equal weighting is shrinkage all the way to the target.

**Why it appears here.** §3.5 lists estimation error and risk-model error as leaks, which [Zhou (2008)](https://www.pm-research.com/content/iijpormgmt/34/4/26){target="_blank"} sizes. §6.3 explains why full $\mathbf{C}^{-1}$ weighting is shrunk heavily, and §6.6 shrinks risk allocations toward equal risk.

**Deeper.** [Portfolio Construction and the Covariance Matrix](portfolio_construction.html), sections 2.3 and 5.7 on what inversion does, and section 6.5 on Ledoit–Wolf shrinkage; [Efron & Morris (1977)](https://doi.org/10.1038/scientificamerican0577-119){target="_blank"} on Stein's paradox, the reason shrinking beats the raw estimates.

## B.22 Backtests, overfitting and out-of-sample evidence {#b22}

**The idea.** A backtest runs a trading rule over historical data as though it had been traded. Data used to design the rule, choose its parameters or decide which variants to keep are **in-sample**. Data that played no part in those choices are **out-of-sample**. A rule tuned on a sample fits that sample's noise as well as its signal. So in-sample performance overstates what the rule will do next, and the gap is **overfitting**. It grows with the number of variants tried and with the flexibility of the rule. Only data the search never touched give evidence the search has not already spent. Such data include a holdout sample and the live record after the rule was frozen.

**Formally.** In the units of §3.6, a sample carrying $T\,\mathrm{SR}^2/2$ nats of evidence loses roughly $\ln K$ nats to a search over $K$ independent variants ([B.15](#b15)). A short sample that was searched hard may have nothing left. **Walk-forward** testing refits the rule on a rolling window and evaluates it only on the period that follows. Every reported return is then out of sample with respect to the fitting. Walk-forward testing does not protect against choices made after looking at the walk-forward results themselves.

**Why it appears here.** §1.3 and §4.7 allow for strategies tried and discarded, and stress that no correction replaces out-of-sample evidence. §6.7 counts only the years since the strategy was fixed.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), sections 9.7 and 10.2; [Systematic Trading Strategies](systematic_strategies.html), section 8.

## B.23 Stationarity and regime change {#b23}

**The idea.** Every estimate from history assumes the future is drawn from the same distribution as the past. A process with that property is **stationary**: its mean, variance and correlations do not drift with the calendar. Markets are only roughly stationary. A **regime** is a stretch of time whose parameters differ from those of other stretches. Examples are high- and low-volatility periods, or the months a signal works and the months it does not. A **structural break** is a lasting change, such as the drop in an anomaly's return after publication. Under regime change, a long record measures an average over regimes, and those regimes need not include the one coming next.

**Formally.** A series is covariance-stationary if $\mathbb{E}[r_t] = \mu$ and $\operatorname{Cov}(r_t, r_{t-k}) = \gamma_k$ do not depend on $t$. A regime-switching model lets the parameters depend on an unobserved state $S_t$. Given $S_t = j$, $r_t$ has mean $\mu_j$ and variance $\sigma_j^2$, and $S_t$ moves between states with fixed transition probabilities. A time-varying IC is a mild case: the $\sigma_{\mathrm{IC}}$ of §7.1 is the standard deviation of a signal's true IC across periods.

**Why it appears here.** §4.7 notes that after a regime change a correct test can answer a question that no longer matters. §6.2 uses the cumulative IC plot and stability across volatility regimes. §7.5 notes that information decays as others learn it.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), section 8.7; [Market Regimes and Machine Learning](market_regimes.html).

---

**Part II — Returns, risk and growth.** These entries explain what the top and bottom of a Sharpe ratio actually are. They cover returns in excess of cash, volatility and how it scales with time, and leverage and why the ratio ignores it. They then cover compounding and the growth of log wealth, and the drawdown, downside and tail measures of §5. The part ends with the utility theory behind the debate over Kelly's yardstick.

## B.24 Excess return and the financing rate {#b24}

**The idea.** A strategy's raw return mixes two things: what cash would have earned with no risk at all, and what the strategy earns for bearing risk. Subtracting the cash return isolates the second. It is also what makes the arithmetic of leverage work. Borrowing to double a position costs the cash rate, so what doubles is the return over cash. For a real levered strategy, the relevant rate is what the leverage actually costs. For most investors, that rate is above the cash rate.

**Formally.** With total return $R_t$ and cash (risk-free) rate $R_{f,t}$ over the same period, the **excess return** is $r_t = R_t - R_{f,t}$. Exposure financed by borrowing at a rate $R_{b,t}$ earns $R_t - R_{b,t}$ on the borrowed part. So the spread $R_b - R_f$ comes straight off the numerator of its Sharpe ratio. A dollar-neutral long-short book needs no cash subtracted. The short sale finances the long side, so the book's return, long minus short, is already a return in excess of financing, before the fee for borrowing the shorted stock.

**Why it appears here.** In the notation table, $r_t$ is in excess of cash. In §4.1, the "cash" rate of a levered strategy is the rate at which its leverage is financed. §7.3 discusses unavailable leverage and financing spreads.

**Deeper.** [Sharpe (1994)](https://web.stanford.edu/~wfsharpe/art/sr/sr.htm){target="_blank"}, which defines the ratio on a zero-investment differential return.

## B.25 Volatility, annualisation and volatility targeting {#b25}

**The idea.** **Volatility** is the standard deviation of returns: the typical size of a period's surprise. Independent variances add ([B.5](#b5)). So a year's volatility is the per-period volatility times the square root of the number of periods, while the expected return scales with the number itself. That is why Sharpe ratios annualise with $\sqrt q$. Volatility is also a dial. "Running a strategy at 10% volatility" means sizing it so that its annual P&L has a standard deviation of 10% of capital. Scaling a position scales its excess return and volatility together, so the setting expresses appetite for risk, not skill.

**Formally.** With per-period mean $\mu$, volatility $\sigma$ and $q$ independent periods a year, the annual mean is $q\mu$, the annual volatility is $\sqrt q\,\sigma$, and the annual Sharpe ratio is $\sqrt q\,\mu/\sigma$. Over $\tau$ years, the same scaling gives, for normal returns, a chance of losing money of $\Phi(-\mathrm{SR}\sqrt\tau)$. **Volatility targeting** sets the position each period to $\sigma_{\text{target}}/\hat\sigma_t$, where $\hat\sigma_t$ is a forecast of the strategy's volatility. Realised risk then stays near the target as markets calm down or become more turbulent.

**Why it appears here.** §2.3 uses it for annualisation. §2.5 uses it for the chances of losing periods and for drawdowns in units of annual volatility. §1.4 and §6.6 describe strategies run at a stated tracking error or volatility.

**Deeper.** [Simple and Log Returns](log_returns.html), section 3.5; [Value at Risk](value_at_risk.html), section 5.4, on the square-root-of-time rule.

## B.26 Leverage and leverage invariance {#b26}

**The idea.** **Leverage** is exposure per unit of capital. Doubling a position doubles its excess return ([B.24](#b24)) and its volatility ([B.25](#b25)). So their ratio, the Sharpe ratio, does not move. It is a property of the strategy, and leverage only chooses how much of the strategy to hold. This holds only while leverage is available in any amount at the cash rate. In practice, leverage is limited by **margin**, the collateral a broker or exchange requires against a position. Losses on a levered position can trigger margin calls that force sales at the worst moment.

**Formally.** Consider a position of $f$ units of exposure per unit of capital, financed at the cash rate. It has excess return $f r_t$, mean $f\mu$, volatility $f\sigma$ and Sharpe ratio $\mu/\sigma$, for every $f > 0$. If borrowing costs $R_b > R_f$, levering beyond $f = 1$ costs $(f-1)(R_b - R_f)$ a period, and the Sharpe ratio falls as $f$ rises. For long-short books, **gross leverage** is (long plus short) over capital, and **net exposure** is (long minus short) over capital.

**Why it appears here.** §4.1 uses it to explain why the Sharpe ratio is the yardstick for strategies that will be scaled. §6.6 uses it for Kelly leverage, and §7.3 for unavailable leverage and margin limits.

**Deeper.** [Systematic Trading Strategies](systematic_strategies.html), section 7.4, on capital, leverage and shorting.

## B.27 Log returns, compounding and volatility drag {#b27}

**The idea.** Wealth compounds: each period multiplies it. Logarithms turn multiplication into addition. So log wealth is a running sum of log returns, and its long-run growth rate is the average log return. That average is lower than the average simple return by about half the variance. A gain of 10% followed by a loss of 10% leaves wealth 1% down. This **volatility drag** is why growth first rises with leverage and then falls ([B.26](#b26)), and why growth is a quadratic in leverage.

**Formally.** The log return is $\ell_t = \ln(1+R_t)$, and $\ln(W_T/W_0) = \sum_t \ell_t$. The geometric mean return $G$, defined by $(1+G)^n = \prod_t (1+R_t)$, is close to $\bar R - \sigma^2/2$ when returns are small. Hold a constant fraction $f$ of wealth in a strategy with excess return $\mu$ and volatility $\sigma$ per unit of time. Over a short interval, the levered excess return $x$ has $\mathbb{E}[x] = f\mu\,\Delta t$ and $\mathbb{E}[x^2] \approx f^2\sigma^2\,\Delta t$, and $\ln(1+x) \approx x - x^2/2$. So log wealth grows in excess of cash at

$$
g(f) = f\mu - \tfrac12 f^2\sigma^2 .
$$

This is exact for continuous rebalancing of a diffusion. For discrete periods it is an approximation, accurate while each period's return is small. [A.11](#a11) maximises it.

**Why it appears here.** §3.2 and §6.6 use it for the growth rate $\mathrm{SR}^2/2$ and the growth-optimal leverage. The table in §3.2 shows the quadratic approximation overstating growth at large ICs. §4.1 uses arithmetic means over short periods, and §2.5 measures drawdowns on log wealth.

**Deeper.** [Simple and Log Returns](log_returns.html), section 3.4 on volatility drag and section 6.3 on where the $\sigma^2/2$ comes from in continuous time.

## B.28 Drawdowns and time to recovery {#b28}

**The idea.** A **drawdown** is how far wealth has fallen from its previous peak. It is the risk investors actually feel: they see it on a statement, and they fire managers for it. Unlike volatility, a drawdown depends on the order of returns. It is a property of one path, and a single losing run sets the maximum drawdown for a whole record. That makes it vivid and very noisy. The **time to recovery** is how long wealth takes to regain its previous peak.

**Formally.** With running peak $M_t = \max_{s \le t} W_s$, the simple drawdown is $1 - W_t/M_t$, and the log drawdown is $\ln M_t - \ln W_t$ ([B.27](#b27)). A log drawdown of $x$ is a simple drawdown of $1 - e^{-x}$. So 24% in log terms is 21% of peak wealth, and 20% is 18%. The **maximum drawdown** is the largest drawdown within a window. The drawdown-based ratios divide an annual return by one of three quantities: the maximum drawdown (Calmar, MAR), an average of the largest drawdowns (Sterling), or the **Ulcer index** (Martin). The Ulcer index is the root-mean-square drawdown, which counts depth and duration together.

**Why it appears here.** The table of §2.5 uses it, together with the warning that large drawdowns are normal. §5.1 and §5.4 present the drawdown ratios and explain why they are the noisiest in the zoo.

**Deeper.** [Value at Risk](value_at_risk.html), section 7.7, on drawdown measures.

## B.29 Downside deviation, lower partial moments and Omega {#b29}

**The idea.** The standard deviation penalises a surprise gain as much as a surprise loss. Downside measures count only outcomes below a target. The **lower partial moments** average the shortfall below the target, raised to a power. The **downside deviation** is the square root of the second lower partial moment: a standard deviation that ignores the upside. **Omega** compares the whole of the distribution above a threshold with the whole of it below.

**Formally.** For a target $\tau$, $\operatorname{LPM}_k(\tau) = \mathbb{E}\big[\max(\tau - r, 0)^k\big]$, averaged over all periods, not only the losing ones. The downside deviation is $\sqrt{\operatorname{LPM}_2(\tau)}$, and the **Sortino ratio** is $(\mu - \tau)/\sqrt{\operatorname{LPM}_2(\tau)}$. For a zero-mean normal variable and $\tau = 0$, the downside deviation is $\sigma/\sqrt2$. Omega is

$$
\Omega(\tau) = \frac{\mathbb{E}\big[\max(r - \tau, 0)\big]}{\mathbb{E}\big[\max(\tau - r, 0)\big]} = 1 + \frac{\mu - \tau}{\operatorname{LPM}_1(\tau)}.
$$

The second form holds because the two expectations differ by $\mu - \tau$. Omega is therefore a monotone function of a Sortino-like ratio with the first lower partial moment in the denominator.

**Why it appears here.** §5.1 places these measures on its grid. §5.2 shows that Sortino is about $\sqrt2$ times Sharpe under normality, and §5.4 that Sortino is about as noisy as Sharpe.

**Deeper.** [Sortino & Price (1994)](https://doi.org/10.3905/joi.3.3.59){target="_blank"}; [Keating & Shadwick (2002)](https://people.duke.edu/~charvey/Teaching/BA453_2004/Keating_A_universal_performance.pdf){target="_blank"}.

## B.30 Value at risk and expected shortfall {#b30}

**The idea.** **Value at risk** (VaR) answers "how bad is a bad day?" with a quantile: the loss exceeded only on the worst 1%, or 5%, of days. It says nothing about how bad those days are. **Expected shortfall** (ES, also called CVaR) does. It is the average loss on the days beyond the VaR, and it is the risk measure the tail-sensitive ratios divide by.

**Formally.** For P&L $X$ over a horizon and a confidence level $c$, $\operatorname{VaR}_c$ is the loss $v$ with $P(X < -v) = 1 - c$, and $\operatorname{ES}_c = \mathbb{E}\big[-X \mid X \le -\operatorname{VaR}_c\big]$. For normal P&L with mean $\mu$ and standard deviation $\sigma$, $\operatorname{VaR}_{99\%} = 2.33\,\sigma - \mu$ and $\operatorname{ES}_{99\%} = 2.67\,\sigma - \mu$. Each is the volatility times a constant, less the mean. Expected shortfall is sub-additive: the ES of a combined book never exceeds the sum of its parts' ES. VaR is not sub-additive.

**Why it appears here.** In §5.1, STARR and the conditional Sharpe ratio divide by expected shortfall. §5.2 shows that under normality they rank strategies exactly as the Sharpe ratio does.

**Deeper.** [Value at Risk](value_at_risk.html), sections 5.6 and 7.1.

## B.31 Expected utility and risk aversion {#b31}

**The idea.** Economists model choice under risk as maximising the average of a **utility** of wealth: a function that rises with wealth, but ever more slowly. That curvature is **risk aversion**. A risk-averse investor prefers a sure amount to a gamble with the same average. Kelly's criterion is the special case of logarithmic utility, and investors more cautious than that should bet less. Samuelson objected that nothing makes log utility right for everyone. The Kelly bettor ends up richer than any other strategy with probability approaching one. That fact does not mean another investor prefers the Kelly bet.

**Formally.** An investor chooses $f$ to maximise $\mathbb{E}[U(W)]$. **Relative risk aversion** is $\gamma = -W U''(W)/U'(W)$. **Power** utility, also called constant relative risk aversion (CRRA), is $U(W) = W^{1-\gamma}/(1-\gamma)$. It has the same $\gamma$ at every level of wealth, and $\gamma \to 1$ gives $U = \ln W$. Take a strategy with excess return $\mu$ and volatility $\sigma$ under continuous rebalancing. The optimal fraction is $f^\ast = \mu/(\gamma\sigma^2)$, which is the Kelly fraction of [A.11](#a11) divided by $\gamma$. So half Kelly is optimal for $\gamma = 2$. The manipulation-proof measure of Goetzmann and colleagues is a certainty equivalent of power utility. An uninformed manager cannot raise it by trading derivatives.

**Why it appears here.** §3.2 and §7.5 treat Kelly as a yardstick, not a recommendation. §6.6 discusses fractional Kelly, and §5.3 the manipulation-proof performance measure.

**Deeper.** [Samuelson (1971)](https://finance.martinsewell.com/money-management/Samuelson1971.pdf){target="_blank"}; [Goetzmann, Ingersoll, Spiegel & Welch (2007)](https://www.ivo-welch.info/research/journalcopy/2007-rfs.pdf){target="_blank"}; [Portfolio Construction and the Covariance Matrix](portfolio_construction.html), section 7.12.

---

**Part III — Benchmarks, factors and portfolios.** These entries cover the machinery between a forecast and a position. They start with benchmarks and the residual returns measured against them, then covariance matrices and the factor models that make them tractable. Next come the factors a signal is neutralised against and the structures a portfolio can take. The part ends with the optimiser, its constraints, and the risk budgets, all of which the transfer coefficient and the sizing rules of §6 score.

## B.32 Benchmarks, active weights and active return {#b32}

**The idea.** Most professional money is managed against a **benchmark**, an index the client could own cheaply instead. The manager's contribution is then the difference. The **active weights** say how much more or less of each asset the portfolio holds than the benchmark does, and they produce the **active return**. A manager who holds the benchmark exactly has zero active weights, zero active return, and no claim to a fee for skill.

**Formally.** With portfolio weights $w_i$ and benchmark weights $w_{B,i}$, the active weight is $\Delta w_i = w_i - w_{B,i}$. For a fully invested portfolio, the active weights sum to zero. The active return is $r_P - r_B = \sum_i \Delta w_i\, r_i$. Its standard deviation, the **active risk**, is one of two quantities that go by the name tracking error. Most equity benchmarks are **capitalisation-weighted**: each stock's weight is its market value divided by the total value of the index.

**Why it appears here.** §1.2 and §4.2 define the information ratio as the Sharpe ratio of the bet against a benchmark. §4.5 uses $\Delta w_i$ in the transfer coefficient. §6.5 explains why cap weights make the long-only constraint bind.

**Deeper.** [Grinold & Kahn (1999)](https://archive.org/details/activeportfoliom0000grin){target="_blank"}.

## B.33 Beta, alpha and residual risk {#b33}

**The idea.** Part of any portfolio's return is just its benchmark moving. **Beta** measures how much. A beta of 1.2 means the portfolio tends to move 1.2% for each 1% move in the benchmark. What is left after removing that part is the **residual return**. Its average is **alpha**, and its volatility is the **residual risk**. Alpha is what skill is supposed to produce, because beta can be bought for almost nothing in an index fund.

**Formally.** The market-model regression ([B.19](#b19)) of excess returns on the benchmark's excess returns is

$$
r_t = \alpha + \beta\, r_{B,t} + \varepsilon_t, \qquad \beta = \frac{\operatorname{Cov}(r, r_B)}{\operatorname{Var}(r_B)}.
$$

It gives residual risk $\omega = \sigma(\varepsilon)$ and splits total variance as $\sigma^2 = \beta^2\sigma_B^2 + \omega^2$. With the market portfolio as $r_B$, the intercept is **Jensen's alpha**. The CAPM predicts that it is zero, because every asset's expected excess return is its $\beta$ times the market's. The two tracking errors differ. One is $\omega$. The other is the standard deviation of the active return $r_t - r_{B,t} = \alpha + (\beta-1)\,r_{B,t} + \varepsilon_t$, which is $\sqrt{(\beta-1)^2\sigma_B^2 + \omega^2}$. Consider a fund with beta 1.2 and residual risk 4%, against a benchmark with 16% volatility. Its active risk is 5.1%. In a year when the benchmark beats cash by 10%, its active return gains 2% from beta alone.

**Why it appears here.** §4.2 and §3.7 compare the Grinold–Kahn and active-return definitions of the information ratio. §5.1 uses Treynor's ratio and Jensen's alpha. In §6.7, a market-neutral claim should show in the beta.

**Deeper.** [Jensen (1968)](https://doi.org/10.1111/j.1540-6261.1968.tb00815.x){target="_blank"}.

## B.34 The covariance matrix {#b34}

**The idea.** A portfolio's risk depends on how volatile each holding is, and also on how the holdings move together. The **covariance matrix** stores every pairwise covariance, and portfolio variance is a weighted sum over all its entries. With hundreds of assets, the matrix has more entries than a few years of data can estimate. So practitioners impose structure rather than estimating it raw. The simplest structure, the **diagonal** model, assumes the assets' residual returns are uncorrelated and keeps only the variances.

**Formally.** For $N$ assets, the covariance matrix $\Sigma$ is the $N \times N$ matrix with entries $\Sigma_{ij} = \operatorname{Cov}(r_i, r_j)$. A portfolio with weight vector $\mathbf{w}$ has variance $\mathbf{w}^\top\Sigma\,\mathbf{w}$. Dividing each entry by the two volatilities gives the correlation matrix. $\Sigma$ has $N(N+1)/2$ distinct entries. For 500 stocks that is 125,250 entries, against 30,000 returns in five years of monthly data. A sample covariance matrix estimated from $T \le N$ periods cannot be inverted. Under a diagonal model, $\mathbf{w}^\top\Sigma\,\mathbf{w} = \sum_i w_i^2\sigma_i^2$.

**Why it appears here.** §4.5 defines the transfer coefficient under a diagonal risk model, and its exact version under a full one. §3.5 lists risk-model error as a leak. §6.3 and §6.6 use the correlation matrices of signals and of strategies. [B.21](#b21) describes what goes wrong when the matrix is inverted.

**Deeper.** [Portfolio Construction and the Covariance Matrix](portfolio_construction.html), sections 5.3 and 6.

## B.35 Factor risk models {#b35}

**The idea.** Stocks move together because they share exposures: to the market as a whole, to their industry, and to broad characteristics such as size, value and momentum. A **factor risk model** writes each stock's return as its exposures times a handful of common **factor returns**, plus a **residual** return. The residual (also called specific, or idiosyncratic) return is particular to that stock and uncorrelated with every other stock's. The covariance matrix ([B.34](#b34)) then needs only the factors' covariances and one residual variance per stock.

**Formally.** $r_i = \sum_{k=1}^{K} X_{ik} f_k + u_i$. Here $X_{ik}$ are the exposures, $f_k$ are factor returns with covariance matrix $\mathbf{F}$, and the residuals $u_i$ are uncorrelated across stocks, with variances $\sigma_i^2$ equal to the squared residual volatilities. Then

$$
\Sigma = \mathbf{X}\mathbf{F}\mathbf{X}^\top + \operatorname{diag}\big(\sigma_1^2, \dots, \sigma_N^2\big).
$$

The model's **predicted tracking error** for active weights $\Delta\mathbf{w}$ is $\sqrt{\Delta\mathbf{w}^\top\Sigma\,\Delta\mathbf{w}}$. When realised tracking error runs persistently above it, the model is missing something correlated across the bets.

**Why it appears here.** §2.4 neutralises against market, sector and style factors. §4.2 uses a factor model as the benchmark for skill beyond known factors, and §6.2 measures ICs on residual outcomes. In §7.1, realised tracking error above predicted is the symptom of strategy risk.

**Deeper.** [Portfolio Construction and the Covariance Matrix](portfolio_construction.html), section 6.8.

## B.36 Factor premia and the common signal families {#b36}

**The idea.** A **factor premium** is the average return to owning assets with some characteristic and shorting those without it ([B.35](#b35)). A handful of characteristics recur across the literature and across asset classes. Most quantitative signals are variants or blends of them. The families matter here for two reasons. A "new" signal is often an old factor in disguise. And two strategies that load on the same factor count, for diversification, as one strategy.

**Formally.** The families are long-short sorts unless noted:

- **Value**: cheap against expensive, on book value, earnings or cash flow over price.
- **Momentum** (cross-sectional): winners against losers, typically on the past 12 months' return excluding the latest month.
- **Carry**: the return if prices do not change, such as a bond's yield, a currency's interest differential or a future's roll yield.
- **Size**: small companies against large.
- **Trend** (time-series momentum): each asset long if its own past return is positive, short if negative.
- **Short-term reversal** (mean reversion): last week's or last month's losers against its winners.
- **Low risk and quality**: low-beta or low-volatility stocks, and profitable, stable companies, against their opposites.

**Why it appears here.** §4.1 gives the Sharpe ratios of single factors and of trend-following. §3.3 notes that strategies exposed to the same factor are one strategy. §6.2 warns about a value signal in a value rally, and §4.6 describes the payoff shapes of trend and mean reversion.

**Deeper.** [Systematic Trading Strategies](systematic_strategies.html), section 5; [Momentum in Financial Markets](momentum_deep_dive.html); [Asness, Moskowitz & Pedersen (2013)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2174501){target="_blank"}.

## B.37 Neutralising a signal {#b37}

**The idea.** A raw signal usually mixes the bet its designer intended with bets nobody chose. A value signal is partly a bet on cheap sectors. A momentum signal is partly a bet on high beta after a rising market. **Neutralising** removes the unintended part. It regresses the signal across assets on the exposures it should not carry and keeps only the residual, which is uncorrelated with those exposures by construction. If the removed exposures carried noise but little information, the IC rises. This is the suppressor effect of [B.20](#b20).

**Formally.** Each period, take the signal vector $\mathbf{s}$ and an exposure matrix $\mathbf{X}$ of industry indicators, beta, size and other styles ([B.35](#b35)). The neutralised signal is the regression residual

$$
\mathbf{s}^\perp = \mathbf{s} - \mathbf{X}\big(\mathbf{X}^\top\mathbf{X}\big)^{-1}\mathbf{X}^\top\mathbf{s},
$$

re-standardised as in [B.1](#b1). Neutralising against industry indicators alone is the same as demeaning the signal within each industry. By the Frisch–Waugh–Lovell theorem, regressing a residualised outcome on a residualised signal gives the same slope as a regression of the outcome on the signal that controls for $\mathbf{X}$. Neutralising the signal before optimisation differs from imposing neutrality on the portfolio. The first removes the exposure from the forecast. The second leaves the exposure in the forecast and makes the optimiser fight it.

**Why it appears here.** §2.4 and §6.4 neutralise before counting bets. §3.4 explains why neutralising can raise the IC. §6.3 combines standardised, neutralised signals, and §6.5 recommends neutralising the signal rather than the portfolio.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), section 3.4, on Frisch–Waugh–Lovell.

## B.38 Cross-sectional and time-series strategies {#b38}

**The idea.** A **cross-sectional** strategy compares assets with each other on each date. It ranks them, buys the top and sells the bottom. It therefore bets on relative returns, while the market's direction largely cancels. A **time-series** strategy judges each asset against its own history, and it can be long or short the whole market. Trend-following and market timing are time-series strategies. The IC splits the same way. A cross-sectional IC is a correlation across $N$ assets on one date, giving one number per period. A time-series IC correlates one asset's forecasts with its returns over time.

**Formally.** Run a cross-sectional regression ([B.19](#b19)) on each date:

$$
y_{i,t+1} = a_t + f_t\, s_{i,t} + e_{i,t+1}.
$$

The slope $f_t$ is the return on a portfolio with unit exposure to the signal. For standardised $s$ and $y$, it equals $\mathrm{IC}_t$. The **Fama–MacBeth** procedure averages the slopes over $P$ periods and takes the standard error from their time series, giving $t = \bar f\big/\big(\operatorname{sd}(f)/\sqrt P\big)$. That is the IC t-statistic of §4.3. It is robust to correlation across assets within a period, because each period contributes a single number.

**Why it appears here.** §1.4 follows a cross-sectional monthly forecast. §3.7 lists the two meanings of IC, and §4.3 describes the IC series and its t-statistic. §7.1 cites Ding and Martin's treatment of the IC as a random factor return.

**Deeper.** [Fama & MacBeth (1973)](https://doi.org/10.1086/260061){target="_blank"}; [Foundations of Econometrics](econometrics_foundations.html), section 9.4.

## B.39 Long-only, long-short and market-neutral portfolios {#b39}

**The idea.** Portfolio structures differ in which views they can express. A **long-only** portfolio can underweight a stock only down to zero. So a negative view on a stock that is a tiny part of the benchmark ([B.32](#b32)) barely registers. A **long-short** portfolio can sell short, borrowing shares to sell now and buy back later, so negative views count as much as positive ones. A **market-neutral** portfolio is long-short with its market exposure removed, so its return is almost all residual. An **extension** portfolio, such as **130/30**, sits in between. It is 130% long and 30% short, net 100% long, and the short book funds more of the positive views.

**Formally.** Long-only requires $w_i \ge 0$, so $\Delta w_i \ge -w_{B,i}$. The average weight in a 500-stock index is 0.2%. Cap weights are skewed toward the largest companies, so most stocks weigh less than that. A typical stock therefore allows an underweight of a fraction of a percentage point, against overweights of several points. **Dollar neutrality** means long and short books of equal value. **Beta neutrality** means $\beta = 0$ ([B.33](#b33)), which makes the information ratio and the Sharpe ratio nearly coincide. Short positions pay a **borrow fee**, which rises with how hard the stock is to borrow.

**Why it appears here.** §1.4, §4.5 and §4.8 give typical transfer coefficients by structure. §3.5 notes that the long-only constraint costs more than any other. §6.5 explains that 130/30 exists to raise the transfer coefficient. §4.2 compares a market-neutral strategy's IR and Sharpe ratio.

**Deeper.** [Clarke, de Silva & Thorley (2002)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=290916){target="_blank"}.

## B.40 Mean-variance optimisation and the tangency portfolio {#b40}

**The idea.** Markowitz posed the problem: given expected returns and a covariance matrix ([B.34](#b34)), choose the weights that give the most expected return for the risk taken. Every investor who cares only about mean and variance ends up holding the same mix of risky assets, scaled up or down by appetite for risk. That mix is the **tangency**, or maximum-Sharpe, portfolio. It weights each asset by its expected return per unit of variance, corrected for correlation. Its squared Sharpe ratio is the sum of what each independent source of return contributes. That is why squared Sharpe ratios add.

**Formally.** Take a vector of expected excess returns $\mu$ and a covariance matrix $\Sigma$. Maximising $\mathbf{w}^\top\mu - \tfrac{\lambda}{2}\,\mathbf{w}^\top\Sigma\,\mathbf{w}$ gives

$$
\mathbf{w}^\ast = \frac1\lambda\,\Sigma^{-1}\mu, \qquad \mathrm{SR}_{\max}^2 = \mu^\top\Sigma^{-1}\mu ,
$$

where the risk aversion $\lambda$ changes only the scale. With uncorrelated assets, $\Sigma$ is diagonal and $w_i^\ast \propto \mu_i/\sigma_i^2$. The risk taken in each asset, $w_i^\ast\sigma_i$, is then proportional to its Sharpe ratio $\mu_i/\sigma_i$, and $\mathrm{SR}_{\max}^2 = \sum_i \mathrm{SR}_i^2$. In terms of a vector of Sharpe ratios $\mathbf{sr}$ and their correlation matrix $\mathbf{C}$, the risk allocation is proportional to $\mathbf{C}^{-1}\mathbf{sr}$, and $\mathrm{SR}_{\max}^2 = \mathbf{sr}^\top\mathbf{C}^{-1}\mathbf{sr}$. This is the algebra of [B.20](#b20) with Sharpe ratios in place of ICs, and it has the same sensitivity to estimation error ([B.21](#b21)).

**Why it appears here.** §3.3 uses it to show that squared Sharpe ratios of uncorrelated strategies add, as in Treynor and Black. §4.5 and §6.1 use the unconstrained position $\Delta w_i \propto \alpha_i/\sigma_i^2$, against which the transfer coefficient is measured. §6.3 and §6.6 apply the same formula to signals and to strategies.

**Deeper.** [Portfolio Construction and the Covariance Matrix](portfolio_construction.html), sections 5.1 and 5.2; [Treynor & Black (1973)](https://doi.org/10.1086/295508){target="_blank"}.

## B.41 Portfolio constraints, hard and soft {#b41}

**The idea.** Real portfolios are optimised under rules. Typical rules cap any one position, limit sector or factor exposure, set a ceiling on turnover, impose a minimum trade size, or forbid short sales ([B.39](#b39)). Each rule pulls the portfolio away from what the forecasts call for, and the transfer coefficient measures how far. A **hard** constraint must hold whatever it costs. A **soft** constraint is a penalty in the objective, which the optimiser can breach when the forecasts make it worthwhile. Constraints are not pure loss. By ruling out extreme positions, they also act as a crude shrinkage against estimation error ([B.21](#b21)).

**Formally.** A constrained version of [B.40](#b40) maximises $\alpha^\top\Delta\mathbf{w} - \lambda\,\Delta\mathbf{w}^\top\Sigma\,\Delta\mathbf{w}$, with $\alpha$ the vector of forecast residual returns. Typical constraints are:

- $\lvert\Delta w_i\rvert \le c$ (position limits);
- $\mathbf{X}^\top\Delta\mathbf{w} = \mathbf{0}$ (factor or sector neutrality);
- $\sum_i \lvert w_i - w_i^{\text{prev}}\rvert \le L$ (turnover);
- $w_i \ge 0$ (long-only).

Each binding constraint has a **shadow price**, its Lagrange multiplier. The shadow price is how much the objective would gain if the constraint were loosened by one unit. A soft constraint replaces the bound by a penalty, such as $\kappa\sum_i \lvert w_i - w_i^{\text{prev}}\rvert$ subtracted from the objective. The penalty fixes the price of turnover instead of its quantity.

**Why it appears here.** §1.2 treats constraints as the first leak, and §4.5 measures their cost with the transfer coefficient. §6.5 lists what lowers the transfer coefficient and prefers penalties to hard bounds.

**Deeper.** [Portfolio Construction and the Covariance Matrix](portfolio_construction.html), section 4.4; [Jagannathan & Ma (2003)](https://www.nber.org/papers/w8922){target="_blank"}, on constraints as shrinkage.

## B.42 Risk budgeting {#b42}

**The idea.** A portfolio of strategies or managers is best allocated in units of risk rather than capital. Capital can be levered, and risk is what each strategy consumes. A **risk budget** says how much volatility or tracking error each strategy receives. Mean-variance logic ([B.40](#b40)) gives each uncorrelated strategy risk in proportion to its Sharpe ratio. **Equal risk** gives them all the same. That is what the mean-variance rule says when the Sharpe ratios cannot be told apart, so equal risk is the natural target to shrink toward ([B.21](#b21)). For a single manager, the same logic sets the amount of active risk.

**Formally.** Grinold and Kahn's manager maximises value added, $\alpha - \lambda\omega^2$, where $\omega$ is active risk and $\lambda$ is the aversion to it. With $\alpha = \mathrm{IR}\cdot\omega$,

$$
\omega^\ast = \frac{\mathrm{IR}}{2\lambda}, \qquad \alpha^\ast = \frac{\mathrm{IR}^2}{2\lambda}, \qquad \text{value added} = \frac{\mathrm{IR}^2}{4\lambda}.
$$

So twice the information ratio justifies twice the tracking error and earns four times the alpha. In practice, $\lambda$ is backed out of the risk a client will tolerate. A client content with 4% tracking error from a manager with an IR of 0.5 has $\lambda = 0.5/(2 \times 0.04) = 6.25$.

**Why it appears here.** §6.6 allocates risk in proportion to Sharpe ratio, shrinks toward equal risk, and sets active risk proportional to the IR. §4.2 notes that the IR alone cannot say how much active risk to take.

**Deeper.** [Grinold & Kahn (1999)](https://archive.org/details/activeportfoliom0000grin){target="_blank"}; [Portfolio Construction and the Covariance Matrix](portfolio_construction.html), section 7.6, on equal risk contribution.

---

**Part IV — Trading, data and the industry.** These entries cover what converts information into money, at a loss that grows with size. They describe the ways a backtest's data can mislead. They cover the payoffs and businesses behind unusually high Sharpe ratios, and the asset-pricing bound on those ratios. They end with how published edges decay, and with the institutions that use these ratios to hire and fire managers.

## B.43 Transaction costs and turnover {#b43}

**The idea.** Every trade has a cost. The visible costs are commissions and the **bid–ask spread**: buying at the ask and selling at the bid loses the spread on a round trip. For large traders, the bigger cost is **market impact**. The price moves against the trader because of the trading itself, and the move grows with the trade's size relative to the market's volume. Shorts add a **borrow fee** ([B.39](#b39)). **Slippage**, the gap between the price when the signal fires and the price obtained, is a cost too. **Turnover**, how much of the portfolio is traded each period, multiplies all of these costs.

**Formally.** The value traded at a rebalance, as a share of capital, is $\sum_i \lvert w_{i,\text{new}} - w_{i,\text{old}}\rvert$. Half of it is the one-way turnover usually quoted. Annual cost is about annual value traded times cost per unit traded. [Practice] Impact is commonly modelled as proportional to daily volatility times the square root of the trade's share of daily volume, $k\,\sigma_{\text{daily}}\sqrt{Q/V}$, with $k$ of order one. In units of the information ratio, an annual cost $c$ against tracking error $\omega$ subtracts $c/\omega$. So 1.5% against 5% takes off 0.3.

**Why it appears here.** In §1.4, costs take 0.3 off the information ratio. §3.5 lists costs and turnover limits as leaks. §6.4 sets fixed costs per trade against an edge that shrinks with the horizon. §7.3 warns about backtests gross of costs.

**Deeper.** [Frazzini, Israel & Moskowitz (2018)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3229719){target="_blank"}, on costs measured from a large manager's own trades; [Isichenko (2021)](https://www.wiley.com/en-us/Quantitative+Portfolio+Management:+The+Art+and+Science+of+Statistical+Arbitrage-p-9781119821328){target="_blank"}.

## B.44 Signal decay and half-life {#b44}

**The idea.** A forecast's value fades as the information in it reaches prices. A signal whose edge arrives over the next day is worthless a week later. A signal about slow-moving fundamentals stays useful for months. The **half-life** is the time it takes the forecast's predictive power to halve. It sets how fast a signal must be traded and how much a delay costs. It also decides whether rebalancing more often adds information or only adds trades.

**Formally.** Under exponential decay with half-life $h$, a forecast acted on $d$ periods late keeps a fraction $2^{-d/h}$ of its IC and $2^{-2d/h}$ of its information. One day's delay on a five-day half-life keeps 87% of the IC and 76% of the information. The **IC decay curve** is a different object: the IC against cumulative forward returns over horizons $\tau$. Suppose the signal predicts a return accruing at rate $m(k)$ in the $k$-th period ahead. The predicted cumulative return is $\sum_{k<\tau} m(k)$, while the noise grows like $\sqrt\tau$ ([B.5](#b5)). So the curve rises like $\sqrt\tau$ while the predicted return accrues steadily, and falls once it stops. With exponential decay, $m(k) = m(0)\,2^{-k/h}$, and the total predictable return is about $m(0)\,h/\ln 2$.

**Why it appears here.** In §1.4, delay costs a tenth of the IC. §3.5 lists delay as a leak. §6.2 uses the decay curve. §6.4 notes that faster trading adds breadth only if the signal refreshes faster.

**Deeper.** [Gârleanu & Pedersen (2013)](https://nbgarleanu.github.io/DynTrad.pdf){target="_blank"}, whose model has signals that decay at different speeds.

## B.45 The aim portfolio {#b45}

**The idea.** With trading costs, chasing the ideal portfolio every period is too expensive, and capping turnover is crude. Gârleanu and Pedersen showed what is optimal when costs rise with the square of the trade. Move a fixed fraction of the way each period toward an **aim portfolio**. The aim is not today's ideal portfolio but a blend of it with the ideal portfolios expected in future. Slowly decaying signals ([B.44](#b44)) get more weight in the aim, because positions built on them will still be useful later. Fast signals get less weight, because their edge is gone before the position is built.

**Formally.** With quadratic costs ([B.43](#b43)), optimal holdings follow $\mathbf{x}_t = \mathbf{x}_{t-1} + \theta\,\big(\mathbf{aim}_t - \mathbf{x}_{t-1}\big)$, with $0 < \theta < 1$. Here $\mathbf{aim}_t$ is a weighted average of the current mean-variance portfolio ([B.40](#b40)) and the expected future ones. The trading rate $\theta$ rises with risk aversion and falls with the cost of trading.

**Why it appears here.** In §6.5, trading toward an aim portfolio keeps the portfolio closer to the forecast for the same cost.

**Deeper.** [Gârleanu & Pedersen (2013)](https://nbgarleanu.github.io/DynTrad.pdf){target="_blank"}.

## B.46 Strategy capacity {#b46}

**The idea.** A strategy's **capacity** is how much capital it can run before trading costs consume its edge. Gross alpha, in percent, does not depend on size. Market impact per unit traded, however, grows with the size of the trades ([B.43](#b43)). So net alpha falls as assets grow. Dollar profit, assets times net alpha, first rises with size and then falls. Capacity is usually quoted as the size at which net alpha falls below a threshold, or at which dollar profit peaks. The information in a signal does not shrink with size. The rate at which it converts into money does.

**Formally.** Take an illustrative model with gross alpha $\alpha$ and a cost rate that grows linearly with assets $A$, $c(A) = kA$. Dollar profit $A(\alpha - kA)$ peaks at $A^\ast = \alpha/(2k)$, where half the gross alpha goes on impact. Steeper cost curves, faster signals with higher turnover, and smaller, less liquid universes all lower $A^\ast$.

**Why it appears here.** §3.7 notes that Shannon's capacity and a strategy's capacity are unrelated. §4.1 and §7.4 place high Sharpe ratios where capacity is small. §6.7 warns that a strategy that worked at a hundred million may not work at a billion.

**Deeper.** [Frazzini, Israel & Moskowitz (2018)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3229719){target="_blank"}, which estimates the capacity of common factors; [Berk & Green (2004)](https://www.nber.org/papers/w9275){target="_blank"}, on decreasing returns to scale in active management.

## B.47 Data biases in backtests {#b47}

**The idea.** A backtest ([B.22](#b22)) can be no more honest than its data. **Look-ahead bias** uses information that was not available when the forecast was supposedly made. **Point-in-time** data is the cure. It records each value as it was known on each date, including the lag before publication and any later revisions. **Survivorship bias** comes from building the sample out of assets or funds that exist today, which silently drops the ones that failed. And a backtest that trades at the price that generated its signal, such as the close it was computed from, assumes a fill nobody could have had.

**Formally.** A forecast for period $t+1$ may use only information time-stamped before the trade at $t$. The following rules apply:

- data released with a lag, such as quarterly accounts that appear weeks after the quarter ends, enter on their release date;
- index membership enters as of each date;
- delisted assets enter with their final returns, including the delisting loss;
- the fill is the first price obtainable after the signal, such as the next open.

**Why it appears here.** §4.3 and the first item of §6.2 name these biases as the most common sources of a too-good IC. §7.3 warns about survivors in fund databases. §7.4 lists them among the usual mistakes behind a backtested Sharpe ratio above 2.

**Deeper.** [Systematic Trading Strategies](systematic_strategies.html), section 8.4, on the bias catalogue; [Foundations of Econometrics](econometrics_foundations.html), section 9.7.

## B.48 Universe construction and quantile portfolios {#b48}

**The idea.** The **universe** is the set of assets a strategy may trade on a given date. Building it is part of the strategy. Filters on market capitalisation, share price, trading volume and borrowability decide which stocks count, and they must be applied point-in-time ([B.47](#b47)). Many signals look strongest in the smallest, least liquid stocks, which are exactly the ones that cannot be traded in size. A **quantile portfolio** sorts the universe by the signal into equal groups, such as deciles, and tracks each group's average outcome. The top-minus-bottom spread, and the shape across groups, show whether the signal works throughout or only at the extremes. An IC cannot show this.

**Formally.** Take a standardised forecast and outcome that are jointly normal ([B.3](#b3)). The expected outcome of the top decile is $\mathrm{IC}\cdot\mathbb{E}[s \mid s > 1.28] = \mathrm{IC}\cdot\varphi(1.28)/0.1 = 1.75\,\mathrm{IC}$, where $\varphi$ is the standard normal density and 1.28 is the 90th percentile. The expected top-minus-bottom decile spread is therefore about $3.5\,\mathrm{IC}$ standard deviations, or 0.18 at an IC of 0.05. A **tail IC** is the IC computed on the most extreme forecasts only.

**Why it appears here.** In §2.2, the 300 highest of 3,000 forecasts beat the 300 lowest by a fifth of a standard deviation. §4.3 and the third item of §6.2 warn about a universe padded with untradable stocks and recommend the IC by size bucket. §7.5 suggests quantile spreads and tail ICs for detecting non-linear predictability.

**Deeper.** [Foundations of Econometrics](econometrics_foundations.html), appendix A.32, on portfolio sorts and breakpoints.

## B.49 Return smoothing {#b49}

**The idea.** An asset without a reliable market price, such as private equity, property or an illiquid bond, is marked by appraisal or at its last trade, which may be weeks old. A shock then reaches the reported returns gradually, spread over several periods. The reported series is smoother than the truth. Its volatility is lower, and its returns are positively autocorrelated ([B.7](#b7)). Its Sharpe ratio, computed naively, is higher, although the investor's risk has not changed.

**Formally.** Getmansky, Lo and Makarov model reported returns as a moving average of true ones, $r^\circ_t = \sum_{j=0}^{k}\theta_j\, r_{t-j}$, with $\theta_j \ge 0$ and $\sum_j\theta_j = 1$. The mean is unchanged. The variance falls to $\sigma^2\sum_j\theta_j^2$, and the lag-$m$ autocorrelation is $\sum_j \theta_j\theta_{j+m}\big/\sum_j\theta_j^2$. Spreading each shock evenly over two months, $\theta = (\tfrac12, \tfrac12)$, halves the variance. It raises the measured monthly Sharpe ratio by 41% and gives a first-order autocorrelation of 0.5. Sums over many periods are barely affected. So Lo's multiplier, applied to the smoothed series, roughly recovers the true annual Sharpe ratio.

**Why it appears here.** §2.4 treats positive autocorrelation as the signature of smoothing, and §7.3 lists smoothing as one way a Sharpe ratio misleads.

**Deeper.** [Getmansky, Lo & Makarov (2004)](https://www.nber.org/papers/w9571){target="_blank"}.

## B.50 Options and short-tail payoffs {#b50}

**The idea.** An option gives the right, but not the obligation, to buy (a **call**) or sell (a **put**) at a fixed **strike** price by a set date. The buyer pays a **premium** for it. An **out-of-the-money** put has its strike below the current price, so it pays only after a fall, like insurance. Selling such puts collects the premium month after month and pays out rarely and heavily. That is a **short-tail**, or short-volatility, payoff. It has small frequent gains, a high hit rate and negative skew ([B.8](#b8)), and its Sharpe ratio looks excellent until the event it insures. Strategies can have the same shape without options. The currency **carry trade** borrows in low-interest currencies to hold high-interest ones. It earns the difference until the funding currency jumps.

**Formally.** At expiry, a put with strike $K$ on an underlying at price $S$ pays $\max(K - S, 0)$, and a call pays $\max(S - K, 0)$. A short put's P&L is the premium minus $\max(K - S, 0)$. It is capped above at the premium, and below the strike it falls one-for-one with the underlying. The payoff is concave. Its sample moments understate its risk until the sample contains a fall through the strike.

**Why it appears here.** §5.3 covers selling options, liquidity provision and carry trades, and the manipulation result. §4.6 reads a high hit rate as the signature of a short tail. §7.3 lists selling the tail among the ways a Sharpe ratio misleads.

**Deeper.** [Systematic Trading Strategies](systematic_strategies.html), section 5.7, on volatility selling; [Brunnermeier, Nagel & Pedersen (2008)](https://www.nber.org/papers/w14473){target="_blank"}, on carry trades and currency crashes; [Implied Volatility](implied_volatility.html).

## B.51 Market making and liquidity provision {#b51}

**The idea.** A market maker quotes a price to buy (the bid) and a slightly higher price to sell (the ask). It earns the difference from traders who want to trade now rather than wait ([B.43](#b43)). Each trade carries a tiny edge, but there are thousands a day. So by the square-root law ([B.5](#b5)), the Sharpe ratio can be very high. Two risks offset the spread. **Adverse selection** is trading against someone who knows more; those are the trades that move the price. **Inventory risk** is holding a position through a sudden move. Capacity is small, because the business can grow only as fast as others' demand to trade. The tail is real, because inventory piles up when markets gap.

**Formally.** A round trip that buys at the bid $b$ and sells at the ask $a$ earns $a - b$. From that come two deductions: the expected price move against the market maker given that it was traded with, and the cost of carrying inventory. In Glosten and Milgrom's model, the spread is set so that gains from uninformed traders exactly cover losses to informed ones.

**Why it appears here.** §4.1 places market making far above a Sharpe ratio of 2, at small capacity. §4.6 describes the high hit rates of liquidity provision. §7.4 locates high Sharpe ratios where a service is being sold.

**Deeper.** [Glosten & Milgrom (1985)](https://milgrom.people.stanford.edu/wp-content/uploads/1984/09/Bid-Ask-and-Transaction-Prices.pdf){target="_blank"}; [Systematic Trading Strategies](systematic_strategies.html), section 5.8.

## B.52 The stochastic discount factor {#b52}

**The idea.** Asset pricing compresses everything about prices into one random variable, the **stochastic discount factor** $M$. $M$ assigns a number to each possible state of the world tomorrow. It is large in bad states, such as crashes and recessions, where an extra dollar is worth a lot, and small in good ones. Every asset's price is the average of its payoff weighted by $M$. This one idea explains risk premia. An asset that pays off badly when $M$ is high is cheap, and so it offers a high expected return. The idea also bounds Sharpe ratios. An excess return can at most be perfectly correlated with $M$, so no Sharpe ratio exceeds what the volatility of $M$ allows.

**Formally.** $\text{price} = \mathbb{E}[M \times \text{payoff}]$ for every traded payoff. A positive $M$ with this property exists if and only if there is no **arbitrage**: no position that costs nothing, can never lose and may gain. An excess return costs nothing to hold, so $\mathbb{E}[M R^e] = 0$. That gives $\mathbb{E}[R^e] = -\operatorname{Cov}(M, R^e)/\mathbb{E}[M]$. The **Cauchy–Schwarz inequality**, $\lvert\operatorname{Cov}(X,Y)\rvert \le \sigma_X\sigma_Y$, says that a correlation lies between $-1$ and $1$ ([B.2](#b2)). It then gives the Hansen–Jagannathan bound $\mathbb{E}[R^e]/\sigma(R^e) \le \sigma(M)/\mathbb{E}[M]$. In consumption models, $M = \delta\,U'(C_{t+1})/U'(C_t)$, with time discount $\delta$ and the marginal utility of [B.31](#b31). It is the rate at which an investor gives up consumption today for consumption tomorrow.

**Why it appears here.** §7.4 uses the Hansen–Jagannathan bound and good-deal bounds on Sharpe ratios.

**Deeper.** [Cochrane (2005)](https://press.princeton.edu/books/hardcover/9780691121376/asset-pricing){target="_blank"}, *Asset Pricing*; [Hansen & Jagannathan (1991)](https://doi.org/10.1086/261749){target="_blank"}.

## B.53 Anomalies, publication and decay {#b53}

**The idea.** An **anomaly** is a predictable pattern in returns that the standard risk model does not explain: a portfolio sorted on some characteristic ([B.36](#b36)) that earns a positive alpha ([B.33](#b33)). Three explanations compete for any anomaly, and they predict different futures. If the anomaly is compensation for risk, it should persist. If it is mispricing, it should shrink as arbitrageurs learn of it and trade it away. If it is a product of data mining ([B.15](#b15)), it should vanish out of sample. With many researchers searching the same datasets, data mining is a standing concern. Publication makes the mispricing explanation testable.

**Formally.** McLean and Pontiff split each anomaly's history into three periods: the original study's sample, the time after the sample ends but before publication, and the time after publication. Returns fall by 26% from the first period to the second. That fall is an upper bound on the share due to data mining. The further fall after publication, to 58% below the in-sample level, measures what trading on the published result takes away.

**Why it appears here.** §7.5 notes that information decays as others learn it. §4.7 gives the multiple-testing case for $t > 3$ on new factors. §9.4 lists the speed of decay after discovery among the unknowns.

**Deeper.** [McLean & Pontiff (2016)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2156623){target="_blank"}; [Systematic Trading Strategies](systematic_strategies.html), section 2.3; [Foundations of Econometrics](econometrics_foundations.html), section 9.6.

## B.54 The institutional landscape {#b54}

**The idea.** Most of the ratios in this chapter are used to make decisions about other people's money, along a chain of institutions. **Plan sponsors** (pension funds, endowments and foundations) own the assets. They hire **managers** to run portions of them under **mandates**, which are contracts that fix the benchmark ([B.32](#b32)), the constraints and the tracking-error budget. **Allocators** and investment **consultants** select and monitor managers, largely by **peer rankings**. A peer ranking compares a return or information ratio over a window against managers of the same style (value, growth, small-cap), and **top quartile** means the best 25%. A **multi-strategy platform** runs many independent teams under one central risk allocation.

**Formally.** A **management fee** is a percentage of assets per year. A **performance fee** is a share of profits, usually above a **hurdle** rate and a **high-water mark**. The high-water mark is the previous peak, so losses must be recovered before the fee is paid again. Fees come off the numerator of every ratio. A 1% fee against 5% tracking error lowers the information ratio by 0.2. Returns reported **gross** of fees overstate what investors received **net**.

**Why it appears here.** §4.2 refers to the benchmark the manager is paid against and to a top-quartile IR of about 0.5. §4.1 mentions a multi-strategy platform's target. §6.7 discusses plan sponsors' hiring and firing, and §7.3 warns about Sharpe ratios gross of fees.

**Deeper.** [Goyal & Wahal (2008)](https://doi.org/10.1111/j.1540-6261.2008.01375.x){target="_blank"}.

---

These documents were generated in whole or in part with the help of a large language model.
Dedicated to the public domain under the [CC0 1.0 Universal Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).

[Index](index.html) · [Source](https://github.com/rmahfoud/quant-research)
