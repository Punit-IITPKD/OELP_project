Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/
Title: 
            A Survey of Methods for Time Series Change Point Detection - PMC
        
Fetched: 2026-11-26T16:34:40.454Z

[Skip to main content](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#main-content)

![](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/icon-dot-gov.svg)

**Official websites use .gov**

A
**.gov** website belongs to an official
government organization in the United States.


![](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/icon-https.svg)

**Secure .gov websites use HTTPS**

A **lock** (
Lock
Locked padlock icon
) or **https://** means you've safely
connected to the .gov website. Share sensitive
information only on official, secure websites.


[Home](https://pmc.ncbi.nlm.nih.gov/ "Home")

![PMC search open icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/search.svg)![PMC search close ison](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/close.svg)

Search PMC Full-Text Archive

Search in PMC![Search](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons-bg/search--white.svg)

- [Journal List](https://pmc.ncbi.nlm.nih.gov/journals/)
- [User Guide](https://pmc.ncbi.nlm.nih.gov/about/userguide/)

- ![Open resources icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/more_vert.svg)
- [![View on publisher site icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/launch.svg)](https://doi.org/10.1007/s10115-016-0987-z) View on publisher site
- [![Download PDF icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/file_download.svg)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/pdf/nihms860556.pdf) Download PDF
- ![Collections icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/action-bookmark-full.svg)![Collections icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/action-bookmark-empty.svg)Add to Collections
- ![Cite icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/format_quote.svg)Cite
- ![Show article permalink icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/share.svg)Permalink




## PERMALINK



![Copy icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/content_copy.svg)Copy


![Open article navigation icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/list.svg)

As a library, NLM provides access to scientific literature. Inclusion in an NLM database does not imply endorsement of, or agreement with,
the contents by NLM or the National Institutes of Health.

Learn more:
[PMC Disclaimer](https://pmc.ncbi.nlm.nih.gov/about/disclaimer/)
\|
[PMC Copyright Notice](https://pmc.ncbi.nlm.nih.gov/about/copyright/)

![NIHPA Author Manuscripts logo](https://cdn.ncbi.nlm.nih.gov/pmc/banners/logo-nihpa.png)

Knowl Inf Syst

. Author manuscript; available in PMC: 2017 Jun 8.

_Published in final edited form as:_ Knowl Inf Syst. 2016 Sep 8;51(2):339–367. doi: [10.1007/s10115-016-0987-z](https://doi.org/10.1007/s10115-016-0987-z)

# A Survey of Methods for Time Series Change Point Detection

[Samaneh Aminikhanghahi](https://pubmed.ncbi.nlm.nih.gov/?term=%22Aminikhanghahi%20S%22[Author])

### Samaneh Aminikhanghahi

1School of Electrical Engineering and Computer Science Washington State University, Pullman, WA

Find articles by [Samaneh Aminikhanghahi](https://pubmed.ncbi.nlm.nih.gov/?term=%22Aminikhanghahi%20S%22[Author])

1, [Diane J Cook](https://pubmed.ncbi.nlm.nih.gov/?term=%22Cook%20DJ%22[Author])

### Diane J Cook

1School of Electrical Engineering and Computer Science Washington State University, Pullman, WA

Find articles by [Diane J Cook](https://pubmed.ncbi.nlm.nih.gov/?term=%22Cook%20DJ%22[Author])

1

- Author information
- Article notes
- Copyright and License information

1School of Electrical Engineering and Computer Science Washington State University, Pullman, WA

Issue date 2017 May.

[PMC Copyright notice](https://pmc.ncbi.nlm.nih.gov/about/copyright/)

PMCID: PMC5464762  NIHMSID: NIHMS860556  PMID: [28603327](https://pubmed.ncbi.nlm.nih.gov/28603327/)

The publisher's version of this article is available at [Knowl Inf Syst](https://doi.org/10.1007/s10115-016-0987-z)

## Abstract

Change points are abrupt variations in time series data. Such abrupt changes may represent transitions that occur between states. Detection of change points is useful in modelling and prediction of time series and is found in application areas such as medical condition monitoring, climate change detection, speech and image analysis, and human activity analysis. This survey article enumerates, categorizes, and compares many of the methods that have been proposed to detect change points in time series. The methods examined include both supervised and unsupervised algorithms that have been introduced and evaluated. We introduce several criteria to compare the algorithms. Finally, we present some grand challenges for the community to consider.

**Keywords:** Change point detection, Time series data, Segmentation, Machine learning, Data mining

## 1\. INTRODUCTION

Time series analysis has become increasingly important in diverse fields including medicine, aerospace, finance, business, meteorology, and entertainment. Time series data are sequences of measurements over time describing the behavior of systems. These behaviors can change over time due to external events and/or internal systematic changes in dynamics/distribution \[ [1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R1)\]. Change point detection (CPD) is the problem of finding abrupt changes in data when a property of the time series changes \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\]. Segmentation, edge detection, event detection and anomaly detection are similar concepts which are occasionally applied as well as change point detection. Change point detection is closely related to the well-known problem of change point estimation or change point mining \[ [3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R3)\]\[ [4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R4)\]\[ [5](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R5)\]. Unlike CPD, however, change point estimation tries to model and interpret known changes in time series rather than identifying that a change has occurred. The focus of change point estimates is to describe the nature and degree of the known change.

In this paper, we survey the topic of change point detection and examine recent research in this area. CPD has been studied over the last several decades in the fields of data mining, statistics, and computer science. This problem covers a broad range of real-world problems. Here are some motivating examples.

##### Medical condition monitoring

Continuous monitoring of patient health involves trend detection in physiological variables such as heart rate, electroencephalogram (EEG), and electrocardiogram (ECG) in order to perform automated, real-time monitoring. Research studies investigate change point detection for specific medical issues such as sleep problems, epilepsy, magnetic resonance imaging (MRI) interpretation, and understanding of brain activities \[ [6](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R6)\]\[ [7](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R7)\]\[ [8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R8)\]\[ [9](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R9)\].

##### Climate change detection

Climate analysis, monitoring, and prediction methods that utilize change point detection have become increasingly important over the last few decades due to the possible occurrence of climate change and the increase of greenhouse gases in the atmosphere \[ [10](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R10)\]\[ [11](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R11)\]\[ [12](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R12)\].

##### Speech recognition

Speech recognition represents the process of converting spoken speech utterances to words or text. Change point detection methods are applied here for audio segmentation and recognizing boundaries between silence, sentences, words, and noise \[ [13](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R13)\]\[ [14](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R14)\].

##### Image analysis

Researchers and practitioners collect image data over time, or video data, for video-based surveillance. The detection of abrupt events, such as security breaches, can be formulated as a change-point problem. Here, the observation at each time point is the digital encoding of an image \[ [15](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R15)\].

##### Human activity analysis

Detecting activity breakpoints or transitions based on characteristics of observed sensor data from smart homes or mobile devices can be formulated as change point detection. These change points are useful for segmenting activities, interacting with humans while minimizing interruptions, providing activity-aware services, and detecting changes in behavior that provide insights on health status \[ [13](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R13)– [20](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R20)\].

In this survey we will explain the problem of change point detection and explore how different supervised and unsupervised methodologies can be used for detecting change points in time series data. We will compare and contrast investigated techniques based on their cost, limitations, and performance. Finally, we discuss the gaps in the research, summarize challenges that arise for change point applications, and provide suggestions for continuing investigation.

## 2\. BACKGROUND

[Figure 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#F1) graphs an example time series that contains several change points. The data illustrate long term mean annual temperature trends of Spitsbergen for the period 1899–2010 \[ [16](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R16)\]. The data can be used for climate change detection. This plot highlights the observation that the climate of Spitsbergen went through six different regimes in this period. We refer to these portions of the time series as states of the time series, or periods of time when the parameters governing the process do not change. Two consecutive distinct states are distinguished by a change point. The objective of change point detection is to identify these state borders by discovering the change points.

### Figure 1.

[![Figure 1](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/de75/5464762/d6acd50932af/nihms860556f1.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5464762_nihms860556f1.jpg)

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/figure/F1/)

Sample time series and change points (horizontal lines indicate separate states).

### 2.1 Definitions and Problem Formulation

We begin by presenting definitions of key terms that we use throughout this survey.

##### Definition 1

A _time series data stream_ is an infinite sequence of elements

|     |
| --- |
| S={x1,…,xi,…} |

where _xi_ is a d-dimensional data vector arriving at time stamp _i_ \[ [17](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R17)\].

##### Definition 2

A _stationary time series_ is a finite variance process whose statistical properties are all constant over time \[ [18](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R18)\]. This definition assumes that

- The mean value function _μt = E_( _xt_) is constant and does not depend on time _t_.

- The auto covariance function _γ_( _s_, _t_) _= cov_( _xs_, _xt_) _= E_\[( _xs_ − _μs_)( _xt_ − _μt_)\] depends on time stamps _s_ and _t_ only through their time difference, or _\|s – t\|_.


##### Definition 3

_Independent and identically distributed (i.i.d.) variables_ are mutually independent of each other, and are identically distributed in the sense that they are drawn from the same probability distribution. An i.i.d. time series is a special case of a stationary time series.

##### Definition 4

Given a time series _T_ of fixed length _m_ (a subset of a time series data stream) and _xt_ as a series sample at time _t_, a matrix _WM_ of all possible subsequences of length _k_ can be built by moving a _sliding window_ of size _k_ across _T_ and placing subsequence _Xp =_ { _xp_, _xp_ +1, … , _xp_ + _k_} ( [Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#F2)) in the _pth_ row of _WM_. The size of the resulting matrix _WM_ is ( _m_ − _k_ \+ 1) × _n_ \[ [19](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R19)\]\[ [20](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R20)\].

###### Figure 2.

[![Figure 2](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/de75/5464762/d6035e9436be/nihms860556f2.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5464762_nihms860556f2.jpg)

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/figure/F2/)

An illustrative example of time series notations.

##### Definition 5

In a time series, using sliding window _Xt_ as a sample instead of _xt_, an _interval χt_ with Hankel matrix { _Xt_, _Xt_ +1, … , _Xt_ + _n_–1} as shown in [Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#F2) will be a set of _n_ retrospective subsequence samples starting at time _t_ \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\]\[ [21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R21)\]\[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\].

##### Definition 6

A _change point_ represents a transition between different states in a process that generates the time series data.

##### Definition 7

Let { _x_ m, _x_ m+1, . . , _xn_} be a sequence of time series variables. _Change point detection (CPD)_ can be defined as the problem of hypothesis testing between two alternatives, the null hypothesis H0: “No change occurs” and the alternative hypothesis H _A_: “A change occurs” \[ [23](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R23)\]\[ [24](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R24)\]

1. H0: ℙ_X_ _m_ _=_ ⋯ _=_ ℙ_X_ _k_ _=_ ⋯ _=_ ℙ_X_ _n_.

2. H _A_: There exists _m < k\* < n_ such that ℙ_X_ _m_ _=_ ⋯ _=_ ℙ_X_ _k\*_ _≠_ ℙ_X_ _k\*_ +1 _=_ ⋯ _=_ ℙ_X_ _n_.

where ℙ_X_ _i_ is the probability density function of the sliding window start at point _xi_ and _k\*_ is a change point.


### 2.2 Criteria

In the previous section we provide a formal introduction to the traditional change point detection. However, practical application of change point detection introduces a number of new challenges that need to be addressed. Here we introduce and describe some of these challenges.

#### 2.2.1 Online detection

Change point detection algorithms are traditionally classified as “online” or “offline”. Offline algorithms consider the entire data set at once, and look back in time to recognize where the change occurred. The goal of this scenario is generally to identify all of a sequence’s change points in batch mode. In contrast, online, or real-time, algorithms run concurrently with the process they are monitoring, processing each data point as it becomes available, with a goal of detecting a change point as soon as possible after it occurs, ideally before the next data point arrives \[ [25](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R25)\].

In practice, no change point detection algorithm operates in perfect real time because it must inspect new data before determining if a change point occurred between the old and new data points. However, different online algorithms require different amounts of new data before change point detection can occur. Based on this observation we will define a new term to use throughout this paper. We will denote as an **_ε_** – **_real time algorithm_** an online algorithm which needs at least _ε_ data samples in the new batch of data to be able to find change points. An offline algorithm can then be viewed as _∞_ –real time and the completely-online algorithm is 1-real time because for every data point, it can predict whether or not a change point occurs before the new data point. Smaller _ε_ values may lead to stronger, more responsive change point detection algorithms.

#### 2.2.2 Scalability

Real world time series data from sources such as human activities and remote sensing satellites are becoming ever larger in both number of data points and number of dimensions. Change detection methods need to be designed in a computationally efficient manner so that they can scale to massive data sizes \[ [26](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R26)\]. Hence we compare the computational cost of alternative CPD algorithms to determine which one can reach an optimal (or a good enough) solution as fast as possible. One way to compare the computational cost of the algorithms is finding the algorithm is parametric or non-parametric. Distinguishing between parametric and nonparametric approaches is important because nonparametric approaches have demonstrated greater success for massively large datasets. Also, the computational cost of parametric methods is higher than nonparametric approaches and does not scale as well with the size of the dataset \[ [23](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R23)\].

A parametric approach specifies a particular functional form to be learned by the model and then estimates the unknown parameters based on labeled training data. Once the model has been trained the training examples can be discarded. In contrast, nonparametric methods do not make any assumptions about the form of the underlying function. The corresponding price to be paid is that all the available data has to be retained while making the inference \[ [27](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R27)\].

A successful algorithm must trade off decision quality for deliberation cost. One promising approach is to use anytime algorithms \[ [28](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R28)\] which allow the execution to be interrupted at any time and output the best possible solution obtained so far. A similar method is a contract algorithm which also trades off computation time for solution quality but is given the allowable run time in advance as a type of contract agreement. In contrast to an anytime algorithm, a contract algorithm receives its allowable execution time as a specified parameter. If a contract algorithm is interrupted before the allocated time is completed, it might not yield any useful results. An interruptible algorithm (such as an anytime algorithm) is one whose execution time is not given in advance and thus must be prepared to be interrupted at any moment, but it uses available time to continually improve the quality of its solution. In general, every interruptible algorithm is trivially a contract algorithm, but the converse is not true \[ [29](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R29)\].

#### 2.2.3 Algorithm constraints

Approaches to CPD can also be distinguished based on the requirements that are imposed on the input data and the algorithm. These constraints are important in selecting an appropriate technique for detecting change points in a specific data sequence. Constraints related to the nature of the time series data may emanate from the stationarity \[ [30](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R30)\], i.i.d. \[ [31](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R31)\], dimensionality, or continuity of the data \[ [32](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R32)\].

Some of the algorithms require information about the data, such as the number of change points in the data, the number of states in the system, and the features of the system states \[ [33](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R33)\]\[ [34](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R34)\]. Another important issue in parametric methods is the degree to which the algorithm is sensitive to the choice of initial parameter values.

### 2.3 Performance Evaluation

In order to compare alternative CPD algorithms and estimate the expected resulting performance, measures of performance are needed. Many performance metrics have been introduced to evaluate change point detection algorithms based on the type of decisions they make \[ [35](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R35)\]. The output of CPD algorithms can contain the following:

- Change-point yes/no decisions (the algorithm is a binary classifier)

- Change point identification with varying levels of precision (i.e., the =change point occurs within _x_ time units. This type of algorithm utilizes a multi-class classifier or unsupervised learning methods.

- The time of the next change point (or the times of all change points in the series)


In case of the first two types of output, standard methods for evaluating supervised learning algorithms can be utilized to evaluate the performance of the change point detector. A first step at evaluating the performance of a supervised change point learner is to generate a confusion matrix which summarizes the actual and predicted classes. [Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#T1) illustrates a confusion matrix for a binary change point classifier.

#### Table 1.

Example confusion matrix. In this example, a change point can be considered the “positive” class while no change point can be considered the “negative” class.

|  | Classified as change point | Classified as non-change point |
| :-- | :-: | :-: |
| True change point | TP | FN |
| True non-change point | FP | TN |

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/table/T1/)

Some of the useful performance metrics that we can employ to evaluate CPD algorithms are summarized below. While these are described in the context of binary classification, they can each be extended to classification of a greater number of classes by providing the measures for each class independently or in combination.

- Accuracy, calculated as the ratio of correctly-classified data points to total data points. This measure provides a high-level idea about the algorithm’s performance. The companion to accuracy is Error Rate, which is computed as 1 - Accuracy. Accuracy and Error Rate do not provide insights on the source of the error or the distribution of error among the different classes. In addition, they are ineffective for evaluating performance in a class-imbalanced dataset, which is typical for change point detection, because they consider different types of classification errors as equally important. Sensitivity and g-mean are useful metrics to utilize in this case.


|     |
| --- |
| Accuracy=TP+TNTP+FP+FN+TN |

- Sensitivity, also referred to as Recall or the true positive rate (TP Rate). This refers to the portion of a class of interest (Change Points) that was recognized correctly.


|     |
| --- |
| Sensitivity=Recall=TPRate=TPTP+FN |

- G-mean. Change point detection typically results in a learning problem with an imbalanced class distribution because the ratio of changes to total data is small. As a result, G-mean is commonly used as an indicator of CPD performance. This utilizes both Sensitivity and Specificity measures to assess the performance of the algorithm both in terms of the ratio of positive accuracy (Sensitivity) and the ratio of negative accuracy (Specificity).


|     |
| --- |
| G-mean=Sensitivity×Specificity=TPTP+FN×TNFP+TN |

- Precision. This is calculated as the ratio of true positive data points (change points) to total points classified as change points.


|     |
| --- |
| Precision=TPTP+FP |

- F-measure (also referred to as f-score or f1 score). This measure provides a way to combine Precision and Recall as a measure of the overall effectiveness of a CPD algorithm. F-measure is calculated as a ratio of the weighted importance of Precision and Recall.


|     |
| --- |
| F-measure=(1+β)2×Recall×Precisionβ2×Recall+Precision=(1+β)2×TPTP+FN×TPTP+FPβ2×TPTP+FN+TPTP+FP |

- Receiver Operating Characteristics Curve (ROC). ROC-based assessment facilitates explicit analysis of the tradeoff between true positive and false positive rates. This is done by plotting a two-dimensional graph with the false positive rate on the x axis and the true positive rates on the y axis. A CPD algorithm produces a (TP\_Rate, FP\_Rate) pair that corresponds to a single point in the ROC space. One algorithm can generally be considered as superior to another if its point is closer to the (0,1) coordinate (the upper left corner) than the other. To assess the overall performance of an algorithm, we can look at the Area Under the ROC curve, or AUC. In general, we want the false positive rate to be low and the true positive rate to be high. This means that the closer to 1 the AUC value is, the stronger is the algorithm. Another useful measure that can be derived from the ROC curve is the Equal Error Rate (EER), which is the point where the false positive rate and the false negative rate are equal. This point is kept small by a strong algorithm.

- Precision-Recall Curve (PR Curve). A PRC can also be generated and used to compare alternative CPD algorithms. The PR curve plots precision rate as a function of recall rate. While optimal algorithm performance for an ROC curve is indicated by points in the upper left of the space, optimal performance in the PR space is near the upper right. As with the ROC, the area under a PRC can be computed to compare two algorithms and attempt to optimize CPD performance. The PR curve in particular provides insightful analysis when the class distribution is highly skewed.


If the difference in time between the detected change point (CP) and the actual CP represents the measure of performance (utilizing supervised or unsupervised CPD methods), then the above metrics are not appropriate choices. Evaluating the performance of these algorithms is not as straightforward as for the previous case, because there is no single label against which the performance of the algorithm can be measured. However, a number of useful metrics exist for this case, including:

- Mean absolute error (MAE). This directly measures how close the predicted CP is to the actual CP. The absolute value of the difference between the predicted and actual CP time is summed and normalized over each of the CP points.


|     |
| --- |
| MAE=∑i=1#CP∣Predicted(CP)-Actual(CP)∣#CP |

- Mean squared error (MSE) is a well-known alternative to MAE. In this case, because the errors are squared, the resulting measure will be very large if a few dramatic outliers exist in the classified data.


|     |
| --- |
| MSE=∑i=1#CP(Predicted(CP)-Actual(CP))2#CP |

- Mean signed difference (MSD). In addition to calculating the difference between the predicted and actual CP, this measure considers the direction of the error (predicting before or after the actual CP time).


|     |
| --- |
| MSD=∑i=1#CP(Predicted(CP)-Actual(CP))#CP |

- Root mean squared error (RMSE). This aggregates the difference between predicted and actual error and squares each difference to remove the sign factor. The square root is computed of the final estimate to offset the scaling factor of squaring the individual differences.


|     |
| --- |
| RMSE=∑i=1#CP(Predicted(CP)-Actual(CP))2#CP |

- Normalized root mean squared error (NRMSE). This measure removes the sensitivity of the values to the unit size of the predicted value. NRMSE facilitates more direct comparison of error between different datasets and aids in interpreting the error measures. Two common methods are to normalize the error to the range of the observed CPs or normalize to the mean of the observed CPs.


|     |
| --- |
| NRSMSE=RMSEMaxLength(ActualCP)-MinLength(ActualCP)NRMSE=RMSEmean(ActualCP) |


## 3\. Review

Many machine learning algorithms have been designed, enhanced, and adapted for change point detection. Here, we provide an overview of the basic algorithms that are commonly applied to the CPD problem. These techniques include both supervised and unsupervised methods, chosen based on the desired outcome of the algorithm.

### 3.1. Supervised Methods

Supervised learning algorithms are machine learning algorithms that learn a mapping from input data to a target attribute of the data, which is usually a class label \[ [35](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R35)\]. [Figure 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#F3) provides an overview of supervised methods used in change point detection. When a supervised approach is employed for change point detection, machine learning algorithms can be trained as binary or multi-class classifiers. If the number of states is specified, the change point detection algorithm is trained to find each state boundary. A sliding window moves through the data, considering each possible division between two data points as a possible change point. While this approach has a simpler training phase, a sufficient amount and diversity of training data needs to be provided to represent all of the classes. On the other hand, detecting each class separately provides enough information to find both the nature and the amount of detected change. A variety of classifiers can be used for this learning problem. Examples include decision tree \[ [33](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R33)\]\[ [34](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R34)\]\[ [36](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R36)\]\[ [37](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R37)\], naïve Bayes \[ [33](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R33)\], Bayesian net \[ [34](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R34)\], support vector machine \[ [33](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R33)\]\[ [34](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R34)\], nearest neighbor \[ [33](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R33)\]\[ [20](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R20)\], hidden Markov model \[ [38](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R38)\]\[ [39](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R39)\]\[ [33](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R33)\], conditional random field \[ [34](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R34)\], and Gaussian mixture model (GMM) \[ [38](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R38)\]\[ [39](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R39)\].

#### Figure 3.

[![Figure 3](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/de75/5464762/5ee38edaf7d3/nihms860556f3.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5464762_nihms860556f3.jpg)

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/figure/F3/)

Supervised methods for change point detection.

An alternative is to treat change point detection as a binary class problem, where all of the possible state transition (change point) sequences represents one class and all of the within-state sequences represents a second class. While only two classes need to be learned in this case, this is a much more complex learning problem if the number of possible types of transitions is large \[ [35](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R35)\]. As with the previous type of supervised approaches, in this learning approach each feature in the input vector indicates a source of possible change. Therefore, any supervised learning algorithm that generates an interpretable model (such as a decision tree or a rule learner) will not only identify a change but also describe the nature of the change. Support vector machines \[ [21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R21)\]\[ [40](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R40)\], naïve Bayes \[ [21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R21)\], and logistic regression \[ [21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R21)\] have been tested using this approach. This type of problem will also suffer from extreme class imbalance as there are typically many more within-state sequences than change point sequences.

Another supervised approach is to use a virtual classifier \[ [4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R4)\]. This method goes beyond just detecting changes to actually interpreting a change that occurs between two consecutive windows. The virtual classifier attaches a hypothetical label (+1) to each sample from the first window and (−1) to each sample from the second window, then trains a virtual classifier (VC) using any supervised method based on the labeled data points. If there is a change point between two windows, they should be correctly classified by the classifier and the classification accuracy _p_ should be significantly higher than random noise _prand=0.5_. In order to test the significance of a change score, the inverse survival function of a binomial distribution is used to determine a critical value, _pcritical_, at which Bernoulli trials are expected to exceed _prand_ with α confidence level. Finally, if _p > pcritical_, a significant change exists between the two windows. Once the change point is detected, the classifier is retrained using all of the samples in the two neighboring windows. If some features play a dominant role in the classifier, then they are the ones that characterize the difference.

### 3.2 Unsupervised Methods

Unsupervised learning algorithms are typically used to discover patterns in unlabeled data. In the context of change point detection, such algorithms can be used to segment time series data, thus finding change points based on statistical features of the data. Unsupervised segmentation is attractive because it may handle a variety of different situations without requiring prior training for each situation. [Figure 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#F4) provides an overview of unsupervised methods that have been used for change point detection. Early reported methods utilize likelihood ratio based on the observation that the probability density of two consecutive intervals are the same if they belong to the same state. Another traditional solution is subspace modelling, which represents a time series using state spaces and thus detects change points by predicting the state space parameters. Probabilistic methods estimate probability distributions of the new interval based on the data that has been observed since the previous candidate change point. In contrast, kernel-based methods map observations onto a higher-dimensional feature space and detect change points by comparing the homogeneity of each subsequence. The graph based technique is a newly-introduced method which represents time series observations as a graph and applies statistical tests to detect change points based on this representation. Finally, clustering methods group time series data into their respective states and find changes by identifying differences between features of the states.

#### Figure 4.

[![Figure 4](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/de75/5464762/29415933b8c8/nihms860556f4.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5464762_nihms860556f4.jpg)

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/figure/F4/)

Unsupervised methods for change point detection.

#### 3.2.1 Likelihood Ratio Methods

A typical statistical formulation of change-point detection is to analyze the probability distributions of data before and after a candidate change point, and identify the candidate as a change point if the two distributions are significantly different. In these approaches, the logarithm of the likelihood ratio between two consecutive intervals in time-series data is monitored for detecting change points \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\].

This strategy requires two steps. First, the probability density of two consecutive intervals is calculated separately. Second, the ratio of these probability densities is computed. The most familiar change point algorithm is cumulative sum \[ [41](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R41)\]\[ [42](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R42)\]\[ [43](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R43)\]\[ [44](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R44)\], which accumulates deviations relative to a specified target of incoming measurements and indicates that a change point exists when the cumulative sum exceeds a specified threshold.

Change Finder \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\]\[ [45](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R45)\]\[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\] is another commonly used method which reduces the problem of change point detection into time series-based outlier detection. This method fits an Auto Regression (AR) model onto the data to represent the statistical behavior of the time series and updates its parameter estimates incrementally so that the effect of past examples is gradually discounted. Considering time series _xt_, we can model the time series using an AR mode of the _k_ th order by:

|     |
| --- |
| xt=ωxt-kt-1+ε |

where
xt-kt-1=(xt-1,xt-2,…,xt-k) are previous observations, _ω =_ ( _ω_ 1, … , _ωk_) ∈ ℝ _k_ are constants, and _ε_ is a normal random variable generated according to a Gaussian distribution like white noise. By updating model parameters the probability density function at time _t_ is calculated and we have a sequence of probability densities { _pt_: _t =_ 1, 2, … }. Next, an auxiliary time-series _yt_ is generated by giving a score to each data point. This score function is defined as the average of the log-likelihood, _Score_( _yt_) _=_ − log _pt_–1( _yt_), or statistical deviation, _Score_( _yt_) _= d_( _pt_–1, _pt_), where _d_( _\*_, _\*_) is provided by any of a number of distance functions including variation distance, Hellinger distance, or quadratic distance. The new time series data represents the difference between each pair of consecutive time series intervals. In order to detect change points, we need to know if there are abrupt changes between two consecutive differences. To do this, one more AR model is fit to the difference-based time series and a new sequence of probability density functions { _qt_: _t =_ 1, 2, … } is constructed. The change-point score is defined using aforementioned score function. A higher score indicates a higher possibility of being a change point.

Since these methods rely on pre-designed parametric models and they are less flexible in real-world change point detection scenarios, some recent studies introduce more flexible non-parametric variations by estimating the ratio of probability densities directly without needing to perform density estimation. The rationale of this density-ratio estimation idea is that knowing the two densities implies knowing the density ratio. However, the inverse is not true: knowing the ratio does not necessarily imply knowing the two densities because such decomposition is not unique. Thus, direct density-ratio estimation is substantially simpler than density estimation. Following this idea, methods of direct density-ratio estimation have been developed \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\]\[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\]. These methods model the density ratio between two consequent intervals _χ_ and _χ′_ by a non-parametric Gaussian kernel model as follows:

|     |
| --- |
| g(X)=p(X)p′(X′)=∑l=1nθlK(X,Xl)K(X,X′)=exp(-‖X-X′‖22σ2) |

Where _p_( _χ_) is the probability distribution of interval _χ_, _θ =_ ( _θ_ 1, … , _θn_) _T_ are parameters to be learned from data samples, _X_ is a sliding window, and _σ >_ 0 is the kernel parameter. In the training phase, the parameters _θ_ are determined so that the dissimilarity measure is minimized. Given a density-ratio estimator _g_( _χ_), an approximator of the dissimilarity measure between two samples _χt_ and _χt_ + _n_ is calculated in the test phase. The higher the dissimilarity measure is, the more likely the point is a change point \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\]\[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\].

A popular choice for the dissimilarity measure is Kullback-Leibler (KL) divergence:

|     |
| --- |
| KL\[p(x)‖p′(x)\]=-∫p′(x)logp(x)p′(x)dx |

The Kullback-Leibler importance estimation procedure (KLIEP) estimates the density ratio using KL divergence. This problem is a convex optimization problem, so the unique global optimal solution _θ_ can be simply obtained, for example, by a gradient projection method. Projected gradient descent moves in the direction of the negative gradient at each step and projects onto the feasible parameter. The resulting approximation of KL divergence is given in the following equation \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\]\[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\].

|     |
| --- |
| KL^=1n∑i=1nlogg^(Yi) |

Another direct density ratio estimator is uLSIF (Unconstrained Least-Squares Importance Fitting) which uses Pearson (PE) divergence as a dissimilarity measure, shown as:

|     |
| --- |
| PE\[p(x)‖p′(x)\]=∫p′(x)(p(x)p′(x)-1)2dx |

As part of the uLSIF training criterion, the density-ratio model is fitted to the true density ratio under the squared loss. An approximator of the PE divergence is as follows \[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\]:

|     |
| --- |
| PE^=-12n∑j=1ng^(Yj′)2+1n∑i=1ng^(Yi)-12 |

Depending on the condition of the second interval density _p′_ ( _x_), the density-ratio value can be unbounded. To overcome this problem, _α_ -relative PE divergence for 0 _≤ α <_ 1 is used as a dissimilarity measure in an approach known as Relative uLSIF (RuLSIF). The RuLSIF measure is:

|     |
| --- |
| PEα\[p(x)‖p′(x)\]=PE(p(x)‖αp(x)+(1-α)p′(x)) |

The _α_-relative density ratio is reduced to a plain density ratio if _α =_ 0, and it tends to be “smoother” as _α_ gets larger. The novelty of RuLSIF is that it is always bounded above by
1α, and it has been shown that the convergence rate for estimating the relative density ratio is faster than that of the uLSIF \[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\]\[ [46](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R46)\].

Recently, a Semi-Parametric Log-Likelihood Change Detector (SPLL) \[ [47](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R47)\]\[ [48](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R48)\]\[ [49](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R49)\] was proposed as a semi-parametric change detector based on Kullback-Leibler statistics. Suppose that the data before the change point (window _W_ 1) come from a Gaussian mixture, _p_ 1( _x_). The change detection criterion is derived using an upper bound of the log-likelihood of the data in the second window, _W_ 2 using the index of the component with the smallest squared Mahalanobis distance between x and its center. If _W_ 2 does not come from the same distribution of _W_ 1, then the mean of the distances will deviate from _n_ (where _n_ is the dimensionality of the feature space). A value of SPLL that is larger or smaller than a specified range will indicate a change. It is important to note that the accuracy of all of these estimation methods is degraded by data noise \[ [46](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R46)\].

#### 3.2.2 Subspace Model Methods

Another line of research bases change point detection on an analysis of subspaces in which time series sequences are constrained. This approach has a strong connection with a system identification method, which has been thoroughly studied in the area of control theory \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\].

One such subspace model method is called subspace identification (SI) \[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\]\[ [50](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R50)\]. SI is based on a state space model of the system which also explicitly considers a noise factor.

|     |
| --- |
| x(t+1)=Ax(t)+Ke(t)y(t)=Cx(t)+e(t) |

Here _C_ and _A_ are system matrices, _e_( _t_) represents system noise and _K_ is the stationary Kalman gain. We are using different notation in subspace methods. Since in these methods x represents model states, we use _y_ as time series.

In system identification, an extended observability matrix is a measure for how well internal states ( _x_( _t_)) of a system can be inferred by knowledge of its external outputs, ( _y_( _t_)). Here we use the extended observability matrix as a representation of a subspace in which time series data are constrained.

An extended observability matrix is defined as:

|     |
| --- |
| Ok=\[CT(CA)T…(CAk-1)T\] |

For each interval as described in Section 2.1, SI estimates the observability matrix using LQ factorization and Singular Value Decomposition (SVD) of the normalized conditional covariance. LQ factorization is the orthogonal decomposition of a matrix into lower trapezoidal matrices. The SVD of a matrix _A_ is the factorization of _A_ into the product of three matrices _A = UDVT_ where the columns of _U_ and _V_ are orthonormal and the matrix _D_ is diagonal with positive real entries. In the next step, the gap between subspaces is calculated and utilized as a measure of the change in the time series sequence. This measure of change, _D_, can be compared to a specified threshold to determine if the current point is a change point.

|     |
| --- |
| D=XTX-XTUUTX |

Here _χ_ represents the Hankel matrix of the new interval and _U_ is calculated by the SVD of the estimated extended observability matrix for the previous interval.

The next subspace model method we will discuss is called a Singular Spectrum Transformation (SST) \[ [11](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R11)\]\[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\] \[ [30](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R30)\], which is also based on a state space model. Unlike the SI model, however, it does not consider the system noise. SST will define a trajectory matrix based on an explained Hankel matrix for each window as shown in the following equation:

|     |
| --- |
| X=(y1y2⋯yKy2y3⋯yK+1⋮⋮⋱⋮yLyL+1⋯yN) |

where _L_ is the window length and _K_ is the number of windows. The trajectory matrix can be decomposed into submatrices using SVD. These submatrices consist of singular value empirical orthogonal functions, or EOF functions, and principal components. Distance-based change point scores are defined by a comparison between singular spectrums of two trajectory matrices for consecutive intervals.

Although both of these subspace model methods are based on a predefined model, SST does not consider the effect of noise on the system. As a result, it is more sensitive than SI to choices of parameter values and has demonstrated lower accuracies for some datasets \[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\]\[ [50](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R50)\].

#### 3.2.3 Probabilistic Methods

Early Bayesian approaches to change point detection were offline ( _∞_ – real time) and were based on retrospective segmentation \[ [51](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R51)\]\[ [52](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R52)\]. One of the first approaches to online Bayesian change point detection (BCPD) was introduced under the assumption that a sequence of observations may be divided into non-overlapping states partitions and the data within each state _ρ_ in time series are i.i.d. from some probability distribution _P_( _xt_ \| _ηρ_) \[ [31](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R31)\].

Compared to the previous methods which only consider pairs of consecutive samples, BCPD compares new sliding window features with the estimation based on all previous intervals from the same state. BCPD estimates the posterior distribution by defining an auxiliary variable _run-length_ ( _rt_) which represents the time that elapsed since the last change point. Given the run length at a time instant _t_, the run length at the next time point can either reset back to 0 (if a change point occurs at this time) or increase by 1 (if the current state continues for one more time unit). The run length distribution based on Bayes’ theorem can be denoted as:

|     |
| --- |
| P(rt∣x1:t)=∑rt-1P(rt∣rt-1)P(xt∣rt-1,xt(r))P(rt-1,x1:t-1)∑rtP(rt,x1:t) |

Where
xt(r) indicates the set of observations associated with the run _rt_ and _P_( _rt_ \| _rt_–1),
P(xt∣rt-1,xt(r)), and _P_( _rt_–1, _x_ 1: _t_–1) are prior, likelihood, and recursive components of the equation. The conditional prior is nonzero at only two outcomes ( _rt =_ 0 _or rt = rt_–1 \+ 1) and simplifies the equation.

|     |
| --- |
| P(rt∣rt-1)={H(rt-1+1)ifrt=01-H(rt-1+1)ifrt=rt-1+les, BCPD compares new sliding window features with the estimation based on all previous intervals from the same state. BCPD estimates the posterior distribution by defining an auxiliary variable _run-length_ ( _rt_) which represents the time that elapsed since the last change point. Given the run length at a time instant _t_, the run length at the next time point can either reset back to 0 (if a change point occurs at this time) or increase by 1 (if the current state continues for one more time unit). The run length distribution based on Bayes’ theorem can be denoted as:

|     |
| --- |
| 𝑃⁡(𝑟𝑡∣𝑥1:𝑡)=∑𝑟𝑡−1𝑃⁡(𝑟𝑡∣𝑟𝑡−1)⁢𝑃⁡(𝑥𝑡∣𝑟𝑡−1,𝑥(𝑟)𝑡)⁢𝑃⁡(𝑟𝑡−1,𝑥1:𝑡−1)∑𝑟𝑡𝑃⁡(𝑟𝑡,𝑥1:𝑡) |

Where
𝑥(𝑟)𝑡 indicates the set of observations associated with the run _rt_ and _P_( _rt_ \| _rt_–1),
𝑃⁡(𝑥𝑡∣𝑟𝑡−1,𝑥(𝑟)𝑡), and _P_( _rt_–1, _x_ 1: _t_–1) are prior, likelihood, and recursive components of the equation. The conditional prior is nonzero at only two outcomes ( _rt =_ 0 _or rt = rt_–1 \+ 1) and simplifies the equation.

|     |
| --- |
| 𝑃⁡(𝑟𝑡∣𝑟𝑡−1)=⎧{<br>{⎨{<br>{⎩𝐻⁡(𝑟𝑡−1+1)𝑖⁢𝑓⁡𝑟𝑡=01−𝐻⁡(𝑟𝑡−1+1)𝑖⁢𝑓⁡𝑟𝑡=𝑟𝑡−1+10𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒 |

In this equation,
𝐻⁡(𝜏)=𝑃⁡(𝜏)∑∞𝑡=𝜏𝑃⁡(𝑡) is a hazard function which is defined as the ratio of probability density over the run to the total value of probability densities \[ [31](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R31)\]\[ [53](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R53)\]\[ [54](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R54)\]. The likelihood term represents the probability that the most recent datum belongs to current run. This is the most challenging term to calculate and it tends to be most computationally efficient when a conjugate exponential model is used \[ [31](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R31)\].

After calculating the run length distribution and updating the corresponding statistics, change point prediction is performed by comparing probability values. If _rt_ has the highest probability in the distribution, then a change point has occurred and the run length is reset to _rt =_ 0\. If not, the run length is incremented by one, _rt = rt_–1 \+ 1 \[ [31](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R31)\]\[ [53](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R53)\].

This method was later extended to the general case of non i.i.d time series by incorporating the likelihood of different subsequences of data in the equations. In addition, a simplification was introduced that reduces the algorithm complexity from _n_ 2 to _n_ using a simple approximation. The key idea is to compute the joint probability weights for only a fixed number of nodes, instead of computing these weights at all
𝑛⁢(𝑛−1)2 nodes \[ [7](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R7)\].

A Gaussian Process (GP) represents another probabilistic method for stationary time series analysis and prediction \[ [55](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R55)\]. A GP is a generalization of a Gaussian distribution and is defined as a collection of random variables, any finite number of which have a joint Gaussian distribution \[ [56](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R56)\]\[ [57](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R57)\]. In this method, time series observations { _xt_} are defined as a noisy version of Gaussian distribution function values _f_( _t_).

|     |
| --- |
| 𝑥𝑡=𝑓⁡(𝑡)+𝜀𝑡 |

In this Gaussian distribution function, _εt_ is a noise term, usually assumed to be a Gaussian noise term
𝒩⁡(0,𝜎2𝑛) and _f_( _t_) _= 𝒢℘_(0, _K_) is a GP distribution function specified by mean zero and covariance function _K_. Typically, a covariance function is specified using a set of hyper-parameters. A widely used covariance function is:

|     |
| --- |
| 𝐾⁡(𝑡1,𝑡2)=𝜎2⁢𝑒𝑥𝑝⁡(−(𝑡1−𝑡2)22⁢𝑙2) |

Given a time series, the GP function can be used to make a normal distribution prediction at time _t_. The GP Change algorithm uses a Gaussian process to estimate the predictive distribution at time _t_ using observations available through time ( _t_ − 1). The algorithm then computes the p-value for the actual observation _yt_ under the reference distribution,
𝒩⁡(̂𝑦𝑡,̂𝜎2𝑡). A threshold _α_ ∈ (0,1) is used to determine when the actual observation does not follow the predictive distribution, which is indicative of a possible state change (and thus a change point) \[ [56](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R56)\]. Using observations available through time _t–1_ to detect change points instead of using only observations from the last state makes the GP method more complicated and yet more accurate than BCPD.

#### 3.2.4 Kernel Based Methods

Although kernel-based methods are typically utilized as supervised learning techniques, some studies use an unsupervised kernel-based test statistic to test the homogeneity of data in time series past and present sliding windows. These methods map the observations in a reproducing kernel Hilbert space (RKHS) _ℋ_ associated with a reproducing kernel _k_(. , . ) and a feature map Φ( _X_) _= k_( _X_, . ) \[ [58](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R58)\]. They then use a test statistic based upon the kernel Fisher discriminant ratio as a measure of homogeneity between windows.

Considering two windows of observations, the empirical mean elements and covariance operators for sample _X_ with length _n_ are calculated as:

|     |
| --- |
| ̂𝜇=1𝑛⁢∑𝑛𝑙=1𝑘⁡(𝑋𝑙,.)̂∑=1𝑛⁢∑𝑛𝑙=1{𝑘⁡(𝑋𝑙,.)−̂𝜇}⊗{𝑘⁡(𝑋𝑙,.)−̂𝜇} |

where the tensor product operator _u_ ⊗ _v_ for all function _f_ ∈ _ℋ_ is defined as ( _u_ ⊗ _v_) _f =_ 〈 _v_, _f_〉 _ℋu_. Now the kernel Fisher discriminant ratio (KFDR) between two samples is defined as \[ [58](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R58)\]\[ [24](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R24)\]:

|     |
| --- |
| 𝐾𝐹𝐷𝑅⁡(𝑋𝑙𝑒𝑛𝑔𝑡ℎ𝑛11,𝑋𝑙𝑒𝑛𝑔𝑡ℎ𝑛22)=𝑛1⁢𝑛2𝑛1+𝑛2⁢〈̂𝜇2−̂𝜇1,(̂∑𝑤+𝛾⁢𝐼)−1⁢(̂𝜇2−̂𝜇1)〉ℋ |

where _γ_ is a regularization parameter and

|     |
| --- |
| ̂∑𝑤=𝑛1𝑛1+𝑛2⁢̂∑1+𝑛2𝑛1+𝑛2⁢̂∑2. |

The easiest way to determine whether a change point exists between two windows is comparing the KFDR ratio with a threshold value \[ [58](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R58)\]. The other method known as running maximum partition strategy \[ [24](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R24)\] calculates the KFDR ratio between all consequent windows in each interval. Then the maximum ratio will be compared to threshold to detect change point.

A common drawback for kernel-based methods is that they rely heavily on the choice of the kernel function and its parameters, and the problem becomes more severe when the data are in moderate to high dimensional spaces \[ [23](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R23)\].

#### 3.2.5 Graph Based Methods

Several recent studies showed time series can be investigated using graph theory tools. The graph is usually derived from a distance or a generalized dissimilarity on the sample space, with time series observations as nodes and edges connecting observations based on their distance. This graph can be defined based on a minimum spanning tree \[ [59](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R59)\], minimum distance pairing \[ [60](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R60)\], nearest neighbor graph \[ [59](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R59)\]\[ [60](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R60)\], or visibility graph \[ [61](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R61)\]\[ [62](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R62)\].

A graph based framework for change point detection is a nonparametric approach that applies a two sample test on an equivalent graph to find whether there is a change point within the observations or not. In this method graph _G_ is constructed for each sequence of data. Each possible value of _τ_ as change point time divides the observations into two windows: observations that come before _τ_ and observations that come after _τ_. The number of edges in the graph G ( _RG_) that connects observations from these two windows is used as an indicator of a change point, so that smaller edges increase the possibility of change point. Since the value of _RG_ depends on time _t_, the standardized function ( _ZG_) is defined as:

|     |
| --- |
| 𝑍𝐺⁡(𝑡)=−𝑅𝐺⁡(𝑡)−𝐸⁡\[𝑅𝐺⁡(𝑡)\]√𝑉𝐴𝑅⁡\[𝑅𝐺⁡(𝑡)\] |

where _E_\[. \] and _VAR_\[. \] are Expectation and Variance, respectively. The maximum value of _ZG_ among all data points in the graph is identified as a candidate change point. The change point is accepted if the maxima is greater than a specified threshold \[ [23](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R23)\]. This method is powerful for high dimensional data with fewer parameter assumptions. However, it does not utilize much information from the time series observations themselves, instead relying on defining an appropriate graph structure.

#### 3.2.6 Clustering Methods

From a different perspective, the problem of change point detection can be considered as a clustering problem with a known or unknown number of clusters, such that observations within clusters are identically distributed, and observations between adjacent clusters are not. If a data point at time stamp _t_ belongs to a different cluster than the data point at time stamp _t+1_, then a change point occurs between the two observations.

One clustering approach used for change point detection combines sliding window and bottom up methods into an algorithm called SWAB (Sliding Window and Bottom-up) \[ [63](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R63)\]. The original bottom-up approach first treats each data point as a separate subsequence, then merges subsequences with an associate merge cost until the stopping criteria is met. In contrast, SWAB maintains a buffer of size _w_ to store enough data for 5 – 6 subsequences. The bottom-up method is applied to the data in the buffer and the leftmost resulting subsequence is reported. The data corresponding to the reported subsequence are removed from the buffer and replaced with the next data in the series.

A second clustering approach groups subsequences based on Minimum Description Length \[ [32](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R32)\]. The description length _DL_ of a time series _T_ of length _m_ is the total number of bits that are required to represent the series, or:

|     |
| --- |
| 𝐷⁢𝐿⁡(𝑇)=𝑚∗𝐻⁡(𝑇) |

where _H_( _T_) is the entropy of the time series.

MDL-based change point detection is a bottom-up greedy search over the space of clusters which can include subsequences of different lengths and does not require the number of clusters to be specified. This method clusters enumerated motifs instead of all the subsequences.

After finding time series motifs, three search operators are applied: create (create a new cluster), add (add a subsequence to an existing cluster), and merge (merge two clusters). The value of _bitsave_ represents the total number of bits that are saved by applying one of these operators to the time series.

|     |
| --- |
| 𝑏𝑖𝑡𝑠𝑎𝑣𝑒=𝐷⁢𝐿⁡(𝐵𝑒𝑓𝑜𝑟𝑒)−𝐷⁢𝐿⁡(𝐴𝑓𝑡𝑒𝑟) |

The _bitsave_ for each operator is defined as the following:

1. Creating a new cluster C from subsequences A and B


|     |
| --- |
| 𝑏𝑖𝑡𝑠𝑎𝑣𝑒=𝐷⁢𝐿⁡(𝐴)+𝐷⁢𝐿⁡(𝐵)−𝐷𝐿𝐶⁡(𝐶) |



_DLC_( _C_) is the number of bits needed to represent all subsequences in cluster C.

2. Adding a subsequence A to an existing cluster C


|     |
| --- |
| 𝑏𝑖𝑡𝑠𝑎𝑣𝑒=𝐷⁢𝐿⁡(𝐴)+𝐷𝐿𝐶⁡(𝐶)−𝐷𝐿𝐶⁡(𝐶′) |



C′ is the cluster C after including subsequence A.

3. Merging cluster C1 and C2 to a new cluster C


|     |
| --- |
| 𝑏𝑖𝑡𝑠𝑎𝑣𝑒=𝐷𝐿𝐶⁡(𝐶1)+𝐷𝐿𝐶⁡(𝐶2)−𝐷𝐿𝐶⁡(𝐶) |


The first step creates a new cluster from the motifs and the number of bits saved using this step is calculated. In the next stage of the algorithm, there are two operators available: create or add. The new subsequence can be added to one of the existing clusters or it can be assigned as the only member of a newly-created cluster. To add a subsequence into an existing cluster, the distance between the subsequence and each cluster is calculated to find the cluster nearest to the subsequence. After the search, the nearest cluster is updated to include the subsequence, the number of bits saved is calculated, and the clusters are recorded. After each step, any pair of clusters is allowed to merge if it maximally decreases the description length (increases bitsave). Since the MDL technique requires discrete data, this method is applicable to discretized time series values.

Another way to cluster time series data as a way to find change points using a Shapelet method \[ [64](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R64)\]. An unsupervised-shapelet, or u-shapelet _S_, is a small pattern in a time series _T_ for which the distance between _S_ and part of time series is much smaller than the distance between _S_ and the rest of the time series. Shapelet-based clustering, which attempts to cluster the data based on the shape of the entire time series, searches for a u-shapelet which can separate and remove a time series subsequence from the rest of the dataset. The algorithm iteratively repeats this search among the remaining data until no data remains to be separated. A greedy search algorithm which attempts to maximize the separation gap between two subsets of data is used to extract u-shapelets. Then any clustering algorithm such as k-means with a Euclidian distance function can be used to cluster the time series and find change points.

Yet another time series clustering approach is Model fitting, in which a change can be considered to occur when a new data item or block of data items do not fit into any of the existing clusters \[ [17](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R17)\]. Assuming a data stream { _x_ 1, … , _xi_, … }, change point is occurred after data point _xi_, if the following logical expression is true.

|     |
| --- |
| 𝑐ℎ𝑎𝑛𝑔𝑒=⋀𝑘𝑗=1\[𝑑⁡(𝑥𝑖+1,𝑐𝑒𝑛𝑡𝑒𝑟⁡(𝐶𝑗))>𝑟𝑎𝑑𝑖𝑢𝑠⁡(𝐶𝑗)\] |

where _d_ ( _xi_ +1, _center_( _Cj_)) is the Euclidian distance between a newly-incoming data point _xi_ +1 and the center of cluster _Cj_, _radius_( _Cj_) is the radius of cluster j, _K_ is the number of clusters, and ^ is the logical and symbol. The radius of cluster _C_ with n data point and mean value of _μ_ is:

|     |
| --- |
| 𝑟𝑎𝑑𝑖𝑢𝑠⁡(𝐶)=√∑𝑛𝑖=1(𝑥𝑖−𝜇)2𝑛 |

## 4\. DISCUSSION AND COMPARISON

The previous sections present an overview of change point detection algorithms that are commonly used in the literature. Choosing the most appropriate algorithm a particular dataset depends on which criterion is most important for the application. Here, we compare CPD methods based on several frequently-used criteria.

### 4.1 Online vs Offline

One important criteria for change point detection is the ability to identify the change point in real time or near-real time. The complete offline algorithms are applicable when processing an entire time series at once, and _ε_ –real time algorithms need to look at least _ε_ data points ahead of the candidate change point. The value of _ε_ depends on the nature of the algorithm and amount of input data that is required for each step. Online algorithms process data within a sliding window with size _n_. For these approaches, _n_ should be large enough to store the data that is necessary to represent the time series state yet small enough to still meet the epsilon requirement.

##### Supervised methods

Once they process enough training data, these methods will predict if there is a CP in the current window. Therefore we can state that supervised techniques are _n_-real time.

##### Likelihood ratio methods

These methods are based on comparing probability densities between two consequent intervals. When a new retrospective subsequence comes the new calculation will return the result so we can say these methods are _n+k_-real time.

##### Subspace Model

New intervals in these techniques are calculated in the same manner as for likelihood methods. As a result, these methods are also _n+k_-real time.

##### Probabilistic Methods

These methods rely only upon a single sliding window for detecting CP, so they are _n_-real time.

##### Kernel Based Methods

Unsupervised kernel methods are based on sliding windows. However, as with the likelihood ratio methods these need a retrospective subsequence of data, so they are _n+k_-real time.

##### Clustering

The SWAB technique is a combination of sliding window and bottom up. SWAB maintains a buffer of size _w_. Bottom-up is applied to the data in the buffer and the leftmost subsequence is reported. As a result, SWAB is _w_-real time. MDL-based methods and Shapelet-based methods need to access the entire time series at once, so they are offline or infinity-real time. The model fitting technique depends on a single window and therefore is _n_-real time.

##### Graph Based Method

This technique derives a graph from a single window. A change point is reported if it exists within the current window, thus the method is _n_-real time.

[Figure 5](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#F5) visualizes the relationship between the alternative CPD approaches and their point on the continuum between complete offline and online processing.

###### Figure 5.

[![Figure 5](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/de75/5464762/ab1adee8cbe8/nihms860556f5.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5464762_nihms860556f5.jpg)

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/figure/F5/)

Offline vs. online CPD algorithm comparison.

### 4.2 Scalability

A second important criteria is the computational cost of change point detection algorithms. The computational cost of the algorithms we survey, where available, are compared in [Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#T2). Where authors do not provide this information, the comparison has been performed qualitatively based on algorithmic descriptions. In general, as the dimension of the time series increases the nonparametric methods gain power in computational cost and will be less expensive than parametric methods. It is very hard to characterize the cost of supervised methods because there are two complexities involved. These are at the run time of the training stage and the run time of the CP detection stage.

#### Table 2.

Comparison of CPD algorithm scalability based on sliding window size _n_. \\* = estimate based on algorithm.

| Category | Method | Parametric/Non Parametric | Computational Cost |
| :-: | :-: | :-: | :-: |
| Probability Density Ratio | CUSUM | Parametric | O(n2)\* |
| AR | Parametric | O(n3)\* |
| KLIEP | Non Parametric | KLIEP< CUSUM ; KLIEP < AR |
| uLSIF | Non Parametric | uLSIF < KLIEP |
| RuLSIF | Non Parametric | RuLSIF < uLSIF |
| SPLL | Semi Parametric | O(n2)\* |
| Subspace Models | SI | Parametric | SI > KLIEP |
| SST | Parametric | SST > KLIEP |
| Probabilistic Method | Bayesian | Parametric | O( _n_) |
| GP | Non Parametric | O(n2) |
| Kernel Based Methods | KcpA | Non Parametric | O(n3) |
| Clustering | SWAB |  | O(L _n_) |
| MDL |  |  |
| Shapelet |  |  |
| Model Fitting |  |  |
| Graph Based Methods |  | Non Parametric |  |
| Multi-Class Classifier | Nearest Neighbor | Non Parametric | = Cost (Training + CP detection) |
| HMM | Parametric |
| GMM | Parametric |
| Binary Class Classifier | SVM | Parametric |
| Naive Bayes | Parametric |
| Logistic Regression | Parametric |

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/table/T2/)

To the best of our knowledge no existing CPD algorithm provides an interruptible or contract anytime option. This can be considered an avenue for future research.

### 4.3 Learning Constraint

Most of the likelihood ratio methods (except SPLL) and all of the subspace model techniques originally were designed for one-dimensional time series. Thus in the case of a _d_-dimensional time series, these methods merge all of the dimensions together and generate a one-dimensional series with a _d_-size value vector. Although there is no constraint on time series dimensionality for the other algorithms, increasing the number of dimensions will increase the algorithm’s computational cost.

All of the algorithms accept both discrete and continuous time series input. One exception is the MDL-based method, which work only with discrete input values.

The supervised learning approaches to CPD operate under the assumption that a transition period can be detected independent of the current time series state. In contrast, the unsupervised learning algorithm operates under the assumption that the distribution of time series data changes before and after each change point \[ [21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R21)\]. While the supervised data frequently outperform unsupervised methods in detecting change points, they depend on sufficient quality and quantity of training data, which is not always accessible for real world data. The multi-class supervised algorithms are the only group that needs to know the number of possible time series states.

In general, non-parametric CPD methods are more robust than parametric ones because the parametric methods rely heavily on the choice of parameters. In addition, the CPD problem becomes more complex for parametric methods when the data has moderate to high dimensionality.

Most unsupervised CPD algorithms operate on limited types of time series data. Some of them are only work for stationary or i.i.d. datasets and others offer parametric versions for non-stationary time series datasets. The corresponding parametric versions use a forgetting factor to remove the effects of older observations. [Table 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#T3) summarizes these limitations for the methods that we survey.

#### Table 3.

Comparison of CPD algorithm limitations.

| Category | Method | Time Series Limitation |
| :-: | :-: | :-: |
| Probability Density Ratio | CUSUM | No Limitation |
| AR | No Limitation |
| KLIEP | The parametric version should be used in case of non-stationary time series |
| uLSIF | The parametric version should be used in case of non-stationary time series |
| RuLSIF | The parametric version should be used in case of non-stationary time series |
| SPLL | Time Series should be i.i.d. |
| Subspace Models | SI | The parametric version should be used in case of non-stationary time series |
| SST | Time Series should be Stationary |
| Probabilistic Method | Bayesian | The original method works only for i.i.d. time series<br>Extended version works for non-i.i.d time series |
| GP | Time Series should be Stationary |
| Kernel Based Methods | KcpA | Time Series should be i.i.d. |
| Clustering | SWAB | No Limitation |
| MDL | No Limitation |
| Shapelet | No Limitation |
| Model Fitting | No Limitation |
| Graph Based Methods |  | Time Series should be i.i.d. |
| Multi-Class Classifier | Nearest Neighbor | No Limitation |
| HMM | No Limitation |
| GMM | No Limitation |
| Binary Class Classifier | SVM | No Limitation |
| Naive Bayes | No Limitation |
| Logistic Regression | No Limitation |

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/table/T3/)

### 4.4 Performance Evaluation

Several artificial and real-world datasets have been used to measure the performance of CPD algorithms. It is important to notice that an objective comparison of the performance of different CPD methods is very difficult due to the use of these different datasets. Here we try to describe some popular benchmark real-world time series datasets and to compare the reported performance of different CPD methods on these datasets.

A majority of the studies do not provide any comparisons, or in some cases, even measures of performance. For example, there are no available results for the SPLL and clustering methods. Similarly, experimental results for graph-based CPD are available only for different graph structures, to demonstrate the fact that accuracy highly depends on the structure of the graph \[ [23](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R23)\]. Studies that include performance analyses tend to calculate the distance between actual and detected CPs and use discrete metrics like accuracy, precision, and recall to evaluate the algorithms. [Table 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#T4) summarizes reported performance from previous studies using the following data sets:

#### Table 4.

Comparison of CPD algorithm performance based on accuracy (Acc), recall (Rec), Precision (Prec), Error (Err), and Area Under the ROC Curve (AUC).

| Method | Dataset 1 \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\] \[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\] | Dataset 2 \[ [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R2)\]\[ [63](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R63)\]\[ [50](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R50)\] | Dataset 3 \[ [58](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R58)\] | Dataset 4 \[ [24](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R24)\] | Dataset 5 \[ [26](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R26)\] | Dataset 6 \[ [21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R21)\] | Dataset 7 \[ [22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R22)\] |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **CUSUM** |  |  |  |  | Acc = 0.75<br>Rec. = 0.75<br>Prec. = 0.75 |  |  |
| **AR** | AUC = 0.79<br>Acc = 0.36 | Acc = 0.23 |  |  |  |  | AUC = 0.85 |
| **KLIEP** | AUC = 0.63<br>Acc = 0.43 | Acc = 0.49 |  |  |  |  | AUC = 0.90 |
| **uLSIF** | AUC = 0.86 |  |  |  |  |  | AUC = 0.90 |
| **RuLSIF** | AUC = 0.94 |  |  |  |  | AUC = 0.89 | AUC = 0.97 |
| **SI** | AUC = 0.76<br>Acc = 0.39 | Acc = 0.47 |  |  |  |  | AUC = 0.94 |
| **SST** | AUC = 0.76<br>Acc = 0.44 | Acc = 0.46 |  |  |  |  | AUC = 0.87 |
| **Bayesian** |  |  |  |  | Acc = 0.50 |  |  |
| **GP** |  |  |  |  | Acc = 78<br>Rec. = 0.75<br>Prec. = 0.82 |  |  |
| **Kernel** |  |  | Prec. = 0.89<br>Rec. =0. 90 | Acc = 0.79 ; 0.74;<br>0.61 |  |  |  |
| **SWAB** |  | Max Err < 0.4 |  |  |  |  |  |
| **B HMM** |  |  | Prec. = 0.93<br>Rec. =0. 96 |  |  |  |  |
| **M SVM** |  |  |  | Acc = 0.76 ; 0.69; 0.60 |  | AUC = 0.85 |  |
| **M Naive Bayes** |  |  |  |  |  | AUC = 0.78 |  |
| **M Logistic Regression** |  |  |  |  |  | AUC = 0.92 |  |

[Open in a new tab](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/table/T4/)

##### Dataset 1: Speech recognition

This is the IPSJ SIG-SLP Corpora and Environments for Noisy Speech Recognition (CENSREC) dataset provided by the National Institute of Informatics (NII) \[ [65](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R65)\]. This dataset records a human voice in a noisy environment. The task is to extract speech sections from recorded signals.

##### Dataset 2: ECG

This is a respiration dataset found in the UCR Time Series Data Mining Archive \[ [66](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R66)\]. This dataset records patients’ respiration measured by thorax extension as they wake up. The series is manually segmented by a medical expert.

##### Dataset 3: Speech recognition

This dataset represents soundtracks from popular French 1980s entertainment TV shows (“Le Grand ‘Echiquier”). The dataset comprises roughly three hours of sound track data.

##### Dataset 4: Brain-Computer Interface Data

Signals acquired during these Brain-Computer Interface (BCI) trial experiments naturally exhibit temporal structure. The corresponding dataset formed the basis of the BCI competition III. Data are acquired during four non-feedback sessions on three normal subjects where each subject was asked to perform different tasks, where time when the subject switches from one task to another are random.

##### Dataset 5: Iowa Crop Biomass NDVI Data

The NDVI time series data was available as a data product for years 2001 to 2006. In this dataset, observations were made for every sixteen days.

##### Dataset 6: Smart Home Data

This data represents sensor readings collected in a smart apartment located on the on WSU campus \[ [67](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R67)\]. The apartment is equipped with infrared motion / ambient light sensors, door / ambient temperature sensors, light switch sensors, and power usage sensors. The data is labeled with corresponding human activities and changes naturally occur between the activities.

##### Dataset 7: Human activity dataset

This is a subset of the Human Activity Sensing Consortium \[ [68](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R68)\] challenge 2011, which provides human activity information collected by portable three-axis accelerometers. The task of change-point detection is to segment the time-series data according to the six behaviors: “stay”, “walk”, “jog”, “skip”, “stair up”, and “stair down”.

In summary, we note that supervised methods tend to be more accurate than unsupervised methods if enough training data exist and the series is stationary. If these conditions are not met, the unsupervised methods are more useful. There is no comprehensive performance comparison among unsupervised methods, but it can be seen from experimental results that RulSIF consistently yields strong accuracy. Because kernel-based methods, subspace models, CUSUM, AR, and clustering methods rely upon parameters to model time series dynamics, they do not exhibit good performance for noisy data, or highly dynamic systems.

Most unsupervised algorithms place constraints on the types of time series methods that can be processed. One notable exception to this is the AR method. In addition, some of these methods have parametric versions for non-stationary data, which makes them sensitive to the choice of parameters. For high-dimension time series data, the likelihood ratio and subspace models are not the best choices, because they cannot directly handle multidimensional data. In this case, graph-based or probabilistic methods are more promising.

## 5\. CONCLUSIONS AND CHALLENGES FOR FUTURE WORK

In this survey, we presented the state of the art in change point detection methods, analyzed their advantages and disadvantages, and summarized challenges that arise for change point detection. Both supervised and supervised method were used in literature to detect changes in time series. Although CPD algorithms have progressed significantly in the last decade, there are still many open challenges.

One important issue for CPD algorithms relates to the need for online algorithms and the detection delay for many existing approaches. In many real world applications, change points are used selecting and executing timely actions, thus finding the change points as soon as possible is crucial. Anytime algorithms can potentially be used to compensate for algorithm delays and adjust the computational time in balance with the quality of the detected change points. Another alternative is to employ methods that need smaller window sizes to calculate change point scores, such as Bayesian methods.

Another open problem is algorithm robustness. Although some discussion does exist about this point and generally non parametric methods are more robust than parametric ones, there is no formal analysis of robustness found in the literature. Finally, for almost all of the methods change detection depends on the window size. Although small windows would detect more local changes compared to large windows, it cannot look ahead of data and will increase cost. Incorporating variable window sizes may provide a good solution to using the best window length for each subsequence.

In many real world data analysis problems, however, the problem of change detection by itself is not of particular interest. For example, a climate change researcher may be interested in finding the amount of change in temperature instead of just detecting that a change occurred. Here, the main interest is the detailed information about the amount and source of change. Some of the existing techniques we surveyed provide information about the amount or source of change, but further work is needed to develop more accurate change analysis or change estimation algorithms. Calculating dissimilarity measures for each feature whenever a change occurs represents one possible solution for finding the change source and the total dissimilarity measure can then be used to conduct a change estimation.

Evaluating the significance of the detected change point is another important open issue for unsupervised methods. Currently, most existing methods compare detect change scores with a threshold value to determine whether change occurs or not. Selecting the optimal threshold value is difficult. These values may be application dependent and they may change over time. Developing statistical method to find significant change point based on previous values may offer greater autonomy and reliability.

Finally, an ongoing challenge for CPD is to handle non-stationary time series. Literature does exist for detecting concept drift, which can be utilized to help with this issue \[ [69](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R69)\]\[ [70](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/#R70)\]. Blending change point detection with concept drift detection is a challenging but important problem, because many real-world datasets are non-stationary and multi-dimensional.

## References

- 1.Montanez GD, Amizadeh S, Laptev N. Inertial Hidden Markov Models: Modeling Change in Multivariate Time Series. AAAI Conference on Artificial Intelligence. 2015:1819–1825. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=AAAI%20Conference%20on%20Artificial%20Intelligence&title=Inertial%20Hidden%20Markov%20Models:%20Modeling%20Change%20in%20Multivariate%20Time%20Series&author=GD%20Montanez&author=S%20Amizadeh&author=N%20Laptev&publication_year=2015&pages=1819-1825&)\]
- 2.Kawahara Y, Sugiyama M. Sequential Change-Point Detection Based on Direct Density-Ratio Estimation. SIAM International Conference on Data Mining. 2009:389–400. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=SIAM%20International%20Conference%20on%20Data%20Mining&title=Sequential%20Change-Point%20Detection%20Based%20on%20Direct%20Density-Ratio%20Estimation&author=Y%20Kawahara&author=M%20Sugiyama&publication_year=2009&pages=389-400&)\]
- 3.Boettcher M. Contrast and change mining. Wiley Interdiscip Rev Data Min Knowl Discov. 2011 May;1(3):215–230. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Wiley%20Interdiscip%20Rev%20Data%20Min%20Knowl%20Discov&title=Contrast%20and%20change%20mining&author=M%20Boettcher&volume=1&issue=3&publication_year=2011&pages=215-230&)\]
- 4.Hido S, Idé T, Kashima H, Kubo H, Matsuzawa H. Unsupervised Change Analysis using Supervised Learning. Adv Knowl Discov Data Min. 2008;5012:148–159. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Adv%20Knowl%20Discov%20Data%20Min&title=Unsupervised%20Change%20Analysis%20using%20Supervised%20Learning&author=S%20Hido&author=T%20Id%C3%A9&author=H%20Kashima&author=H%20Kubo&author=H%20Matsuzawa&volume=5012&publication_year=2008&pages=148-159&)\]
- 5.Scholz M, Klinkenberg R. Boosting classifiers for drifting concepts. Intell Data Anal. 2007;11(1):3–28. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Intell%20Data%20Anal&title=Boosting%20classifiers%20for%20drifting%20concepts&author=M%20Scholz&author=R%20Klinkenberg&volume=11&issue=1&publication_year=2007&pages=3-28&)\]
- 6.Yang P, Dumont G, Ansermino JM. Adaptive change detection in heart rate trend monitoring in anesthetized children. IEEE Trans Biomed Eng. 2006 Nov;53(11):2211–9. doi: 10.1109/TBME.2006.877107. \[ [DOI](https://doi.org/10.1109/TBME.2006.877107)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/17073326/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20Trans%20Biomed%20Eng&title=Adaptive%20change%20detection%20in%20heart%20rate%20trend%20monitoring%20in%20anesthetized%20children&author=P%20Yang&author=G%20Dumont&author=JM%20Ansermino&volume=53&issue=11&publication_year=2006&pages=2211-9&pmid=17073326&doi=10.1109/TBME.2006.877107&)\]
- 7.Malladi R, Kalamangalam GP, Aazhang B. Online Bayesian change point detection algorithms for segmentation of epileptic activity. Asilomar Conference on Signals, Systems and Computers. 2013:1833–1837. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Asilomar%20Conference%20on%20Signals,%20Systems%20and%20Computers&title=Online%20Bayesian%20change%20point%20detection%20algorithms%20for%20segmentation%20of%20epileptic%20activity&author=R%20Malladi&author=GP%20Kalamangalam&author=B%20Aazhang&publication_year=2013&pages=1833-1837&)\]
- 8.Staudacher M, Telser S, Amann A, Hinterhuber H, Ritsch-Marte M. A new method for change-point detection developed for on-line analysis of the heart beat variability during sleep. Phys A Stat Mech its Appl. 2005 Apr;349(3–4):582–596. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Phys%20A%20Stat%20Mech%20its%20Appl&title=A%20new%20method%20for%20change-point%20detection%20developed%20for%20on-line%20analysis%20of%20the%20heart%20beat%20variability%20during%20sleep&author=M%20Staudacher&author=S%20Telser&author=A%20Amann&author=H%20Hinterhuber&author=M%20Ritsch-Marte&volume=349&issue=3%E2%80%934&publication_year=2005&pages=582-596&)\]
- 9.Bosc M, Heitz F, Armspach JP, Namer I, Gounot D, Rumbach L. Automatic change detection in multimodal serial MRI: application to multiple sclerosis lesion evolution. Neuroimage. 2003 Oct;20(2):643–56. doi: 10.1016/S1053-8119(03)00406-3. \[ [DOI](https://doi.org/10.1016/S1053-8119(03)00406-3)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/14568441/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Neuroimage&title=Automatic%20change%20detection%20in%20multimodal%20serial%20MRI:%20application%20to%20multiple%20sclerosis%20lesion%20evolution&author=M%20Bosc&author=F%20Heitz&author=JP%20Armspach&author=I%20Namer&author=D%20Gounot&volume=20&issue=2&publication_year=2003&pages=643-56&pmid=14568441&doi=10.1016/S1053-8119(03)00406-3&)\]
- 10.Reeves J, Chen J, Wang XL, Lund R, Lu QQ. A Review and Comparison of Changepoint Detection Techniques for Climate Data. J Appl Meteorol Climatol. 2007 Jun;46(6):900–915. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=J%20Appl%20Meteorol%20Climatol&title=A%20Review%20and%20Comparison%20of%20Changepoint%20Detection%20Techniques%20for%20Climate%20Data&author=J%20Reeves&author=J%20Chen&author=XL%20Wang&author=R%20Lund&author=QQ%20Lu&volume=46&issue=6&publication_year=2007&pages=900-915&)\]
- 11.Itoh N, Kurths J. Change-Point Detection of Climate Time Series by Nonparametric Method. World Congress on Engineering and Computer Science 2010 Vol I. 2010 \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=World%20Congress%20on%20Engineering%20and%20Computer%20Science%202010%20Vol%20I&title=Change-Point%20Detection%20of%20Climate%20Time%20Series%20by%20Nonparametric%20Method&author=N%20Itoh&author=J%20Kurths&publication_year=2010&)\]
- 12.Ducre-Robitaille JF, Vincent LA, Boulet G. Comparison of techniques for detection of discontinuities in temperature series. Int J Climatol. 2003 Jul;23(9):1087–1101. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Int%20J%20Climatol&title=Comparison%20of%20techniques%20for%20detection%20of%20discontinuities%20in%20temperature%20series&author=JF%20Ducre-Robitaille&author=LA%20Vincent&author=G%20Boulet&volume=23&issue=9&publication_year=2003&pages=1087-1101&)\]
- 13.Chowdhury MFR, Selouani SA, O’Shaughnessy D. Bayesian on-line spectral change point detection: a soft computing approach for on-line ASR. Int J Speech Technol. 2011 Oct;15(1):5–23. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Int%20J%20Speech%20Technol&title=Bayesian%20on-line%20spectral%20change%20point%20detection:%20a%20soft%20computing%20approach%20for%20on-line%20ASR&author=MFR%20Chowdhury&author=SA%20Selouani&author=D%20O%E2%80%99Shaughnessy&volume=15&issue=1&publication_year=2011&pages=5-23&)\]
- 14.Rybach D, Gollan C, Schluter R, Ney H. Audio segmentation for speech recognition using segment features. IEEE International Conference on Acoustics, Speech and Signal Processing. 2009:4197–4200. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20International%20Conference%20on%20Acoustics,%20Speech%20and%20Signal%20Processing&title=Audio%20segmentation%20for%20speech%20recognition%20using%20segment%20features&author=D%20Rybach&author=C%20Gollan&author=R%20Schluter&author=H%20Ney&publication_year=2009&pages=4197-4200&)\]
- 15.Radke RJ, Andra S, Al-Kofahi O, Roysam B. Image change detection algorithms: a systematic survey. IEEE Trans Image Process. 2005 Mar;14(3):294–307. doi: 10.1109/tip.2004.838698. \[ [DOI](https://doi.org/10.1109/tip.2004.838698)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/15762326/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20Trans%20Image%20Process&title=Image%20change%20detection%20algorithms:%20a%20systematic%20survey&author=RJ%20Radke&author=S%20Andra&author=O%20Al-Kofahi&author=B%20Roysam&volume=14&issue=3&publication_year=2005&pages=294-307&pmid=15762326&doi=10.1109/tip.2004.838698&)\]
- 16.Nordli Ø, Przybylak R, Ogilvie AEJ, Isaksen K. Long-term temperature trends and variability on Spitsbergen: the extended Svalbard Airport temperature series, 1898–2012. Polar Res. 2014 Jan;33 \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Polar%20Res&title=Long-term%20temperature%20trends%20and%20variability%20on%20Spitsbergen:%20the%20extended%20Svalbard%20Airport%20temperature%20series,%201898%E2%80%932012&author=%C3%98%20Nordli&author=R%20Przybylak&author=AEJ%20Ogilvie&author=K%20Isaksen&volume=33&publication_year=2014&)\]
- 17.Tran D-H. Automated Change Detection and Reactive Clustering in Multivariate Streaming Data. 2013 Nov; \[ [Google Scholar](https://scholar.google.com/scholar_lookup?Tran%20D-H.%20Automated%20Change%20Detection%20and%20Reactive%20Clustering%20in%20Multivariate%20Streaming%20Data.%202013%20Nov;)\]
- 18.Shumway RH, Stoffer DS. Time Series Analysis and Its Applications. New York, NY: Springer New York; 2011.  \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Time%20Series%20Analysis%20and%20Its%20Applications&author=RH%20Shumway&author=DS%20Stoffer&publication_year=2011&)\]
- 19.Keogh E, Lin J. Clustering of time-series subsequences is meaningless: implications for previous and future research. Knowl Inf Syst. 2004 Aug;8(2):154–177. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Knowl%20Inf%20Syst&title=Clustering%20of%20time-series%20subsequences%20is%20meaningless:%20implications%20for%20previous%20and%20future%20research&author=E%20Keogh&author=J%20Lin&volume=8&issue=2&publication_year=2004&pages=154-177&)\]
- 20.Wei L, Keogh E. Semi-supervised time series classification. 12th ACM SIGKDD international conference on Knowledge discovery and data mining - KDD ’06. 2006:748. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=12th%20ACM%20SIGKDD%20international%20conference%20on%20Knowledge%20discovery%20and%20data%20mining%20-%20KDD%20%E2%80%9906&title=Semi-supervised%20time%20series%20classification&author=L%20Wei&author=E%20Keogh&publication_year=2006&pages=748&)\]
- 21.Feuz KD, Cook DJ, Rosasco C, Robertson K, Schmitter-Edgecombe M. Automated Detection of Activity Transitions for Prompting. IEEE Trans Human-Machine Syst. 2014;45(5):1–11. doi: 10.1109/THMS.2014.2362529. \[ [DOI](https://doi.org/10.1109/THMS.2014.2362529)\] \[ [PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4805372/)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/27019791/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20Trans%20Human-Machine%20Syst&title=Automated%20Detection%20of%20Activity%20Transitions%20for%20Prompting&author=KD%20Feuz&author=DJ%20Cook&author=C%20Rosasco&author=K%20Robertson&author=M%20Schmitter-Edgecombe&volume=45&issue=5&publication_year=2014&pages=1-11&pmid=27019791&doi=10.1109/THMS.2014.2362529&)\]
- 22.Liu S, Yamada M, Collier N, Sugiyama M. Change-point detection in time-series data by relative densityratio estimation. Neural Netw. 2013 Jul;43:72–83. doi: 10.1016/j.neunet.2013.01.012. \[ [DOI](https://doi.org/10.1016/j.neunet.2013.01.012)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/23500502/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Neural%20Netw&title=Change-point%20detection%20in%20time-series%20data%20by%20relative%20densityratio%20estimation&author=S%20Liu&author=M%20Yamada&author=N%20Collier&author=M%20Sugiyama&volume=43&publication_year=2013&pages=72-83&pmid=23500502&doi=10.1016/j.neunet.2013.01.012&)\]
- 23.Chen H, Zhang N. Graph-Based Change-Point Detection. Ann Stat. 2014 Sep;43(1):139–176. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Ann%20Stat&title=Graph-Based%20Change-Point%20Detection&author=H%20Chen&author=N%20Zhang&volume=43&issue=1&publication_year=2014&pages=139-176&)\]
- 24.Harchaoui Z, Moulines E, Bach FR. Kernel Change-point Analysis. Advances in Neural Information Processing Systems. 2009:609–616. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Advances%20in%20Neural%20Information%20Processing%20Systems&title=Kernel%20Change-point%20Analysis&author=Z%20Harchaoui&author=E%20Moulines&author=FR%20Bach&publication_year=2009&pages=609-616&)\]
- 25.Downey AB. A novel changepoint detection algorithm. 2008 Dec; \[ [Google Scholar](https://scholar.google.com/scholar_lookup?Downey%20AB.%20A%20novel%20changepoint%20detection%20algorithm.%202008%20Dec;)\]
- 26.Chandola V, Vatsavai RR. A gaussian process based online change detection algorithm for monitoring periodic time series \| Varun Mithal - Academia.edu. SIAM international conference on data mining. 2011:95–106. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=SIAM%20international%20conference%20on%20data%20mining&title=A%20gaussian%20process%20based%20online%20change%20detection%20algorithm%20for%20monitoring%20periodic%20time%20series%20|%20Varun%20Mithal%20-%20Academia.edu&author=V%20Chandola&author=RR%20Vatsavai&publication_year=2011&pages=95-106&)\]
- 27.Raykar VC. Scalable machine learning for massive datasets: Fast summation algorithms. University of Maryland; College Park: 2007.  \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Scalable%20machine%20learning%20for%20massive%20datasets:%20Fast%20summation%20algorithms&author=VC%20Raykar&publication_year=2007&)\]
- 28.Shieh J, Keogh E. Polishing the Right Apple: Anytime Classification Also Benefits Data Streams with Constant Arrival Times. IEEE International Conference on Data Mining. 2010:461–470. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20International%20Conference%20on%20Data%20Mining&title=Polishing%20the%20Right%20Apple:%20Anytime%20Classification%20Also%20Benefits%20Data%20Streams%20with%20Constant%20Arrival%20Times&author=J%20Shieh&author=E%20Keogh&publication_year=2010&pages=461-470&)\]
- 29.Shlomo Zilberstein SR. Optimal Composition of Real-Time Systems. Artif Intell. 1996;82(1):181–213. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Artif%20Intell&title=Optimal%20Composition%20of%20Real-Time%20Systems&author=SR%20Shlomo%20Zilberstein&volume=82&issue=1&publication_year=1996&pages=181-213&)\]
- 30.Moskvina V, Zhigljavsky A. An Algorithm Based on Singular Spectrum Analysis for Change-Point Detection. Commun Stat - Simul Comput. 2003 Jan;32(2):319–352. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Commun%20Stat%20-%20Simul%20Comput&title=An%20Algorithm%20Based%20on%20Singular%20Spectrum%20Analysis%20for%20Change-Point%20Detection&author=V%20Moskvina&author=A%20Zhigljavsky&volume=32&issue=2&publication_year=2003&pages=319-352&)\]
- 31.Adams RP, MacKay DJC. Bayesian Online Changepoint Detection. Machine Learning. 2007 Oct; \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Machine%20Learning&title=Bayesian%20Online%20Changepoint%20Detection&author=RP%20Adams&author=DJC%20MacKay&publication_year=2007&)\]
- 32.Rakthanmanon T, Keogh EJ, Lonardi S, Evans S. Time Series Epenthesis: Clustering Time Series Streams Requires Ignoring Some Data. IEEE 11th International Conference on Data Mining. 2011:547–556. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%2011th%20International%20Conference%20on%20Data%20Mining&title=Time%20Series%20Epenthesis:%20Clustering%20Time%20Series%20Streams%20Requires%20Ignoring%20Some%20Data&author=T%20Rakthanmanon&author=EJ%20Keogh&author=S%20Lonardi&author=S%20Evans&publication_year=2011&pages=547-556&)\]
- 33.Reddy S, Mun M, Burke J, Estrin D, Hansen M, Srivastava M. Using mobile phones to determine transportation modes. ACM Trans Sens Networks. 2010 Feb;6(2):1–27. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=ACM%20Trans%20Sens%20Networks&title=Using%20mobile%20phones%20to%20determine%20transportation%20modes&author=S%20Reddy&author=M%20Mun&author=J%20Burke&author=D%20Estrin&author=M%20Hansen&volume=6&issue=2&publication_year=2010&pages=1-27&)\]
- 34.Zheng Y, Liu L, Wang L, Xie X. Learning transportation mode from raw gps data for geographic applications on the web. 17th international conference on World Wide Web - WWW ’08. 2008:247. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=17th%20international%20conference%20on%20World%20Wide%20Web%20-%20WWW%20%E2%80%9908&title=Learning%20transportation%20mode%20from%20raw%20gps%20data%20for%20geographic%20applications%20on%20the%20web&author=Y%20Zheng&author=L%20Liu&author=L%20Wang&author=X%20Xie&publication_year=2008&pages=247&)\]
- 35.Cook DJ, Krishnan NC. Activity Learning: Discovering, Recognizing, and Predicting Human Behavior from Sensor Data. Wiley; 2015.  \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Activity%20Learning:%20Discovering,%20Recognizing,%20and%20Predicting%20Human%20Behavior%20from%20Sensor%20Data&author=DJ%20Cook&author=NC%20Krishnan&publication_year=2015&)\]
- 36.Zheng Y, Li Q, Chen Y, Xie X, Ma W-Y. Understanding mobility based on GPS data. 10th international conference on Ubiquitous computing - UbiComp ’08. 2008:312. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=10th%20international%20conference%20on%20Ubiquitous%20computing%20-%20UbiComp%20%E2%80%9908&title=Understanding%20mobility%20based%20on%20GPS%20data&author=Y%20Zheng&author=Q%20Li&author=Y%20Chen&author=X%20Xie&author=W-Y%20Ma&publication_year=2008&pages=312&)\]
- 37.Zheng Y, Chen Y, Xie X, Ma W-Y. Understanding transportation modes based on GPS data for Web applications - Microsoft Research. ACM Trans Web. 2010;4(1) \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=ACM%20Trans%20Web&title=Understanding%20transportation%20modes%20based%20on%20GPS%20data%20for%20Web%20applications%20-%20Microsoft%20Research&author=Y%20Zheng&author=Y%20Chen&author=X%20Xie&author=W-Y%20Ma&volume=4&issue=1&publication_year=2010&)\]
- 38.Cleland I, Han M, Nugent C, Lee H, McClean S, Zhang S, Lee S. Evaluation of prompted annotation of activity data recorded from a smart phone. Sensors (Basel) 2014 Jan;14(9):15861–79. doi: 10.3390/s140915861. \[ [DOI](https://doi.org/10.3390/s140915861)\] \[ [PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4208150/)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/25166500/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Sensors%20(Basel)&title=Evaluation%20of%20prompted%20annotation%20of%20activity%20data%20recorded%20from%20a%20smart%20phone&author=I%20Cleland&author=M%20Han&author=C%20Nugent&author=H%20Lee&author=S%20McClean&volume=14&issue=9&publication_year=2014&pages=15861-79&pmid=25166500&doi=10.3390/s140915861&)\]
- 39.Han M, Vinh LT, Lee YK, Lee S. Comprehensive Context Recognizer Based on Multimodal Sensors in a Smartphone. Sensors. 2012 Sep;12(12):12588–12605. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Sensors&title=Comprehensive%20Context%20Recognizer%20Based%20on%20Multimodal%20Sensors%20in%20a%20Smartphone&author=M%20Han&author=LT%20Vinh&author=YK%20Lee&author=S%20Lee&volume=12&issue=12&publication_year=2012&pages=12588-12605&)\]
- 40.Desobry F, Davy M, Doncarli C. An online kernel change detection algorithm. IEEE Trans Signal Process. 2005 Aug;53(8):2961–2974. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20Trans%20Signal%20Process&title=An%20online%20kernel%20change%20detection%20algorithm&author=F%20Desobry&author=M%20Davy&author=C%20Doncarli&volume=53&issue=8&publication_year=2005&pages=2961-2974&)\]
- 41.Basseville M, Nikiforov IV. Detection of Abrupt Changes- theory and application. Prentice Hall; 1993.  \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Detection%20of%20Abrupt%20Changes-%20theory%20and%20application&author=M%20Basseville&author=IV%20Nikiforov&publication_year=1993&)\]
- 42.Cho H, Fryzlewicz P. Multiple-change-point detection for high dimensional time series via sparsified binary segmentation. J R Stat Soc Ser B (Statistical Methodol. 2015 Mar;77(2):475–507. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=J%20R%20Stat%20Soc%20Ser%20B%20(Statistical%20Methodol&title=Multiple-change-point%20detection%20for%20high%20dimensional%20time%20series%20via%20sparsified%20binary%20segmentation&author=H%20Cho&author=P%20Fryzlewicz&volume=77&issue=2&publication_year=2015&pages=475-507&)\]
- 43.Aue A, Hormann S, Horvath L, Reimherr M. Break Detection In The Covariance Structure Of Multivariate Time Series Models. Ann Stat. 2009;37(6B):4046–4087. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Ann%20Stat&title=Break%20Detection%20In%20The%20Covariance%20Structure%20Of%20Multivariate%20Time%20Series%20Models&author=A%20Aue&author=S%20Hormann&author=L%20Horvath&author=M%20Reimherr&volume=37&issue=6B&publication_year=2009&pages=4046-4087&)\]
- 44.Jeske DR, Montes De Oca V, Bischoff W, Marvasti M. Cusum techniques for timeslot sequences with applications to network surveillance. Comput Stat Data Anal. 2009 Oct;53(12):4332–4344. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Comput%20Stat%20Data%20Anal&title=Cusum%20techniques%20for%20timeslot%20sequences%20with%20applications%20to%20network%20surveillance&author=DR%20Jeske&author=V%20Montes%20De%20Oca&author=W%20Bischoff&author=M%20Marvasti&volume=53&issue=12&publication_year=2009&pages=4332-4344&)\]
- 45.Yamanishi K, Takeuchi J. A unifying framework for detecting outliers and change points from non-stationary time series data. 8th ACM SIGKDD international conference on Knowledge discovery and data mining - KDD ’02. 2002:676. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=8th%20ACM%20SIGKDD%20international%20conference%20on%20Knowledge%20discovery%20and%20data%20mining%20-%20KDD%20%E2%80%9902&title=A%20unifying%20framework%20for%20detecting%20outliers%20and%20change%20points%20from%20non-stationary%20time%20series%20data&author=K%20Yamanishi&author=J%20Takeuchi&publication_year=2002&pages=676&)\]
- 46.Yamada M, Kimura A, Naya F, Sawada H. Change-point detection with feature selection in high-dimensional time-series data. International Joint Conference on Artificial Intelligence. 2013 \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=International%20Joint%20Conference%20on%20Artificial%20Intelligence&title=Change-point%20detection%20with%20feature%20selection%20in%20high-dimensional%20time-series%20data&author=M%20Yamada&author=A%20Kimura&author=F%20Naya&author=H%20Sawada&publication_year=2013&)\]
- 47.Kuncheva LI, Faithfull WJ. PCA feature extraction for change detection in multidimensional unlabeled data. IEEE Trans neural networks Learn Syst. 2014 Jan;25(1):69–80. doi: 10.1109/TNNLS.2013.2248094. \[ [DOI](https://doi.org/10.1109/TNNLS.2013.2248094)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/24806645/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20Trans%20neural%20networks%20Learn%20Syst&title=PCA%20feature%20extraction%20for%20change%20detection%20in%20multidimensional%20unlabeled%20data&author=LI%20Kuncheva&author=WJ%20Faithfull&volume=25&issue=1&publication_year=2014&pages=69-80&pmid=24806645&doi=10.1109/TNNLS.2013.2248094&)\]
- 48.Kuncheva LI. Change Detection in Streaming Multivariate Data Using Likelihood Detectors. IEEE Trans Knowl Data Eng. 2013 May;25(5):1175–1180. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20Trans%20Knowl%20Data%20Eng&title=Change%20Detection%20in%20Streaming%20Multivariate%20Data%20Using%20Likelihood%20Detectors&author=LI%20Kuncheva&volume=25&issue=5&publication_year=2013&pages=1175-1180&)\]
- 49.Alippi C, Boracchi G, Carrera D, Roveri M. Change Detection in Multivariate Datastreams: Likelihood and Detectability Loss. 2015 Oct; \[ [Google Scholar](https://scholar.google.com/scholar_lookup?Alippi%20C,%20Boracchi%20G,%20Carrera%20D,%20Roveri%20M.%20Change%20Detection%20in%20Multivariate%20Datastreams:%20Likelihood%20and%20Detectability%20Loss.%202015%20Oct;)\]
- 50.Kawahara Y, Yairi T, Machida K. Change-Point Detection in Time-Series Data Based on Subspace Identification. 7th IEEE International Conference on Data Mining (ICDM 2007) 2007:559–564. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=7th%20IEEE%20International%20Conference%20on%20Data%20Mining%20(ICDM%202007)&title=Change-Point%20Detection%20in%20Time-Series%20Data%20Based%20on%20Subspace%20Identification&author=Y%20Kawahara&author=T%20Yairi&author=K%20Machida&publication_year=2007&pages=559-564&)\]
- 51.Chib S. Estimation and Comparison of multiple change point models. J Econom. 1998;86(2):221–241. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=J%20Econom&title=Estimation%20and%20Comparison%20of%20multiple%20change%20point%20models&author=S%20Chib&volume=86&issue=2&publication_year=1998&pages=221-241&)\]
- 52.Barry D, Hartigan JA. A Bayesian Analysis for Change Point Problems. J Am Stat Assoc. 1993;88(421):309–319. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=J%20Am%20Stat%20Assoc&title=A%20Bayesian%20Analysis%20for%20Change%20Point%20Problems&author=D%20Barry&author=JA%20Hartigan&volume=88&issue=421&publication_year=1993&pages=309-319&)\]
- 53.Lau HF, Yamamoto S. Bayesian online changepoint detection to improve transparency in human-machine interaction systems. 49th IEEE Conference on Decision and Control (CDC) 2010:3572–3577. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=49th%20IEEE%20Conference%20on%20Decision%20and%20Control%20(CDC)&title=Bayesian%20online%20changepoint%20detection%20to%20improve%20transparency%20in%20human-machine%20interaction%20systems&author=HF%20Lau&author=S%20Yamamoto&publication_year=2010&pages=3572-3577&)\]
- 54.Tan BA, Gerstoft P, Yardim C, Hodgkiss WS. Change-point detection for recursive Bayesian geoacoustic inversions. J Acoust Soc Am. 2015 Apr;137(4):1962–70. doi: 10.1121/1.4916887. \[ [DOI](https://doi.org/10.1121/1.4916887)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/25920847/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=J%20Acoust%20Soc%20Am&title=Change-point%20detection%20for%20recursive%20Bayesian%20geoacoustic%20inversions&author=BA%20Tan&author=P%20Gerstoft&author=C%20Yardim&author=WS%20Hodgkiss&volume=137&issue=4&publication_year=2015&pages=1962-70&pmid=25920847&doi=10.1121/1.4916887&)\]
- 55.Saatçi Y, Turner RD, Rasmussen CE. Gaussian Process Change Point Models. International Conference on Machine Learning. 2010:927–934. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=International%20Conference%20on%20Machine%20Learning&title=Gaussian%20Process%20Change%20Point%20Models&author=Y%20Saat%C3%A7i&author=RD%20Turner&author=CE%20Rasmussen&publication_year=2010&pages=927-934&)\]
- 56.Chandola V, Vatsavai R. Scalable Time Series Change Detection for Biomass Monitoring Using Gaussian Process. Conference on Intelligent Data Understanding 2010 - CIDU. 2010 \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Conference%20on%20Intelligent%20Data%20Understanding%202010%20-%20CIDU&title=Scalable%20Time%20Series%20Change%20Detection%20for%20Biomass%20Monitoring%20Using%20Gaussian%20Process&author=V%20Chandola&author=R%20Vatsavai&publication_year=2010&)\]
- 57.Brahim-Belhouari S, Bermak A. Gaussian process for nonstationary time series prediction. Comput Stat Data Anal. 2004 Nov;47(4):705–712. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Comput%20Stat%20Data%20Anal&title=Gaussian%20process%20for%20nonstationary%20time%20series%20prediction&author=S%20Brahim-Belhouari&author=A%20Bermak&volume=47&issue=4&publication_year=2004&pages=705-712&)\]
- 58.Harchaoui Z, Vallet F, Lung-Yut-Fong A, Cappe O. A regularized kernel-based approach to unsupervised audio segmentation. IEEE International Conference on Acoustics, Speech and Signal Processing. 2009:1665–1668. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20International%20Conference%20on%20Acoustics,%20Speech%20and%20Signal%20Processing&title=A%20regularized%20kernel-based%20approach%20to%20unsupervised%20audio%20segmentation&author=Z%20Harchaoui&author=F%20Vallet&author=A%20Lung-Yut-Fong&author=O%20Cappe&publication_year=2009&pages=1665-1668&)\]
- 59.Friedman JH, Rafsky LC. Multivariate Generalizations of the Wald-Wolfowitz and Smirnov Two-Sample Tests. Ann Stat. 1979 Jul;7(4):697–717. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Ann%20Stat&title=Multivariate%20Generalizations%20of%20the%20Wald-Wolfowitz%20and%20Smirnov%20Two-Sample%20Tests&author=JH%20Friedman&author=LC%20Rafsky&volume=7&issue=4&publication_year=1979&pages=697-717&)\]
- 60.Rosenbaum PR. An exact distribution-free test comparing two multivariate distributions based on adjacency. J R Stat Soc. 2005;67:515–530. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=J%20R%20Stat%20Soc&title=An%20exact%20distribution-free%20test%20comparing%20two%20multivariate%20distributions%20based%20on%20adjacency&author=PR%20Rosenbaum&volume=67&publication_year=2005&pages=515-530&)\]
- 61.Zhang J, Small M. Complex Network from Pseudoperiodic Time Series: Topology versus Dynamics. Phys Rev Lett. 2006 Jun;96(23):238701. doi: 10.1103/PhysRevLett.96.238701. \[ [DOI](https://doi.org/10.1103/PhysRevLett.96.238701)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/16803415/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Phys%20Rev%20Lett&title=Complex%20Network%20from%20Pseudoperiodic%20Time%20Series:%20Topology%20versus%20Dynamics&author=J%20Zhang&author=M%20Small&volume=96&issue=23&publication_year=2006&pages=238701&pmid=16803415&doi=10.1103/PhysRevLett.96.238701&)\]
- 62.Lacasa L, Luque B, Ballesteros F, Luque J, Nuño JC. From time series to complex networks: the visibility graph. Proc Natl Acad Sci U S A. 2008 Apr;105(13):4972–5. doi: 10.1073/pnas.0709247105. \[ [DOI](https://doi.org/10.1073/pnas.0709247105)\] \[ [PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC2278201/)\] \[ [PubMed](https://pubmed.ncbi.nlm.nih.gov/18362361/)\] \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Proc%20Natl%20Acad%20Sci%20U%20S%20A&title=From%20time%20series%20to%20complex%20networks:%20the%20visibility%20graph&author=L%20Lacasa&author=B%20Luque&author=F%20Ballesteros&author=J%20Luque&author=JC%20Nu%C3%B1o&volume=105&issue=13&publication_year=2008&pages=4972-5&pmid=18362361&doi=10.1073/pnas.0709247105&)\]
- 63.Keogh E, Chu S, Hart D, Pazzani M. An online algorithm for segmenting time series. IEEE International Conference on Data Mining. 2001:289–296. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20International%20Conference%20on%20Data%20Mining&title=An%20online%20algorithm%20for%20segmenting%20time%20series&author=E%20Keogh&author=S%20Chu&author=D%20Hart&author=M%20Pazzani&publication_year=2001&pages=289-296&)\]
- 64.Zakaria J, Mueen A, Keogh E. Clustering Time Series Using Unsupervised-Shapelets. IEEE 12th International Conference on Data Mining. 2012:785–794. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%2012th%20International%20Conference%20on%20Data%20Mining&title=Clustering%20Time%20Series%20Using%20Unsupervised-Shapelets&author=J%20Zakaria&author=A%20Mueen&author=E%20Keogh&publication_year=2012&pages=785-794&)\]
- 65. \[Accessed: 16–Sep-2015\];CENSREC-4 - Speech Resources Consortium. \[Online\]. Available: [http://research.nii.ac.jp/src/en/CENSREC-4.html](http://research.nii.ac.jp/src/en/CENSREC-4.html).
- 66. \[Accessed: 16–Sep-2015\];Welcome to the UCR Time Series Classification/Clustering Page. \[Online\]. Available: [http://www.cs.ucr.edu/~eamonn/time\_series\_data/](http://www.cs.ucr.edu/~eamonn/time_series_data/)
- 67. \[Accessed: 16–Sep-2015\];Welcome to CASAS. \[Online\]. Available: [http://casas.wsu.edu/datasets/](http://casas.wsu.edu/datasets/)
- 68. \[Accessed: 16–Sep-2015\];Hasc Challenge 2011. \[Online\]. Available: [http://hasc.jp/hc2011/](http://hasc.jp/hc2011/)
- 69.Harel M, Mannor S, El-yaniv R, Crammer K. Concept Drift Detection Through Resampling. Proceedings of the 31st International Conference on Machine Learning - ICML-14. 2014:1009–1017. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Proceedings%20of%20the%2031st%20International%20Conference%20on%20Machine%20Learning%20-%20ICML-14&title=Concept%20Drift%20Detection%20Through%20Resampling&author=M%20Harel&author=S%20Mannor&author=R%20El-yaniv&author=K%20Crammer&publication_year=2014&pages=1009-1017&)\]
- 70.Bach S, Maloof M. A Bayesian Approach to Concept Drift. Advances in Neural Information Processing Systems. 2010:127–135. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?journal=Advances%20in%20Neural%20Information%20Processing%20Systems&title=A%20Bayesian%20Approach%20to%20Concept%20Drift&author=S%20Bach&author=M%20Maloof&publication_year=2010&pages=127-135&)\]

![Close](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/close.svg)

## ACTIONS

- [![View on publisher site icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/launch.svg)View on publisher site](https://doi.org/10.1007/s10115-016-0987-z)
- [![Download PDF icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/file_download.svg)PDF (1.2 MB)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5464762/pdf/nihms860556.pdf)
- ![Cite icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/format_quote.svg)Cite
- ![Collections icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/action-bookmark-full.svg)![Collections icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/action-bookmark-empty.svg)Collections
- ![Permalink icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/share.svg)Permalink




## PERMALINK



![Copy icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/content_copy.svg)Copy


## RESOURCES

### Similar articles

### Cited by other articles

### Links to NCBI Databases

Back to Top![back to top icon](https://cdn.ncbi.nlm.nih.gov/pmc/pd-medc-pmc-cloudpmc-viewer/production/9b1d9d87/var/data/static/img/usa-icons/arrow_upward.svg)