Source: http://proceedings.mlr.press/v127/ma20a/ma20a.pdf
Title: 
Fetched: 2026-11-26T15:58:23.366Z

Journal of Machine Learning Research (2020) Submitted; Published

# Predictive and Causal Implications of using Shapley Value for Model Interpretation

Sisi Ma sisima@umn.edu *Institute for Health Informatics* *Department of Medicine* *University of Minnesota* *Minneapolis, Minnesota, USA*

Roshan Tourani roshan@umn.edu *Institute for Health Informatics* *University of Minnesota* *Minneapolis, Minnesota, USA*

Editor: Thuc Duy Le, Lin Liu, Kun Zhang, Emre Kıcıman, Peng Cui, and Aapo Hyv¨arinen

Abstract Shapley value is a concept from game theory. Recently, it has been used for explaining complex models produced by machine learning techniques. Although the mathematical definition of Shapley value is straight-forward, the implication of using it as a model interpretation tool is yet to be described. In the current paper, we analyzed Shapley value in the Bayesian network framework. We established the relationship between Shapley value and conditional independence, a key concept in both predictive and causal modeling. Our results indicate that, eliminating a variable with high Shapley value from a model do not necessarily impair predictive performance, whereas eliminating a variable with low Shapley value from a model could impair performance. Therefore, using Shapley value for feature selection do not result in the most parsimonious and predictively optimal model in the general case. More importantly, Shapley value of a variable do not reflect their causal relationship with the target of interest. Keywords: Causal Bayesian Networks, Predictive Models, Shapley Value, Model Explanation, Model Interpretability

## 1. Introduction

