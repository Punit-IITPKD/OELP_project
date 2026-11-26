Source: https://link.springer.com/article/10.1007/s10994-023-06336-7
Title: Classifier calibration: a survey on how to assess and improve predicted class probabilities | Machine Learning | Springer Nature Link
Fetched: 2026-11-26T15:58:18.459Z

Loading \[MathJax\]/jax/output/SVG/fonts/TeX/Main/Bold/Main.js

 [Skip to main content](https://link.springer.com/article/10.1007/s10994-023-06336-7#main)

## Search

Search by keyword or author

Search

## Navigation

- [Find a journal](https://link.springer.com/journals/)
- [Publish with us](https://www.springernature.com/gp/authors)
- [Track your research](https://link.springernature.com/home/)

# Classifier calibration: a survey on how to assess and improve predicted class probabilities

- [Open access](https://www.springernature.com/gp/open-science/about/the-fundamentals-of-open-access-and-open-research)
- Published: 16 May 2023

- Volume 112, pages 3211–3260 (2023)

- [Cite this article](https://link.springer.com/article/10.1007/s10994-023-06336-7#citeas)

You have full access to this open access article

[Download PDF](https://link.springer.com/content/pdf/10.1007/s10994-023-06336-7.pdf)

Save article

[View saved research](https://link.springer.com/saved-research)

[![](https://media.springernature.com/w72/springer-static/cover-hires/journal/10994?as=webp)Machine Learning](https://link.springer.com/journal/10994) [Aims and scope](https://link.springer.com/journal/10994/aims-and-scope) [Submit manuscript](https://submission.springernature.com/new-submission/10994/3)

Classifier calibration: a survey on how to assess and improve predicted class probabilities


[Download PDF](https://link.springer.com/content/pdf/10.1007/s10994-023-06336-7.pdf)

## Abstract

This paper provides both an introduction to and a detailed overview of the principles and practice of classifier calibration. A well-calibrated classifier correctly quantifies the level of uncertainty or confidence associated with its instance-wise predictions. This is essential for critical applications, optimal decision making, cost-sensitive classification, and for some types of context change. Calibration research has a rich history which predates the birth of machine learning as an academic field by decades. However, a recent increase in the interest on calibration has led to new methods and the extension from binary to the multiclass setting. The space of options and issues to consider is large, and navigating it requires the right set of concepts and tools. We provide both introductory material and up-to-date technical details of the main concepts and methods, including proper scoring rules and other evaluation metrics, visualisation approaches, a comprehensive account of post-hoc calibration methods for binary and multiclass classification, and several advanced topics.

### Similar content being viewed by others

![](https://media.springernature.com/w92h120/springer-static/cover-hires/book/978-3-031-08974-9?as=webp)

### [Classifier Probability Calibration Through Uncertain Information Revision](https://link.springer.com/chapter/10.1007/978-3-031-08974-9_48?fromPaywallRec=false)

Chapter© 2022

![](https://media.springernature.com/w92h120/springer-static/cover-hires/book/978-3-031-63800-8?as=webp)

### [Investigating Calibrated Classification Scores Through the Lens of Interpretability](https://link.springer.com/chapter/10.1007/978-3-031-63800-8_11?fromPaywallRec=false)

Chapter© 2024

![](https://media.springernature.com/w92h120/springer-static/cover-hires/book/978-3-030-86380-7?as=webp)

### [Estimating Expected Calibration Errors](https://link.springer.com/chapter/10.1007/978-3-030-86380-7_12?fromPaywallRec=false)

Chapter© 2021

### Explore related subjects

Discover the latest articles, books and news in related subjects, suggested using machine learning.

- [Data Mining](https://link.springer.com/subjects/data-mining)
- [Categorization](https://link.springer.com/subjects/categorization)
- [Machine Learning](https://link.springer.com/subjects/machine-learning)
- [Probability and Statistics in Computer Science](https://link.springer.com/subjects/probability-and-statistics-in-computer-science)
- [Learning algorithms](https://link.springer.com/subjects/learning-algorithms)
- [Statistical Learning](https://link.springer.com/subjects/statistical-learning)
- [Evidential Reasoning and Classification in Uncertain Data](https://link.springer.com/subjects/evidential-reasoning-and-classification-in-uncertain-data)

## 1 Introduction and motivation

A _K_-class probabilistic classifier is _well-calibrated_ if among test instances receiving a predicted _K_-dimensional probability vector {\\textbf{s}}, the class distribution is (approximately) distributed as {\\textbf{s}}. This property is of fundamental importance when using a classifier for cost-sensitive classification, for human decision making, or within an autonomous system. It means that the classifier correctly quantifies the level of uncertainty or confidence associated with its predictions. In a binary setting, scores given by a sufficiently calibrated classifier can be simply thresholded to minimise expected misclassification cost. Thresholds can also be derived to optimally adapt to a change in class prior, or to a combination of both. In contrast, for a poorly calibrated classifier the optimal thresholds cannot be obtained without optimisation.

Many machine learning algorithms are known to produce over-confident models, unless dedicated procedures are applied during training. The goal of _(post-hoc) calibration methods_ is to use hold-out validation data to learn a _calibration map_ for a previously trained model that transforms the model’s predictions to be better calibrated. Many calibration methods for binary classifiers have been introduced, including logistic calibration (also known as ‘Platt scaling’), various binning methods including isotonic calibration (also known as the ROC convex hull method), as well as more recent methods including beta calibration and Bayesian methods.

When we have more than two classes, calibration is generally more involved, as is often the case with multiclass classification. Multiclass calibration has mostly been approached by decomposing the problem into _K_ one-vs-rest binary calibration tasks, one for each class. The predictions of these _K_ calibration models form unnormalised probability vectors, which, after normalisation, may not be calibrated in a multiclass sense. Native multiclass calibration methods were introduced recently focusing on neural networks. These methods constitute various multiclass extensions of Platt scaling, adding a calibration layer between the logits of the neural network and the softmax layer.

The literature on post-hoc classifier calibration in machine learning is now sufficiently rich that it is no longer straightforward to obtain or maintain a good overview of the area, which was the main motivation for writing this survey. It grew out of a tutorial we presented at the 2020 European Conference on Machine Learning and Principles and Practice of Knowledge Discovery in Databases (see [https://classifier-calibration.github.io](https://classifier-calibration.github.io/)). Our aim then and now is to provide both introductory material and up-to-date technical details of the main concepts and methods. Our focus is on the classical setup where the classifier is deployed in the same setting where it was calibrated, except for potential changes in class prior or misclassification costs. We do not cover methods to achieve robustness under conditions of other distributional shifts or out-of-distribution inputs (Ovadia et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR60 "Ovadia, Y., Fertig, E., Ren, J., Nado, Z., Sculley, D., Nowozin, S., Dillon, J., Lakshminarayanan, B., & Snoek, J. (2019). Can you trust your model’s uncertainty? Evaluating predictive uncertainty under dataset shift. Advances in Neural Information Processing Systems, 32.")). We try to do justice to historical developments and pay attention to important topics that are not as widely known as they deserve to be, such as proper scoring rules.

We also try to identify and clarify possible sources for confusion. The multiclass setting in particular introduces numerous subtleties that have not always been recognised or correctly dealt with in previous work. For example, some authors use the weaker notion of _confidence calibration_, which requires only that the classifier’s predicted probability for what it considers the most likely class is calibrated. While this is perfectly valid in its own right, it isn’t always appreciated by subsequent authors that this is a much weaker notion of calibration than the one defined informally in the first sentence of this survey. One can also observe variations in the evaluation metric used and in the way calibrated probabilities are visualised. Our main aim in this survey is hence to provide a unified perspective on the different methods and metrics for binary and multiclass calibration, giving each variation its proper place.

For the purpose of this survey we have developed a Python library which includes most of the functionalities presented in the following sections. PyCalib [Footnote 1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fn1) implements several calibration metrics (eg. confidence and classwise ECE, and their MCE counterparts), common calibration methods (eg. Isotonic Calibration, Platt’s Scaling, Binning calibration), a method to combine arbitrary classifiers and calibrators into a unified training and deployment pipeline, a one-vs-the-rest implementation to adapt any binary calibration method to the multiclass setting, and multiple visualisation tools to inspect visually the calibration quality as well as tools to get better insights about the learned calibration maps. As an illustration of the library’s capabilities, most of the figures and results reported in this paper have been generated using PyCalib.

The survey is structured as follows. The next section will cover important notions and intuitions related to calibration. It aims to be at a more introductory level, leaving technical detail for later sections. Section [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec6) discusses proper scoring rules, an important general framework for evaluation of probability estimates. In Sect. [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec8) we present systematic overview of visualisation approaches and evaluation metrics for classifier calibration. Section [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec13) is devoted to a comprehensive account of post-hoc calibration methods for both the binary and multiclass scenarios. Section [6](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec30) covers hypothesis tests for calibration, and Sect. [7](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec31) concludes with a summary and outlook.

## 2 A brief introduction to classifier calibration

The origins of classifier calibration can be traced back to weather forecasting and meteorology. Here is what the UK Met Office website used to say about what their forecast probabilities mean:

> “\[S\]uppose the Met Office says that the probability of rain tomorrow in your region is 80%. They aren’t saying that it will rain in 80% of the land area of your region, and not rain in the other 20%. Nor are they saying it will rain for 80% of the time. What they are saying is there is an 80% chance of rain occurring at any one place in the region, such as in your garden. \[...\] \[A\] forecast of 80% chance of rain in your region should broadly mean that, on about 80% of days when the weather conditions are like tomorrow’s, you will experience rain where you are. \[...\] If it doesn’t rain in your garden tomorrow, then the 80% forecast wasn’t wrong, because it didn’t say rain was certain. But if you look at a long run of days, on which the Met Office said the probability of rain was 80%, you’d expect it to have rained on about 80% of them. ” ( [https://web.archive.org/web/20210928235732/https://www.metoffice.gov.uk/about-us/what/accuracy-and-trust/probability](https://web.archive.org/web/20210928235732/https://www.metoffice.gov.uk/about-us/what/accuracy-and-trust/probability))

Note the phrase “a long run of days”: determining the degree to which a forecaster is well-calibrated cannot be done on a per-forecast basis, but rather requires looking at a sufficiently large and diverse set of forecasts.

**Table 1 Reproduced from Hallenbeck ( [1920](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR26 "Hallenbeck, C. (1920). Forecasting precipitation in percentages of probability. Monthly Weather Review, 48(11), 645–647."))**

[Full size table](https://link.springer.com/article/10.1007/s10994-023-06336-7/tables/1)

**Fig. 1**

![Fig. 1](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig1_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/1)

Two different graphical representations of the forecasts in Table [1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab1). **(Left)** The bottom graph gives a histogram of the probability forecasts. The top graph compares the forecast probabilities with the proportion of actual rain events in that bin. The red bars indicate to what extent these proportions are higher or lower than predicted. **(Right)** A simplified visualisation, only showing the proportion of rain events in a bin (y-axis) against the average prediction in the bin (x-axis)

Table [1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab1), reproduced from Hallenbeck ( [1920](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR26 "Hallenbeck, C. (1920). Forecasting precipitation in percentages of probability. Monthly Weather Review, 48(11), 645–647.")), groups 123 weather forecasts in 10 equal-width bins, and compares each bin with the actual empirical percentage of rain events. Figure [1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig1) shows two possibilities of displaying this information graphically, comparing the predicted probabilities on the _x_-axis to empirical probabilities on the _y_-axis. A variety of such graphical representations can be found in the literature; they are generally known as _reliability diagrams_, ‘reliability’ being one of many terms used to denote goodness of calibration (Murphy & Winkler, [1977](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR56 "Murphy, A. H., & Winkler, R. L. (1977). Reliability of subjective probability forecasts of precipitation and temperature. Journal of the Royal Statistical Society Series C (Applied Statistics), 26(1), 41–47.")). We can see that most of the forecasts are slight under-estimates: for example, of the 15 forecasts in the 40–49% bin, 8/15=53\\% were actual rain events. In the left graph this is shown by the vertical red line, which indicates how much the top of the blue bar extends above the diagonal (meaning that the actual proportion of rain events was higher than estimated). On the right graph this can be seen directly from how much the respective point is higher than the diagonal. Similarly, we see that two of the bins (20–29% and 30–39%) are very slight over-estimates: on the left graph the top of the blue bar is below the diagonal, which means that the actual proportion of rain events was lower than estimated.

**Fig. 2**

![Fig. 2](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig2_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/2)

Dividing the forecasts in Table [1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab1) in five (left figure) and two (right figure) equal-width bins

The choice of ten equal-width bins is somewhat arbitrary, and it is informative to consider different choices. Merging pairs of adjacent bins results in five equal-width bins, as depicted in Fig. [2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig2) (left). We see that all but the right-most bin averages are now slightly off-centre (we assumed that within each original bin all forecast probabilities are the same and equal to the bin centre: e.g., 25% in the 20–29% bin). Again, the pattern is that the higher forecast probabilities are about 10% too low. Figure [2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig2) (right) shows what we get with only two bins. We have lost a bit too much information here, so bins shouldn’t be taken too wide. On the other hand they shouldn’t be taken too narrow either, in order to be able to measure the true proportion of rain events with sufficient resolution.

Taking the forecast event as a binary variable means that the calibration concept is directly applicable to binary classification. Here is an example from the typical machine learning task of learning a classifier for distinguishing ‘junk’ or ‘spam’ emails from regular ones:

> A prediction ‘70% chance of spam’ should be spam 70% of the time.

And a generalisation to categorical variables with more than two values is equally straightforward, as this example from Fisher’s famous Iris dataset shows:

> A prediction ‘70% chance of setosa, 10% chance of versicolor and 20% chance of virginica’ should be setosa/versicolor/virginica 70/10/20% of the time.

So, to sum up: _A predicted probability (vector) should match empirical (observed) probabilities._ In the language of predictive machine learning, given an instance space {\\mathbb {X}}, a binary target space {\\mathbb {Y}} = \\{+, -\\}, and a binary probabilistic classifier {\\textsf{f}}:{\\mathbb {X}}\\rightarrow \[0, 1\], the binary classifier is _calibrated_ if \\forall s \\in \[0,1\]:

\\begin{aligned} {\\textsf{P}}(Y=+ \\, \| \\, {\\textsf{f}}({\\textbf{X}}) = s)=s \\end{aligned}

### 2.1 Why calibration matters

What are the benefits of using well-defined calibrated scales in general, and well-calibrated probabilities in particular? One obvious benefit of calibrated scales is that we can easily combine measurements that are expressed on the same scale without comparing apples and oranges. Another is that we can use standardised decision rules, e.g., defining a fever as a body temperature exceeding 100 degrees Fahrenheit. These benefits directly carry over to the class probability scenario, justifying decision rules such as predicting the class whose estimated probability exceeds 0.5 in binary classification, or the class with the highest predicted probability for multiclass classification. Importantly, there is a further benefit to using calibrated probabilities as it means we can adjust these decision rules in a straightforward way to account for different class priors or misclassification costs, as we will briefly discuss presently.

Let c = \\frac{{\\textsf{C}}(+\|-)}{{\\textsf{C}}(+\|-) + {\\textsf{C}}(-\|+)} be the cost of a false positive in proportion to the combined cost of one false positive and one false negative. With these cost parameters the Bayes-optimal decision rule is to set the decision threshold to _c_. For instance, if false positives are 4 times as costly as false negatives then we set the decision threshold to 4/(4+1)=0.8 in order to only make positive predictions if we are sufficiently certain. Similar reasoning applies to changes in class priors:

- If we trained on balanced classes but want to deploy with 4 times as many positives compared to negatives, we lower the decision threshold to 0.2;

- More generally, if we trained for class ratio _r_ and deploy for class ratio r' we set the decision threshold to r/(r+r').


Cost and class prior changes can be combined in the obvious way; see Flach ( [2014](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR18 "Flach, P. (2014). Classification in context: Adapting to changes in class and cost distribution. In First international workshop on learning over multiple contexts at European conference on machine learning and principles and practice of knowledge discovery in databases (ECML-PKDD).")) for details.

In summary, an important reason to be interested in calibrating our classifiers is that default decision rules such as predicting the class with the highest predicted probability are fully justified from a decision-theoretic point of view, and can easily be adapted to changes in class and cost distributions. In contrast, poorly calibrated classifiers such as naive Bayes will often perform sub-optimally with default decision rules. It is possible to learn a better decision rule for a given cost and class skew using, e.g., ROC analysis (Lachiche & Flach, [2003](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR45 "Lachiche, N., & Flach, P. A. (2003). Improving accuracy and cost of two-class and multi-class probabilistic classifiers using roc curves. In Proceedings of the 20th International Conference on Machine Learning (ICML-03), (pp. 416–423).")) but this would have to be repeated each time the skew changes. The great advantage of post-calibration is that it only needs to be done once – in a sense, it optimises all possible decision rules in one go.

### 2.2 Common forms of miscalibration, and how to fix them

There are many reasons why a probabilistic classifier might produce miscalibrated scores, and hence many ways in which miscalibration manifests itself, but two main types stand out: underconfidence and overconfidence. In this section we look at some examples and introduce two mitigation techniques.

Figure [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig3), taken from Niculescu-Mizil and Caruana ( [2005](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR59 "Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In 22nd International Conference on Machine Learning (ICML’05), (pp. 625–632), New York, New York, USA. ACM Press.")), shows two typical examples. In both cases the points in the reliability diagram are far from the diagonal, although the effect is smaller in the figure on the right.

**Fig. 3**

![Fig. 3](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig3_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/3)

Examples of under- and overconfident classifiers. The axes are the same as for the previous figures: x-axis shows predicted probabilities and y-axis shows empirical probabilities. The dots represent the reliability diagram, and the lines show the best-fit logistic curve and beta curve. Note that the logistic sigmoid is a good fit for underconfident scores but not for overconfidence. The figure has been adapted from Niculescu-Mizil and Caruana ( [2005](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR59 "Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In 22nd International Conference on Machine Learning (ICML’05), (pp. 625–632), New York, New York, USA. ACM Press.")), and the beta curves have been added

What do we see in the left figure? It is quite natural to give precedence to vertical information in such graphs, so you might be inclined to say “The points on the left are too low, and the points on the right are too high”. But keeping in mind that the predicted probabilities on the _x_-axis are under our control but not the empirical probabilities on the _y_-axis, a more ‘actionable’ way to express this is

> The lower points are too far to the right, and the higher points are too far to the left. In other words, the points have a tendency to sit too close to the midpoint on the _x_-axis.

This is the typical pattern displayed by an _underconfident_ classifier, which thinks it’s worse at separating classes than it actually is.

Hence, to mitigate this, we need to pull predicted probabilities away from the centre. As the left plot in Fig. [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig3) shows, this can be neatly modelled by a sigmoidal logistic curve, which can be defined in parametric form as

\\begin{aligned} {\\textsf{c}}(s; w, m)&= \\frac{1}{1+\\exp (-w(s-m))} \\end{aligned}

Here, _s_ is the uncalibrated score produced by the classifier and {\\textsf{c}} gives the logistically calibrated score. _m_ and _w_ are the two parameters of the logistic family, which determine the point where {\\textsf{c}}(s)=0.5 and the slope at that point, respectively. They can be estimated from the points in the reliability diagram in order to find the best fit. In this case they can be obtained analytically as the mean of the classwise average scores, and the difference between those two means in proportion to the score variance (Flach, [2012](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR17 "Flach, P. (2012). Machine learning: The art and science of algorithms that make sense of data. Cambridge: Cambridge University Press.")).

The fitted logistic curve thus establishes a _calibration map_ which transforms uncalibrated scores _s_ into calibrated scores {\\textsf{c}}(s). Even though the calibration map doesn’t map to empirical probabilities, plotting it over the reliability diagram allows us to see clearly that if we project each point in the reliability diagram vertically onto the calibration map, and replace its _x_-value with the corresponding _y_-value of the projection, we end up with points on or very close to the diagonal, and hence near-perfectly calibrated scores (Fig. [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig4)).

**Fig. 4**

![Fig. 4](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig4_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/4)

Graphical illustration of how a well-fitted calibration map leads to near-perfect calibration. From left to right, the dotted arrows show (1) using a point’s uncalibrated score _s_ on the _x_-axis as input to the calibration map, (2) mapping the resulting output {\\textsf{c}}(s) back to the diagonal, and (3) combine with the empirical probability of the point we started from. The closer the original point is to the fitted calibration map, the closer the calibrated point (in red) will be to the diagonal

The logistic curve is widely used as a ‘squashing function’, compressing values on a possibly unbounded scale into the \[0, 1\] interval. Following Platt ( [2000](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR63 "Platt, J. (2000). Probabilities for SV Machines. In A. J. Smola, P. Bartlett, B. Schölkopf, & D. Schuurmans (Eds.), Advances in Large-Margin Classifiers (pp. 61–74). Cambridge: MIT Press.")) it is often used as a way to convert scores from a Support Vector Machine into probabilities. Technically this isn’t calibration as SVM scores are not probabilities but (signed) geometric distances from the decision boundary – this is also called _scaling_ to emphasise the difference (hence the popular name ‘Platt scaling‘). The parametric form of the logistic map can be derived from first principles by assuming that within each class the uncalibrated scores are normally distributed with the same variance.

The other common form of miscalibration is overconfidence, as exemplified in Fig. [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig3) b, c. An _overconfident_ classifier thinks it’s better at separating classes than it actually is. Hence we need to make predicted probabilities less extreme by pushing them toward the centre. The paper we took this figure from Niculescu-Mizil and Caruana ( [2005](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR59 "Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In 22nd International Conference on Machine Learning (ICML’05), (pp. 625–632), New York, New York, USA. ACM Press.")) also fitted a logistic curve to this reliability diagram Fig. [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig3) b, because they were investigating the effect of Platt scaling in a wide range of scenarios. But we see clearly that the fit is rather poor, and using this logistic curve as a calibration map is likely to make matters worse. In this particular case we would be looking for something that can produce an inverse sigmoidal curve. What would be a principled way to achieve this?

One approach that works well is to model the classwise scores with Beta distributions (Kull et al., [2017a](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR41 "Kull, M., Silva Filho, T., & Flach, P. (2017a). Beta calibration: A well-founded and easily implemented improvement on logistic calibration for binary classifiers. In A. Singh, & J. Zhu (Eds.), In Proceedings of the 20th International Conference on Artificial Intelligence and Statistics, vol. 54 of Proceedings of Machine Learning Research, (pp. 623–631). Fort Lauderdale, FL, USA. PMLR, PMLR."), [2017b](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR42 "Kull, M., Silva Filho, T. M., & Flach, P. (2017). Beyond sigmoids: How to obtain well-calibrated probabilities from binary classifiers with beta calibration. Electronic Journal of Statistics, 11(2), 5052–5080.")). These assume random variables bounded in \[0, 1\] which is exactly what we need for post-hoc calibration. Beta distributions can easily model the skewed distributions resulting from overconfident classifiers, as demonstrated in Fig. [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig3) b. Mathematically, these curves have three parameters:

\\begin{aligned} {\\textsf{c}}(s; a, b, c)&= \\frac{1}{1+\\exp (-a \\ln s + b \\ln (1-s) - c)} \\end{aligned}

This additional degree of freedom allows Beta calibration to produce both sigmoidal and inverse-sigmoidal calibration maps. It can even fit the identity map (a=b=1, c=0), which means that Beta calibration can recognise that scores are already calibrated. In contrast, applying logistic calibration to a calibrated classifier will decalibrate it. While Beta calibration can achieve many shapes of calibration maps, it is still a limited parametric family. Methods to fit richer calibration map families will be discussed in Sect. [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec13).

### 2.3 Multiclass calibration

The examples we have seen so far all relate to binary classification. Is it straightforward to generalise calibration concepts and methods to more than two classes? The answer to this question is somewhat involved. Some ideas do generalise quite easily: for example, we can model per-class scores by multivariate distributions such as Dirichlet distributions (Kull et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR40 "Kull, M., Perello-Nieto, M., Kängsepp, M., Filho, T. S., Song, H., & Flach, P. (2019). Beyond temperature scaling: Obtaining well-calibrated multiclass probabilities with Dirichlet calibration. Advances in Neural Information Processing Systems (NeurIPS’19), 32, 12316–12326.")). Some other ideas don’t generalise easily at all: for example, a multiclass generalisation of isotonic regression is not straightforward because rankings are inherently bipartite. Such approaches therefore need to be approximated by considering classes in a pairwise or one-versus-rest manner.

This helps to explain why there is divergence even at a definitional level. There are at least three different ways of _defining_ what it means to be calibrated in a multiclass setting. They are equivalent for binary classification but increasingly stronger for more than two classes,[Footnote 2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fn2) and can be summarised as follows:

- Confidence calibration: only consider the highest predicted probability.

- Classwise calibration: only consider marginal probabilities.

- Multiclass calibration: consider the entire vector of predicted probabilities.


We will use this terminology throughout the paper to avoid confusion.

_Confidence calibration_ was proposed by Guo et al. ( [2017](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR24 "Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In 34th International Conference on Machine Learning, (pp. 1321–1330), Sydney, Australia. PMLR.")), although not under that name. It requires that among all instances where the probability of _the most likely class_ is predicted to be \\alpha, the expected accuracy is \\alpha. Let {\\mathbb {X}} denote the instance space and {\\mathbb {P}}\_{{\\mathbb {Y}}} the probability _K_-simplex, then a probabilistic classifier {\\textsf{f}}:{\\mathbb {X}}\\rightarrow {\\mathbb {P}}\_{{\\mathbb {Y}}} is _confidence-calibrated_, if for any confidence level \\alpha \\in \[0,1\], the actual proportion of the predicted class, among all possible instances {\\textbf{x}} being predicted this class with confidence \\alpha, is equal to \\alpha:

\\begin{aligned} {\\textsf{P}}(Y={\\hat{Y}} \\, \| \\, S\_{{\\hat{Y}}}=\\alpha )=\\alpha \\qquad \\text {where }\ {\\hat{Y}}=\\mathop {\\textrm{argmax}}\\limits \_j S\_j. \\end{aligned}

Here, S\_j denotes the _j_-th dimension of {\\textsf{f}}({\\textbf{X}}).

_Classwise calibration_, proposed by Zadrozny and Elkan ( [2002](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR87 "Zadrozny, B. & Elkan, C. (2002). Transforming classifier scores into accurate multiclass probability estimates. In 8th ACM SIGKDD international conference on Knowledge discovery and data mining - KDD ’02, (pp. 694–699), New York, New York, USA. ACM Press.")), requires that all _one-vs-rest_ probability estimators obtained from the original multiclass model are calibrated. Formally, a probabilistic classifier {\\textsf{f}}:{\\mathbb {X}}\\rightarrow {\\mathbb {P}}\_{{\\mathbb {Y}}} is _classwise-calibrated_, if for any class i \\in \\{1, \\dots , K\\} and any predicted probability value s \\in \[0, 1\] for this class, the actual proportion of class _i_, among all possible instances on the random variable {\\textbf{X}} getting the same prediction on class i, is equal to _s_:

\\begin{aligned} {\\textsf{P}}(Y=i\\mid S\_i=s)=s \\end{aligned}

_Multiclass calibration_, also called _calibration in the strong sense_ (Widmann et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR83 "Widmann, D., Lindsten, F., & Zachariah, D. (2019). Calibration tests in multi-class classification: A unifying framework. Advances in Neural Information Processing Systems, 32, 12257–12267.")), is the strongest form of calibration for more than two classes, subsuming the previous two definitions. A probabilistic classifier {\\textsf{f}}:{\\mathbb {X}}\\rightarrow {\\mathbb {P}}\_{{\\mathbb {Y}}} is _multiclass-calibrated_ if for any prediction vector {\\textbf{s}}=\[s\_1,\\dots ,s\_K\]\\in {\\mathbb {P}}\_{{\\mathbb {Y}}}, the proportions of classes among all possible instances on the random variable {\\textbf{X}} getting the same prediction {\\textsf{f}}({\\textbf{X}})={\\textbf{s}} are equal to the prediction vector {\\textbf{s}}:

\\begin{aligned} {\\textsf{P}}(Y=i\\mid {\\textsf{f}}({\\textbf{X}})={\\textbf{s}})=s\_i\\qquad \\text {for }\ i=1,\\dots ,K. \\end{aligned}

For practical purposes, the conditions in these definitions need to be relaxed. This is where binning comes in. Once we define the bins, we can draw a reliability diagram as in the two-class case. For classwise calibration, we can show per-class reliability diagrams or a single averaged one. One way to assess the degree of calibration is by means of the gaps in the reliability diagram. These topics will be explored in Sect. [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec8). We will first take a closer look at the important concept of _proper scoring rules_ in the next section. Proper scoring rules are instance-wise evaluation measures for probability estimates that avoid the need for score binning. As a result they cannot measure the degree of calibration directly, but through decomposition results, we will show how the scores can be decomposed into various components, including the calibration loss.

## 3 From proper scoring rules to calibration

As early as 1950 researchers were interested in scoring functions that would evaluate probabilistic forecasts without influencing the forecaster into making undesirable predictions (Brier, [1950](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR6 "Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. Monthly Weather Review, 78(1), 1–3.")), thus keeping the forecaster “honest” while encouraging useful forecasts. In the late 1960s the term _proper scoring rule_ was already in use for score functions whose computation was based on a forecaster’s probabilities and the actual occurrence or not of the corresponding events (Winkler, [1969](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR85 "Winkler, R. L. (1969). Scoring rules and the evaluation of probability assessors. Journal of the American Statistical Association, 64(327), 1073–1078.")). Informally, a scoring rule is said to be proper if optimal values are obtained by the forecaster predicting the true probabilities of the events. Proper scoring rules and their ability to induce useful and accurate forecasts also lend themselves to game-theoretic interpretations, as discussed in the seminal work of Savage ( [1971](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR70 "Savage, L. J. (1971). Elicitation of personal probabilities and expectations. Journal of the American Statistical Association, 66(336), 783–801.")).

Before diving into details, let us introduce the notation. In a multiclass classification task with _K_ classes, let the true class of an instance be a vector \\dot{{\\textbf{y}}}=\[y\_1,\\ldots ,y\_K\], where y\_j = 1 when the true class is _j_, otherwise y\_j = 0. Additionally, let {\\textbf{s}}=\[s\_1,\\ldots ,s\_K\] be a class probability vector obtained from a classification model for an instance, i.e. s\_j \\ge 0, j=1,\\ldots ,K and \\sum ^K\_{j=1} s\_j = 1. A scoring rule \\phi ({\\textbf{s}}, \\dot{{\\textbf{y}}}) is a non-negative measure of how well the estimated probability vector {\\textbf{s}} matches the true class vector \\dot{\\textbf{y}}. We assume that lower values of \\phi ({\\textbf{s}}, \\dot{{\\textbf{y}}}) are better.[Footnote 3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fn3)

Popular scoring rules include Brier score \\phi \_{\\text {BS}} and log-loss \\phi \_{\\text {LL}}, which are defined as follows:

\\begin{aligned} \\phi \_{\\text {BS}}({\\textbf{s}}, \\dot{\\textbf{y}})= & {} \\sum \_{j=1}^{K} (s\_j - y\_j)^2. \\end{aligned}

(1)


\\begin{aligned} \\phi \_{\\text {LL}}({\\textbf{s}}, \\dot{\\textbf{y}})= & {} - \\sum \_{j=1}^{K} y\_j \\log s\_j. \\end{aligned}

(2)


Our Brier score definition ranges between 0 and 2, agreeing with Brier’s original definition (Brier, [1950](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR6 "Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. Monthly Weather Review, 78(1), 1–3.")), although it is now common for half this quantity to be called Brier score. While scoring rules evaluate the loss incurred by the class probability estimates for a single instance, we are usually interested in evaluating the performance of a model on test data. Thus, given a test dataset, we can calculate the empirical loss as the average instance-wise loss across the data.

Suppose the class labels \\dot{\\textbf{y}} are drawn from the true distribution {\\textbf{q}} over classes. A scoring rule \\phi is proper if its expected value on probability vector {\\textbf{s}} and \\dot{\\textbf{y}} is higher than (i.e., worse) or the same as its expected value on {\\textbf{q}} and \\dot{\\textbf{y}}, that is if

\\begin{aligned} {\\textsf{E}}\_{\\dot{\\textbf{y}} \\sim {\\textbf{q}}} \\Big \[ \\phi \\big ({\\textbf{s}}, \\dot{\\textbf{y}}\\big ) \\Big \] \\ge {\\textsf{E}}\_{\\dot{\\textbf{y}} \\sim {\\textbf{q}}} \\Big \[ \\phi \\big ({\\textbf{q}}, \\dot{\\textbf{y}}\\big ) \\Big \], \\end{aligned}

and it is strictly proper if and only if both sides of the expression being equal implies {\\textbf{s}} = {\\textbf{q}}. Both Brier score and log-loss are strictly proper scoring rules.

Among proper scoring rules, log-loss in particular is frequently used as the training loss of machine learning methods such as neural networks, often under the name of cross-entropy. It is also the loss function used by most of the calibration methods discussed in Sect. [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec13), including Platt scaling, temperature scaling and its variations (vector and matrix), beta calibration and Dirichlet calibration. A notable exception is isotonic calibration, which optimised Brier score.

At the instance level, log-loss only depends on the predicted class probability for the true class (as all other classes y\_j are zero) and it might not be obvious why it is a proper scoring function. For example, one could argue that it does not matter whether the model predicts \[0.8, 0.2, 0.0\] or \[0.8, 0.1, 0.1\] on an instance of class 1, as log-loss would be -\\ln (0.8) in both cases. However, one needs to keep in mind that properness is defined as an expectation over a population. For instance, suppose that, for a population of instances, the true probability is \[0.8, 0.2, 0.0\]. In this case, the expected log-loss will be -(0.8 \\log (s\_1) + 0.2 \\log (s\_2)), which can only be minimised by predicting the probability vector \[0.8, 0.2, 0.0\], satisfying the properness condition. Note that log-loss can be dominated by cases where the true class is predicted with low probability: in the extreme case of a single instance with zero probability for the true class the loss is infinite.

### 3.1 Decompositions of proper scoring rules

When proposing the forecast evaluation that would later be known as Brier score, Brier mentioned that it could not be “gamed”, i.e. in order to obtain low scores, the forecaster has to produce honest, useful and correct predictions. Later research focused on why this was true for Brier score and other proper scoring rules.

Sanders ( [1963](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR69 "Sanders, F. (1963). On subjective probability forecasting. Journal of Applied Meteorology, 2(2), 191–201.")) showed that Brier score corresponds to the sum of two aspects of probability evaluation: validity and sharpness, terms introduced by Miller ( [1962](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR54 "Miller, R. G. (1962). Statistical Prediction by Discriminant Analysis (pp. 1–54). Boston, MA: American Meteorological Society.")) and Bross ( [1954](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR8 "Bross, I. (1954). Design for decision. Science Education, 38(4), 325.")), respectively. Validity, later known as reliability (Murphy & Winkler, [1977](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR56 "Murphy, A. H., & Winkler, R. L. (1977). Reliability of subjective probability forecasts of precipitation and temperature. Journal of the Royal Statistical Society Series C (Applied Statistics), 26(1), 41–47.")), is now often called _calibration loss_ (Kull & Flach, [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR39 "Kull, M., & Flach, P. (2015). Novel decompositions of proper scoring rules for classification: Score adjustment as precursor to calibration. In Joint European Conference on Machine Learning and Knowledge Discovery in Databases, (pp. 68–85). Springer.")). It refers to the fit between the forecasts and the frequency of occurrence of the event, which means that it is a joint property of the predictions and the events. Sharpness, which is now commonly called _refinement loss_ and was also known as resolution (Murphy & Winkler, [1977](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR56 "Murphy, A. H., & Winkler, R. L. (1977). Reliability of subjective probability forecasts of precipitation and temperature. Journal of the Royal Statistical Society Series C (Applied Statistics), 26(1), 41–47.")), is the loss due to predicting the same probability for instances from different classes. DeGroot and Fienberg ( [1983](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR12 "DeGroot, M. H., & Fienberg, S. E. (1983). The comparison and evaluation of forecasters. Journal of the Royal Statistical Society Series D (The Statistician), 32(1/2), 12–22.")) showed that these two terms make up proper scoring rules in general, and that probabilistic predictions should minimise refinement loss subject to calibration.

We now formally introduce such proper scoring rule decompositions. Let {\\textbf{X}} and \\dot{\\textbf{Y}}=\[Y\_1,\\ldots ,Y\_K\] be multivariate random variables, respectively corresponding to the features and the class of a randomly picked instance, where Y\_j=1 if the instance is of class _j_, otherwise Y\_j= 0, for j=1,2,\\ldots ,k. Given a scoring classifier, class probability estimator or probability forecaster {\\textsf{f}}, we denote by {\\textbf{S}}=\[S\_1,S\_2,...,S\_k\]={\\textsf{f}}({\\textbf{X}}) the vector output of {\\textsf{f}} for random feature {\\textbf{X}}, where {\\textbf{S}} is a random vector due to its dependence on {\\textbf{X}}. The expected value of proper scoring rule \\phi with respect to {\\textbf{S}} and \\dot{\\textbf{Y}} is then {\\textsf{E}} \\Big \[ \\phi \\big ({\\textbf{S}}, \\dot{\\textbf{Y}}\\big ) \\Big \].

**Table 2 Example dataset with three classes and three features. Column Q^{(i)} shows class posteriors given by the optimal model with Q\_1 = 0.25X\_1, Q\_2 = 0.25X\_2 and Q\_3 = 1 - (Q\_1 + Q\_2). Column S^{(i)} corresponds to estimated class posteriors S=f(X), which are given by S\_1 = 0.3X\_3, S\_2 = 0.1X\_2 and S\_3 = 1 - (S\_1 + S\_2). Finally, column _C_ represents calibrated probabilities**

[Full size table](https://link.springer.com/article/10.1007/s10994-023-06336-7/tables/2)

Consider a classification test set of 10 instances belonging to three classes (K=3) and described by 3 features, as shown in column {\\textbf{X}}^{(i)} of Table [2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab2). Suppose instances 1, 2, 3 and 5 belong to class 1, i.e. Y\_1=1, instances 4, 6, 7, 8 belong to class 2 and the rest belong to class 3. Note that in this example, the optimal class posteriors {\\textbf{Q}}^{(i)} are given, however this is not generally the case. Additionally, the sample is representative by design, with average {\\textbf{Y}}^{(i)}, among instances with the same feature values, exactly agreeing with {\\textbf{Q}}^{(i)}. Given columns {\\textbf{S}}^{(i)} and {\\textbf{Y}}^{(i)} from Table [2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab2), and using Equations ( [1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Equ1)) and ( [2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Equ2)), by averaging over the 10 instances, we get a mean Brier score of 0.71 and mean log-loss of 1.12.

Now let {\\textbf{C}}=\[C\_1,C\_2,\\ldots ,C\_K\] be yet another random vector, where C\_j={\\textsf{E}}\[Y\_j\| {\\textbf{S}}\], i.e. C\_j represents the actual proportion of class _j_ given all instances which received the same estimate {\\textbf{S}} from model {\\textsf{f}}. The decomposition of proper scoring rule \\phi into calibration loss and refinement loss is then the sum of expected loss between {\\textbf{S}} and {\\textbf{C}} and expected loss between {\\textbf{C}} and {\\textbf{Y}} (Bröcker & Smith, [2007](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR7 "Bröcker, J., & Smith, L. A. (2007). Increasing the reliability of reliability diagrams. Weather and Forecasting, 22(3), 651–661."); Kull & Flach, [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR39 "Kull, M., & Flach, P. (2015). Novel decompositions of proper scoring rules for classification: Score adjustment as precursor to calibration. In Joint European Conference on Machine Learning and Knowledge Discovery in Databases, (pp. 68–85). Springer.")):

\\begin{aligned} {\\textsf{E}} \\Big \[ {\\textsf{d}}\\big ({\\textbf{S}}, \\dot{\\textbf{Y}}\\big ) \\Big \] = {\\textsf{E}} \\Big \[ {\\textsf{d}}\\big ({\\textbf{S}}, {\\textbf{C}}\\big )\\Big \] + {\\textsf{E}} \\Big \[ {\\textsf{d}}\\big ({\\textbf{C}}, \\dot{\\textbf{Y}}\\big ) \\Big \], \\end{aligned}

where {\\textsf{d}}: {\\mathbb {P}}\_{{\\mathbb {Y}}} \\times {\\mathbb {P}}\_{{\\mathbb {Y}}} \\rightarrow {\\mathbb {R}} is the divergence associated to proper scoring rule \\phi. For log-loss and Brier score, {\\textsf{d}} has been shown to correspond to the Kullback-Leibler divergence and the mean squared difference, respectively (Kull & Flach, [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR39 "Kull, M., & Flach, P. (2015). Novel decompositions of proper scoring rules for classification: Score adjustment as precursor to calibration. In Joint European Conference on Machine Learning and Knowledge Discovery in Databases, (pp. 68–85). Springer.")).

The definition above is given based on expected population loss. In practice, we would be calculating these quantities on test data, as we generally do not have access to the whole population. Thus, we actually calculate an empirical loss. But assuming that test data is representative of the whole population and that there is a uniform distribution over the test instances and zero probability elsewhere, empirical loss can be interpreted as a special case of expected loss and all decompositions derived for expected loss also apply to empirical loss (Kull & Flach, [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR39 "Kull, M., & Flach, P. (2015). Novel decompositions of proper scoring rules for classification: Score adjustment as precursor to calibration. In Joint European Conference on Machine Learning and Knowledge Discovery in Databases, (pp. 68–85). Springer.")).

In our example in Table [2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab2), the first four instances share the same model scores {\\textbf{S}}=\[0.9,0.1,0.0\], with the first three instances belonging to class 1 and the fourth to class 2. Thus, for these instances, {\\textbf{C}}=\[0.75,0.25,0.0\]. The other six instances also share a score vector, with 1 instance from class 1, three from class 2 and 2 instances from class 3. As a result, they share the same calibrated probabilities {\\textbf{C}}=\[1/6, 3/6, 2/6\]. Given these values and considering Brier score, calibration loss is 0.19 and refinement loss is 0.52, which sum up to the Brier score of 0.71, as expected. For log-loss the decomposition is 1.12 = 0.29 + 0.83.

It is easy to see that a function that maps {\\textbf{S}} to {\\textbf{C}}, known as a calibrator in Sect. [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec13), could potentially reduce calibration loss to 0, consequently decreasing proper scoring rule loss. Refinement loss, on the other hand, is only zero if there are no ties between instances of different classes, i.e. they do not share the same value for {\\textbf{S}}. If that is the case, it is possible to map {\\textbf{S}} to {\\textbf{C}} such that it is perfectly confident and correct, i.e. C\_j = Y\_j.

Now suppose we knew the optimal model that outputs the true posterior class probabilities {\\textbf{Q}}=\[Q\_1,Q\_2,\\ldots ,Q\_K\], where Q\_j={\\textsf{E}}\[Y\_j\|{\\textbf{X}}\], i.e. Q\_j is the true proportion of class _j_ among instances with feature values {\\textbf{X}}. Then the expected loss according to proper scoring rule \\phi can be decomposed into the sum of expected divergences between {\\textbf{S}} and {\\textbf{Q}} and {\\textbf{Q}} and {\\textbf{Y}}:

\\begin{aligned} {\\textsf{E}} \\Big \[ {\\textsf{d}}\\big ({\\textbf{S}}, \\dot{\\textbf{Y}}\\big ) \\Big \] = {\\textsf{E}} \\Big \[ {\\textsf{d}}\\big ({\\textbf{S}}, {\\textbf{Q}}\\big )\\Big \] + {\\textsf{E}} \\Big \[ {\\textsf{d}}\\big ({\\textbf{Q}}, \\dot{\\textbf{Y}}\\big ) \\Big \], \\end{aligned}

The first term in the sum is called epistemic loss (Senge et al., [2014](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR71 "Senge, R., Bösner, S., Dembczyński, K., Haasenritter, J., Hirsch, O., Donner-Banzhoff, N., & Hüllermeier, E. (2014). Reliable classification: Learning classifiers that distinguish aleatoric and epistemic uncertainty. Information Sciences, 255, 16–29.")) and is the loss due to our model {\\textsf{f}}({\\textbf{X}}) not being optimal. The second term is called irreducible or aleatoric loss (Senge et al., [2014](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR71 "Senge, R., Bösner, S., Dembczyński, K., Haasenritter, J., Hirsch, O., Donner-Banzhoff, N., & Hüllermeier, E. (2014). Reliable classification: Learning classifiers that distinguish aleatoric and epistemic uncertainty. Information Sciences, 255, 16–29.")) and is the loss of the optimal model. Going back to the example in Table [2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab2), for Brier score, epistemic loss is 0.26 and irreducible loss is 0.45. For log-loss the decomposition is 1.12 = 0.48 + 0.64. The irreducible loss is only zero if the attributes of every instance {\\textbf{X}} carry enough information to uniquely define the label \\dot{\\textbf{Y}}. It is thus not possible to come up with a procedure to reduce the overall loss based on it. Additionally it would be unrealistic to do so based on epistemic loss. We are then naturally drawn to calibration loss as it is simple to interpret (we want our predicted probabilities of occurrence of an event to match the actual frequencies of occurrence) and also because we can easily estimate it with enough data. Thus, as discussed in the following section, visualisation and estimation of miscalibration have received considerable attention in the literature of probability evaluation and machine learning.

## 4 Evaluation and visualisation of classifier calibration

In this section we present a range of approaches to evaluate and visualise calibration, and discuss the advantages and disadvantages of each. In Sect. [4.1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec9) we explore the first steps towards measuring miscalibration, starting from the early work on weather forecast calibration, and discuss various approaches to visually inspect miscalibration. Some of those early approaches have been later adapted and proposed as new calibration metrics which are discussed in the following sections. We start with binary calibration in Sect. [4.2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec10) which will serve as a building block for the two multiclass calibration measures discussed in Sects. [4.3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec11) and [4.4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec12).

### 4.1 Visualising calibration

Several visualisation techniques have been proposed for easier inspection of the reliability of predictions at different score ranges. In this section we summarise a range of approaches that have been proposed in the literature, from simple tabular inspection to the more recent reliability diagrams (see Bröcker and Smith ( [2007](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR7 "Bröcker, J., & Smith, L. A. (2007). Increasing the reliability of reliability diagrams. Weather and Forecasting, 22(3), 651–661.")) for an extended discussion of reliability diagrams).

Starting from the binary case, the basic idea has been to show the relation between a particular predicted score {\\hat{s}} \\in \[0, 1\] for the positive class of a probabilistic classifier and the respective observed proportion of positives, which we denote by \\bar{\\textsf{y}}({\\hat{s}}). In order to compute a observed proportion of positives we require multiple samples with the same score {\\hat{s}}. However, given that the scores are continuous variables, the probability of getting multiple samples with the same score is almost zero. For that reason, the score space is commonly discretised into _M_ bins \\{{\\mathbb {B}}\_1, \\dots , {\\mathbb {B}}\_M\\}, thus increasing the probability of having multiple samples per estimation range (perhaps by forcing each bin to have a minimum number of samples). Then, we can obtain _M_ observed proportions of positives \\bar{\\textsf{y}}({\\mathbb {B}}\_m) instead of one per score value {\\hat{s}}. See Table [1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab1) for an early use of observed proportions of positives using equal-width bins of predicted probabilities.

**Fig. 5**

![Fig. 5](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig5_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/5)

Different graphical representations of calibration-related information found in the literature

Later work showed line plots instead of tabular data, with markers at the centre of each bin (Sanders, [1963](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR69 "Sanders, F. (1963). On subjective probability forecasting. Journal of Applied Meteorology, 2(2), 191–201."); Lichtenstein et al., [1977](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR47 "Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1977). Calibration of probabilities: The state of the art. In Decision Making and Change in Human Affairs, (pp. 275–324). Springer."), [1982](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR48 "Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1982). Calibration of Probabilities: The state of the art to 1980 (pp. 306–334). Cambridge: Cambridge University Press."); Murphy & Winkler, [1977](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR56 "Murphy, A. H., & Winkler, R. L. (1977). Reliability of subjective probability forecasts of precipitation and temperature. Journal of the Royal Statistical Society Series C (Applied Statistics), 26(1), 41–47.")); occasionally including the number of samples in each bin next to the markers (See Fig. [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig5) a). Other authors showed the markers with size relative to the sample size (Hagedorn et al., [2005](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR25 "Hagedorn, R., Doblas-Reyes, F. J., & Palmer, T. N. (2005). The rationale behind the success of multi-model ensembles in seasonal forecasting - I. Basic concept. Tellus A: Dynamic Meteorology and Oceanography, 57(3), 219–233.")), or as a separate histogram next to the reliability diagram (Niculescu-Mizil & Caruana, [2005](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR59 "Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In 22nd International Conference on Machine Learning (ICML’05), (pp. 625–632), New York, New York, USA. ACM Press.")). Line plots facilitate visual inspection of the discrepancy of the observed proportions of positives against a perfectly calibrated model, which corresponds to the diagonal. However, positioning the markers at the centre of the bins can be misleading, as even perfectly calibrated scores may result in a _visually_ non-calibrated reliability diagram with a deviation of up to half the bin width from the diagonal (Bröcker & Smith, [2007](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR7 "Bröcker, J., & Smith, L. A. (2007). Increasing the reliability of reliability diagrams. Weather and Forecasting, 22(3), 651–661.")) (See Fig. [6](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig6) for an example). This may happen in cases in which the scores are not evenly distributed in each bin.

**Fig. 6**

![Fig. 6](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig6_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/6)

Simple example showing the maximum discrepancy in calibration error when using the centre of the bin for the marker instead of the average score of the bin. Both examples show only two bins \[0, 0.5) and \[0.5, 1\]. **a** shows a model not calibrated, but using the centre of the bin (green dashed line) visually seems calibrated. The gap between the centre of the bin and the average score is maximum, which corresponds to half of the bin size with respect to the average score (red line). **b** shows a calibrated model which seems uncalibrated if using the centre of the bin. The gap is again half of the bin size\
\
In order to alleviate this problem, later work centred the markers on the average predicted scores \\bar{\\textsf{s}}({\\mathbb {B}}\_m) in each bin instead.\
\
There are two main methods to group the predicted scores into bins to build reliability diagrams. The first one, commonly called _width binning_, distributes scores into a number of bins of the same width, choosing bin edges accordingly (e.g., 10 bins \[0, 0.1\], (0.1, 0.2\], \\ldots , (0.9, 1.0\]). Another method, called _frequency binning_ (also equal size or equal mass binning) groups the scores by keeping the same number of samples in each bin. Frequency binning can and will normally result in bins with different widths, but it ensures that all bins have the same “weight” when assessing the model’s miscalibration.

Bin estimations have varying reliability, e.g., depending on the number of samples in the bin. One way to show this visually is by incorporating confidence intervals. One of the simplest methods is to assume that each bin is sampled from a binomial distribution, and compute the corresponding confidence intervals of the observed proportion of positives (see Fig. [7](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig7) b). However, making the assumption of fixed bins, score averages and proportion of positives is unrealistic; unless the score distribution is uniform (see Bröcker and Smith ( [2007](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR7 "Bröcker, J., & Smith, L. A. (2007). Increasing the reliability of reliability diagrams. Weather and Forecasting, 22(3), 651–661.")) for a detailed discussion). More accurate intervals can be obtained by using the _consistency resampling_ method proposed by Bröcker and Smith ( [2007](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR7 "Bröcker, J., & Smith, L. A. (2007). Increasing the reliability of reliability diagrams. Weather and Forecasting, 22(3), 651–661.")), which consists on sampling the scores with replacement several times in order to obtain multiple surrogate forecasts and observations and their respective quantiles.

More recently, binary reliability diagrams have been extended to the multiclass setting. One method to show multiclass scores in a binary fashion consists in plotting only the _confidence_ of the model for each sample (the highest score among all possible classes). This approach was already used for binary classification by Lichtenstein et al. ( [1977](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR47 "Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1977). Calibration of probabilities: The state of the art. In Decision Making and Change in Human Affairs, (pp. 275–324). Springer.")), reproduced here as Fig. [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig5) b. The figure shows a binary reliability diagram with scores in the range \[0.5, 1\] (with _K_ classes the confidence is never lower than 1/ _K_). Another example of the use of confidences in multiclass problems is the recent work of Guo et al. ( [2017](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR24 "Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In 34th International Conference on Machine Learning, (pp. 1321–1330), Sydney, Australia. PMLR.")), which shows the confidence for multiclass problems in the form of bar plots and the ECE and MCE metrics discussed below. Finally, instead of collapsing all classes into a single diagram one could construct one reliability diagram per class as line plots or bars in a one-vs-rest manner (Kull et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR40 "Kull, M., Perello-Nieto, M., Kängsepp, M., Filho, T. S., Song, H., & Flach, P. (2019). Beyond temperature scaling: Obtaining well-calibrated multiclass probabilities with Dirichlet calibration. Advances in Neural Information Processing Systems (NeurIPS’19), 32, 12316–12326.")) (see Fig. [7](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig7) c).

**Fig. 7**

![Fig. 7](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig7_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/7)

Examples of reliability diagrams using the Python library PyCalib

**Table 3 Class probabilities given by a classifier to 30 instances belonging to three different classes**

[Full size table](https://link.springer.com/article/10.1007/s10994-023-06336-7/tables/3)

### 4.2 Evaluating calibration error: the binary case

We now proceed with discussing how to measure calibration error. We will use the three-class toy problem in Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3) throughout. In this section we convert it to a binary classification problem by taking class 1 as positive and classes 2 and 3 as negative. We then apply equal-width binning to the class 1 probabilities. Table [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab4) shows the resulting bins {\\mathbb {B}}\_m, m \\in \\{1, \\ldots , 5\\}, from which we calculate the number of instances in the bin denoted as \|{\\mathbb {B}}\_{m}\|, the average probability \\bar{{\\textsf{s}}}({\\mathbb {B}}\_{m}), the proportion of positives \\bar{{\\textsf{y}}}({\\mathbb {B}}\_{m}), and the absolute gap between them \|\\bar{{\\textsf{y}}}({\\mathbb {B}}\_m) - \\bar{{\\textsf{s}}}({\\mathbb {B}}\_m)\|.

**Table 4 Positive probabilities and corresponding instance labels separated into 5 bins. The probabilities were obtained by taking class 1 as the positive class in the multiclass problem in Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3). To reduce the width of the table, a number followed by a superscript parenthesis X^{(Y)} indicates a list of number _X_ repeated _Y_ times**

[Full size table](https://link.springer.com/article/10.1007/s10994-023-06336-7/tables/4)

The values of \\bar{{\\textsf{p}}}({\\mathbb {B}}\_{m}), \\bar{{\\textsf{y}}}({\\mathbb {B}}\_{m}) and \|\\bar{{\\textsf{y}}}({\\mathbb {B}}\_m) - \\bar{{\\textsf{s}}}({\\mathbb {B}}\_m)\| in Table [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab4) can be used to draw the reliability diagram shown in Fig. [8](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig8), where we can see the red bars representing the calibration error at each bin.

**Fig. 8**

![Fig. 8](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig8_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/8)

Reliability diagram corresponding to the 5 bins presented in Table [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab4)

Given the information about the bins in Table [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab4) we could calculate an average of the bin-wise calibration error, which leads us to binary estimated calibration error, as defined in Definition [1](https://link.springer.com/article/10.1007/s10994-023-06336-7#FPar1).

### Definition 1

( _Binary-ECE_) Binary _estimated calibration error_ (Roelofs et al., [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR66 "Roelofs, R., Cain, N., Shlens, J., & Mozer, M. C. (2021). Mitigating bias in calibration error estimation. arXiv preprint                   arXiv:2012.08668                                    .")), or binary-ECE (Naeini et al., [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR58 "Naeini, P., Cooper, G. F., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using bayesian binning. In 29th AAAI Conference on Artificial Intelligence, vol. 29.")), is the average gap across all bins in a reliability diagram, weighted by the number of instances in each bin:

\\begin{aligned} \\textsf{ECE}\_{\\text {binary}} = \\sum \_{m=1}^M \\frac{\|{\\mathbb {B}}\_{m}\|}{N} \|\\bar{{\\textsf{y}}}({\\mathbb {B}}\_{m}) - \\bar{{\\textsf{s}}}({\\mathbb {B}}\_{m})\|, \\end{aligned}

where _M_ and _N_ are the number of bins and instances, respectively. Binary-ECE is also commonly called binary _expected calibration error_, however this quantity is empirically estimated on a validation or test sample, which is why we prefer to call it binary _estimated calibration error_.

Binary-ECE aggregates part of the visual information about calibration error in Fig. [8](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig8) by taking the weighted mean of the sizes of these gaps. In this example, \\textsf{ECE}\_{\\text {binary}} =0.1873.

Binary-ECE ranges from 0 to 1, with particular values including \\textsf{ECE}\_{\\text {binary}} =\\pi \_1 (proportion of positives) for a classifier that randomly outputs probability 1 for one of the classes, \\textsf{ECE}\_{\\text {binary}} =0 for a perfect classifier that always predicts probability 1 for the correct class or for a classifier that constantly outputs positive probability equal to \\pi \_1, and \\textsf{ECE}\_{\\text {binary}} =1 for a classifier that always assigns probability 1 to the wrong class.

Instead of measuring how miscalibrated the model is on average, one might be interested in the worst case, in other words “how maximally miscalibrated is the model”? In this case, one might use the binary maximum calibration error (Naeini et al., [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR58 "Naeini, P., Cooper, G. F., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using bayesian binning. In 29th AAAI Conference on Artificial Intelligence, vol. 29.")).

### Definition 2

( _Binary-MCE_) Binary maximum calibration error (binary-MCE) is the maximum gap across all bins in a reliability diagram:

\\begin{aligned} \\textsf{MCE}\_{\\text {binary}} = \\max \_{m \\in \\{1, \\ldots , M\\}} \|\\bar{{\\textsf{y}}}({\\mathbb {B}}\_m) - \\bar{{\\textsf{s}}}({\\mathbb {B}}\_m)\|. \\end{aligned}

In our example, Table [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab4) and Fig. [8](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig8) show that the fourth bin has the largest gap, with its size corresponding to \\textsf{MCE}\_{\\text {binary}} = 0.48.

Binary-MCE can be very sensitive to bins with few instances, where the values of \\bar{{\\textsf{y}}}({\\mathbb {B}}\_m) and \\bar{{\\textsf{s}}}({\\mathbb {B}}\_m) are calculated based on very little information. In extreme cases with only a single instance in a bin, \\bar{{\\textsf{y}}}({\\mathbb {B}}\_m) will be the instance’s actual label (1 or 0), potentially resulting in a large gap that would have a small weight in binary-ECE, while being the whole value of binary-MCE, meaning that the model would be evaluated based on its performance for a single instance.

### 4.3 Classwise calibration error

We now proceed to settings with more than two classes and start by defining the estimated calibration error corresponding to a single class _j_ in a multiclass task.

### Definition 3

( _Class_- _j_- _ECE_) Given a multiclass task with _K_ classes, class- _j_-ECE corresponds to the binary-ECE calculated by taking class _j_ as positive and the other K-1 classes together as a new negative class:

\\begin{aligned} \\textsf{ECE}\_{j} = \\sum \_{m=1}^M \\frac{\|{\\mathbb {B}}\_{m,j}\|}{N} \|\\bar{{\\textsf{y}}}\_j({\\mathbb {B}}\_{m,j}) - \\bar{{\\textsf{s}}}\_j({\\mathbb {B}}\_{m,j})\|, \\end{aligned}

where {\\mathbb {B}}\_{m,j} is the _m_-th bin of class _j_.

Once again we turn to our example in Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3). Following Definition [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#FPar3), we have already calculated class-1-ECE (0.1873) in our binary-ECE example. Now we need to calculate class-2-ECE and class-3-ECE. Tables [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab5) and [6](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab6) show the binary bins for classes 2 and 3, respectively, while the binary reliability diagrams of the three classes can be seen in Fig. [9](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig9).

**Table 5 Positive probabilities and corresponding instance labels separated into 5 bins. The probabilities were obtained by taking class 2 as the positive class in the multiclass problem in Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3)**

[Full size table](https://link.springer.com/article/10.1007/s10994-023-06336-7/tables/5)

**Table 6 Positive probabilities and corresponding instance labels separated into 5 bins. The probabilities were obtained by taking class 3 as the positive class in the multiclass problem in Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3)**

[Full size table](https://link.springer.com/article/10.1007/s10994-023-06336-7/tables/6)

**Fig. 9**

![Fig. 9](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig9_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/9)

Binary reliability diagram of each class in our running example. Note the empty bins in the second and third reliability diagrams, showing that the classifier never outputs high probabilities for these classes

From the values in Tables [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab5) and [6](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab6) and following Definition [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#FPar3), we get \\text {class-2-ECE} = 0.147 and \\text {class-3-ECE} = 0.2017.

We can now define classwise-ECE (Kull et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR40 "Kull, M., Perello-Nieto, M., Kängsepp, M., Filho, T. S., Song, H., & Flach, P. (2019). Beyond temperature scaling: Obtaining well-calibrated multiclass probabilities with Dirichlet calibration. Advances in Neural Information Processing Systems (NeurIPS’19), 32, 12316–12326.")).

### Definition 4

( _Classwise-ECE_) The estimated classwise calibration error (classwise-ECE) is the average class- _j_-ECE across all classes:

\\begin{aligned} \\textsf{ECE}\_{\\text {classwise}} = \\frac{1}{K}\\sum \_{j=1}^K \\textsf{ECE}\_{j}. \\end{aligned}

According to Definition [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#FPar4), in our example \\text {classwise-ECE} = (0.1873 + 0.147 + 0.2017)/3 = 0.1787.

### Definition 5

( _Classwise-MCE_) The maximum classwise calibration error (classwise-MCE) (Kull et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR40 "Kull, M., Perello-Nieto, M., Kängsepp, M., Filho, T. S., Song, H., & Flach, P. (2019). Beyond temperature scaling: Obtaining well-calibrated multiclass probabilities with Dirichlet calibration. Advances in Neural Information Processing Systems (NeurIPS’19), 32, 12316–12326.")) is defined as the maximum gap across all bins and all classwise-reliability diagrams:

\\begin{aligned} \\textsf{MCE}\_{\\text {classwise}} = \\max \_{j \\in \\{1, \\ldots , K\\}\\, m \\in \\{1, \\ldots , M\\}} \|\\bar{{\\textsf{y}}}\_j(B\_{m,j}) - \\bar{{\\textsf{s}}}\_j(B\_{m,j})\|. \\end{aligned}

In our running example, \\textsf{MCE}\_{\\text {classwise}} = 0.48.

Note that this is not the only way to define classwise-MCE. For example, one could be interested in the average maximum gap across classes, i.e. an average class- _j_-MCE, which in our example would be (0.48 + 0.24 + 0.3)/3 = 0.34. As another variation, one could take the maximum class- _j_-ECE, which would then indicate the most miscalibrated class on average. In our example, this variation corresponds to class-3-ECE (0.2017).

Although classwise-ECE and MCE measure calibration error over all classes, they do not take into account the miscalibration that arises from every possible relationship between classes. For a true multiclass-ECE, we could bin the probability vectors in simplex space and then calculate the gaps between the average probability vector and the vector of class proportions in each bin. Although this seems like the right thing to do when evaluating multiclass calibration, it might not be efficiently computable with large numbers of classes, as the number of bins can be prohibitively high and most bins would likely be empty.

Similarly to binary-ECE, a value of \\text {classwise-ECE} = 0 can be obtained by a classifier that constantly outputs the class proportions. For example, if a classifier always predicts 1/3 setosa, 1/3 versicolor and 1/3 virginica for Fisher’s Iris dataset, the resulting classwise-ECE will be 0.

### 4.4 Confidence calibration error

As already mentioned, some calibration measures only consider a model’s confidence, defined as the maximum value in the predicted probability vector, i.e. the probability given to the winning class. Prediction confidence is not a new idea and has been around since at least the 1970s. Lichtenstein et al. ( [1977](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR47 "Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1977). Calibration of probabilities: The state of the art. In Decision Making and Change in Human Affairs, (pp. 275–324). Springer.")) called it the half-range method in the binary case (referred to as “two alternatives” in the paper) and it was also mentioned as one of the variations of the multiclass task, which the authors called “three or more alternatives”. More recently it has been popularised by Guo et al. ( [2017](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR24 "Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In 34th International Conference on Machine Learning, (pp. 1321–1330), Sydney, Australia. PMLR.")).

To calculate confidence-ECE, we first bin the confidence values and, for each instance of each bin, we produce a binary value indicating if the classifier predicted correctly or not. Recalling the example from Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3), the resulting confidence bins are presented in Table [7](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab7), where \\bar{{\\textsf{p}}}({\\mathbb {B}}\_{m}) and \\textsf{acc}({\\mathbb {B}}\_{m}) are respectively the average confidence and prediction accuracy in bin {\\mathbb {B}}\_{m}, with the corresponding reliability diagram in Fig. [10](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig10). Note that bin {\\mathbb {B}}\_1 is empty, which demonstrates that confidence-ECE and confidence reliability diagrams are different from binary-ECE even on two-class problems.

**Table 7 Confidence bins corresponding to the toy example from Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3). The binary values in the fifth column indicate if the classifier correctly classified each instance**

[Full size table](https://link.springer.com/article/10.1007/s10994-023-06336-7/tables/7)

**Fig. 10**

![Fig. 10](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig10_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/10)

Confidence reliability diagram corresponding to the bins in Table [7](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab7)

### Definition 6

( _Confidence-ECE_) Confidence-ECE is the average difference between accuracy and average confidence across all bins in a confidence reliability diagram, weighted by the number of instances in each bin:

\\begin{aligned} \\textsf{ECE}\_{\\text {confidence}} = \\sum \_{m=1}^M \\frac{\|{\\mathbb {B}}\_{m}\|}{N} \|\\textsf{acc}({\\mathbb {B}}\_{m}) - \\bar{{\\textsf{p}}}({\\mathbb {B}}\_{m})\|. \\end{aligned}

We then calculate confidence-ECE as the weighted mean of the gaps between average confidence and prediction accuracy at each bin, thus \\textsf{ECE}\_{\\text {confidence}}=0.2117, while the maximum confidence calibration error (confidence-MCE) corresponds to the largest gap, i.e. \\textsf{MCE}\_{\\text {confidence}}=0.3. As with binary-ECE and for the same reasons, confidence-MCE is very sensitive to small bins, but in this particular example, its value corresponds to the gap of the largest bin.

As we show in Sect. [5](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec13), there is a wide range of post-hoc calibration techniques in the literature, each one capable of handling different miscalibration patterns. Thus, it can be useful to first analyse a model’s reliability diagram, as it allows us to diagnose model miscalibration, i.e. in what probability ranges it is underconfident or overconfident, and this can help choose an appropriate calibration method. In addition, any of the ECE measures discussed in this Section can be used to decide if a classifier actually needs to be calibrated, by testing the hypothesis that the model is already calibrated, as shown in Sect. [6](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec30). Finally, it is important to consider that all ECE/MCE measures can provide very different values given different number of bins, as shown in Figs. [1](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig1) and [2](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig2), and they can be minimised by predicting the overall class distribution, regardless of the given instance. Thus, it is good practice to use them together with the proper scoring rules presented in Sect. [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec6), to get a full evaluation of the probabilities produced by a model.

## 5 Calibration methods

In this section we provide a systematic review of standard approaches to calibrating classifiers through the construction of calibration maps. In particular, we focus on post-hoc calibration methods for classification, which can be used to adjust probability outputs separately from the initial training process. For each method, we cover the mathematical formulation, the objective function for learning the map, and the predictive function to calculate the class probabilities for a new instance. We include a few test cases to empirically analyse each method, and discuss their advantages and disadvantages. General guidance on each method’s implementation is also discussed, addressing issues such as overfitting and computational effort. At the end of the section, we briefly describe some related work to classifier calibration, such as methods that can improve the calibration level during training time, methods that are designed for getting well-calibrated probability for other predictive tasks, and approaches that are designed for specific tasks in areas such as computer vision and natural language processing.

### 5.1 Preliminaries

We denote a calibration map as a function {\\textsf{g}}: {\\mathbb {S}}\_{{\\mathbb {Y}}} \\rightarrow {\\mathbb {P}}\_{{\\mathbb {Y}}}. Here {\\mathbb {Y}} =\\{1, \\dots , K\\} is the discrete space with _K_ classes of the target variable. {\\mathbb {P}}\_{{\\mathbb {Y}}} denotes the probability vector space on {\\mathbb {Y}}, that is: {\\mathbb {P}}\_{{\\mathbb {Y}}} = \\{ \[s\_1, \\dots , s\_K\] \\mid s\_j \\ge 0, \\sum \_{j=1}^{K} s\_j = 1\\}. {\\mathbb {S}}\_{{\\mathbb {Y}}} represents the original output space of the (uncalibrated) classifier, which can take various forms depending on the formalisation of the classifier. For instance, for a typical probabilistic classifier, we have {\\mathbb {S}}\_{{\\mathbb {Y}}} = {\\mathbb {P}}\_{{\\mathbb {Y}}}. A one-vs-rest SVM might produce _K_-dimensional vectors in {\\mathbb {S}}\_{{\\mathbb {Y}}} = {\\mathbb {R}}^{K}. Deep neural networks can also provide unnormalised vector outputs before the softmax is performed at the final layer. Calibration maps that work with such vector spaces are referred to as scaling approaches. The name suggests these approaches are used to scale the vector output into a probability output, which is quite useful for models like SVMs, as the hinge loss does not optimise probability estimates by default. However, other than the name and historical motivation, in modern applications, probability calibrators and scaling approaches can be used interchangeably, as the probability space and vector space can be transformed into each other by using the link function (e.g. softmax) and inverse link function (e.g. logit transform ).

In general, to obtain a calibration map, we will have a calibration set with uncalibrated probabilities and labels, denoted as {\\mathbb {C}} = \\{({\\textbf{s}}\_1, y\_1), \\dots , ({\\textbf{s}}\_N, y\_N)\\}, and an objective function {\\textsf{L}}({\\mathbb {C}}) to optimise. Typically, the objective function is constructed using proper scoring rules, that is, {\\textsf{L}}({\\mathbb {C}}) = \\sum \_{i=1}^{N} \\phi ({\\textbf{s}}\_i, y\_i), and it can be optimised via various gradient descent algorithms.

**Training Schemes**: While the above notation suggested that the calibration map can be obtained by fitting a calibrator on a given hold-out calibration set, in practice a small training set and calibration set might lead to over-fitting thus limiting the performance of the calibrated model. A typical solution here is to introduce multi-fold dataset splits as introduced in Platt ( [1999](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR64 "Platt, J. C. (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. Advances in large margin classifiers (pp. 61–74). Cambridge: MIT Press.")). The author proposes to divide the training sets into three different folds and fit the model and calibration map in cross-validation. Two folds are used to train the uncalibrated model, and the model predictions on the last fold are collected and used to fit the calibration map. This training process thus ends up with three pairs of models and calibration maps. At test time each instance will be predicted with all three pairs, and resulting probabilities are averaged to give the final estimate. Alternatively, people have also used applied label smoothing (Müller et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR55 "Müller, R., Kornblith, S., & Hinton, G. (2019). When does label smoothing help? arXiv preprint                   arXiv:1906.02629                                    .")) to reduce the level of overfitting and over-confidence. The idea is to have a weighted average between the original probability vector (either from the uncalibrated model or after a calibration method has been applied) and a uniform probability vector. Therefore, the final probability vector will be pushed somewhat towards the uniform probability vector, which avoids overly high confidence for unsuitable cases.

### 5.2 Two-class test cases

We designed some test cases to illustrate each calibration map’s characteristics empirically. These test cases are designed with a known distribution and allow us to directly sample the instances. For ease of understanding, we consider a scenario with a univariate feature ({\\textbf{x}} \\in {\\mathbb {R}}), so that we can inspect the fitted functions and reliability diagrams by means of _x_- _y_ plots.

Figure [11](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig11) depicts the probability density functions for the synthetic two-class dataset, as well as the posterior class probabilities when predicting any new instances. The generative model is equally likely to produce a positive and a negative, and the distribution of the feature values are mixtures of two normal distributions within each class. Denoting the mixture components as H=1 and H=2, our generative model can be formally written down as:

\\begin{aligned} Y&\\sim \\text {Bernoulli}(0.5) \\\ H&\\sim \\text {Bernoulli}(0.5) \\\ X \\mid Y=1, H=1&\\sim \\text {Gaussian}(-4, 960) \\\ X \\mid Y=1, H=2&\\sim \\text {Gaussian}(64, 1280) \\\ X \\mid Y=2, H=1&\\sim \\text {Gaussian}(4, 980) \\\ X \\mid Y=2, H=2&\\sim \\text {Gaussian}(-72, 1024) \\\ \\end{aligned}

**Fig. 11**

![Fig. 11](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig11_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/11)

The synthetic dataset used in the test cases. The left two figures shows the data distribution for each class respectively. The figure on the right gives the Bayes-optimal posterior probability for class 1

This generative assumption allows us to approximate the ‘true’ reliability diagram closely for every test case and provides better insights into each calibration map. Specifically, we generate a large number of random samples and use small bin sizes to approximate a smooth reliability diagram.

We consider three cases for binary classification, each of which may occur in practice. The first two cases are hypothetical over/under-confident scenarios using a logistic regression model of the form \\hat{{\\textsf{f}}}(x) = (1 + \\exp (-a\\cdot x))^{-1}. Such a model puts the decision boundary at x=0, which is nearly Bayes-optimal for the synthetic data. The model confidence can be moderated with the parameter _a_, and we will use the following two cases:

\\begin{aligned} \\hat{{\\textsf{f}}}\_{\\text {under}}(x)&= \\frac{1}{1 + \\exp (-0.01\\cdot x)} \\\ \\hat{{\\textsf{f}}}\_{\\text {over}}(x)&= \\frac{1}{1 + \\exp (-0.05\\cdot x)} \\end{aligned}

The third case is obtained with an MLP classifier as implemented by the scikit-learn Python package. The model is specified with a two layer structure with 128 hidden units per layer. The activation is selected as the ReLU function. The remaining settings are left at their default values. 10, 000 instances are sampled to train the model.

The smoothed reliability diagrams for these three cases are shown in Fig. [12](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig12). In the under-confident case the output probabilities barely reach the outside of the interval \[0.1, 0.9\]. The reliability diagram shows a higher slope compared with the perfectly calibrated one (the diagonal). In contrast, the over-confident case has a shallower slope around the middle compared with the diagonal. It further causes the reliability diagram to have sharp transitions while approaching the extremes. For the MLP case, we can observe both under-confident and over-confident regions throughout the reliability diagram. This specific MLP classifier tends to be under-confident around s \\in \[0, 0.1\] and s \\in \[0.65, 1\], and mostly over-confident elsewhere.

**Fig. 12**

![Fig. 12](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig12_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/12)

The reliability diagrams of the three uncalibrated classifiers. The left figure shows the \\hat{{\\textsf{f}}}\_{\\text {under}} case, where the classifier predicts a probability closer to 0.5 compared with the Bayes-optimal case (Fig. [11](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig11), right), resulting in a reliability diagram with steeper slope. The middle figure shows the \\hat{{\\textsf{f}}}\_{\\text {over}} case, where the predicted probabilities are pushed towards 0 and 1 respectively, resulting in a shallower reliability curve. The right figure is obtained with a MLP classifier (\\hat{{\\textsf{f}}}\_{\\text {MLP}}), where the reliability diagram shows over-confident and under-confident predictions around different regions

### 5.3 Calibration for binary classification

We start with methods that can learn calibration maps for binary problems. In binary classification, probability estimates are scalars, so the calibration maps are functions mapping from \[0, 1\] to \[0, 1\]. Here we describe four widely applied methods in detail: empirical binning, isotonic regression, logistic calibration and Beta calibration. Other approaches will be be briefly mentioned at the end of this section.

#### 5.3.1 Empirical binning

Empirical binning (Zadrozny & Elkan, [2001](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR86 "Zadrozny, B., & Elkan, C. (2001). Obtaining calibrated probability estimates from decision trees and naive bayesian classifiers. ICML, 1, 609–616."); Naeini et al., [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR58 "Naeini, P., Cooper, G. F., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using bayesian binning. In 29th AAAI Conference on Artificial Intelligence, vol. 29.")) is one of the simplest methods to build a calibration map. It directly connects to the previously introduced ECE measure, which evaluates the calibration level by calculating the empirical frequencies within a set of score intervals. Therefore, binning approaches can directly optimise a variant of ECE depending on how the binning scheme is selected.

**Fig. 13**

![Fig. 13](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig13_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/13)

Examples of empirical binning calibration with 10 equal-width bins. As the binning approach can only give discrete outputs, we can observe the probabilities after calibration are no longer continuous and are only presented with 10 values or less (the under-confidence case has fewer values as there are no observations in bins closer to the extremes. The reliability diagrams show that the calibration method works well with all three test case, with most points being close to the calibrated diagonal

For a typical setting, the empirical binning approach comes with the following parameters. (1) Bins: \\{{\\mathbb {B}}\_1, \\dots , {\\mathbb {B}}\_M \\}, where each bin {\\mathbb {B}}\_m \\subset \[0, 1\] is an interval of probability range, and \\cup \_{m=1}^{M} {\\mathbb {B}}\_m = \[0, 1\]. (2) Probability estimates in the bins: {\\textbf{a}}=\\{a\_1,\\dots ,a\_{M}\\}, where a\_m \\in \[0, 1\] specifies the calibrated probability value in each bin. We usually assume that these bins do not overlap with each other. To make a prediction based on an uncalibrated probability _s_, empirical binning uses the following functional form:

\\begin{aligned} {\\textsf{g}}(s; {\\mathbb {B}}\_1, \\dots , {\\mathbb {B}}\_M, {\\textbf{a}}) = a\_m \\quad \\quad \\quad \\text {if}\ s \\in {\\mathbb {B}}\_m \\end{aligned}

(3)


Here s \\in {\\mathbb {B}}\_m means that the uncalibrated probability _s_ falls within {\\mathbb {B}}\_m.

Fitting a binning calibration map can be done by optimising {\\textbf{a}} using ECE as a loss function:

\\begin{aligned} {\\textbf{a}}^\*&= \\arg \\min \_{{\\textbf{a}}} {\\textsf{L}}({\\textbf{a}}) \\end{aligned}

(4)


\\begin{aligned} {\\textsf{L}}({\\textbf{a}})&= \\textsf{ECE}({\\textbf{a}}) = \\sum \_{m=1}^{M} \\Big \| \\bar{{\\textsf{y}}}({\\mathbb {B}}\_m) - a\_m \\Big \| \\end{aligned}

(5)


Here \\bar{{\\textsf{y}}}({\\mathbb {B}}\_m) represents the empirical frequency within {\\mathbb {B}}\_m as defined in the previous section. The equation hence indicates that we want to assign each a\_m according to the empirical frequency of the labels within each bin {\\mathbb {B}}\_m.

We empirically analyse the binning approach with a simple setting of M=10 equal-width bins. The results with the three test cases are shown in Fig. [13](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig13). The binning approach performs well on most points, as the reliability diagram are close to the diagonal after calibration. However, it should be noted that the output probabilities can only take _M_ different values. Therefore, while the final probabilities are calibrated, we can no longer distinguish instances that receive different predictions from the uncalibrated model. In other words, binning approaches can reduce the calibration loss at the cost of a higher grouping loss (Kull & Flach, [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR39 "Kull, M., & Flach, P. (2015). Novel decompositions of proper scoring rules for classification: Score adjustment as precursor to calibration. In Joint European Conference on Machine Learning and Knowledge Discovery in Databases, (pp. 68–85). Springer.")).

While here we illustrated the binning approach with equal-width bins, it is possible to use other binning schemes such as equal-frequency binning. For example, (Naeini et al., [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR58 "Naeini, P., Cooper, G. F., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using bayesian binning. In 29th AAAI Conference on Artificial Intelligence, vol. 29.")) propose a Bayesian binning approach.

To summarise, the main advantages of binning approaches are as follows: (1) They can be used to directly minimise a specific variant of ECE, hence are useful when calibration loss is of primary concern. (2) Training is reasonably fast and straightforward. (3) Given its non-parametric nature, it does not have any constraint on the form of the calibration maps and therefore can capture arbitrary shapes according to the given bins. In addition, other binning strategies can also be applied to deal with different datasets and uncalibrated models.

#### 5.3.2 Isotonic calibration

Calibration by means of isotonic regression is another widely used non-parametric approach (Barlow & Brunk, [1972](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR4 "Barlow, R. E., & Brunk, H. D. (1972). The isotonic regression problem and its dual. Journal of the American Statistical Association, 67(337), 140–147."); Niculescu-Mizil & Caruana, [2005](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR59 "Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In 22nd International Conference on Machine Learning (ICML’05), (pp. 625–632), New York, New York, USA. ACM Press."); Naeini & Cooper, [2016](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR57 "Naeini, M. P., & Cooper, G. F. (2016). Binary Classifier Calibration Using An Ensemble Of Near Isotonic Regression Models. In IEEE 16th International Conference on Data Mining (ICDM) (pp. 360–369). Institute of Electrical and Electronics Engineers (IEEE): IEEE.")). The isotonic approach was originally proposed to solve univariate regression tasks where the function were required to be monotonic. In the case of probability calibration, if we assume the uncalibrated model has a monotonic reliability diagram, then isotonic regression is a suitable approach to achieve a better level of calibration.

Isotonic regression achieves a monotonic fit by estimating a set of non-decreasing constant segments, corresponding to a set of bins of varying width. Isotonic regression can therefore be described with the following parameters: (1) Bin boundaries: {\\textbf{b}}=(b\_1,\\dots ,b\_M), b\_j \\in \[0, 1\], b\_j < b\_{j+1}, and (2) Edge values: {\\textbf{v}}=(v\_1,\\dots ,v\_{M}), v\_j \\in \[0, 1\], v\_j \\le v\_{j+1}. As indicated by the parameters, isotonic regression is quite close to an empirical binning approach. The main difference is that instead of having a pre-defined set of bin edges, isotonic regression learns these bin boundaries from the data. As a result, isotonic regression can have an variable number of bins depending on the training set. To calibrate a probability _s_, isotonic regression uses the following predictive function:

\\begin{aligned} {\\textsf{g}}(s; {\\textbf{b}}, {\\textbf{v}}) = \\sum \_{m=1}^{M-1} {\\textsf{I}}(s\\ge b\_m)\\cdot {\\textsf{I}}(s<b\_{m+1}) \\cdot m\_j \\end{aligned}

(6)


**Fig. 14**

![Fig. 14](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig14_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/14)

Examples of isotonic calibration trained with 10,000 samples. Compared with empirical binning, we can see the isotonic approach can provide a larger variety of outputs in the continuous interval of \[0, 1\], and different bins can be automatically learnt according to the observations. The calibration method works reasonably well on all three test cases. The over-confidence case still has some errors around around the middle-left and middle-right boundaries, due to the lack of training points within these areas

The three test cases on istonic regression are shown in Fig. [14](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig14). To compare with the empirical binning approach again, while in the empirical case we have a constant prediction within each bin, we can see the prediction of the isotonic approach depends on the two values on the bin edges. In the case where the two bin edges do not share the same value, isotonic regression performs linear interpolation to calculate the predicted value. This behaviour is due to the way that the isotonic approach is estimated. To ensure the estimated function is monotonically increasing, the learning algorithm starts with the first bin edge as the minimal feature value (0 in the case of an isotonic calibration) and extends the following bin edges until it sees a higher target value (this is also referred to as ‘pooling adjacent violators’ (Fawcett & Niculescu-Mizil, [2007](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR16 "Fawcett, T., & Niculescu-Mizil, A. (2007). PAV and the ROC convex hull. Machine Learning, 68(1), 97–106."))). It can be proven that, with monotonic sets of {\\textbf{b}} and {\\textbf{s}}, the learning algorithm is equivalent to optimising the following loss (Ayer et al., [1955](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR3 "Ayer, M., Brunk, H. D., Ewing, G. M., Reid, W. T., & Silverman, E. (1955). An empirical distribution function for sampling with incomplete information. The Annals of Mathematical Statistics, 26, 641–647.")):

\\begin{aligned} {\\textsf{L}}({\\textbf{b}}, {\\textbf{v}}) = \\frac{1}{N} \\sum \_{i=1}^{N}\\Big ( {\\textsf{g}}(s\_i; {\\textbf{b}}, {\\textbf{v}}) - y\_i\\Big )^2 \\end{aligned}

(7)


Therefore, when used as a probability calibration map, isotonic regression minimises the Brier score on the training set. Instead of applying isotonic regression directly, (Naeini & Cooper, [2016](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR57 "Naeini, M. P., & Cooper, G. F. (2016). Binary Classifier Calibration Using An Ensemble Of Near Isotonic Regression Models. In IEEE 16th International Conference on Data Mining (ICDM) (pp. 360–369). Institute of Electrical and Electronics Engineers (IEEE): IEEE.")) also consider building an ensemble calibration map by combining a set of near-isotonic functions. Recently, (Allikivi & Kull, [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR1 "Allikivi, M.-L., & Kull, M. (2019). Non-parametric bayesian isotonic calibration: Fighting over-confidence in binary classification. In Joint European Conference on Machine Learning and Knowledge Discovery in Databases (ECML-PKDD’19), (pp. 68–85).")) propose a Bayesian approach to improve isotonic regression, with demonstrated improvements on binary tasks.

Isotonic regression is a compelling approach for probability calibration, with the following advantages: (1) When the monotonic assumption is suitable, isotonic regression can find the optimal bin edges for Brier score on the training sets, which is also known to give the convex hull in ROC analysis. (2) The non-parametric nature avoids catastrophic model misfit. On the other hand, isotonic regression has some drawbacks also: (1) By predicting constant values within bins, it inevitably increases grouping loss. (2) When the uncalibrated model has a non-monotonic reliability diagram, isotonic regression can only give sub-optimal results (i.e. large grouping loss). (3) While it performs well on large datasets, isotonic regression’s training time and memory consumption are also high on large datasets. (4) Isotonic regression can result in the first and last bins having full confidence (0 and 1), which can be problematic for certain datasets and evaluation metrics (e.g. log-loss). It is therefore common to clip the outputs from isotonic regression with a small \\epsilon (i.e., 0 to \\epsilon and 1 to 1 - \\epsilon).

#### 5.3.3 Platt scaling

Platt scaling is probably one of the most widely known approaches for probability calibration, partly due to the popularity of SVMs around the year 2000 (Platt, [2000](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR63 "Platt, J. (2000). Probabilities for SV Machines. In A. J. Smola, P. Bartlett, B. Schölkopf, & D. Schuurmans (Eds.), Advances in Large-Margin Classifiers (pp. 61–74). Cambridge: MIT Press.")). As SVMs are optimised with hinge loss, they can only output scores on the samples based on the estimated margins. Given that the margins are real scalars by definition, John Platt proposed to transform the scores into probability estimates with logistic regression. Platt scaling hence has the same parameters as a univariate logistic regression model: a shape parameter w \\in {\\mathbb {R}}, and a location parameter b \\in {\\mathbb {R}}. The predictive function is then:

\\begin{aligned} {\\textsf{g}}(s; w, b) = \\frac{1}{1+\\exp (-w \\cdot s-b)} \\end{aligned}

(8)


The parameters can be estimated by optimising the log-likelihood on the training set, so Platt scaling can be seen as optimising log-loss in the calibration context:

\\begin{aligned} {\\textsf{L}}(w, b) = \\frac{1}{N} \\sum \_{i=1}^{N} \\ln \\Big (\\sum \_{j=1}^{2} - {\\textsf{I}}(y\_i=j) \\cdot {\\textsf{g}}(s; w, b)\\Big ) \\end{aligned}

(9)


**Fig. 15**

![Fig. 15](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig15_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/15)

Examples of the Platt scaling approach. While it improves the under-confidence case well, it fails to do much with the over-confidence case. This is due to the fact that the sigmoid shape can not push the probabilities towards the middle hence can not fix over-confidence. Such result can also be observed with the MLP test case, where Platt scaling actually makes the level of calibration worse around several regions

Platt also included a technique to prevent overfitting and improve the generalisation of calibration, which is introduced as one of the training schemes at the beginning of this section. The test results are shown in Fig. [15](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig15).

In general, Platt scaling is a practical calibration approach with the following advantages: (1) As it is based on logistic regression, implementation is straightforward. (2) The standard logistic regression has a convex loss. The overall training process can, therefore be quite fast. On the negative side, Platt scaling has two main drawbacks: (1) The calibration map is restricted to a sigmoid shape, which effectively pushes probabilities away from the centre and may lead to over-confidence. (2) By definition, the logistic regression model considers the input space to be a real scalar space. While such an assumption is suitable for the margins obtained from an SVM, it is less appropriate for probabilistic classifiers, as the input is bounded by the interval \[0, 1\]. Hence, certain transformations are required when applying Platt scaling to calibrate probabilistic classifiers, such as the logit transform.

#### 5.3.4 Beta calibration

Beta calibration is specifically designed for probabilistic classifiers and alleviates both drawbacks of Platt scaling (Kull et al., [2017a](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR41 "Kull, M., Silva Filho, T., & Flach, P. (2017a). Beta calibration: A well-founded and easily implemented improvement on logistic calibration for binary classifiers. In A. Singh, & J. Zhu (Eds.), In Proceedings of the 20th International Conference on Artificial Intelligence and Statistics, vol. 54 of Proceedings of Machine Learning Research, (pp. 623–631). Fort Lauderdale, FL, USA. PMLR, PMLR."), [b](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR42 "Kull, M., Silva Filho, T. M., & Flach, P. (2017). Beyond sigmoids: How to obtain well-calibrated probabilities from binary classifiers with beta calibration. Electronic Journal of Statistics, 11(2), 5052–5080.")). While the latter can be derived from first principles by assuming that within each class the scores are normally distributed with the same variance, Beta calibration instead assumes two Beta distributions. This gives a richer family of calibration functions with three parameters: two shape parameters a, b \\in {\\mathbb {R}}, and a location parameter c \\in {\\mathbb {R}}. The calibration function is then given as:

\\begin{aligned} {\\textsf{g}}(s; a, b, c) = \\frac{1}{1+\\exp \\big (-a \\cdot \\ln s + b \\cdot \\ln (1-s) - c \\big )} \\end{aligned}

(10)


In comparison with Platt scaling, Beta calibration is a bivariate logistic regression model, where the two features are \\ln s and \\ln (1-s) respectively. Similar cross-validation training is also adopted as proposed in Kull et al. ( [2017a](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR41 "Kull, M., Silva Filho, T., & Flach, P. (2017a). Beta calibration: A well-founded and easily implemented improvement on logistic calibration for binary classifiers. In A. Singh, & J. Zhu (Eds.), In Proceedings of the 20th International Conference on Artificial Intelligence and Statistics, vol. 54 of Proceedings of Machine Learning Research, (pp. 623–631). Fort Lauderdale, FL, USA. PMLR, PMLR.")).

Given its close relationship to logistic regression, Beta calibration also optimises the log-loss and the objective function can be given with the log-likelihood:

\\begin{aligned} {\\textsf{L}}(a, b, c) = \\frac{1}{N} \\sum \_{i=1}^{N} \\ln \\Big (\\sum \_{j=1}^{2} - {\\textsf{I}}(y\_i=j) \\cdot {\\textsf{g}}(s; a, b, c)\\Big ) \\end{aligned}

(11)


**Fig. 16**

![Fig. 16](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig16_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/16)

Examples of Beta calibration. The Beta approach deals with the under-confident case fairly well, as the reliability diagram follows the diagonal closely after calibration. Regarding the over-confident case, Beta calibration manages to put more corrections than the Platt scaling around the \[0, 0.5\] region, as it pushes the reliability diagram towards the diagonal. However, it doesn’t help much in \[0.5, 1.0\] region. On the MLP case, Beta provides some improvements around the \[0.6, 1.0\] region, and matches the reliability diagram to the diagonal. Here we can see that the reliability diagrams after calibration are almost identical for the over-confidence and under-confidence test cases. This observation is because the Beta calibration method fits the map on the logarithm of the uncalibrated probabilities, and therefore reverts the sigmoid functions of the pseudo-models in both test cases. The calibration method then finds similar solutions as the pre-sigmoid parts are both linear models on the feature. This result suggests that the Beta calibration method can effectively fix the over/under-confidence caused by a sub-optimal linear-sigmoid operation

Figure [16](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig16) demonstrates Beta calibration on the three test cases. The advantages of Beta calibration include: (1) Compared with Platt scaling, it allows a richer family of calibration maps including inverse sigmoids and the identity map. The latter is particularly useful to prevent over-calibration and apply unnecessary adjustments to already calibrated probabilities. (2) Like with Platt scaling, implementation is straightforward. (3) With the Beta assumption, the calibration map supports any two-class probabilistic classifiers, and the calibration map is learnt from a set of functions that map from \[0, 1\] to \[0, 1\]. However, Beta calibration’s main drawback is that it can only model specific calibration maps, so if the original classifier is severely uncalibrated and requires a complicated calibration map, it might be preferable to choose non-parametric methods instead.

### 5.4 Calibration for multi-class classification

We now proceed with calibration maps that can work natively with a multi-class classification task, without the need for binarisation. We define a three-class test case for the purpose of examining multi-class calibration with a multi-layer perceptron (MLP). We modify the previous synthetic dataset to add an additional class, such that all classes are equi-probable and the distribution of the feature for the instances of class 3 is Gaussian also:

\\begin{aligned} Y&\\sim \\text {Categorical}\\left( \\left\[ \\frac{1}{3}, \\frac{1}{3}, \\frac{1}{3}\\right\] \\right) \\\ H&\\sim \\text {Categorical}(0.5) \\\ X \\mid Y=1, H=1&\\sim \\text {Gaussian}(-4, 960) \\\ X \\mid Y=1, H=2&\\sim \\text {Gaussian}(64, 1280) \\\ X \\mid Y=2, H=1&\\sim \\text {Gaussian}(4, 980) \\\ X \\mid Y=2, H=2&\\sim \\text {Gaussian}(-72, 1024) \\\ X \\mid Y=3&\\sim \\text {Gaussian}(0, 8) \\\ \\end{aligned}

We visualise the calibration maps in the probability simplex (one for each class). An example can be seen in the top row of Fig. [17](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig17), where the heat maps indicate the change of probability for each class after calibration. For the figure on the left, each point within the simplex represents an uncalibrated probability vector, a positive value (i.e., red colour) on that point indicates that the calibration map increases the probability value of class 1 in the vector and a negative value (i.e., blue colour) shows that the probability value on class 1 is reduced. The white line indicates where the probability values for class 1 remain (almost) unchanged. Class 2 and class 3 calibration maps are also depicted. The bottom row of each figure shows the class-wise reliability diagrams.

#### 5.4.1 Temperature scaling

**Fig. 17**

![Fig. 17](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig17_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/17)

MLP classifier with Temperature scaling (top: class-wise calibration map, bottom: class-wise reliability diagram). While Temperature scaling manages to improve the reliability diagram around the \[0.1, 0.4\] region for classes 1 and 2, we can see it actually makes things worse elsewhere. As the calibration maps show, Temperature scaling applies the same calibration map to all three classes despite them having different class-wise reliability diagrams, which is the main reason for the sub-optimal results

Temperature scaling has become one of the default approaches to provide better-calibrated probabilities, particularly in deep learning research (Hinton et al., [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR27 "Hinton, G., Vinyals, O., & Dean, J., et al. (2015). Distilling the knowledge in a neural network. arXiv preprint                   arXiv:1503.02531                                    , 2(7)."); Guo et al., [2017](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR24 "Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In 34th International Conference on Machine Learning, (pp. 1321–1330), Sydney, Australia. PMLR.")). Instead of simply applying the softmax operation at the last layer to obtain a probability vector on the classes, Temperature scaling assumes a single temperature parameter t \\in {\\mathbb {R}} and applies a linear operation before the softmax. Denoting {\\textbf{z}} = \[z\_1, \\dots , z\_K\] \\in {\\mathbb {R}}^K as the _K_-dimensional real vector before softmax, the probability output after Temperature scaling is given as:

\\begin{aligned} {\\textsf{c}}\_{j}({\\textbf{z}}; t) = \\frac{\\exp \\big (-z\_j / t\\big )}{\\sum \_{j=1}^{K}\\exp \\big (-z\_j / t\\big )} \\end{aligned}

(12)


Therefore, conventional softmax can be seen as the case of scaling with a fixed temperature of t=1.

If we want to apply Temperature scaling to a generic probabilistic model where _z_ is not accessible, we can also use the \\textsf{logit} transform on the uncalibrated probability vector to obtain a real vector:

\\begin{aligned} z\_j&= \\textsf{logit}\_j ({\\textbf{s}}) \\\&= \\ln \\frac{s\_j}{s\_K} \\end{aligned}

Here, _K_ is selected as the reference class to compute the probability ratio with other classes. The parameter is also normally estimated with the log-loss, and the objective function is given as:

\\begin{aligned} {\\textsf{L}}(t) = \\frac{1}{N} \\sum \_{i=1}^{N} \\ln \\Big (\\sum \_{j=1}^{K} - {\\textsf{I}}(y\_i=j) \\cdot {\\textsf{g}}\_{j}({\\textbf{z}}\_i; t)\\Big ) \\end{aligned}

(13)


Figure [17](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig17) gives the results on the MLP test case. The most distinctive characteristic of Temperature scaling is that it only has a single parameter, which can be seen as both an advantage and a disadvantage. On the positive side, a single parameter restricts the space of calibration maps and can prevent overfitting for small datasets with many classes. On the negative side, Temperature scaling can be sub-optimal when the function space of the calibration maps does not include the right reliability diagram.

#### 5.4.2 Vector scaling

**Fig. 18**

![Fig. 18](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig18_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/18)

Class-wise calibration maps and reliability diagrams for the MLP classifier with Vector scaling. The most obvious change from Temperature scaling is that now the calibration maps are different for each class. However, the calibration maps still have a circular shape as Vector scaling only adjusts one dimension of the logit vector for each class. As a result, the reliability diagram is close to the ones of Temperature scaling. Some minor improvements can be seen with class 3, where Vector scaling does not make it quite as bad as for Temperature scaling

Where Temperature scaling only has a single parameter across all classes, it is natural to extend the parameters to support a richer form of calibration maps. Vector scaling (Guo et al., [2017](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR24 "Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In 34th International Conference on Machine Learning, (pp. 1321–1330), Sydney, Australia. PMLR.")) allows a different temperature for each class, denoted as {\\textbf{w}} \\in {\\mathbb {R}}^{K}, as well as adding a set of intercept parameters {\\textbf{b}} \\in {\\mathbb {R}}^{K} for the _K_ classes. The predictive function is given as ({\\textbf{z}} can also be obtained with the logit transform for generic probability classifier, as in Temperature scaling):

\\begin{aligned} {\\textsf{c}}\_{j}({\\textbf{z}}; {\\textbf{w}}) = \\frac{\\exp \\big (-w\_j \\cdot z\_j -b\_j\\big )}{\\sum \_{j=1}^{K}\\exp \\big (-w\_j \\cdot z\_j - b\_j\\big )} \\end{aligned}

(14)


And the objective function to optimise log-likelihood is similar to the one for Temperature scaling, but with more parameters:

\\begin{aligned} {\\textsf{L}}({\\textbf{w}}, {\\textbf{b}})= \\frac{1}{N} \\sum \_{i=1}^{N} \\ln \\Big (\\sum \_{j=1}^{K} - {\\textsf{I}}(y\_i=j) \\cdot {\\textsf{g}}\_{j}({\\textbf{z}}\_i; {\\textbf{w}}, {\\textbf{b}})\\Big ) \\end{aligned}

(15)


The test result is given in Fig. [18](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig18). Vector scaling can be seen as a middle point between the quite restrictive Temperature scaling and the general approach of Matrix scaling discussed below. Hence it balances the risk of overfitting and the richness of available calibration maps.

#### 5.4.3 Matrix scaling

Matrix scaling (Guo et al., [2017](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR24 "Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In 34th International Conference on Machine Learning, (pp. 1321–1330), Sydney, Australia. PMLR.")) removes all the parameter constraints on Temperature scaling and Vector scaling. Similar to a fully connected layer, it has a matrix parameter ({\\textbf{w}}\_1, \\cdots , {\\textbf{w}}\_K), {\\textbf{w}}\_j \\in {\\mathbb {R}}^K together with the intercept parameter {\\textbf{b}} \\in {\\mathbb {R}}^{K}. The predictive function is ({\\textbf{z}} can also be obtained with the logit transform, as in Temperature scaling):

\\begin{aligned} {\\textsf{c}}\_{j}({\\textbf{z}}; {\\textbf{w}}\_1, \\dots , {\\textbf{w}}\_{K}, {\\textbf{b}}) = \\frac{\\exp \\big (-{\\textbf{w}}\_j^T {\\textbf{z}} - b\_j\\big )}{\\sum \_{j=1}^{K}\\exp \\big (-{\\textbf{w}}\_j^T {\\textbf{z}} - b\_j\\big )} \\end{aligned}

(16)


and the objective function is:

\\begin{aligned} {\\textsf{L}}({\\textbf{w}}\_1, \\dots , {\\textbf{w}}\_K, {\\textbf{b}})= \\frac{1}{N} \\sum \_{i=1}^{N} \\ln \\Big (\\sum \_{j=1}^{K} - {\\textsf{I}}(y\_i=j) \\cdot {\\textsf{g}}\_{j}({\\textbf{z}}\_i; {\\textbf{w}}\_1, \\dots , {\\textbf{w}}\_K, {\\textbf{b}})\\Big ) \\end{aligned}

(17)


As indicated in Fig. [19](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig19), Matrix scaling can support a broader family of calibration maps than Vector scaling and Temperature scaling, but may be vulnerable to overfitting as it can be seen as another fully connected layer.

**Fig. 19**

![Fig. 19](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig19_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/19)

Class-wise calibration maps and reliability diagrams for the MLP classifier with Matrix scaling. As Matrix scaling is capable of providing fully linear adjustments on the logits for each class, we can see the class-wise calibration map no longer has the circular shape. While there are still minor improvements on the reliability diagram of class 1 and class 2, class 3 has gained a significant improvement

#### 5.4.4 Dirichlet calibration

Dirichlet calibration is the multi-class extension of Beta calibration (Kull et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR40 "Kull, M., Perello-Nieto, M., Kängsepp, M., Filho, T. S., Song, H., & Flach, P. (2019). Beyond temperature scaling: Obtaining well-calibrated multiclass probabilities with Dirichlet calibration. Advances in Neural Information Processing Systems (NeurIPS’19), 32, 12316–12326.")). Assuming Dirichlet distributions for the predicted probability vectors within each class, Dirichlet calibration is determined by a set of coefficient vectors ({\\textbf{w}}\_1, \\cdots , {\\textbf{w}}\_K), {\\textbf{w}}\_j \\in {\\mathbb {R}}^K, and a set of intercepts {\\textbf{b}} \\in {\\mathbb {R}}^{K}. The calibrated probability on the j\\text {-th} class is obtained as:

\\begin{aligned} {\\textsf{g}}\_{j}({\\textbf{s}}; {\\textbf{w}}\_1, \\dots , {\\textbf{w}}\_{K}, {\\textbf{b}}) = \\frac{\\exp (-b\_j - {\\textbf{w}}\_j^T \\ln {\\textbf{s}})}{\\sum \_{j=1}^{K}\\exp (-b\_j-{\\textbf{w}}\_j^T \\ln {\\textbf{s}})} \\end{aligned}

(18)


This function can be seen as a _K_-dimensional logistic regression on the log-probabilities (i.e., the sufficient statistics of the Dirichlet distribution). Therefore, to apply Dirichlet calibration to a deep neural network, one can first obtain a probability vector using the softmax function, then apply Dirichlet calibration as with other probabilistic classifiers. The objective function is:

\\begin{aligned} {\\textsf{L}}({\\textbf{w}}\_1, \\dots , {\\textbf{w}}\_K, {\\textbf{b}})= \\frac{1}{N} \\sum \_{i=1}^{N} \\ln \\Big (\\sum \_{j=1}^{K} - {\\textsf{I}}(y\_i=j) \\cdot {\\textsf{g}}\_{j}({\\textbf{s}}\_i; {\\textbf{w}}\_1, \\dots , {\\textbf{w}}\_K, {\\textbf{b}})\\Big ) \\end{aligned}

(19)


The test results are given in Fig. [20](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig20). Similar to Beta calibration, one of the advantages of Dirichlet calibration is that it also supports the identity map, so it can also prevent over-adjusting calibrated results. As the number of parameters is similar to that of Matrix scaling, the Dirichlet calibration can also overfit on small datasets. The authors propose the ODIR (Off-Diagonal and Intercept Regularisation) approach to address this issue further and report various performance improvements in their experiments.

**Fig. 20**

![Fig. 20](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig20_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/20)

Class-wise calibration maps and reliability diagrams for the MLP classifier with Dirichlet calibration. The overall results on the class-wise reliability diagrams are close to those obtained with Matrix scaling. The major differences are seen in the calibration maps, where we can clearly observe a local region for the changes on class 3. Importantly, this region for the Dirichlet calibration approach doesn’t cover the area where the predicted probability of class 3 is close to 1. This is more reasonable compared with Matrix scaling, as both the Bayes-optimal predictions and the MLP predictions for class 3 are capped around 0.8

### 5.5 Extended methods for post-hoc classifier calibration

In this section we discuss more recent work extending the standard calibration methods discussed above.

Leathart et al. ( [2017](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR46 "Leathart, T., Frank, E., Holmes, G., & Pfahringer, B. (2017). Probability Calibration Trees. In Asian Conference on Machine Learning, (pp. 145–160). PMLR.")) aim to build calibration maps locally instead of a global calibration map and proposes using modified logistic model trees to build an ensemble calibration method. A decision tree is learnt to separate the original feature space into multiple regions, where a local calibrator can then be estimated using the corresponding outputs and labels. Kumar et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR43 "Kumar, A., Liang, P., & Ma, T. (2019). Verified Uncertainty Calibration. In: Advances in Neural Information Processing Systems (NeurIPS’19).")) propose a combined approach of scaling and binning methods to achieve better calibration with smaller calibration sets. Instead of calculating the label frequency in binning methods, the authors show that using the average value of a pre-fit continuous calibration map gives better calibration. The authors also indicate that a debiased estimator can provide better calibration error in sample complexity. Wang et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR80 "Wang, Y., Li, L., & Dang, C. (2019). Calibrating classification probabilities with shape-restricted polynomial regression. IEEE Transactions on Pattern Analysis and Machine Intelligence, 41(8), 1813–1827.")) discuss how to build flexible univariate non-decreasing calibration maps from shape-restricted polynomial regression models. The resulting method provides a useful alternative when methods like Plat scaling and Beta calibration cannot approximate the actual reliability diagram. Wenger et al. ( [2020](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR82 "Wenger, J., Kjellström, H., & Triebel, R. (2020). Non-parametric calibration for classification. In International Conference on Artificial Intelligence and Statistics, (pp. 178–190). PMLR.")) investigate non-parametric post-hoc approaches that can support richer forms of calibration map for a multi-class setting. The idea is to employ the framework of Gaussian processes and model the calibration map as latent distribution of functions. The family of calibration maps can thus be richer with the selection of suitable kernels. Zhang et al. ( [2020](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR88 "Zhang, J., Kailkhura, B., & Han, T. Y.-J. (2020). Mix-n-match: Ensemble and compositional methods for uncertainty calibration in deep learning. In International Conference on Machine Learning, (pp. 11117–11128).")) propose an approach to build an ensemble of base calibrators, which can improve the capacity of the calibration maps while preserving the accuracy. The authors also adapt kernel density estimation as an alternative approach to evaluating calibration error. Ma and Blaschko ( [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR51 "Ma, X., & Blaschko, M. B. (2021). Meta-cal: Well-controlled post-hoc calibration by ranking. In International Conference on Machine Learning, (pp. 7235–7245). PMLR.")) consider the confidence calibration setting and propose to improve a calibration map with a ranking model. The authors demonstrate that the ranking model can be used to maintain the performance of the uncalibrated classifier in terms of precision and false positive rate. Patel et al. ( [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR61 "Patel, K., Beluch, W. H., Yang, B., Pfeiffer, M., & Zhang, D. (2021). Multi-class uncertainty calibration via mutual information maximization-based binning. In International Conference on Learning Representations.")) tackle the issue of applying class-wise binning calibrators to a multi-class setting. An iterative update method is provided to adjust the bin edges to better calibration, and a sample-sharing approach among similar classes is also introduced for better sample efficiency.

### 5.6 Methods that can improve calibration during training time

While post-hoc calibration can be applied to most existing classifiers, it is of practical interest to train well-calibrated models in the first place. Here we briefly mention some training-time calibration methods.

Kumar et al. ( [2018](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR44 "Kumar, A., Sarawagi, S., &Jain, U. (2018). Trainable Calibration Measures For Neural Networks From Kernel Mean Embeddings. In Dy, J. and Krause, A., editors, 35th International Conference on Machine Learning, volume 80 of Proceedings of Machine Learning Research, vol. 80 of Proceedings of Machine Learning Research, (pp. 2805–2814). Stockholmsmässan, Stockholm Sweden. PMLR.")) consider a regularisation approach with kernel mean embedding. The idea is to add a differentiable regularisation term concerning the goodness of calibration, where the kernel mean of the scores is calculated as an approximation of the calibration error. The overall objective function allows the model to achieve better calibration during the training phase. Thulasidasan et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR74 "Thulasidasan, S., Chennupati, G., Bilmes, J., Bhattacharya, T., & Michalak, S. (2019). On mixup training: Improved calibration and predictive uncertainty for deep neural networks. arXiv preprint                   arXiv:1905.11001                                    .")) show that the Mixup strategy can improve the calibration level when introduced during the training phase. Vicinal points are created by combining existing data points and labels, and then added to the training set. The authors suggest that the improvement in calibration is due to the augmentation effect and label smoothing effect, both from the mixup process and act as a form of regularisation. Kristiadi et al. ( [2020](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR35 "Kristiadi, A., Hein, M., & Hennig, P. (2020). Being bayesian, even just a bit, fixes overconfidence in relu networks. In International Conference on Machine Learning, (pp. 5436–5446). PMLR.")) consider a Bayesian approach where a Gaussian approximation distribution is fitted to the last layer’s weights of a ReLu network. The authors demonstrated that the method could reduce the over-confidence problem in a classification setting, particularly on data points not commonly seen in the original training set. Wen et al. ( [2020](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR81 "Wen, Y., Tran, D., & Ba, J. (2020). Batchensemble: An alternative approach to efficient ensemble and lifelong learning. arXiv preprint                   arXiv:2002.06715                                    .")) propose an efficient ensemble approach that can train multiple deep networks with lower computational and memory costs. The authors show that the obtained ensemble achieves better calibration on out-of-distribution samples at test time.

Other than deep networks, some recent work achieves better calibration on Bayesian nonparametric methods. Milios et al. ( [2018](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR53 "Milios, D., Michiardi, P., Rosasco, L., & Filippone, M. (2018). Dirichlet-based gaussian processes for large-scale calibrated classification. Advances in Neural Information Processing Systems (NIPS’18), 31, 6005–6015.")) propose an alternative approach to train Gaussian Processes for classification tasks. While the traditional GP classifier relies on sigmoid or probit link functions and requires suitable approximated inference schemes to ensure good performance, the authors propose a modified Dirichlet link function to ensure the level of calibration as well as scalability. Tran et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR75 "Tran, G.-L., Bonilla, E. V., Cunningham, J., Michiardi, P., & Filippone, M. (2019). Calibrating deep convolutional gaussian processes. In The 22nd International Conference on Artificial Intelligence and Statistics, (pp. 1554–1563). PMLR.")) demonstrate that convolution Gaussian process classifiers can be miscalibrated, and propose a solution to mitigate the issue.

### 5.7 Methods for probability calibration for other predictive settings

The concept of calibration can be naturally generalised to predictive settings other than classification. The most straightforward extension is the calibration of regression outputs. As in the classification scenario, there are multiple definitions of calibration for regression models. The standard definition of calibration comes from the field of quantile regression Koenker and Hallock ( [2001](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR34 "Koenker, R., & Hallock, K. F. (2001). Quantile regression. Journal of Economic Perspectives, 15(4), 143–156.")), where being calibrated means that the predicted quantile matches the marginal distribution of the target variable. As in the case of classification, there are methods designed for training calibrated quantile regression as well as post-hoc approaches that calibrate pre-trained models. Fasiolo et al. ( [2020](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR15 "Fasiolo, M., Wood, S. N., Zaffran, M., Nedellec, R., & Goude, Y. (2020). Fast calibrated additive quantile regression. Journal of the American Statistical Association, 1–11.")) provide an approach to train generalised additive regression models with calibrated quantiles. Cui et al. ( [2020](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR11 "Cui, P., Hu, W., & Zhu, J. (2020). Calibrated reliable regression using maximum mean discrepancy. Advances in Neural Information Processing Systems, 33, 17164–75.")) propose an approach to train deep regression models with better-calibrated quantiles, where the model parameter is first fit with log-loss and then updated with a loss based on the maximal mean discrepancy Gretton et al. ( [2012](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR22 "Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B., & Smola, A. (2012). A kernel two-sample test. The Journal of Machine Learning Research, 13(1), 723–773.")). For the post-hoc setting, Kuleshov et al. ( [2018](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR37 "Kuleshov, V., Fenner, N., & Ermon, S. (2018). Accurate uncertainties for deep learning using calibrated regression. In 35th International Conference on Machine Learning, ICML 2018, vol. 6, (pp. 4369–4377). International Machine Learning Society (IMLS).")) point out that deep regression models’ quantiles can be calibrated with binary calibrators such as isotonic regression and yield better performance on downstream tasks such as reinforcement learning. Chung et al. ( [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR9 "Chung, Y., Neiswanger, W., Char, I., & Schneider, J. (2021). Beyond pinball loss: Quantile methods for calibrated uncertainty quantification. Advances in Neural Information Processing Systems, 34, 10971–10984.")) introduce some modified loss functions to train quantile calibrators with specific emphases, such as balancing between calibration and sharpness.

Regarding the definition of calibration, Song et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR73 "Song, H., Diethe, T., Kull, M., & Flach, P. (2019). Distribution calibration for regression. In Chaudhuri, K. and Salakhutdinov, R., editors, 36th International Conference on Machine Learning, vol. 97, (pp. 5897–5906), Long Beach, California, USA. PMLR.")) propose a stronger notion of calibration in regression, where the local conditional distribution is required to be calibrated instead of the global quantile. The authors show that being distribution-calibrated in this sense implies being quantile-calibrated. A post-hoc approach based on the Gaussian process is also introduced, where the GP models a distribution of Beta calibrators conditioning on the original regression outputs. Kuleshov and Deshpande ( [2022](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR36 "Kuleshov, V., & Deshpande, S. (2022). Calibrated and sharp uncertainties in deep learning via density estimation. In International Conference on Machine Learning, (pp. 11683–11693). PMLR.")) consider achieving post-hoc distribution calibration by learning a lower dimensional representation of the (uncalibrated) local distributions, and the post-hoc calibrators can then be built with density estimators on these representations and the target values, which avoids the costs of distributional kernels and sparse variational inference. Sahoo et al. ( [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR68 "Sahoo, R., Zhao, S., Chen, A., & Ermon, S. (2021). Reliable decisions with threshold calibration. Threshold, 3, 3–5.")) propose the definition of threshold calibration for regression models, which is a stronger notion of calibration than being quantile-calibrated and weaker than the distribution-calibrated definition. Instead of asking for calibration on a marginal quantile or local distribution level, the proposed definition requires the model to be calibrated on a group of distributions that satisfy a given threshold condition, which ensures optimal decision-making when a threshold is put on the regression outputs.

Calibration of structured outputs, such as sequential outputs, is also of interest for application domains such as natural language processing and time-series modelling. Kuleshov and Liang ( [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR38 "Kuleshov, V., & Liang, P. S. (2015). Calibrated structured prediction. Advances in Neural Information Processing Systems, 28, 3474–3482.")) propose approaches to simplify the structured output to a two-class problem and employ a well-calibrated binary classifier to improve the calibration level. On the information-retrieval side, the traditional precision-recall curve is not sufficiently similar to a ROC curve to allow a similar calibration property. In contrast, the precision-recall-gain curve proposed by Flach and Kull ( [2015](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR19 "Flach, P. A., & Kull, M. (2015). Precision-recall-gain curves: PR analysis done right. Advances in Neural Information Processing Systems (NIPS’15), 1, 838–846.")) can be seen as a proper generalisation of ROC curve obtained by replacing weighted accuracy with F-score.

Conformal prediction (Vovk et al., [2005](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR77 "Vovk, V., Gammerman, A., & Shafer, G. (2005). Algorithmic learning in a random world. Berlin: Springer Science & Business Media."); Romano et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR67 "Romano, Y., Patterson, E., & Candes, E. (2019). Conformalized quantile regression. Advances in Neural Information Processing Systems, 32, 3543–3553."); Angelopoulos & Bates, [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR2 "Angelopoulos, A. N. & Bates, S. (2021). A gentle introduction to conformal prediction and distribution-free uncertainty quantification. arXiv preprint                   arXiv:2107.07511                                    .")) is another area closely related to the topic of probability calibration. For classification, conformal prediction aims to predict a set of labels that has a probability of 1 - \\alpha that includes the true label, where \\alpha is a user-defined significance level. Therefore, we can see the conformal prediction for classifiers as an alternative definition of calibration to label probability calibration. That is, instead of requiring the probability to be accurate on the label distributions, conformal prediction wants to ensure the calibration on a variable set of labels that are exactly calibrated on the given significance level. One of the approaches to construct a conformal classifier is to use a Venn predictor (Vovk et al., [2003](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR79 "Vovk, V., Shafer, G., & Nouretdinov, I. (2003). Self-calibrating probability forecasting. Advances in Neural Information Processing Systems, 16."); Vovk & Petej, [2012](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR78 "Vovk, V., & Petej, I. (2012). Venn-abers predictors. arXiv preprint                   arXiv:1211.0025                                    ."); Johansson et al., [2018](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR32 "Johansson, U., Löfström, T., Sundell, H., Linusson, H., Gidenstam, A., & Boström, H. (2018). Venn predictors for well-calibrated probability estimation trees. In A. Gammerman, V. Vovk, Z. Luo, E. Smirnov, & R. Peeters (Eds.), Proceedings of the Seventh Workshop on Conformal and Probabilistic Prediction and Applications, (pp. 3–14). PMLR.")). The framework makes use of the Venn taxonomy to define subsets of the original label space, and requires a classifier to make predictions about each element in the subset. The final conformal prediction can then be calculated using these predictions.

### 5.8 Methods designed for other research fields and applications

The notion of calibration can also be generalised to other areas where uncertainty quantification is of interest. rRecent work has started to explore other topics in statistics, machine learning and artificial intelligence related to calibration. Here we briefly introduce some of them. A comprehensive analysis of these works is left as future work. Pleiss et al. ( [2017](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR65 "Pleiss, G., Raghavan, M., Wu, F., Kleinberg, J., & Weinberger, K. Q. (2017). On fairness and calibration. arXiv preprint                   arXiv:1709.02012                                    .")) draw a link between the level of calibration and the evaluation of classifier fairness. Cobb et al. ( [2018](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR10 "Cobb, A. D., Roberts, S. J., & Gal, Y. (2018). Loss-Calibrated Approximate Inference in Bayesian Neural Networks. ICML: Theory of deep learning workshop.")) propose an approach to modify the lower bound of approximate Bayesian inference so that the final objective function can be calibrated according to a given decision loss. Liu et al. ( [2018](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR50 "Liu, S., Long, M., Wang, J., & Jordan, M. I. (2018). Generalized zero-shot learning with deep calibration network. Advances in Neural Information Processing Systems, 31, 2005–2015.")) adopt calibrated deep models to improve zero-shot learning. Menon and Williamson ( [2018](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR52 "Menon, A. K., & Williamson, R. C. (2018). A loss framework for calibrated anomaly detection. In Proceedings of the 32nd International Conference on Neural Information Processing Systems, (pp. 1494–1504).")) consider the calibration problem for an anomaly detection setup. Ghandeharioun et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR20 "Ghandeharioun, A., Eoff, B., Jou, B., & Picard, R. (2019). Characterizing sources of uncertainty to proxy calibration and disambiguate annotator and data bias. In 2019 IEEE/CVF International Conference on Computer Vision Workshop (ICCVW), (pp. 4202–4206). IEEE.")) consider uncertainty and calibration as a tool to improve explainability for computer vision tasks. And Liu et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR49 "Liu, J. Z., Paisley, J., Kioumourtzoglou, M.-A., & Coull, B. (2019). Accurate uncertainty estimation and decomposition in ensemble learning. arXiv preprint                   arXiv:1911.04061                                    .")) adopt a calibration procedure to achieve better posterior distributions for a Bayesian non-parametric ensemble model. Ding et al. ( [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR13 "Ding, Z., Han, X., Liu, P., & Niethammer, M. (2021). Local temperature scaling for probability calibration. In Proceedings of the IEEE/CVF International Conference on Computer Vision, (pp. 6889–6899).")) consider the problem of improving calibration for semantic segmentation. Guillory et al. ( [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR23 "Guillory, D., Shankar, V., Ebrahimi, S., Darrell, T., & Schmidt, L. (2021). Predicting with confidence on unseen distributions. In Proceedings of the IEEE/CVF International Conference on Computer Vision, (pp. 1134–1144).")); Jiang et al. ( [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR31 "Jiang, Y., Nagarajan, V., Baek, C., & Kolter, J. Z. (2021). Assessing generalization of sgd via disagreement. arXiv preprint                   arXiv:2106.13799                                    .")) show that calibrated classifier can be used to estimate the model performance on OOD test sets.

## 6 Hypothesis tests for calibration

Even if a classifier is perfectly calibrated, it almost always slightly deviates from calibration on any finite dataset due to sampling effects. Here we consider a method of testing whether the dataset provides sufficient evidence that the classifier is uncalibrated.

A common way to test for calibration is to apply goodness-of-fit tests that were originally proposed for logistic regression models, but can be extended to any model that predicts probabilities. For example, one could apply the Pearson chi-squared goodness-of-fit test, which works by grouping instances sharing the same value of the independent variable _X_ and then applying a chi-squared test under the null hypothesis that the observed number of positives in the target variable is equal to the predicted number of positives for each unique value of _X_.

The issue with this approach is that the higher the number of unique values of _X_ or the higher the number of combinations of values of multiple independent variables, the lower the probability that each group of instances will be well-represented enough for the calculation of the Pearson chi-squared statistic to be reliable. A possible solution to this problem is to group instances into _M_ bins based on percentiles of the predicted probabilities for the positive class (equal-frequency binning) and then apply the Hosmer-Lemeshow (HL) test, which involves calculating the statistic _H_ given by Equation ( [20](https://link.springer.com/article/10.1007/s10994-023-06336-7#Equ20)) (Hosmer & Lemeshow, [2003](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR28 "Hosmer, D., & Lemeshow, S. (2003). Applied Logistic Regression. New Jersey: Wiley.")).

\\begin{aligned} H = \\sum \_{m=1}^{M} \\left( \\frac{\\left( O\_{m+} - E\_{m+}\\right) ^2}{E\_{m+}}+\\frac{\\left( O\_{m-} - E\_{m-}\\right) ^2}{E\_{m-}} \\right) , \\end{aligned}

(20)


where O\_{m+} and O\_{m-} are the observed counts of positives and negatives in bin {\\mathbb {B}}\_{m} and E\_{m+} and E\_{m-} are the expected counts of positives and negatives in bin {\\mathbb {B}}\_{m}, calculated as the sums of positive and negative probabilities in the bin, respectively.

The HL test was later extended to evaluate the goodness-of-fit of multinomial logistic regression models, by binning instances based on the percentiles of \\sum \_{j=2}^K s\_{ij} = 1 - s\_{i1}, i.e. the complement of the probabilities assigned to the reference class (Fagerland et al., [2008](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR14 "Fagerland, M. W., Hosmer, D. W., & Bofin, A. M. (2008). Multinomial goodness-of-fit tests for logistic regression models. Statistics in Medicine, 27(21), 4238–4253.                    https://doi.org/10.1002/sim.3202                                    ")). Then, similarly to the binary case, once the instances are binned, we calculate O\_{mj} and E\_{mj}, respectively the observed and expected counts for each class _j_ and bin _m_. Finally we calculate the _C_ statistic, given by Equation ( [21](https://link.springer.com/article/10.1007/s10994-023-06336-7#Equ21)), which is expected to follow a chi-squared distribution with (M-2)(K-1) degrees of freedom.

\\begin{aligned} C = \\sum \_{m=1}^{M}\\sum \_{j=1}^{K} \\left( \\frac{\\left( O\_{mj} - E\_{mj}\\right) ^2}{E\_{mj}}+\\frac{\\left( O\_{mj} - E\_{mj}\\right) ^2}{E\_{mj}} \\right) . \\end{aligned}

(21)


Table [8](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab8) shows M=5 bins based on the toy example of Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3). By applying Equation ( [21](https://link.springer.com/article/10.1007/s10994-023-06336-7#Equ21)) to these values, we get C = 25.3. Finally, to complete the HL test under the null hypothesis that the observed and expected proportions are the same, we compare _C_ to a chi-squared distribution with (M-2)(K-1) = 6 degrees of freedom, obtaining a p-value of 0.0003, rejecting the null hypothesis with \\alpha =0.05.

**Table 8 Instances grouped into 5 bins using equal-frequency binning on the complement of the probabilities predicted for class 1. Column {\\textsf{s}}({\\mathbb {B}}\_{m}) shows the probability intervals corresponding to each bin. The probabilities were obtained by considering the multiclass toy problem in Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3)**

[Full size table](https://link.springer.com/article/10.1007/s10994-023-06336-7/tables/8)

This example is of course simply illustrative, as the HL test is not recommended for such small samples, as experiments have shown that it has satisfactory power for samples of over 400 instances (Fagerland et al., [2008](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR14 "Fagerland, M. W., Hosmer, D. W., & Bofin, A. M. (2008). Multinomial goodness-of-fit tests for logistic regression models. Statistics in Medicine, 27(21), 4238–4253.                    https://doi.org/10.1002/sim.3202                                    ")). There are several other goodness-of-fit tests, most of them using some sort of binning to calculate a statistic that is assumed to follow a chi-squared distribution. Additionally, as the multiclass HL test, they usually test for classwise calibration. Testing for multiclass calibration is a more complex task and has recently been investigated by Widmann et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR83 "Widmann, D., Lindsten, F., & Zachariah, D. (2019). Calibration tests in multi-class classification: A unifying framework. Advances in Neural Information Processing Systems, 32, 12257–12267.")), by using kernel-based measures. These measures were later adapted for regression calibration (Widmann et al., [2022](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR84 "Widmann, D., Lindsten, F., & Zachariah, D. (2022). Calibration tests beyond classification.                    arXiv:2210.13355                                    ,                    https://doi.org/10.48550/ARXIV.2210.13355                                    ")). For details on how these measures can be interpreted as test statistics, we refer the reader to their original papers.

Another approach, proposed by Vaicenavicius et al. ( [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR76 "Vaicenavicius, J., Widmann, D., Andersson, C., Lindsten, F., Roll, J., & Schön, T. (2019). Evaluating model calibration in classification. In The 22nd International Conference on Artificial Intelligence and Statistics, (pp. 3459–3467). PMLR.")), is to test the classifier’s probabilities according to an arbitrary measure of calibration. Given a classifier {\\textsf{f}}, we can check if its predictions for a test set \\{({\\varvec{x}}\_1, y\_1), \\dots , ({\\varvec{x}}\_N, y\_N)\\} are calibrated according to a chosen calibration measure \\phi ({\\textsf{f}}({\\textbf{X}}\_{\\text {test}}),\\dot{\\textbf{Y}}\_{\\text {test}}), such as ECE, log-loss or Brier score. We discuss a simple resampling-based hypothesis test under the null hypothesis that the classifier’s outputs are calibrated (Vaicenavicius et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR76 "Vaicenavicius, J., Widmann, D., Andersson, C., Lindsten, F., Roll, J., & Schön, T. (2019). Evaluating model calibration in classification. In The 22nd International Conference on Artificial Intelligence and Statistics, (pp. 3459–3467). PMLR.")). Algorithm 1 details the steps of the hypothesis test procedure.

![figure a](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Figa_HTML.png)

Let us return to our toy example (Table [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Tab3)). If we follow Algorithm 1 and choose \\textsf{ECE}\_{\\text {classwise}} as the calibration measure and L=1,000, we obtain a distribution such as the one in Fig. [21](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fig21).

**Fig. 21**

![Fig. 21](https://media.springernature.com/lw685/springer-static/image/art%3A10.1007%2Fs10994-023-06336-7/MediaObjects/10994_2023_6336_Fig21_HTML.png)

[Full size image](https://link.springer.com/article/10.1007/s10994-023-06336-7/figures/21)

Distribution of \\textsf{ECE}\_{\\text {classwise}} values \\phi \_1,\\dots ,\\phi \_L calculated for every resampled label set \\dot{\\textbf{Y}}\_l with l \\in \\{1, \\ldots , L\\}, following the procedure described in Algorithm 1. The red bars represent the region where \\phi \_l > 0.1787

Recall that in our example \\textsf{ECE}\_{\\text {classwise}} = 0.1787. The p-value for this test is then {\\textsf{P}}\\Big (\\phi \_l > 0.1787\\Big ) \\approx 0.016, which means we can reject the null hypothesis that the classifier is calibrated according to \\textsf{ECE}\_{\\text {classwise}}. Note that we keep the scores fixed and only resample the labels to perform this test. This means that instances will stay in the same bins and small bins will have low weights for all _L_ resampled \\textsf{ECE}\_{\\text {classwise}} values.

## 7 Concluding remarks

In this survey we have given a detailed overview of the principles and practice of classifier calibration. We discussed the motivation, definition, evaluation and related approaches for the calibration of probabilistic classifiers, and touched upon topics beyond the standard classification setting. With the recent proliferation of predictive machine learning, it is becoming more and more important that models are carefully evaluated and if possibly improved on multiple criteria to ensure the overall system robustness. Classifier calibration relates to the criterion of uncertainty quantification, investigating the statistical relationships between model predictions and observed target variables. There are other levels of uncertainty in the overall modelling procedure, including uncertainty pertaining to model parameters when the training set is limited, uncertainty brought about by model mismatch, or uncertainty regarding whether the model should abstain when there might be novel target values that were not seen in the training set – see (Hüllermeier & Waegeman, [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR30 "Hüllermeier, E., & Waegeman, W. (2021). Aleatoric and epistemic uncertainty in machine learning: An introduction to concepts and methods. Machine Learning, 110(3), 457–506.")) for a recent survey on uncertainty in machine learning.

As we hopefully have made clear in this survey, calibration research has a rich history which predates the birth of machine learning as an academic field by decades. It is important to take full advantage of that history, which perhaps isn’t always fully acknowledged in recent literature on classifier calibration (e.g., of deep neural networks, which are often over-confident). Recent proposals such as confidence calibration, temperature scaling and expected calibration error have value but are far from the only options and may not be suitable for a particular application. As is often the case in machine learning, the space of options and things to consider is large, and navigating this space requires the right set of concepts and tools, many of which we have discussed in detail in this survey.

It is perhaps useful to point out that, naturally, there are also concepts that are less than helpful when thinking about classifier calibration. One of the most prominent of these is the concept of a decision boundary, which is like describing Mount Everest with a single contour line, halfway up. To faithfully characterise the mountain – which is what is needed for optimal decision making – one needs many contour lines at different elevations. The only case in which the decision boundary is useful is when the class prior (and misclassification costs, if any) won’t change after training, in which case only the decision threshold needs calibrating. In all other cases context change is expected and needs to be anticipated with a proper calibration analysis.

If a trained classifier _f_ is going to be used for a task for which it is good enough to be accurate, precise or to perform well according to any contingency matrix-based measure, then there is no particular need to consider calibration in the model’s development pipeline. However, if calibrated probabilities are important for any decisions supported by _f_, the following steps can be taken to implement what was discussed in this paper:

1. 1.
If possible, any classifiers considered for a task should be trained using a proper scoring rule as loss function;
   - The resulting models are likely to produce better probabilities than if a non-proper loss function is used, as probability refinement and calibration will be encouraged during training (recall Sect. [3](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec6));

   - An alternative is to use a method that encourages calibration during training time, as discussed in Sect. [5.6](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec27);
2. 2.
With the trained classifiers and, preferably a held-out calibration dataset, the calibration of the probabilities produced by the models can be evaluated using classwise reliability diagrams, to understand the miscalibration patterns, and/or ECE measures (recall Sect. [4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec8));

3. 3.
To help define which models are uncalibrated, a hypothesis test for calibration can be applied (recall Sect. [6](https://link.springer.com/article/10.1007/s10994-023-06336-7#Sec30));

4. 4.
If any models produce uncalibrated probabilities, post-hoc calibrators should be used to fix them;
   - The resulting calibrators should also be evaluated using reliability diagrams, ECE measures and hypothesis tests to find out which ones work best for the particular miscalibration patterns found during step 2.

In order to help with the aforementioned steps, we have developed an open-source Python library called PyCalib (Perello-Nieto et al., [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR62 "Perello-Nieto, M., Song, H., Silva Filho, T., & Kängsepp, M. (2021). Pycalib a library for classifier calibration. Zenodo: Retrieved from.                    https://doi.org/10.5281/zenodo.5518877                                     (If you use this software, please cite it as below)")).[Footnote 4](https://link.springer.com/article/10.1007/s10994-023-06336-7#Fn4) This library provides tools to measure the calibration quality of a classifier, multiple visualisation functions to better understand how calibrated is a model, and some calibration methods and pipelines to directly train arbitrary calibrated classifiers.

We close this survey with some open problems. First, although binning is such an important concept in calibration, there is no standard method to decide which type of binning, e.g. equal frequency or equal width, or what number of bins to use. Recent work (Kängsepp et al., [2022](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR33 "Kängsepp, M., Valk, K., & Kull, M. (2022). On the usefulness of the fit-on-the-test view on evaluating calibration of classifiers.                    arXiv. Retrieved                                     from                    arXiv:2203.08958                                    ,                    https://doi.org/10.48550/ARXIV.2203.08958                                    ")) has investigated cross-validation to tune the number of bins used to evaluate a model on a calibration set. Second, a recurrent topic of interest is the fact that post-hoc calibration does not improve robustness against out-of-distribution inputs and what can be done to improve calibration in this context (Ovadia et al., [2019](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR60 "Ovadia, Y., Fertig, E., Ren, J., Nado, Z., Sculley, D., Nowozin, S., Dillon, J., Lakshminarayanan, B., & Snoek, J. (2019). Can you trust your model’s uncertainty? Evaluating predictive uncertainty under dataset shift. Advances in Neural Information Processing Systems, 32.")). Finally, and somewhat related to the previous point, even though calibrated probabilities provide estimations of the uncertainty regarding an instance’s class given its feature values (aleatoric or first-order uncertainty), classifiers could also be made to predict their uncertainty about the predicted probabilities, which comes from not knowing the true probabilities (epistemic uncertainty). This type of prediction, a distribution of distributions, also called second-order uncertainty (Hüllermeier et al., [2022](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR29 "Hüllermeier, E., Destercke, S., & Shaker, M. H. (2022). Quantification of credal uncertainty in machine learning: A critical analysis and empirical comparison. In J. Cussens, & K. Zhang (Eds.), Proceedings of the Thirty-Eighth Conference on Uncertainty in Artificial Intelligence, vol. 180 of Proceedings of Machine Learning Research, (pp. 548–557). PMLR."); Bengs et al., [2022](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR5 "Bengs, V., Hüllermeier, E., & Waegeman, W. (2022). Pitfalls of epistemic uncertainty quantification through loss minimisation. In A. H. Oh, A. Agarwal, D. Belgrave, & K. Cho (eds.),  Advances in Neural Information Processing Systems.")), has been recently treated using inference based on Bayesian methods and credal sets, which are convex sets of probability distributions (Shaker & Hüllermeier, [2021](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR72 "Shaker, M. H., & Hüllermeier, E. (2021). Ensemble-based uncertainty quantification: Bayesian versus credal inference.                    arXiv. Retrieved                                     from                    arXiv:2107.10384                                    ,                    https://doi.org/10.48550/ARXIV.2107.10384                                    ")).

## Data availibility

The availability of data and material used in this survey can be found at [https://github.com/classifier-calibration/additional\_material](https://github.com/classifier-calibration/additional_material). Further information is available at [https://classifier-calibration.github.io/survey/](https://classifier-calibration.github.io/survey/).

## Code availability

The code to generate measurements, visualisation and results is part of PyCalib. Further information can be found in the documentation of the library [https://classifier-calibration.github.io/PyCalib/](https://classifier-calibration.github.io/PyCalib/).

## Notes

1. [https://classifier-calibration.github.io/PyCalib/](https://classifier-calibration.github.io/PyCalib/).

2. In rare cases it is possible for a multiclass classifier to be classwise calibrated but not confidence calibrated. Here is an example with 40 instances in four groups: 10 instances with predicted probabilities (0.3,0.3,0.4) and actual class distribution (4,2,4); another 10 with probabilities (0.4,0.3,0.3) and classes (3,4,3); another 10 with probabilities (0.4,0.6,0.0) and classes (5,5,0); and the remaining 10 instances with probabilities (0.3,0.6,0.1) and classes (2,7,1). This classifier is classwise-calibrated but not confidence-calibrated. There are 20 instances with confidence level 0.6 and accuracy 0.6 (5+7=12 out of 20), but the remaining 20 instances have confidence 0.4 and accuracy 0.35 (4+3=7 out of 20). The key idea of this construction is that classwise calibration considers the instances with 0.4 predicted for class 1 as a single group, but confidence calibration looks among them only at those instances for which 0.4 is the highest probability – e.g., it does consider (0.4,0.3,0.3) but not (0.4,0.6,0.0).

3. Some authors (Winkler, [1969](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR85 "Winkler, R. L. (1969). Scoring rules and the evaluation of probability assessors. Journal of the American Statistical Association, 64(327), 1073–1078."); Gneiting & Raftery, [2007](https://link.springer.com/article/10.1007/s10994-023-06336-7#ref-CR21 "Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. Journal of the American Statistical Association, 102(477), 359–378.")) use scoring rules in the opposite way, i.e. higher is better, sometimes calling them utility or payoff functions, in the sense that a forecaster is rewarded for giving better predictions. If a scoring rule was proposed as a payoff function, we can typically negate its values such that lower values are better.

4. The documentation of the library can be found at [https://classifier-calibration.github.io/PyCalib/](https://classifier-calibration.github.io/PyCalib/).


## References

- Allikivi, M.-L., & Kull, M. (2019). Non-parametric bayesian isotonic calibration: Fighting over-confidence in binary classification. In _Joint European Conference on Machine Learning and Knowledge Discovery in Databases (ECML-PKDD’19)_, (pp. 68–85).

- Angelopoulos, A. N. & Bates, S. (2021). A gentle introduction to conformal prediction and distribution-free uncertainty quantification. _arXiv preprint_ [arXiv:2107.07511](http://arxiv.org/abs/2107.07511).

- Ayer, M., Brunk, H. D., Ewing, G. M., Reid, W. T., & Silverman, E. (1955). An empirical distribution function for sampling with incomplete information. _The Annals of Mathematical Statistics,_ _26_, 641–647.

[Article](https://doi.org/10.1214%2Faoms%2F1177728423) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=73895) [MATH](http://www.emis.de/MATH-item?0066.38502) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=An%20empirical%20distribution%20function%20for%20sampling%20with%20incomplete%20information&journal=The%20Annals%20of%20Mathematical%20Statistics&doi=10.1214%2Faoms%2F1177728423&volume=26&pages=641-647&publication_year=1955&author=Ayer%2CM&author=Brunk%2CHD&author=Ewing%2CGM&author=Reid%2CWT&author=Silverman%2CE)

- Barlow, R. E., & Brunk, H. D. (1972). The isotonic regression problem and its dual. _Journal of the American Statistical Association,_ _67_(337), 140–147.

[Article](https://doi.org/10.1080%2F01621459.1972.10481216) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=314205) [MATH](http://www.emis.de/MATH-item?0236.62050) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20isotonic%20regression%20problem%20and%20its%20dual&journal=Journal%20of%20the%20American%20Statistical%20Association&doi=10.1080%2F01621459.1972.10481216&volume=67&issue=337&pages=140-147&publication_year=1972&author=Barlow%2CRE&author=Brunk%2CHD)

- Bengs, V., Hüllermeier, E., & Waegeman, W. (2022). Pitfalls of epistemic uncertainty quantification through loss minimisation. In A. H. Oh, A. Agarwal, D. Belgrave, & K. Cho (eds.), _Advances in Neural Information Processing Systems_.

- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. _Monthly Weather Review,_ _78_(1), 1–3.

[Article](https://doi.org/10.1175%2F1520-0493%281950%29078%3C0001%3AVOFEIT%3E2.0.CO%3B2) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Verification%20of%20forecasts%20expressed%20in%20terms%20of%20probability&journal=Monthly%20Weather%20Review&doi=10.1175%2F1520-0493%281950%29078%3C0001%3AVOFEIT%3E2.0.CO%3B2&volume=78&issue=1&pages=1-3&publication_year=1950&author=Brier%2CGW)

- Bröcker, J., & Smith, L. A. (2007). Increasing the reliability of reliability diagrams. _Weather and Forecasting,_ _22_(3), 651–661.

[Article](https://doi.org/10.1175%2FWAF993.1) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Increasing%20the%20reliability%20of%20reliability%20diagrams&journal=Weather%20and%20Forecasting&doi=10.1175%2FWAF993.1&volume=22&issue=3&pages=651-661&publication_year=2007&author=Br%C3%B6cker%2CJ&author=Smith%2CLA)

- Bross, I. (1954). Design for decision. _Science Education,_ _38_(4), 325.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Design%20for%20decision&journal=Science%20Education&volume=38&issue=4&publication_year=1954&author=Bross%2CI)

- Chung, Y., Neiswanger, W., Char, I., & Schneider, J. (2021). Beyond pinball loss: Quantile methods for calibrated uncertainty quantification. _Advances in Neural Information Processing Systems,_ _34_, 10971–10984.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Beyond%20pinball%20loss%3A%20Quantile%20methods%20for%20calibrated%20uncertainty%20quantification&journal=Advances%20in%20Neural%20Information%20Processing%20Systems&volume=34&pages=10971-10984&publication_year=2021&author=Chung%2CY&author=Neiswanger%2CW&author=Char%2CI&author=Schneider%2CJ)

- Cobb, A. D., Roberts, S. J., & Gal, Y. (2018). _Loss-Calibrated Approximate Inference in Bayesian Neural Networks_. ICML: Theory of deep learning workshop.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Loss-Calibrated%20Approximate%20Inference%20in%20Bayesian%20Neural%20Networks&publication_year=2018&author=Cobb%2CAD&author=Roberts%2CSJ&author=Gal%2CY)

- Cui, P., Hu, W., & Zhu, J. (2020). Calibrated reliable regression using maximum mean discrepancy. _Advances in Neural Information Processing Systems,_ _33_, 17164–75.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Calibrated%20reliable%20regression%20using%20maximum%20mean%20discrepancy&journal=Advances%20in%20Neural%20Information%20Processing%20Systems&volume=33&pages=17164-75&publication_year=2020&author=Cui%2CP&author=Hu%2CW&author=Zhu%2CJ)

- DeGroot, M. H., & Fienberg, S. E. (1983). The comparison and evaluation of forecasters. _Journal of the Royal Statistical Society Series D (The Statistician),_ _32_(1/2), 12–22.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20comparison%20and%20evaluation%20of%20forecasters&journal=Journal%20of%20the%20Royal%20Statistical%20Society%20Series%20D%20%28The%20Statistician%29&volume=32&issue=1%2F2&pages=12-22&publication_year=1983&author=DeGroot%2CMH&author=Fienberg%2CSE)

- Ding, Z., Han, X., Liu, P., & Niethammer, M. (2021). Local temperature scaling for probability calibration. In _Proceedings of the IEEE/CVF International Conference on Computer Vision_, (pp. 6889–6899).

- Fagerland, M. W., Hosmer, D. W., & Bofin, A. M. (2008). Multinomial goodness-of-fit tests for logistic regression models. _Statistics in Medicine,_ _27_(21), 4238–4253. [https://doi.org/10.1002/sim.3202](https://doi.org/10.1002/sim.3202)

[Article](https://doi.org/10.1002%2Fsim.3202) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=2526542) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Multinomial%20goodness-of-fit%20tests%20for%20logistic%20regression%20models&journal=Statistics%20in%20Medicine&doi=10.1002%2Fsim.3202&volume=27&issue=21&pages=4238-4253&publication_year=2008&author=Fagerland%2CMW&author=Hosmer%2CDW&author=Bofin%2CAM)

- Fasiolo, M., Wood, S. N., Zaffran, M., Nedellec, R., & Goude, Y. (2020). Fast calibrated additive quantile regression. _Journal of the American Statistical Association_, 1–11.

- Fawcett, T., & Niculescu-Mizil, A. (2007). PAV and the ROC convex hull. _Machine Learning,_ _68_(1), 97–106.

[Article](https://link.springer.com/article/10.1007/s10994-007-5011-0) [MATH](http://www.emis.de/MATH-item?1470.62082) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=PAV%20and%20the%20ROC%20convex%20hull&journal=Machine%20Learning&doi=10.1007%2Fs10994-007-5011-0&volume=68&issue=1&pages=97-106&publication_year=2007&author=Fawcett%2CT&author=Niculescu-Mizil%2CA)

- Flach, P. (2012). _Machine learning: The art and science of algorithms that make sense of data_. Cambridge: Cambridge University Press.

[Book](https://doi.org/10.1017%2FCBO9780511973000) [MATH](http://www.emis.de/MATH-item?1267.68010) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Machine%20learning%3A%20The%20art%20and%20science%20of%20algorithms%20that%20make%20sense%20of%20data&doi=10.1017%2FCBO9780511973000&publication_year=2012&author=Flach%2CP)

- Flach, P. (2014). Classification in context: Adapting to changes in class and cost distribution. In _First international workshop on learning over multiple contexts at European conference on machine learning and principles and practice of knowledge discovery in databases (ECML-PKDD)_.

- Flach, P. A., & Kull, M. (2015). Precision-recall-gain curves: PR analysis done right. _Advances in Neural Information Processing Systems (NIPS’15),_ _1_, 838–846.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Precision-recall-gain%20curves%3A%20PR%20analysis%20done%20right&journal=Advances%20in%20Neural%20Information%20Processing%20Systems%20%28NIPS%E2%80%9915%29&volume=1&pages=838-846&publication_year=2015&author=Flach%2CPA&author=Kull%2CM)

- Ghandeharioun, A., Eoff, B., Jou, B., & Picard, R. (2019). Characterizing sources of uncertainty to proxy calibration and disambiguate annotator and data bias. In _2019 IEEE/CVF International Conference on Computer Vision Workshop (ICCVW)_, (pp. 4202–4206). IEEE.

- Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. _Journal of the American Statistical Association,_ _102_(477), 359–378.

[Article](https://doi.org/10.1198%2F016214506000001437) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=2345548) [MATH](http://www.emis.de/MATH-item?1284.62093) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Strictly%20proper%20scoring%20rules%2C%20prediction%2C%20and%20estimation&journal=Journal%20of%20the%20American%20Statistical%20Association&doi=10.1198%2F016214506000001437&volume=102&issue=477&pages=359-378&publication_year=2007&author=Gneiting%2CT&author=Raftery%2CAE)

- Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B., & Smola, A. (2012). A kernel two-sample test. _The Journal of Machine Learning Research,_ _13_(1), 723–773.

[MathSciNet](http://www.ams.org/mathscinet-getitem?mr=2913716) [MATH](http://www.emis.de/MATH-item?1283.62095) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20kernel%20two-sample%20test&journal=The%20Journal%20of%20Machine%20Learning%20Research&volume=13&issue=1&pages=723-773&publication_year=2012&author=Gretton%2CA&author=Borgwardt%2CKM&author=Rasch%2CMJ&author=Sch%C3%B6lkopf%2CB&author=Smola%2CA)

- Guillory, D., Shankar, V., Ebrahimi, S., Darrell, T., & Schmidt, L. (2021). Predicting with confidence on unseen distributions. In _Proceedings of the IEEE/CVF International Conference on Computer Vision_, (pp. 1134–1144).

- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In _34th International Conference on Machine Learning_, (pp. 1321–1330), Sydney, Australia. PMLR.

- Hagedorn, R., Doblas-Reyes, F. J., & Palmer, T. N. (2005). The rationale behind the success of multi-model ensembles in seasonal forecasting - I. Basic concept. _Tellus A: Dynamic Meteorology and Oceanography,_ _57_(3), 219–233.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20rationale%20behind%20the%20success%20of%20multi-model%20ensembles%20in%20seasonal%20forecasting%20-%20I.%20Basic%20concept&journal=Tellus%20A%3A%20Dynamic%20Meteorology%20and%20Oceanography&volume=57&issue=3&pages=219-233&publication_year=2005&author=Hagedorn%2CR&author=Doblas-Reyes%2CFJ&author=Palmer%2CTN)

- Hallenbeck, C. (1920). Forecasting precipitation in percentages of probability. _Monthly Weather Review,_ _48_(11), 645–647.

[Article](https://doi.org/10.1175%2F1520-0493%281920%2948%3C645%3AFPIPOP%3E2.0.CO%3B2) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Forecasting%20precipitation%20in%20percentages%20of%20probability&journal=Monthly%20Weather%20Review&doi=10.1175%2F1520-0493%281920%2948%3C645%3AFPIPOP%3E2.0.CO%3B2&volume=48&issue=11&pages=645-647&publication_year=1920&author=Hallenbeck%2CC)

- Hinton, G., Vinyals, O., & Dean, J., et al. (2015). Distilling the knowledge in a neural network. _arXiv preprint_ [arXiv:1503.02531](http://arxiv.org/abs/1503.02531), 2(7).

- Hosmer, D., & Lemeshow, S. (2003). _Applied Logistic Regression_. New Jersey: Wiley.

[MATH](http://www.emis.de/MATH-item?0967.62045) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Applied%20Logistic%20Regression&publication_year=2003&author=Hosmer%2CD&author=Lemeshow%2CS)

- Hüllermeier, E., Destercke, S., & Shaker, M. H. (2022). Quantification of credal uncertainty in machine learning: A critical analysis and empirical comparison. In J. Cussens, & K. Zhang (Eds.), _Proceedings of the Thirty-Eighth Conference on Uncertainty in Artificial Intelligence_, vol. 180 of _Proceedings of Machine Learning Research_, (pp. 548–557). PMLR.

- Hüllermeier, E., & Waegeman, W. (2021). Aleatoric and epistemic uncertainty in machine learning: An introduction to concepts and methods. _Machine Learning,_ _110_(3), 457–506.

[Article](https://link.springer.com/article/10.1007/s10994-021-05946-3) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=4234924) [MATH](http://www.emis.de/MATH-item?07432810) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Aleatoric%20and%20epistemic%20uncertainty%20in%20machine%20learning%3A%20An%20introduction%20to%20concepts%20and%20methods&journal=Machine%20Learning&doi=10.1007%2Fs10994-021-05946-3&volume=110&issue=3&pages=457-506&publication_year=2021&author=H%C3%BCllermeier%2CE&author=Waegeman%2CW)

- Jiang, Y., Nagarajan, V., Baek, C., & Kolter, J. Z. (2021). Assessing generalization of sgd via disagreement. _arXiv preprint_ [arXiv:2106.13799](http://arxiv.org/abs/2106.13799).

- Johansson, U., Löfström, T., Sundell, H., Linusson, H., Gidenstam, A., & Boström, H. (2018). Venn predictors for well-calibrated probability estimation trees. In A. Gammerman, V. Vovk, Z. Luo, E. Smirnov, & R. Peeters (Eds.), _Proceedings of the Seventh Workshop on Conformal and Probabilistic Prediction and Applications_, (pp. 3–14). PMLR.

- Kängsepp, M., Valk, K., & Kull, M. (2022). On the usefulness of the fit-on-the-test view on evaluating calibration of classifiers. [arXiv. Retrieved](http://arxiv.org/abs/Retrieved) from [arXiv:2203.08958](http://arxiv.org/abs/2203.08958), [https://doi.org/10.48550/ARXIV.2203.08958](https://doi.org/10.48550/ARXIV.2203.08958)

- Koenker, R., & Hallock, K. F. (2001). Quantile regression. _Journal of Economic Perspectives,_ _15_(4), 143–156.

[Article](https://doi.org/10.1257%2Fjep.15.4.143) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Quantile%20regression&journal=Journal%20of%20Economic%20Perspectives&doi=10.1257%2Fjep.15.4.143&volume=15&issue=4&pages=143-156&publication_year=2001&author=Koenker%2CR&author=Hallock%2CKF)

- Kristiadi, A., Hein, M., & Hennig, P. (2020). Being bayesian, even just a bit, fixes overconfidence in relu networks. In _International Conference on Machine Learning_, (pp. 5436–5446). PMLR.

- Kuleshov, V., & Deshpande, S. (2022). Calibrated and sharp uncertainties in deep learning via density estimation. In _International Conference on Machine Learning_, (pp. 11683–11693). PMLR.

- Kuleshov, V., Fenner, N., & Ermon, S. (2018). Accurate uncertainties for deep learning using calibrated regression. In _35th International Conference on Machine Learning, ICML 2018_, vol. 6, (pp. 4369–4377). International Machine Learning Society (IMLS).

- Kuleshov, V., & Liang, P. S. (2015). Calibrated structured prediction. _Advances in Neural Information Processing Systems,_ _28_, 3474–3482.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Calibrated%20structured%20prediction&journal=Advances%20in%20Neural%20Information%20Processing%20Systems&volume=28&pages=3474-3482&publication_year=2015&author=Kuleshov%2CV&author=Liang%2CPS)

- Kull, M., & Flach, P. (2015). Novel decompositions of proper scoring rules for classification: Score adjustment as precursor to calibration. In _Joint European Conference on Machine Learning and Knowledge Discovery in Databases_, (pp. 68–85). Springer.

- Kull, M., Perello-Nieto, M., Kängsepp, M., Filho, T. S., Song, H., & Flach, P. (2019). Beyond temperature scaling: Obtaining well-calibrated multiclass probabilities with Dirichlet calibration. _Advances in Neural Information Processing Systems (NeurIPS’19),_ _32_, 12316–12326.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Beyond%20temperature%20scaling%3A%20Obtaining%20well-calibrated%20multiclass%20probabilities%20with%20Dirichlet%20calibration&journal=Advances%20in%20Neural%20Information%20Processing%20Systems%20%28NeurIPS%E2%80%9919%29&volume=32&pages=12316-12326&publication_year=2019&author=Kull%2CM&author=Perello-Nieto%2CM&author=K%C3%A4ngsepp%2CM&author=Filho%2CTS&author=Song%2CH&author=Flach%2CP)

- Kull, M., Silva Filho, T., & Flach, P. (2017a). Beta calibration: A well-founded and easily implemented improvement on logistic calibration for binary classifiers. In A. Singh, & J. Zhu (Eds.), In _Proceedings of the 20th International Conference on Artificial Intelligence and Statistics_, vol. 54 of _Proceedings of Machine Learning Research_, (pp. 623–631). Fort Lauderdale, FL, USA. PMLR, PMLR.

- Kull, M., Silva Filho, T. M., & Flach, P. (2017). Beyond sigmoids: How to obtain well-calibrated probabilities from binary classifiers with beta calibration. _Electronic Journal of Statistics,_ _11_(2), 5052–5080.

[Article](https://doi.org/10.1214%2F17-EJS1338SI) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=3738205) [MATH](http://www.emis.de/MATH-item?1384.62197) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Beyond%20sigmoids%3A%20How%20to%20obtain%20well-calibrated%20probabilities%20from%20binary%20classifiers%20with%20beta%20calibration&journal=Electronic%20Journal%20of%20Statistics&doi=10.1214%2F17-EJS1338SI&volume=11&issue=2&pages=5052-5080&publication_year=2017&author=Kull%2CM&author=Silva%20Filho%2CTM&author=Flach%2CP)

- Kumar, A., Liang, P., & Ma, T. (2019). Verified Uncertainty Calibration. In: _Advances in Neural Information Processing Systems (NeurIPS’19)_.

- Kumar, A., Sarawagi, S., &Jain, U. (2018). Trainable Calibration Measures For Neural Networks From Kernel Mean Embeddings. In Dy, J. and Krause, A., editors, _35th International Conference on Machine Learning, volume 80 of Proceedings of Machine Learning Research_, vol. 80 of _Proceedings of Machine Learning Research_, (pp. 2805–2814). Stockholmsmässan, Stockholm Sweden. PMLR.

- Lachiche, N., & Flach, P. A. (2003). Improving accuracy and cost of two-class and multi-class probabilistic classifiers using roc curves. In _Proceedings of the 20th International Conference on Machine Learning (ICML-03)_, (pp. 416–423).

- Leathart, T., Frank, E., Holmes, G., & Pfahringer, B. (2017). Probability Calibration Trees. In _Asian Conference on Machine Learning_, (pp. 145–160). PMLR.

- Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1977). Calibration of probabilities: The state of the art. In _Decision Making and Change in Human Affairs_, (pp. 275–324). Springer.

- Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1982). _Calibration of Probabilities: The state of the art to 1980_ (pp. 306–334). Cambridge: Cambridge University Press.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Calibration%20of%20Probabilities%3A%20The%20state%20of%20the%20art%20to%201980&pages=306-334&publication_year=1982&author=Lichtenstein%2CS&author=Fischhoff%2CB&author=Phillips%2CLD)

- Liu, J. Z., Paisley, J., Kioumourtzoglou, M.-A., & Coull, B. (2019). Accurate uncertainty estimation and decomposition in ensemble learning. _arXiv preprint_ [arXiv:1911.04061](http://arxiv.org/abs/1911.04061).

- Liu, S., Long, M., Wang, J., & Jordan, M. I. (2018). Generalized zero-shot learning with deep calibration network. _Advances in Neural Information Processing Systems,_ _31_, 2005–2015.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Generalized%20zero-shot%20learning%20with%20deep%20calibration%20network&journal=Advances%20in%20Neural%20Information%20Processing%20Systems&volume=31&pages=2005-2015&publication_year=2018&author=Liu%2CS&author=Long%2CM&author=Wang%2CJ&author=Jordan%2CMI)

- Ma, X., & Blaschko, M. B. (2021). Meta-cal: Well-controlled post-hoc calibration by ranking. In _International Conference on Machine Learning_, (pp. 7235–7245). PMLR.

- Menon, A. K., & Williamson, R. C. (2018). A loss framework for calibrated anomaly detection. In _Proceedings of the 32nd International Conference on Neural Information Processing Systems_, (pp. 1494–1504).

- Milios, D., Michiardi, P., Rosasco, L., & Filippone, M. (2018). Dirichlet-based gaussian processes for large-scale calibrated classification. _Advances in Neural Information Processing Systems (NIPS’18),_ _31_, 6005–6015.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Dirichlet-based%20gaussian%20processes%20for%20large-scale%20calibrated%20classification&journal=Advances%20in%20Neural%20Information%20Processing%20Systems%20%28NIPS%E2%80%9918%29&volume=31&pages=6005-6015&publication_year=2018&author=Milios%2CD&author=Michiardi%2CP&author=Rosasco%2CL&author=Filippone%2CM)

- Miller, R. G. (1962). _Statistical Prediction by Discriminant Analysis_ (pp. 1–54). Boston, MA: American Meteorological Society.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Statistical%20Prediction%20by%20Discriminant%20Analysis&pages=1-54&publication_year=1962&author=Miller%2CRG)

- Müller, R., Kornblith, S., & Hinton, G. (2019). When does label smoothing help? _arXiv preprint_ [arXiv:1906.02629](http://arxiv.org/abs/1906.02629).

- Murphy, A. H., & Winkler, R. L. (1977). Reliability of subjective probability forecasts of precipitation and temperature. _Journal of the Royal Statistical Society Series C (Applied Statistics),_ _26_(1), 41–47.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Reliability%20of%20subjective%20probability%20forecasts%20of%20precipitation%20and%20temperature&journal=Journal%20of%20the%20Royal%20Statistical%20Society%20Series%20C%20%28Applied%20Statistics%29&volume=26&issue=1&pages=41-47&publication_year=1977&author=Murphy%2CAH&author=Winkler%2CRL)

- Naeini, M. P., & Cooper, G. F. (2016). Binary Classifier Calibration Using An Ensemble Of Near Isotonic Regression Models. In _IEEE 16th International Conference on Data Mining (ICDM)_ (pp. 360–369). Institute of Electrical and Electronics Engineers (IEEE): IEEE.

- Naeini, P., Cooper, G. F., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using bayesian binning. In _29th AAAI Conference on Artificial Intelligence_, vol. 29.

- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In _22nd International Conference on Machine Learning (ICML’05)_, (pp. 625–632), New York, New York, USA. ACM Press.

- Ovadia, Y., Fertig, E., Ren, J., Nado, Z., Sculley, D., Nowozin, S., Dillon, J., Lakshminarayanan, B., & Snoek, J. (2019). Can you trust your model’s uncertainty? Evaluating predictive uncertainty under dataset shift. _Advances in Neural Information Processing Systems, 32_.

- Patel, K., Beluch, W. H., Yang, B., Pfeiffer, M., & Zhang, D. (2021). Multi-class uncertainty calibration via mutual information maximization-based binning. In _International Conference on Learning Representations_.

- Perello-Nieto, M., Song, H., Silva Filho, T., & Kängsepp, M. (2021). _Pycalib a library for classifier calibration_. Zenodo: Retrieved from. [https://doi.org/10.5281/zenodo.5518877](https://doi.org/10.5281/zenodo.5518877) (If you use this software, please cite it as below)

- Platt, J. (2000). Probabilities for SV Machines. In A. J. Smola, P. Bartlett, B. Schölkopf, & D. Schuurmans (Eds.), _Advances in Large-Margin Classifiers_ (pp. 61–74). Cambridge: MIT Press.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Probabilities%20for%20SV%20Machines&pages=61-74&publication_year=2000&author=Platt%2CJ)

- Platt, J. C. (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. _Advances in large margin classifiers_ (pp. 61–74). Cambridge: MIT Press.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Probabilistic%20outputs%20for%20support%20vector%20machines%20and%20comparisons%20to%20regularized%20likelihood%20methods&pages=61-74&publication_year=1999&author=Platt%2CJC)

- Pleiss, G., Raghavan, M., Wu, F., Kleinberg, J., & Weinberger, K. Q. (2017). On fairness and calibration. _arXiv preprint_ [arXiv:1709.02012](http://arxiv.org/abs/1709.02012).

- Roelofs, R., Cain, N., Shlens, J., & Mozer, M. C. (2021). Mitigating bias in calibration error estimation. _arXiv preprint_ [arXiv:2012.08668](http://arxiv.org/abs/2012.08668).

- Romano, Y., Patterson, E., & Candes, E. (2019). Conformalized quantile regression. _Advances in Neural Information Processing Systems,_ _32_, 3543–3553.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Conformalized%20quantile%20regression&journal=Advances%20in%20Neural%20Information%20Processing%20Systems&volume=32&pages=3543-3553&publication_year=2019&author=Romano%2CY&author=Patterson%2CE&author=Candes%2CE)

- Sahoo, R., Zhao, S., Chen, A., & Ermon, S. (2021). Reliable decisions with threshold calibration. _Threshold,_ _3_, 3–5.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Reliable%20decisions%20with%20threshold%20calibration&journal=Threshold&volume=3&pages=3-5&publication_year=2021&author=Sahoo%2CR&author=Zhao%2CS&author=Chen%2CA&author=Ermon%2CS)

- Sanders, F. (1963). On subjective probability forecasting. _Journal of Applied Meteorology,_ _2_(2), 191–201.

[Article](https://doi.org/10.1175%2F1520-0450%281963%29002%3C0191%3AOSPF%3E2.0.CO%3B2) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=3511364) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=On%20subjective%20probability%20forecasting&journal=Journal%20of%20Applied%20Meteorology&doi=10.1175%2F1520-0450%281963%29002%3C0191%3AOSPF%3E2.0.CO%3B2&volume=2&issue=2&pages=191-201&publication_year=1963&author=Sanders%2CF)

- Savage, L. J. (1971). Elicitation of personal probabilities and expectations. _Journal of the American Statistical Association,_ _66_(336), 783–801.

[Article](https://doi.org/10.1080%2F01621459.1971.10482346) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=331571) [MATH](http://www.emis.de/MATH-item?0253.92008) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Elicitation%20of%20personal%20probabilities%20and%20expectations&journal=Journal%20of%20the%20American%20Statistical%20Association&doi=10.1080%2F01621459.1971.10482346&volume=66&issue=336&pages=783-801&publication_year=1971&author=Savage%2CLJ)

- Senge, R., Bösner, S., Dembczyński, K., Haasenritter, J., Hirsch, O., Donner-Banzhoff, N., & Hüllermeier, E. (2014). Reliable classification: Learning classifiers that distinguish aleatoric and epistemic uncertainty. _Information Sciences,_ _255_, 16–29.

[Article](https://doi.org/10.1016%2Fj.ins.2013.07.030) [MathSciNet](http://www.ams.org/mathscinet-getitem?mr=3117127) [MATH](http://www.emis.de/MATH-item?1320.68145) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Reliable%20classification%3A%20Learning%20classifiers%20that%20distinguish%20aleatoric%20and%20epistemic%20uncertainty&journal=Information%20Sciences&doi=10.1016%2Fj.ins.2013.07.030&volume=255&pages=16-29&publication_year=2014&author=Senge%2CR&author=B%C3%B6sner%2CS&author=Dembczy%C5%84ski%2CK&author=Haasenritter%2CJ&author=Hirsch%2CO&author=Donner-Banzhoff%2CN&author=H%C3%BCllermeier%2CE)

- Shaker, M. H., & Hüllermeier, E. (2021). Ensemble-based uncertainty quantification: Bayesian versus credal inference. [arXiv. Retrieved](http://arxiv.org/abs/Retrieved) from [arXiv:2107.10384](http://arxiv.org/abs/2107.10384), [https://doi.org/10.48550/ARXIV.2107.10384](https://doi.org/10.48550/ARXIV.2107.10384)

- Song, H., Diethe, T., Kull, M., & Flach, P. (2019). Distribution calibration for regression. In Chaudhuri, K. and Salakhutdinov, R., editors, _36th International Conference on Machine Learning_, vol. 97, (pp. 5897–5906), Long Beach, California, USA. PMLR.

- Thulasidasan, S., Chennupati, G., Bilmes, J., Bhattacharya, T., & Michalak, S. (2019). On mixup training: Improved calibration and predictive uncertainty for deep neural networks. _arXiv preprint_ [arXiv:1905.11001](http://arxiv.org/abs/1905.11001).

- Tran, G.-L., Bonilla, E. V., Cunningham, J., Michiardi, P., & Filippone, M. (2019). Calibrating deep convolutional gaussian processes. In _The 22nd International Conference on Artificial Intelligence and Statistics_, (pp. 1554–1563). PMLR.

- Vaicenavicius, J., Widmann, D., Andersson, C., Lindsten, F., Roll, J., & Schön, T. (2019). Evaluating model calibration in classification. In _The 22nd International Conference on Artificial Intelligence and Statistics_, (pp. 3459–3467). PMLR.

- Vovk, V., Gammerman, A., & Shafer, G. (2005). _Algorithmic learning in a random world_. Berlin: Springer Science & Business Media.

[MATH](http://www.emis.de/MATH-item?1105.68052) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Algorithmic%20learning%20in%20a%20random%20world&publication_year=2005&author=Vovk%2CV&author=Gammerman%2CA&author=Shafer%2CG)

- Vovk, V., & Petej, I. (2012). Venn-abers predictors. _arXiv preprint_ [arXiv:1211.0025](http://arxiv.org/abs/1211.0025).

- Vovk, V., Shafer, G., & Nouretdinov, I. (2003). Self-calibrating probability forecasting. _Advances in Neural Information Processing Systems_, 16.

- Wang, Y., Li, L., & Dang, C. (2019). Calibrating classification probabilities with shape-restricted polynomial regression. _IEEE Transactions on Pattern Analysis and Machine Intelligence,_ _41_(8), 1813–1827.

[Article](https://doi.org/10.1109%2FTPAMI.2019.2895794) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Calibrating%20classification%20probabilities%20with%20shape-restricted%20polynomial%20regression&journal=IEEE%20Transactions%20on%20Pattern%20Analysis%20and%20Machine%20Intelligence&doi=10.1109%2FTPAMI.2019.2895794&volume=41&issue=8&pages=1813-1827&publication_year=2019&author=Wang%2CY&author=Li%2CL&author=Dang%2CC)

- Wen, Y., Tran, D., & Ba, J. (2020). Batchensemble: An alternative approach to efficient ensemble and lifelong learning. _arXiv preprint_ [arXiv:2002.06715](http://arxiv.org/abs/2002.06715).

- Wenger, J., Kjellström, H., & Triebel, R. (2020). Non-parametric calibration for classification. In _International Conference on Artificial Intelligence and Statistics_, (pp. 178–190). PMLR.

- Widmann, D., Lindsten, F., & Zachariah, D. (2019). Calibration tests in multi-class classification: A unifying framework. _Advances in Neural Information Processing Systems,_ _32_, 12257–12267.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Calibration%20tests%20in%20multi-class%20classification%3A%20A%20unifying%20framework&journal=Advances%20in%20Neural%20Information%20Processing%20Systems&volume=32&pages=12257-12267&publication_year=2019&author=Widmann%2CD&author=Lindsten%2CF&author=Zachariah%2CD)

- Widmann, D., Lindsten, F., & Zachariah, D. (2022). Calibration tests beyond classification. [arXiv:2210.13355](http://arxiv.org/abs/2210.13355), [https://doi.org/10.48550/ARXIV.2210.13355](https://doi.org/10.48550/ARXIV.2210.13355)

- Winkler, R. L. (1969). Scoring rules and the evaluation of probability assessors. _Journal of the American Statistical Association,_ _64_(327), 1073–1078.

[Article](https://doi.org/10.1080%2F01621459.1969.10501037) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Scoring%20rules%20and%20the%20evaluation%20of%20probability%20assessors&journal=Journal%20of%20the%20American%20Statistical%20Association&doi=10.1080%2F01621459.1969.10501037&volume=64&issue=327&pages=1073-1078&publication_year=1969&author=Winkler%2CRL)

- Zadrozny, B., & Elkan, C. (2001). Obtaining calibrated probability estimates from decision trees and naive bayesian classifiers. _ICML,_ _1_, 609–616.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Obtaining%20calibrated%20probability%20estimates%20from%20decision%20trees%20and%20naive%20bayesian%20classifiers&journal=ICML&volume=1&pages=609-616&publication_year=2001&author=Zadrozny%2CB&author=Elkan%2CC)

- Zadrozny, B. & Elkan, C. (2002). Transforming classifier scores into accurate multiclass probability estimates. In _8th ACM SIGKDD international conference on Knowledge discovery and data mining - KDD ’02_, (pp. 694–699), New York, New York, USA. ACM Press.

- Zhang, J., Kailkhura, B., & Han, T. Y.-J. (2020). Mix-n-match: Ensemble and compositional methods for uncertainty calibration in deep learning. In _International Conference on Machine Learning_, (pp. 11117–11128).


[Download references](https://citation-needed.springer.com/v2/references/10.1007/s10994-023-06336-7?format=refman&flavour=references)

## Funding

The work of PF, RSR and MPN was supported by the SPHERE Next Steps Project funded by the UK Engineering and Physical Sciences Research Council (EPSRC) \[grant EP/R005273/1\]. The work of RSR was funded by the UKRI Turing AI Fellowship \[grant EP/V024817/1\]. The work of PF and HS was supported by The Alan Turing Institute under EPSRC \[grant EP/N510129/1\]. The work of PF was partially supported by TAILOR, a project funded by EU Horizon 2020 research and innovation programme under GA No 952215. The work of MK was supported by Estonian Research Council \[grant PRG1604\] and by the Estonian Centre of Excellence in IT (EXCITE), funded by the European Regional Development Fund.

## Author information

Author notes

1. Telmo Silva Filho, Hao Song and Miquel Perello-Nieto have contributed equally to this work.


### Authors and Affiliations

1. Department of Statistics, Federal University of Paraíba, Cidade Universitária, João Pessoa, Paraíba, 58.051-900, Brazil

Telmo Silva Filho

2. Intelligent Systems Laboratory, University of Bristol, Merchant Venturers Building, Woodland Road, Bristol, BS8 1UB, United Kingdom

Telmo Silva Filho, Hao Song, Miquel Perello-Nieto, Raul Santos-Rodriguez & Peter Flach

3. Department of Computer Science, University of Tartu, Ülikooli 18, Tartu, 50090, Estonia

Meelis Kull


Authors

1. Telmo Silva Filho


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Telmo%20Silva%20Filho)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Telmo%20Silva%20Filho) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Telmo%20Silva%20Filho%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

2. Hao Song


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Hao%20Song)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Hao%20Song) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Hao%20Song%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

3. Miquel Perello-Nieto


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Miquel%20Perello-Nieto)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Miquel%20Perello-Nieto) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Miquel%20Perello-Nieto%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

4. Raul Santos-Rodriguez


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Raul%20Santos-Rodriguez)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Raul%20Santos-Rodriguez) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Raul%20Santos-Rodriguez%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

5. Meelis Kull


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Meelis%20Kull)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Meelis%20Kull) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Meelis%20Kull%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

6. Peter Flach


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Peter%20Flach)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Peter%20Flach) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Peter%20Flach%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)


### Contributions

TSF: conceptualisation, formal analysis, methodology, software, writing (original draft, and review and editing). HS: conceptualisation, formal analysis, methodology, software, writing (original draft, and review and editing). MPN: formal analysis, methodology, software, visualisation, writing (original draft, and review and editing). RSR: formal analysis, writing (review and editing). MK: conceptualisation, formal analysis, methodology, writing (review and editing). PF: conceptualisation, formal analysis, methodology, supervision, writing (original draft, and review and editing). (The categories follow the CRediT taxonomy: [http://credit.niso.org/](http://credit.niso.org/))

### Corresponding author

Correspondence to
[Miquel Perello-Nieto](mailto:miquel.perellonieto@bristol.ac.uk).

## Ethics declarations

### Conflict of interest

None.

### Ethics approval

Not applicable.

### Consent to participate

Not applicable.

### Consent for publication

Not applicable.

## Additional information

Editor: Eyke Hüllermeier.

### Publisher's Note

Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

## Rights and permissions

**Open Access** This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit [http://creativecommons.org/licenses/by/4.0/](http://creativecommons.org/licenses/by/4.0/).

[Reprints and permissions](https://s100.copyright.com/AppDispatchServlet?title=Classifier%20calibration%3A%20a%20survey%20on%20how%20to%20assess%20and%20improve%20predicted%20class%20probabilities&author=Telmo%20Silva%20Filho%20et%20al&contentID=10.1007%2Fs10994-023-06336-7&copyright=The%20Author%28s%29&publication=0885-6125&publicationDate=2023-05-16&publisherName=SpringerNature&orderBeanReset=true&oa=CC%20BY)

## About this article

[![Check for updates. Verify currency and authenticity via CrossMark](<Base64-Image-Removed>)](https://crossmark.crossref.org/dialog/?doi=10.1007/s10994-023-06336-7)

### Cite this article

Silva Filho, T., Song, H., Perello-Nieto, M. _et al._ Classifier calibration: a survey on how to assess and improve predicted class probabilities.
_Mach Learn_ **112**, 3211–3260 (2023). https://doi.org/10.1007/s10994-023-06336-7

[Download citation](https://citation-needed.springer.com/v2/references/10.1007/s10994-023-06336-7?format=refman&flavour=citation)

- Received: 05 January 2022

- Revised: 26 January 2023

- Accepted: 07 April 2023

- Published: 16 May 2023

- Version of record: 16 May 2023

- Issue date: September 2023

- DOI: https://doi.org/10.1007/s10994-023-06336-7


### Share this article

Anyone you share the following link with will be able to read this content:

Get shareable link

Sorry, a shareable link is not currently available for this article.

Copy shareable link to clipboard

Provided by the Springer Nature SharedIt content-sharing initiative


### Keywords

- [Classification](https://link.springer.com/search?query=Classification&facet-discipline=%22Computer%20Science%22)
- [Calibration](https://link.springer.com/search?query=Calibration&facet-discipline=%22Computer%20Science%22)
- [Confidence](https://link.springer.com/search?query=Confidence&facet-discipline=%22Computer%20Science%22)
- [Uncertainty](https://link.springer.com/search?query=Uncertainty&facet-discipline=%22Computer%20Science%22)
- [Multiclass](https://link.springer.com/search?query=Multiclass&facet-discipline=%22Computer%20Science%22)
- [Evaluation](https://link.springer.com/search?query=Evaluation&facet-discipline=%22Computer%20Science%22)

### Profiles

1. Telmo Silva Filho [View author profile](https://link.springer.com/researchers/88718628SN)
2. Miquel Perello-Nieto [View author profile](https://link.springer.com/researchers/84360220SN)
3. Peter Flach [View author profile](https://link.springer.com/researchers/56552020SN)