Source: https://doi.org/10.3390/analytics2040042
Title: An Exploration of Clustering Algorithms for Customer Segmentation in the UK Retail Market
Fetched: 2026-11-26T15:58:40.461Z

[Skip to Content](https://www.mdpi.com/2813-2203/2/4/42#main)

[![](https://mdpi-res.com/cdn-cgi/image/width=32%2Cheight=32%2Conerror=redirect/https://mdpi-res.com/img/journals/analytics-logo-sq.png?67937756f41d691c)AnalyticsAnalytics](https://www.mdpi.com/journal/analytics)

CiteCite

ShareShare

Get Alerted Get Alerted

[Download PDF  PDF](https://www.mdpi.com/2813-2203/2/4/42/pdf)

- Editor’s Choice

- Article

- ![Open Access](https://mdpi-res.com/data/open-access.svg)


12 October 2023

15 Pages

# An Exploration of Clustering Algorithms for Customer Segmentation in the UK Retail Market

Jeen Mary John 1,

Olamilekan Shobayo 1,\* and

Bayode Ogunleye 2

1

Department of Computing, Sheffield Hallam University, Sheffield S1 2NU, UK

2

Department of Computing & Mathematics, University of Brighton, Brighton BN2 4GJ, UK

\*

Author to whom correspondence should be addressed.

[Analytics](https://www.mdpi.com/journal/analytics) **2023**, _2_(4), 809-823; [https://doi.org/10.3390/analytics2040042](https://doi.org/10.3390/analytics2040042)

More formats

[Version Notes](https://www.mdpi.com/2813-2203/2/4/42/notes)

[Order Reprints](https://www.mdpi.com/2813-2203/2/4/42/reprints)

## Abstract

Recently, peoples’ awareness of online purchases has significantly risen. This has given rise to online retail platforms and the need for a better understanding of customer purchasing behaviour. Retail companies are pressed with the need to deal with a high volume of customer purchases, which requires sophisticated approaches to perform more accurate and efficient customer segmentation. Customer segmentation is a marketing analytical tool that aids customer-centric service and thus enhances profitability. In this paper, we aim to develop a customer segmentation model to improve decision-making processes in the retail market industry. To achieve this, we employed a UK-based online retail dataset obtained from the UCI machine learning repository. The retail dataset consists of 541,909 customer records and eight features. Our study adopted the RFM (recency, frequency, and monetary) framework to quantify customer values. Thereafter, we compared several state-of-the-art (SOTA) clustering algorithms, namely, K-means clustering, the Gaussian mixture model (GMM), density-based spatial clustering of applications with noise (DBSCAN), agglomerative clustering, and balanced iterative reducing and clustering using hierarchies (BIRCH). The results showed the GMM outperformed other approaches, with a Silhouette Score of 0.80.

Keywords:

[customer segmentation](https://www.mdpi.com/search?q=customer+segmentation); [DBSCAN](https://www.mdpi.com/search?q=DBSCAN); [Gaussian mixture model](https://www.mdpi.com/search?q=Gaussian+mixture+model); [K-means clustering](https://www.mdpi.com/search?q=K-means+clustering); [BIRCH](https://www.mdpi.com/search?q=BIRCH); [RFM framework](https://www.mdpi.com/search?q=RFM+framework)

## 1\. Introduction

The UK’s retail market has been known to create a sizable amount of employment and sales. In the era of Big Data, decision making based on data is becoming increasingly important for organisations, especially the retail industry. Big Data Analytics (BDA) is used to analyse massive datasets and identify patterns in data, which can be used to make informed decisions \[1\]. Segmentation is a well-established marketing strategy that involves dividing customers into distinct groups, known as market segments, and focusing marketing efforts towards the most favourable segment \[2\]. Gaining insight into consumer behaviour and the decision-making process is crucial in formulating efficient strategies to deliver a customer-centric service and enhance profitability. Business Intelligence (BI) and Big Data Analytics (BDA) are employed in the customer segmentation framework to discern the prospective customer profile and market both new and established products. However, there is a lack of contextual framework behind practice development, specifically regarding the influence on decision marketing strategic issues.

Online customer data could be used to generate personas that represent distinct groups of individuals \[3,4\]. Business Intelligence (BI) and Big Data Analytics (BDA) could also be leveraged for the creation of a framework aimed at discerning the prospective customer profile for the purpose of marketing both new and established products \[4\].

This study aims to develop a customer segmentation model to improve decision-making processes in the retail market industry. To this end, we conduct an experimental comparison of various unsupervised machine-learning-based clustering algorithms for retail customer segmentation. Hicham and Karim \[5\] and Turkmen \[6\] compared some clustering approaches for customer segmentation. Their studies achieved Silhouette Scores of 0.72 and 0.6, respectively. These studies are similar to ours, but differ in terms of methodology and results. Thus, our contributions can be summarised as follows. We performed a comprehensive analysis of several algorithms for retail customer segmentation and discuss them from both a scientific and business perspective. We demonstrated the use of principal component analysis (PCA) and the Gaussian mixture model (GMM) and achieved a more accurate model and interpretable results. Subsequent sections present the background knowledge to this study ( [Section 2](https://www.mdpi.com/2813-2203/2/4/42#sec2-analytics-02-00042)), the methodology ( [Section 3](https://www.mdpi.com/2813-2203/2/4/42#sec3-analytics-02-00042)), and the results ( [Section 4](https://www.mdpi.com/2813-2203/2/4/42#sec4-analytics-02-00042)), and [Section 5](https://www.mdpi.com/2813-2203/2/4/42#sec5-analytics-02-00042) will provide conclusions and recommendations.

## 2\. Related Work

Retailers in the UK must compete on pricing to stay afloat during the present economic crisis. To assist the economy, client loyalty research is essential. According to a study conducted in the UK, consumers are more devoted to specific retailers and brands when purchasing is convenient. The cost of the goods is not as significant as service operations and customer pleasure. To successfully control consumer purchasing behaviour and boost retail sales, retail companies must strengthen service operations skills \[7\]. By allowing personalised shopping experiences, predicting patterns, and taking wise choices based on market information, BD has transformed the retail industry \[8\].

During the era of Big Data (BD), decision making driven by data is common, irrespective of the scale of the business or the industry, who will be able to tackle complex business problems by taking actions based on data-driven insights \[9\]. According to Oussous et al. \[10\], BD, in contrast to traditional data, refers to vast, expanding data collections that encompass many different diverse forms, including un-structured, semi-structured, and structured data.

A case study was conducted by Jin and Kim on a typical courier company’s sorting and logistics processing \[11\]. According to the study, BD can enhance business efficiency by transforming raw data into valuable information. Identifying the type and scope of data is crucial for achieving sustainable growth and competitiveness. Integrated use of BI, BD, and BDA in management decision support systems may aid businesses in achieving time- and cost-effectiveness. This case study provides useful insights for future company plans to reduce trial-and-error iterations. The authors of \[12\] developed a generic framework for organisational excellence by integrating Baldrige and BI frameworks. They formed respective matrices and adapted the Baldrige and BI frameworks, incorporating knowledge management and BI frameworks with specific key performance indicator (KPI) parameters. The framework integrates KPIs from the Baldrige framework, customer management, workforce engagement, knowledge management, operations focus, strategic planning, and academic accreditation. The dashboard is designed as an infographic mechanism, incorporating business, content, analytics, and continuous intelligence.

A K-means clustering (KC)-based consumer segmentation model was proposed in \[13\] and implemented using RStudio. The CSV-formatted dataset was analysed using various R functions. Visualisations were developed to understand client demographics. To identify the clusters, the elbow technique, average silhouette method, and gap statistics were used.

To examine the use of BDA in supply chain demand forecasting, the authors of \[14\] employed neural networks (NNs) and a regression analysis approach. The research findings are based on closed-loop supply chains (CLSCs) and provide suggestions for future research.

Customer segmentation is crucial in marketing as it helps organisations understand and meet their consumers’ demands by breaking down an intended market into groups based on shared traits. Machine-learning-based customer segmentation models, such as k-means clustering, density-based spatial clustering of applications with noise (DBSCAN), and balanced iterative reducing and clustering using hierarchies (BIRCH), have presented potential insights in analysing customer data for effective decision making in the marketing sector. Ushakovato and Mikhaylov \[15\] developed a Gaussian-based framework for analysing smart meter data for predicting tasks. The experimental study analysed and compared different clustering techniques for predicting time series data and cluster assignments without additional customer information. Fontanini and Abreu \[16\] used the BIRCH algorithm to determine common load forms in neighbourhoods. The global clustering measure was developed by solving issues generated during optimisation of load forms. Lorbeer et al. \[17\] found that BIRCH requires the maximum number of clusters for a better clustering quality performance. This technique extracts load forms from large databases, clusters high, moderate, and minimal load types using cost functions, and determines the right number of clusters for global grouping. It is suitable for urban-scale loading assessments and real-time online education. Hicham and Karim \[5\] proposed a clustering ensemble method which consists of DBSCAN, k-means, MiniBatch k-means, and the mean shift algorithm for customer segmentation. They applied their clustering ensemble method to 35,000 records and achieved a Silhouette Score of 0.72. The authors of \[18\] developed a customer segmentation model (RFM+B) using indicators of RFM and balance (B) to enhance marketing decisions. This model classifies client savings using transactional patterns and current balances using the RFM and B qualities. The model achieved an accuracy of 77.85% using the K-means clustering technique. Hossain \[19\] segmented customer data based on spending patterns through k-means clustering and the DBSCAN algorithm, determining clients with out-of-the-ordinary spending patterns. This study suggested incorporating neural-network-based clustering techniques for customer segmentation on large datasets. Punhani et al. \[20\] applied k-means clustering to 25,000 online customer records obtained from Kaggle repository. They used the Davies–Bouldin Index (BDI) to evaluate their optimal number of K and thus segmented the customer records into four segments. Turkmen \[6\] compared DBSCAN, k-means clustering, agglomerative clustering, and the RFM framework with 541,909 retail customer datasets. They employed random forest for selection of variables fitted into the algorithms. They showed k-means clustering achieved the best result with a Silhouette Score of 0.6. In summary, our literature review findings suggest there is limited comparative studies of sophisticated unsupervised learning approaches for customer segmentation in the retail marketing context. Thus, subsequent sections will present our methodology and the results.

## 3\. Methodology

This section presents the methods adopted in this study. The concept is to segment customers based on their attributes (purchase behaviour). Thus, unsupervised machine learning clustering techniques are considered appropriate for this purpose. We employ sophisticated clustering algorithms, namely, k-means clustering, the Gaussian mixture model (GMM), density-based spatial clustering of applications with noise (DBSCAN), agglomerative clustering, and balanced iterative reducing and clustering using hierarchies (BIRCH). Beforehand, we employed the recency frequency monetary (RFM) model. We will thus provide a comprehensive analysis of the ML-based clustering models for customer segmentation. In the subsequent section, we will discuss the concepts of these algorithms.

### 3.1. RFM

The recency, frequency, monetary (RFM) model is a valuable tool for client segmentation, focusing on three key factors, namely, recent purchases, transaction frequency, and spending amount \[19\]. It helps companies identify distinct client segments and develop customised marketing strategies. The RFM model’s simplicity and efficiency enable companies to allocate resources more effectively, focusing on high-value consumers and fostering customer loyalty. To enhance segmentation and gain deeper insights, the model can be supplemented with new dimensions or complementary methods like clustering algorithms. This approach has gained significant attention in shaping specialised marketing strategies \[6\]. [Figure 1](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f001) below provides a simple illustration of the RFM model.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g001-550.jpg)

**Figure 1.**
RFM model.

### 3.2. Principal Component Analysis

Principal component analysis (PCA) is a statistical technique that leverages the covariance component of a multivariate data, although they are different variants of the algorithm, for example, that use multi-layer perceptron to compute the linear auto-associative properties \[21\]. The principal components of multivariate data are computed and the subspace in one-dimension, where the data have the highest variance, is the first principal component. The subsequent principal components, i.e., second, third … …nth principal components, follow in the direction of the highest variance in space that is orthogonal to the previous principal component. The PCA is calculated by the eigenvalue of the input multivariate data by decomposition of the covariance matrix \[22\].

PCA works on the standardised range of values to allow for equal contribution for analysis. To obtain the PCA, the covariance matrix is first computed.

Given two-dimensional variables 𝑥1𝑎⁢𝑛⁢𝑑𝑥2, the covariance can be computed as thus:

𝐶⁢𝑜⁢𝑣⁡(𝑥1,𝑥2)=∑𝑛𝑖=1(𝑥1⁢𝑖−̅̅̅̅̅̅̅̅̅̅𝑥1)⁢(𝑥2⁢𝑖−̅̅̅̅̅̅̅̅̅̅𝑥2)𝑛−1

(1)

For multivariate data, the covariant matrix can be developed. Let us consider n-dimensional data that can be obtained by:

𝑛!(𝑛−1)!×2

(2)

Additionally, the covariance matrix for the set of data is given by:

𝐶𝑛×𝑛=(𝑐1⁢𝑖,𝑗,𝑐1⁢𝑖,𝑗=𝑐⁢𝑜⁢𝑣⁡(𝐷⁢𝑖⁢𝑚𝑖,𝐷⁢𝑖⁢𝑚𝑗)

where 𝐶𝑛×𝑛 is a matrix with 𝑛 rows and 𝑛 columns. The covariance matrix of a three-dimensional variable 𝑥1,𝑥2,𝑥3 is thus represented as


𝐶=⎛⎜
⎜
⎜
⎜⎝𝑐⁢𝑜⁢𝑣⁡(𝑥1,𝑥1)𝑐⁢𝑜⁢𝑣⁡(𝑥1,𝑥2)𝑐⁢𝑜⁢𝑣⁡(𝑥1,𝑥3)𝑐⁢𝑜⁢𝑣⁡(𝑥2,𝑥1)𝑐⁢𝑜⁢𝑣⁡(𝑥2,𝑥2)𝑐⁢𝑜⁢𝑣⁡(𝑥2,𝑥3)𝑐⁢𝑜⁢𝑣⁡(𝑥3,𝑥1)𝑐⁢𝑜⁢𝑣⁡(𝑥3,𝑥2)𝑐⁢𝑜⁢𝑣⁡(𝑥3,𝑥3)⎞⎟
⎟
⎟
⎟⎠

(3)

The corresponding eigenvalues 𝜆 and eigenvectors 𝑋 of the covariance matrix can be expressed using the formula:

\|𝐴−𝜆⁢𝐼\|=0

(4)

𝐴⁢𝑋=𝜆⁢𝑋

(5)

where 𝐴 is an 𝑛×𝑛 square matrix and 𝐼 is an identity matrix of the same shape as 𝐴.

### 3.3. Clustering Techniques

Cluster analysis is an iterative process that divides data into clusters based on similar attributes \[23\]. Techniques include density-based, partition-based, and hierarchical-based algorithms. Partition-based clustering decomposes data points into distinct K groups. The approach requires the number of clusters (K) to be pre-defined. Hierarchical clustering gradually creates clusters. This can be by adding up nearest data points from the bottom to the top (agglomerative) or by splitting data points from the top (divisive). In this case, the number of clusters required or needed is not pre-defined. In contrast, density-based clustering groups closely packed data points in space. This technique examines irregular shapes and is less sensitive to noise samples.

#### 3.3.1. K-Means Algorithm

The K-means algorithm enables the identification of homogenous groups within a consumer base \[23\]. It splits a dataset into discrete clusters based on similarity, enabling personalised marketing activities that cater to individual tastes and requirements \[24\]. The algorithm selects initial centroids, updates centroids based on the mean of the allocated points, and iteratively assigns data points to the closest cluster centroid \[23\]. The objective is to find K cluster centroids that minimise the sum of squared distances between data points and their respective cluster centroids. The within-cluster sum of squares (WCSS) is determined by dividing the sum of squared distances by the number of clusters.

The following is how the WCSS is determined:

𝑊⁢𝐶⁢𝑆⁢𝑆=∑𝑁𝑖=1∑𝐾𝑘=1𝑟𝑖⁢𝑘·⁢\|\|𝑥𝑖−𝜇𝑘\|\|2

(6)

where:


- 𝑁: number of data points.

- 𝐾: number of clusters.

- 𝑥𝑖: ith data point.

- 𝜇𝑘: kth cluster centroid.

- 𝑟𝑖⁢𝑘: indicator variable that is returned as 1 if data point 𝑥𝑖 belongs to cluster k and 0 otherwise.


The K-means algorithm aids in customer profiling in consumer segmentation, helping firms identify segments with distinctive behavioural patterns, purchase frequencies, and preferences.

#### 3.3.2. Gaussian Mixture Model (GMM) Algorithm

The Gaussian mixture model (GMM) is a powerful method for identifying subtle patterns in consumer datasets for customer segmentation. It captures the probabilistic distribution of data points, revealing hidden structures and linkages within customer behaviours. The GMM assumes a Gaussian distribution of data points within a cluster, finding hidden patterns that simpler algorithms might miss \[25\]. Its adaptability allows it to find clusters of various shapes, sizes, and densities, making it ideal for capturing intricate customer segmentation scenarios. For a dataset with 𝑁 data points and 𝐾 clusters, the GMM simplifies identifying client categories with complex behaviours, preferences, and interactions, enabling firms to adjust marketing campaigns to meet each segment’s needs.

The GMM is defined as follows for a dataset with 𝑁 data points and 𝐾 clusters:

𝑃⁡(𝑥)=∑𝐾𝑘=1𝜋𝑘·𝑁⁡(𝑥\|𝜇𝑘,𝜀𝑘)

(7)

where:


- 𝜋𝑘: proportion of data points in each cluster.

- 𝜇𝑘: mean vectors for each distribution.

- 𝜀𝑘: matrices that represent the shape and orientation of each distribution.


#### 3.3.3. DBSCAN Algorithm

The density-based spatial clustering of applications with noise (DBSCAN) algorithm is a useful tool for identifying complex structures in consumer data for customer segmentation. It is particularly effective in recognising clusters of various shapes and densities, particularly in datasets with noise and irregularities \[5\]. DBSCAN groups data points based on their proximity and density, identifying core points with a minimum number of nearby points. It can identify both dense and sparse clusters, providing a comprehensive understanding of client behaviour trends. The reachability distance from point p to point q is calculated using the maximum of the core distance and Euclidean distance.

The maximum of the core distance of data point 𝑝 and the Euclidean distance p and q is the reachability distance from point 𝑝 to point 𝑞.


𝑟⁢𝑒⁢𝑎⁢𝑐⁢ℎ..𝑑⁢𝑖⁢𝑠⁢𝑡⁡(𝑝,𝑞)=max(𝑐⁢𝑜⁢𝑟⁢𝑒..𝑑⁢𝑖⁢𝑠⁢𝑡⁡(𝑝),\|\|𝑝−𝑞\|\|

(8)

#### 3.3.4. BIRCH Algorithm

The balanced iterative reducing and clustering utilising hierarchies (BIRCH) algorithm is a powerful tool for handling large datasets quickly and maintaining hierarchical linkages in customer segmentation \[17\]. It uses a two-phase strategy, organising data points into subclusters and creating a Cluster Feature Tree (CFT) in the first phase. The second phase merges smaller clusters into larger ones, providing insights into broad and specific trends and scalable segmentation.

The formula for the distance between the two clusters 𝐶1 and 𝐶2 is:

𝐷⁡(𝐶1,𝐶2)=√𝑁1⁢𝑁2𝑁1+𝑁2⁢·⁢𝐿⁢𝑆⁢𝑈⁢𝑀1𝑁1−𝐿⁢𝑆⁢𝑈⁢𝑀2𝑁2

(9)

where:


- N: number of data points in the cluster.

- 𝐿⁢𝑆⁢𝑈⁢𝑀: sum of data points in the cluster.


#### 3.3.5. Agglomerative Algorithm

Agglomerative clustering is a popular hierarchical clustering method used in customer segmentation research. It treats each data point as an independent cluster and merges the nearest clusters iteratively until all data points are contained in a single cluster or a preset number of clusters are formed \[26\]. The distance between two clusters is computed using the algorithm’s linking criteria, which include single linkage, complete linkage, average linkage, and Ward’s linkage. Ward’s linkage minimises the variance increase following cluster fusion, while the average linkage computes the average distance between all points.

The equations for these linkage approaches are as follows, given two clusters A 𝐴 and 𝐵 and 𝑎 distance metric 𝑑⁡(𝐴,𝐵) that gauges the distance between the clusters:

𝑑𝑠⁢𝑖⁢𝑛⁢𝑔⁡𝑙⁢𝑒⁡(𝐴,𝐵)=𝑚⁢𝑖⁢𝑛𝑎∈𝐴,𝑏∈𝐵⁢𝑑⁡(𝑎,𝑏)

(10)

𝑑𝑐⁢𝑜⁢𝑚⁢𝑝⁢𝑙⁢𝑒⁢𝑡⁢𝑒⁡(𝐴,𝐵)=𝑚⁢𝑎⁢𝑥𝑎∈𝐴,𝑏∈𝐵⁢𝑑⁡(𝑎,𝑏)

(11)

𝑑𝑎⁢𝑣⁢𝑒⁢𝑟⁢𝑎⁢𝑔⁡𝑒⁡(𝐴,𝐵)=∑𝑎∈𝐴∑𝑏∈𝐵𝑑⁡(𝑎,𝑏)

(12)

### 3.4. Dataset

We used a retail dataset obtained from the UCI machine learning repository for our study. The dataset is publicly accessible at the UCI Machine Learning Repository: Online Retail Data Set ( [https://archive.ics.uci.edu/dataset/352/online+retail](https://archive.ics.uci.edu/dataset/352/online+retail)) (accessed on 16 May 2023). We chose the dataset due to its volume and popularity in proposing algorithms for retail customer segmentation \[6\]. The dataset contains 541,909 entries and eight different variables detailed below.

- InvoiceNo: Invoice number. A nominal, six-digit integral number uniquely assigned to each transaction. If this code starts with the letter ‘c’, it indicates a cancellation.

- StockCode: Product (item) code. A nominal, five-digit integral number uniquely assigned to each distinct product.

- Description: Product (item) name. Nominal.

- Quantity: The quantities of each product (item) per transaction. Numeric.

- InvoiceDate: Invoice date and time. Numeric, the day and time at which each transaction was generated.

- UnitPrice: Unit price. Numeric. Product price per unit in sterling.

- CustomerID: Customer number. A nominal, five-digit integral number uniquely assigned to each customer.

- Country: Country name. Nominal. The name of the country where each customer resides.


### 3.5. Experimental Set Up

Python is a robust tool for implementing advanced customer segmentation techniques due to its versatility, extensive libraries, and user-friendly syntax, making it an ideal choice for extracting valuable insights from complex datasets. Different python libraries were utilised in this research. Pandas was used for statistical analysis, NumPy for numerical calculations, StatsModels for data analysis, Matplotlib for charting, Scikit-Learn for ML algorithms and metrics evaluation, Seaborn for data visualisation, and Deap for evolutionary algorithms. Specialised imports include tools from the Deap library, modules like RandomizedSearchCV, LabelEncoder, MinMaxScaler, StandardScaler, PCA, KMeans, GaussianMixture, Silhouette\_score, DBSCAN, and make\_blobs, and various metrics. The warning module was imported to optimise code performance. The experimental setup is shown in [Figure 2](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f002) below.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g002-550.jpg)

**Figure 2.**
Experimental setup.

### 3.6. Data Pre-Processing

Data pre-processing is an essential step in ensuring a correct, consistent, and unbiased analysis. During the pre-processing stage, the null values were identified, specifically in the ‘Description’ and ‘CustomerID’ fields. The modified dimensions of the dataset are 406,829 rows and eight columns, indicating successful removal of blank “CustomerID” entries. Furthermore, incorrect values were removed from the dataset, with 8905 entries having negative values in the ‘quantity’ field. In addition, we eliminated duplicate records, removing rows with identical values in all columns. After pre-processing, we had a total of 397,924 records with eight columns. A sample data representation of the features is provided in [Table 1](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-t001) below.

![](https://pub.mdpi-res.com/img/table.png)

**Table 1.**
Important features in the retail dataset.


### 3.7. Model Evaluation

The Silhouette Score is a metric used to assess the quality of clusters produced by various clustering techniques like k-means, DBSCAN, and Gaussian mixture models \[6,27\]. It measures the separation and compactness of the clusters, quantifying the cohesion of data points within the same cluster and separation between distinct clusters. Higher scores indicate better segmentation, aiding in selecting the best algorithm. The Silhouette Score is explained mathematically below:

𝑠⁡(𝑖)=𝑏⁡(𝑖)−𝑎⁡(𝑖)max⁡(𝑎⁡(𝑖),𝑏⁡(𝑖))

(13)

where:


- 𝑠⁡(𝑖) is the Silhouette Score for the data point.

- 𝑎⁡(𝑖) is the average distance between i and other data points in the same cluster.

- 𝑏⁡(𝑖) is the smallest average distance between i and data points in different clusters.


The Silhouette Score for the entire dataset is the average of the Silhouette Scores of all data points.

## 4\. Result

This section presents our results for the RFM customer analysis and an experimental comparison of the unsupervised machine learning algorithms employed.

### 4.1. RFM Results

The RFM analysis includes recency, frequency, monetary value, and ranking customer scores based on the RFM scores. Customer value is segmented into top, high-value, medium-value, low-value, and lost customers based on their scores. Customer segments were annotated using nested NP. The input dataset was split into training and testing datasets at 80% and 20%, respectively. Each row displayed a unique customer and customer segment along with their score.

The process calculates the recency, frequency, and monetary values for each customer, determining their latest invoice date. Frequency is determined by counting distinct invoice dates for each customer. The total invoice price is represented as monetary. The first five records shown in [Table 2](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-t002) represent distinct customers with corresponding RFM values.

![](https://pub.mdpi-res.com/img/table.png)

**Table 2.**
RFM components.


The study uses the rank method to rank customers based on their recency, frequency, and monetary worth. It assigns a rank to each customer based on their score, dividing each rank by the highest rank and multiplying it by 100. The first five entries in [Table 3](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-t003) represent distinct customers and their sum of recent, frequent, and monetary values. The RFM score was then used to rank customers’ data. The RFM score was calculated using the following formula:

𝑅⁢𝐹⁡𝑀𝑆⁢𝑐⁢𝑜⁢𝑟⁢𝑒=(𝑅⁢𝑒⁢𝑐⁢𝑒⁢𝑛⁢𝑐⁢𝑦𝑆⁢𝑐⁢𝑜⁢𝑟⁢𝑒×𝑅⁢𝑒⁢𝑐⁢𝑒⁢𝑛⁢𝑐⁢𝑦𝑊⁢𝑒⁢𝑖⁢𝑔⁡ℎ⁡𝑡)+(𝐹⁡𝑟⁢𝑒⁢𝑞⁢𝑢⁢𝑒⁢𝑛⁢𝑐⁢𝑦𝑆⁢𝑐⁢𝑜⁢𝑟⁢𝑒×⁢𝐹⁡𝑟⁢𝑒⁢𝑞⁢𝑢⁢𝑒⁢𝑛⁢𝑐⁢𝑦𝑊⁢𝑒⁢𝑖⁢𝑔⁡ℎ⁡𝑡)+(𝑀⁢𝑜⁢𝑛⁢𝑒⁢𝑡⁢𝑎⁢𝑟⁢𝑦𝑆⁢𝑐⁢𝑜⁢𝑟⁢𝑒×𝑀⁢𝑜⁢𝑛⁢𝑒⁢𝑡⁢𝑎⁢𝑟⁢𝑦𝑊⁢𝑒⁢𝑖⁢𝑔⁡ℎ⁡𝑡)

(14)

where:


![](https://pub.mdpi-res.com/img/table.png)

**Table 3.**
RFM score.


- 𝑅⁢𝑒⁢𝑐⁢𝑒⁢𝑛⁢𝑐⁢𝑦𝑊⁢𝑒⁢𝑖⁢𝑔⁡ℎ⁡𝑡 reflects how important recency is in the analysis.

- 𝐹⁡𝑟⁢𝑒⁢𝑞⁢𝑢⁢𝑒⁢𝑛⁢𝑐⁢𝑦𝑊⁢𝑒⁢𝑖⁢𝑔⁡ℎ⁡𝑡 reflects how important frequency is in the analysis.

- 𝑀⁢𝑜⁢𝑛⁢𝑒⁢𝑡⁢𝑎⁢𝑟⁢𝑦𝑊⁢𝑒⁢𝑖⁢𝑔⁡ℎ⁡𝑡 reflects how important monetary value is in the analysis.


The customer segments were categorised based on their RFM score, with top customers having a score above 4.5, high-value customers having a score above 4, medium-value customers having a score above 3, low-value customers having a score above 1.6, and lost customers having a score below 1.6.

[Table 4](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-t004) below displays the top 10 records in the dataset, with each row representing a unique customer and the ‘Customer\_segment’ column indicating their segment based on their score.

![](https://pub.mdpi-res.com/img/table.png)

**Table 4.**
Customer segmentation based on RFM score.


[Figure 3](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f003) displays the sizes and percentages of different client groups, with 31% of them being lost customers, 30% being low-value customers, 21% being medium-value customers, 10% being high-value customers, and 8% being top customers.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g003-550.jpg)

**Figure 3.**
Visualisation of customer segments.

### 4.2. Clustering Results

Unsupervised machine learning algorithms were applied and evaluated using the Silhouette Score. Each clustering algorithm was evaluated by accessing the quality of clustering samples within the dataset.

#### 4.2.1. K-Means Clustering

We employed the elbow approach to determine the optimal number of clusters (k). It estimates inertia, representing sample distances to the nearest cluster centre, for various cluster counts from 2 to 10. The inertia values were plotted against the number of clusters, as shown in [Figure 3](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f003) below.

[Figure 4](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f004) below illustrates the elbow method for visualising inertia, revealing that the optimal number of clusters is 3, as we are looking for a sharp edge like an elbow. We have scaled our dataset using Min–Max scaling for the dataset to conform to the same scale. This is a good practice for algorithms that rely on distance metrics for computation in order to avoid bias. The scaled data were then used to build our k-means clustering model. The result of the three clusters are visualised in [Figure 5](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f005) below. [Figure 5](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f005) displays a scatter plot of k-means, coloured by cluster labels assigned by the model. Inertia indicates the compactness of the clusters, while cluster centres reflect the centroid coordinates of each cluster.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g004-550.jpg)

**Figure 4.**
Elbow method.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g005-550.jpg)

**Figure 5.**
K-means algorithm visualisation.

#### 4.2.2. Gaussian Mixture Model

Beforehand, we employed principal component analysis (PCA) for dimensionality reduction. The number of PCA components should not exceed the maximum possible number of components, which is determined by the minimum of the number of samples and features in the dataset. In this dataset, we have two features, so choosing two PCA components is a reasonable choice for visualisation purposes because it reduces the data to a two-dimensional space, making it easier to plot and interpret. Two principal components were found and thus these were fed into the GMM. [Figure 6](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f006) below shows a visualisation of the GMM clustering results using P1 and P2 components. Each data point is assigned a colour based on its cluster.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g006-550.jpg)

**Figure 6.**
GMM result visualisation.

#### 4.2.3. DBSCAN Clustering Algorithm

The DBSCAN clustering algorithm uses standardised data to compute cluster labels using the eps parameter to determine the maximum distance between samples in the same neighbourhood. We used a K-distance plot to determine the best epsilon (eps) value. While it was challenging to identify the knee point from the plot, we experimented with different epsilon values and found that the one yielding the highest accuracy was 0.3. The min\_samples parameter specifies the minimum number of samples needed for dense regions. The algorithm assigns cluster labels to data points and identifies core samples with sufficient neighbours. The code segment calculates clusters by checking for noise points and subtracting one from the total number of unique labels to exclude noise clusters. [Figure 7](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f007) below displays the DBSCAN clustering results, with markers representing data points and colours based on cluster labels. Noise points, represented by black, are not clustered and plotted as larger markers. The plot includes a title indicating the estimated number of clusters. There are three clusters: yellow, green, and red. Yellow clusters are between −2 and 0.5 on the x axis and −2 and 0.5 on the y axis. Green clusters are between (0, 0.5) and (2, 0.5), and red clusters are between 0 and 2. Visualising these results helps understand data distribution and separation.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g007-550.jpg)

**Figure 7.**
DBSCAN visualisation.

#### 4.2.4. BIRCH Algorithm

The BIRCH clustering algorithm efficiently handles large datasets and is suitable for memory usage concerns. The threshold value determines the maximum diameter of subclusters in the hierarchical clustering structure. A lower threshold creates more fine-grained clusters, while a higher threshold leads to larger and coarser clusters. We tried different thresholds ranging from 0.01 to 1 and found that 0.01 yielded the highest performance based on the Silhouette Score. Three distinct groups have been identified in the dataset, as shown in [Figure 8](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f008). The algorithm achieved a reasonable degree of separation based on the Silhouette Score, indicating a good clustering performance.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g008-550.jpg)

**Figure 8.**
BIRCH algorithm visualisation.

#### 4.2.5. Agglomerative Clustering

[Figure 9](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-f009) below shows the scatter plots of data points coloured according to their assigned cluster labels. This visualisation helps identify patterns, separations, and areas of similarities and dissimilarities. The “rainbow” colormap assigns different colours to each cluster, aiding in analysis and decision making.

![](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g009-550.jpg)

**Figure 9.**
Agglomerative clustering visualisation.

### 4.3. Model Performance Evaluation

The Gaussian mixture model, k-means clustering, BIRCH, and agglomerative clustering created clusters in minimal computation times, making them better clustering algorithms in terms of complexity and the dataset used. [Table 5](https://www.mdpi.com/2813-2203/2/4/42#analytics-02-00042-t005) above shows the Silhouette Score for various clustering algorithms in our study compared to previous studies. We chose the Silhouette Score as our evaluation measure because it is commonly used in existing studies. This allowed us to compare the performance of our models with existing ones. The Silhouette Score of k-means is equal to 0.64, and those of the GMM model, the DBSCAN model, BIRCH, and the agglomerative algorithm are equal to 0.80, 0.626, 0.64, and 0.64, respectively. The Silhouette Score analysis revealed that our use of PCA and GMM achieved the best performance, with a Silhouette Score of 0.80. The GMM result showed cohesive datapoints and distinct clusters. We assessed the result visually and discovered that our approach produced elements that are closely packed. This implies that overlapping clusters or mislabelled data samples did not occur. This is because the Gaussian model captures the variance of the data, resulting in a better performance than other clustering models. BIRCH and DBSCAN consider the density and proximity of points rather than explicitly modelling distributions, which makes them less prone to issues related to high dimensionalities. GMM generally struggles with high-dimensional datasets. However, in our study, GMM benefitted from PCA (reduced dimension functionality). Several runs of the k-means algorithm were performed to check for improvements. The results varied by ± 0.06. This is due to the randomness in selecting the initial centroids. This is one of the limitations of k-means in the context of Big Data.

![](https://pub.mdpi-res.com/img/table.png)

**Table 5.**
Comparison of clustering algorithms for customer segmentation.


## 5\. Conclusions

In this study, we aimed to develop a customer segmentation model to enhance decision-making processes in the retail market industry. To achieve this, we conducted an experimental comparative analysis of unsupervised machine learning clustering algorithms and thus showed that the use of principal component analysis (PCA) and the Gaussian mixture model (GMM) achieved a Silhouette Score of 0.8. The GMM provides useful insights into cluster formation. This paper also facilitates a data-driven decision-making approach through customer-data-based segmentation using machine learning techniques. This approach is beneficial to professionals performing customer segmentation, specifically in the retail market, as data are growing exponentially. One of the limitations of the RFM technique is its inability to reflect differences between the consumption and behaviour of customers. Less consideration is also given to business investments in customers. For future work, the use of sophisticated machine learning algorithms such as spectral clustering, which will allow for better analysis of customer behaviour, is proposed as they will help provide better insights into customer segmentation. Additionally, we aim to apply the kernel function to improve the linear separability of the GMM cluster output.

## Author Contributions

Conceptualisation, J.M.J. and O.S.; Data curation, J.M.J.; Formal analysis, B.O.; Investigation, J.M.J. and O.S.; Methodology, J.M.J., O.S. and B.O.; Supervision, O.S.; Visualisation, O.S. and B.O.; Writing—original draft, J.M.J.; Writing—review and editing, O.S. and B.O. All authors have read and agreed to the published version of the manuscript.

## Funding

This research received no external funding.

## Institutional Review Board Statement

Not applicable.

## Informed Consent Statement

Not applicable.

## Data Availability Statement

The dataset used in this work is available at the UCI Machine Learning Repository: Online Retail Data Set and the code can be accessed publicly via this link: [https://github.com/jeenmary55/Retail-Customer-Segmentaion](https://github.com/jeenmary55/Retail-Customer-Segmentaion) (accessed on 2 September 2023).

## Conflicts of Interest

The authors declare no conflict of interest.

## References

01. Lekhwar, S.; Yadav, S.; Singh, A. Big data analytics in retail. In Information and Communication Technology for Intelligent Systems: Proceedings of ICTIS 2018, Volume 2; Springer: Singapore, 2019; pp. 469–477. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Big+data+analytics+in+retail&author=Lekhwar,+S.&author=Yadav,+S.&author=Singh,+A.&publication_year=2019&pages=469%E2%80%93477)\]
02. Gwozdz, W.; Steensen Nielsen, K.; Müller, T. An environmental perspective on clothing consumption: Consumer segments and their behavioral patterns. Sustainability **2017**, 9, 762\. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=An+environmental+perspective+on+clothing+consumption:+Consumer+segments+and+their+behavioral+patterns&author=Gwozdz,+W.&author=Steensen+Nielsen,+K.&author=M%C3%BCller,+T.&publication_year=2017&journal=Sustainability&volume=9&pages=762&doi=10.3390/su9050762)\] \[ [CrossRef](https://doi.org/10.3390/su9050762)\] \[ [Scilit](https://www.scilit.com/publications/005a2ae0c5884ba2cd54403d20369ce8)\]
03. An, J.; Kwak, H.; Jung, S.G.; Salminen, J.; Jansen, B.J. Customer segmentation using online platforms: Isolating behavioral and demographic segments for persona creation via aggregated user data. Soc. Netw. Anal. Min. **2018**, 8, 54\. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Customer+segmentation+using+online+platforms:+Isolating+behavioral+and+demographic+segments+for+persona+creation+via+aggregated+user+data&author=An,+J.&author=Kwak,+H.&author=Jung,+S.G.&author=Salminen,+J.&author=Jansen,+B.J.&publication_year=2018&journal=Soc.+Netw.+Anal.+Min.&volume=8&pages=54&doi=10.1007/s13278-018-0531-0)\] \[ [CrossRef](https://doi.org/10.1007/s13278-018-0531-0)\] \[ [Scilit](https://www.scilit.com/publications/4dcf55beed76c2aec62e351dee0973de)\]
04. Fotaki, G.; Spruit, M.; Brinkkemper, S.; Meijer, D. Exploring big data opportunities for online customer segmentation. Int. J. Bus. Intell. Res. (IJBIR) **2014**, 5, 58–75. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Exploring+big+data+opportunities+for+online+customer+segmentation&author=Fotaki,+G.&author=Spruit,+M.&author=Brinkkemper,+S.&author=Meijer,+D.&publication_year=2014&journal=Int.+J.+Bus.+Intell.+Res.+(IJBIR)&volume=5&pages=58%E2%80%9375&doi=10.4018/ijbir.2014070105)\] \[ [CrossRef](https://doi.org/10.4018/ijbir.2014070105)\] \[ [Scilit](https://www.scilit.com/publications/bee27471d1820019d4e80207ce72de2c)\]
05. Hicham, N.; Karim, S. Analysis of Unsupervised Machine Learning Techniques for an Efficient Customer Segmentation using Clustering Ensemble and Spectral Clustering. Int. J. Adv. Comput. Sci. Appl. **2022**, 13, 122–130. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Analysis+of+Unsupervised+Machine+Learning+Techniques+for+an+Efficient+Customer+Segmentation+using+Clustering+Ensemble+and+Spectral+Clustering&author=Hicham,+N.&author=Karim,+S.&publication_year=2022&journal=Int.+J.+Adv.+Comput.+Sci.+Appl.&volume=13&pages=122%E2%80%93130&doi=10.14569/IJACSA.2022.0131016)\] \[ [CrossRef](https://doi.org/10.14569/IJACSA.2022.0131016)\] \[ [Scilit](https://www.scilit.com/publications/0561cca83dae0f836bbf2bc9a5e19fc4)\]
06. Turkmen, B. Customer Segmentation with Machine Learning for Online Retail Industry. Eur. J. Soc. Behav. Sci. **2022**, 31, 111–136. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Customer+Segmentation+with+Machine+Learning+for+Online+Retail+Industry&author=Turkmen,+B.&publication_year=2022&journal=Eur.+J.+Soc.+Behav.+Sci.&volume=31&pages=111%E2%80%93136&doi=10.15405/ejsbs.316)\] \[ [CrossRef](https://doi.org/10.15405/ejsbs.316)\] \[ [Scilit](https://www.scilit.com/publications/b82b2408cc35c1897ee6362904ecb6c8)\]
07. Ramanathan, U.; Subramanian, N.; Yu, W.; Vijaygopal, R. Impact of customer loyalty and service operations on customer behaviour and firm performance: Empirical evidence from UK retail sector. Prod. Plan. Control **2017**, 28, 478–488. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Impact+of+customer+loyalty+and+service+operations+on+customer+behaviour+and+firm+performance:+Empirical+evidence+from+UK+retail+sector&author=Ramanathan,+U.&author=Subramanian,+N.&author=Yu,+W.&author=Vijaygopal,+R.&publication_year=2017&journal=Prod.+Plan.+Control&volume=28&pages=478%E2%80%93488&doi=10.1080/09537287.2017.1309707)\] \[ [CrossRef](https://doi.org/10.1080/09537287.2017.1309707)\] \[ [Scilit](https://www.scilit.com/publications/6f77099f5cc9a64123428474713d3dca)\]
08. Li, C.; Chen, Y.; Shang, Y. A review of industrial big data for decision making in intelligent manufacturing. Eng. Sci. Technol. Int. J. **2022**, 29, 101021\. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=A+review+of+industrial+big+data+for+decision+making+in+intelligent+manufacturing&author=Li,+C.&author=Chen,+Y.&author=Shang,+Y.&publication_year=2022&journal=Eng.+Sci.+Technol.+Int.+J.&volume=29&pages=101021&doi=10.1016/j.jestch.2021.06.001)\] \[ [CrossRef](https://doi.org/10.1016/j.jestch.2021.06.001)\] \[ [Scilit](https://www.scilit.com/publications/73f92b70ba17a85bf83c4689b6b76f6b)\]
09. Arunachalam, D.; Kumar, N. Benefit-based consumer segmentation and performance evaluation of clustering approaches: An evidence of data-driven decision-making. Expert Syst. Appl. **2018**, 111, 11–34. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Benefit-based+consumer+segmentation+and+performance+evaluation+of+clustering+approaches:+An+evidence+of+data-driven+decision-making&author=Arunachalam,+D.&author=Kumar,+N.&publication_year=2018&journal=Expert+Syst.+Appl.&volume=111&pages=11%E2%80%9334&doi=10.1016/j.eswa.2018.03.007)\] \[ [CrossRef](https://doi.org/10.1016/j.eswa.2018.03.007)\] \[ [Scilit](https://www.scilit.com/publications/351e288743f34118768b211b2c438d59)\]
10. Oussous, A.; Benjelloun, F.Z.; Lahcen, A.A.; Belfkih, S. Big Data technologies: A survey. J. King Saud Univ.-Comput. Inf. Sci. **2018**, 30, 431–448. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Big+Data+technologies:+A+survey&author=Oussous,+A.&author=Benjelloun,+F.Z.&author=Lahcen,+A.A.&author=Belfkih,+S.&publication_year=2018&journal=J.+King+Saud+Univ.-Comput.+Inf.+Sci.&volume=30&pages=431%E2%80%93448&doi=10.1016/j.jksuci.2017.06.001)\] \[ [CrossRef](https://doi.org/10.1016/j.jksuci.2017.06.001)\] \[ [Scilit](https://www.scilit.com/publications/9d27c757c7b771c7a2d5687b26ef9a85)\]
11. Jin, D.H.; Kim, H.J. Integrated understanding of big data, big data analysis, and business intelligence: A case study of logistics. Sustainability **2018**, 10, 3778\. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Integrated+understanding+of+big+data,+big+data+analysis,+and+business+intelligence:+A+case+study+of+logistics&author=Jin,+D.H.&author=Kim,+H.J.&publication_year=2018&journal=Sustainability&volume=10&pages=3778&doi=10.3390/su10103778)\] \[ [CrossRef](https://doi.org/10.3390/su10103778)\] \[ [Scilit](https://www.scilit.com/publications/87a8ff149ad87f27fe68e697052443b4)\]
12. Jayakrishnan, M.; Mohamad, A.K.; Yusof, M.M. Understanding big data analytics (BDA) and business intelligence (BI) towards establishing organisational performance diagnostics framework. Int. J. Recent Technol. Eng. **2019**, 8, 128–132. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Understanding+big+data+analytics+(BDA)+and+business+intelligence+(BI)+towards+establishing+organisational+performance+diagnostics+framework&author=Jayakrishnan,+M.&author=Mohamad,+A.K.&author=Yusof,+M.M.&publication_year=2019&journal=Int.+J.+Recent+Technol.+Eng.&volume=8&pages=128%E2%80%93132)\]
13. Mathew, A.; Scholar, P.G.; Jobin, T.J. Role of Big Data Analysis and Machine Learning in Ecommerce-Customer Segmentation. In Proceedings of the National Conference on Emerging Computer Applications (NCECA), Online, 17 June 2021; p. 189. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Role+of+Big+Data+Analysis+and+Machine+Learning+in+Ecommerce-Customer+Segmentation&conference=Proceedings+of+the+National+Conference+on+Emerging+Computer+Applications+(NCECA)&author=Mathew,+A.&author=Scholar,+P.G.&author=Jobin,+T.J.&publication_year=2021&pages=189)\]
14. Seyedan, M.; Mafakheri, F. Predictive big data analytics for supply chain demand forecasting: Methods, applications, and research opportunities. J. Big Data **2020**, 7, 1–22. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Predictive+big+data+analytics+for+supply+chain+demand+forecasting:+Methods,+applications,+and+research+opportunities&author=Seyedan,+M.&author=Mafakheri,+F.&publication_year=2020&journal=J.+Big+Data&volume=7&pages=1%E2%80%9322&doi=10.1186/s40537-020-00329-2)\] \[ [CrossRef](https://doi.org/10.1186/s40537-020-00329-2)\] \[ [Scilit](https://www.scilit.com/publications/dc2c1212352eb0f1a560bc53e42c0853)\]
15. Ushakova, A.; Mikhaylov, S.J. Big data to the rescue? Challenges in analysing granular household electricity consumption in the United Kingdom. Energy Res. Soc. Sci. **2020**, 64, 101428\. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Big+data+to+the+rescue?+Challenges+in+analysing+granular+household+electricity+consumption+in+the+United+Kingdom&author=Ushakova,+A.&author=Mikhaylov,+S.J.&publication_year=2020&journal=Energy+Res.+Soc.+Sci.&volume=64&pages=101428&doi=10.1016/j.erss.2020.101428)\] \[ [CrossRef](https://doi.org/10.1016/j.erss.2020.101428)\] \[ [Scilit](https://www.scilit.com/publications/9a6ccb38abe89b8f6555909ceee5d389)\]
16. Fontanini, A.D.; Abreu, J. A data-driven BIRCH clustering method for extracting typical load profiles for big data. In Proceedings of the 2018 IEEE Power & Energy Society General Meeting (PESGM), Portland, OR, USA, 5–10 August 2018; pp. 1–5. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=A+data-driven+BIRCH+clustering+method+for+extracting+typical+load+profiles+for+big+data&conference=Proceedings+of+the+2018+IEEE+Power+&+Energy+Society+General+Meeting+(PESGM)&author=Fontanini,+A.D.&author=Abreu,+J.&publication_year=2018&pages=1%E2%80%935)\]
17. Lorbeer, B.; Kosareva, A.; Deva, B.; Softić, D.; Ruppel, P.; Küpper, A. Variations on the clustering algorithm BIRCH. Big Data Res. **2018**, 11, 44–53. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Variations+on+the+clustering+algorithm+BIRCH&author=Lorbeer,+B.&author=Kosareva,+A.&author=Deva,+B.&author=Softi%C4%87,+D.&author=Ruppel,+P.&author=K%C3%BCpper,+A.&publication_year=2018&journal=Big+Data+Res.&volume=11&pages=44%E2%80%9353&doi=10.1016/j.bdr.2017.09.002)\] \[ [CrossRef](https://doi.org/10.1016/j.bdr.2017.09.002)\] \[ [Scilit](https://www.scilit.com/publications/0253fcd52acbc3cd7d30cb4c4024300e)\]
18. Firdaus, U.; Utama, D. Development of bank’s customer segmentation model based on rfm+ b approach. Int. J. Innov. Comput. Inf. Cont. **2021**, 12, 17–26. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Development+of+bank%E2%80%99s+customer+segmentation+model+based+on+rfm++b+approach&author=Firdaus,+U.&author=Utama,+D.&publication_year=2021&journal=Int.+J.+Innov.+Comput.+Inf.+Cont.&volume=12&pages=17%E2%80%9326)\]
19. Hossain, A.S. Customer segmentation using centroid based and density based clustering algorithms. In Proceedings of the 2017 3rd International Conference on Electrical Information and Communication Technology (EICT), Khulna, Bangladesh, 7–9 December 2017; pp. 1–6. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Customer+segmentation+using+centroid+based+and+density+based+clustering+algorithms&conference=Proceedings+of+the+2017+3rd+International+Conference+on+Electrical+Information+and+Communication+Technology+(EICT)&author=Hossain,+A.S.&publication_year=2017&pages=1%E2%80%936)\]
20. Punhani, R.; Arora, V.S.; Sabitha, S.; Shukla, V.K. Application of clustering algorithm for effective customer segmentation in E-commerce. In Proceedings of the 2021 International Conference on Computational Intelligence and Knowledge Economy (ICCIKE), Dubai, United Arab Emirates, 17–18 March 2021; pp. 149–154. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Application+of+clustering+algorithm+for+effective+customer+segmentation+in+E-commerce&conference=Proceedings+of+the+2021+International+Conference+on+Computational+Intelligence+and+Knowledge+Economy+(ICCIKE)&author=Punhani,+R.&author=Arora,+V.S.&author=Sabitha,+S.&author=Shukla,+V.K.&publication_year=2021&pages=149%E2%80%93154)\]
21. Diamantaras, K.I.; Kung, S.Y. Principal Component Neural Networks: Theory and Applications; John Wiley & Sons, Inc.: Hoboken, NJ, USA, 1996. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Principal+Component+Neural+Networks:+Theory+and+Applications&author=Diamantaras,+K.I.&author=Kung,+S.Y.&publication_year=1996)\]
22. Weingessel, A.; Hornik, K. Local PCA algorithms. IEEE Trans. Neural Netw. **2000**, 11, 1242–1250. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Local+PCA+algorithms&author=Weingessel,+A.&author=Hornik,+K.&publication_year=2000&journal=IEEE+Trans.+Neural+Netw.&volume=11&pages=1242%E2%80%931250&pmid=18249850)\] \[ [PubMed](https://www.ncbi.nlm.nih.gov/pubmed/18249850)\]
23. Ogunleye, B.; Maswera, T.; Hirsch, L.; Gaudoin, J.; Brunsdon, T. Comparison of topic modelling approaches in the banking context. Appl. Sci. **2023**, 13, 797\. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Comparison+of+topic+modelling+approaches+in+the+banking+context&author=Ogunleye,+B.&author=Maswera,+T.&author=Hirsch,+L.&author=Gaudoin,+J.&author=Brunsdon,+T.&publication_year=2023&journal=Appl.+Sci.&volume=13&pages=797&doi=10.3390/app13020797)\] \[ [CrossRef](https://doi.org/10.3390/app13020797)\] \[ [Scilit](https://www.scilit.com/publications/1ac6a88bc26bca5bb7fb0b39cf933602)\]
24. Lloyd, S.P. Least squares quantization in PCM. IEEE Trans. Inf. Theory **1982**, 28, 129–137. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Least+squares+quantization+in+PCM&author=Lloyd,+S.P.&publication_year=1982&journal=IEEE+Trans.+Inf.+Theory&volume=28&pages=129%E2%80%93137&doi=10.1109/TIT.1982.1056489)\] \[ [CrossRef](https://doi.org/10.1109/TIT.1982.1056489)\] \[ [Scilit](https://www.scilit.com/publications/f11c10eadffad6dd59391608268387fa)\]
25. Zhang, Y.; Li, M.; Wang, S.; Dai, S.; Luo, L.; Zhu, E.; Xu, H.; Zhu, X.; Yao, C.; Zhou, H. Gaussian mixture model clustering with incomplete data. ACM Trans. Multimed. Comput. Commun. Appl. (TOMM) **2021**, 17, 1–14. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Gaussian+mixture+model+clustering+with+incomplete+data&author=Zhang,+Y.&author=Li,+M.&author=Wang,+S.&author=Dai,+S.&author=Luo,+L.&author=Zhu,+E.&author=Xu,+H.&author=Zhu,+X.&author=Yao,+C.&author=Zhou,+H.&publication_year=2021&journal=ACM+Trans.+Multimed.+Comput.+Commun.+Appl.+(TOMM)&volume=17&pages=1%E2%80%9314&doi=10.1145/3408318)\] \[ [CrossRef](https://doi.org/10.1145/3408318)\] \[ [Scilit](https://www.scilit.com/publications/3b7d3a13f1288619950e92c87bfd6860)\]
26. Müllner, D. Modern hierarchical, agglomerative clustering algorithms. arXiv **2011**, arXiv:1109.2378. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Modern+hierarchical,+agglomerative+clustering+algorithms&author=M%C3%BCllner,+D.&publication_year=2011&journal=arXiv)\]
27. Shirole, R.; Salokhe, L.; Jadhav, S. Customer segmentation using rfm model and k-means clustering. Int. J. Sci. Res. Sci. Technol. **2021**, 8, 591–597. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=Customer+segmentation+using+rfm+model+and+k-means+clustering&author=Shirole,+R.&author=Salokhe,+L.&author=Jadhav,+S.&publication_year=2021&journal=Int.+J.+Sci.+Res.+Sci.+Technol.&volume=8&pages=591%E2%80%93597&doi=10.32628/IJSRST2183118)\] \[ [CrossRef](https://doi.org/10.32628/IJSRST2183118)\] \[ [Scilit](https://www.scilit.com/publications/0458473a7f2ff82476a91bc0634f34ad)\]
28. Kansal, T.; Bahuguna, S.; Singh, V.; Choudhury, T. December Customer segmentation using K-means clustering. In Proceedings of the 2018 International Conference on Computational Techniques, Electronics and Mechanical Systems (CTEMS), Belgaum, India, 21–22 December 2018; pp. 135–139. \[ [Google Scholar](https://scholar.google.com/scholar_lookup?title=December+Customer+segmentation+using+K-means+clustering&conference=Proceedings+of+the+2018+International+Conference+on+Computational+Techniques,+Electronics+and+Mechanical+Systems+(CTEMS)&author=Kansal,+T.&author=Bahuguna,+S.&author=Singh,+V.&author=Choudhury,+T.&publication_year=2018&pages=135%E2%80%93139)\]

![Analytics 02 00042 g001](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g001-550.jpg)

**Figure 1.**
RFM model.

![Analytics 02 00042 g002](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g002-550.jpg)

**Figure 2.**
Experimental setup.

![Analytics 02 00042 g003](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g003-550.jpg)

**Figure 3.**
Visualisation of customer segments.

![Analytics 02 00042 g004](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g004-550.jpg)

**Figure 4.**
Elbow method.

![Analytics 02 00042 g005](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g005-550.jpg)

**Figure 5.**
K-means algorithm visualisation.

![Analytics 02 00042 g006](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g006-550.jpg)

**Figure 6.**
GMM result visualisation.

![Analytics 02 00042 g007](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g007-550.jpg)

**Figure 7.**
DBSCAN visualisation.

![Analytics 02 00042 g008](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g008-550.jpg)

**Figure 8.**
BIRCH algorithm visualisation.

![Analytics 02 00042 g009](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g009-550.jpg)

**Figure 9.**
Agglomerative clustering visualisation.

![](https://pub.mdpi-res.com/img/table.png)

**Table 1.**
Important features in the retail dataset.


![](https://pub.mdpi-res.com/img/table.png)

**Table 2.**
RFM components.


![](https://pub.mdpi-res.com/img/table.png)

**Table 3.**
RFM score.


![](https://pub.mdpi-res.com/img/table.png)

**Table 4.**
Customer segmentation based on RFM score.


![](https://pub.mdpi-res.com/img/table.png)

**Table 5.**
Comparison of clustering algorithms for customer segmentation.


|     |     |
| --- | --- |
|  | **Disclaimer/Publisher’s Note:** The statements, opinions and data contained in all publications are solely those of the individual author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting from any ideas, methods, instructions or products referred to in the content. |

© 2023 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license ( [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)).

## Article Metrics

Citations

- [Google Scholar](https://scholar.google.com/scholar_lookup?title=An+Exploration+of+Clustering+Algorithms+for+Customer+Segmentation+in+the+UK+Retail+Market&volume=2&doi=10.3390%2Fanalytics2040042&journal=Analytics&publication_year=2023&author=Jeen+Mary+John&author=Olamilekan+Shobayo&author=Bayode+Ogunleye)


71

[Scopus](https://www.scopus.com/inward/citedby.uri?partnerID=HzOxMe3b&scp=105009206796&origin=inward)

30

[Web of Science](https://www.webofscience.com/api/gateway?GWVersion=2&SrcApp=PARTNER_APP&SrcAuth=LinksAMR&KeyUT=WOS:001901393900001&DestLinkType=FullRecord&DestApp=ALL_WOS&UsrCustomerID=7e717b028bc90856e7c55c7029afc773)

61

Crossref

### Article Access Statistics

[Journal Statistics](https://www.mdpi.com/journal/analytics/stats)

Multiple requests from the same IP address are counted as one view.

[A Novel Curve Clustering Method for Functional Data: Applications to COVID-19 and Financial Data\\
Previous](https://www.mdpi.com/2813-2203/2/4/41) [Relating the Ramsay Quotient Model to the Classical D-Scoring Rule\\
Next](https://www.mdpi.com/2813-2203/2/4/43)

[![X](https://mdpi-res.com/data/x-square-filled.svg)](https://x.com/AnalyticsMDPI)[![Facebook](https://mdpi-res.com/data/facebook-square-filled.svg)](https://www.facebook.com/MDPIOpenAccessPublishing)[![LinkedIn](https://mdpi-res.com/data/linkedin-square-filled.svg)](https://www.linkedin.com/company/analytics-mdpi)

Analytics \- ISSN 2813-2203

[Imprint](https://www.mdpi.com/journal/analytics/imprint)

RSS Download RSS feed

[Download Flyer](https://mdpi-res.com/journals/555/flyer.pdf)

**Figure 1.**
RFM model.

![Analytics 02 00042 g001](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g001.png)

**Figure 2.**
Experimental setup.

![Analytics 02 00042 g002](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g002.png)

**Figure 3.**
Visualisation of customer segments.

![Analytics 02 00042 g003](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g003.png)

**Figure 4.**
Elbow method.

![Analytics 02 00042 g004](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g004.png)

**Figure 5.**
K-means algorithm visualisation.

![Analytics 02 00042 g005](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g005.png)

**Figure 6.**
GMM result visualisation.

![Analytics 02 00042 g006](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g006.png)

**Figure 7.**
DBSCAN visualisation.

![Analytics 02 00042 g007](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g007.png)

**Figure 8.**
BIRCH algorithm visualisation.

![Analytics 02 00042 g008](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g008.png)

**Figure 9.**
Agglomerative clustering visualisation.

![Analytics 02 00042 g009](https://mdpi-res.com/analytics/analytics-02-00042/article_deploy/html/images/analytics-02-00042-g009.png)

**Table 1.**
Important features in the retail dataset.

| Invoice No | Invoice Counts | Invoice Price (GBP) |
| :-: | :-: | :-: |
| 536365 | 7 | 139.122 |
| 536366 | 2 | 22.20 |
| 536367 | 12 | 278.73 |
| 536368 | 4 | 70.05 |
| 536369 | 1 | 17.85 |

**Table 2.**
RFM components.

| Customer ID | Recency | Frequency | Monetary (GBP) |
| :-: | :-: | :-: | :-: |
| 12346 | 325 | 1 | 77,183.60 |
| 12347 | 1 | 182 | 4310.00 |
| 12348 | 74 | 31 | 1797.24 |
| 12349 | 18 | 73 | 1757.55 |
| 12350 | 309 | 17 | 334.40 |

**Table 3.**
RFM score.

| Customer ID | RFM\_Score |
| :-: | :-: |
| 12346 | 0.06 |
| 12347 | 4.48 |
| 12348 | 2.09 |
| 12349 | 3.41 |
| 12350 | 1.10 |

**Table 4.**
Customer segmentation based on RFM score.

| Customer ID | RFM\_Score | Customer\_Segment |
| :-: | :-: | :-: |
| 12346 | 0.06 | Lost customer |
| 12347 | 4.48 | High-value customer |
| 12348 | 2.09 | Low-value customer |
| 12349 | 3.41 | Medium-value customer |
| 12350 | 1.10 | Lost customer |
| 12352 | 3.46 | Medium-value customer |
| 12353 | 0.03 | Lost customer |
| 12354 | 2.67 | Low-value customer |
| 12355 | 0.93 | Lost customer |
| 12356 | 3.11 | Medium-value customer |

**Table 5.**
Comparison of clustering algorithms for customer segmentation.

| Research Studies | Clustering Algorithm | Silhouette Score |
| :-- | :-- | :-- |
| Existing Studies | Mean shift \[28\] | 0.54 |
| K-means \[5\] | 0.71 |
| K-means \[28\] | 0.57 |
| K-means \[6\] | 0.61 |
| DBSCAN \[5\] | 0.72 |
| Agglomerative \[28\] | 0.57 |
| Our study | K-means | 0.64 |
| BIRCH | 0.64 |
| DBSCAN | 0.62 |
| Agglomerative | 0.64 |
| Gaussian Mixture Model | 0.80 |

Feedback

[Posted by **2** X users](https://www.altmetric.com/details.php?domain=www.mdpi.com&citation_id=155472019&tab=twitter) Opens the X tab of this output's Altmetric details page

[**551** readers on Mendeley](https://www.altmetric.com/details.php?domain=www.mdpi.com&citation_id=155472019#mendeley-demographics) Opens the Mendeley readers on this output's Altmetric details page

[See more details](https://www.altmetric.com/details.php?domain=www.mdpi.com&citation_id=155472019)