With the increased availability of data and the rapid advancement in predictive modeling, predictive models are playing important roles in many domains (Bellazzi and Zupan, 2008; Heaton et al., 2017; Xingjian et al., 2015; Sharma et al., 2011). Many predictive modeling methods, such as deep learning, produce highly complex models containing thousands of predictor variables. Although these models can be highly accurate, they are also very dif- ficult to interpret. Various methods have been developed for model interpretation (Lipton,

2018). Shapley value based model interpretation methods have gained a lot of popularity recently, since they have solid theoretical foundation and has been demonstrated to produce interpretations that matches human intuitions (Štrumbelj and Kononenko, 2014; Lundberg and Lee, 2017). Also, since Shapley value of a variable takes into account the variables’ individual as well as combined contribution for predicting a target of interest, it is also *©*c 2020 Sisi Ma and Roshan Tourani. License: CC-BY 4.0, see [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/). Attribution requirements are provided at [http://jmlr.org/papers/v/.html](http://jmlr.org/papers/v/.html).

Ma and Tourani

widely adopted as a metric for feature importance (often considered a component of model interpretation as well.). Many recent studies reports Shapley value for variables in reported predictive models (AlAref et al., 2020; Dworzynski et al., 2020; Artzi et al., 2020). And, many variants of Shapley value feature importance based feature selection methods were proposed (Zaeri-Amirani et al., 2018; Cohen et al., 2007; Mikenina and Zimmermann, 1999; Sun et al., 2012). Although the definition of Shapley value is relatively straight-forward, the implication of using it as a model explanation tool is yet to be described. Possibly because the goal of model explanation and interpretation can be hard to define (Lipton, 2018). Here, we focus on the relationship between Shapley value and a variable’s importance for the predictive task. We also examine whether the Shapley value is indicative of a variable’s causal relationship with the target of interest (i.e. causal interpretation). We seek answers to the questions of the following nature: If a variable have a larger Shapley value compared to other variables, does it mean removing it would result in a more significant performance loss? What are the consequences of using Shapley value as a heuristic for feature selection? Does a variable’s Shapley value indicate causal relationship with respect to the target? The reminder of the paper is organized as the following. In section 2, we introduce relevant concepts for Shapley value and predictive modeling. In section 3, we consider predictive modeling as a coalitional game and examine the characteristics of Shapley value of each variable. We assume that the predictive models are built on data generated from a faithful causal Bayesian network. We attempt to establish correspondence between Shapley value of variables and the structural properties of the Bayesian network. We illustrate the implications of using Shapley value for attributing variable importance. We also demon- strate that, in general, there is no relationship between Shapley value and causality. The key results and practical implications for using Shapley value for model interpretation is summarized in section 4.

## 2. Notations and Definitions

In this section, we provide a minimal set of definitions of essential concepts and analytical tools used in subsequent sections of the paper. Other relevant definitions and theorems regarding predictive modeling, variable importance, and (causal) Bayesian networks are included in Appendix A through D. Unless specifically mentioned, we use uppercase letters to denote a variable (e.g. *X*, *Y*) and its corresponding vertex in the causal Bayesian network underlying the data generation processes of these variables. We use bold uppercase letters to denote a set of variables or vertices (e.g. Z). We use lowercase letters to denote instantiations or values of the corresponding uppercase variables (e.g. *x* is a instantiation of *X*). For all the discussion below, we use the following common notations. V = *{V₁,V₂,...,V<sub>p</sub>}* denotes all measured variables. *T* denotes the target of interest with respect to a predictive model. *p*(V*,T*) denotes the joint distribution over of all variables. The Shapley value is a solution concept in game theory (Shapley, 1953). The Shapley value defines the division of total payoff generated by all players to individual players according to their contribution.

Shapley Value for Model Interpretation

Definition 1 *Coalitional game. A coalitional game is a tuple 〈*N*,v〉 where* N = *{*1*,*2*,...,n}* *is a finite set of n players, and v* : 2<sup>N</sup> *→* IR *is a characteristic function such that v*(*∅*) = 0*.*

*v* is a function defined over subsets of N that describes the value of each subset of N. The goal is to come up with a solution to distribute the total amount of payoff from all players, i.e. *v*(N), to each player. We use *φ<sub>i</sub>*(*v*) to denote the distributed payoff to player *i*, according to the value function *v*. The Shapley value is a distribution solution *φ* that have unique properties.

Definition 2 *Shapley value. For a game 〈*N*,v〉, Shapley value for a player i is defined as:*

∑ <u>(|N|−|S|− 1)!|S|!</u> *φ<sub>i</sub>*(*v*) = [*v*(S *∪{i}*) *− v*(S)]*.* *|*N*|*! S*⊆*N*−{i}*

Briefly, the Shapley value of a variable *i* is the weighted sum of the contribution of *i* in each subset of N. The contribution of *i* with respect to a subset S is computed by *v*(S*∪{i}*)*−v*(S).

The Shapley value is considered a uniquely fair way for distributing the total payoff *v*(N) into (*φ₁*(*v*)*,φ₂*(*v*)*,...,φ<sub>n</sub>*(*v*)) for the *n* players, since it satisfies the following characteristics (in fact, Shapley value is the only solution to distribute *v*(N) that satisfies all the characteristics below): ∑

- ** Efficiency:
*i∈* <sub>N</sub> *φ<sub>i</sub>*(*v*) = *v*(N).

- ** Symmetry: If for two players *i* and *j*, *∀*S *⊆* N *−{i,j}*, *v*(S *∪{i}*) = *v*(S *∪{j}*), then *φ<sub>i</sub>*(*v*) = *φ<sub>j</sub>*(*v*).
- ** Dummy: If *∀*S *⊆* N *−{i}*, *v*(S *∪{i}*) = *v*(S), then *φ<sub>i</sub>*(*v*) = 0.
- ** Additivity: For any pair of games *〈*N*,v〉*, *〈*N*,w〉*: *φ*(*v* + *w*) = *φ*(*v*) + *φ*(*w*), where *∀*S*,* (*v* + *w*)(S) = *v*(S) + *w*(S). Since predictive modeling could be viewed as a coalitional game, Shapley value have
been considered as a metric for variable importance and model explanation.

Definition 3 *Predictive Modeling as a coalition game. Let f*(V) *be a predictive model for* *a target of interest T. f* (*·*) *could be view as a coalition game 〈*V*,m〉, where each variable* *V<sub>i</sub> ∈* V *is a player in the coalition game, and m* : 2 *|N |* *→* IR *is a function that maps a subset* *of variables* S *to a real number representing the contribution of* S *for predicting T.*

There are a variety of choices for *m*, depending on nature of the task. One popular task that Shapley value has been applied to is model explanation of individual observations (Štrumbelj and Kononenko, 2014; Lundberg and Lee, 2017). The goal of this task is to explain why a predictive model made a specific prediction for the outcome given the observed predictor values from an observation. In this case, *m* is commonly defined as the deviation of the predictive outcome from a null model (which would make prediction based solely on the distribution of the outcome). Another task that Shapley value has been applied to is the attribution of variable importance (Owen and Prieur, 2017; Shorrocks, 1999).

The goal of this task is to assign a quantitative value to each variable to indicate their importance for the predictive performance of the model over a collection of observations. In this case, *m* can be based on any metric for predictive performance, such as the area under the receiver operating curve (AUC), accuracy, sensitivity, specificity, or the mean ab- solute deviation of the predictive outcome from a null model. The last metric is generated by the most popular Shapley value model explanation package SHAP (Lundberg, 2018), and therefore is commonly reported in application focused literature. Similar to mentioned above, to define *m*, the predictive performance metric of choice need to be subtracted by the predictive performance of a null model, to ensure the efficiency and dummy characteristics are met. In this study, we focus our discussion on using Shapley value for evaluating variable importance and its implications. Our results can be extended to model explanation of individual observations, which would be the topic of a subsequent paper.

## 3. Shapley Value, Network Structure, Causation, and Prediction

In this Section, we discuss the relationship between Shapley value and variable importance in a predictive model. We also describe the relationship between a variable’s Shapley value with its (causal) structural property with respect to the target of interest characterized by the (causal) Bayesian network over V *∪{T}*. We restrict our discussion to faithful (causal) Bayesian networks. We denote *〈*V*∪T,G,p〉* a (causal) Bayesian network faithful to distribution *p* over variable set V *∪ T*. And *f*(V) is a predictive model for *T* as a coalition game *〈*V*,m〉*, where *m* is maximized for each S *⊆* V only when *p*(*T |*S) is estimated accurately.

3.1 Shapley Value Summands and Conditional Independence We first introduce theorems relating the summands of Shapley value of a variable to its structural properties in the (causal) Bayesian network. This is achieved by establishing the connection between conditional independence relations in a faithful Bayesian network, which directly corresponds to the structural properties of the network, with the summands of Shapley value of a variable. Briefly, a Shapley value summand for variable *i* given a subset S with respect to predicting *T* is *m*(S *∪{i}*) *− m*(S); it captures the additional contribution of *i* to *T* given S. This bears conceptual similarity to the conditional independence between *i* and *T* given S (Definition 11). If we constrain function *m* to be maximized for each S *⊆* V only when *p*(*T |*S) is estimated accurately (similar to the treatment for the performance metric in Theorem 17), then, we have: (1) the conditional independence relationship *p*(*T |i,* S) = *p*(*T |*S) corresponds to *m*(S *∪{i}*) *− m*(S) = 0; And, (2) the conditional dependence relationship *p*(*T |i,* S) *6*= *p*(*T |*S) corresponds to *m*(S *∪{i}*) *− m*(S) *>* 0. Theorem 4 *∀*S *⊆* V *−{X}, m*(S *∪ X*) *− m*(S) *>* 0*, iff X ∈ PC*(*T*)*. (i.e. All Shapley* *value summands of parents and children of T are none-zero.)* Proof We prove *∀*S *⊆* V *−{X}*, *m*(S *∪ X*) *− m*(S) *>* 0 *⇐X∈ PC*(*T*). And note that each step of the proof is reversible, so we omit the proof for the sufficiency.

Since *X ∈ PC*(*T*), there is an edge between *X* and *T*. From Theorem 22, we know that, *X 6⊥ T |*S, *∀*S *⊆* V *−{X}*. Therefore, according to Definition 11, *∀*S, *p*(*T |X,* S) *6*= *p*(*T |*S) where *p*(S) *>* 0, i.e. *X* gives more information regarding *T* in addition to any S. And since we constrain *m* to be functions that are maximized for each S *⊆* V only when *p*(*T |*S) is estimated accurately, *∀*S *⊆* V *−{X}*, *m*(S *∪{X}*) *− m*(S) *>* 0.

Corollary 5 *Not all Markov boundary members (strongly relevant variables) of T have all* *non-zero Shapley value summands.*

Proof Let *X* be a parent of the children of *T*, and *X 6∈ PC*(*T*). *X* is a Markov boundary member of *T* but it has at least one Shapley value summands being zero due to Theorem 4.

Theorem 6 *∀X that is not connected to T by any path, all summands of its Shapley value* *m*(S *∪{X}*)) *− m*(S) *are zero, ∀*S *⊆* V *−{X}.*

