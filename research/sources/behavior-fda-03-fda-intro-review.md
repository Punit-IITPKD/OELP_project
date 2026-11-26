Source: https://arxiv.org/html/2312.05523v1
Title: Functional Data Analysis:An Introduction and Recent Developments
Fetched: 2026-11-26T15:58:06.820Z

[Skip to main content](https://arxiv.org/html/2312.05523v1#infobox)

Title:

Content selection saved. Describe the issue below:

Description:

[License: CC BY 4.0](https://info.arxiv.org/help/license/index.html#licenses-available)

arXiv:2312.05523v1 \[stat.ME\] 09 Dec 2023

# Functional Data Analysis:   An Introduction and Recent Developments

Jan Gertheiss
††thanks: Corresponding author: jan.gertheiss@hsu-hh.deAffiliation: Department of Mathematics and Statistics
Affiliation: School of Economics and Social Sciences
Affiliation: Helmut Schmidt University, Hamburg, Germany
David Rügamer
Affiliation: Department of Statistics, LMU Munich
Affiliation: Munich Center for Machine Learning, Munich, Germany
Bernard X.W. Liew
Affiliation: School of Sport, Rehabilitation and Exercise Sciences
Affiliation: University of Essex, Essex, UK
Sonja Greven
Affiliation: Chair of Statistics
Affiliation: School of Business and Economics
Affiliation: Humboldt-Universität zu Berlin, Berlin, Germany

###### Abstract

Functional data analysis (FDA) is a statistical framework that allows for the analysis of curves, images, or functions on higher dimensional domains. The goals of FDA, such as descriptive analyses, classification, and regression, are generally the same as for statistical analyses of scalar-valued or multivariate data, but FDA brings additional challenges due to the high- and infinite dimensionality of observations and parameters, respectively. This paper provides an introduction to FDA, including a description of the most common statistical analysis techniques, their respective software implementations, and some recent developments in the field. The paper covers fundamental concepts such as descriptives and outliers, smoothing, amplitude and phase variation, and functional principal component analysis. It also discusses functional regression, statistical inference with functional data, functional classification and clustering, and machine learning approaches for functional data analysis. The methods discussed in this paper are widely applicable in fields such as medicine, biophysics, neuroscience, and chemistry, and are increasingly relevant due to the widespread use of technologies that allow for the collection of functional data. Sparse functional data methods are also relevant for longitudinal data analysis. All presented methods are demonstrated using available software in R by analyzing a data set on human motion and motor control. To facilitate the understanding of the methods, their implementation, and hands-on application, the code for these practical examples is made available on Github: https://github.com/davidruegamer/FDA\_tutorial.

## 1 Introduction

In functional data analysis (FDA), curves, images, or functions on higher dimensional domains constitute the observations and the objects of interest in the analysis ( [Ramsay and Silverman, 2005](https://arxiv.org/html/2312.05523v1#bib.bib156 "")). The goals of FDA, such as descriptive analyses, classification, regression, etc., are often the same as for statistical analyses of scalar-valued or multivariate data, and many corresponding methods have been transferred to function-valued data, while FDA also brings additional challenges including infinite/high dimensionality of observations and parameters as well as misalignment. In contrast to simpler methods that reduce the functional observations to scalar summary values, FDA retains all important information by directly using the functional observations in the analysis. Functional data occur in many different fields, including medicine ( [Sørensen et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib194 "")), biophysics ( [Liew et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib109 "")), neuroscience ( [Rügamer et al., 2018](https://arxiv.org/html/2312.05523v1#bib.bib165 "")) or chemistry ( [Brockhaus et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib12 "")). Nowadays, technologies such as imaging techniques, electroencephalographs and
electrocardiographs, gyroscopes, or accelerometers, standard in bio-medical research or even built into everyday devices such as smartphones, controllers, or wristwatches, allow for seamlessly collecting functional data. Consequently, many research fields observe an increased interest in methods to analyze this type of data. In this paper, we describe a range of the most common statistical analysis techniques in FDA, their respective software implementations, and some more recent developments in the field. We aim to provide an introduction and tutorial for some of the most important topics in FDA, while providing a partial review with further reading for some additional, more advanced topics.

### 1.1 Functional data, longitudinal data, and time series

Data sets collected over time occur in different fields and under different names and we thus briefly discuss differences between FDA and longitudinal as well as time-series data for readers new to the field.

In health and social sciences, repeated observations over time on the same subjects or observational units are often termed longitudinal data (LD) or panel data. LD usually involves only a few repeated measurements per observation unit (e.g., subject observed before medication and at two follow-up appointments) with potentially different (numbers of) time points for different observation units. While functional data (FD) with different measurement points across observations exists (so-called sparse FD), the data is often recorded on the same (time) interval, with the same frequency, and exhibits a large number of measurements per observation unit. Methods to analyze FD and LD thus traditionally differ in how data is understood and treated. While the repeated measurements of observation units in the analysis of LD are often accounted for by using random effects in a parametric model, FD usually treats the observed sequences per measurement unit as observations of a smooth process observed at discrete time points. It thus models this data using non- or semi-parametric methods, aided by the typically larger number of available measurement points per curve. Nevertheless, there is an overlap between the two areas, and ideas and methods from (sparse) functional data analysis have more recently been used to make longitudinal data models less parametric and more flexible ( [Yao et al., 2005](https://arxiv.org/html/2312.05523v1#bib.bib215 ""); [Goldsmith et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib60 ""); [Köhler et al., 2017](https://arxiv.org/html/2312.05523v1#bib.bib95 ""), e.g.).

Time-series analysis, on the other hand, typically considers a single observation of a stochastic process on an equidistant time grid from a single observation unit (e.g., values of a share at one stock market observed over time). It is thus different from LD and FD where repeated observations on each of a sample of observational units are available. Due to the limited amount of data, methods usually focus on parametric estimation and often aim for good forecasting performance for unseen future time points. Goals and data structure thus differ from LD and FDA. If a sample of different time series is available, however, as, e.g., considered in the field of time series classification, and the focus is less on parametric methods, the setting can also be considered from a functional data viewpoint.

### 1.2 Notation

In this paper, we will usually focus on a sample of functional data xix\_{i} considered to be realizations of random
functions Xi,i=1,…,nX\_{i},i=1,\\dots,n, with values Xi​(t)∈ℝ,t∈𝒯X\_{i}(t)\\in\\mathbb{R},t\\in\\mathcal{T}, over an interval 𝒯⊂ℝ\\mathcal{T}\\subset\\mathbb{R}. Note that both tt and Xi​(t)X\_{i}(t) can be generalized to take values in some other domain than ℝ\\mathbb{R}, but this will not be the focus here.
The mean function will be denoted by 𝔼⁡(X⁡(t))=μ⁡(t){\\mathbb{E}}(X(t))=\\mu(t) and the covariance function by Cov⁡(X⁡(s),X⁡(t))=Σ⁡(s,t){\\operatorname{Cov}}(X(s),X(t))=\\Sigma(s,t), s,t∈𝒯s,t\\in\\mathcal{T}. In practice, the functional data is only observed on a discrete grid of measurement points ti​l∈𝒯t\_{il}\\in\\mathcal{T},
giving observations xi​(ti​l)x\_{i}(t\_{il}),
l=1,…,Li,i=1,…,nl=1,\\dots,L\_{i},i=1,\\dots,n. For so-called dense functional data, the grid is equal across functions and (relatively) dense in 𝒯\\mathcal{T}. For so-called sparse functional data, the grids are curve-specific and can be relatively sparse, but should together still cover 𝒯\\mathcal{T} well. If the grids differ but are relatively dense in 𝒯\\mathcal{T}, one also speaks of irregular functional data. While a common assumption in FDA is smoothness of the functions, they are often observed with additional measurement erorr. Then, we observe
Xi​(ti​l)=X~i​(ti​l)+εi​lX\_{i}(t\_{il})=\\widetilde{X}\_{i}(t\_{il})+\\varepsilon\_{il}
at ti​l∈𝒯,l=1,…,Li,i=1,…,nt\_{il}\\in\\mathcal{T},l=1,\\dots,L\_{i},i=1,\\dots,n, where X~i​(t)\\widetilde{X}\_{i}(t) is the underlying (smooth) function and εi​l\\varepsilon\_{il} are independent and identically distributed (i.i.d.) noise terms. Functions are commonly considered as elements of the ℒ2\\mathcal{L}^{2} space of functions

|     |     |     |
| --- | --- | --- |
|  | ℒ2(𝒯)={f:𝒯→ℝ\|∫𝒯f2(t)dt<∞}with scalar product<f,g>=∫𝒯f(t)g(t)dt\\mathcal{L}^{2}(\\mathcal{T})=\\left\\{f:\\mathcal{T}\\rightarrow{\\mathbb{R}}\\left\|\\int\_{\\mathcal{T}}f^{2}(t)dt<\\infty\\right\\}\\right.\\quad\\text{with scalar product}\\;<f,g>=\\int\_{\\mathcal{T}}f(t)g(t)dt |  |

for functions f,g∈ℒ2​(𝒯)f,g\\in\\mathcal{L}^{2}(\\mathcal{T}),
which induces the norm ‖f‖ℒ2=<f,f>1/2\\\|f\\\|\_{\\mathcal{L}^{2}}=<f,f>^{1/2} and a Hilbert space structure.

### 1.3 Running data example(s): human motion and motor control

Data from the biomechanical analysis of human motion and motor control almost always exhibit temporal, spatial, or both spatio-temporal characteristics within regular discrete bounds (e.g., gait events). For example, the flexion-extension knee joint angle during running over the stance phase of running reflects a one-dimensional (1D) time-series variable ( [Pataky, 2010](https://arxiv.org/html/2312.05523v1#bib.bib145 "")); the plantar pressure distribution of the foot at an instant during standing reflects a 2D spatial variable ( [Montagnani et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib132 "")), and the 3D bone strain patterns of the femur at an instant during an exercise reflects a spatial variable ( [Martelli et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib122 "")). The typical approach to analyzing biomechanical data is to first reduce multi-dimensional data into a single scalar variable (e.g., maximal value), followed by statistical inference. However, statistically analyzing discretized biomechanical data could, in some instances, lead to elevated Type 1 and 2 errors ( [Pataky et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib146 ""); [Pataky et al., 2016](https://arxiv.org/html/2312.05523v1#bib.bib147 ""); [Robinson et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib162 "")). In addition, it is commonly the interest of researchers to not only know “what” is statistically different but, in human movement, “where” and “when” the differences occur. One approach used to answer these questions is functional data analysis, allowing, e.g., in functional regression to model repeated measurements and to include functional biomechanical variables as the outcome ( [Warmenhoven et al., 2018](https://arxiv.org/html/2312.05523v1#bib.bib209 "")), the covariates ( [Liew et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib109 "")), or both ( [Liew et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib110 "")).

The data we use in this paper are derived from three primary sources –- a publicly available running dataset ( [Fukuchi et al., 2017](https://arxiv.org/html/2312.05523v1#bib.bib52 "")), and two datasets from the third author’s (BL) research on load carriage running ( [Liew et al., 2016a](https://arxiv.org/html/2312.05523v1#bib.bib107 ""); [Liew et al., 2016b](https://arxiv.org/html/2312.05523v1#bib.bib108 "")). Details of the experimental methods will be briefly mentioned here.
In the first publicly available dataset on running (with sample size n=28n=28) in healthy adults ( [Fukuchi et al., 2017](https://arxiv.org/html/2312.05523v1#bib.bib52 "")), running was performed on a dual-belt, force-instrumented treadmill (300 Hz; Bertec, USA), whilst lower-limb kinematic trajectories were captured with 12 optoelectronic cameras (150 Hz; Motion Analysis Corporation, USA). Participants performed running with shoes at 2.5 m/s, 3.5 m/s, and 4.5 m/s. The second dataset comes from a previously published work investigating the effects of load carriage on running biomechanics (n=31n=31) ( [Liew et al., 2016b](https://arxiv.org/html/2312.05523v1#bib.bib108 "")), which involved participants performing overground running across in-ground embedded force platforms (2000 Hz, AMTI, Watertown, MA), while carrying three load conditions (0%, 10%, 20% body weight (BW)) across three velocities (3.0 m/s, 4.0 m/s, 5.0 m/s). Lower-limb kinematic trajectories were captured using an 18 camera motion capture system (Vicon T-series, Oxford Metrics, UK; 250 Hz).
The last dataset comes from a project investigating the influence of strength training on load carriage running biomechanics (n=31n=31) ( [Liew et al., 2016a](https://arxiv.org/html/2312.05523v1#bib.bib107 "")). Participants performed overground running at a fixed velocity of 3.5 m/s (±\\pm10%) while carrying two load conditions (0%, 20% BW). Motion capture equipment was identical to [Liew et al. (2016a)](https://arxiv.org/html/2312.05523v1#bib.bib107 "").

For all datasets, three-dimensional (3D) bilateral lower-limb kinematics (joint angle, velocity, acceleration) and kinetics (moments) of the ankle, knee, and hip joints were extracted as variables, which yields 3×4×3=363\\times 4\\times 3=36 variables as the combinations of the entries in the first three columns of Table [1](https://arxiv.org/html/2312.05523v1#S1.T1 "Table 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"). All kinematic and moment variables were time normalized to 101 data points within the stance phase of each lower limb. The joint moment was normalized to body mass (N/kg).

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| body part | kinematics/kinetics | axis | resp. | type of motion |
| anklehipknee | acceleration (degreesec2)\\left(\\frac{\\text{degree}}{\\text{sec}^{2}}\\right) | anterior-posteriormedial-lateralvertical |  | inversion-eversion (ankle) /abduction-adduction (hip, knee)plantarflexion-dorsiflexion (ankle) /flexion-extension (hip, knee)abduction-adduction (ankle) /axial rotation (hip, knee) |
| angle (degree) |  |
| moment (NmKg)\\left(\\frac{\\text{Nm}}{\\text{Kg}}\\right) |  |
| velocity (degreesec)\\left(\\frac{\\text{degree}}{\\text{sec}}\\right) |  |

Table 1: Variables available in the human motion and motor control data example, obtained as the combinations of ‘body part’, ‘kinematics/kinetics’, and ‘axis’; the latter also corresponds to specific types of motion, which may differ between body parts.

Figure 1: Knee axial rotation acceleration measurements (left) with colors corresponding to the maximum moment, and hip abduction–adduction acceleration profiles (right) with colors corresponding to subjects’ sex.

For illustration, Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) shows the knee flexion-extension acceleration (divided by 10,000) across the stance phase of running for all participants from the second study ( [Liew et al., 2016b](https://arxiv.org/html/2312.05523v1#bib.bib108 "")), when running at 3 m/s with no backpack. Colors correspond to the maximum moment. One goal of the data analysis could be to investigate how acceleration profiles relate to the often-used scalar quantity ‘maximum moment’. In the right panel of Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"), the hip abduction-adduction acceleration is shown for females (solid blue) and males (dashed black). Here, it could be interesting to study if and where males and females differ in their profiles.

The remainder of this paper is structured as follows. We first introduce fundamental aspects of functional data in Section [2](https://arxiv.org/html/2312.05523v1#S2 "2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments") including descriptive analysis methods, smoothing approaches, amplitude and phase variation, and functional principal component analysis. In Section [3](https://arxiv.org/html/2312.05523v1#S3 "3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") we then summarize different parametric and non-parametric regression approaches before discussing methods for statistical inference with functional data in Section [4](https://arxiv.org/html/2312.05523v1#S4 "4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"). Methods beyond regression such as classification and clustering are considered in Section [5](https://arxiv.org/html/2312.05523v1#S5 "5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") followed by an outline of machine and deep learning approaches in Section [6](https://arxiv.org/html/2312.05523v1#S6 "6 Machine Learning Approaches ‣ Functional Data Analysis:An Introduction and Recent Developments"). In a final outlook section (Section [7](https://arxiv.org/html/2312.05523v1#S7 "7 Outlook ‣ Functional Data Analysis:An Introduction and Recent Developments")) we briefly discuss relationships of FDA to other fields, as well as FDA beyond one-dimensional functional observations. All sections are complemented with a selection of existing software packages that implement the respective approaches.

## 2 Fundamentals

### 2.1 Descriptives and Outliers

The first step in FDA usually is a descriptive analysis of the data, including visualizations and potentially the identification of outlying observations that may be influential in the analysis. For scalar data, this is relatively straightforward using tools such as a boxplot. For functional data, the task is more complex. In particular, outlying curves can differ from the majority of the sample by the range of their function values (“magnitude outliers”) and/or by their shape (“shape outliers”) ( [Hyndman and Shang, 2010](https://arxiv.org/html/2312.05523v1#bib.bib85 ""), see).

It is thus first necessary to define a notion of outlyingness or centrality of such data, which can be done using so-called functional data depths, of which different versions exist. [Sun and Genton (2011)](https://arxiv.org/html/2312.05523v1#bib.bib190 "") use the band-depth or modified band-depth of [López-Pintado and Romo (2009)](https://arxiv.org/html/2312.05523v1#bib.bib113 ""), which looks at the fraction of bands between pairs of other curves in the sample that contain (part of) a given curve, to define a functional boxplot. The sample median then is the curve with the highest functional depth, whereas the 50% central region (corresponding to the inter-quartile range of a standard boxplot) is defined to envelop the 50% most central curves in the sample with the highest depth. This region is inflated by 1.5 to generate the analog of whiskers in the boxplot and any curve lying outside this region is flagged as an outlier.

Alternative visualizations include the rainbowplot, functional bagplot, and functional highest density region boxplot of [Hyndman and Shang (2010)](https://arxiv.org/html/2312.05523v1#bib.bib85 ""), which are built on corresponding versions for multivariate data for the first two scores of a functional principal analysis (see Section [2.4](https://arxiv.org/html/2312.05523v1#S2.SS4 "2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")), thus capturing only the two main modes of variation in the data. A simple visualization method can also be to color functions according to another variable of interest, e.g., to inform a regression analysis (compare Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"), left), or according to depth. The outliergram of [Arribas-Gil and Romo (2014)](https://arxiv.org/html/2312.05523v1#bib.bib2 "") specifically
aims to detect shape outliers. [Dai and Genton (2018)](https://arxiv.org/html/2312.05523v1#bib.bib32 "") discuss visualization and outlier detection for multivariate functional data.

For our running example, Figure [2](https://arxiv.org/html/2312.05523v1#S2.F2 "Figure 2 ‣ 2.1 Descriptives and Outliers ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments") shows an example rainbow plot and functional bagplot for the knee axial rotation acceleration profiles of Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) obtained using the rainbow R package. Note that the functional depth measure in both plots uses only the first two functional principal components (compare Section [2.4](https://arxiv.org/html/2312.05523v1#S2.SS4 "2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) and thus only captures about 62% of the variation in the functional data.

Figure 2: Rainbow plot
for the knee axial rotation acceleration profiles from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) with yellow colors indicating low and red high functional depth; sample median given in black in both plots, with 95% pointwise confidence intervals (right); functional bagplot with 50% inner region and 99% fence region shaded in dark and light gray, respectively, and flagged outlying curves highlighted in color (right).

### 2.2 Smoothing for functional data

Functional data is in practice observed on finite grids – which may be curve-specific – and commonly with measurement error. A typical model for the observations thus is
Xi​(ti​l)=X~i​(ti​l)+εi​lX\_{i}(t\_{il})=\\widetilde{X}\_{i}(t\_{il})+\\varepsilon\_{il},
where Xi​(ti​l)X\_{i}(t\_{il}) constitutes the observable value at ti​l∈𝒯,l=1,…,Li,i=1,…,nt\_{il}\\in\\mathcal{T},l=1,\\dots,L\_{i},i=1,\\dots,n, X~i​(t)\\widetilde{X}\_{i}(t) is the underlying (smooth) function and εi​l\\varepsilon\_{il} are i.i.d. noise terms (compare Section [1.2](https://arxiv.org/html/2312.05523v1#S1.SS2 "1.2 Notation ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments")). As part of an analysis, it is often of interest to reconstruct the underlying “true” curves X~i​(t)\\widetilde{X}\_{i}(t).

The earliest approaches in functional data analysis usually do this reconstruction as an initial step using presmoothing of the curves ( [Ramsay and Silverman, 2005](https://arxiv.org/html/2312.05523v1#bib.bib156 "")).
For a given curve ii, we can view
Xi​(ti​l)=X~i​(ti​l)+εi​lX\_{i}(t\_{il})=\\widetilde{X}\_{i}(t\_{il})+\\varepsilon\_{il} with i.i.d. noise εi​l\\varepsilon\_{il}
as a nonparametric regression problem and use corresponding approaches for scatterplot smoothing. Typical methods used include kernel smoothing, local polynomial smoothing, and spline or penalized spline approaches ( [Ramsay and Silverman, 2005](https://arxiv.org/html/2312.05523v1#bib.bib156 "")).

For example, we can expand X~i=X~i​(⋅)\\widetilde{X}\_{i}=\\widetilde{X}\_{i}(\\cdot) in a spline basis, i.e., assume that it can be written or approximated (asymptotically) as a linear combination of spline basis functions ϕk\\phi\_{k}, k=1,…,Kk=1,\\dots,K,
and write

|     |     |     |     |
| --- | --- | --- | --- |
|  | Xi​(ti​l)=X~i​(ti​l)+εi​l=∑k=1Kϕk​(ti​l)​θi​k+εi​l.X\_{i}(t\_{il})=\\widetilde{X}\_{i}(t\_{il})+\\varepsilon\_{il}=\\sum\_{k=1}^{K}\\phi\_{k}(t\_{il})\\theta\_{ik}+\\varepsilon\_{il}. |  | (1) |

Unknown coefficients θi​k\\theta\_{ik} are estimated using a least squares or penalized least squares criterion, penalizing the integrated squared (e.g. second) derivative of the function to encourage smoothness or an approximation such as the finite differences of neighboring B-spline coefficients ( [Eilers and Marx, 2021](https://arxiv.org/html/2312.05523v1#bib.bib41 "")).

After presmoothing, the resulting curves are treated as if they were truly functional observations, i.e., fully observed curves. The advantage of this presmoothing approach is that theory and methods developed for observations that are truly functional ( [Dauxois et al., 1982](https://arxiv.org/html/2312.05523v1#bib.bib33 ""); [Bosq, 2000](https://arxiv.org/html/2312.05523v1#bib.bib10 ""), e.g.) can be directly applied. The clear disadvantage is that the uncertainty in estimating X~i​(t)\\widetilde{X}\_{i}(t) from noisy and discrete data is ignored in subsequent analysis steps. In particular, for sparse functional data, this source of uncertainty can be substantial and vary across curves depending on the number of available observation points. Also, smoothing can fail or not work well if only a few points for a curve are observed ( [Yao et al., 2005](https://arxiv.org/html/2312.05523v1#bib.bib215 "")).

Thus, more recent approaches have often worked with the observed data and incorporated one of the smoothing methods into the analysis itself, in particular for sparse functional data ( [Yao et al., 2005](https://arxiv.org/html/2312.05523v1#bib.bib215 "")). This has the clear advantage that the true information content of the data is acknowledged both in the analysis and the uncertainty quantification. Also, and importantly, such an approach allows “borrowing of strength” across functions, which is particularly useful in the case of sparse functional data.
This approach was spearheaded by [Yao et al. (2005)](https://arxiv.org/html/2312.05523v1#bib.bib215 "") for the case of functional principal component analysis discussed in Section [2.4](https://arxiv.org/html/2312.05523v1#S2.SS4 "2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments") below, where smoothing is incorporated in the estimation of the covariance function. Similar ideas were then included in other methods for functional data, such as in regression ( [Scheipl et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib168 ""); [Greven and Scheipl, 2017](https://arxiv.org/html/2312.05523v1#bib.bib65 ""); [Goldsmith et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib63 ""), e.g.). We will introduce these approaches in the corresponding sections.

A further approach that is similar to presmoothing is to expand the functions in a basis prior to analysis and subsequently work with the multivariate vector of basis coefficients instead of the presmoothed functions. If the basis transformation is loss-less, as can be the case for, e.g., wavelets and functions on regular grids ( [Morris and Carroll, 2006](https://arxiv.org/html/2312.05523v1#bib.bib133 "")), this approach can be equivalent to working with the functions (up to potential simplifying assumptions in the subsequent model such as independence between coefficients). For splines ( [Ramsay and Silverman, 2005](https://arxiv.org/html/2312.05523v1#bib.bib156 "")), this approach is very similar to presmoothing, and after the denoising usually the resulting uncertainty in curve reconstruction is also ignored.
Other approaches besides presmoothing that include some sort of denoising as preprocessing of functional data include functional principal component analysis ( [Goldsmith et al., 2011](https://arxiv.org/html/2312.05523v1#bib.bib59 ""), e.g.) or factor models ( [Hörmann and Jammoul, 2022](https://arxiv.org/html/2312.05523v1#bib.bib78 "")).

As data from our running example are already smooth, they can be nearly perfectly reconstructed using a B-spline basis expansion with a sufficient number of knots, e.g., K=30K=30. Figure [3](https://arxiv.org/html/2312.05523v1#S2.F3 "Figure 3 ‣ 2.2 Smoothing for functional data ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments") illustrates this for the first knee axial rotation acceleration profile using the fda package. On the left, a basis with only 10 basis functions is shown for better visibility. The reconstruction of the functional observation on the right with 30 basis functions is extremely close to the observed data points.

Figure 3: B-spline basis with 10 knots (left);
reconstruction (solid curve) of the first knee axial rotation acceleration profile (observed points as circles) with 30 B-spline basis functions (right).

### 2.3 Amplitude and phase variation

In functional data, we often observe two kinds of variation: _amplitude_ and _phase_ variation. When displaying functions by plotting xi​(t)x\_{i}(t) versus t∈𝒯t\\in\\mathcal{T}, these become visible as variations “along the y-axis” and “along the x-axis”, respectively. Typical examples are functions over time such as, e.g., growth curves ( [Ramsay and Silverman, 2005](https://arxiv.org/html/2312.05523v1#bib.bib156 "")), where there is variation both in the height (amplitude) of children as well as in the timing of growth spurts (phase). Further examples are functions over space such as, e.g., diffusion tensor imaging (DTI) measurements along different neuronal tracks in the brain ( [Greven et al., 2010](https://arxiv.org/html/2312.05523v1#bib.bib66 "")), where there is variation both in the fractional anisotropy measurement as a proxy for neuronal health (amplitude), as well as variation in the brain location corresponding to a given tt (phase), due to different proportions of anatomies and due to imprecisions in the measurement process. In our running example, phase variability is clearly visible, as maxima and minima in vertical knee acceleration are not aligned in Figures [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") and [2](https://arxiv.org/html/2312.05523v1#S2.F2 "Figure 2 ‣ 2.1 Descriptives and Outliers ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments"). This means that there is not only variation in the magnitude of acceleration between observations, but also in the timing of the acceleration pattern.

Ignoring phase variation in an analysis can lead to confounding effects between amplitude and phase and to less interpretable results. Intuitively speaking, in functional data analysis, we usually assume that the same argument tt corresponds across functions – e.g., corresponds to the same event in time or to the same location in space – and comparisons across functions per tt are thus sensible. If there is phase variation, this is no longer the case.
Depending on the context, it is thus often of interest to either (i) align functions before the analysis (of amplitude only) if phase variation is not of interest, which is also known as _registration_ or _warping_, or (ii) to separate amplitude and phase variation and analyze them separately or jointly.

Most existing approaches focus on (i), the registration or warping problem. If we want to align the functions xix\_{i}, e.g., to some overall mean μ\\mu, this can be formulated as finding suitable so-called _warping functions_ γi\\gamma\_{i} that monotonically map 𝒯\\mathcal{T} onto 𝒯\\mathcal{T}, such that xi​(γi​(t))x\_{i}(\\gamma\_{i}(t)) is optimally aligned to μ⁡(t)\\mu(t) for all t∈𝒯t\\in\\mathcal{T}. The γi\\gamma\_{i} then capture different “speeds” (phase) of the different functions xix\_{i} along the interval 𝒯\\mathcal{T}.
Traditionally (e.g. [Ramsay and Silverman, 2005](https://arxiv.org/html/2312.05523v1#bib.bib156 ""), Ch. 7), registration has often been performed by matching certain landmarks – e.g., maxima, minima, zero-crossings, or corresponding values for derivatives – across functions and linearly interpolating γi\\gamma\_{i} in between. This approach is simple and works reasonably well in the case of clearly defined and equal numbers of such landmarks.
More sophisticated approaches take the whole function into account and often work with minimizing the ℒ2\\mathcal{L}^{2} distance between one function xjx\_{j} and a second aligned function xix\_{i} over γ\\gamma, i.e.,

|     |     |     |     |
| --- | --- | --- | --- |
|  | infγ‖xi∘γ−xj‖ℒ22=infγ∫𝒯(xi​(γ⁡(t))−xj​(t))2​𝑑t.\\inf\_{\\gamma}\\\|x\_{i}\\circ\\gamma-x\_{j}\\\|^{2}\_{\\mathcal{L}^{2}}=\\inf\_{\\gamma}\\int\_{\\mathcal{T}}(x\_{i}(\\gamma(t))-x\_{j}(t))^{2}dt. |  | (2) |

In addition to not being symmetric, i.e., warping xix\_{i} to xjx\_{j} and warping xjx\_{j} to xix\_{i} are not equivalent, this approach carries the so-called _pinching problem_( [Marron et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib121 "")). This means that the distance ( [2](https://arxiv.org/html/2312.05523v1#S2.E2 "In 2.3 Amplitude and phase variation ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) can become small or zero even if xix\_{i} and xjx\_{j} are not warped versions of each other, by using a warping function γ\\gamma that compresses areas of 𝒯\\mathcal{T} where xix\_{i} and xjx\_{j} are dissimilar and expands those where they are close, resulting in spiky warping functions. Regularization or Bayesian approaches
( [Ramsay and Li, 1998](https://arxiv.org/html/2312.05523v1#bib.bib155 ""); [Ramsay and Silverman, 2005](https://arxiv.org/html/2312.05523v1#bib.bib156 ""); [Lu et al., 2017](https://arxiv.org/html/2312.05523v1#bib.bib114 ""); [Matuk et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib127 ""), e.g.)
restrict the amount of warping possible, but can only partially solve this problem. [Srivastava et al. (2010a)](https://arxiv.org/html/2312.05523v1#bib.bib182 "") thus proposed to work with the so-called _elastic distance_ instead, the Fisher-Rao-metric optimized over warping. This distance can be shown to simplify to the ℒ2{\\mathcal{L}^{2}} distance in ( [2](https://arxiv.org/html/2312.05523v1#S2.E2 "In 2.3 Amplitude and phase variation ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) for the optimally aligned square-root-velocity transformed curves Q​(xi)​(t)Q({x}\_{i})(t) and Q​(xj)​(t)Q({x}\_{j})(t), which simplifies computations. Here,
Q⁡(xi)​(t)=x˙i​(t)/\|x˙i​(t)\|Q({x}\_{i})(t)={\\dot{x}\_{i}(t)}/{\\sqrt{\|\\dot{x}\_{i}(t)\|}} (if x˙i​(t)≠0\\dot{x}\_{i}(t)\\neq 0, else Q​(xi)​(t)=0Q({x}\_{i})(t)=0) for the first derivative x˙\\dot{x} of xx.
The elastic distance constitutes a proper distance between functions modulo warping (and level due to the derivative) and avoids the pinching problem. It can thus be used to align functions or to obtain e.g. a mean estimate after alignment, by taking out all information about phase. Approaches for computations with sparsely observed (multivariate) functional data have also been developed ( [Steyer et al., 2023a](https://arxiv.org/html/2312.05523v1#bib.bib185 "")).

In some settings, phase is of interest as well. Some more recent approaches thus consider a joint analysis of both phase and amplitude, i.e., point (ii) above, e.g., in the context of functional principal component analysis (cf. Section [2.4](https://arxiv.org/html/2312.05523v1#S2.SS4 "2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) ( [Happ et al., 2019](https://arxiv.org/html/2312.05523v1#bib.bib74 "")) or regression (cf. Section [3](https://arxiv.org/html/2312.05523v1#S3 "3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) ( [Hadjipantelis et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib71 "")).

In our running example, there is a clear misalignment of maxima and minima between functions. As the number of maxima and minima can differ between functions, simple warping approaches based on landmarks do not work well here. Figure [4](https://arxiv.org/html/2312.05523v1#S2.F4 "Figure 4 ‣ 2.3 Amplitude and phase variation ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments") shows the knee axial rotation acceleration profiles from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) before and after elastic alignment using the time\_warping function in R package fdasrvf, together with the warping functions transforming the time for alignment.
Note that warping functions (up to numerics) are centered around the identity line.
Plotted are also the means of the unaligned and aligned functions in black. After the alignment, the mean shows more pronounced peaks and valleys, as it is no longer averaging over functions with their maxima and minima at different time points, and thus better represents the functions in the data.

Figure 4: Knee axial rotation acceleration profiles from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) with their mean function in black (left); same functions iteratively aligned to their mean given at the end of the algorithm in black (middle); warping functions warping the original time to the aligned time (right).

### 2.4 Functional principal component analysis

Functional principal component (FPC) analysis is an important tool in FDA as it allows dimension reduction of at least in theory infinite-dimensional functional data to manageable finite vectors of FPC scores.
It is based on the Karhunen-Loéve expansion ( [Karhunen, 1947](https://arxiv.org/html/2312.05523v1#bib.bib93 ""); [Loeve, 1945](https://arxiv.org/html/2312.05523v1#bib.bib112 "")), which allows us to expand a random function, i.e., a stochastic process, XX over 𝒯\\mathcal{T} as

|     |     |     |     |
| --- | --- | --- | --- |
|  | X⁡(t)=μ⁡(t)+∑m=1∞ξm​ϕm​(t),t∈𝒯,X(t)=\\mu(t)+\\sum\_{m=1}^{\\infty}\\xi\_{m}\\phi\_{m}(t),\\quad t\\in\\mathcal{T}, |  | (3) |

where μ\\mu is the mean function of XX and ϕm\\phi\_{m} are orthonormal eigenfunctions of the covariance, with ∫𝒯ϕm​(t)​ϕk​(t)​𝑑t=1\\int\_{\\mathcal{T}}\\phi\_{m}(t)\\phi\_{k}(t)dt=1 iff k=mk=m and =0=0 otherwise. In particular, according to Mercer’s theorem ( [Mercer, 1909](https://arxiv.org/html/2312.05523v1#bib.bib130 "")),

|     |     |     |     |
| --- | --- | --- | --- |
|  | Cov⁡(X⁡(s),X⁡(t))=∑m=1∞νm​ϕm​(s)​ϕm​(t),{\\operatorname{Cov}}(X(s),X(t))=\\sum\_{m=1}^{\\infty}\\nu\_{m}\\phi\_{m}(s)\\phi\_{m}(t), |  | (4) |

with decreasing eigenvalues ν1≥ν2≥⋯≥0\\nu\_{1}\\geq\\nu\_{2}\\geq\\dots\\geq 0.
Furthermore, ξm\\xi\_{m} are uncorrelated random scores with mean zero and variance νm\\nu\_{m}, m=1,2,…m=1,2,\\dots, and are independent normal if XX is a Gaussian process.

Truncating the sum in ( [3](https://arxiv.org/html/2312.05523v1#S2.E3 "In 2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) at a finite upper limit MM gives the best approximation to XX with MM basis functions in terms of mean-square prediction error ( [Rice and Silverman, 1991](https://arxiv.org/html/2312.05523v1#bib.bib161 "")). This allows for a parsimonious representation that approximates a sample XiX\_{i}, i=1,…,ni=1,\\dots,n, of independent replicates of XX with finitely many functions ϕm\\phi\_{m} common to all observations, and individual scores ξm,i\\xi\_{m,i} that capture the function-specific deviations from the overall mean. As the components have decreasing importance as measured by νm\\nu\_{m}, the first few components often capture most of the relevant features in the data. Looking at the fraction ∑m=1Mνm/∑m=1∞νm\\sum\_{m=1}^{M}\\nu\_{m}/\\sum\_{m=1}^{\\infty}\\nu\_{m} allows a quantitative assessment of the (integrated) variance explained by the approximation, and a choice of MM to explain, e.g., 95% or 99% of the overall variance.

Functional principal component analysis (FPCA) estimates μ\\mu, the ξm,i,νm\\xi\_{m,i},\\nu\_{m} and ϕm\\phi\_{m} in practice from a sample of curves taken to be realizations xix\_{i} of independent copies of ( [3](https://arxiv.org/html/2312.05523v1#S2.E3 "In 2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")), i.e., Xi​(t)=μ⁡(t)+∑m=1∞ξm,i​ϕm​(t)X\_{i}(t)=\\mu(t)+\\sum\_{m=1}^{\\infty}\\xi\_{m,i}\\phi\_{m}(t). Usually, a smoothness assumption is incorporated for the estimation of the ϕm\\phi\_{m}, which can be done in several ways. We here briefly describe an approach based on [Yao et al. (2005)](https://arxiv.org/html/2312.05523v1#bib.bib215 "") that accommodates sparsely observed functions with additional white noise errors ϵi​t\\epsilon\_{it} and thus works relatively generally. As in this setting presmoothing the observed functions xix\_{i} or computing the scores using numerical integration based on ξm,i=∫𝒯(Xi​(t)−μ⁡(t))​ϕm​(t)​𝑑t\\xi\_{m,i}=\\int\_{\\mathcal{T}}(X\_{i}(t)-\\mu(t))\\phi\_{m}(t)dt does not work well, the idea is to incorporate smoothing into the estimation of the covariance in ( [4](https://arxiv.org/html/2312.05523v1#S2.E4 "In 2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")). After estimation of μ⁡(t)\\mu(t) by μ^​(t)\\hat{\\mu}(t), and detrending x~i​(t)=xi​(t)−μ^​(t)\\tilde{x}\_{i}(t)=x\_{i}(t)-\\hat{\\mu}(t), estimation is based on the cross-products of observed points within curves, x~i​(ti​j)​x~i​(ti​k)\\tilde{x}\_{i}(t\_{ij})\\tilde{x}\_{i}(t\_{ik}), which are roughly unbiased estimates of Cov⁡(X⁡(ti​j),X⁡(ti​k)){\\operatorname{Cov}}(X(t\_{ij}),X(t\_{ik})). All cross-products are pooled and a smoothing method of choice is used for bivariate smoothing – local polynomial smoothing in [Yao et al. (2005)](https://arxiv.org/html/2312.05523v1#bib.bib215 ""), penalized spline smoothing in the refund R package ( [Goldsmith et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib63 "")), with further improvements for the particular case of covariance smoothing regarding speed and symmetry proposed e.g. in [Xiao et al. (2013)](https://arxiv.org/html/2312.05523v1#bib.bib214 ""); [Cederbaum et al. (2018)](https://arxiv.org/html/2312.05523v1#bib.bib18 ""). If an additional error is assumed, the diagonal cross-products approximate Cov⁡(X⁡(ti​j),X⁡(ti​j)){\\operatorname{Cov}}(X(t\_{ij}),X(t\_{ij})) plus the error variance, the diagonal is thus left out for smoothing and the error variance estimated from the difference of the smooth diagonal and the average (possibly boundary-trimmed) diagonal cross-products.

Once the smooth covariance is available, the orthogonal decomposition ( [4](https://arxiv.org/html/2312.05523v1#S2.E4 "In 2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) is typically done numerically on a fine grid using the usual matrix eigendecomposition. Eigenvectors are then rescaled to approximate orthonormality of the ϕm\\phi\_{m} with respect to the functional ℒ2{\\mathcal{L}^{2}} norm rather than the Euclidean vector norm. Finally, the scores ξm,i\\xi\_{m,i} are estimated. In the dense case, this could be based on ξm,i=∫𝒯(Xi​(t)−μ⁡(t))​ϕm​(t)​𝑑t\\xi\_{m,i}=\\int\_{\\mathcal{T}}(X\_{i}(t)-\\mu(t))\\phi\_{m}(t)dt with the estimated eigenfunctions and numerical integration. In the sparse case, where numerical integration based on only a few grid points does not give good results, it is preferable to work with conditional expectations ( [Yao et al., 2005](https://arxiv.org/html/2312.05523v1#bib.bib215 "")) of the ξm,i\\xi\_{m,i} given the data. Another way of looking at this is viewing equation ( [3](https://arxiv.org/html/2312.05523v1#S2.E3 "In 2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) truncated to MM eigenfunctions as a linear mixed model with random effects ξ1,i,…,ξM,i\\xi\_{1,i},\\dots,\\xi\_{M,i}, which can be assumed to be uncorrelated and thus have diagonal covariance matrix due to the Karhunen-Loève expansion ( [Greven et al., 2010](https://arxiv.org/html/2312.05523v1#bib.bib66 ""); [Goldsmith et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib60 ""); [Scheipl et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib168 ""), e.g.). The eigenfunctions ϕm\\phi\_{m} take the place of, e.g., a constant function and a linear function for a random intercept random slope model, thus allowing for more modeling flexibility with data-driven basis functions. The conditional expectations then correspond to the usual best linear unbiased prediction of the random effects.

The estimated scores 𝝃i=(ξ1,i,…,ξM,i)⊤\\boldsymbol{\\xi}\_{i}=(\\xi\_{1,i},\\dots,\\xi\_{M,i})^{\\top} give a multivariate summary vector of the individual functions that provides dimension reduction and enables many methods developed for multivariate data to be transferred to functional data. In addition, the estimated approximation
μ^​(t)+∑m=1Mξ^m,i​ϕ^m​(t)\\hat{\\mu}(t)+\\sum\_{m=1}^{M}\\hat{\\xi}\_{m,i}\\hat{\\phi}\_{m}(t) allows predicting the whole function even from sparse individual data, by pooling of information across functions. [Goldsmith et al. (2013)](https://arxiv.org/html/2312.05523v1#bib.bib60 "") provide confidence bands for the individual functions based on this approach that additionally take the uncertainty in the estimated eigendecomposition into account.

In our running example, the first four functional principal components explain about 83% of the total variation of the first knee axial rotation acceleration profiles, as shown in Figure [5](https://arxiv.org/html/2312.05523v1#S2.F5 "Figure 5 ‣ 2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments"). The importance decreases quickly, with the 5th to 7th FPCs only explaining further 6%, 4%, and 2%, respectively. Positive scores for the first FPC mostly indicate more pronounced movements with higher peaks and lower valleys, and scores for this component tend to be slightly higher for females. The second FPC contrasts more pronounced movements at different times during the whole movement. Please note that FPCs are only unique up to sign, and FPCs and corresponding scores could also be flipped compared to the output of function fpca.face in R package refund in case this allowed for simpler interpretation. We here rescaled the fpca.face output to ensure orthonormality of estimated eigenfunctions with respect to the ℒ2\\mathcal{L}^{2} instead of the vector inner product, please see the code on Github for details.
Also note that clearly the eigenfunctions are picking up some of the phase variability in the data that we already saw in Figure [4](https://arxiv.org/html/2312.05523v1#S2.F4 "Figure 4 ‣ 2.3 Amplitude and phase variation ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments"), such that an alternative FPCA would first align the functions and then analyse either the main directions of variation in the aligned data or in the aligned data and warping functions jointly.

Figure 5: First four functional principal components (FPCs, bottom left)
with the percentage of explained variation in the knee axial rotation acceleration profiles from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"); mean function plus/minus ν^1\\sqrt{\\hat{\\nu}\_{1}} times the first FPC (top left) respectively ν^2\\sqrt{\\hat{\\nu}\_{2}} times the second FPC (top right); scatterplot of second against first FPC scores (bottom right). Note that νm\\sqrt{\\nu\_{m}} corresponds to the standard deviation of the mmth score ξm\\xi\_{m}, m=1,2m=1,2.

Given its centrality as a tool for dimension reduction and to obtain a parsimonious empirical basis, there are several extensions of FPCA to more complex settings.
Multivariate functional principal component analysis extends FPCA to multivariate functional data. These could be several functions observed over 𝒯\\mathcal{T} such that the setting is that of vector-valued functional data ( [Chiou et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib27 ""), e.g.). Or it could be several functions observed potentially over different domains. [Happ and Greven (2018)](https://arxiv.org/html/2312.05523v1#bib.bib73 "") develop this setting, with an example of one function being a sparsely observed longitudinal trajectory over time and another being a 2D or 3D image, and provide a link between the univariate and multivariate FPCAs that simplifies estimation.
Covariate-dependent FPCA is, for instance, considered by [Ding et al. (2022)](https://arxiv.org/html/2312.05523v1#bib.bib38 "").
[Di et al. (2009)](https://arxiv.org/html/2312.05523v1#bib.bib37 ""), [Greven et al. (2010)](https://arxiv.org/html/2312.05523v1#bib.bib66 ""), and [Shou et al. (2015)](https://arxiv.org/html/2312.05523v1#bib.bib179 "") develop multilevel FPCA extensions for settings where functions are, e.g., repeatedly observed within observational units such as subjects, and where a FPCA decomposition is desired of both the within-subject and the between-subject functional variation.
In the case of correlated functional data, we cannot view the XiX\_{i} as independent copies of ( [3](https://arxiv.org/html/2312.05523v1#S2.E3 "In 2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")). Extensions of FPCA have thus also been developed, e.g., for functional time series and functions observed repeatedly over time ( [Chen and Müller, 2012](https://arxiv.org/html/2312.05523v1#bib.bib24 ""); [Panaretos and Tavakoli, 2013](https://arxiv.org/html/2312.05523v1#bib.bib140 ""); [Park and Staicu, 2015](https://arxiv.org/html/2312.05523v1#bib.bib143 ""), e.g.), using a double decomposition in both the time dimension and the tt dimension.

### 2.5 Software

The Comprehensive R Archive Network (CRAN) ( [R Core Team, 2023](https://arxiv.org/html/2312.05523v1#bib.bib153 "")) contains a “Task View: Functional Data Analysis” listing most R packages related to functional data analysis. We here name some of the packages implementing methods mentioned in the previous subsections.

For descriptives and outlier detection (Section [2.1](https://arxiv.org/html/2312.05523v1#S2.SS1 "2.1 Descriptives and Outliers ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")), the functional boxplot of ( [Sun and Genton, 2011](https://arxiv.org/html/2312.05523v1#bib.bib190 "")) is implemented in the function fbplot in the R package fda( [Ramsay et al., 2022](https://arxiv.org/html/2312.05523v1#bib.bib158 "")). The rainbow package ( [Shang and Hyndman, 2022](https://arxiv.org/html/2312.05523v1#bib.bib175 "")) can be used to obtain functional bagplots, boxplots, and rainbow plots ( [Hyndman and Shang, 2010](https://arxiv.org/html/2312.05523v1#bib.bib85 "")). fdaoutlier( [Ojo et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib137 "")) provides a collection of functions for functional data outlier detection.

For smoothing of curves (Section [2.2](https://arxiv.org/html/2312.05523v1#S2.SS2 "2.2 Smoothing for functional data ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")), many methods developed for scatterplot smoothing can be used to presmooth functions. The fda package provides functionality to expand observed functions in bases such as, e.g., B-splines. A very flexible R package for smoothing in general is the mgcv package ( [Wood, 2017](https://arxiv.org/html/2312.05523v1#bib.bib212 "")). Further packages build smoothing into the analysis, such as, e.g., into the estimation of covariances for FPCA as discussed below.

For warping/alignment of functions and separation of their amplitude and phase (Section [2.3](https://arxiv.org/html/2312.05523v1#S2.SS3 "2.3 Amplitude and phase variation ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")), elastic options based on the square-root-velocity framework are implemented in R packages fdasrvf( [Tucker, 2023](https://arxiv.org/html/2312.05523v1#bib.bib199 "")) for functions with the same number of sample points and in elasdics( [Steyer, 2022](https://arxiv.org/html/2312.05523v1#bib.bib184 "")) for irregularly or sparsely observed (multivariate) functions. The fda package offers several alternative options based, e.g., on landmarks.

For FPCA (Section [2.4](https://arxiv.org/html/2312.05523v1#S2.SS4 "2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) of univariate functional data, different packages offer options based on covariance smoothing and conditional expectations for the scores. Function FPCA in R package fdapace( [Zhou et al., 2022](https://arxiv.org/html/2312.05523v1#bib.bib223 "")) uses local polynomial smoothing, while several functions in R package refund( [Goldsmith et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib63 "")) use penalized spline smoothing, such as fpca.sc and fpca.face with the faster FACE method. ccb.fpc provides corrected confidence bands for the predicted functions incorporating uncertainty in estimated FPCs ( [Goldsmith et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib60 "")). R package MFPCA( [Happ-Kurz, 2022](https://arxiv.org/html/2312.05523v1#bib.bib75 "")) implements FPCA for multivariate functional data ( [Happ and Greven, 2018](https://arxiv.org/html/2312.05523v1#bib.bib73 "")).

## 3 Functional Regression

### 3.1 Introduction/Overview

We call a regression problem ‘functional regression’ if at least one functional variable is found on the left and/or right-hand side of the model equation. This means that functional variables may be the response, covariate(s), or both. To distinguish the different settings, we use the terms ‘scalar-on-function(s)’ regression, ‘function-on-scalar’ regression, and ‘function-on-function(s)’ regression, respectively. In what follows, we will first give an overview of those three settings. Then, we will describe two popular strategies for statistical modeling, inference, and prediction, namely semi-parametric models using basis functions, and non-parametric approaches using kernels. We will focus on the former, semi-parametric models and basis functions here because results are easier to interpret (from our point of view). In addition to the ‘statistical’ approaches described in Section [3](https://arxiv.org/html/2312.05523v1#S3 "3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), also methods borrowed from and inspired by the machine learning community can be used, which will be discussed in more detail in Section [6](https://arxiv.org/html/2312.05523v1#S6 "6 Machine Learning Approaches ‣ Functional Data Analysis:An Introduction and Recent Developments").

#### 3.1.1 Scalar-on-Functions Regression (SOFR)

‘Scalar-on-function(s)’ regression corresponds to the case that the response is scalar, and among the covariates, there is at least one functional variable. In the simplest case, there is only a single covariate, which is functional. For instance, Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) showed knee axial rotation acceleration with colors corresponding to the maximum moment. For illustration, we may try to explain/predict the latter using the acceleration profiles. Then the simplest, but probably still the most popular model for scalar-on-function regression is the so-called _functional linear model_

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi=α+∫𝒯xi(t)β(t)dt+ϵi,i=1,…,n,Y\_{i}=\\alpha+\\int\_{\\mathcal{T}}x\_{i}(t)\\beta(t)\\,dt+\\epsilon\_{i},\\quad i=1,\\ldots,n, |  | (5) |

where β\\beta is the so-called _coefficient function_, YiY\_{i} is the (scalar) response and xix\_{i} is the functional covariate observed for subject/unit ii (such as the curves shown in Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"), left). As in the classical linear model with both scalar covariate(s) and response, it is typically assumed that xix\_{i} is set by the experimenter, or if the covariate is, in fact, a random variable, we take the ‘conditional view’ in terms of modeling YiY\_{i} given Xi=xiX\_{i}=x\_{i}. With functional data, however, it is usually the latter. Assumptions for the error term ϵi\\epsilon\_{i} are typically also the same as in the classical linear model. Thus, ϵi\\epsilon\_{i} are assumed to be i.i.d. (scalar) random variables with mean zero and constant variance σ2\\sigma^{2}, and sometimes the additional assumption of normality is made. The latter can, for instance, be relevant when using likelihood-based approaches for estimating unknown model parameters (compare Section [3.2.1](https://arxiv.org/html/2312.05523v1#S3.SS2.SSS1 "3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") below). When interpreting the results after fitting model ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) to the data at hand, the coefficient function β\\beta is particularly important, analogously to the β\\beta-coefficient(s) in the standard linear model, see the examples below.

As pointed out above, the functional linear model ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) is the simplest model for scalar-on-function regression. However, as in the scalar case, it can be seen as the starting point for numerous generalizations and extensions. The most obvious extension is including scalar covariates Z1,…,ZqZ\_{1},\\ldots,Z\_{q} and multiple functional covariates X1,…,XpX\_{1},\\ldots,X\_{p} with domains 𝒯1,…,𝒯p\\mathcal{T}\_{1},\\ldots,\\mathcal{T}\_{p}, respectively, leading to

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi=α+∑j=1p∫𝒯jxi​j(t)βj(t)dt+∑r=1qzi​rγr+ϵi,i=1,…,n,Y\_{i}=\\alpha+\\sum\_{j=1}^{p}\\int\_{\\mathcal{T}\_{j}}x\_{ij}(t)\\beta\_{j}(t)\\,dt+\\sum\_{r=1}^{q}z\_{ir}\\gamma\_{r}+\\epsilon\_{i},\\quad i=1,\\ldots,n, |  | (6) |

with further assumptions being analogous to ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")). In the case of the data shown in Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"), for instance, we should at least take the person’s sex into account by including a corresponding factor as an additional scalar covariate. When fitting the corresponding model using function pfr() from R package refund( [Goldsmith et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib63 "")), the coefficient function for the functional covariate ‘knee axial rotation acceleration’ as shown in Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) is obtained, together with approximate, pointwise 95% confidence intervals (shaded region). For modeling/fitting the coefficient function, we used a penalized, cubic spline with 15 (B-spline) basis functions and a penalty on the second-order differences of neighboring basis coefficients, a so-called _P-spline_( [Marx and Eilers, 1999](https://arxiv.org/html/2312.05523v1#bib.bib123 "")). For details on fitting and software, see Sections [3.2.1](https://arxiv.org/html/2312.05523v1#S3.SS2.SSS1 "3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") and [3.3](https://arxiv.org/html/2312.05523v1#S3.SS3 "3.3 Software ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), respectively. Further statistical inference, such as confidence intervals, is discussed in Section [4](https://arxiv.org/html/2312.05523v1#S4 "4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"). Qualitatively speaking, the interpretation of β⁡(t)\\beta(t) from Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) is as follows: (positive) values of knee acceleration at the beginning of the cycle have a positive effect on the maximum moment, whereas the association is negative at the end of the cycle, but uncertainty is very high in that area (as can be seen from the large confidence intervals). So, the main takeaway from this example is that people with large (positive) knee axial rotation acceleration at the beginning of the cycle tend to have a larger maximum moment than people with lower acceleration at the beginning of the cycle. This effect is also visible from the colors in Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left). In general, however, such findings are not necessarily possible from descriptive plots only, particularly if more than one covariate is present.

Figure 6: The estimated coefficient function in the functional linear model (left) when predicting the maximum moment using the knee axial rotation acceleration profiles from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left) and additional covariate ‘sex’, together with approximate, pointwise 95% confidence intervals (shaded region). The estimated coefficient function in the functional logit model with response ‘sex’ and functional covariate hip abduction-adduction acceleration from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (right) is given in the right panel.

If the error term ϵi\\epsilon\_{i} in ( [6](https://arxiv.org/html/2312.05523v1#S3.E6 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) is clearly non-Gaussian, e.g., because the response is binary, model ( [6](https://arxiv.org/html/2312.05523v1#S3.E6 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) can be generalized to a response variable with simple exponential-family distribution, analogously to the well-known generalized linear model (GLM). With functional covariates, we can define the linear predictor

|     |     |     |     |
| --- | --- | --- | --- |
|  | ηi=α+∑j=1p∫𝒯jxi​j(t)βj(t)dt+∑r=1qzi​rγr,i=1,…,n.\\eta\_{i}=\\alpha+\\sum\_{j=1}^{p}\\int\_{\\mathcal{T}\_{j}}x\_{ij}(t)\\beta\_{j}(t)\\,dt+\\sum\_{r=1}^{q}z\_{ir}\\gamma\_{r},\\quad i=1,\\ldots,n. |  | (7) |

Then, with μi=𝔼\[Yi\|Xi​1=xi​1,…,Xi​p=xi​p,Zi​1=zi​1,…,Zi​q=zi​q\]\\mu\_{i}={\\mathbb{E}}\[Y\_{i}\|X\_{i1}=x\_{i1},\\ldots,X\_{ip}=x\_{ip},Z\_{i1}=z\_{i1},\\ldots,Z\_{iq}=z\_{iq}\] being the conditional mean of the response given the covariates, ηi=g⁡(μi)\\eta\_{i}=g(\\mu\_{i}), and known link function g⁡(⋅)g(\\cdot), the _generalized functional linear model_, or _functional generalized linear model_ (both terms used in the literature) is obtained. Instead of the link function, the concrete model can be specified through the inverse link, the so-called response function h=g−1h=g^{-1}, in terms of μi=h⁡(ηi)\\mu\_{i}=h(\\eta\_{i}). Further extensions that relax the assumption of linearity in ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), ( [6](https://arxiv.org/html/2312.05523v1#S3.E6 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), or ( [7](https://arxiv.org/html/2312.05523v1#S3.E7 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) will be discussed in more detail in Section [3.2](https://arxiv.org/html/2312.05523v1#S3.SS2 "3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") below. A review entirely on scalar-on-function regression is found in [Reiss et al. (2017)](https://arxiv.org/html/2312.05523v1#bib.bib160 ""). For an illustration of the functional GLM ( [7](https://arxiv.org/html/2312.05523v1#S3.E7 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), we may try to identify the persons’ sex by looking at the hip acceleration profiles as shown in Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (right). The fitted coefficient function (again using pfr() from refund) in a functional logit model with response ‘sex’ (female: 0, male: 1) is given in the right panel of Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"). Again, we used a P-spline approach with 15 basis functions and a second-order penalty on the basis coefficients. In analogy to the usual logit model, the functional version is defined by the link function

|     |     |     |
| --- | --- | --- |
|  | g⁡(πi)=log⁡{πi1−πi},g(\\pi\_{i})=\\log\\left\\{\\frac{\\pi\_{i}}{1-\\pi\_{i}}\\right\\}, |  |

with πi=μi=P⁡(Yi=1\|Xi=xi)\\pi\_{i}=\\mu\_{i}=P(Y\_{i}=1\|X\_{i}=x\_{i}) being the conditional probability of person ii being male given the covariate curve (hip acceleration) xix\_{i}. Equivalently, the model is specified through the response function

|     |     |     |
| --- | --- | --- |
|  | πi=h⁡(ηi)=exp⁡(ηi)1+exp⁡(ηi).\\pi\_{i}=h(\\eta\_{i})=\\frac{\\exp(\\eta\_{i})}{1+\\exp(\\eta\_{i})}. |  |

As seen from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (right), males and females can be separated very well by looking at hip acceleration roughly between time points 0.7 and 0.8. Not surprisingly, the corresponding β\\beta-function shown in Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") (right) also has its clear maximum in that area, indicating that subjects with large/positive hip acceleration in that area tend to be men, whereas small/negative values typically correspond to females.

It should be noted, though, that the functional data shown in Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") is very smooth and measured on a dense and regular grid. In practice, however, functional data can be noisy and/or sparsely/irregularly sampled. In those cases, functional regression can be combined with (pre-)smoothing as discussed in Section [2](https://arxiv.org/html/2312.05523v1#S2 "2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments"), see also Section [3.2](https://arxiv.org/html/2312.05523v1#S3.SS2 "3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), or even joint (Bayesian) modeling of both YiY\_{i} and Xi​(t)X\_{i}(t)( [McLean et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib128 "")) to take uncertainty in the smooth underlying functions into account.

#### 3.1.2 Function-on-Scalar Regression (FOSR)

If the response Y⁡(t)Y(t), t∈𝒯t\\in\\mathcal{T} is functional, but all covariates X1,…,XpX\_{1},\\ldots,X\_{p} are scalar, the simplest model is the _linear function-on-scalar_ model

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi(t)=α(t)+∑j=1pxi​jβj(t)+ϵi(t),i=1,…,n,t∈𝒯,Y\_{i}(t)=\\alpha(t)+\\sum\_{j=1}^{p}x\_{ij}\\beta\_{j}(t)+\\epsilon\_{i}(t),\\quad i=1,\\ldots,n,\\;t\\in\\mathcal{T}, |  | (8) |

where α⁡(t)\\alpha(t) and βj​(t)\\beta\_{j}(t), j=1,…,pj=1,\\ldots,p are coefficient functions and ϵi​(t)\\epsilon\_{i}(t) is the error function drawn from a stochastic process with mean zero and covariance function Σ⁡(s,t)\\Sigma(s,t), s,t∈𝒯s,t\\in\\mathcal{T}; compare, e.g., [Chen et al. (2016)](https://arxiv.org/html/2312.05523v1#bib.bib25 ""). The latter assumption takes into account that measurements taken from the same individual ii at different time points, i.e., within-function errors, are typically correlated. This is important for proper statistical inference. [Chen et al. (2016)](https://arxiv.org/html/2312.05523v1#bib.bib25 ""), for instance, apply a “pre-whitening” step before estimating unknown regression parameters from ( [8](https://arxiv.org/html/2312.05523v1#S3.E8 "In 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) above. [Greven and Scheipl (2017)](https://arxiv.org/html/2312.05523v1#bib.bib65 ""), by contrast, decompose ϵi​(t)\\epsilon\_{i}(t) into a smooth, subject-specific functional random effect Ei​(t)E\_{i}(t) and remaining white noise error ϵi​t\\epsilon\_{it}. For illustration, let us revisit the data from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (right), but now treat hip acceleration as the (functional) response and sex as the (scalar) covariate with ‘female’ as the reference category. Then model ( [8](https://arxiv.org/html/2312.05523v1#S3.E8 "In 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) takes the simple form Yi​(t)=α⁡(t)+xi​β​(t)+ϵi​(t)Y\_{i}(t)=\\alpha(t)+x\_{i}\\beta(t)+\\epsilon\_{i}(t),
where α⁡(t)\\alpha(t) is the functional intercept and xix\_{i} is a dummy with xi=1x\_{i}=1 if subject ii is male, and xi=0x\_{i}=0 if ii is female. So α⁡(t)\\alpha(t) (see the corresponding estimate in Figure [7](https://arxiv.org/html/2312.05523v1#S3.F7 "Figure 7 ‣ 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), left) can also be interpreted here as the (functional) mean for females and β⁡(t)\\beta(t) (estimate in Figure [7](https://arxiv.org/html/2312.05523v1#S3.F7 "Figure 7 ‣ 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), right/black dashed) is the effect of being male. The error process ϵi​(t)\\epsilon\_{i}(t) is decomposed into a smooth, subject-specific functional random effect plus white noise error here ( [Greven and Scheipl, 2017](https://arxiv.org/html/2312.05523v1#bib.bib65 ""), compare). From Figure [7](https://arxiv.org/html/2312.05523v1#S3.F7 "Figure 7 ‣ 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") (right) it is seen that the first peak in the (mean) acceleration profiles is somewhat higher and wider for males and that males’ profiles tend to lie above the profiles of females around t=0.75t=0.75 (also compare Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"), right).

Figure 7: Estimated parameter functions when regressing hip abduction-adduction acceleration from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (right) on the person’s sex using model ( [8](https://arxiv.org/html/2312.05523v1#S3.E8 "In 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")); shown are the functional intercept (left) and the estimated effects (right) with colors corresponding to subjects’ sex, and approximate, pointwise 95% confidence intervals (dotted).

In general, besides ( [8](https://arxiv.org/html/2312.05523v1#S3.E8 "In 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), also more complicated models may be fitted in the semi-parametric framework. For instance, [Scheipl et al. (2015)](https://arxiv.org/html/2312.05523v1#bib.bib168 "") consider additive, smooth effects in terms of

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi(t)=α(t)+∑j=1pγj(xi​j,t)+ϵi(t),i=1,…,n,t∈𝒯.Y\_{i}(t)=\\alpha(t)+\\sum\_{j=1}^{p}\\gamma\_{j}(x\_{ij},t)+\\epsilon\_{i}(t),\\quad i=1,\\ldots,n,\\;t\\in\\mathcal{T}. |  | (9) |

This means that the effect of covariate XjX\_{j} is allowed to be non-linear and varying over tt.

#### 3.1.3 Function-on-Function Regression (FOFR)

If both the response and the covariate(s) are functional and assumed to be observed over the same domain 𝒯\\mathcal{T}, a small modification of ( [8](https://arxiv.org/html/2312.05523v1#S3.E8 "In 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) gives the so-called functional linear _concurrent_ model as

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi(t)=α(t)+∑j=1pxi​j(t)βj(t)+ϵi(t),i=1,…,n,t∈𝒯.Y\_{i}(t)=\\alpha(t)+\\sum\_{j=1}^{p}x\_{ij}(t)\\beta\_{j}(t)+\\epsilon\_{i}(t),\\quad i=1,\\ldots,n,\\;t\\in\\mathcal{T}. |  | (10) |

As a modification of ( [6](https://arxiv.org/html/2312.05523v1#S3.E6 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), with potentially different domains, we may introduce linear functional effects such that

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi(t)=α(t)+∑j=1p∫𝒮jxi​j(s)βj(s,t)ds+ϵi(t),i=1,…,n,Y\_{i}(t)=\\alpha(t)+\\sum\_{j=1}^{p}\\int\_{\\mathcal{S}\_{j}}x\_{ij}(s)\\beta\_{j}(s,t)\\,ds+\\epsilon\_{i}(t),\\quad i=1,\\ldots,n, |  | (11) |

where t∈𝒯t\\in\\mathcal{T}, and 𝒮j\\mathcal{S}\_{j} denotes the domain of the jjth functional covariate. Similarly as done in ( [9](https://arxiv.org/html/2312.05523v1#S3.E9 "In 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) above, ( [11](https://arxiv.org/html/2312.05523v1#S3.E11 "In 3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) may be relaxed to ( [Scheipl et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib168 ""))

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi(t)=α(t)+∑j=1p∫𝒮jFj(xi​j(s),s,t)ds+ϵi(t),i=1,…,n,Y\_{i}(t)=\\alpha(t)+\\sum\_{j=1}^{p}\\int\_{\\mathcal{S}\_{j}}F\_{j}(x\_{ij}(s),s,t)\\,ds+\\epsilon\_{i}(t),\\quad i=1,\\ldots,n, |  | (12) |

although this approach requires the estimation of three-dimensional smooths FjF\_{j} and is thus less often used in practice.

In particular, if the response and the covariates have the same time domain 𝒯\\mathcal{T}, it can also be relevant to allow for more general integration limits than in ( [11](https://arxiv.org/html/2312.05523v1#S3.E11 "In 3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")). This allows only (part of) the past of the covariates to affect the current value Yi​(t)Y\_{i}(t), but is more general than a concurrent effect as in ( [10](https://arxiv.org/html/2312.05523v1#S3.E10 "In 3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")). Common examples of such _historical_ effects replace ∫𝒮j\\int\_{\\mathcal{S}\_{j}} in ( [11](https://arxiv.org/html/2312.05523v1#S3.E11 "In 3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) by ∫0t\\int\_{0}^{t} or ∫t−ht\\int\_{t-h}^{t} for some lag h>0h>0; see [Brockhaus et al. (2017)](https://arxiv.org/html/2312.05523v1#bib.bib13 ""); [Rügamer et al. (2018)](https://arxiv.org/html/2312.05523v1#bib.bib165 "") for a more detailed discussion of different possible specifications.

### 3.2 Semi- and Fully Non-Parametric Approaches

We will start by giving some further insight into semi-parametric modeling of functional data by use of basis functions, as all models presented so far can be considered in this framework. Fully non-parametric approaches providing even larger flexibility in terms of the association structure between response and covariate(s) will be described in Subsection [3.2.2](https://arxiv.org/html/2312.05523v1#S3.SS2.SSS2 "3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments").

#### 3.2.1 Semi-parametric Models and the Basis Functions Approach

The idea here is very similar to presmoothing of functional data as given in ( [1](https://arxiv.org/html/2312.05523v1#S2.E1 "In 2.2 Smoothing for functional data ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")). The (unknown) coefficient functions, such as β\\beta in ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), are expanded in basis functions as

|     |     |     |     |
| --- | --- | --- | --- |
|  | β⁡(t)=∑k=1Kϕk​(t)​bk,\\beta(t)=\\sum\_{k=1}^{K}\\phi\_{k}(t)b\_{k}, |  | (13) |

where ϕk\\phi\_{k} could, e.g., be B-spline basis functions as shown in Figure [3](https://arxiv.org/html/2312.05523v1#S2.F3 "Figure 3 ‣ 2.2 Smoothing for functional data ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments") or the eigenbasis obtained via FPCA (compare Section [2.4](https://arxiv.org/html/2312.05523v1#S2.SS4 "2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")) of some functional data, typically the covariate functions; and bkb\_{k} are unknown basis coefficients that need to be estimated from the data. The integrals found in Section [3.1.1](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS1 "3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") and [3.1.3](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS3 "3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") are typically calculated/approximated through numerical integration. If considering the functional linear model ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), for instance, we have

|     |     |     |     |
| --- | --- | --- | --- |
|  | ∫𝒯xi​(t)​β​(t)​𝑑t≈∑v=1VΔ⁡(tv)​xi​(tv)​β​(tv),\\int\_{\\mathcal{T}}x\_{i}(t)\\beta(t)dt\\approx\\sum\_{v=1}^{V}\\Delta(t\_{v})x\_{i}(t\_{v})\\beta(t\_{v}), |  | (14) |

with a grid t1,…,tVt\_{1},\\ldots,t\_{V} of evaluation points in 𝒯\\mathcal{T} and suitable integration weights Δ⁡(tv)\\Delta(t\_{v}). If evaluation points are equidistant and reasonably dense, the simplest (but most often used) approximation is, up to a proportionality factor, given by ∑v=1Vx⁡(tv)​β​(tv)\\sum\_{v=1}^{V}x(t\_{v})\\beta(t\_{v}). Thus, many methods, such as signal regression as considered by [Marx and Eilers (1999)](https://arxiv.org/html/2312.05523v1#bib.bib123 ""), can be seen as functional regression. If choosing the basis functions approach in the (generalized) functional linear model (compare ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), ( [6](https://arxiv.org/html/2312.05523v1#S3.E6 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), or ( [7](https://arxiv.org/html/2312.05523v1#S3.E7 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"))), the functional model turns into a (generalized) linear model with the basis coefficients being the (unknown) regression coefficients that can be estimated using the usual methods for (generalized) linear models. If using basis functions like B-splines, however, typically, a large number of basis functions needs to be used to allow sufficient flexibility concerning the β\\beta-functions that can be fitted. With standard methods like least squares or maximum likelihood, the resulting coefficient functions then tend to over-fit the data while showing some erratic, non-smooth behavior. A popular fix is adding a penalty on the integrated squared (second) derivative(s) of the β\\beta-function(s) or a difference penalty on neighboring basis coefficients to encourage smoothness; compare Section [2.2](https://arxiv.org/html/2312.05523v1#S2.SS2 "2.2 Smoothing for functional data ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments") and below. The observed functional data, such as xi​(t)x\_{i}(t) in ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), might be taken as they are if they are reasonably smooth (compare, e.g., Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), or they may be presmoothed, e.g., by use of pre-chosen basis functions, FPCA, or other techniques (compare Section [2](https://arxiv.org/html/2312.05523v1#S2 "2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments")). On the one hand, the use of FPCA has the additional advantage that models ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), ( [6](https://arxiv.org/html/2312.05523v1#S3.E6 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) and ( [7](https://arxiv.org/html/2312.05523v1#S3.E7 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) then transform into a standard (generalized) linear model with FPCA scores as the covariates; compare, e.g., [Müller and Stadtmüller (2005)](https://arxiv.org/html/2312.05523v1#bib.bib135 "") and [Müller and Yao (2008)](https://arxiv.org/html/2312.05523v1#bib.bib136 ""). Since often a relatively small number of principal components suffices to capture the main information in the data, the number of unknown regression coefficients in the resulting functional model remains small as well, and further regularization is not necessary. Furthermore, regression on FPCA scores is convenient to generalize. For example, the scores can directly be used in an additive model where the influence of each score is allowed to be non-linear ( [Müller and Yao, 2008](https://arxiv.org/html/2312.05523v1#bib.bib136 "")). On the other hand, however, “the principal component scores are computed independently from the
response, in an unsupervised fashion, so there is no a priori reason to believe that these scores will correspond to the best dimensions for the regression problem” ( [Fan et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib43 "")), and additionally, the discrete parameter KK needs to be carefully chosen. Alternatives to additive regression on FPCA scores that induce nonlinear relationships, for instance, include functional index models ( [Fan et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib43 ""))

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi=α+∑j=1pgj(∫𝒯jxi​j(t)βj(t)dt)+ϵi,i=1,…,n,Y\_{i}=\\alpha+\\sum\_{j=1}^{p}g\_{j}\\left(\\int\_{\\mathcal{T}\_{j}}x\_{ij}(t)\\beta\_{j}(t)dt\\right)+\\epsilon\_{i},\\quad i=1,\\ldots,n, |  | (15) |

where both β\\beta\- and gg-functions are represented via basis functions and estimated in an iterative manner. Basis coefficients for β\\beta and gg are alternatingly updated while fixing the other set of coefficients at their current values, cycling through those two steps until convergence. Apparently, ( [15](https://arxiv.org/html/2312.05523v1#S3.E15 "In 3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) includes the functional linear model as a special case if all gg-functions are set to be the identity. As before, appropriate penalties can or should be included when fitting the basis coefficients of the β\\beta and/or gg-functions.

Analogous basis/penalty approaches can be used for FOSR and FOFR as introduced in Section [3.1.2](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS2 "3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") and [3.1.3](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS3 "3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"). In the additive model ( [9](https://arxiv.org/html/2312.05523v1#S3.E9 "In 3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) or the linear model ( [11](https://arxiv.org/html/2312.05523v1#S3.E11 "In 3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) for function-on-functions regression, however, the unknown functions (γj\\gamma\_{j} and βj\\beta\_{j}, respectively) have two arguments. This means that the basis needs to be chosen appropriately, e.g., as a so-called tensor product basis. If considering a single functional covariate in ( [11](https://arxiv.org/html/2312.05523v1#S3.E11 "In 3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), for instance, equation ( [13](https://arxiv.org/html/2312.05523v1#S3.E13 "In 3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) then turns into

|     |     |     |     |
| --- | --- | --- | --- |
|  | β⁡(s,t)=∑k=1K1∑l=1K2ϕk​(s)​ϕl​(t)​bk​l,\\beta(s,t)=\\sum\_{k=1}^{K\_{1}}\\sum\_{l=1}^{K\_{2}}\\phi\_{k}(s)\\phi\_{l}(t)b\_{kl}, |  | (16) |

and smoothing should typically be done in both ss\- and tt-direction.

As already pointed out, if using a rich basis such as a large number of B-splines, smoothing is typically carried out by adding a penalty when fitting the basis coefficients (such as those in ( [13](https://arxiv.org/html/2312.05523v1#S3.E13 "In 3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) and ( [16](https://arxiv.org/html/2312.05523v1#S3.E16 "In 3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"))), which prevents over-fitting and ensures interpretability of the resulting coefficient functions. In the simplest case, for instance, the functional linear model ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) with reasonably smooth functional covariate curves that are observed on a dense and regular grid t1,…,tVt\_{1},\\ldots,t\_{V}, fitting can be done by minimizing the penalized quadratic loss

|     |     |     |     |
| --- | --- | --- | --- |
|  | Q⁡(α,𝐛)=(𝐲−𝜶−𝐗​𝚽​𝐛)⊤​(𝐲−𝜶−𝐗​𝚽​𝐛)+λ​𝐛⊤​𝛀​𝐛Q(\\alpha,\\mathbf{b})=(\\mathbf{y}-\\boldsymbol{\\alpha}-\\mathbf{X}\\mathbf{\\Phi}\\mathbf{b})^{\\top}(\\mathbf{y}-\\boldsymbol{\\alpha}-\\mathbf{X}\\mathbf{\\Phi}\\mathbf{b})+\\lambda\\mathbf{b}^{\\top}\\mathbf{\\Omega}\\mathbf{b} |  | (17) |

as a function of the basis coefficients 𝐛=(b1,…,bK)⊤\\mathbf{b}=(b\_{1},\\ldots,b\_{K})^{\\top} and the intercept 𝜶=(α,…,α)⊤\\boldsymbol{\\alpha}=(\\alpha,\\ldots,\\alpha)^{\\top}. Here, 𝐗\\mathbf{X} is a (n×Vn\\times V) data matrix with the entry in row ii and column vv being xi​(tv)x\_{i}(t\_{v}), i.e., (𝐗)i​v=xi​(tv)(\\mathbf{X})\_{iv}=x\_{i}(t\_{v}); (V×KV\\times K) matrix 𝚽\\mathbf{\\Phi}, with (𝚽)v​k=ϕk​(tv)(\\mathbf{\\Phi})\_{vk}=\\phi\_{k}(t\_{v}), contains the basis functions ϕ1,…,ϕK\\phi\_{1},\\ldots,\\phi\_{K} evaluated at t1,…,tVt\_{1},\\ldots,t\_{V}, 𝐲\\mathbf{y} collects the observed response values, and 𝛀\\mathbf{\\Omega} is a penalty matrix specifying the concrete type of quadratic penalty imposed on 𝐛\\mathbf{b}. The strength of the penalty is controlled through tuning parameter λ\\lambda. Simple matrix algebra shows that, up to integration weights, the iith entry of 𝐗​𝚽​𝐛\\mathbf{X}\\mathbf{\\Phi}\\mathbf{b} corresponds to ( [14](https://arxiv.org/html/2312.05523v1#S3.E14 "In 3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) for equidistant and dense grids. If using a P-spline approach ( [Marx and Eilers, 1999](https://arxiv.org/html/2312.05523v1#bib.bib123 "")) with second-order penalty (as done in Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), for instance, 𝛀\\mathbf{\\Omega} takes the form 𝛀=𝐃2⊤​𝐃2\\mathbf{\\Omega}=\\mathbf{D}\_{2}^{\\top}\\mathbf{D}\_{2}, where 𝐃2\\mathbf{D}\_{2} produces second-order differences in coefficients as 𝐃2​𝐛=(b3−2​b2+b1,…,bK−2​bK−1+bK−2)⊤\\mathbf{D}\_{2}\\mathbf{b}=(b\_{3}-2b\_{2}+b\_{1},\\ldots,b\_{K}-2b\_{K-1}+b\_{K-2})^{\\top}. In the case of a generalized model, such as ( [7](https://arxiv.org/html/2312.05523v1#S3.E7 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), the quadratic loss (𝐲−𝜶−𝐗​𝚽​𝐛)⊤​(𝐲−𝜶−𝐗​𝚽​𝐛)(\\mathbf{y}-\\boldsymbol{\\alpha}-\\mathbf{X}\\mathbf{\\Phi}\\mathbf{b})^{\\top}(\\mathbf{y}-\\boldsymbol{\\alpha}-\\mathbf{X}\\mathbf{\\Phi}\\mathbf{b}) in ( [17](https://arxiv.org/html/2312.05523v1#S3.E17 "In 3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) is replaced by the negative log-likelihood. If more than one (functional) covariate is to be considered (compare ( [6](https://arxiv.org/html/2312.05523v1#S3.E6 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"))), the design matrix 𝐗\\mathbf{X} as well as the matrix of basis functions 𝚽\\mathbf{\\Phi} and vector of basis coefficients 𝐛\\mathbf{b} needs to be extended accordingly, and further penalty terms are added. Since suitable values for the associated penalty parameter(s) are typically unknown, those need to be chosen in a data-driven way. Besides generic approaches such as cross-validation or information criteria, a popular and smart way in the case of _quadratic_ penalties (as they are typically used with functional data), is offered through the _mixed model_ perspective. The latter means that quadratic smoothing penalties are equivalent to interpreting basis coefficients as random effects with normal (prior) distribution and implies a one-to-one correspondence of variance components and smoothing parameters. As a consequence, the latter can be estimated via maximum likelihood or restricted maximum likelihood; compare [Wood (2011)](https://arxiv.org/html/2312.05523v1#bib.bib210 ""), [Wood et al. (2016)](https://arxiv.org/html/2312.05523v1#bib.bib211 ""), [Wood (2017)](https://arxiv.org/html/2312.05523v1#bib.bib212 ""), and [Scheipl et al. (2015)](https://arxiv.org/html/2312.05523v1#bib.bib168 ""); [Scheipl et al. (2016)](https://arxiv.org/html/2312.05523v1#bib.bib169 ""). In addition to the estimation of smoothing parameters, the mixed model perspective also offers tools for further statistical inference, such as testing and confidence intervals (compare Section [4](https://arxiv.org/html/2312.05523v1#S4 "4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")).

An important point when choosing the final model is variable selection, particularly if the number of potential covariates is large. As before, we need to distinguish between scalar-on-function, function-on-scalar, and function-on-function regression. Most contributions in the literature, however, are on the first two cases, with a very popular approach being sparsity-inducing penalties; see, e.g., [Matsui and Konishi (2011)](https://arxiv.org/html/2312.05523v1#bib.bib126 ""), [Gertheiss et al. (2013)](https://arxiv.org/html/2312.05523v1#bib.bib55 ""), [Feng et al. (2022)](https://arxiv.org/html/2312.05523v1#bib.bib45 "") for variable selection in the (generalized) linear model for scalar-on-functions regression, [Fan et al. (2015)](https://arxiv.org/html/2312.05523v1#bib.bib43 "") for the functional index model; and [Lian (2013)](https://arxiv.org/html/2312.05523v1#bib.bib105 ""), [Chen et al. (2016)](https://arxiv.org/html/2312.05523v1#bib.bib25 ""), [Barber et al. (2017)](https://arxiv.org/html/2312.05523v1#bib.bib4 ""), [Fan and Reimherr (2017)](https://arxiv.org/html/2312.05523v1#bib.bib44 ""), [Parodi and Reimherr (2018)](https://arxiv.org/html/2312.05523v1#bib.bib144 "") for the function-on-scalar case. Alternatives include functional lars ( [Cheng et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib26 "")), Bayesian methods ( [Goldsmith et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib61 ""); [Kowal and Bourgeois, 2020](https://arxiv.org/html/2312.05523v1#bib.bib101 "")), and boosting as discussed in Section [6](https://arxiv.org/html/2312.05523v1#S6 "6 Machine Learning Approaches ‣ Functional Data Analysis:An Introduction and Recent Developments"). Also, more classic approaches such as forward/backward selection based on statistical testing as given in Section [4](https://arxiv.org/html/2312.05523v1#S4 "4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments") could be used. A recent review on variable selection in functional regression models is provided by [Aneiros et al. (2022)](https://arxiv.org/html/2312.05523v1#bib.bib1 ""). Finally, variable selection with functional data is sometimes interpreted as selecting the most predictive design (grid) points ( [Ferraty et al., 2010](https://arxiv.org/html/2312.05523v1#bib.bib48 ""); [Blanquero et al., 2019](https://arxiv.org/html/2312.05523v1#bib.bib9 "")) or intervals/regions in the functions’ domain ( [James et al., 2009](https://arxiv.org/html/2312.05523v1#bib.bib91 ""); [Tutz and Gertheiss, 2010](https://arxiv.org/html/2312.05523v1#bib.bib200 ""); [Zhou et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib222 ""); [Centofanti et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib19 "")); which typically requires alternative methods to the basis functions and smoothing approach as described above. For further information, we refer to the literature cited above. The following subsection provides a short introduction to fully non-parametric functional regression.

#### 3.2.2 Non-parametric Approaches

Let us consider the regression problem with continuous YiY\_{i} and a single functional covariate XiX\_{i} in its most general form, where

|     |     |     |     |
| --- | --- | --- | --- |
|  | Yi=f⁡(Xi)+ϵi,Y\_{i}=f(X\_{i})+\\epsilon\_{i}, |  | (18) |

ff being an unknown regression function, and ϵi\\epsilon\_{i} some mean zero noise variable, potentially with some further assumptions such as being i.i.d. across subjects i=1,…,ni=1,\\ldots,n. Compared to the semi-parametric approaches above, in particular, the functional linear model ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), assumptions with respect to both the form of ff and the distribution of ϵi\\epsilon\_{i} are much milder.

For functional as for multivariate covariates, for a new observation with known covariate value xx and unknown YY, a kernel-based, non-parametric prediction Y^=f^​(x)\\hat{Y}=\\hat{f}(x) is given by

|     |     |     |     |
| --- | --- | --- | --- |
|  | f^​(x)=∑i=1nYi​K​(d⁡(Xi,x)/hn)∑i=1nK⁡(d⁡(Xi,x)/hn),\\hat{f}(x)=\\frac{\\sum\_{i=1}^{n}Y\_{i}K(d(X\_{i},x)/h\_{n})}{\\sum\_{i=1}^{n}K(d(X\_{i},x)/h\_{n})}, |  | (19) |

with some kernel KK, bandwidth hn↘0h\_{n}\\searrow 0 (for n→∞n\\rightarrow\\infty) and distance measure dd appropriate for the type of covariate considered, as further discussed below. From the mean zero error term, it follows that f^​(x)\\hat{f}(x) is an estimate of the conditional expectation 𝔼⁡\[Y\|X=x\]{\\mathbb{E}}\[Y\|X=x\]. For f^\\hat{f} as defined above to be consistent, a necessary condition, informally speaking, is that the probability of a training observation to be in the close neighborhood of xx in terms of dd is strictly positive. For details on this so-called _small ball probability_, see, e.g., [Ferraty and Vieu (2006)](https://arxiv.org/html/2312.05523v1#bib.bib47 ""). In general, each density function may be used as kernel KK, but typically we restrict ourselves to symmetric kernels with the maximum at zero, such as the (standard) normal density – the so-called _Gaussian_ kernel. For details on kernel functions, see, e.g., [Gasser et al. (1985)](https://arxiv.org/html/2312.05523v1#bib.bib54 "").

When dealing with functional covariates, in particular, the choice of dd is crucial. A popular choice for functional Xi,x∈ℒ2X\_{i},x\\in\\mathcal{L}^{2}, for instance, is the ℒ2\\mathcal{L}^{2} norm as introduced in [1.2](https://arxiv.org/html/2312.05523v1#S1.SS2 "1.2 Notation ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"),

|     |     |     |     |
| --- | --- | --- | --- |
|  | d⁡(Xi,x)=‖Xi−x‖ℒ2.d(X\_{i},x)=\\\|X\_{i}-x\\\|\_{\\mathcal{L}^{2}}. |  | (20) |

However, restricting dd to be a metric such as ( [20](https://arxiv.org/html/2312.05523v1#S3.E20 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) is sometimes too restrictive in the functional case. So-called _semi-metrics_ may also be considered such as

|     |     |     |     |
| --- | --- | --- | --- |
|  | d⁡(Xi,x)=‖X˙i−x˙‖ℒ2,d(X\_{i},x)=\\\|\\dot{X}\_{i}-\\dot{x}\\\|\_{\\mathcal{L}^{2}}, |  | (21) |

where X˙i,x˙\\dot{X}\_{i},\\dot{x} are (first) derivatives, see [Ferraty and Vieu (2006)](https://arxiv.org/html/2312.05523v1#bib.bib47 "") for a deeper insight into this topic. An important difference between metrics and semi-metrics is that in the latter case d⁡(Xi,x)=0d(X\_{i},x)=0 does not necessarily imply Xi=xX\_{i}=x. With ( [21](https://arxiv.org/html/2312.05523v1#S3.E21 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), for example, d⁡(Xi,x)=0d(X\_{i},x)=0 is also obtained if x⁡(t)=Xi​(t)+cx(t)=X\_{i}(t)+c, for some vertical shift constant c≠0c\\neq 0. In general, the choice of which (semi-)metric to take depends on the shape of the data and the goal of the statistical analysis. For instance, if dimension reduction for functional observations is of interest, one possibility is FPCA as discussed in Section [2.4](https://arxiv.org/html/2312.05523v1#S2.SS4 "2.4 Functional principal component analysis ‣ 2 Fundamentals ‣ Functional Data Analysis:An Introduction and Recent Developments"), in which case options for dd include distances on the extracted scores. In general, results can look very different, depending on the chosen measure of proximity. In Chapter 3 of [Ferraty and Vieu (2006)](https://arxiv.org/html/2312.05523v1#bib.bib47 "") examples to illustrate this effect are given. Also, further suggestions for semi-metrics and a survey on which semi-metric may be appropriate for which situation can be found there. For example, semi-metric ( [21](https://arxiv.org/html/2312.05523v1#S3.E21 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), which is based on the derivatives, is often well suited for smooth data, whereas for rough data a different approach should be considered.

Figure 8: Predicted values vs. true values (left) and estimated probabilities of class 1 (i.e., ‘male’) vs. true classes (right; 0=0= ‘female’, 1=1= ‘male’) when using nonparametric functional data analysis (‘npfda’) or a (generalized) functional linear model fitted by pfr() on the data from the left and right of Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"), respectively.

For an illustration of nonparametric scalar-on-function regression ( [19](https://arxiv.org/html/2312.05523v1#S3.E19 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), consider the knee acceleration data from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left). We use nonparametric regression/prediction ( [19](https://arxiv.org/html/2312.05523v1#S3.E19 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) with a semi-metric in terms of an (unweighted) Euclidean distance on the scores from an FPCA with 5 components. The (global) bandwidth is chosen via (inner) cross-validation. Figure [8](https://arxiv.org/html/2312.05523v1#S3.F8 "Figure 8 ‣ 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") (blue circles, left) shows the predicted values obtained via leaving-one-out (outer) cross-validation vs. the true values. For comparison, we also give the results for a functional linear model (fitted by pfr(), and applying leaving-one-out cross-validation as well). A perfect prediction would correspond to values on the bisecting (dashed black) line. We see that this is a rather difficult regression problem, with nonparametric functional data analysis (‘npfda’) performing slightly better in terms of the mean squared error (MSE), which indicates at least some non-linearity in the association between the response and the covariate (although the larger MSE of ‘pfr’ is mainly caused by the two extreme observations with true values around 0.7 that are fitted much better by ‘npfda’). A potential issue with nonparametric functional regression as introduced so far, however, is that it is restricted to cases with only one (functional) covariate. An approach how to extend ( [19](https://arxiv.org/html/2312.05523v1#S3.E19 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) to settings with additional, functional, or scalar covariates (such as ‘sex’), is presented in [Selk and Gertheiss (2023)](https://arxiv.org/html/2312.05523v1#bib.bib174 "") and [Selk (2023)](https://arxiv.org/html/2312.05523v1#bib.bib173 "").

If using the nonparametric approach ( [19](https://arxiv.org/html/2312.05523v1#S3.E19 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) on the data from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (right) with a binary, 0/1-coded response (female: 0, male: 1), the conditional expectation/regression function f⁡(x)f(x) corresponds to the (conditional) probability of class 1 given input xx. The corresponding estimates obtained by npfda and pfr are shown in Figure [8](https://arxiv.org/html/2312.05523v1#S3.F8 "Figure 8 ‣ 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") (right). As we can see, the functional logit model from Section [3.1.1](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS1 "3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") performs much better here than the nonparametric approach. This can be explained as follows. As noted earlier (compare Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"), right), the two classes can be separated very well by focusing on hip acceleration between time points 0.70.7 and 0.80.8. The coefficient function fitted by pfr() is able to exploit this (compare Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), right), whereas the distance/semi-metric dd used here (FPCA) is not. The nonparametric approach might perform better, for instance, by introducing an appropriate weight function in ( [20](https://arxiv.org/html/2312.05523v1#S3.E20 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")). Examples of such functions, including an algorithm for estimating a weight function from the data at hand, are given by [Chen et al. (2014)](https://arxiv.org/html/2312.05523v1#bib.bib23 ""). An advantage of the nonparametric approach ( [19](https://arxiv.org/html/2312.05523v1#S3.E19 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) is that it can be easily used for regression with a multi-class response as well. As this is closely related to the classification of functional data, we refer to Section [5.1](https://arxiv.org/html/2312.05523v1#S5.SS1 "5.1 Classification of Functional Data ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") for more details. Furthermore, the kernel-based approach presented in Section [3.2.2](https://arxiv.org/html/2312.05523v1#S3.SS2.SSS2 "3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") could be combined with the more structured models as presented in [3.1.1](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS1 "3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"). For instance, [Jeon et al. (2021)](https://arxiv.org/html/2312.05523v1#bib.bib92 "") proposed a very general approach for additive regression with nonstandard response and covariates, including functional data.

### 3.3 Software

Some functions for functional regression analysis, where either the dependent variable or one or more independent variables are functional, are available in R package fda( [Ramsay and Silverman, 2005](https://arxiv.org/html/2312.05523v1#bib.bib156 ""); [Ramsay et al., 2009](https://arxiv.org/html/2312.05523v1#bib.bib157 "")); in particular, for the functional linear model for scalar-on-function regression ( [6](https://arxiv.org/html/2312.05523v1#S3.E6 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) and the concurrent model ( [10](https://arxiv.org/html/2312.05523v1#S3.E10 "In 3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")). A broader class of models, including the models presented in [3.1.1](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS1 "3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") to [3.1.3](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS3 "3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), can be fit by use of refund( [Goldsmith et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib63 "")). The functions implemented there typically use mgcv methodology ( [Wood, 2011](https://arxiv.org/html/2312.05523v1#bib.bib210 ""); [Wood et al., 2016](https://arxiv.org/html/2312.05523v1#bib.bib211 ""); [Wood, 2017](https://arxiv.org/html/2312.05523v1#bib.bib212 "")), and the latter R package can also be used directly to fit at least some of those models, but the use of refund may often be easier for the inexperienced user. R functions for nonparametric functional data analysis as presented in [3.2.2](https://arxiv.org/html/2312.05523v1#S3.SS2.SSS2 "3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") and thoroughly discussed in the monograph by [Ferraty and Vieu (2006)](https://arxiv.org/html/2312.05523v1#bib.bib47 "") are found at the accompanying website http://www.math.univ-toulouse.fr/staph/npfda/.

## 4 Statistical Inference with Functional Data

### 4.1 Functional ANOVA

The setting of one-way univariate functional ANOVA is similar to the well-known scalar case. We typically have a grouping variable, a so-called factor, defining groups 1,…,g1,\\ldots,g, and functional data Xi​j​(t)X\_{ij}(t), t∈𝒯t\\in\\mathcal{T}, coming from these gg groups, j=1,…,gj=1,\\ldots,g, i=1,…,nji=1,\\ldots,n\_{j}, with njn\_{j} denoting the sample size in group jj. The overall sample size is n=n1+…+ngn=n\_{1}+\\ldots+n\_{g}. Given group membership, functional variables are assumed to be (conditionally) independent. Furthermore, it is typically assumed that functions are square-integrable on 𝒯\\mathcal{T}, i.e., elements of ℒ2​(𝒯)\\mathcal{L}^{2}(\\mathcal{T}) (compare Section [1.2](https://arxiv.org/html/2312.05523v1#S1.SS2 "1.2 Notation ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments")). The hypothesis to test is

|     |     |     |     |
| --- | --- | --- | --- |
|  | H0:μ1​(t)=…=μg​(t),t∈𝒯,H\_{0}:\\mu\_{1}(t)=\\ldots=\\mu\_{g}(t),\\quad t\\in\\mathcal{T}, |  | (22) |

with μj​(t)\\mu\_{j}(t) denoting the mean function in group jj. Alternatively, we can use a linear function-on-scalar model with one categorical covariate in terms of

|     |     |     |     |
| --- | --- | --- | --- |
|  | Xi​j​(t)=μ⁡(t)+αj​(t)+ϵi​j​(t),X\_{ij}(t)=\\mu(t)+\\alpha\_{j}(t)+\\epsilon\_{ij}(t), |  | (23) |

where μ⁡(t)\\mu(t) is the grand mean (function), αj​(t)=μj​(t)−μ⁡(t)\\alpha\_{j}(t)=\\mu\_{j}(t)-\\mu(t) the deviation from the grand mean in group jj, and ϵi​j​(t)\\epsilon\_{ij}(t) a mean zero error/noise process. Furthermore, it is typically assumed that all functions Xi​j​(t)X\_{ij}(t), and thus ϵi​j​(t)\\epsilon\_{ij}(t), share the same covariance function Σ⁡(s,t)\\Sigma(s,t), s,t∈𝒯s,t\\in\\mathcal{T}. This is the functional version of homoscedasticity as commonly assumed in the scalar case (see below for literature on testing the equality of covariance operators between groups). For identifiability, a constraint such as ∑jαj​(t)=0\\sum\_{j}\\alpha\_{j}(t)=0 for all tt is needed. Then, hypothesis ( [22](https://arxiv.org/html/2312.05523v1#S4.E22 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) can be rewritten as

|     |     |     |     |
| --- | --- | --- | --- |
|  | H0:α1​(t)=…=αg​(t)=0,t∈𝒯.H\_{0}:\\alpha\_{1}(t)=\\ldots=\\alpha\_{g}(t)=0,\\quad t\\in\\mathcal{T}. |  | (24) |

An example is given in Figure [9](https://arxiv.org/html/2312.05523v1#S4.F9 "Figure 9 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"). Here, the data (dotted lines), a subset of our running example data, comes from g=3g=3 groups defined by different experimental conditions: run at 3 m/s with no backpack (‘slowbw’), with 10% body mass backpack (‘slowten’), with 20% body mass backpack (‘slowtwe’). The empirical, group-wise mean functions are given as solid lines. For simplicity, we restrict ourselves to a small, illustrative data set comprising 15 males, with five persons in each group.

In what follows, we will give a short overview of some procedures proposed for testing ( [22](https://arxiv.org/html/2312.05523v1#S4.E22 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) and ( [24](https://arxiv.org/html/2312.05523v1#S4.E24 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")), respectively. Many of these tests are based on the pointwise between-groups sum of squares

|     |     |     |     |
| --- | --- | --- | --- |
|  | SSR​(t)=∑j=1gnj​(μ^j​(t)−μ^​(t))2\\text{SSR}(t)=\\sum\_{j=1}^{g}n\_{j}(\\hat{\\mu}\_{j}(t)-\\hat{\\mu}(t))^{2} |  | (25) |

and the pointwise within-groups/error sum of squares

|     |     |     |     |
| --- | --- | --- | --- |
|  | SSE​(t)=∑j=1g∑i=1nj(Xi​j​(t)−μ^j​(t))2,\\text{SSE}(t)=\\sum\_{j=1}^{g}\\sum\_{i=1}^{n\_{j}}(X\_{ij}(t)-\\hat{\\mu}\_{j}(t))^{2}, |  | (26) |

compare [Ramsay and Silverman (2005)](https://arxiv.org/html/2312.05523v1#bib.bib156 "") and [Górecki and Smaga (2019)](https://arxiv.org/html/2312.05523v1#bib.bib70 ""). One way of constructing a test statistic then is the ratio of the integrated between- and within-groups sum of squares, that is

|     |     |     |     |
| --- | --- | --- | --- |
|  | 1g−1​∫𝒯SSR​(t)​𝑑t1n−g​∫𝒯SSE​(t)​𝑑t,\\frac{\\frac{1}{g-1}\\int\_{\\mathcal{T}}\\text{SSR}(t)dt}{\\frac{1}{n-g}\\int\_{\\mathcal{T}}\\text{SSE}(t)dt}, |  | (27) |

and the tests proposed in the literature vary concerning the method used for representing the functional data and estimating the unknown parameters, and the way p-values are calculated. For instance, under some assumptions such as Gaussian error processes, [Shen and Faraway (2004)](https://arxiv.org/html/2312.05523v1#bib.bib176 "") derived the test statistics’ null distribution and also provided an approximation based on the Karhunen-Loéve expansion of the error process. [Zhang (2011)](https://arxiv.org/html/2312.05523v1#bib.bib217 "") proposed an improved, biased-reduced approximation, and [Górecki and Smaga (2015)](https://arxiv.org/html/2312.05523v1#bib.bib68 "") used a finite-dimensional basis function representation of the observable functional data Xi​j​(t)X\_{ij}(t) as the starting point.

As an alternative to ( [27](https://arxiv.org/html/2312.05523v1#S4.E27 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")), we may also calculate the pointwise F-statistic,

|     |     |     |     |
| --- | --- | --- | --- |
|  | F⁡(t)=1g−1​SSR​(t)1n−g​SSE​(t),F(t)=\\frac{\\frac{1}{g-1}\\text{SSR}(t)}{\\frac{1}{n-g}\\text{SSE}(t)}, |  | (28) |

and integrate/globalize this quantity in terms of ∫𝒯F⁡(t)​𝑑t\\int\_{\\mathcal{T}}F(t)dt( [Zhang and Liang, 2014](https://arxiv.org/html/2312.05523v1#bib.bib219 "")), or use only its maximum, i.e., supt∈𝒯F⁡(t)\\sup\_{t\\in\\mathcal{T}}F(t)( [Zhang et al., 2019](https://arxiv.org/html/2312.05523v1#bib.bib221 "")).

Figure 9: Example knee measurements (dotted lines), compare Table [1](https://arxiv.org/html/2312.05523v1#S1.T1 "Table 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments"), for three experimental conditions: ‘slowbw’ (black) ‘slowten’ (red), ‘slowtwe’ (green); the solid curves give group-wise means.

A somewhat different approach is presented in [Cuevas et al. (2004)](https://arxiv.org/html/2312.05523v1#bib.bib31 ""), who used the sum of pairwise ℒ2{\\mathcal{L}^{2}}-distances ∑j<l∫𝒯(μ^j​(t)−μ^l​(t))2​𝑑t\\sum\_{j<l}\\int\_{\\mathcal{T}}(\\hat{\\mu}\_{j}(t)-\\hat{\\mu}\_{l}(t))^{2}dt as the test statistic and a parametric bootstrap to approximate the null distribution. [Cuesta-Albertos and Febrero-Bande (2010)](https://arxiv.org/html/2312.05523v1#bib.bib30 ""), by contrast, considered testing through random projects of the functional data observed. Specifically, a trajectory vv is sampled on a fine grid, e.g., through a sequence of partial sums of independent normal variables (i.e., a Gaussian random walk). Then, the functional data is projected as Pi​j=∫𝒯Xi​j​(t)​v​(t)​𝑑tP\_{ij}=\\int\_{\\mathcal{T}}X\_{ij}(t)v(t)dt, and a test is performed for mean differences of the projected data between groups. This procedure is repeated kk times, i.e., for kk different vv-trajectories, and resulting p-values are corrected using the FDR approach of [Benjamini and Yekutieli (2001)](https://arxiv.org/html/2312.05523v1#bib.bib5 ""). For testing mean differences in the (scalar) projections Pi​jP\_{ij}, there are several options, for instance, the approach by [Brunner et al. (1997)](https://arxiv.org/html/2312.05523v1#bib.bib15 "")

Figure 10: P-values for five different tests for functional ANOVA on the data shown in Figure [9](https://arxiv.org/html/2312.05523v1#S4.F9 "Figure 9 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"); significance on the 5% or 10% level is indicated by the dashed and dotted line, respectively.

For illustration, Figure [10](https://arxiv.org/html/2312.05523v1#S4.F10 "Figure 10 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments") shows the p-values for five different tests for functional ANOVA on the data shown in Figure [9](https://arxiv.org/html/2312.05523v1#S4.F9 "Figure 9 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"). Computations were done using R package fdanova( [Górecki and Smaga, 2019](https://arxiv.org/html/2312.05523v1#bib.bib70 "")), which provides about a dozen tests for testing ( [22](https://arxiv.org/html/2312.05523v1#S4.E22 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")). Here we considered a permutation test employing the ratio of the integrated sums of squares ( [27](https://arxiv.org/html/2312.05523v1#S4.E27 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) and basis representation of the functional data ( [Górecki and Smaga, 2015](https://arxiv.org/html/2312.05523v1#bib.bib68 "")), globalizing the pointwise F-statistic ( [28](https://arxiv.org/html/2312.05523v1#S4.E28 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) ( [Zhang and Liang, 2014](https://arxiv.org/html/2312.05523v1#bib.bib219 "")), using its maximum only ( [Zhang et al., 2019](https://arxiv.org/html/2312.05523v1#bib.bib221 "")), ℒ2{\\mathcal{L}^{2}}-distances between groupwise means ( [Cuevas et al., 2004](https://arxiv.org/html/2312.05523v1#bib.bib31 "")), and random projections ( [Cuesta-Albertos and Febrero-Bande, 2010](https://arxiv.org/html/2312.05523v1#bib.bib30 "")). Figure [10](https://arxiv.org/html/2312.05523v1#S4.F10 "Figure 10 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments") shows large agreement in terms of significant differences between groups (‘yes’ or ‘no’, according to the dashed/dotted lines in Figure [10](https://arxiv.org/html/2312.05523v1#S4.F10 "Figure 10 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")). In particular, significant differences are detected between the three experimental conditions for (e) ‘knee flexion-extension angle’ and (h) ‘knee flexion-extension moment’. The different tests, however, are obviously not equivalent. For example, the projection-based approach also identifies significant differences (at the 5% level) in the mean functions of (c) ‘knee axial rotation acceleration’ and (j) ‘knee abduction-adduction velocity’, whereas the other tests do not. In light of these findings, and keeping in mind that a large number of tests is available for testing ( [22](https://arxiv.org/html/2312.05523v1#S4.E22 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"))–even many more than considered in Figure [10](https://arxiv.org/html/2312.05523v1#S4.F10 "Figure 10 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"), see [Górecki and Smaga (2019)](https://arxiv.org/html/2312.05523v1#bib.bib70 "")–it should be pointed out that running all these tests on the data, and reporting significant differences if any test has a p-value below α\\alpha, is not admissible, since it may substantially increase the type-I error rate. For illustration, we used all data available ( [Liew et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib110 "")) for knee abduction-adduction angle, drew a random sample of 150 curves, and used these curves to form, also at random, five groups of equal size (30). Thus, the null hypothesis ( [22](https://arxiv.org/html/2312.05523v1#S4.E22 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) is true by design because all curves are sampled from the same population. We then repeated this procedure a thousand times and stored the p-values given by the five tests from Figure [10](https://arxiv.org/html/2312.05523v1#S4.F10 "Figure 10 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"). As a result, each test, if considered separately, indeed controls the type-I error rate (or may even be conservative), but the naive approach of considering all five tests together and reporting significance if any p-value is below α\\alpha increased rejection rates to 8.7% and 17.1% well above the nominal level of 5% and 10%, respectively. An obvious solution to this problem is to decide on the test to use _before_ analyzing the data. But even if we do, there might still be issues, particularly if we choose to use the approach based on random projections ( [Cuesta-Albertos and Febrero-Bande, 2010](https://arxiv.org/html/2312.05523v1#bib.bib30 "")). Due to the randomness involved, it can be very difficult to replicate the results obtained, even on the exact same data. For instance, if running the test on (c) ‘knee axial rotation acceleration’ (Figure [9](https://arxiv.org/html/2312.05523v1#S4.F9 "Figure 9 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) a hundred times, we obtained p-values smaller than 5% (as seen in Figure [10](https://arxiv.org/html/2312.05523v1#S4.F10 "Figure 10 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments"), yellow) only in about 10% of all runs. In addition, this provides another easy way of “cheating” to researchers who are merely “hunting statistical significance” ( [Szucs, 2016](https://arxiv.org/html/2312.05523v1#bib.bib193 ""); [Simmons et al., 2011](https://arxiv.org/html/2312.05523v1#bib.bib180 "")): they may just run the test a few times (e.g., with a sequence of some popular seeds for the random number generator such as ‘1234’, ‘2345’, etc. for “reproducibility”) until the desired result appears. For instance, if allowing for five trials in a setting with all curves actually sampled from the same population described above, we observed type-I error rates of around 10% for nominal α\\alpha of 5%. Consequently, although it is tempting, researchers should refrain from such behavior.

An important special case of ( [22](https://arxiv.org/html/2312.05523v1#S4.E22 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) is the two-sample problem, where just two groups, such as case/control or treatment/control, are to be compared; and many testing procedures have been proposed for such situations; see, e.g., [Ramsay and Silverman (2005)](https://arxiv.org/html/2312.05523v1#bib.bib156 ""), [Zhang et al. (2010)](https://arxiv.org/html/2312.05523v1#bib.bib220 ""), [Horváth et al. (2013)](https://arxiv.org/html/2312.05523v1#bib.bib81 "") and [Ghiglietti et al. (2017)](https://arxiv.org/html/2312.05523v1#bib.bib58 ""). Besides mean functions, the distributions of functional data from different groups may also be compared in a broader sense ( [Benko et al., 2009](https://arxiv.org/html/2312.05523v1#bib.bib6 ""); [Pomann et al., 2016](https://arxiv.org/html/2312.05523v1#bib.bib152 ""); [Pini and Vantini, 2016](https://arxiv.org/html/2312.05523v1#bib.bib150 ""); [Krzysko and Smaga, 2021](https://arxiv.org/html/2312.05523v1#bib.bib103 ""); [Wynne and Duncan, 2022](https://arxiv.org/html/2312.05523v1#bib.bib213 ""), e.g.,). Furthermore, there are proposals targeting specifically the covariance functions ( [Kraus and Panaretos, 2012](https://arxiv.org/html/2312.05523v1#bib.bib102 ""); [Fremdt et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib50 ""), e.g.,). An entire textbook on inference for functional data is, for instance, provided by [Horváth and Kokoszka (2012)](https://arxiv.org/html/2312.05523v1#bib.bib80 "").

The comparison of mean functions as in testing ( [22](https://arxiv.org/html/2312.05523v1#S4.E22 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) can be generalized in (at least) two ways. First, we may consider more than one factor in multi-way (functional) ANOVA; see, e.g., [Cuesta-Albertos and Febrero-Bande (2010)](https://arxiv.org/html/2312.05523v1#bib.bib30 ""). Second, the functional variables to compare between groups may be multivariate, which yields a functional version of MANOVA ( [Górecki and Smaga, 2017](https://arxiv.org/html/2312.05523v1#bib.bib69 ""), e.g.,).

### 4.2 Testing and Confidence Intervals in Functional Regression

In the framework of function-on-scalar regression, various testing procedures can be found in the literature. For instance, after rewriting the linear model ( [11](https://arxiv.org/html/2312.05523v1#S3.E11 "In 3.1.3 Function-on-Function Regression (FOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) as Yi​(t)=𝐱i⊤​𝜷​(t)+ϵi​(t)Y\_{i}(t)=\\mathbf{x}\_{i}^{\\top}\\boldsymbol{\\beta}(t)+\\epsilon\_{i}(t), ℒ2{\\mathcal{L}^{2}}-norm based ( [Zhang and Chen, 2007](https://arxiv.org/html/2312.05523v1#bib.bib218 "")) and F-tests ( [Shen and Faraway, 2004](https://arxiv.org/html/2312.05523v1#bib.bib176 ""); [Zhang, 2011](https://arxiv.org/html/2312.05523v1#bib.bib217 "")) have been proposed for testing the general linear hypothesis H0:𝐂​𝜷​(t)=𝐜⁡(t)H\_{0}:\\mathbf{C}\\boldsymbol{\\beta}(t)=\\mathbf{c}(t), where 𝐂\\mathbf{C} is a given matrix of appropriate dimension, and 𝐜⁡(t)\\mathbf{c}(t) is a corresponding vector of given functions. Functional ANOVA as in ( [22](https://arxiv.org/html/2312.05523v1#S4.E22 "In 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments")) can be seen as a special case of this more general testing problem.

The opposite setting is scalar-on-function regression, where a scalar response is regressed on a functional covariate. In its most general form ( [18](https://arxiv.org/html/2312.05523v1#S3.E18 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), only a few assumptions are made, while particularly in the functional linear model ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), assumptions are much stronger. The most interesting hypothesis to test in this setting is typically whether there is an effect of the covariate on the response at all. That means, in ( [18](https://arxiv.org/html/2312.05523v1#S3.E18 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), the null hypothesis is that the regression function ff is constant. In the linear model ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) this translates into the coefficient function being zero. Also, if comparing ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) and ( [18](https://arxiv.org/html/2312.05523v1#S3.E18 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), an interesting hypothesis to test could be whether the linear model ( [5](https://arxiv.org/html/2312.05523v1#S3.E5 "In 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) holds. For both problems, a few different testing procedures have been proposed. For instance, [Swihart et al. (2014)](https://arxiv.org/html/2312.05523v1#bib.bib192 "") and [McLean et al. (2015)](https://arxiv.org/html/2312.05523v1#bib.bib129 "") used the mixed model perspective of functional regression and proposed restricted likelihood ratio tests for checking the significance of a functional covariate and/or linearity of the effect. [Kong et al. (2016)](https://arxiv.org/html/2312.05523v1#bib.bib99 "") extended four tests common in classical regression (Wald, score, likelihood ratio, and F-tests) to the functional linear model by use of FPCA, intending to test the null hypothesis that there is no association between a scalar response and a functional covariate. A Wald-type test is also discussed in [Su et al. (2017)](https://arxiv.org/html/2312.05523v1#bib.bib189 ""), and [Yi et al. (2022)](https://arxiv.org/html/2312.05523v1#bib.bib216 "") present an improved F-test. [García-Portugués et al. (2014)](https://arxiv.org/html/2312.05523v1#bib.bib53 "") proposed a goodness-of-fit test based on random projections for the functional linear model with scalar response that can also be used for testing the special case of no association between the functional covariate and the scalar response. A thorough comparison of at least some of those tests is found in [Tekbudak et al. (2019)](https://arxiv.org/html/2312.05523v1#bib.bib196 "").

In addition to the fitted coefficient functions in a (generalized) functional linear model, Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") also provides pointwise 95% confidence intervals as shaded regions. Those were estimated using the pfr() function from refund, which uses mgcv methodology (compare Section [3.3](https://arxiv.org/html/2312.05523v1#S3.SS3 "3.3 Software ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), and are based on the Bayesian view of the smoothing process. For simplicity, let us consider the basis coefficients 𝐛\\mathbf{b} from ( [17](https://arxiv.org/html/2312.05523v1#S3.E17 "In 3.2.1 Semi-parametric Models and the Basis Functions Approach ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) where only a single functional covariate was present. Given the data and smoothing parameter, the posterior distribution of 𝐛\\mathbf{b} is multivariate normal with some covariance matrix 𝚪𝐛\\boldsymbol{\\Gamma}\_{\\mathbf{b}} (for details on the form of 𝚪𝐛\\boldsymbol{\\Gamma}\_{\\mathbf{b}}, see, e.g., [Wood (2017)](https://arxiv.org/html/2312.05523v1#bib.bib212 "")). Then, with 𝜷^=(β^​(t1),…,β^​(tV))⊤=𝚽​𝐛^\\hat{\\boldsymbol{\\beta}}=(\\hat{\\beta}(t\_{1}),\\ldots,\\hat{\\beta}(t\_{V}))^{\\top}=\\boldsymbol{\\Phi}\\hat{\\mathbf{b}} denoting the vector that contains the estimated coefficient function at the evaluation points, an approximate pointwise (1−α1-\\alpha)100% credible interval for β⁡(tv)\\beta(t\_{v}) is given by β^​(tv)±z1−α/2​ζv\\hat{\\beta}(t\_{v})\\pm z\_{1-\\alpha/2}\\sqrt{\\zeta\_{v}}, where 𝜻=(ζ1,…,ζV)\\boldsymbol{\\zeta}=(\\zeta\_{1},\\ldots,\\zeta\_{V}) is the diagonal of 𝚽​𝚪𝐛​𝚽⊤\\boldsymbol{\\Phi}\\boldsymbol{\\Gamma}\_{\\mathbf{b}}\\boldsymbol{\\Phi}^{\\top} and z1−α/2z\_{1-\\alpha/2} is the (1−α/21-\\alpha/2) quantile of the standard normal distribution. These intervals also have “surprisingly good frequentist coverage properties” (averaged over tt) ( [Wood, 2017](https://arxiv.org/html/2312.05523v1#bib.bib212 "")). Since z0.975=1.96≈2z\_{0.975}=1.96\\approx 2, β^​(tv)±2​νv\\hat{\\beta}(t\_{v})\\pm 2\\sqrt{\\nu\_{v}} gives an approximate pointwise 95% confidence interval. When calculating confidence intervals in function-on-scalar or function-on-function regression models, it is important to make sure that within-function correlation is accounted for (compare Section [3.1.2](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS2 "3.1.2 Function-on-Scalar Regression (FOSR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")). This may, for instance, be done in a conditional model through functional random effects ( [Scheipl et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib168 "")) or a marginal model through robust standard errors ( [Chen et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib22 ""); [Gertheiss et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib56 "")).

While pointwise confidence intervals (only) work ‘pointwise’ in terms of coverage properties, so-called simultaneous confidence bands can be interpreted globally. That means the provided bands cover the _entire_ (true) function with some prespecified probability such as 95%. Most methods proposed for simultaneous confidence bands for functional data use resampling techniques, particularly different versions of the bootstrap ( [Degras, 2011](https://arxiv.org/html/2312.05523v1#bib.bib34 ""); [Chang et al., 2017](https://arxiv.org/html/2312.05523v1#bib.bib20 ""), e.g.,). Some approaches also use dimension reduction through functional principal component analysis and the Karhunen-Loève expansion; e.g., [Goldsmith et al. (2013)](https://arxiv.org/html/2312.05523v1#bib.bib60 "") and [Choi and Reimherr (2018)](https://arxiv.org/html/2312.05523v1#bib.bib29 ""). In a very recent paper, [Liebl and Reimherr (2023)](https://arxiv.org/html/2312.05523v1#bib.bib106 "") present a broad framework based on random process theory. Among other things, the confidence bands proposed also provide some ‘local’ control of the false positive rate over subsets of the bands’ domain.

### 4.3 Software

A collection of various tests for functional ANOVA is found in R package fdANOVA( [Górecki and Smaga, 2019](https://arxiv.org/html/2312.05523v1#bib.bib70 "")), and all p-values shown in Figure [10](https://arxiv.org/html/2312.05523v1#S4.F10 "Figure 10 ‣ 4.1 Functional ANOVA ‣ 4 Statistical Inference with Functional Data ‣ Functional Data Analysis:An Introduction and Recent Developments") were calculated through the fanova.tests() function provided there. The R package fdatest( [Pini and Vantini, 2022](https://arxiv.org/html/2312.05523v1#bib.bib151 "")) implements the interval testing procedure by [Pini and Vantini (2016)](https://arxiv.org/html/2312.05523v1#bib.bib150 ""). Pointwise confidence intervals for terms in SOFR, FOSR, and FOFR models are, for instance, provided by refund functions pfr() and pffr(), respectively. Both are wrappers for mgcv’s gam() and its siblings (compare Section [3.3](https://arxiv.org/html/2312.05523v1#S3.SS3 "3.3 Software ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")).

## 5 Classification and Clustering

The purpose of regression, as presented in Section [3](https://arxiv.org/html/2312.05523v1#S3 "3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), was to explain and/or predict a scalar or functional response variable using one or more scalar/functional explanatory variables. Further approaches with origin in the machine learning community and a clear focus on prediction will be discussed in Section [6](https://arxiv.org/html/2312.05523v1#S6 "6 Machine Learning Approaches ‣ Functional Data Analysis:An Introduction and Recent Developments"). In Section [5](https://arxiv.org/html/2312.05523v1#S5 "5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments"), we will present two further topics beyond regression for functional data from a statistical perspective, namely classification, and clustering. We will start with classification, which shows close links to Section [3](https://arxiv.org/html/2312.05523v1#S3 "3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments").

### 5.1 Classification of Functional Data

We assume that functional data comes from distinct classes 1,…,G1,\\ldots,G, and training data with known class labels is available for determining a classification rule such that new (functional) data with unknown group membership can be assigned to its underlying class with low probability of an error. According to Bayes’ rule, each unit should be classified based on posterior class probabilities, that is, the conditional probabilities of each class given the (functional) data. In practice, however, those conditional probabilities are unknown and need to be estimated from the training data. In the simplest case, functional data only come from two classes. Then, we are in a situation like Figure [6](https://arxiv.org/html/2312.05523v1#S3.F6 "Figure 6 ‣ 3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") (right), where we can simply use the functional logit model to estimate conditional class probabilities and assign each unit to the class of the highest (estimated) probability.

If G>2G>2 the semiparametric approach, in particular the functional logit model, can be generalized in terms of a functional multinomial model ( [Matsui, 2014](https://arxiv.org/html/2312.05523v1#bib.bib125 "")), increasing, however, the number of parameter functions that need to be estimated. The nonparametric, kernel-based approach as presented in Section [3.2.2](https://arxiv.org/html/2312.05523v1#S3.SS2.SSS2 "3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments") on the other hand, can be applied directly. Specifically, following the idea of nonparametric regression ( [19](https://arxiv.org/html/2312.05523v1#S3.E19 "In 3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")), we can estimate the conditional probability Pg​(x):=P⁡(Y=g\|x)P\_{g}(x):=P(Y=g\|x) of class gg given a (functional) covariate xx with unknown class label YY by

|     |     |     |     |
| --- | --- | --- | --- |
|  | P^g​(x)=∑i=1nIg​(Yi)​K​(d⁡(Xi,x)/hn)∑i=1nK⁡(d⁡(Xi,x)/hn).\\hat{P}\_{g}(x)=\\frac{\\sum\_{i=1}^{n}I\_{g}(Y\_{i})K(d(X\_{i},x)/h\_{n})}{\\sum\_{i=1}^{n}K(d(X\_{i},x)/h\_{n})}. |  | (29) |

Here Ig​(Yi)I\_{g}(Y\_{i}) denotes the indicator function, which equals one if Yi=gY\_{i}=g and zero otherwise. Besides the semi- and nonparametric approaches described so far, there are many further methods that could be used for the classification of functional data. After dimension reduction via FPCA, for instance, the obtained scores may be used as input to any statistical or machine learning algorithm designed for the classification of multivariate data, e.g., a random forest or a neural net. Also, functional data may be used directly in some situations, e.g., as input to a convolutional neural network. Please refer to Section [6](https://arxiv.org/html/2312.05523v1#S6 "6 Machine Learning Approaches ‣ Functional Data Analysis:An Introduction and Recent Developments") for details. A recent review on functional data classification is provided by [Wang et al. (2023)](https://arxiv.org/html/2312.05523v1#bib.bib208 "").

### 5.2 Clustering

In [5.1](https://arxiv.org/html/2312.05523v1#S5.SS1 "5.1 Classification of Functional Data ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") above, functional data came from distinct classes 1,…,G1,\\ldots,G, which were known for the training data and unknown for the test data. The purpose was to classify the test data using a classification rule that was learned from the training data. Since there are known class labels for the training data, this type of learning problem is also called _supervised_ learning. If those classes are not given but are to be built using the (functional) data only, we call this process ‘clustering’, which is a so-called _unsupervised_ learning problem. Further supervised and unsupervised learning techniques for functional data from a machine learning perspective are discussed in Section [6](https://arxiv.org/html/2312.05523v1#S6 "6 Machine Learning Approaches ‣ Functional Data Analysis:An Introduction and Recent Developments"). The basic idea of clustering is that data are grouped, such that those groups, the ‘clusters’, are homogeneous in some sense. A survey on functional data clustering is, for instance, provided by [Jacques and Preda (2014a)](https://arxiv.org/html/2312.05523v1#bib.bib88 ""). Here, we will only give a short, and not necessarily exhaustive overview.

In general, most clustering methods (not only functional clustering) can roughly be classified as either ‘data/observation-based’ or ‘model-based’. In the latter case, it is assumed that the data observed are generated by some underlying stochastic mechanism. Then, observations can, e.g., be clustered according to conditional class probabilities. Data-based methods, by contrast, make no distributional assumptions but start directly from the data. Common strategies involve hierarchical clustering and k-means (or variants thereof, such as k-median or k-medoids). Hierarchical clustering algorithms are typically distance-based and either successively group similar objects into clusters and fuse clusters (‘agglomerative’ hierarchical clustering), or subsequently split larger into smaller clusters (‘divisive’ hierarchical clustering). The concrete form of the algorithm results from the chosen distance measures for objects and clusters. In both cases, a ‘hierarchy’ of partitions is created from which clusters might be chosen. For details on hierarchical clustering, see, e.g., [Murtagh and Contreras (2012)](https://arxiv.org/html/2312.05523v1#bib.bib134 ""). As an alternative, we may try to optimize some criterion across all potential partitions into kk clusters. The latter is done with k-means, etc.; and a couple of different algorithms have been proposed for doing so ([MacQueen, 1967](https://arxiv.org/html/2312.05523v1#bib.bib115 ""); [Hartigan and Wong, 1979](https://arxiv.org/html/2312.05523v1#bib.bib76 ""); just to name two of the most prominent references). For an overview of clustering algorithms (including categorizations apart from data vs. model-based) see, e.g., [Ezugwu et al. (2021)](https://arxiv.org/html/2312.05523v1#bib.bib42 "") and references therein.

With functional data, we suggest classifying clustering algorithms according to the _two_ dimensions ‘data/observation-based’ vs. ‘model-based’, _and_ ‘raw data methods’ vs. ‘dimension reduction’, because any combination may be possible. In the case of raw data methods, curves are clustered on the basis of their evaluation points. Within the ‘dimension reduction’ category, we may further distinguish between ‘filtering methods’ and ‘adaptive methods’ ( [Jacques and Preda, 2014a](https://arxiv.org/html/2312.05523v1#bib.bib88 "")). Filtering methods first approximate the functions by using a set of basis functions and then use the basis coefficients for clustering. Adaptive methods, by contrast, carry out dimension reduction and clustering simultaneously, which may involve that also the type and number of basis functions may depend on the cluster. Model-based functional clustering typically assumes a mixture model that is based on some kind of basis expansion. For instance, [James and Sugar (2003)](https://arxiv.org/html/2312.05523v1#bib.bib90 "") use a spline basis and assume that basis coefficients follow cluster-specific Gaussian distributions. [Bouveyron and Jacques (2011)](https://arxiv.org/html/2312.05523v1#bib.bib11 "") and [Jacques and Preda (2013)](https://arxiv.org/html/2312.05523v1#bib.bib87 "") allow for cluster-specific eigendecompositions (FPCA). Similarly to usual, model-based clustering for multivariate data, various specifications for the underlying Gaussian distributions are possible, leading to different numbers of unknown parameters that need to be estimated, e.g., using an EM-type algorithm; compare [Bouveyron and Jacques (2011)](https://arxiv.org/html/2312.05523v1#bib.bib11 "") for details. A Bayesian version of model-based clustering for functional data is, for instance, used in [Heard et al. (2006)](https://arxiv.org/html/2312.05523v1#bib.bib77 ""). Extensions to multivariate functional data are, e.g., provided by [Jacques and Preda (2014b)](https://arxiv.org/html/2312.05523v1#bib.bib89 "") and [Schmutz et al. (2020)](https://arxiv.org/html/2312.05523v1#bib.bib170 ""). More generally speaking, all those approaches correspond to the ‘adaptive methods’ from above, and have to be distinguished from the much simpler, two-stage approach of calculating principal component scores on the entire data set first, and then using those values as input to an algorithm for model-based clustering of usual, multivariate data (which would be a ‘filtering method’). Analogously, distances between functions may be computed/defined via a basis expansion and corresponding basis coefficients, and then be used as input to hierarchical clustering or k-means, which can be described as ‘dimension reduction in combination with data/observation-based clustering’. By contrast, if computing distances directly from raw data, we would end up with a raw, observation-based functional clustering. A discussion of k-means, dimension reduction (particularly FPCA), and specific cases of equivalence between approaches is found in [Tarpey and Kinateder (2003)](https://arxiv.org/html/2312.05523v1#bib.bib195 ""). Of course, in addition to dimension reduction, there may also be other pre-processing steps before calculating distances between functions; see, e.g., [Ieva et al. (2013)](https://arxiv.org/html/2312.05523v1#bib.bib86 "").

Figure 11: Results for hierarchical clustering with complete linkage of functional data from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left), with dendrogram (left) and visualization of the 2-cluster solution by age and sex (right).

For illustration, let us consider the curves from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left). To start with, we use the Euclidean distance on the raw data (compare [3.2.2](https://arxiv.org/html/2312.05523v1#S3.SS2.SSS2 "3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments")) as input to hierarchical clustering with complete linkage. The resulting dendrogram is found in Figure [11](https://arxiv.org/html/2312.05523v1#S5.F11 "Figure 11 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") (left), where we can nicely see how curves are successively grouped (bottom-up) into clusters. From the dendrogram, we also get the impression that the data set essentially consists of two clusters. Those two clusters in the space of the first two principal components are found in Figure [12](https://arxiv.org/html/2312.05523v1#S5.F12 "Figure 12 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") (left). The distribution of age and sex in the clusters is shown in Figure [11](https://arxiv.org/html/2312.05523v1#S5.F11 "Figure 11 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") (right). We see that females are primarily found in cluster 1 whereas cluster 2 mainly consists of males. On average, people in cluster 1 are a little bit older, but the overlap of clusters is much larger for age than sex. Instead of using the raw data, we could also carry out FPCA first. Then, we could use the component scores as input to a standard clustering algorithm for multivariate data, such as hierarchical clustering or k-means. The latter approach minimizes the so-called _within-cluster sum of squares_ across all potential partitions into kk clusters. With k=2k=2, we obtain the clusters as shown in Figure [12](https://arxiv.org/html/2312.05523v1#S5.F12 "Figure 12 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments"). If looking at the scores of the first two principal components (Figure [12](https://arxiv.org/html/2312.05523v1#S5.F12 "Figure 12 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments"), left), we see that clusters are primarily determined by the first principal component. The first eigenfunction is depicted in pink in Figure [12](https://arxiv.org/html/2312.05523v1#S5.F12 "Figure 12 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") (right), together with the functional data observed and the clustering. In particular, in the plot’s left part, we see how small (i.e., negative) values in the first principal component translate into cluster 2 membership, as cluster 2 mainly consists of curves with a first peak shifted to the right (dashed black). Also, it should be noted that the clusters that are obtained with k-means of FPCA scores (Figure [12](https://arxiv.org/html/2312.05523v1#S5.F12 "Figure 12 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments")) are precisely the same as those obtained with hierarchical clustering/complete linkage on the raw data above (Figure [11](https://arxiv.org/html/2312.05523v1#S5.F11 "Figure 11 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments")).

Figure 12: Results for k-means clustering using principal component scores of functional data from Figure [1](https://arxiv.org/html/2312.05523v1#S1.F1 "Figure 1 ‣ 1.3 Running data example(s): human motion and motor control ‣ 1 Introduction ‣ Functional Data Analysis:An Introduction and Recent Developments") (left), with clusters in the space of the first two principal components (left) and visualization of the 2-cluster solution in the functions’ space together with the first eigenfunction (right). Note, this gives the same result as hierarchical clustering with complete linkage using the raw data (compare Figure [11](https://arxiv.org/html/2312.05523v1#S5.F11 "Figure 11 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments"), left). The blue color indicates the one curve (12) that moves from cluster 1 into cluster 2 if using model-based, adaptive clustering.

A minimal change in the clusters is observed if using the model-based, adaptive approach by [Bouveyron and Jacques (2011)](https://arxiv.org/html/2312.05523v1#bib.bib11 ""), where different FPCA solutions are allowed between clusters. Then, one observation (female, age 24), as marked in blue in Figure [12](https://arxiv.org/html/2312.05523v1#S5.F12 "Figure 12 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments"), moves from cluster 1 into cluster 2. This curve is somewhat peculiar regarding the beginning of the cycle; compare the blue line in Figure [12](https://arxiv.org/html/2312.05523v1#S5.F12 "Figure 12 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") (right). Otherwise, however, clustering results are very consistent across different algorithms here.

### 5.3 Software

After dimension reduction (FPCA, spline basis, etc.) using already discussed functions, e.g., from R packages fda or refund, estimated component scores or basis coefficients can simply be used as input to standard cluster algorithms such as hclust() or kmeans() from R’s basic stats package ( [R Core Team, 2023](https://arxiv.org/html/2312.05523v1#bib.bib153 "")); compare Figure [12](https://arxiv.org/html/2312.05523v1#S5.F12 "Figure 12 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments"). Also functions from the cluster( [Maechler et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib116 "")) package can be used. If algorithms work on distance/similarity matrices, the latter may also be computed on raw data, e.g., using the dist() function in R, as has been done above (compare Figure [11](https://arxiv.org/html/2312.05523v1#S5.F11 "Figure 11 ‣ 5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments")). Model-based clustering for multivariate data is, for instance, provided by [Scrucca et al. (2016)](https://arxiv.org/html/2312.05523v1#bib.bib172 "") through R-package mclust. A functional version as employed above ( [Bouveyron and Jacques, 2011](https://arxiv.org/html/2312.05523v1#bib.bib11 ""); [Schmutz et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib170 "")) is available in funHDDC( [Schmutz et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib171 "")).

## 6 Machine Learning Approaches

Functional data analysis can also be found in machine learning (ML) and its deep learning (DL) subcategory. We here mainly focus on models for supervised learning. In contrast to previously discussed methods, analyses in ML and DL mainly target predictive performance and the incorporation of functional data primarily serves as an appropriate data representation, rather than to allow for an interpretable relationship of (functional) model in- and outputs. We will also outline a few approaches that deal with unsupervised learning or generative approaches and are related to unsupervised approaches described in Section [5](https://arxiv.org/html/2312.05523v1#S5 "5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments").

### 6.1 Implicit Approaches

In analogy to the different types of regression (FOSR, SOFR, and FOFR) in previous sections, models in ML are categorized by the nature of their input and output. For a scalar outcome, a distinction is usually made between a _classification_ and a _regression task_. Classification includes statistical modeling tasks where the outcome is of discrete nature, e.g., Bernoulli- or multinoulli-distributed, while regression in ML is often used as an umbrella term for all modeling tasks including continuous outcomes (e.g., normally distributed response). Many different ML approaches only implicitly deal with functional data and do not explicitly account for the functional nature of variables, e.g., the smoothness of the inputs. Instead, functional covariates are considered as sequences or (multivariate) time series ( [Ott et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib138 ""), see, e.g.,). Another common practice is to calculate summary statistics of the functional inputs (the mean of the function, location of the mode, different frequency statistics, etc.) to characterize inputs using scalar values instead of using the actual functions ( [Vogel et al., 2022](https://arxiv.org/html/2312.05523v1#bib.bib204 ""), e.g.,). These statistics can subsequently be used with classical ML approaches intended for scalar data inputs and pre-processing steps turning functional into scalar values are defined as a (tunable) pre-processing pipeline. [Pfisterer et al. (2019)](https://arxiv.org/html/2312.05523v1#bib.bib149 "") compare such classical ML approaches with functional classification algorithms described in Section [3.1.1](https://arxiv.org/html/2312.05523v1#S3.SS1.SSS1 "3.1.1 Scalar-on-Functions Regression (SOFR) ‣ 3.1 Introduction/Overview ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"). An alternative representation of functional inputs in, e.g., the field of biomechanics, is a picture representation of multivariate functions ( [Liew et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib110 "")). Given all functional inputs have the same domain 𝒯\\mathcal{T}, the approach concatenates the pp functional observations (xi​1​(tv),…,xi​p​(tv))(x\_{i1}(t\_{v}),\\ldots,x\_{ip}(t\_{v})) for v=1,…,Vv=1,\\ldots,V to a V×pV\\times p dimensional matrix for every observation ii, which is then considered as an “image” in the subsequent analysis. This allows the use of pre-trained models and is based on the idea of transfer learning ( [Pan and Yang, 2010](https://arxiv.org/html/2312.05523v1#bib.bib139 ""), see, e.g.,). For functional outcomes, ML methods are often referred to as trajectory regression ( [Ott et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib138 "")) or sequence-to-sequence models ( [Sutskever et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib191 "")). Most approaches do not impose smoothness of the output function, but either adjust the loss function to favor smooth(er) outputs or impose regularization to foster generalization and thereby implicitly generate smoother output functions.

In addition to the previously described implicit approaches, there is also a body of literature in ML that explicitly takes the functional nature of objects into account. We describe several methods in the next subsection.

### 6.2 Explicit Approaches

##### Machine Learning

Among the classic ML approaches, [Rossi and Villa (2006)](https://arxiv.org/html/2312.05523v1#bib.bib163 "") are one of the first to propose an explicit approach for functional data by adapting support vector machines (SVMs) for FD. SVMs are kernel-based methods, but in contrast to the use of kernels in Section [3.2.2](https://arxiv.org/html/2312.05523v1#S3.SS2.SSS2 "3.2.2 Non-parametric Approaches ‣ 3.2 Semi- and Fully Non-Parametric Approaches ‣ 3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"), SVMs utilize kernels K⁡(⋅,⋅)K(\\cdot,\\cdot) as a distance measure between two observations. [Rossi and Villa (2006)](https://arxiv.org/html/2312.05523v1#bib.bib163 "") argue that, although kernels in principle also work for functions in a Hilbert space ℋ\\mathcal{H}, it is difficult to implement calculations in practice and these kernels do not take advantage of the functional nature of the data. The authors derive a simple solution by defining a map 𝒫\\mathcal{P} from ℋ\\mathcal{H} to the Euclidean space. In this space classic kernels K⁡(⋅,⋅)K(\\cdot,\\cdot) such as the Gaussian or exponential kernel can be straightforwardly implemented and then used as K⁡(𝒫⁡(f),𝒫⁡(g))K(\\mathcal{P}(f),\\mathcal{P}(g)) to evaluate the distance between to functions f,g∈ℋf,g\\in\\mathcal{H}. Another kernel-based ML approach is Gaussian processes (GPs). An adaptation of GPs called Gaussian process functional regression (GPFR) for functional data has been proposed in [Shi and Choi (2011)](https://arxiv.org/html/2312.05523v1#bib.bib177 "") with implementation in [Konzen et al. (2021)](https://arxiv.org/html/2312.05523v1#bib.bib100 ""). GPFR additively combines the mean estimation of a functional regression model with a multivariate GP. The linear (functional) effects of scalar or functional covariates thereby define the mean of the functional response while functional covariate(s) over 𝒯\\mathcal{T} or the time information is used for the estimation of the covariance using the GP. Another important class of ML models is boosting. Gradient boosting approaches for functional regression models and various extensions have been proposed by [Brockhaus et al. (2015)](https://arxiv.org/html/2312.05523v1#bib.bib12 ""); [Brockhaus et al. (2017)](https://arxiv.org/html/2312.05523v1#bib.bib13 ""); [Rügamer et al. (2018)](https://arxiv.org/html/2312.05523v1#bib.bib165 ""). By not relying on regression trees but on single additive predictors, the corresponding boosting implementation ( [Brockhaus et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib14 "")) can be seen as a special coordinate-wise gradient descent optimization routine. The Gauss-Southwell-type update rule in this case guarantees good convergence and additionally induces sparsity due to the coordinate-wise nature of the optimization. This, in particular, allows fitting functional regression models in very high dimensions as the optimization routine only optimizes the effect of one (functional) feature at a time. Other extensions of this approach have been proposed recently, including densities-on-scalar regression models using a Bayes Hilbert space representation ( [Maier et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib117 "")) or functional additive models on manifolds of planar shape and form ( [Stöcker et al., 2022b](https://arxiv.org/html/2312.05523v1#bib.bib188 "")). Finally, tree-based methods have also been brought forward, both for functional covariates using random forests ( [Möller et al., 2016](https://arxiv.org/html/2312.05523v1#bib.bib131 ""); [Rahman et al., 2019](https://arxiv.org/html/2312.05523v1#bib.bib154 "")), and also via functional random forests for functional outcomes ( [Fu et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib51 "")).

In addition to these supervised learning approaches, several unsupervised methods with explicit function representation exist. The most prominent example is functional data clustering ( [Tarpey and Kinateder, 2003](https://arxiv.org/html/2312.05523v1#bib.bib195 "")) as explained in detail in Section [5.2](https://arxiv.org/html/2312.05523v1#S5.SS2 "5.2 Clustering ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments"). An overview can be found in [Jacques and Preda (2014a)](https://arxiv.org/html/2312.05523v1#bib.bib88 ""). In DL, one prominent unsupervised learning technique is autoencoders ( [Kingma and Welling, 2013](https://arxiv.org/html/2312.05523v1#bib.bib94 ""), AEs;), which try to encode a high-dimensional input into a small number of hidden variables and then decode these variables back to the original input size with the goal to recover the original input. A recent adaption of AE is given by [Hsieh et al. (2021)](https://arxiv.org/html/2312.05523v1#bib.bib82 ""), proposing a functional autoencoder. The proposed approach can be seen as a non-linear extension of FPCA. Another method that can be seen as an unsupervised technique from an ML perspective is function registration, which has recently been combined with deep neural networks ( [Chen and Srivastava, 2021](https://arxiv.org/html/2312.05523v1#bib.bib21 "")). The following paragraph will explain the idea of functions in neural networks in some more detail.

##### Deep Learning and Neural Networks

[Rossi et al. (2002)](https://arxiv.org/html/2312.05523v1#bib.bib164 "") are among the first to combine neural networks with functional data by proposing a multi-layer perceptron (MLP) for functional data and also extending the universal approximation theorem of neural networks ( [Hornik et al., 1989](https://arxiv.org/html/2312.05523v1#bib.bib79 "")) to functional inputs. An MLP for scalar values is defined by multiple neurons gathered in layers that are in turn stacked onto each other. Every neuron (or unit) can be seen as a function h:ℝ→ℝ,x↦τ⁡(b+w​x)h:\\mathbb{R}\\to\\mathbb{R},x\\mapsto\\tau(b+wx) that takes a scalar value xx and computes a hidden state value of the form τ⁡(b+w​x)\\tau(b+wx) with bias (intercept) bb, weight (coefficient) ww and activation (response) function τ\\tau. Similar to scalar-on-function regression, a functional analog for functional inputs xx can be defined by τ⁡(b+∫w⁡(t)​x​(t)​𝑑t)\\tau(b+\\int w(t)x(t)dt) and approximated at given measurement points by finding a suitable approximation for w⁡(t)w(t) and the integral over tt. This will result in units h:ℋ→ℝh:\\mathcal{H}\\to\\mathbb{R} that take functions as input and output a scalar value. Thus, the MLP is only functional in its first layer, while the following layers consist of conventional layers and neurons. In recent years, various other authors have proposed extensions and unifications ( [Guss, 2016](https://arxiv.org/html/2312.05523v1#bib.bib67 ""); [Wang et al., 2019](https://arxiv.org/html/2312.05523v1#bib.bib207 ""); [Thind et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib197 ""); [Rao and Reimherr, 2023](https://arxiv.org/html/2312.05523v1#bib.bib159 "")). For functional response variables, the functional MLP can be extended in an analogous manner to the extension from a scalar-on-function to a function-on-function regression. The kkth output neuron hk(l)h\_{k}^{(l)} of a functional layer l=1,…,Ll=1,\\ldots,L in a functional MLP with LL layers, each with JlJ\_{l} output neurons, is recursively defined by its previous layers as

|     |     |     |     |
| --- | --- | --- | --- |
|  | hk(l)​(t)=τ(l)​(bk(l)​(t)+∑j=1Jl−1∫wj,k(l)​(s,t)​hj(l−1)​(s)​𝑑s),h^{(l)}\_{k}(t)=\\tau^{(l)}\\left(b\_{k}^{(l)}(t)+\\sum\_{j=1}^{J\_{l-1}}\\int w\_{j,k}^{(l)}(s,t)h^{(l-1)}\_{j}(s)ds\\right), |  | (30) |

where bk(l)∈ℒ2​(𝒯)b\_{k}^{(l)}\\in\\mathcal{L}^{2}(\\mathcal{T}) and wj,k(l)∈ℒ2​(𝒯×𝒯)w\_{j,k}^{(l)}\\in\\mathcal{L}^{2}(\\mathcal{T}\\times\\mathcal{T}). In addition, special roles are given to the input layer by defining hj(0)​(⋅)=xj​(⋅)h\_{j}^{(0)}(\\cdot)=x\_{j}(\\cdot) for all covariates j=1,…,pj=1,\\ldots,p, and the very last layer consisting of only one unit JL=1J\_{L}=1 defined as h(L)​(t)=𝔼⁡(Y⁡(t)\|𝑿)h^{(L)}(t)=\\mathbb{E}(Y(t)\|\\boldsymbol{X}), where 𝑿\\boldsymbol{X} collects all pp functional covariates. Similar to the mean function, it is also possible to learn the covariance kernel using deep neural networks ( [Sarkar and Panaretos, 2022](https://arxiv.org/html/2312.05523v1#bib.bib167 "")). An extension to neural networks that model functional data both with structured predictors and arbitrary deep neural network architectures has been recently proposed by [Rügamer et al. (2023)](https://arxiv.org/html/2312.05523v1#bib.bib166 "").

### 6.3 Benchmark Comparison

To demonstrate the performance of different methods presented in this section, we conduct a small benchmark comparison between selected methods with available software implementations.
We want to emphasize that all ML and DL methods are not tuned but either used with default settings or trained with values from preliminary experiments. We use two implicit neural network approaches as proposed in [Liew et al. (2021)](https://arxiv.org/html/2312.05523v1#bib.bib110 "") that represent functional covariates as images. One network is a classic convolutional neural network (CNN) with several convolution blocks to process the “image” and predict a vector of the length of the discretized output function y⁡(t)y(t). The second implicit neural network approach uses a pre-trained deep neural network (more specifically the ImageNet architecture ( [Deng et al., 2009](https://arxiv.org/html/2312.05523v1#bib.bib36 ""))) and applies transfer learning for the given “images”. We also use an explicit functional neural network as proposed by [Thind et al. (2020)](https://arxiv.org/html/2312.05523v1#bib.bib197 "") (FuncNN), the boosting approach FDboost by [Brockhaus et al. (2020)](https://arxiv.org/html/2312.05523v1#bib.bib14 "") and compare these approaches against a statistical approach, the pffr function for penalized function-on-function regression in [Goldsmith et al. (2020)](https://arxiv.org/html/2312.05523v1#bib.bib63 ""), see also Section [3](https://arxiv.org/html/2312.05523v1#S3 "3 Functional Regression ‣ Functional Data Analysis:An Introduction and Recent Developments"). We split the data into a train and test set, using the ankle moment (inversion-eversion) as the outcome function and the different joint accelerations, velocities, and angles of all three body parts as functional covariates. For all methods except for the CNNs, we additionally use the scalar covariates age, height, weight, and sex as scalar features. For structured models (pffr, FDboost), we also incorporate random effects for the running condition and the study. Figure [13](https://arxiv.org/html/2312.05523v1#S6.F13 "Figure 13 ‣ 6.3 Benchmark Comparison ‣ 6 Machine Learning Approaches ‣ Functional Data Analysis:An Introduction and Recent Developments") depicts the true functions in the test set as well as predictions of the five methods. In addition, test performance results for the average point-wise root mean squared error (RMSE) between actual and predicted functions is given for every method. Results suggest that methods all work well in general capturing the overall trend in the data, but the approaches estimating an additive model (FDboost, pffr) perform better in the details than the different neural network approaches.

Figure 13: Comparison of different ML and DL methods (facets) to fit a function-on-function relationship on the running data with respective test RMSE values for every method in the bottom left corner.

### 6.4 Software

Software packages that model functional data explicitly using machine and deep learning include FDboost( [Brockhaus et al., 2017](https://arxiv.org/html/2312.05523v1#bib.bib13 "")) building on a model-based boosting framework, FuncNN( [Thind et al., 2020](https://arxiv.org/html/2312.05523v1#bib.bib197 "")) for functional neural networks, funGp( [Betancourt et al., 2023](https://arxiv.org/html/2312.05523v1#bib.bib8 "")) using GPs for functional inputs or GPFDA( [Shi et al., 2023](https://arxiv.org/html/2312.05523v1#bib.bib178 "")) to combine functional regression with GPs.

## 7 Outlook

### 7.1 Functional data and related fields

While we discussed the differences between FDA, LDA, and time series analysis in the introduction, developments in functional data analysis have also led to fruitful cross-fertilization in these other two areas. Depending on the goal of the analysis and the data structure, especially the semi/nonparametric analysis methods
of FDA can also be of interest in these two fields. In particular,
longitudinal data can be viewed as sparse (and noisy) functional data.
FDA then provides new perspectives: the commonly used linear mixed models for longitudinal data are parametric, with, e.g., a random intercept random slope model being linear over time per subject (observational unit). On the other hand, FPCA with its subject-specific random scores for the general principal component (PC) functions, can be viewed as a linear mixed model with data-driven PC basis functions replacing the constant and linear basis functions, yielding larger flexibility and a better semi-parametric fit to the longitudinal data ( [Yao et al., 2005](https://arxiv.org/html/2312.05523v1#bib.bib215 ""); [Goldsmith et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib60 ""), e.g.).
Similar approaches have also been successfully incorporated in
joint models for longitudinal and time-to-event data to allow for more flexible modeling of the univariate or multivariate longitudinal trajectories ( [Köhler et al., 2017](https://arxiv.org/html/2312.05523v1#bib.bib95 ""); [Köhler et al., 2018](https://arxiv.org/html/2312.05523v1#bib.bib96 ""); [Li et al., 2022](https://arxiv.org/html/2312.05523v1#bib.bib104 ""); [Volkmann et al., 2023b](https://arxiv.org/html/2312.05523v1#bib.bib206 ""), e.g.).
While time series analysis usually focuses on one time series, there are also cases where a sample of time series is collected and questions such as time series classification are of interest, in which case functional data classification methods can be utilized as discussed in Sections [5.1](https://arxiv.org/html/2312.05523v1#S5.SS1 "5.1 Classification of Functional Data ‣ 5 Classification and Clustering ‣ Functional Data Analysis:An Introduction and Recent Developments") and [6](https://arxiv.org/html/2312.05523v1#S6 "6 Machine Learning Approaches ‣ Functional Data Analysis:An Introduction and Recent Developments"). Generally, there are often
different ways to look at the same data depending on the research questions of interest. In addition to longitudinal and time series data, this also holds, e.g., for spatio-temporal data, which depending on the setting and questions of interest could also often be viewed as repeated observations of spatial random fields over time, or spatially correlated curves (time series or functional data) over time ( [Delicado et al., 2010](https://arxiv.org/html/2312.05523v1#bib.bib35 ""); [Kokoszka, 2012](https://arxiv.org/html/2312.05523v1#bib.bib97 ""), e.g.,). Besides spatial correlation, functional data can appear with other additional structures known from scalar data, such as, e.g., functional time series ( [Hyndman and Shang, 2009](https://arxiv.org/html/2312.05523v1#bib.bib84 ""); [Kokoszka, 2012](https://arxiv.org/html/2312.05523v1#bib.bib97 ""); [Aue et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib3 ""), e.g.,) or longitudinal functional data ( [Greven et al., 2010](https://arxiv.org/html/2312.05523v1#bib.bib66 ""); [Park and Staicu, 2015](https://arxiv.org/html/2312.05523v1#bib.bib143 ""), e.g.,).
[Koner and Staicu (2023)](https://arxiv.org/html/2312.05523v1#bib.bib98 "") call multivariate functional data, longitudinal functional data, functional time series, and spatially correlated functional data “second-generation functional data” and provide a review.

### 7.2 Beyond one-dimensional functions

Functional data analysis is still an active field of research with many current developments. In recent years, an important focus of the field has been to broaden the view and see functional data as just one example of more general ‘object data’, i.e., of data where each observation constitutes an object in a more complex space than the usual ℝd\\mathbb{R}^{d} space for vectors. This area is sometimes called object (oriented) data analysis ( [Marron and Alonso, 2014](https://arxiv.org/html/2312.05523v1#bib.bib120 "")). While the univariate functional data considered here are often viewed as objects in the ℒ2​(𝒯)\\mathcal{L}^{2}(\\mathcal{T}) of square-integrable functions on some interval 𝒯⊂ℝ\\mathcal{T}\\subset\\mathbb{R}, images and surface-valued data ( [Goldsmith et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib61 ""); [Happ and Greven, 2018](https://arxiv.org/html/2312.05523v1#bib.bib73 ""), e.g.,) can be viewed as ℒ2​(𝒯)\\mathcal{L}^{2}(\\mathcal{T}) functions on a higher-dimensional domain 𝒯⊂ℝd\\mathcal{T}\\subset\\mathbb{R}^{d}, d>1d>1, while multivariate functions are often defined on an interval 𝒯\\mathcal{T} but to be vector-valued in ℝd\\mathbb{R}^{d}, d>1d>1( [Chiou et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib27 ""); [Górecki et al., 2018](https://arxiv.org/html/2312.05523v1#bib.bib64 ""), e.g.,), with a more general setting considered in ( [Happ and Greven, 2018](https://arxiv.org/html/2312.05523v1#bib.bib73 "")). Examples are brain scans for the former, and movement trajectories, outlines, or several recorded functions for the latter ( [Steyer et al., 2023a](https://arxiv.org/html/2312.05523v1#bib.bib185 ""); [Steyer et al., 2023b](https://arxiv.org/html/2312.05523v1#bib.bib186 ""); [Volkmann et al., 2023a](https://arxiv.org/html/2312.05523v1#bib.bib205 ""), e.g.,). Many methods developed for univariate functional data can be suitably extended to images and multivariate functional data such as, e.g., functional principal component analysis ( [Berrendero et al., 2011](https://arxiv.org/html/2312.05523v1#bib.bib7 ""); [Chiou et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib27 ""); [Happ and Greven, 2018](https://arxiv.org/html/2312.05523v1#bib.bib73 ""), e.g.,) or regression models ( [Goldsmith et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib61 ""); [Chiou et al., 2016](https://arxiv.org/html/2312.05523v1#bib.bib28 ""); [Volkmann et al., 2023a](https://arxiv.org/html/2312.05523v1#bib.bib205 ""), e.g.,). For both settings, phase variation can also be important, for image analysis due to necessary registration. For multivariate functional data, it can also be relevant to have the analysis be invariant to warping, i.e., only analyze the image of a curve, such as when an outline of an object such as a cell or bone is recorded and the parametrization of the curve along that outline is essentially arbitrary. In this case, the object of interest is the equivalence class of such curves with respect to reparametrization, and methods such as distance and mean computation as well as regression have also been developed for such elements of quotient spaces ( [Srivastava et al., 2010b](https://arxiv.org/html/2312.05523v1#bib.bib183 ""); [Srivastava and Klassen, 2016](https://arxiv.org/html/2312.05523v1#bib.bib181 ""); [Steyer et al., 2023a](https://arxiv.org/html/2312.05523v1#bib.bib185 ""); [Steyer et al., 2023b](https://arxiv.org/html/2312.05523v1#bib.bib186 ""), e.g.,). Similarly, the shape/form of an object (an outline or vector of landmark coordinates) is considered to be the equivalence class under rotation, translation, and (for shape) scale ( [Dryden and Mardia, 2016](https://arxiv.org/html/2312.05523v1#bib.bib39 "")), and is of interest if the coordinate system of the recorded object is arbitrary or not relevant. Such shapes/forms live on certain manifolds ( [Huckemann et al., 2009](https://arxiv.org/html/2312.05523v1#bib.bib83 ""); [Thomas Fletcher, 2013](https://arxiv.org/html/2312.05523v1#bib.bib198 ""); [Stöcker et al., 2022b](https://arxiv.org/html/2312.05523v1#bib.bib188 ""), e.g.,) or in more complex quotient spaces, e.g., if parametrization invariance is simultaneously considered ( [Stöcker et al., 2022a](https://arxiv.org/html/2312.05523v1#bib.bib187 ""); [Steyer et al., 2023a](https://arxiv.org/html/2312.05523v1#bib.bib185 ""), e.g.).
Shape analysis ( [Dryden and Mardia, 2016](https://arxiv.org/html/2312.05523v1#bib.bib39 "")) is an important field in itself and has more recently intersected with functional data analysis in functional shape analysis ( [Srivastava and Klassen, 2016](https://arxiv.org/html/2312.05523v1#bib.bib181 "")) when the shape of a curve is of interest, e.g., as the outcome in a regression model ( [Stöcker et al., 2022b](https://arxiv.org/html/2312.05523v1#bib.bib188 "")).
Similarly, compositional data analysis
( [van den Boogaart and Tolosana-Delgado, 2013](https://arxiv.org/html/2312.05523v1#bib.bib201 ""); [Pawlowsky-Glahn et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib148 ""); [Filzmoser et al., 2018](https://arxiv.org/html/2312.05523v1#bib.bib49 "")) is a field with a long tradition, looking at multivariate vectors of non-negative entries that add up to a constant such as 1 or 100%. It takes into account the special geometry of the simplex, which compositions are elements of. More recently, this field has also intersected with functional data analysis when looking at probability densities, which can be viewed as functional data with particular constraints or as infinite compositions. More generally, continuous, discrete, mixed, bivariate, etc. densities can be considered ( [Maier et al., 2021](https://arxiv.org/html/2312.05523v1#bib.bib117 ""), e.g.,), with one possible geometry given by the so-called Bayes-Hilbert-space approach ( [van den Boogaart et al., 2010](https://arxiv.org/html/2312.05523v1#bib.bib202 ""); [van den Boogaart et al., 2014](https://arxiv.org/html/2312.05523v1#bib.bib203 "")) and compositions seen as the special case of discrete densities. Other possible approaches include Wasserstein spaces ( [Panaretos and Zemel, 2020](https://arxiv.org/html/2312.05523v1#bib.bib142 "")). Further examples of object data include so-called generalized functional data ( [Hall and Yao, 2008](https://arxiv.org/html/2312.05523v1#bib.bib72 ""); [Goldsmith et al., 2015](https://arxiv.org/html/2312.05523v1#bib.bib62 ""); [Scheipl et al., 2016](https://arxiv.org/html/2312.05523v1#bib.bib169 ""); [Greven and Scheipl, 2017](https://arxiv.org/html/2312.05523v1#bib.bib65 ""); [Gertheiss et al., 2017](https://arxiv.org/html/2312.05523v1#bib.bib57 ""), e.g.,), where conditional on a smooth mean curve over 𝒯\\mathcal{T} as in functional data, observed values are viewed as realizations from some non-Gaussian (e.g., binary or count) distribution, directional data ( [Mardia, 1975](https://arxiv.org/html/2312.05523v1#bib.bib119 ""); [Mardia, 1988](https://arxiv.org/html/2312.05523v1#bib.bib118 "")), covariance-(matrix- or operator-)valued data ( [Masarotto et al., 2019](https://arxiv.org/html/2312.05523v1#bib.bib124 ""); [Lin et al., 2023](https://arxiv.org/html/2312.05523v1#bib.bib111 ""), e.g.,), point-process-valued data ( [Panaretos and Zemel, 2016](https://arxiv.org/html/2312.05523v1#bib.bib141 ""), e.g.,), and tree- or network-valued data ( [Feragen et al., 2013](https://arxiv.org/html/2312.05523v1#bib.bib46 ""); [Duncan et al., 2018](https://arxiv.org/html/2312.05523v1#bib.bib40 ""); [Calissano et al., 2022](https://arxiv.org/html/2312.05523v1#bib.bib16 ""); [Calissano et al., 2023](https://arxiv.org/html/2312.05523v1#bib.bib17 ""), e.g.,). In contrast to neighboring fields such as graphical models, the focus is not on modeling, e.g., a single network, but always on the setting where a sample of networks or more generally objects is observed. The objects constitute the unit of analysis, e.g., the response or covariate in a regression model. Many developments are expected to occur in this exciting field in the coming years.

## Acknowledgement

Sonja Greven gratefully acknowledges funding by grants GR 3793/2-2, GR 3793/3-1 and GR 3793/8-1 from the German research foundation (DFG). Bernard Liew is supported by The Academy of Medical Sciences, UK, Springboard Award SBF006/1019.

## References

- Aneiros et al. \[2022\]
G. Aneiros, S. Novo, and P. Vieu.

Variable selection in functional regression models: A review.

_Journal of Multivariate Analysis_, 188:104871, Mar.
2022.

- Arribas-Gil and Romo \[2014\]
A. Arribas-Gil and J. Romo.

Shape outlier detection and visualization for functional data: the
outliergram.

_Biostatistics_, 15(4):603–619, 2014.

- Aue et al. \[2015\]
A. Aue, D. D. Norinho, and S. Hörmann.

On the prediction of stationary functional time series.

_Journal of the American Statistical Association_, 110(509):378–392, 2015.

- Barber et al. \[2017\]
R. F. Barber, M. Reimherr, and T. Schill.

The function-on-scalar LASSO with applications to longitudinal
GWAS.

_Electronic Journal of Statistics_, 11(1):1351–1389, Jan. 2017.

Publisher: Institute of Mathematical Statistics and Bernoulli
Society.

- Benjamini and Yekutieli \[2001\]
Y. Benjamini and D. Yekutieli.

The control of the false discovery rate in multiple testing under
dependency.

_The Annals of Statistics_, 29:1165–1188, 2001.

- Benko et al. \[2009\]
M. Benko, W. Härdle, and K. A.

Common functional principal components.

_The Annals of Statistics_, 37:1–34, 2009.

- Berrendero et al. \[2011\]
J. R. Berrendero, A. Justel, and M. Svarc.

Principal components for multivariate functional data.

_Computational Statistics & Data Analysis_, 55(9):2619–2634, 2011.

- Betancourt et al. \[2023\]
J. Betancourt, F. Bachoc, T. Klein, and J. Rohmer.

_funGp: Gaussian Process Models for Scalar and Functional_
_Inputs_, 2023.

URL https://CRAN.R-project.org/package=funGp.

R package version 0.3.2.

- Blanquero et al. \[2019\]
R. Blanquero, E. Carrizosa, A. Jiménez-Cordero, and B. Martín-Barragán.

Variable selection in classification for multivariate functional
data.

_Information Sciences_, 481:445–462, May 2019.

- Bosq \[2000\]
D. Bosq.

_Linear processes in function spaces: theory and applications_,
volume 149.

Springer Science & Business Media, 2000.

- Bouveyron and Jacques \[2011\]
C. Bouveyron and J. Jacques.

Model-based clustering of time series in group-specific functional
subspaces.

_Advances in Data Analysis and Classification_, 5(4):281–300, Dec. 2011.

- Brockhaus et al. \[2015\]
S. Brockhaus, F. Scheipl, T. Hothorn, and S. Greven.

The functional linear array model.

_Statistical Modelling_, 15(3):279–300,
2015.

- Brockhaus et al. \[2017\]
S. Brockhaus, M. Melcher, F. Leisch, and S. Greven.

Boosting flexible functional regression models with a high number of
functional historical effects.

_Statistics and Computing_, 27(4):913–926,
2017.

- Brockhaus et al. \[2020\]
S. Brockhaus, D. Rügamer, and S. Greven.

Boosting functional regression models with fdboost.

_Journal of Statistical Software, Articles_, 94(10):1–50, 2020.

- Brunner et al. \[1997\]
E. Brunner, H. Dette, and A. Munk.

Box-type approximations in nonparametric factorial designs.

_Journal of the American Statistical Association_, 92:1494–1502, 1997.

- Calissano et al. \[2022\]
A. Calissano, A. Feragen, and S. Vantini.

Graph-valued regression: Prediction of unlabelled networks in a
non-euclidean graph space.

_Journal of Multivariate Analysis_, 190:104950, 2022.

- Calissano et al. \[2023\]
A. Calissano, A. Feragen, and S. Vantini.

Populations of unlabelled networks: Graph space geometry and
generalized geodesic principal components.

_Biometrika_, page asad024, 2023.

- Cederbaum et al. \[2018\]
J. Cederbaum, F. Scheipl, and S. Greven.

Fast symmetric additive covariance smoothing.

_Computational Statistics & Data Analysis_, 120:25–41, 2018.

- Centofanti et al. \[2020\]
F. Centofanti, M. Fontana, A. Lepore, and S. Vantini.

Smooth Lasso Estimator for the Function-on-Function Linear
Regression Model.

_arXiv:2007.00529 \[stat\]_, July 2020.

arXiv: 2007.00529.

- Chang et al. \[2017\]
C. Chang, X. Lin, and R. Ogden.

Simultaneous confidence bands for functional regression models.

_Journal of Statistical Planning and Inference_, 188:67–81, 2017.

- Chen and Srivastava \[2021\]
C. Chen and A. Srivastava.

Srvfregnet: Elastic function registration using deep neural networks.

In _Proceedings of the IEEE/CVF Conference on Computer Vision_
_and Pattern Recognition_, pages 4462–4471, 2021.

- Chen et al. \[2013\]
H. Chen, Y. Wang, M. C. Paik, and H. A. Choi.

A marginal approach to reduced-rank penalized spline smoothing with
application to multi-level functional data.

_Journal of the American Statistical Association_, 108:1216–1229, 2013.

- Chen et al. \[2014\]
H. Chen, P. T. Reiss, and T. Tarpey.

Optimally weighted L2 distance for functional data.

_Biometrics_, 70(3):516–525, 2014.

- Chen and Müller \[2012\]
K. Chen and H.-G. Müller.

Modeling repeated functional observations.

_Journal of the American Statistical Association_, 107(500):1599–1609, 2012.

- Chen et al. \[2016\]
Y. Chen, J. Goldsmith, and R. T. Ogden.

Variable selection in function-on-scalar regression.

_Stat_, 5(1):88–101, 2016.

- Cheng et al. \[2020\]
Y. Cheng, J. Q. Shi, and J. Eyre.

Nonlinear mixed-effects scalar-on-function models and variable
selection.

_Statistics and Computing_, 30(1):129–140,
Feb. 2020.

- Chiou et al. \[2014\]
J.-M. Chiou, Y.-T. Chen, and Y.-F. Yang.

Multivariate functional principal component analysis: A normalization
approach.

_Statistica Sinica_, pages 1571–1596, 2014.

- Chiou et al. \[2016\]
J.-M. Chiou, Y.-F. Yang, and Y.-T. Chen.

Multivariate functional linear regression and prediction.

_Journal of Multivariate Analysis_, 146:301–312,
2016.

- Choi and Reimherr \[2018\]
H. Choi and M. Reimherr.

A geometric approach to confidence regions and bands for functional
parameters.

_Journal of the Royal Statistical Society B_, 80:239–260, 2018.

- Cuesta-Albertos and Febrero-Bande \[2010\]
J. A. Cuesta-Albertos and M. Febrero-Bande.

A simple multiway anova for functional data.

_Test_, 19:537–557, 2010.

- Cuevas et al. \[2004\]
A. Cuevas, F. M, and F. R.

An anova test for functional data.

_Computational Statistics & Data Analysis_, 47:111–122, 2004.

- Dai and Genton \[2018\]
W. Dai and M. G. Genton.

Multivariate functional data visualization and outlier detection.

_Journal of Computational and Graphical Statistics_, 27(4):923–934, 2018.

- Dauxois et al. \[1982\]
J. Dauxois, A. Pousse, and Y. Romain.

Asymptotic theory for the principal component analysis of a vector
random function: some applications to statistical inference.

_Journal of multivariate analysis_, 12(1):136–154, 1982.

- Degras \[2011\]
D. Degras.

Simultaneous confidence bands for nonparametric regression with
functional data.

_Statistica Sinica_, 21:1735–1765, 2011.

- Delicado et al. \[2010\]
P. Delicado, R. Giraldo, C. Comas, and J. Mateu.

Statistics for spatial functional data: some recent contributions.

_Environmetrics: The official journal of the International_
_Environmetrics Society_, 21(3-4):224–239, 2010.

- Deng et al. \[2009\]
J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei.

ImageNet: A Large-Scale Hierarchical Image Database.

In _CVPR09_, 2009.

- Di et al. \[2009\]
C.-Z. Di, C. M. Crainiceanu, B. S. Caffo, and N. M. Punjabi.

Multilevel functional principal component analysis.

_The annals of applied statistics_, 3(1):458, 2009.

- Ding et al. \[2022\]
F. Ding, S. He, D. E. Jones, and J. Z. Huang.

Functional PCA With Covariate-Dependent Mean and
Covariance Structure.

_Technometrics_, 64(3):335–345, July 2022.

- Dryden and Mardia \[2016\]
I. L. Dryden and K. V. Mardia.

_Statistical shape analysis: with applications in R_, volume
995.

John Wiley & Sons, 2016.

- Duncan et al. \[2018\]
A. Duncan, E. Klassen, and A. Srivastava.

Statistical shape analysis of simplified neuronal trees.

_The Annals of Applied Statistics_, 12(3):1385–1421, 2018.

- Eilers and Marx \[2021\]
P. H. Eilers and B. D. Marx.

_Practical smoothing: The joys of P-splines_.

Cambridge University Press, 2021.

- Ezugwu et al. \[2021\]
A. E. Ezugwu, A. K. Shukla, M. B. Agbaje, O. N. Oyelade, A. José-García, and
J. O. Agushaka.

Automatic clustering algorithms: a systematic review and bibliometric
analysis of relevant literature.

_Neural Computing and Applications_, 33(11):6247–6306, June 2021.

- Fan et al. \[2015\]
Y. Fan, G. M. James, and P. Radchenko.

Functional additive regression.

_The Annals of Statistics_, 43:2296–2325, 2015.

- Fan and Reimherr \[2017\]
Z. Fan and M. Reimherr.

High-dimensional adaptive function-on-scalar regression.

_Econometrics and Statistics_, 1:167–183, Jan. 2017.

- Feng et al. \[2022\]
S. Feng, M. Zhang, and T. Tong.

Variable selection for functional linear models with strong heredity
constraint.

_Annals of the Institute of Statistical Mathematics_,
74(2):321–339, Apr. 2022.

- Feragen et al. \[2013\]
A. Feragen, M. Owen, J. Petersen, M. M. Wille, L. H. Thomsen, A. Dirksen, and
M. de Bruijne.

Tree-space statistics and approximations for large-scale analysis of
anatomical trees.

In _Information Processing in Medical Imaging: 23rd_
_International Conference, IPMI 2013, Asilomar, CA, USA, June 28–July 3,_
_2013\. Proceedings 23_, pages 74–85. Springer, 2013.

- Ferraty and Vieu \[2006\]
F. Ferraty and P. Vieu.

_Nonparametric Functional Data Analysis_.

Springer Series in Statistics. Springer, New York, 2006.

ISBN 978-0387-30369-7.

- Ferraty et al. \[2010\]
F. Ferraty, P. Hall, and P. Vieu.

Most-predictive design points for functional data predictors.

_Biometrika_, 97(4):807–824, Dec. 2010.

- Filzmoser et al. \[2018\]
P. Filzmoser, K. Hron, and M. Templ.

_Applied Compositional Data Analysis- With Worked Examples in_
_R._Springer International Publishing, Cham, 2018.

ISBN 978-3-319-96420-1.

doi: 10.1007/978-3-319-96422-5.

- Fremdt et al. \[2013\]
S. Fremdt, J. Steinebach, L. Horváth, and P. Kokoszka.

Testing the equality of covariance operators in functional samples.

_Scandinavian Journal of Statistics_, 40:138–152,
2013.

- Fu et al. \[2021\]
G. Fu, X. Dai, and Y. Liang.

Functional random forests for curve response.

_Scientific reports_, 11(1):1–14, 2021.

- Fukuchi et al. \[2017\]
R. K. Fukuchi, C. A. Fukuchi, and M. Duarte.

A public dataset of running biomechanics and the effects of running
speed on lower extremity kinematics and kinetics.

_PeerJ_, 5:e3298, 2017.

- García-Portugués et al. \[2014\]
E. García-Portugués, W. González-Manteiga, and M. Febrero-Bande.

A Goodness-of-Fit Test for the Functional Linear Model
with Scalar Response.

_Journal of Computational and Graphical Statistics_, 23(3):761–778, July 2014.

ISSN 1061-8600.

doi: 10.1080/10618600.2013.812519.

URL https://doi.org/10.1080/10618600.2013.812519.

Publisher: Taylor & Francis \_eprint:
https://doi.org/10.1080/10618600.2013.812519.

- Gasser et al. \[1985\]
T. Gasser, H.-G. Müller, and V. Mammitzsch.

Kernels for nonparametric curve estimation.

_Journal of the Royal Statistical Society B_, 47(2):238–252, 1985.

- Gertheiss et al. \[2013\]
J. Gertheiss, A. Maity, and A.-M. Staicu.

Variable selection in generalized functional linear models.

_Stat_, 2(1):86–101, 2013.

- Gertheiss et al. \[2015\]
J. Gertheiss, V. Maier, E. F. Hessel, and A.-M. Staicu.

Marginal functional regression models for analyzing the feeding
behavior of pigs.

_Journal of Agricultural, Biological and Environmental_
_Statistics_, 20:353–370, 2015.

- Gertheiss et al. \[2017\]
J. Gertheiss, J. Goldsmith, and A.-M. Staicu.

A note on modeling sparse exponential-family functional response
curves.

_Computational Statistics & Data Analysis_, 105:46–52, 2017.

- Ghiglietti et al. \[2017\]
A. Ghiglietti, F. Ieva, and A. Paganoni.

Statistical inference for stochastic processes: Two-sample hypothesis
tests.

_Journal of Statistical Planning and Inference_, 180:49–68, 2017.

- Goldsmith et al. \[2011\]
J. Goldsmith, J. Bobb, C. M. Crainiceanu, B. Caffo, and D. Reich.

Penalized functional regression.

_Journal of computational and graphical statistics_, 20(4):830–851, 2011.

- Goldsmith et al. \[2013\]
J. Goldsmith, S. Greven, and C. Crainiceanu.

Corrected confidence bands for functional data using principal
components.

_Biometrics_, 69(1):41–51, 2013.

- Goldsmith et al. \[2014\]
J. Goldsmith, L. Huang, and C. M. Crainiceanu.

Smooth Scalar-on-Image Regression via Spatial Bayesian
Variable Selection.

_Journal of Computational and Graphical Statistics_, 23(1):46–64, Jan. 2014.

Publisher: Taylor & Francis.

- Goldsmith et al. \[2015\]
J. Goldsmith, V. Zipunnikov, and J. Schrack.

Generalized multilevel function-on-scalar regression and principal
component analysis.

_Biometrics_, 71(2):344–353, 2015.

- Goldsmith et al. \[2020\]
J. Goldsmith, F. Scheipl, L. Huang, J. Wrobel, C. Di, J. Gellar, J. Harezlak,
M. W. McLean, B. Swihart, L. Xiao, C. Crainiceanu, and P. T. Reiss.

_refund: Regression with Functional Data_, 2020.

R package version 0.1-23.

- Górecki et al. \[2018\]
T. Górecki, M. Krzyśko, Ł. Waszak, and W. Wołyński.

Selected statistical methods of data analysis for multivariate
functional data.

_Statistical Papers_, 59:153–182, 2018.

- Greven and Scheipl \[2017\]
S. Greven and F. Scheipl.

A general framework for functional regression modelling.

_Statistical Modelling_, 17(1-2):1–35,
2017.

- Greven et al. \[2010\]
S. Greven, C. Crainiceanu, B. Caffo, and D. Reich.

Longitudinal functional principal component analysis.

_Electronic journal of statistics_, 4:1022–1054,
2010.

- Guss \[2016\]
W. H. Guss.

Deep function machines: Generalized neural networks for topological
layer expression.

_arXiv preprint arXiv:1612.04799_, 2016.

- Górecki and Smaga \[2015\]
T. Górecki and L. Smaga.

A comparison of tests for the one-way anova problem for functional
data.

_Computational Statistics_, 30:987–1010, 2015.

- Górecki and Smaga \[2017\]
T. Górecki and L. Smaga.

Multivariate analysis of variance for functional data.

_Journal of Applied Statistics_, 44:2172–2189, 2017.

- Górecki and Smaga \[2019\]
T. Górecki and L. Smaga.

fdANOVA: an R software package for analysis of variance for
univariate and multivariate functional data.

_Computational Statistics_, 34(2):571–597,
2019.

- Hadjipantelis et al. \[2014\]
P. Z. Hadjipantelis, J. A. Aston, H.-G. Müller, and J. Moriarty.

Analysis of spike train data: A multivariate mixed effects model for
phase and amplitude.

_Electronic Journal of Statistics_, 8(2):1797–1807, 2014.

- Hall and Yao \[2008\]
H. Hall, P. Müller and F. Yao.

Modelling sparse generalized longitudinal observations with latent
gaussian processes.

_J. R. Stat. Soc. B: Stat. Methodol._, 70:703–723,
2008.

- Happ and Greven \[2018\]
C. Happ and S. Greven.

Multivariate functional principal component analysis for data
observed on different (dimensional) domains.

_Journal of the American Statistical Association_, 113(522):649–659, 2018.

- Happ et al. \[2019\]
C. Happ, F. Scheipl, A.-A. Gabriel, and S. Greven.

A general framework for multivariate functional principal component
analysis of amplitude and phase variation.

_Stat_, 8(1):e220, 2019.

- Happ-Kurz \[2022\]
C. Happ-Kurz.

_MFPCA: Multivariate Functional Principal Component Analysis for_
_Data Observed on Different Dimensional Domains_, 2022.

URL https://github.com/ClaraHapp/MFPCA.

R package version 1.3-10.

- Hartigan and Wong \[1979\]
J. A. Hartigan and M. A. Wong.

Algorithm AS 136: A K-Means Clustering Algorithm.

_Journal of the Royal Statistical Society. Series C (Applied_
_Statistics)_, 28(1):100–108, 1979.

Publisher: \[Wiley, Royal Statistical Society\].

- Heard et al. \[2006\]
N. A. Heard, C. C. Holmes, and D. A. Stephens.

A Quantitative Study of Gene Regulation Involved in the
Immune Response of Anopheline Mosquitoes.

_Journal of the American Statistical Association_, 101(473):18–29, Mar. 2006.

Publisher: Taylor & Francis.

- Hörmann and Jammoul \[2022\]
S. Hörmann and F. Jammoul.

Preprocessing noisy functional data: A multivariate perspective.

_Electronic Journal of Statistics_, 16(2):6232 – 6266, 2022.

- Hornik et al. \[1989\]
K. Hornik, M. Stinchcombe, and H. White.

Multilayer feedforward networks are universal approximators.

_Neural networks_, 2(5):359–366, 1989.

- Horváth and Kokoszka \[2012\]
L. Horváth and P. Kokoszka.

_Inference for Functional Data with Applications_.

Springer, New York, NY, 2012.

- Horváth et al. \[2013\]
L. Horváth, P. Kokoszka, and R. Reeder.

Estimation of the mean of functional time series and a two-sample
problem.

_Journal of the Royal Statistical Society B_, 75:103–122, 2013.

- Hsieh et al. \[2021\]
T.-Y. Hsieh, Y. Sun, S. Wang, and V. G. Honavar.

Functional autoencoders for functional data representation learning.

In _Proceedings of the SIAM Conference on Data Mining_, 2021.

- Huckemann et al. \[2009\]
S. Huckemann, T. Hotz, and A. Munk.

Intrinsic manova for riemannian manifolds with an application to
kendall’s space of planar shapes.

_IEEE Transactions on Pattern Analysis and Machine_
_Intelligence_, 32(4):593–603, 2009.

- Hyndman and Shang \[2009\]
R. J. Hyndman and H. L. Shang.

Forecasting functional time series.

_Journal of the Korean Statistical Society_, 38:199–211, 2009.

- Hyndman and Shang \[2010\]
R. J. Hyndman and H. L. Shang.

Rainbow plots, bagplots, and boxplots for functional data.

_Journal of Computational and Graphical Statistics_, 19(1):29–45, 2010.

- Ieva et al. \[2013\]
F. Ieva, A. M. Paganoni, D. Pigoli, and V. Vitelli.

Multivariate functional clustering for the morphological analysis of
electrocardiograph curves.

_Journal of the Royal Statistical Society: Series C (Applied_
_Statistics)_, 62(3):401–418, 2013.

- Jacques and Preda \[2013\]
J. Jacques and C. Preda.

Funclust: A curves clustering method using functional random
variables density approximation.

_Neurocomputing_, 112:164–171, July 2013.

- Jacques and Preda \[2014a\]
J. Jacques and C. Preda.

Functional data clustering: a survey.

_Advances in Data Analysis and Classification_, 8(3):231–255, 2014a.

- Jacques and Preda \[2014b\]
J. Jacques and C. Preda.

Model-based clustering for multivariate functional data.

_Computational Statistics & Data Analysis_, 71:92–106, Mar. 2014b.

- James and Sugar \[2003\]
G. M. James and C. A. Sugar.

Clustering for Sparsely Sampled Functional Data.

_Journal of the American Statistical Association_, 98(462):397–408, June 2003.

Publisher: Taylor & Francis.

- James et al. \[2009\]
G. M. James, J. Wang, and J. Zhu.

Functional linear regression that’s interpretable.

_The Annals of Statistics_, 37(5A):2083–2108, Oct. 2009.

- Jeon et al. \[2021\]
J. Jeon, B. U. Park, and I. Van Keilegom.

Additive regression for non-euclidean responses and predictors.

_The Annals of Statistics_, 49:2611–2641, 2021.

- Karhunen \[1947\]
K. Karhunen.

Über lineare Methoden in der Wahrscheinlichkeitsrechnung.

_Annales Academiae Scientiarum Fennicae_, 37:1–79,
1947.

- Kingma and Welling \[2013\]
D. P. Kingma and M. Welling.

Auto-encoding variational Bayes.

_arXiv preprint arXiv:1312.6114_, 2013.

- Köhler et al. \[2017\]
M. Köhler, N. Umlauf, A. Beyerlein, C. Winkler, A.-G. Ziegler, and
S. Greven.

Flexible bayesian additive joint models with an application to type 1
diabetes research.

_Biometrical Journal_, 59(6):1144–1165,
2017.

- Köhler et al. \[2018\]
M. Köhler, N. Umlauf, and S. Greven.

Nonlinear association structures in flexible bayesian additive joint
models.

_Statistics in medicine_, 37(30):4771–4788,
2018.

- Kokoszka \[2012\]
P. Kokoszka.

Dependent functional data.

_International Scholarly Research Notices_, 2012, 2012.

- Koner and Staicu \[2023\]
S. Koner and A.-M. Staicu.

Second-generation functional data.

_Annual Review of Statistics and Its Application_, 10:547–572, 2023.

- Kong et al. \[2016\]
D. Kong, A.-M. Staicu, and A. Maity.

Classical testing in functional linear models.

_Journal of Nonparametric Statistics_, 28:813–838,
2016.

- Konzen et al. \[2021\]
E. Konzen, Y. Cheng, and J. Q. Shi.

Gaussian process for functional data analysis: The gpfda package for
r, 2021.

- Kowal and Bourgeois \[2020\]
D. R. Kowal and D. C. Bourgeois.

Bayesian Function-on-Scalars Regression for
High-Dimensional Data.

_Journal of Computational and Graphical Statistics_, 29(3):629–638, July 2020.

Publisher: Taylor & Francis.

- Kraus and Panaretos \[2012\]
D. Kraus and V. Panaretos.

Dispersion operators and resistant second-order analysis of
functional data.

_Biometrika_, 99:813–832, 2012.

- Krzysko and Smaga \[2021\]
M. Krzysko and L. Smaga.

Two-sample tests for functional data using characteristic functions.

_Austrian Journal of Statistics_, 50:53–64, 2021.

- Li et al. \[2022\]
C. Li, L. Xiao, and S. Luo.

Joint model for survival and multivariate sparse functional data with
application to a study of alzheimer’s disease.

_Biometrics_, 78(2):435–447, 2022.

- Lian \[2013\]
H. Lian.

Shrinkage estimation and selection for multiple functional
regression.

_Statistica Sinica_, 2013.

- Liebl and Reimherr \[2023\]
D. Liebl and M. Reimherr.

Fast and fair simultaneous confidence bands for functional
parameters.

_Journal of the Royal Statistical Society B_, accepted for
publication, 2023.

- Liew et al. \[2016a\]
B. X. Liew, S. Morris, J. W. Keogh, B. Appleby, and K. Netto.

Effects of two neuromuscular training programs on running
biomechanics with load carriage: a study protocol for a randomised controlled
trial.

_BMC Musculoskeletal Disorders_, 17(1):1–10, 2016a.

- Liew et al. \[2016b\]
B. X. Liew, S. Morris, and K. Netto.

The effects of load carriage on joint work at different running
velocities.

_Journal of Biomechanics_, 49(14):3275–3280, 2016b.

- Liew et al. \[2020\]
B. X. Liew, D. Rugamer, A. Stocker, and A. M. De Nunzio.

Classifying neck pain status using scalar and functional
biomechanical variables–development of a method using functional data
boosting.

_Gait & posture_, 76:146–150, 2020.

- Liew et al. \[2021\]
B. X. Liew, D. Rügamer, X. Zhai, Y. Wang, S. Morris, and K. Netto.

Comparing shallow, deep, and transfer learning in predicting joint
moments in running.

_Journal of biomechanics_, 129:110820, 2021.

- Lin et al. \[2023\]
Z. Lin, H.-G. Müller, and B. Park.

Additive models for symmetric positive-definite matrices and lie
groups.

_Biometrika_, 110(2):361–379, 2023.

- Loeve \[1945\]
M. Loeve.

Fonctions aléatoires du second ordre.

_Comptes Rendus Académie des Sciences_, 220:380,
1945.

- López-Pintado and Romo \[2009\]
S. López-Pintado and J. Romo.

On the concept of depth for functional data.

_Journal of the American statistical Association_, 104(486):718–734, 2009.

- Lu et al. \[2017\]
Y. Lu, R. Herbei, and S. Kurtek.

Bayesian registration of functions with a Gaussian process prior.

_Journal of Computational and Graphical Statistics_, 26(4):894–904, 2017.

doi: 10.1080/10618600.2017.1336444.

URL https://doi.org/10.1080/10618600.2017.1336444.

- MacQueen \[1967\]
J. MacQueen.

Some methods for classification and analysis of multivariate
observations.

In L. M. Le Cam and J. Neyman, editors, _Proceedings of the_
_Fifth Berkeley Symposium on Mathematical Statistics and Probability_,
volume 1, pages 281–297, Berkeley/Los Angeles, 1967. University of
California Press.

- Maechler et al. \[2021\]
M. Maechler, P. Rousseeuw, A. Struyf, M. Hubert, and K. Hornik.

_cluster: Cluster Analysis Basics and Extensions_, 2021.

R package version 2.1.1 — For new features, see the ’Changelog’
file (in the package source).

- Maier et al. \[2021\]
E.-M. Maier, A. Stöcker, B. Fitzenberger, and S. Greven.

Additive density-on-scalar regression in Bayes Hilbert spaces with
an application to gender economics.

_arXiv preprint arXiv:2110.11771_, 2021.

- Mardia \[1988\]
K. Mardia.

Directional data analysis: an overview.

_Journal of Applied Statistics_, 15(2):115–122, 1988.

- Mardia \[1975\]
K. V. Mardia.

Statistics of directional data.

_Journal of the Royal Statistical Society Series B: Statistical_
_Methodology_, 37(3):349–371, 1975.

- Marron and Alonso \[2014\]
J. S. Marron and A. M. Alonso.

Overview of object oriented data analysis.

_Biometrical Journal_, 56(5):732–753, 2014.

- Marron et al. \[2015\]
J. S. Marron, J. O. Ramsay, L. M. Sangalli, and A. Srivastava.

Functional data analysis of amplitude and phase variation.

_Statist. Sci._, 30(4):468–484, 11 2015.

doi: 10.1214/15-STS524.

URL https://doi.org/10.1214/15-STS524.

- Martelli et al. \[2014\]
S. Martelli, M. E. Kersh, A. G. Schache, and M. G. Pandy.

Strain energy in the femoral neck during exercise.

_Journal of biomechanics_, 47(8):1784–1791,
2014.

- Marx and Eilers \[1999\]
B. D. Marx and P. H. C. Eilers.

Generalized linear regression on sampled signals and curves: A
p-spline approach.

_Technometrics_, 41(1):1–13, 1999.

- Masarotto et al. \[2019\]
V. Masarotto, V. M. Panaretos, and Y. Zemel.

Procrustes metrics on covariance operators and optimal transportation
of gaussian processes.

_Sankhya A_, 81:172–213, 2019.

- Matsui \[2014\]
H. Matsui.

Variable and boundary selection for functional data via multiclass
logistic regression modeling.

_Computational Statistics & Data Analysis_, 78:176–185, 2014.

- Matsui and Konishi \[2011\]
H. Matsui and S. Konishi.

Variable selection for functional regression models via the l1
regularization.

_Computational Statistics & Data Analysis_, 55(12):3304–3310, Dec. 2011.

- Matuk et al. \[2021\]
J. Matuk, K. Bharath, O. Chkrebtii, and S. Kurtek.

Bayesian framework for simultaneous registration and estimation of
noisy, sparse, and fragmented functional data.

_Journal of the American Statistical Association_, In
Press:1–17, 2021.

- McLean et al. \[2013\]
M. W. McLean, F. Scheipl, G. Hooker, S. Greven, and D. Ruppert.

Bayesian functional generalized additive models with sparsely
observed covariates.

_arXiv preprint arXiv:1305.3585_, 2013.

- McLean et al. \[2015\]
M. W. McLean, G. Hooker, and D. Ruppert.

Restricted likelihood ratio tests for linearity in scalar-on-function
regression.

_Statistics and Computing_, 25(5):997–1008,
Sept. 2015.

ISSN 1573-1375.

doi: 10.1007/s11222-014-9473-1.

URL https://doi.org/10.1007/s11222-014-9473-1.

- Mercer \[1909\]
J. Mercer.

Functions of positive and negative type, and their connection with
the theory of integral equations.

_Philosophical transactions of the royal society of London._
_Series A_, 209(441-458):415–446, 1909.

- Möller et al. \[2016\]
A. Möller, G. Tutz, and J. Gertheiss.

Random forests for functional covariates.

_Journal of Chemometrics_, 30(12):715–725,
2016.

- Montagnani et al. \[2021\]
E. Montagnani, S. C. Morrison, M. Varga, and C. Price.

Pedobarographic statistical parametric mapping of plantar pressure
data in new and confident walking infants: A preliminary analysis.

_Journal of biomechanics_, 129:110757, 2021.

- Morris and Carroll \[2006\]
J. S. Morris and R. J. Carroll.

Wavelet-based functional mixed models.

_Journal of the Royal Statistical Society: Series B (Statistical_
_Methodology)_, 68(2):179–199, 2006.

- Murtagh and Contreras \[2012\]
F. Murtagh and P. Contreras.

Algorithms for hierarchical clustering: an overview.

_WIREs Data Mining and Knowledge Discovery_, 2(1):86–97, 2012.

- Müller and Stadtmüller \[2005\]
H.-G. Müller and U. Stadtmüller.

Generalized functional linear models.

_The Annals of Statistics_, 33:774–805, 2005.

- Müller and Yao \[2008\]
H.-G. Müller and F. Yao.

Functional additive models.

_Journal of the American Statistical Association_, 103:1534–1544, 2008.

- Ojo et al. \[2021\]
O. T. Ojo, R. E. Lillo, and A. Fernandez Anta.

_fdaoutlier: Outlier Detection Tools for Functional Data_
_Analysis_, 2021.

URL https://CRAN.R-project.org/package=fdaoutlier.

R package version 0.2.0.

- Ott et al. \[2021\]
F. Ott, D. Rügamer, L. Heublein, B. Bischl, and C. Mutschler.

Joint Classification and Trajectory Regression of Online Handwriting
using a Multi-Task Learning Approach.

In _Proceedings of the IEEE/CVF Winter Conference on_
_Applications of Computer Vision_, 2021.

- Pan and Yang \[2010\]
S. J. Pan and Q. Yang.

A survey on transfer learning.

_IEEE Transactions on Knowledge and Data Engineering_,
22(10):1345–1359, 2010.

- Panaretos and Tavakoli \[2013\]
V. M. Panaretos and S. Tavakoli.

Cramér–karhunen–loève representation and harmonic principal
component analysis of functional time series.

_Stochastic Processes and their Applications_, 123(7):2779–2807, 2013.

- Panaretos and Zemel \[2016\]
V. M. Panaretos and Y. Zemel.

Amplitude and phase variation of point processes.

_Annals of Statistics_, 44:771–812, 2016.

- Panaretos and Zemel \[2020\]
V. M. Panaretos and Y. Zemel.

_An invitation to statistics in Wasserstein space_.

Springer Nature, 2020.

- Park and Staicu \[2015\]
S. Y. Park and A.-M. Staicu.

Longitudinal functional data analysis.

_Stat_, 4(1):212–226, 2015.

- Parodi and Reimherr \[2018\]
A. Parodi and M. Reimherr.

Simultaneous variable selection and smoothing for high-dimensional
function-on-scalar regression.

_Electronic Journal of Statistics_, 12(2):4602–4639, Jan. 2018.

Publisher: Institute of Mathematical Statistics and Bernoulli
Society.

- Pataky \[2010\]
T. C. Pataky.

Generalized n-dimensional biomechanical field analysis using
statistical parametric mapping.

_Journal of biomechanics_, 43(10):1976–1982, 2010.

- Pataky et al. \[2015\]
T. C. Pataky, J. Vanrenterghem, and M. A. Robinson.

Zero-vs. one-dimensional, parametric vs. non-parametric, and
confidence interval vs. hypothesis testing procedures in one-dimensional
biomechanical trajectory analysis.

_Journal of biomechanics_, 48(7):1277–1285,
2015.

- Pataky et al. \[2016\]
T. C. Pataky, J. Vanrenterghem, and M. A. Robinson.

The probability of false positives in zero-dimensional analyses of
one-dimensional kinematic, force and emg trajectories.

_Journal of Biomechanics_, 49(9):1468–1476,
2016.

- Pawlowsky-Glahn et al. \[2015\]
V. Pawlowsky-Glahn, J. J. Egozcue, and R. Tolosana-Delgado.

_Modeling and Analysis of Compositional Data_.

John Wiley & Sons, New York, NY, 2015.

- Pfisterer et al. \[2019\]
F. Pfisterer, L. Beggel, X. Sun, F. Scheipl, and B. Bischl.

Benchmarking time series classification–functional data vs machine
learning approaches.

_arXiv preprint arXiv:1911.07511_, 2019.

- Pini and Vantini \[2016\]
A. Pini and S. Vantini.

The interval testing procedure: A general framework for inference in
functional data analysis.

_Biometrics_, 72:835–845, 2016.

- Pini and Vantini \[2022\]
A. Pini and S. Vantini.

_fdatest: Interval Testing Procedure for Functional Data_, 2022.

URL https://CRAN.R-project.org/package=fdatest.

R package version 2.1.1.

- Pomann et al. \[2016\]
G.-M. Pomann, A.-M. Staicu, and S. Ghosh.

A two-sample distribution-free test for functional data with
application to a diffusion tensor imaging study of multiple sclerosis.

_Journal of the Royal Statistical Society: Series C (Applied_
_Statistics)_, 65(3):395–414, 2016.

- R Core Team \[2023\]
R Core Team.

_R: A Language and Environment for Statistical Computing_.

R Foundation for Statistical Computing, Vienna, Austria, 2023.

- Rahman et al. \[2019\]
R. Rahman, S. R. Dhruba, S. Ghosh, and R. Pal.

Functional random forest with applications in dose-response
predictions.

_Scientific reports_, 9(1):1–14, 2019.

- Ramsay and Li \[1998\]
J. O. Ramsay and X. Li.

Curve registration.

_Journal of the Royal Statistical Society: Series B (Statistical_
_Methodology)_, 60(2):351–363, 1998.

doi: https://doi.org/10.1111/1467-9868.00129.

URL
https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/1467-9868.00129.

- Ramsay and Silverman \[2005\]
J. O. Ramsay and B. W. Silverman.

_Functional Data Analysis_.

Springer Series in Statistics. Springer, New York, NY, 2005.

ISBN 978-0-387-40080-8 978-0-387-22751-1.

- Ramsay et al. \[2009\]
J. O. Ramsay, G. Hooker, and S. Graves.

_Functional Data Analysis with R and MATLAB_.

Springer, New York, NY, 2009.

- Ramsay et al. \[2022\]
J. O. Ramsay, S. Graves, and G. Hooker.

_fda: Functional Data Analysis_, 2022.

URL https://CRAN.R-project.org/package=fda.

R package version 6.0.5.

- Rao and Reimherr \[2023\]
A. R. Rao and M. Reimherr.

Nonlinear functional modeling using neural networks.

_Journal of Computational and Graphical Statistics_, 0(0):1–10, 2023.

- Reiss et al. \[2017\]
P. T. Reiss, J. Goldsmith, H. L. Shang, and R. T. Ogden.

Methods for Scalar-on-Function Regression.

_International Statistical Review_, 85(2):228–249, 2017.

- Rice and Silverman \[1991\]
J. A. Rice and B. W. Silverman.

Estimating the mean and covariance structure nonparametrically when
the data are curves.

_Journal of the Royal Statistical Society: Series B_
_(Methodological)_, 53(1):233–243, 1991.

- Robinson et al. \[2015\]
M. A. Robinson, J. Vanrenterghem, and T. C. Pataky.

Statistical parametric mapping (spm) for alpha-based statistical
analyses of multi-muscle emg time-series.

_Journal of Electromyography and Kinesiology_, 25(1):14–19, 2015.

- Rossi and Villa \[2006\]
F. Rossi and N. Villa.

Support vector machine for functional data classification.

_Neurocomputing_, 69(7-9):730–742, Mar
2006.

- Rossi et al. \[2002\]
F. Rossi, B. Conan-Guez, and F. Fleuret.

Functional data analysis with multi layer perceptrons.

In _Proceedings of the 2002 International Joint Conference on_
_Neural Networks. IJCNN’02 (Cat. No. 02CH37290)_, volume 3, pages 2843–2848.
IEEE, 2002.

- Rügamer et al. \[2018\]
D. Rügamer, S. Brockhaus, K. Gentsch, K. Scherer, and S. Greven.

Boosting factor-specific functional historical models for the
detection of synchronization in bioelectrical signals.

_Journal of the Royal Statistical Society: Series C (Applied_
_Statistics)_, 67(3):621–642, 2018.

- Rügamer et al. \[2023\]
D. Rügamer, B. Liew, Z. Altai, and A. Stöcker.

Semi-structutred functional regression: A scalable and flexible
extension of function-on-function regression, 2023.

Under Review.

- Sarkar and Panaretos \[2022\]
S. Sarkar and V. M. Panaretos.

Covnet: Covariance networks for functional data on multidimensional
domains.

_Journal of the Royal Statistical Society Series B: Statistical_
_Methodology_, 84(5):1785–1820, 2022.

- Scheipl et al. \[2015\]
F. Scheipl, A.-M. Staicu, and S. Greven.

Functional additive mixed models.

_Journal of Computational and Graphical Statistics_, 24(2):477–501, 2015.

- Scheipl et al. \[2016\]
F. Scheipl, J. Gertheiss, and S. Greven.

Generalized functional additive mixed models.

_Electronic Journal of Statistics_, 10:1455–1492,
2016.

- Schmutz et al. \[2020\]
A. Schmutz, J. Jacques, C. Bouveyron, L. Chèze, and P. Martin.

Clustering multivariate functional data in group-specific functional
subspaces.

_Computational Statistics_, 35(3):1101–1131, Sept. 2020.

- Schmutz et al. \[2021\]
A. Schmutz, J. Jacques, and C. Bouveyron.

_funHDDC: Univariate and Multivariate Model-Based Clustering in_
_Group-Specific Functional Subspaces_, 2021.

R package version 2.3.1.

- Scrucca et al. \[2016\]
L. Scrucca, M. Fop, T. B. Murphy, and A. E. Raftery.

mclust 5: clustering, classification and density estimation using
Gaussian finite mixture models.

_The R Journal_, 8(1):289–317, 2016.

- Selk \[2023\]
L. Selk.

Uniform convergence rates and automatic variable selection in
nonparametric regression with functional and categorical covariates.

_Journal of Nonparametric Statistics_, 2023.

URL https://doi.org/10.1080/10485252.2023.2207673.

(in press).

- Selk and Gertheiss \[2023\]
L. Selk and J. Gertheiss.

Nonparametric regression and classification with functional,
categorical, and mixed covariates.

_Advances in Data Analysis and Classification_, 17:519–543, 2023.

- Shang and Hyndman \[2022\]
H. L. Shang and R. Hyndman.

_rainbow: Bagplots, Boxplots and Rainbow Plots for Functional_
_Data_, 2022.

URL https://CRAN.R-project.org/package=rainbow.

R package version 3.7.

- Shen and Faraway \[2004\]
Q. Shen and J. Faraway.

An F test for linear models with functional responses.

_Statistica Sinica_, 14:1239–1257, 2004.

- Shi and Choi \[2011\]
J. Q. Shi and T. Choi.

_Gaussian process regression analysis for functional data_.

CRC Press, 2011.

- Shi et al. \[2023\]
J. Q. Shi, Y. Cheng, and E. Konzen.

_GPFDA: Gaussian Process for Functional Data Analysis_, 2023.

R package version 4.0.0.

- Shou et al. \[2015\]
H. Shou, V. Zipunnikov, C. M. Crainiceanu, and S. Greven.

Structured functional principal component analysis.

_Biometrics_, 71(1):247–257, 2015.

- Simmons et al. \[2011\]
J. P. Simmons, L. D. Nelson, and U. Simonsohn.

False-positive psychology: undisclosed flexibility in data collection
and analysis allows presenting anything as significant.

_Psychological Science_, 22:1359–1366, 2011.

- Srivastava and Klassen \[2016\]
A. Srivastava and E. P. Klassen.

_Functional and shape data analysis_, volume 1.

Springer, 2016.

- Srivastava et al. \[2010a\]
A. Srivastava, E. Klassen, S. Joshi, and I. Jermyn.

Shape analysis of elastic curves in Euclidean spaces.

_IEEE Transactions on Pattern Analysis and Machine_
_Intelligence_, 33(7):1415–1428, 09 2010a.

doi: 10.1109/TPAMI.2010.184.

- Srivastava et al. \[2010b\]
A. Srivastava, E. Klassen, S. H. Joshi, and I. H. Jermyn.

Shape analysis of elastic curves in euclidean spaces.

_IEEE transactions on pattern analysis and machine_
_intelligence_, 33(7):1415–1428, 2010b.

- Steyer \[2022\]
L. Steyer.

_elasdics: Elastic Analysis of Sparse, Dense and Irregular_
_Curves_, 2022.

URL https://CRAN.R-project.org/package=elasdics.

R package version 1.1.1.

- Steyer et al. \[2023a\]
L. Steyer, A. Stöcker, and S. Greven.

Elastic analysis of irregularly or sparsely sampled curves.

_Biometrics_, 79:2103–2115, 2023a.

- Steyer et al. \[2023b\]
L. Steyer, A. Stöcker, and S. Greven.

Regression in quotient metric spaces with a focus on elastic curves.

_arXiv preprint arXiv:2305.02075_, 2023b.

- Stöcker et al. \[2022a\]
A. Stöcker, M. Pfeuffer, L. Steyer, and S. Greven.

Elastic full procrustes analysis of plane curves via hermitian
covariance smoothing.

_arXiv preprint arXiv:2203.10522_, 2022a.

- Stöcker et al. \[2022b\]
A. Stöcker, L. Steyer, and S. Greven.

Functional additive models on manifolds of planar shapes and forms.

_Journal of Computational and Graphical Statistics_, to appear,
2022b.

URL https://arxiv.org/abs/2109.02624.

- Su et al. \[2017\]
Y.-R. Su, C.-Z. Di, and L. Hsu.

Hypothesis testing in functional linear models.

_Biometrics_, 73(2):551–561, 2017.

ISSN 1541-0420.

doi: 10.1111/biom.12624.

URL https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12624.

\_eprint: https://onlinelibrary.wiley.com/doi/pdf/10.1111/biom.12624.

- Sun and Genton \[2011\]
Y. Sun and M. G. Genton.

Functional boxplots.

_Journal of Computational and Graphical Statistics_, 20(2):316–334, 2011.

- Sutskever et al. \[2014\]
I. Sutskever, O. Vinyals, and Q. V. Le.

Sequence to sequence learning with neural networks.

In _Advances in neural information processing systems_, pages
3104–3112, 2014.

- Swihart et al. \[2014\]
B. J. Swihart, J. Goldsmith, and C. M. Crainiceanu.

Restricted Likelihood Ratio Tests for Functional Effects in
the Functional Linear Model.

_Technometrics_, 56(4):483–493, Oct. 2014.

ISSN 0040-1706.

doi: 10.1080/00401706.2013.863163.

URL https://doi.org/10.1080/00401706.2013.863163.

Publisher: Taylor & Francis \_eprint:
https://doi.org/10.1080/00401706.2013.863163.

- Szucs \[2016\]
D. Szucs.

A tutorial on hunting statistical significance by chasing n.

_Frontiers in Psychology_, 7:1444, 2016.

- Sørensen et al. \[2013\]
H. Sørensen, J. Goldsmith, and L. M. Sangalli.

An introduction with medical applications to functional data
analysis.

_Statistics in Medicine_, 32(30):5222–5240,
2013.

- Tarpey and Kinateder \[2003\]
T. Tarpey and K. K. Kinateder.

Clustering functional data.

_Journal of Classification_, 20(1):93–114,
2003.

- Tekbudak et al. \[2019\]
M. Y. Tekbudak, M. Alfaro-Córdoba, A. Maity, and A.-M. Staicu.

A comparison of testing methods in scalar-on-function regression.

_AStA Advances in Statistical Analysis_, 103(3):411–436, Sept. 2019.

ISSN 1863-818X.

doi: 10.1007/s10182-018-00337-x.

URL https://doi.org/10.1007/s10182-018-00337-x.

- Thind et al. \[2020\]
B. Thind, K. Multani, and J. Cao.

Deep learning with functional inputs.

_arXiv preprint arXiv:2006.09590_, 2020.

- Thomas Fletcher \[2013\]
P. Thomas Fletcher.

Geodesic regression and the theory of least squares on riemannian
manifolds.

_International journal of computer vision_, 105:171–185, 2013.

- Tucker \[2023\]
J. D. Tucker.

_fdasrvf: Elastic Functional Data Analysis_, 2023.

URL https://CRAN.R-project.org/package=fdasrvf.

R package version 2.0.1.

- Tutz and Gertheiss \[2010\]
G. Tutz and J. Gertheiss.

Feature Extraction in Signal Regression: A Boosting
Technique for Functional Data Regression.

_Journal of Computational and Graphical Statistics_, 19(1):154–174, Jan. 2010.

- van den Boogaart and Tolosana-Delgado \[2013\]
K. G. van den Boogaart and R. Tolosana-Delgado.

_Analyzing compositional data with R_.

Springer, 2013.

- van den Boogaart et al. \[2010\]
K. G. van den Boogaart, J. J. Egozcue, and V. Pawlowsky-Glahn.

Bayes linear spaces.

_SORT: statistics and operations research transactions_,
34(4):201–222, 2010.

- van den Boogaart et al. \[2014\]
K. G. van den Boogaart, J. J. Egozcue, and V. Pawlowsky-Glahn.

Bayes hilbert spaces.

_Australian & New Zealand Journal of Statistics_, 56(2):171–194, 2014.

doi: 10.1111/anzs.12074.

URL https://onlinelibrary.wiley.com/doi/abs/10.1111/anzs.12074.

- Vogel et al. \[2022\]
F. Vogel, N. M. Vahle, J. Gertheiss, and M. J. Tomasik.

Supervised learning for analysing movement patterns in a virtual
reality experiment.

_Royal Society Open Science_, 9:211594, 2022.

- Volkmann et al. \[2023a\]
A. Volkmann, A. Stöcker, F. Scheipl, and S. Greven.

Multivariate functional additive mixed models.

_Statistical Modelling_, 23(4):303–326,
2023a.

- Volkmann et al. \[2023b\]
A. Volkmann, N. Umlauf, and S. Greven.

Flexible joint models for multivariate longitudinal and time-to-event
data using multivariate functional principal components.

_arXiv preprint arXiv:2311.06409_, 2023b.

- Wang et al. \[2019\]
Q. Wang, S. Zheng, A. Farahat, S. Serita, T. Saeki, and C. Gupta.

Multilayer perceptron for sparse functional data.

In _2019 International Joint Conference on Neural Networks_
_(IJCNN)_, pages 1–10. IEEE, 2019.

- Wang et al. \[2023\]
S. Wang, Y. Huang, and G. Cao.

Review on functional data classification.

_WIREs Computational Statistics_, e1638, 2023.

- Warmenhoven et al. \[2018\]
J. Warmenhoven, A. Harrison, M. A. Robinson, J. Vanrenterghem, N. Bargary,
R. Smith, S. Cobley, C. Draper, C. Donnelly, and T. Pataky.

A force profile analysis comparison between functional data analysis,
statistical parametric mapping and statistical non-parametric mapping in
on-water single sculling.

_Journal of Science and Medicine in Sport_, 21(10):1100–1105, 2018.

- Wood \[2011\]
S. N. Wood.

Fast stable restricted maximum likelihood and marginal likelihood
estimation of semiparametric generalized linear models.

_Journal of the Royal Statistical Society Series B_,
73:3–36, 2011.

- Wood et al. \[2016\]
S. N. Wood, N. Pya, and B. Säfken.

Smoothing parameter and model selection for general smooth models.

_Journal of the American Statistical Association_, 111:1548–1575, 2016.

- Wood \[2017\]
S. S. Wood.

_Generalized Additive Models: An Introduction with R_.

CRC Press, Boca Raton, 2nd edition, 2017.

- Wynne and Duncan \[2022\]
G. Wynne and A. B. Duncan.

A Kernel Two-Sample Test for Functional Data.

_Journal of Machine Learning Research_, 23:1–51,
2022.

- Xiao et al. \[2013\]
L. Xiao, Y. Li, and D. Ruppert.

Fast bivariate p-splines: the sandwich smoother.

_Journal of the Royal Statistical Society Series B: Statistical_
_Methodology_, 75(3):577–599, 2013.

- Yao et al. \[2005\]
F. Yao, H.-G. Müller, and J.-L. Wang.

Functional data analysis for sparse longitudinal data.

_Journal of the American statistical association_, 100(470):577–590, 2005.

- Yi et al. \[2022\]
M. Yi, Z. Li, and Y. Tang.

F-type testing in functional linear models.

_Stat_, 11(1):e420, 2022.

ISSN 2049-1573.

doi: 10.1002/sta4.420.

URL https://onlinelibrary.wiley.com/doi/abs/10.1002/sta4.420.

\_eprint: https://onlinelibrary.wiley.com/doi/pdf/10.1002/sta4.420.

- Zhang \[2011\]
J. T. Zhang.

Statistical inferences for linear models with functional responses.

_Statistica Sinica_, 21:1431–1451, 2011.

- Zhang and Chen \[2007\]
J.-T. Zhang and J. Chen.

Statistical inferences for functional data.

_The Annals of Statistics_, 35(3):1052–1079, July 2007.

ISSN 0090-5364, 2168-8966.

doi: 10.1214/009053606000001505.

URL
https://projecteuclid.org/journals/annals-of-statistics/volume-35/issue-3/Statistical-inferences-for-functional-data/10.1214/009053606000001505.full.

Publisher: Institute of Mathematical Statistics.

- Zhang and Liang \[2014\]
J. T. Zhang and X. Liang.

One-way ANOVA for functional data via globalizing the pointwise
F-test.

_Scandinavian Journal of Statistics_, 41:51–71, 2014.

- Zhang et al. \[2010\]
J.-T. Zhang, X. Liang, and S. Xiao.

On the two-sample behrens-fisher problem for functional data.

_Journal of Statistical Theory and Practice_, 4:571–587, 2010.

- Zhang et al. \[2019\]
J. T. Zhang, M. Y. Cheng, H. T. Wu, and B. Zhou.

A new test for functional one-way anova with applications to ischemic
heart screening.

_Computational Statistics & Data Analysis_, 132:3–17, 2019.

- Zhou et al. \[2013\]
J. Zhou, N.-Y. Wang, and N. Wang.

Functional Linear Model with Zero-value Coefficient
Function at Sub-regions.

_Statistica Sinica_, 23(1):25–50, Jan.
2013.

- Zhou et al. \[2022\]
Y. Zhou, S. Bhattacharjee, C. Carroll, Y. Chen, X. Dai, J. Fan, A. Gajardo,
P. Z. Hadjipantelis, K. Han, H. Ji, C. Zhu, H.-G. Müller, and J.-L. Wang.

_fdapace: Functional Data Analysis and Empirical Dynamics_,
2022.

URL https://CRAN.R-project.org/package=fdapace.

R package version 0.5.9.