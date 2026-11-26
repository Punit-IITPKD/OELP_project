Source: https://arxiv.org/html/1101.1438v3
Title: Optimal detection of changepoints with a linear computational cost
Fetched: 2026-11-26T15:58:29.350Z

[Skip to main content](https://arxiv.org/html/1101.1438v3#infobox)

Title:

Content selection saved. Describe the issue below:

Description:

[License: arXiv.org perpetual non-exclusive license](https://info.arxiv.org/help/license/index.html#licenses-available)

arXiv:1101.1438v3 \[stat.ME\] 09 Oct 2012

# Optimal detection of changepoints with a linear computational cost

Killick
R
Fearnhead
P
Eckley
I.A
Note: R. Killick is Senior Research Associate, Department of Mathematics & Statistics, Lancaster University, Lancaster, UK (E-mail:
r.killick@lancs.ac.uk). P. Fearnhead is Professor, Department of Mathematics & Statistics, Lancaster University, Lancaster, UK (E-mail: p.fearnhead@lancs.ac.uk). I.A. Eckley is Senior Lecturer,
Department of Mathematics & Statistics, Lancaster University, Lancaster, UK (E-mail: i.eckley@lancs.ac.uk). The authors are grateful to Richard Davis and Alice Cleynen for providing the Auto-PARM and
PDPA software respectively. Part of this research was conducted whilst R. Killick was a jointly funded Engineering
and Physical Sciences Research Council (EPSRC) / Shell Research Ltd graduate student at Lancaster University. Both I.A. Eckley and R. Killick also gratefully acknowledge the financial support of the
EPSRC grant number EP/I016368/1.

###### Abstract

We consider the problem of detecting multiple changepoints in large data sets. Our focus is on applications where the number of changepoints will increase as we collect more data:
for example in genetics as we analyse larger regions of the genome, or in finance as we observe time-series over longer periods. We consider the common approach of detecting changepoints through
minimising a cost function over possible numbers and locations of changepoints. This includes several established procedures for detecting changing points, such as penalised likelihood and minimum
description length. We introduce a new method for finding the minimum of such cost functions and hence the optimal number and location of changepoints that has a computational cost which, under mild
conditions, is linear in the number of observations. This compares favourably with existing methods for the same problem whose computational cost can be quadratic or even cubic. In simulation studies
we show that our new method can be orders of magnitude faster than these alternative exact methods. We also compare with the Binary Segmentation algorithm for identifying changepoints, showing that
the exactness of our approach can lead to substantial improvements in the accuracy of the inferred segmentation of the data.

KEYWORDS Structural Change; Dynamic Programming; Segmentation; PELT.

## 1. INTRODUCTION

As increasingly longer data sets are being collected, more and more applications require the detection of changes in the distributional properties of such data.
Consider for example recent work in genomics, looking at detecting changes in gene copy numbers or in the compositional structure of the genome [Braun et al., (2000)](https://arxiv.org/html/1101.1438v3#bib.bib7 ""); [Olshen et al., (2004)](https://arxiv.org/html/1101.1438v3#bib.bib21 ""); [Picard et al., (2005)](https://arxiv.org/html/1101.1438v3#bib.bib23 "");
and in finance where, for example, interest lies in detecting changes in the volatility of time series [Aggarwal et al., (1999)](https://arxiv.org/html/1101.1438v3#bib.bib1 ""); [Andreou and Ghysels, (2002)](https://arxiv.org/html/1101.1438v3#bib.bib3 ""); [Fernandez, (2004)](https://arxiv.org/html/1101.1438v3#bib.bib11 "").
Typically such series will contain several changepoints. There is therefore a growing need to be able to search for such changes efficiently.
It is this search problem which we consider in this paper. In particular we focus on applications where we expect the number of changepoints to increase as we collect more data.
This is a natural assumption in many cases, for example as we analyse longer regions of the genome or as we record financial time-series over longer time-periods. By comparison it does not necessarily apply to situations where we are obtaining data over a fixed time-period at a higher frequency.

At the time of writing Binary Segmentation proposed by [Scott and Knott, (1974)](https://arxiv.org/html/1101.1438v3#bib.bib26 "") is arguably the most widely used changepoint search method. It is approximate in nature with an 𝒪⁡(n​log⁡n)\\mathcal{O}(n\\log{n})
computational cost, where nn is the number of data points. While exact search algorithms exist for the most common forms of changepoint models, these have a much greater computational cost. Several
exact search methods are based on dynamic programming. For example the Segment Neighbourhood method proposed by [Auger and Lawrence, (1989)](https://arxiv.org/html/1101.1438v3#bib.bib4 "") is 𝒪⁡(Q​n2)\\mathcal{O}(Qn^{2}), where QQ is the maximum number of
changepoints you wish to search for. Note that in scenarios where the number of changepoints increases linearly with nn, this can correspond to a computational cost that is cubic in the length of the
data. An alternative dynamic programming algorithm is provided by the Optimal Partitioning approach of [Jackson et al., (2005)](https://arxiv.org/html/1101.1438v3#bib.bib19 ""). As we describe in Section [2.2](https://arxiv.org/html/1101.1438v3#S2.SS2 "2.2 Exact methods ‣ 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost") this can be applied to a
slightly smaller class of
problems and is an exact approach whose computational cost is 𝒪⁡(n2)\\mathcal{O}(n^{2}).

We present a new approach to search for changepoints, which is exact and under mild conditions has a computational cost that is linear in the number of data points:
the Pruned Exact Linear Time (PELT) method. This approach is based on the algorithm of [Jackson et al., (2005)](https://arxiv.org/html/1101.1438v3#bib.bib19 ""), but involves a pruning step within
the dynamic program. This pruning reduces the computational cost of the method, but does not affect the exactness of the resulting segmentation.
It can be applied to find changepoints under a range of statistical criteria such as penalised likelihood, quasi-likelihood
[Braun et al., (2000)](https://arxiv.org/html/1101.1438v3#bib.bib7 "") and cumulative sum of squares [Inclan and Tiao, (1994)](https://arxiv.org/html/1101.1438v3#bib.bib18 ""); [Picard et al., (2011)](https://arxiv.org/html/1101.1438v3#bib.bib22 "").
In simulations we compare PELT with both Binary Segmentation and Optimal Partitioning. We show that PELT can be calculated orders of magnitude faster than Optimal Partitioning, particularly for long data sets.
Whilst asymptotically PELT can be quicker, we find that in practice Binary Segmentation is quicker on the examples we consider, and we believe this would be the case in almost all applications.
However, we show that PELT leads to a substantially more accurate segmentation than Binary Segmentation.

The paper is organised as follows. We begin in Section [2](https://arxiv.org/html/1101.1438v3#S2 "2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost") by reviewing some basic changepoint notation and summarizing existing work in the area of search methods.
The PELT method is introduced in Section [3](https://arxiv.org/html/1101.1438v3#S3 "3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost") and the computational cost of this approach is considered in Section [3.1](https://arxiv.org/html/1101.1438v3#S3.SS1 "3.1 Linear Computational Cost of PELT ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost").
The efficiency and accuracy of the PELT method are demonstrated in Section [4](https://arxiv.org/html/1101.1438v3#S4 "4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost"). In particular we demonstrate the methods’ performance on large data sets coming from oceanographic (Section [4.2](https://arxiv.org/html/1101.1438v3#S4.SS2 "4.2 Application to Canadian Wave Heights ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost")) and financial (supplementary material) applications. Results show the speed gains over other exact search methods and the increased accuracy relative to approximate search methods such as Binary Segmentation. The paper concludes with a discussion.

## 2. BACKGROUND

Changepoint analysis can, loosely speaking, be considered to be the identification of points within a data set where the statistical properties change. More formally, let us assume we have an ordered sequence of data, y1:n=(y1,…,yn){y}\_{1:n}=(y\_{1},\\ldots,y\_{n}). Our model will have a number of changepoints, mm, together with their positions, τ1:m=(τ1,…,τm)\\tau\_{1:m}=(\\tau\_{1},\\ldots,\\tau\_{m}). Each changepoint position is an integer between 1 and n−1n-1 inclusive. We define τ0=0\\tau\_{0}=0 and τm+1=n\\tau\_{m+1}=n and assume that the changepoints are ordered such that τi<τj\\tau\_{i}<\\tau\_{j} if, and only if, i<ji<j. Consequently the mm changepoints will split the data into m+1m+1 segments, with the iith segment containing y(τi−1+1):τiy\_{(\\tau\_{i-1}+1):\\tau\_{i}}.

One commonly used approach to identify multiple changepoints is to minimise:

|     |     |     |     |
| --- | --- | --- | --- |
|  | ∑i=1m+1\[𝒞(y(τi−1+1):τi)\]+βf(m).\\displaystyle\\sum\_{i=1}^{m+1}{\\left\[\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})\\right\]+\\beta f(m)}. |  | (1) |

Here 𝒞\\mathcal{C} is a cost function for a segment and β​f​(m)\\beta f(m) is a penalty to guard against over fitting.
Twice the negative log likelihood is a commonly used cost function in the changepoint literature ( [Horvath,, 1993](https://arxiv.org/html/1101.1438v3#bib.bib16 ""); [Chen and Gupta,, 2000](https://arxiv.org/html/1101.1438v3#bib.bib8 ""), see for example),
although other cost functions such as quadratic loss and cumulative sums are also used ( [Rigaill,, 2010](https://arxiv.org/html/1101.1438v3#bib.bib24 ""); [Inclan and Tiao,, 1994](https://arxiv.org/html/1101.1438v3#bib.bib18 ""), e.g. ), or those based on both the segment log-likelihood and the length of
the segment [Zhang and Siegmund, (2007)](https://arxiv.org/html/1101.1438v3#bib.bib29 "").
Turning to choice of penalty, in practice by far the most common choice is one which is linear in the number of changepoints, i.e. β​f​(m)=β​m\\beta f(m)=\\beta m.
Examples of such penalties include Akaike’s Information Criterion (AIC, [Akaike, (1974)](https://arxiv.org/html/1101.1438v3#bib.bib2 "")) (β=2​p)(\\beta=2p) and Schwarz Information Criterion ( [Schwarz,, 1978](https://arxiv.org/html/1101.1438v3#bib.bib25 ""), SIC, also known as BIC;)(β=p​log⁡n)(\\beta=p\\log{n}), where pp is the number of additional parameters introduced by adding a changepoint.
The PELT method which we introduce in Section [3](https://arxiv.org/html/1101.1438v3#S3 "3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost") is designed for such linear cost functions.
Although linear cost functions are commonplace within the changepoint literature [Guyon and Yao, (1999)](https://arxiv.org/html/1101.1438v3#bib.bib14 ""), [Picard et al., (2005)](https://arxiv.org/html/1101.1438v3#bib.bib23 "") and [Birge and Massart, (2007)](https://arxiv.org/html/1101.1438v3#bib.bib6 "") offer examples and discussion of alternative penalty choices.
In Section [3.2](https://arxiv.org/html/1101.1438v3#S3.SS2 "3.2 PELT for concave penalties ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost") we show how PELT can be applied to some of these alternative choices.

The remainder of this section describes two commonly used methods for multiple changepoint detection; Binary Segmentation ( [Scott and Knott,, 1974](https://arxiv.org/html/1101.1438v3#bib.bib26 "")) and Segment Neighbourhoods ( [Auger and Lawrence,, 1989](https://arxiv.org/html/1101.1438v3#bib.bib4 "")). A third method proposed by [Jackson et al., (2005)](https://arxiv.org/html/1101.1438v3#bib.bib19 "") is also described as it forms the basis for the PELT method which we propose. For notational simplicity we describe all the algorithms (including PELT) assuming that the minimum segment length is a single observation, i.e. τi−1−τi≥1\\tau\_{i-1}-\\tau\_{i}\\geq 1. A larger minimum segment length is easily implemented when appropriate, see for example Section [4](https://arxiv.org/html/1101.1438v3#S4 "4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost").

### 2.1 Binary Segmentation

Binary Segmentation (BS) is arguably the most established search method used within the changepoint literature. Early applications include [Scott and Knott, (1974)](https://arxiv.org/html/1101.1438v3#bib.bib26 "") and [Sen and Srivastava, (1975)](https://arxiv.org/html/1101.1438v3#bib.bib27 ""). In essence the method extends any single changepoint method to multiple changepoints by iteratively repeating the method on different subsets of the sequence. It begins by initially applying the single changepoint method to the entire data set, i.e. we test if a τ\\tau exists that satisfies

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝒞(y1:τ)+𝒞(y(τ+1):n)+β<𝒞(y1:n).\\displaystyle\\mathcal{C}(y\_{1:\\tau})+\\mathcal{C}(y\_{(\\tau+1):n})+\\beta<\\mathcal{C}(y\_{1:n}). |  | (2) |

If ( [2](https://arxiv.org/html/1101.1438v3#S2.E2 "In 2.1 Binary Segmentation ‣ 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost")) is false then no changepoint is detected and the method stops. Otherwise the data is split into two segments consisting of the sequence before and after the identified changepoint, τa\\tau\_{a} say,
and apply the detection method to each new segment.
If either or both tests are true, we split these into further segments at the newly identified changepoint(s), applying the detection method to each new segment. This procedure is repeated until no further changepoints are detected. For pseudo-code of the BS method see for example [Eckley et al., (2011)](https://arxiv.org/html/1101.1438v3#bib.bib10 "").

Binary Segmentation can be viewed as attempting to minimise equation ( [1](https://arxiv.org/html/1101.1438v3#S2.E1 "In 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost")) with f⁡(m)=mf(m)=m: each step of the algorithm attempts to introduce an extra changepoint if and only if it reduces ( [1](https://arxiv.org/html/1101.1438v3#S2.E1 "In 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost")).
The advantage of the BS method is that it is computationally efficient, resulting in an 𝒪⁡(n​log⁡n)\\mathcal{O}(n\\log{n}) calculation.
However this
comes at a cost as it is not guaranteed to find the global minimum of ( [1](https://arxiv.org/html/1101.1438v3#S2.E1 "In 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost")).

### 2.2 Exact methods

#### Segment Neighbourhood

[Auger and Lawrence, (1989)](https://arxiv.org/html/1101.1438v3#bib.bib4 "") propose an alternative, exact search method for changepoint detection, namely the Segment Neighbourhood (SN) method. This approach searches the entire segmentation space
using dynamic programming ( [Bellman and Dreyfus,, 1962](https://arxiv.org/html/1101.1438v3#bib.bib5 "")). It begins by setting an upper limit on the size of the segmentation space (i.e. the maximum number of changepoints) that is required – this is
denoted QQ. The method then continues by computing the cost function for all possible segments. From this all possible segmentations with between 0 and QQ changepoints are considered.

In addition to being an exact search method, the SN approach has the ability to incorporate an arbitrary penalty of the form, β​f​(m)\\beta f(m). However, a consequence of the exhaustive search is that the method has significant computational cost, 𝒪⁡(Q​n2)\\mathcal{O}(Qn^{2}). If as the observed data increases, the number of changepoints increases linearly, then Q=𝒪⁡(n)Q=\\mathcal{O}(n) and the method will have a computational cost of 𝒪⁡(n3)\\mathcal{O}(n^{3}).

#### The optimal partitioning method

[Yao, (1984)](https://arxiv.org/html/1101.1438v3#bib.bib28 "") and [Jackson et al., (2005)](https://arxiv.org/html/1101.1438v3#bib.bib19 "") propose a search method that aims to minimise

|     |     |     |     |
| --- | --- | --- | --- |
|  | ∑i=1m+1\[𝒞(y(τi−1+1):τi)+β\].\\displaystyle\\sum\_{i=1}^{m+1}{\\left\[\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})+\\beta\\right\]}. |  | (3) |

This is equivalent to ( [1](https://arxiv.org/html/1101.1438v3#S2.E1 "In 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost")) where f⁡(m)=mf(m)=m.

Following [Jackson et al., (2005)](https://arxiv.org/html/1101.1438v3#bib.bib19 "") the optimal partitioning (OP) method begins by first conditioning on the last point of change. It then relates the optimal value of the cost function to the cost for the optimal partition of the data prior to the last changepoint plus the cost for the segment from the last changepoint to the end of the data.
More formally, let F⁡(s)F(s) denote the minimisation from ( [3](https://arxiv.org/html/1101.1438v3#S2.E3 "In The optimal partitioning method ‣ 2.2 Exact methods ‣ 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost")) for data y1:sy\_{1:s} and 𝒯s={𝝉:0=τ0<τ1<⋯<τm<τm+1=s}\\mathcal{T}\_{s}=\\{\\mbox{\\boldmath$\\tau$}:0=\\tau\_{0}<\\tau\_{1}<\\cdots<\\tau\_{m}<\\tau\_{m+1}=s\\}
be the set of possible vectors of changepoints for such data. Finally set F⁡(0)=−βF(0)=-\\beta. It therefore follows that:

|     |     |     |     |
| --- | --- | --- | --- |
|  | F⁡(s)\\displaystyle F(s) | =min𝝉∈𝒯s{∑i=1m+1\[𝒞(y(τi−1+1):τi)+β\]},\\displaystyle=\\min\_{\\mbox{\\boldmath$\\tau$}\\in\\mathcal{T}\_{s}}\\left\\{\\sum\_{i=1}^{m+1}{\\left\[\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})+\\beta\\right\]}\\right\\}, |  |
|  |  | =mint{min𝝉∈𝒯t∑i=1m\[𝒞(y(τi−1+1):τi)+β\]+𝒞(y(t+1):n)+β},\\displaystyle=\\min\_{t}\\left\\{\\min\_{\\mbox{\\boldmath$\\tau$}\\in\\mathcal{T}\_{t}}\\sum\_{i=1}^{m}\\left\[\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})+\\beta\\right\]+\\mathcal{C}(y\_{(t+1):n})+\\beta\\right\\}, |  |
|  |  | =mint{F(t)+𝒞(y(t+1):n)+β}.\\displaystyle=\\min\_{t}\\left\\{F(t)+\\mathcal{C}(y\_{(t+1):n})+\\beta\\right\\}. |  |

This provides a recursion which gives the minimal cost for data y1:sy\_{1:s} in terms of the minimal cost for data y1:ty\_{1:t} for t<st<s. This recursion can be solved in turn for s=1,2,…,ns=1,2,\\ldots,n. The cost of solving the recursion for time ss
is linear in ss, so the overall computational cost of finding F⁡(n)F(n) is quadratic in nn. Steps for implementing the OP method are given in Algorithm [1](https://arxiv.org/html/1101.1438v3#algorithm1 "Algorithm 1 ‣ The optimal partitioning method ‣ 2.2 Exact methods ‣ 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost").

Optimal Partitioning

|     |     |
| --- | --- |
| Input: | A set of data of the form, (y1,y2,…,yn)(y\_{1},y\_{2},\\ldots,y\_{n}) where yi∈ℝy\_{i}\\in\\mathbb{R}. |
|  | A measure of fit 𝒞⁡(⋅)\\mathcal{C}(\\cdot) dependent on the data. |
|  | A penalty constant β\\beta which does not depend on the number or location of changepoints. |
| Initialise: | Let n=n= length of data and set F⁡(0)=−βF(0)=-\\beta, c​p​(0)=N​U​L​Lcp(0)=NULL. |

Iterate for τ∗=1,…,n\\tau^{\*}=1,\\ldots,n

1. 1.


Calculate F(τ∗)=min0≤τ<τ∗\[F(τ)+𝒞(y(τ+1):τ∗)+β\]F(\\tau^{\*})=\\min\_{0\\leq\\tau<\\tau^{\*}}\\left\[F(\\tau)+\\mathcal{C}(y\_{(\\tau+1):\\tau^{\*}})+\\beta\\right\].

2. 2.


Let τ′=arg{min0≤τ<τ∗\[F(τ)+𝒞(y(τ+1):τ∗)+β\]}\\tau^{\\prime}=\\arg\\left\\{\\min\_{0\\leq\\tau<\\tau^{\*}}\\left\[F(\\tau)+\\mathcal{C}(y\_{(\\tau+1):\\tau^{\*}})+\\beta\\right\]\\right\\}.

3. 3.


Set c​p​(τ∗)=(c​p​(τ′),τ′)cp(\\tau^{\*})=(cp(\\tau^{\\prime}),\\tau^{\\prime}).


Output the change points recorded in c​p​(n)cp(n).

Algorithm 1:  Optimal Partitioning.

Whilst OP improves on the computational efficiency of the SN method, it is still far from being competitive computationally with the BS method.
Section [3](https://arxiv.org/html/1101.1438v3#S3 "3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost") introduces a modification of the optimal partitioning method denoted PELT which results in an approach whose computational cost can be linear in nn whilst retaining an exact
minimisation of ( [3](https://arxiv.org/html/1101.1438v3#S2.E3 "In The optimal partitioning method ‣ 2.2 Exact methods ‣ 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost")).
This exact and efficient computation is achieved via a combination of optimal partitioning and pruning.

## 3. A PRUNED EXACT LINEAR TIME METHOD

We now consider how pruning can be used to increase the computational efficiency of the OP method whilst still ensuring that the method finds a global minimum of the cost function ( [3](https://arxiv.org/html/1101.1438v3#S2.E3 "In The optimal partitioning method ‣ 2.2 Exact methods ‣ 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost")).
The essence of pruning in this context is to remove those values of τ\\tau which can never be minima from the minimisation performed at each iteration in (1) of Algorithm [1](https://arxiv.org/html/1101.1438v3#algorithm1 "Algorithm 1 ‣ The optimal partitioning method ‣ 2.2 Exact methods ‣ 2. BACKGROUND ‣ Optimal detection of changepoints with a linear computational cost").

The following theorem gives a simple condition under which we can do such pruning.

###### Theorem 3.1

We assume that when introducing a changepoint into a sequence of observations the cost, 𝒞\\mathcal{C}, of the sequence reduces. More formally, we assume there exists a constant KK such that for all t<s<Tt<s<T,

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝒞(y(t+1):s)+𝒞(y(s+1):T)+K≤𝒞(y(t+1):T).\\displaystyle\\mathcal{C}(y\_{(t+1):s})+\\mathcal{C}(y\_{(s+1):T})+K\\leq\\mathcal{C}(y\_{(t+1):T}). |  | (4) |

Then if

|     |     |     |     |
| --- | --- | --- | --- |
|  | F(t)+𝒞(y(t+1):s)+K≥F(s)\\displaystyle F(t)+\\mathcal{C}(y\_{(t+1):s})+K\\geq F(s) |  | (5) |

holds, at a future time T>sT>s, tt can never be the optimal last changepoint prior to TT.

Proof. See Section 5 of Supplementary Material. □\\Box

The intuition behind this result is that if ( [5](https://arxiv.org/html/1101.1438v3#S3.E5 "In Theorem 3.1 ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost")) holds then for any T>sT>s the best segmentation with the most recent changepoint prior to TT being at ss will be better than any which has this most recent changepoint at tt. Note that almost all cost functions used in practice satisfy assumption ( [4](https://arxiv.org/html/1101.1438v3#S3.E4 "In Theorem 3.1 ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost")). For example, if we take the cost function to be minus the log-likelihood then the constant K=0K=0 and if we take it to be minus a penalised log-likelihood then KK would equal the penalisation factor.

The condition imposed in Theorem [3.1](https://arxiv.org/html/1101.1438v3#S3.Thmdefinition1 "Theorem 3.1 ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost") for a candidate changepoint, tt, to be discarded from future consideration is important as it removes computations that are not relevant for obtaining the final set of changepoints. This condition can be easily implemented into the OP method and the pseudo-code is given in Algorithm [2](https://arxiv.org/html/1101.1438v3#algorithm2 "Algorithm 2 ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost"). This shows that at each step in the method the candidate changepoints satisfying the condition are noted and removed from the next iteration. We show in the next section that under certain conditions the computational cost of this method will be linear in the number of observations, as a result we call this the Pruned Exact Linear Time (PELT) method.

PELT Method

|     |     |
| --- | --- |
| Input: | A set of data of the form, (y1,y2,…,yn)(y\_{1},y\_{2},\\ldots,y\_{n}) where yi∈ℝy\_{i}\\in\\mathbb{R}. |
|  | A measure of fit 𝒞(.)\\mathcal{C}(.) dependent on the data. |
|  | A penalty constant β\\beta which does not depend on the number or location of changepoints. |
|  | A constant KK that satisfies equation [4](https://arxiv.org/html/1101.1438v3#S3.E4 "In Theorem 3.1 ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost"). |
| Initialise: | Let n=n= length of data and set F⁡(0)=−βF(0)=-\\beta, c​p​(0)=N​U​L​Lcp(0)=NULL, R1={0}R\_{1}=\\{0\\}. |

Iterate for τ∗=1,…,n\\tau^{\*}=1,\\ldots,n

1. 1.


Calculate F(τ∗)=minτ∈Rτ∗\[F(τ)+𝒞(y(τ+1):τ∗)+β\]F(\\tau^{\*})=\\min\_{\\tau\\in R\_{\\tau^{\*}}}\\left\[F(\\tau)+\\mathcal{C}(y\_{(\\tau+1):\\tau^{\*}})+\\beta\\right\].

2. 2.


Let τ1=arg{minτ∈Rτ∗\[F(τ)+𝒞(y(τ+1):τ∗)+β\]}\\tau^{1}=\\arg\\left\\{\\min\_{\\tau\\in R\_{\\tau^{\*}}}\\left\[F(\\tau)+\\mathcal{C}(y\_{(\\tau+1):\\tau^{\*}})+\\beta\\right\]\\right\\}.

3. 3.


Set c​p​(τ∗)=\[c​p​(τ1),τ1\]cp(\\tau^{\*})=\[cp(\\tau^{1}),\\tau^{1}\].

4. 4.


Set Rτ∗+1={τ∈Rτ∗∪{τ∗}:F(τ)+𝒞(yτ+1:τ∗)+K≤F(τ∗)}R\_{\\tau^{\*}+1}=\\left\\{\\tau\\in R\_{\\tau^{\*}}\\cup\\{\\tau^{\*}\\}:F(\\tau)+\\mathcal{C}(y\_{\\tau+1:\\tau^{\*}})+K\\leq F(\\tau^{\*})\\right\\}.


Output the change points recorded in c​p​(n)cp(n).

Algorithm 2:  PELT Method.

### 3.1 Linear Computational Cost of PELT

We now investigate the theoretical computational cost of the PELT method. We focus on the most important class of changepoint models and penalties and provide sufficient conditions for the method to have a computational cost
that is linear in the number of data points.
The case we focus on is the set of models where the
segment parameters are independent across segments and the cost function for a segment is minus the maximum log-likelihood value for the data in that segment.

More formally, our result relates to the expected computational cost of the method and how this depends on the number of data points we analyse. To this end we define an underlying stochastic model for the data generating process. Specifically we define such a process over positive-integer time points and then consider analysing the first nn data points generated by this process. Our result assumes that the parameters associated with a given segment are IID with density function π⁡(θ)\\pi(\\theta). For notational simplicity we assume that given the parameter, θ\\theta, for a segment, the data points within the segment are IID with density function f⁡(y\|θ)f(y\|\\theta) although extensions to dependence within a segment is trivial. Finally, as previously stated our cost function will be based on minus the maximum log-likelihood:

|     |     |     |
| --- | --- | --- |
|  | 𝒞(y(t+1):s)=−maxθ∑i=t+1slogf(yi\|θ).\\mathcal{C}(y\_{(t+1):s})=-\\max\_{\\theta}\\sum\_{i=t+1}^{s}\\log f(y\_{i}\|\\theta). |  |

Note that for this loss-function, K=0K=0 in ( [4](https://arxiv.org/html/1101.1438v3#S3.E4 "In Theorem 3.1 ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost")). Hence pruning in PELT will just depend on the choice of penalty constant β\\beta.

We also require a stochastic model for the location of the changepoints in the form of a model for the length of each segment. If the changepoint positions are τ1,τ2,…,\\tau\_{1},\\tau\_{2},\\ldots, then define the segment lengths to be S1=τ1S\_{1}=\\tau\_{1} and for i=2,3,…,i=2,3,\\ldots,Si=τi−τi−1S\_{i}=\\tau\_{i}-\\tau\_{i-1}. We assume the SiS\_{i} are IID copies of a random variable SS. Furthermore S1,S2,…,S\_{1},S\_{2},\\ldots, are independent of the parameters associated with the segments.

###### Theorem 3.2

Define θ∗\\theta^{\*} to be the value that maximises the expected log-likelihood

|     |     |     |
| --- | --- | --- |
|  | θ∗=arg⁡max⁡∫∫⁡f⁡(y\|θ)​f​(y\|θ0)​d​y​π​(θ0)​d​θ0.\\theta^{\*}=\\arg\\max\\int\\int f(y\|\\theta)f(y\|\\theta\_{0})\\mbox{d}y\\pi(\\theta\_{0})\\mbox{d}\\theta\_{0}. |  |

Let θi\\theta\_{i} be the true parameter associated with the segment containing yiy\_{i} and θ^n\\hat{\\theta}\_{n} be the maximum likelihood estimate for θ\\theta given data y1:ny\_{1:n} and an assumption of a single segment:

|     |     |     |
| --- | --- | --- |
|  | θ^n=arg⁡max⁡∑i=1nθ⁡log⁡f⁡(yi\|θ).\\hat{\\theta}\_{n}=\\arg\\max\_{\\theta}\\sum\_{i=1}^{n}\\log f(y\_{i}\|\\theta). |  |

Then if

- (A1)


denoting



|     |     |     |
| --- | --- | --- |
|  | Bn=∑i=1n\[log⁡f⁡(yi\|θ^n)−log⁡f⁡(yi\|θ∗)\],B\_{n}=\\sum\_{i=1}^{n}\\left\[\\log f(y\_{i}\|\\hat{\\theta}\_{n})-\\log f(y\_{i}\|\\theta^{\*})\\right\], |  |



we have 𝔼⁡(Bn)=o⁡(n)\\mathbb{E}\\left(B\_{n}\\right)=o(n) and 𝔼⁡(\[Bn−𝔼⁡(Bn)\]4)=𝒪⁡(n2)\\mathbb{E}\\left(\[B\_{n}-\\mathbb{E}\\left(B\_{n}\\right)\]^{4}\\right)=\\mathcal{O}(n^{2});

- (A2)


|     |     |     |
| --- | --- | --- |
|  | 𝔼⁡(\[log⁡f⁡(Yi\|θi)−log⁡f⁡(Yi\|θ∗)\]4)<∞;\\mathbb{E}\\left(\\left\[\\log f(Y\_{i}\|\\theta\_{i})-\\log f(Y\_{i}\|\\theta^{\*})\\right\]^{4}\\right)<\\infty; |  |

- (A3)


|     |     |     |
| --- | --- | --- |
|  | 𝔼⁡(S4)<∞; and\\mathbb{E}\\left(S^{4}\\right)<\\infty;\\mbox{ and} |  |

- (A4)


|     |     |     |
| --- | --- | --- |
|  | 𝔼⁡(log⁡f⁡(Yi\|θi)−log⁡f⁡(Yi\|θ∗))>β𝔼⁡(S);\\mathbb{E}\\left(\\log f(Y\_{i}\|\\theta\_{i})-\\log f(Y\_{i}\|\\theta^{\*})\\right)>\\frac{\\beta}{\\mathbb{E}\\left(S\\right)}; |  |


where SS is the expected segment length, the expected CPU cost of PELT for analysing nn data points is bounded above by L​nLn for some constant L<∞L<\\infty.

Proof. See Section 6 of Supplementary Material. □\\Box

Conditions (A1) and (A2) of Theorem [3.2](https://arxiv.org/html/1101.1438v3#S3.Thmdefinition2 "Theorem 3.2 ‣ 3.1 Linear Computational Cost of PELT ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost") are weak technical conditions. For example, general asymptotic results for maximum likelihood estimation would give Bn=𝒪p​(1)B\_{n}=\\mathcal{O}\_{p}(1), and (A1) is a slightly stronger condition which is controlling the probability of BnB\_{n} taking values that are 𝒪⁡(n1/2)\\mathcal{O}(n^{1/2}) or greater.

The other two conditions are more important. Condition (A3) is needed to control the probability of large segments. One important consequence of (A3) is that the expected number of changepoints will increase linearly with nn. Finally condition (A4) is a natural one as it is required for the expected penalised likelihood value obtained with the true changepoint and parameter values to be greater than the expected penalised likelihood value if we fit a single segment to the data with segment parameter θ∗\\theta^{\*}.

In all cases the worst case complexity of the algorithm is where no pruning occurs and the computational cost is 𝒪⁡(n2)\\mathcal{O}(n^{2}).

### 3.2 PELT for concave penalties

There is a growing body of research ( [Guyon and Yao,, 1999](https://arxiv.org/html/1101.1438v3#bib.bib14 ""); [Picard et al.,, 2005](https://arxiv.org/html/1101.1438v3#bib.bib23 ""); [Birge and Massart,, 2007](https://arxiv.org/html/1101.1438v3#bib.bib6 ""), see) that consider nonlinear penalty forms.
In this section we address how PELT can be applied to penalty functions which are concave.

|     |     |     |     |
| --- | --- | --- | --- |
|  | βf(m)+∑i=1m+1𝒞(y(τi−1+1):τi),\\displaystyle\\beta f(m)+\\sum\_{i=1}^{m+1}{\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})}, |  | (6) |

where f⁡(m)f(m) is concave and differentiable.

For an appropriately chosen γ\\gamma, the following result shows that the optimum segmentation based on such a penalty corresponds to minimising

|     |     |     |     |
| --- | --- | --- | --- |
|  | mγ+∑i=1m+1𝒞(y(τi−1+1):τi).m\\gamma+\\sum\_{i=1}^{m+1}{\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})}. |  | (7) |

###### Theorem 3.3

Assume that ff is concave and differentiable, with derivative denoted f′f^{\\prime}. Further, let m^\\hat{m} be the value of mm for which the criteria ( [6](https://arxiv.org/html/1101.1438v3#S3.E6 "In 3.2 PELT for concave penalties ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost")) is minimised. Then the optimal segmentation under this set of penalties is the segmentation that minimises

|     |     |     |     |
| --- | --- | --- | --- |
|  | mf′(m^)+∑i=1m+1𝒞(y(τi−1+1):τi).mf^{\\prime}(\\hat{m})+\\sum\_{i=1}^{m+1}{\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})}. |  | (8) |

Proof. See Section 7 of Supplementary Material. □\\Box

This suggests that we can minimize penalty functions based on f⁡(m)f(m) using PELT – the correct penalty constant just needs to be applied.
A simple approach, is to run PELT with an arbitrary penalty constant, say γ=f′​(1)\\gamma=f^{\\prime}(1). Let m0m\_{0} denote the resulting number of changepoints estimated.
We then run PELT with penalty constant γ=f′​(m0)\\gamma=f^{\\prime}(m\_{0}), and get a new estimate of the number of changepoints m1m\_{1}. If m0=m1m\_{0}=m\_{1} we stop. Otherwise we update the penalty constant and repeat until convergence.
This simple procedure is not guaranteed to find the optimal number of changepoints. Indeed more elaborate search schemes may be better. However, as tests of this simple approach in Section
[4.3](https://arxiv.org/html/1101.1438v3#S4.SS3 "4.3 Changes in Auto-covariance within Autoregressive Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost") show, it can be quite effective.

## 4. SIMULATION AND DATA EXAMPLES

We now compare PELT with both Optimal Partitioning (OP) and Binary Segmentation (BS) on a range of simulated and real examples. Our aim is to see empirically (i) how the computational cost of PELT is affected by the amount of data, (ii) to evaluate the computational savings that PELT gives over OP, and (iii) to evaluate the increased accuracy of exact methods over BS. Unless otherwise stated, we used the SIC penalty. In this case the penalty constant increases with the amount of data, and as such the application of PELT lies outside the conditions of Theorem [3.2](https://arxiv.org/html/1101.1438v3#S3.Thmdefinition2 "Theorem 3.2 ‣ 3.1 Linear Computational Cost of PELT ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost"). We also consider the impact of the number of changepoints not increasing linearly with the amount of data, a further violation of the conditions of Theorem [3.2](https://arxiv.org/html/1101.1438v3#S3.Thmdefinition2 "Theorem 3.2 ‣ 3.1 Linear Computational Cost of PELT ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost").

### 4.1 Changes in Variance within Normally Distributed Data

In the following subsections we consider multiple changes in variance within data sets that are assumed to follow a Normal distribution with a constant (unknown) mean.
We begin by showing the power of the PELT method in detecting multiple changes via a simulation study, and then use PELT to analyse Oceanographic data and Dow Jones Index returns (Section
2 in supplementary material).

#### Simulation Study

In order to evaluate PELT we shall construct sets of simulated data on which we shall run various multiple changepoint methods. It is reasonable to set the cost function, 𝒞\\mathcal{C} as twice the
negative log-likelihood.
Note that for a change in variance (with unknown mean), the minimum segment length is two observations. The cost of a segment is then

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝒞(y(τi−1+1):τi)=(τi−τi−1)(log(2π)+log(∑j=τi−1+1τi(yj−μ)2τi−τi−1)+1).\\displaystyle\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})=(\\tau\_{i}-\\tau\_{i-1})\\left(\\log(2\\pi)+\\log\\left(\\frac{\\sum\_{j=\\tau\_{i-1}+1}^{\\tau\_{i}}{(y\_{j}-\\mu)^{2}}}{\\tau\_{i}-\\tau\_{i-1}}\\right)+1\\right). |  | (9) |

Figure 1: A realisation of multiple changes in variance where the true changepoint locations are shown by vertical lines.

Our simulated data consists of scenarios with varying lengths, n=n=(100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000). For each value of nn we
consider
a linearly increasing number of changepoints, m=n/100m=n/100.
In each case the changepoints are distributed uniformly across (2,n−2)(2,n-2) with the only constraint being that there must be at least 30 observations between changepoints.
Within each of these scenarios we have 1,000 repetitions where the mean is fixed at 0 and the variance parameters for each segment are assumed to have a Log-Normal distribution with mean 0
and standard deviation log⁡(10)2\\tfrac{\\log(10)}{2}. These parameters are chosen so that 95% of the simulated variances are within the range \[110,10\]\\left\[\\tfrac{1}{10},10\\right\].
An example realisation is shown in Figure [1](https://arxiv.org/html/1101.1438v3#S4.F1 "Figure 1 ‣ Simulation Study ‣ 4.1 Changes in Variance within Normally Distributed Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost").
Additional simulations considering a wider range of options for the number of changepoints (square root: m=⌊n/4⌋m=\\lfloor\\sqrt{n}/4\\rfloor and fixed: m=2m=2) and parameter values are given in Section 1 of
the Supplementary Material.

Results are shown in Figure [2](https://arxiv.org/html/1101.1438v3#S4.F2 "Figure 2 ‣ Simulation Study ‣ 4.1 Changes in Variance within Normally Distributed Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost") where we denote the Binary Segmentation method which identifies the _same_ number of changepoints as PELT as subBS. Conversely the number of changepoints
BS would optimally select is called optimal BS. Firstly Figure [2](https://arxiv.org/html/1101.1438v3#S4.F2 "Figure 2 ‣ Simulation Study ‣ 4.1 Changes in Variance within Normally Distributed Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost") shows that when the number of changepoints increases linearly with nn,
PELT does indeed have a CPU cost that is linear in nn. By comparison figures in the supplementary material show that if the number of changepoints increases at a slower rate, for example,
square root or even fixed number of changepoints, the CPU cost of PELT is no longer linear. However even in the latter two cases, substantial computational savings are attained relative to OP.
Comparison of times with BS are also given in the Supplementary material. These show that PELT and BS have similar computational costs for the case of linearly increasing number of changepoints, but BS can be orders of magnitude quicker for other situations.

Figure 2: (a) Average Computational Time (in seconds) for a change in variance (thin: OP, thick: PELT). (b) Average difference in cost between PELT and BS for subBS (thin), optimal BS
(thick)) (c) MSE for PELT (thick), optimal BS (thin) and subBS (dotted).

The advantage of PELT over BS is that PELT is guaranteed to find the optimal segmentation under the chosen cost function, and as such is likely to be preferred providing sufficient computational time is available to run it.
Figure [2](https://arxiv.org/html/1101.1438v3#S4.F2 "Figure 2 ‣ Simulation Study ‣ 4.1 Changes in Variance within Normally Distributed Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost") shows the improved fit to the data that PELT attains over BS in terms of the smaller values of the cost function that are found. If you consider using the log-likelihood to choose between competing models, the value for n=50,000n=50,000 is over 1000 which is very large.
An alternative comparison is to look at how well each method estimates the parameters in the model. We measure this using mean square error:

|     |     |     |     |
| --- | --- | --- | --- |
|  | MSE =∑i=1n(θ^i−θi)2n,\\displaystyle\\mbox{MSE }=\\frac{\\sum\_{i=1}^{n}{(\\hat{\\theta}\_{i}-\\theta\_{i}})^{2}}{n}, |  | (10) |

Figure [2](https://arxiv.org/html/1101.1438v3#S4.F2 "Figure 2 ‣ Simulation Study ‣ 4.1 Changes in Variance within Normally Distributed Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost") shows the increase in accuracy in terms of mean square error of estimates of the parameter. The figures in the supplementary material show that for the fixed number of changepoints scenario the difference is negligible but, for the linearly increasing number of changepoints scenario, the difference is relatively large.

A final way to compare the accuracy of PELT with that of BS is to look at how accurately each method detects the actual times at which changepoints occurred. For the purposes of this study a
changepoint is considered correctly identified if we infer its location within a distance of 10 time-points of the true position. If two changepoints are identified in this window then one is counted
as correct and one false. The number of false changepoints is then the total number of changepoints identified minus the number correctly identified. The results are depicted in Figure
[3](https://arxiv.org/html/1101.1438v3#S4.F3 "Figure 3 ‣ Simulation Study ‣ 4.1 Changes in Variance within Normally Distributed Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost") for a selection of data lengths, nn, for the case m=n/100m=n/100. As nn increases the difference between the PELT and BS algorithms becomes clearer with PELT correctly identifying more
changepoints than BS.
Qualitatively similar results are obtained if we change how close an inferred changepoint has to be to a true changepoint to be classified as correct. Figures for square root increasing and fixed
numbers of changepoints are given in the supplementary material.
As the number of changepoints decreases a higher proportion of true changepoints are detected with fewer false changepoints.

Figure 3: Proportion of correctly identified changepoints against the proportion of falsely detected changepoints. Change in variance with m=n/100m=n/100 where (a) n=500n=500, (b) n=5,000n=5,000, (c) n=50,000n=50,000 (PELT: thick line, BS: thin line, +: SIC penalty).

The supplementary material also contains an exploration of the same properties for changes in both mean and variance. The results are broadly similar to those described above. We now demonstrate increased accuracy of the PELT algorithm compared with BS on an oceanographic data set; a financial application is given in the supplementary material.

### 4.2 Application to Canadian Wave Heights

There is interest in characterising the ocean environment, particularly in areas where there are marine structures, e.g. offshore wind farms or oil installations. Short-term operations, such as
inspection and maintenance of these marine structures, are typically performed in periods where the sea is less volatile to minimize risk.

Here we consider publically available data for a location in the North Atlantic where data has been collected on wave heights at hourly intervals from January 2005 until September 2012, see Figure
[4](https://arxiv.org/html/1101.1438v3#S4.F4 "Figure 4 ‣ 4.2 Application to Canadian Wave Heights ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost"). Our interest is in segmenting the series into period of lower and higher volatility. The data we use is obtained from Fisheries and Oceans Canada, East Scotian Slop buoy ID
C44137 and has been reproduced in the changepoint R package ( [Killick and Eckley,, 2010](https://arxiv.org/html/1101.1438v3#bib.bib20 "")).

The cyclic nature of larger wave heights in the winter and small wave heights in the summer is clear. However, the transition point from periods of higher volatility (winter storms) to lower
volatility (summer calm) is unclear, particularly in some years. To identify these features we work with the first difference data. Consequently a natural approach is to use the change in variance
cost function of Section [4.1](https://arxiv.org/html/1101.1438v3#S4.SS1 "4.1 Changes in Variance within Normally Distributed Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost"). Of course this is but one of several ways in which the data could be segmented.

For the data we consider (Figure [4](https://arxiv.org/html/1101.1438v3#S4.F4 "Figure 4 ‣ 4.2 Application to Canadian Wave Heights ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost")) there is quite a difference in the number of changepoints identified by PELT (17) and optimal Binary Segmentation (6). However, the location of
the detected changepoints is quite similar. The difference in likelihood between the inferred segmentations is 3851. PELT chooses a segmentation which, by-eye, segments the series well into the
different volatility regions (Figure [4](https://arxiv.org/html/1101.1438v3#S4.F4 "Figure 4 ‣ 4.2 Application to Canadian Wave Heights ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost")). Conversely, the segmentation produced by BS does not (Figure [4](https://arxiv.org/html/1101.1438v3#S4.F4 "Figure 4 ‣ 4.2 Application to Canadian Wave Heights ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost")); most notably it fails to detect any transitions between
2008 and 2012. If we increase the number of changepoints BS finds to equal that of PELT, the additional changepoints still fail to capture the regions appropriately.

Figure 4: North Atlantic Wave Heights (a) Original data (b) Differenced data with PELT changepoints (c) Differenced data with optimal BS changepoints and additional subBS changepoints
(dotted lines).

### 4.3 Changes in Auto-covariance within Autoregressive Data

Changes in AR models have been considered by many authors including [Davis et al., (2006)](https://arxiv.org/html/1101.1438v3#bib.bib9 ""), [Huskova et al., (2007)](https://arxiv.org/html/1101.1438v3#bib.bib17 "") and [Gombay, (2008)](https://arxiv.org/html/1101.1438v3#bib.bib13 "").
This section describes a simulation study that compares the properties of PELT and the genetic algorithm used in [Davis et al., (2006)](https://arxiv.org/html/1101.1438v3#bib.bib9 "") to implement the minimum description length (MDL) test statistic.

#### Minimum Description Length for AR Models

The simulation study here will be constructed in a similar way to that of Section [4.1](https://arxiv.org/html/1101.1438v3#S4.SS1 "4.1 Changes in Variance within Normally Distributed Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost").
It is assumed that the data follow an autoregressive model with order and parameter values depending on the segment. We shall take the cost function to be the MDL,
and consider allowing AR models of order 1,…,pm​a​x1,\\ldots,p\_{max}, for some chosen pm​a​xp\_{max} within each segment. The associated cost for a segment is

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝒞(y(τi−1+1):τi)=minp∈{1,…,pm​a​x}{logp+p+22log(τi−τi−1)+τi−τi−12log(2πσ^(p,τi−1+1,τi)2)}.\\displaystyle\\mathcal{C}(y\_{(\\tau\_{i-1}+1):\\tau\_{i}})=\\min\_{p\\in\\{1,\\ldots,p\_{max}\\}}\\left\\{\\log{p}+\\frac{p+2}{2}\\log(\\tau\_{i}-\\tau\_{i-1})+\\frac{\\tau\_{i}-\\tau\_{i-1}}{2}\\log{\\left(2\\pi\\hat{\\sigma}(p,\\tau\_{i-1}+1,\\tau\_{i})^{2}\\right)}\\right\\}. |  | (11) |

where σ^​(p,τi−1+1,τi)2\\hat{\\sigma}(p,\\tau\_{i-1}+1,\\tau\_{i})^{2} is the Yule-Walker estimate of the innovation variance for data y(τi−1+1):τiy\_{(\\tau\_{i-1}+1):\\tau\_{i}} and order pp.
When implementing PELT, we set K=−\[2​log⁡(pm​a​x)+(pm​a​x/2)​log⁡(n)\]K=-\[2\\log(p\_{max})+(p\_{max}/2)\\log(n)\], to ensure that ( [4](https://arxiv.org/html/1101.1438v3#S3.E4 "In Theorem 3.1 ‣ 3. A PRUNED EXACT LINEAR TIME METHOD ‣ Optimal detection of changepoints with a linear computational cost")) is satisfied.

#### Simulation Study

The simulated data consists of 5 scenarios with varying lengths, n=cn=c(1000, 2000, 5000, 10000, 20000) and each scenario contains 0.003​n0.003n changepoints.
These changepoints are distributed uniformly across (2,n−2)(2,n-2) with the constraint that there must be at least 50 observations between changepoints.
Within each of these 5 scenarios we have 200 repetitions where the segment order is selected randomly from {0,1,2,3}\\{0,1,2,3\\} and the autoregressive parameters for each segment are a realisation from a
standard Normal distribution subject to stationarity conditions. We compare the output from PELT with an approximate method proposed by [Davis et al., (2006)](https://arxiv.org/html/1101.1438v3#bib.bib9 "") for minimising the MDL criteria, which uses a genetic algorithm.
This was implemented in the program Auto-PARM, made available by the authors. We used the recommended settings except that for both methods we assumed pm​a​x=7p\_{max}=7.

Table [1](https://arxiv.org/html/1101.1438v3#S4.T1 "Table 1 ‣ Simulation Study ‣ 4.3 Changes in Auto-covariance within Autoregressive Data ‣ 4. SIMULATION AND DATA EXAMPLES ‣ Optimal detection of changepoints with a linear computational cost") shows the average difference in MDL over each scenario for each fitted model. It is clear that on average PELT achieves a lower MDL than the Auto-PARM algorithm and that this
difference increases as the length of the data increases. Overall, for 91% of data sets, PELT gave a lower value of MDL than Auto-Parm. In addition, the average number of iterations required for PELT to converge is small in all cases.

Table 1: Average MDL and number of PELT iterations over 200 repetitions.

| nn | 1,000 | 2,000 | 5,000 | 10,000 | 20,000 |
| --- | --- | --- | --- | --- | --- |
| no. iterations | 2.470 | 2.710 | 2.885 | 2.970 | 3.000 |
| Auto-PARM - PELT | 8.856 | 13.918 | 59.825 | 252.796 | 900.869 |

Previously, it was noted that the PELT algorithm for the MDL penalty is no longer an exact search algorithm.
For n=1,000n=1,000 we evaluated the accuracy of PELT by calculating the optimal segmentation in each case using Segment Neighbourhood (SN).
The average difference in MDL between the SN and PELT algorithms is 1.011.01 (to 2dp). However SN took an order of magnitude longer to run than PELT, its computational cost increasing with the cube of the data size making it impracticable for large nn. A better approach to improve on the results of our analysis would be to improve the search strategy
for the value of penalty function to run PELT with.

## 5. DISCUSSION

In this paper we have presented the PELT method; an alternative exact multiple changepoint method that is both computationally efficient and versatile in its application.
It has been shown that under certain conditions, most importantly that the number of changepoints is increasing linearly with nn, the computational efficiency of PELT is 𝒪⁡(n)\\mathcal{O}(n).
The simulation study and real data examples demonstrate that the assumptions and conditions are not restrictive and a wide class of cost functions can be implemented.
The empirical results show a resulting computational cost for PELT that can be orders of magnitude smaller than alternative exact search methods. Furthermore, the results show
substantial increases in accuracy by using PELT compared with Binary Segmentation. Whilst PELT is not, in practice, computationally quicker than Binary Segmentation,
we would argue that the statistical benefits of an exact segmentation outweigh the relatively small computational costs. There are other fast algorithms for segementing data that
improve upon Binary Segmentation ( [Gey and Lebarbier,, 2008](https://arxiv.org/html/1101.1438v3#bib.bib12 ""); [Harchaoui and Levy-Leduc,, 2010](https://arxiv.org/html/1101.1438v3#bib.bib15 "")), although these do not have the guarantee of exactness that PELT does.

[Rigaill, (2010)](https://arxiv.org/html/1101.1438v3#bib.bib24 "") develops a competing exact method called pruned dynamic programming (PDPA). This method also aims to improve the computational efficiency of an exact method, this time Segment
Neighbourhood, through pruning, but the way pruning is implemented is very different from PELT. The methods are complementary. Firstly they can be applied to different problems, with PDPA able to cope
with a non-linear penalty functions for the number of changepoints, but restricted to models with a single parameter within each segment. Secondly the applications under which they are computationally
efficient is different, with PDPA best suited to applications with few changepoints. Whilst unable to compare PELT with PDPA on the change in variance or the change in mean and variance models
considered in the results section, we have done a comparison between them on a change in mean. Results are presented in Table 1 of the Supplementary material. Our comparison was for both a linearly
increasing number of changepoints,
and a
fixed number of changepoints scenario. For the former PELT was substantially quicker, by a factors of between 300 and 40,000 as the number of data-points varied between 500 and 500,000. When we fixed the number of changepoints to 2, PDPA was a factor of 2 quicker for data with 500,000 changepoints, though often much slower for smaller data sets.

Code implementing PELT is contained within the R library changepoint which is available on CRAN ( [Killick and Eckley,, 2010](https://arxiv.org/html/1101.1438v3#bib.bib20 "")).

## References

- Aggarwal et al., (1999)
Aggarwal, R., Inclan, C., and Leal, R. (1999).

Volatility in emerging stock markets.

The Journal of Financial and Quantitative Analysis,
34(1):33–55.

- Akaike, (1974)
Akaike, H. (1974).

A new look at the statistical model identification.

IEEE Transactions on Automatic Control, 19(6):716–723.

- Andreou and Ghysels, (2002)
Andreou, E. and Ghysels, E. (2002).

Detecting multiple breaks in financial market volatility dynamics.

Journal of Applied Econometrics, 17(5).

- Auger and Lawrence, (1989)
Auger, I. E. and Lawrence, C. E. (1989).

Algorithms for the optimal identification of segment neighborhoods.

Bulletin of Mathematical Biology, 51(1):39–54.

- Bellman and Dreyfus, (1962)
Bellman, E. and Dreyfus, S. E. (1962).

Applied Dynamic Programming.

Princeton.

- Birge and Massart, (2007)
Birge, L. and Massart, P. (2007).

Minimal Penalties for Gaussian Model Selection.

Probability Theory and Related Fields, 138(1):33–73.

- Braun et al., (2000)
Braun, J. V., Braun, R. K., and Muller, H. G. (2000).

Multiple changepoint fitting via quasilikelihood, with application
to DNA sequence segmentation.

Biometrika, 87(2):301–314.

- Chen and Gupta, (2000)
Chen, J. and Gupta, A. K. (2000).

Parametric statistical change point analysis.

Birkhauser.

- Davis et al., (2006)
Davis, R. A., Lee, T. C. M., and Rodriguez-Yam, G. A. (2006).

Structural break estimation for nonstationary time series models.

JASA, 101(473):223–239.

- Eckley et al., (2011)
Eckley, I. A., Fearnhead, P., and Killick, R. (2011).

Analysis of changepoint models.

In Barber, D., Cemgil, T., and Chiappa, S., editors, Bayesian
Time Series Models. Cambridge University Press.

- Fernandez, (2004)
Fernandez, V. (2004).

Detection of breakpoints in volatility.

Estudios de Administracion, 11(1):1–38.

- Gey and Lebarbier, (2008)
Gey, S. and Lebarbier, E. (2008).

Using cart to detect multiple change-points in the mean for large
samples.

SSB Preprint, No.12.

- Gombay, (2008)
Gombay, E. (2008).

Change detection in autoregressive time series.

J. Multivariate Anal., 99(3):451 – 464.

- Guyon and Yao, (1999)
Guyon, X. and Yao, J.-f. (1999).

On the underfitting and overfitting sets of models chosen by order
selection criteria.

J. Multivariate Anal., 70(2):221 – 249.

- Harchaoui and Levy-Leduc, (2010)
Harchaoui, Z. and Levy-Leduc, C. (2010).

Multiple change-point estimation with a total-variation penalty.

JASA, 105(492):1480–1493.

- Horvath, (1993)
Horvath, L. (1993).

The maximum likelihood method of testing changes in the parameters of
normal observations.

Annals of Statistics, 21(2):671–680.

- Huskova et al., (2007)
Huskova, M., Praskova, Z., and Steinebach, J. (2007).

On the detection of changes in autoregressive time series.

J. Statist. Plann. Inference, 137(4):1243 – 1259.

- Inclan and Tiao, (1994)
Inclan, C. and Tiao, G. C. (1994).

Use of cumulative sums of squares for retrospective detection of
changes of variance.

JASA, 89(427):913–923.

- Jackson et al., (2005)
Jackson, B., Sargle, J. D., Barnes, D., Arabhi, S., Alt, A., Gioumousis, P.,
Gwin, E., Sangtrakulcharoen, P., Tan, L., and Tsai, T. T. (2005).

An algorithm for optimal partitioning of data on an interval.

IEEE, Signal Processing Letters, 12(2):105–108.

- Killick and Eckley, (2010)
Killick, R. and Eckley, I. A. (2010).

changepoint: Analysis of Changepoint Models.

Lancaster University, Lancaster, UK.

- Olshen et al., (2004)
Olshen, A. B., Venkatraman, E. S., Lucito, R., and Wigler, M. (2004).

Circular binary segmentation for the analysis of array-based DNA
copy number data. .

Biostatistics, 5:557–72.

- Picard et al., (2011)
Picard, F., Lebarbier, E., Hoebeke, M., Rigaill, G., Thiam, B., and Robin, S.
(2011).

Joint segmentation, calling and normalization of multiple cgh
profiles.

Biostatistics, 12(3):413 – 428.

- Picard et al., (2005)
Picard, F., Robin, S., Lavielle, M., Vaisse, C., and Daudin, J. J. (2005).

A statistical approach for array cgh data analysis.

Bioinformatics, 6(27).

- Rigaill, (2010)
Rigaill, G. (2010).

Pruned dynamic programming for optimal multiple change-point
detection.

ArXiv e-prints.

- Schwarz, (1978)
Schwarz, G. (1978).

Estimating the dimension of a model.

Ann. Statist., 6(2):461–464.

- Scott and Knott, (1974)
Scott, A. J. and Knott, M. (1974).

A cluster analysis method for grouping means in the analysis of
variance.

Biometrics, 30(3):507–512.

- Sen and Srivastava, (1975)
Sen, A. and Srivastava, M. S. (1975).

On tests for detecting change in mean.

The Annals of Statistics, 3(1):98–108.

- Yao, (1984)
Yao, Y. (1984).

Estimation of a noisy discrete-time step function: Bayes and
empirical Bayes approaches.

The Annals of Statistics, 12(4):1434–1447.

- Zhang and Siegmund, (2007)
Zhang, N. R. and Siegmund, D. O. (2007).

A modified bayes information criterion with applications to the
analysis of comparative genomic hybridization data.

Biometrics, 63(1):22–32.