Proof Given Theorem 27, *X* is an irrelevant variable. Given Theorem 22, *∀*S *⊆* V*−{X}*, *X ⊥ T |*S, i.e. *∀*S, *p*(*T |X,* S) = *p*(*T |*S) where *p*(S) *>* 0. Therefore, *∀*S *⊂* V *−{X},m*(S *∪* *−{X}*) *− m*(S) = 0.

Theorem 6 is related to the dummy characteristics of the Shapley value. The theorems in this section illustrate that given faithfulness and specific *m* functions, the Shapley value summands contain rich information about the structural properties of a variable with respect to a target in a (causal) Bayesian network. This connection between Shapley value summands and the structural property of the Bayesian network can be ex- ploited in two ways. Firstly, examining the distribution of the Shapley summands values can give insight into the structural property of a variable. For example, even one summand of Shapley value being zero indicates that the variable is not directly connected to (or is not a direct cause or direct effect in a causal Bayesian network) of the target. Secondly, com- puting Shapley value exactly is often computationally intensive, since all 2 *|*V*|* summands associated with 2 *|* <sup>V</sup> *|* models need to be computed. Therefore, the Shapley value is often computed by sampling from all possible subsets S (Štrumbelj and Kononenko, 2014). Given the structure of a faithful Bayesian network, one might be able to sample S more efficiently and reduce the computation needed to achieve a good approximation of the Shapley value.

3.2 Shapley Value of Variables in a Faithful Bayesian Network When using the Shapley value for model explanation or feature importance, the summands of a variable are not examined individually. But rather, the resulted sum, i.e. Shapley value, for individual variables are compared. The theorem below describe the relationship between the Shapley value of a variable and the variable’s structural property in a faithful (causal) Bayesian network. Specifically, when variable *V<sub>j</sub>* d-separates *V<sub>i</sub>* from *T*, *V<sub>j</sub>*’s Shapley value is larger than that of *V<sub>i</sub>*. Theorem 7 *If V<sub>i</sub> ⊥ T |V<sub>j</sub> and V<sub>j</sub> 6⊥ T |V<sub>i</sub> in a faithful (causal) Bayesian network 〈*V *∪* *T,G,p〉, then the Shapley value of V<sub>j</sub> is larger than the Shapley value of V<sub>i</sub>, i.e. phi<sub>j</sub> > phi<sub>i</sub>.*

Proof First we separate the summation in Shapley value of *V<sub>i</sub>* to two components, *φ* *i|ĵ*, the sum over sets S where *V<sub>j</sub> ∈/* S, and *φi|j*, the sum over sets S where *V<sub>j</sub> ∈* S,

∑ <u>(|N|−|S|− 1)!|S|!</u> *φ<sub>i</sub>* = [*m*(S *∪{V<sub>i</sub>}*) *− m*(S)] = *φ* *i|ĵ* + *φi|j,* *|*N*|*! S*⊆*V*−{Vi}*

∑ <u>(|N|−|S|− 1)!|S|!</u> *φ* *i|ĵ* = [*m*(S *∪{V<sub>i</sub>}*) *− m*(S)] *|*N*|*! S*⊆*V*−{Vi},Vj∈/*S ∑ <u>(|N|−|S|− 1)!|S|!</u> *φi|j*= [*m*(S *∪{V<sub>i</sub>}*) *− m*(S)] *|*N*|*! S*⊆*V*−{Vi},Vj∈*S

Similarly, for variable *V<sub>j</sub>*, we write *φ<sub>j</sub>* = *φ* *j|î* + *φj|i*where *φ* *j|î* only sums over S where *V<sub>i</sub> ∈/* S and *φj|i*only sums over S where *V<sub>i</sub> ∈* S. Now we rewrite all the sums with S *⊆ V −{V<sub>i</sub>,V<sub>j</sub>}*, { ∑ <u>(|N|−|S|− 1)!|S|!</u> *φ<sub>i</sub>* = [*m*(S *∪{V<sub>i</sub>}*) *− m*(S)] + *|*N*|*! S*⊆*V*−{Vi,Vj}* } <u>(|N|−|S|− 2)!(|S| + 1)!</u> + [*m*(S *∪{V<sub>i</sub>,V<sub>j</sub>}*) *− m*(S *∪{V<sub>j</sub>}*)]*,* *|*N*|*!

{ ∑ <u>(|N|−|S|− 1)!|S|!</u> *φ<sub>j</sub>* = [*m*(S *∪{V<sub>j</sub>}*) *− m*(S)] + *|*N*|*! S*⊆*V*−{Vi,Vj}* } <u>(|N|−|S|− 2)!(|S| + 1)!</u> + [*m*(S *∪{V<sub>i</sub>,V<sub>j</sub>}*) *− m*(S *∪{V<sub>i</sub>}*)]*.* *|*N*|*!

Now writing *φ<sub>i</sub> − φ<sub>j</sub>* we can easily cancel out the *m*(S) and *m*(S*∪{V<sub>i</sub>,V<sub>j</sub>}*) terms, and write *φ<sub>i</sub> − φ<sub>j</sub>* as,

() ∑ <u>(|N|−|S|− 1)!|S|! (|N|−|S|− 2)!(|S| + 1)!</u> *φ<sub>i</sub> − φ<sub>j</sub>* = + *|*N*|*! *|*N*|*! S*⊆*V*−{Vi,Vj}* *×* [*m*(S *∪{V<sub>i</sub>}*) *− m*(S *∪{V<sub>j</sub>}*)]*,*

Since *V<sub>i</sub> ⊥ T |V<sub>j</sub>*, i.e. *p*(*T |*S*,V<sub>i</sub>,V<sub>j</sub>*) = *p*(*T |*S*,V<sub>j</sub>*), we have *m*(S*∪{V<sub>i</sub>,V<sub>j</sub>}*)*− m*(S*∪{V<sub>j</sub>}*) = 0. And *V<sub>j</sub> 6⊥ T |V<sub>i</sub>*, i.e. *p*(*T |*S*,V<sub>i</sub>,V<sub>j</sub>*) *6*= *p*(*T |*S*,V<sub>i</sub>*), we have: *m*(S *∪{V<sub>i</sub>,V<sub>j</sub>}*)*− m*(S *∪{V<sub>i</sub>}*) *>* 0. Therefore, *m*(S *∪{V<sub>i</sub>}*) *− m*(S *∪{V<sub>j</sub>}*) *<* 0, and thus, *φ<sub>j</sub> > φ<sub>i</sub>*.

Theorem 7 state that, in a faithful (causal) Bayesian network, if *V<sub>j</sub>* renders *V<sub>i</sub>* conditional independent of *T*, i.e. *V<sub>j</sub>* contains all information in *V<sub>i</sub>* regarding *T*, the Shapley value of *V<sub>j</sub>* is larger than that of *V<sub>i</sub>*. It is worth noting that, the converse is true only under special
conditions such as when the graph is a chain (*V₁ → V₂ → ... → V<sub>i</sub> → ... → V<sub>j</sub> → ... →*

*T*). In general, the magnitude of the Shapley value of two variables do not entail their

conditional independence relationship. It is easy to consider an example where *V<sub>i</sub>* and *V<sub>j</sub>* are both parents of the target *T*, one of them could have a larger Shapley value, but none of them is conditionally independent of *T* given the other. The fact that one can not infer conditional independency from Shapley value in the general case is related to our discussion in Section 3.1. Specifically, the conditional independence relationship corresponds to the summands of Shapley value. Summing the summands together results in information loss with respect to conditional independency.

3.3 Shapley Value of Variables: Implications for Prediction and Causation In this section, we introduce two theorems that have important implications for using Shapley value for feature importance and model explanation. We focus on the Shapley values of the Markov boundary members of *T*, since these variables are of critical importance for both prediction and causation. Predictively, the Markov boundary of *T* is the most parsimonious set of variables that contains all the information regarding *T* and thus the optimal predictor set of *T* (Theorem 17). Causally, the faithful causal Bayesian networks, the Markov Boundary of *T* constitutes of the direct causes, direct effects, and direct cause of direct effects of *T* (Theorem 25). Theorem 8 *Markov boundary members of T can have smaller Shapley value compared to* *non-Markov boundary members.* Proof We proof the theorem by an example: Let *G* be a faithful Bayesian network containing 5 vertices, where *A→T*, *B→T*, *C→T*, *A→S*, *B→S*, *C→S*. The data generating process is the following:
## A ∼N(0,2<sup>2</sup>)

## B ∼N(0,2<sup>2</sup>)

## C ∼N(0,2<sup>2</sup>)

*T* = *A* + *B* + *C* + *N*(0*,*2<sup>2</sup>)

*S* = *A* + *B* + *C* + *N*(0*,*2<sup>2</sup>)

We use a linear regression model and the ordinary *R²* as the *m*(*·*) function. We have:

## m(∅) = 0

<u>1</u> *m*(*{A}*) = *m*(*{B}*) = *m*(*{C}*) = 4 <u>9</u> *m*(*{S}*) = 16 <u>1</u> *m*(*{A,B}*) = *m*(*{B,C}*) = *m*(*{A,C}*) = 2

## m({A,S}) = m({B,S}) = m({C,S}) =

<u>5</u> *m*(*{A,B,S}*) = *m*(*{A,C,S}*) = *m*(*{B,C,S}*) = 8 <u>3</u> *m*(*{A,B,C}*) = *m*(*{A,B,C,S}*) = 4

## Applying Shapley value formular, we have:

*φ<sub>A</sub>* = *φ<sub>B</sub>* = *φ<sub>C</sub>* = 95*/*576 = 0*.*1649*...*

## φ<sub>S</sub> = 49/192 = 0.2552...

The Markov Boundary members *A*, *B*, and *C* all have smaller Shapley value compared to non-Markov boundary member *S*.

Theorem 9 *The sum of the Shapley values of all Markov boundary members of T can be* *smaller than the Shapley value of a non-Markov boundary member.*

Proof We prove the theorem by an example: Let *G* be a faithful Bayesian network containing 3 vertices, where *C→A*, *C→B*, *A→T*, *B→T*. The data generating process is the following:

*P* (*C* = 1) = *P* (*C* = 2) = *P* (*C* = 3) = *P* (*C* = 4)

*P* (*A* = 1*|C* = 1) = 0*.*05;*P* (*B* = 1*|C* = 1) = 0*.*05

*P* (*A* = 1*|C* = 2) = 0*.*05;*P* (*B* = 1*|C* = 2) = 0*.*95

*P* (*A* = 1*|C* = 3) = 0*.*95;*P* (*B* = 1*|C* = 3) = 0*.*05

*P* (*A* = 1*|C* = 4) = 0*.*95;*P* (*B* = 1*|C* = 4) = 0*.*95

*P* (*T* = 1*|A* = 0*,B* = 0) = 0*.*9

*P* (*T* = 1*|A* = 0*,B* = 1) = 0*.*05

*P* (*T* = 1*|A* = 1*,B* = 0) = 0*.*15

*P* (*T* = 1*|A* = 1*,B* = 1) = 0*.*9

We compute the Shapley value for the best possible model (the model that results in irre- ducible error), such classifier will predict *T* = 1 if *P* (*T* = 1*|*S = s) *>* 0*.*5, and predict *T* = 0 ∑ otherwise. We use the *m* function: <sub>s</sub> *P*(S = s) max(*P* (*T* = 1*|*S = s)*,P*(*T* = 0*|*S = s))*.* We have:

*m*(*∅*) = 0*.*5;*m*(*{A}*) = *m*(*{B}*) = 0*.*0525;*m*(*{C}*) = 0*.*8235

*m*(*{A,B}*) = 0*.*9;*m*(*{A,C}*) = *m*(*{B,C}*) = 0*.*8597;

*m*(*{A,B,C}*) = 0*.*9;

## and the Shapley values are:

*φ<sub>A</sub>* = *φ<sub>B</sub>* = 0*.*0903*...*; *φ<sub>C</sub>* = 0*.*2194*...*

We have (*φ<sub>A</sub>* + *φ<sub>B</sub>*) *< φ<sub>C</sub>*, i.e. the sum of the Shapley values of all Markov boundary members of *T* can be smaller than that of a non-Markov boundary member.

Theroem 8 and 9 have several implications for using Shapley values in predictive modeling. With respect to feature selection, a non-zero Shapley value does not indicate a variable is non-redundant. The Shapley value of a non-Markov boundary member *C* in the proof for Theorem 9, is redundant for predicting *T* with the presence of *A* and *B*, but its Shapley value is non-zero and larger than the Markov boundary members. Similarly, a smaller Shapley value does not indicate a variable is redundant. Several recent publi- cations uses Shapley value for feature selection (Zaeri-Amirani et al., 2018; Cohen et al., 2007; Mikenina and Zimmermann, 1999; Sun et al., 2012). Typical methods either select a set of variables of a fixed size with the highest Shapley value, or employ recursive feature elimination using Shapley value as the method for ranking variables. Only selecting the top ranked several variables could potentially miss a Markov boundary member and results in suboptimal performance. Whereas, the recursive feature elimination by Shapley value could result in optimal feature set with redundant features, since any feature that have higher Shapley value than the Markov boundary member with the lowest Shapley value would be kept. With respect to model interpretation, the magnitude of Shapley value of variables do not necessarily correspond to causality. In the example from Theorem 8, *S* is neither a cause nor an effect of *T*, but it has larger Shapley value compared to all other causes of *T*. Moreover, the magnitude of Shapley value of variables also do not necessarily correspond to local causality: In the example from Theorem 9, *C* is an indirect cause *T*, but it has larger Shapley value compared to the sum of all direct causes of *T <sup>1</sup>*.

## 4. Discussion and Conclusion

In this study, we established the theoretical background for examining the Shapley value and relating it to faithful (causal) Bayesian network. This approach revealed several implications for using Shaplely value for variable importance and model explanation. We summarize the key points from this study:

- ** The summands of Shapley value correspond to conditional independency under specific definition of *m*.
- ** Using Shapley value for feature selection do not guarantee obtaining the minimal optimal feature set.
- ** Magnitude of Shapley value of variables do not necessarily correspond to causality.
- ** Variables that are in the local causal neighborhood of *T* do not necessarily have larger Shapley value compared to other variables. Despite the theoretical importance of Theorem 8 and Theorem 9, they are possibility
results proven by examples. We intend to explore the following questions in the future:

1. In general, the relationships learned by supervised learning predictive learning algorithms are not guar- anteed to reflect causal relationships. Therefore, there is no reason to believe the explanation of these models via Shapley values or other methods should reflect causality.

What are the general conditions under which the disassociation between Shapley value and causality emerges? How prevalent is the disassociation between Shapley value and causality in datasets collected from different domains? How does the performance of Shapley value based feature selection methods compare to other types of feature selection methods?

## Appendix A: Predictive Models and Variable Importance

First, we introduce a set of concepts that are related to predictive modeling. We focus our discussion on the importance of variables in the predictive model, since one of the utility of Shapley value is to access variable importance.

Definition 10 *Optimal variable set (Tsamardinos and Aliferis, 2003). Given a data set* *D sampled from p*(V*,T*)*, a learning algorithm* L*, and a performance metric* M*, variable* *set* V<sub>opt</sub> *is an optimal variable set of T if applying* L *on* V<sub>opt</sub> *maximizes the performance* *metric* M *for predicting T.*

To put it plainly, the optimal variable set V<sub>opt</sub> for predicting *T* is a subset of variables that produces a model that maximizes the predictive performance *T*. This definition is intuitive but not very useful, since it neither provides the mathematical characteristics of V<sub>opt</sub> nor a way to identify V<sub>opt</sub>. Therefore, next we introduce the Markov Blanket theory and related concepts, since it describes the statistical characteristics of the optimal variable set and provides the theoretical foundation for deriving the optimal variable set.

We first define conditional independence, a key concept underlying variable importance.

Definition 11 *Conditional Independence (Pearl, 2009). Let* V *be a set of variables and* *p*(V) *be the joint distribution over* V*, ∀*X*,* Y*,* Z *⊂* V*,* X *and* Y *are conditionally independent given* Z*, if p*(X*|*Y*,*Z) = *p*(X*|*Z)*, where p*(Z) *>* 0*.*

In other words, variables in Y do not provide additional information regarding X when Z is available. And therefore including variables in Y in a model for predicting variables in X is redundant, when Z is part of the model. We use the symbol *⊥* to represent independence and symbol *|* to represent conditioning. The statement “X and Y are conditionally independent given Z” is expressed as X *⊥* Y*|*Z. To define a variable’s relevance with respect to predicting a target variable *T*, Kohavi and John (Kohavi et al., 1997) first introduced the strong, weak, and irrelevant variables.

Definition 12 *Strong relevance. Let* S<sub>i</sub> = V*−V<sub>i</sub>, the set of all features except V<sub>i</sub>. A feature* *V<sub>i</sub> is strongly relevant to T iff there exists some v<sub>i</sub>, t, and* s<sub>i</sub> *for which p*(*V<sub>i</sub>* = *v<sub>i</sub>,* S<sub>i</sub> = s<sub>i</sub>) *>* 0*,* *such that p*(*T* = *t|V<sub>i</sub>* = *v<sub>i</sub>,* S<sub>i</sub> = s<sub>i</sub>) *6*= *p*(*T* = *t|*S<sub>i</sub> = s<sub>i</sub>)*.*

Definition 13 *Weak relevance. A feature V<sub>i</sub> is weakly relevant to T iff it is not strongly* *relevant, and ∃*S<sup>′i</sup> *⊂* S<sub>i</sub> *and some v<sub>i</sub>, t, and* s<sup>′i</sup> *for which p*(*V<sub>i</sub>* = *v<sub>i</sub>,* S<sup>′i</sup> = s<sup>′i</sup>) *>* 0*, such that* *p*(*T* = *t|V<sub>i</sub>* = *v<sub>i</sub>,* S<sup>′i</sup> = s<sup>′i</sup>) *6*= *p*(*T* = *t|*S<sub>i</sub> = s<sup>′i</sup>)*.*

Definition 14 *Irrelevance. A feature is relevant if it is either weakly relevant or strongly* *relevant; otherwise, it is irrelevant.*

The strongly relevant variables contain distinct information about *T* given all other variables, omitting them from the model will result in suboptimal models for *T*. Weakly relevant variables do not contain additional information about *T* given all other variables. But they contain additional information about *T* given a subset of other variables. They

are redundant when all the strongly relevant variables are part of the model for *T*.The irrelevant variables do not contain any information about *T*. The Kohavi and John definitions for variable relevance focus on the distinct information content regarding *T* in individual variable with respect to other variables, whereas Markov boundary and Markov blanket considers the joint information in a set of variables with respect to the target of interest.

Definition 15 *Markov blanket (Pearl, 2009; Aliferis et al., 2003). A Markov blanket* M *of the response variable T in the joint probability distribution p*(V*,T*) *is a set of variables* *conditioned on which all other variables are independent of T, that is, ∀Y ∈* V *−* M*,T ⊥* *Y |*M*.*

Definition 16 *Markov boundary (Pearl, 2009; Aliferis et al., 2003). If no proper subset of* *Markov blanket* M *of T satisfies the definition of Markov blanket of T, then* M *is a Markov* *boundary (MB) of T.*

The correspondence between Markov blanket and optimal feature set of *T* was established in the theorem below.

Theorem 17 *If* M *is a performance metric that is maximized only when p*(*T |*V) *is estimated accurately, and* L *is a learning algorithm that can approximate any conditional* *probability distribution, then variable set* M *is a Markov blanket of T if and only if it is an* *optimal feature set of T. Variable set* M *is a Markov boundary of T if and only if it is a* *minimal optimal feature set of T (Tsamardinos and Aliferis, 2003; Statnikov et al., 2013).*

## Appendix B: Faithful Bayesian Networks

We next introduce a set of concepts related to Bayesian network, since we will be examining Shapley value for predictive models built from data generated from faithful Bayesian networks.

Definition 18 *Bayesian network (Neapolitan et al., 2004). Let* V *be a set of variables and* *p be a joint probability distribution over* V*. Let G be a directed acyclic graph (DAG) such* *that all vertices of G correspond one-to-one to members of* V*. ∀X ∈* V*, X is conditionally* *independent of all non-descendants of X, given the parents of X (i.e. Markov condition* *holds). The triplet 〈*V*,G,p〉 defines a Bayesian network*

Definition 19 *Faithfulness (Spirtes et al., 2000). If all and only the conditional independence relations that are true in the joint distribution p are entailed by the Markov condition* *applied to a DAG G, then p and G are faithful to one another.*

Given faithfulness, it is possible to establish the relationship between the structural property of the Bayesian network and the statistical properties of its joint distribution. The structural property of a Bayesian network can be described with the help of d-separation and d-connection:

Definition 20 *d-separation and d-connection (Spirtes et al., 2000). A collider on a path* *p is a vertex with two incoming edges that belong to p. A path between X and Y given a* *conditioning set* Z *is open, if (i) every collider of p is in* Z *or has a descendant in* Z*, and* *(ii) no other nodes on p are in* Z*. If a path is not open, then it is blocked. Two variables X* *and Y are d-separated given a conditioning set* Z *in Bayesian network iff every path between* *X,Y is blocked. if 6∃*Z *⊂* V *that d-separates X and Y, X and Y are d-connected.*

In a faithful Bayesian Network, d-connection and d-separation (structural properties of the network) have a one-to-one correspondence to all conditional dependence and independence relations (statistical properties of the joint distribution), as stated in the Theorem 21:

Theorem 21 *Two variables X and Y are d-separated given a conditioning set* Z *in a* *faithful Bayesian network iff X ⊥ Y |*Z*. It follows, that if they are d-connected, they are* *conditionally dependent given* Z *(Spirtes et al., 2000).*

Below we list other two theorems that can be derived from Theorem 21. They are particularly useful when it comes to the local neighbourhood of a target variable of interest

*T*. Theorem 22 *In a faithful BN 〈*V*,G,p〉, there is an edge between the pair of nodes X,Y ∈* V*, iff X 6⊥ Y |*S*, ∀*S *⊆* V *−{X,Y} (Spirtes et al., 2000).* Theorem 23 *In a faithful BN 〈*V*,G,p〉, let PC*(*V<sub>i</sub>*) *denote the set containing all parents* *of children of V<sub>i</sub>. If for a triple of nodes X,T,Y in G, X ∈ PC*(*Y*)*, Y ∈ PC*(*T*)*, and* *X 6∈ PC*(*T*)*, then X → Y ← T, iff X 6⊥ T |*S *∪ Y, ∀*S *⊆* V *−{X,T} (Spirtes et al., 2000).* Appendix C: Faithful Bayesian Networks and Variable Importance in Predictive Models Also, since the notion of strongly, weakly and irrelevant variables are based on conditional independence, we can also infer their network structural properties given faithfulness (Tsamardinos and Aliferis, 2003; Aliferis et al., 2003). Theorem 24 *In a faithful Bayesian network, a variable X ∈* V *is strongly relevant if and* *only if X ∈ MB*(*T*)*..* Theorem 25 *In a faithful Bayesian network 〈*V*,G,p〉, the unique Markov boundary MB*(*T*) *correspond to the parents, children, and parents of the children of T.* Theorem 26 *Let 〈*V*∪ T,G,p〉 be a faithful Bayesian network. A variable V<sub>i</sub> ∈* V *is weakly* *relevant, iff it is not strongly relevant and there is an undirected path from V<sub>i</sub> to T.* Theorem 27 *Let 〈*V *∪ T,G,p〉 be a faithful Bayesian network. A variable V<sub>i</sub> ∈* V *is* *irrelevant, iff there is no path from V<sub>i</sub> to T.*

## Appendix D: Faithful Causal Bayesian Networks

Next, we introduce causal Bayesian network. A causal Bayesian network is a Bayesian network with causally relevant edge semantics. In a causal Bayesian network, the parents of a variable *X* are the direct causes of *X*, the children of *X* are direct effects of *X*, the non-parents ancestors of *X* are indirect causes of *X*, the non-children descendants of *X* are indirect effects of *X*. The causal edge semantics and causal Bayesian network can be defined as the following:

Definition 28 *Causation (Pearl, 2009). Let do*(*X* = *x<sub>i</sub>*) *denote a manipulation, where the* *value of X is set to x<sub>i</sub>. If ∃x<sub>i</sub>,x<sub>j</sub>, such that p*(*Y |do*(*X* = *x<sub>i</sub>*)) *6*= *p*(*Y |do*(*X* = *x<sub>j</sub>*))*, then X* *is a cause of Y.*

Definition 29 *Causal Bayesian Network (Pearl, 2009; Spirtes et al., 2000). A causal* *Bayesian network 〈*V*,G,p〉 is the Bayesian network 〈*V*,G,p〉 with the additional semantics* *that if there is an edge X → Y in G, then X directly causes Y, ∀X,Y ∈* V*. (ref citation* *Spirtes causality book)*

All the theoretical results introduced in the sections above for faithful Bayesian network applies to faithful causal Bayesian network. The main difference is, in a causal Bayesian network, structural properties can be interpreted causally. For example, Theorem 25 can be rewritten for the causal Bayesian network as below.

Theorem 30 *Let 〈*V*,G,p〉 be a faithful causal Bayesian network. The unique Markov* *boundary MB*(*T*) *corresponds to the direct causes, direct effects, and the direct causes of* *the direct effects of T.*

For brevity, we do not restate the causal correspondence for all theorems regarding faithful Bayesian network.

References

Constantin F Aliferis, Ioannis Tsamardinos, and Alexander Statnikov. Hiton: a novel markov blanket algorithm for optimal variable selection. In *AMIA Annual Symposium* *Proceedings*, volume 2003, page 21. American Medical Informatics Association, 2003.

Subhi J AlAref, Gabriel Maliakal, Gurpreet Singh, Alexander R van Rosendael, Xiaoyue Ma, Zhuoran Xu, Omar Al Hussein Alawamlh, Benjamin Lee, Mohit Pandey, Stephan Achenbach, et al. Machine learning of clinical variables and coronary artery calcium scoring for the prediction of obstructive coronary artery disease on coronary computed tomography angiography: analysis from the confirm registry. *European heart journal*, 41

(3):359–367, 2020.
Nitzan Shalom Artzi, Smadar Shilo, Eran Hadar, Hagai Rossman, Shiri Barbash-Hazan, Avi Ben-Haroush, Ran D Balicer, Becca Feldman, Arnon Wiznitzer, and Eran Segal. Prediction of gestational diabetes based on nationwide electronic health records. *Nature* *Medicine*, 26(1):71–76, 2020.

Riccardo Bellazzi and Blaz Zupan. Predictive data mining in clinical medicine: current issues and guidelines. *International journal of medical informatics*, 77(2):81–97, 2008.

Shay Cohen, Gideon Dror, and Eytan Ruppin. Feature selection via coalitional game theory. *Neural Computation*, 19(7):1939–1961, 2007.

Piotr Dworzynski, Martin Aasbrenn, Klaus Rostgaard, Mads Melbye, Thomas Alexander Gerds, Henrik Hjalgrim, and Tune H Pers. Nationwide prediction of type 2 diabetes comorbidities. *Scientific reports*, 10(1):1–13, 2020.

JB Heaton, NG Polson, and Jan Hendrik Witte. Deep learning for finance: deep portfolios. *Applied Stochastic Models in Business and Industry*, 33(1):3–12, 2017.

Ron Kohavi, George H John, et al. Wrappers for feature subset selection. *Artificial intelli-* *gence*, 97(1-2):273–324, 1997.

Zachary C Lipton. The mythos of model interpretability. *Queue*, 16(3):31–57, 2018.

Scott Lundberg. Shap python package. [https://github.com/slundberg/shap](https://github.com/slundberg/shap), 2018. Ac- cessed: 2020-05-12.

Scott M Lundberg and Su-In Lee. A unified approach to interpreting model predictions. In *Advances in neural information processing systems*, pages 4765–4774, 2017.

Lara Mikenina and H-J Zimmermann. Improved feature selection and classification by the 2-additive fuzzy measure. *Fuzzy sets and systems*, 107(2):197–218, 1999.

Richard E Neapolitan et al. *Learning bayesian networks*, volume 38. Pearson Prentice Hall Upper Saddle River, NJ, 2004.

Art B Owen and Cl´ementine Prieur. On shapley value for measuring importance of dependent inputs. *SIAM/ASA Journal on Uncertainty Quantification*, 5(1):986–1002, 2017.

Judea Pearl. *Causality*. Cambridge university press, 2009.

Lloyd S Shapley. A value for n-person games. *Contributions to the Theory of Games*, 2(28): 307–317, 1953.

Navin Sharma, Pranshu Sharma, David Irwin, and Prashant Shenoy. Predicting solar generation from weather forecasts using machine learning. In *2011 IEEE international conference on smart grid communications (SmartGridComm)*, pages 528–533. IEEE, 2011.

Anthony F Shorrocks. Decomposition procedures for distributional analysis: a unified framework based on the shapley value. Technical report, mimeo, University of Essex,

1999.
Peter Spirtes, Clark N Glymour, Richard Scheines, and David Heckerman. *Causation,* *prediction, and search*. MIT press, 2000.

Alexander Statnikov, Nikita I Lytkin, Jan Lemeire, and Constantin F Aliferis. Algorithms for discovery of multiple markov boundaries. *Journal of Machine Learning Research*, 14 (Feb):499–566, 2013.

Erik Štrumbelj and Igor Kononenko. Explaining prediction models and individual predictions with feature contributions. *Knowledge and information systems*, 41(3):647–665,

2014.
Xin Sun, Yanheng Liu, Jin Li, Jianqi Zhu, Xuejie Liu, and Huiling Chen. Using cooperative game theory to optimize the feature selection problem. *Neurocomputing*, 97:86–93, 2012.

Ioannis Tsamardinos and Constantin F Aliferis. Towards principled feature selection: rele- vancy, filters and wrappers. In *AISTATS*, 2003.

SHI Xingjian, Zhourong Chen, Hao Wang, Dit-Yan Yeung, Wai-Kin Wong, and Wang- chun Woo. Convolutional lstm network: A machine learning approach for precipitation nowcasting. In *Advances in neural information processing systems*, pages 802–810, 2015.

Mohammad Zaeri-Amirani, Fatemeh Afghah, and Sajad Mousavi. A feature selection method based on shapley value to false alarm reduction in icus a genetic-algorithm approach. In *2018 40th Annual International Conference of the IEEE Engineering in* *Medicine and Biology Society (EMBC)*, pages 319–323. IEEE, 2018.
