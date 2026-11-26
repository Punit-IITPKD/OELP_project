Source: https://link.springer.com/article/10.1057/s41270-023-00235-5
Title: How can algorithms help in segmenting users and customers? A systematic review and research agenda for algorithmic customer segmentation | Journal of Marketing Analytics | Springer Nature Link
Fetched: 2026-11-26T15:58:15.634Z

[Skip to main content](https://link.springer.com/article/10.1057/s41270-023-00235-5#main)

## Search

Search by keyword or author

Search

## Navigation

- [Find a journal](https://link.springer.com/journals/)
- [Publish with us](https://www.springernature.com/gp/authors)
- [Track your research](https://link.springernature.com/home/)

# How can algorithms help in segmenting users and customers? A systematic review and research agenda for algorithmic customer segmentation

- Original Article
- [Open access](https://www.springernature.com/gp/open-science/about/the-fundamentals-of-open-access-and-open-research)
- Published: 06 July 2023

- Volume 11, pages 677–692 (2023)

- [Cite this article](https://link.springer.com/article/10.1057/s41270-023-00235-5#citeas)

You have full access to this open access article

[Download PDF](https://link.springer.com/content/pdf/10.1057/s41270-023-00235-5.pdf)

Save article

[View saved research](https://link.springer.com/saved-research)

[![](https://media.springernature.com/w72/springer-static/cover-hires/journal/41270?as=webp)Journal of Marketing Analytics](https://link.springer.com/journal/41270) [Aims and scope](https://link.springer.com/journal/41270/aims-and-scope) [Submit manuscript](https://submission.springernature.com/new-submission/41270/3)

How can algorithms help in segmenting users and customers? A systematic review and research agenda for algorithmic customer segmentation


[Download PDF](https://link.springer.com/content/pdf/10.1057/s41270-023-00235-5.pdf)

## Abstract

What algorithm to choose for customer segmentation? Should you use one algorithm or many? How many customer segments should you create? How to evaluate the results? In this research, we carry out a systematic literature review to address such central questions in customer segmentation research and practice. The results from extracting information from 172 relevant articles show that algorithmic customer segmentation is the predominant approach for customer segmentation. We found researchers employing 46 different algorithms and 14 different evaluation metrics. For the algorithms, K-means clustering is the most employed. For the metrics, separation-focused metrics are slightly more prevalent than statistics-focused metrics. However, extant studies rarely use domain experts in evaluating the outcomes. Out of the 169 studies that provided details about hyperparameters, more than four out of five used segment size as their only hyperparameter. Typically, studies generate four segments, although the maximum number rarely exceeds twenty, and in most cases, is less than ten. Based on these findings, we propose seven key goals and three practical implications to enhance customer segmentation research and application.

### Similar content being viewed by others

![](https://media.springernature.com/w92h120/springer-static/cover-hires/book/978-981-99-3932-9?as=webp)

### [Customer Segmentation Analysis Using Clustering Algorithms](https://link.springer.com/chapter/10.1007/978-981-99-3932-9_31?fromPaywallRec=false)

Chapter© 2024

![](https://media.springernature.com/w92h120/springer-static/cover-hires/book/978-981-97-4860-0?as=webp)

### [Analysis of Customer Transaction Along with Segmentation and Feedback Analysis](https://link.springer.com/chapter/10.1007/978-981-97-4860-0_9?fromPaywallRec=false)

Chapter© 2024

![](https://media.springernature.com/w92h120/springer-static/cover-hires/book/978-3-030-16148-4?as=webp)

### [Customer Segmentation Based on Transactional Data Using Stream Clustering](https://link.springer.com/chapter/10.1007/978-3-030-16148-4_22?fromPaywallRec=false)

Chapter© 2019

### Explore related subjects

Discover the latest articles, books and news in related subjects, suggested using machine learning.

- [Customer Relationship Management](https://link.springer.com/subjects/customer-relationship-management)
- [Algorithms](https://link.springer.com/subjects/algorithms)
- [Functional clustering](https://link.springer.com/subjects/functional-clustering)
- [Survey Methodology](https://link.springer.com/subjects/survey-methodology)
- [Mathematical Applications in Computer Science](https://link.springer.com/subjects/mathematical-applications-in-computer-science)
- [Discrete Mathematics in Computer Science](https://link.springer.com/subjects/discrete-mathematics-in-computer-science)
- [Market Segmentation Strategies and Methodologies](https://link.springer.com/subjects/market-segmentation-strategies-and-methodologies)

## Introduction

Business success depends on understanding customers and their needs. A key method to achieve this is _customer segmentation_, i.e., dividing individual customers into groups based on their similarities and differences (Cooil et al. [2008](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR5 "Cooil, B., L. Aksoy, and T.L. Keiningham. 2008. Approaches to Customer Segmentation. Journal of Relationship Marketing 6 (3–4): 9–39.")). As postulated by Punj and Stewart ( [1983](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR35 "Punj, G., and D.W. Stewart. 1983. Cluster Analysis in Marketing Research: Review and Suggestions for Application. Journal of Marketing Research 20 (2): 134–148."): 135), “All segmentation research, regardless of the method used, is designed to identify groups of entities (people, markets, organizations) that share certain common characteristics (attitudes, purchase propensities, media habits, etc.)”. Customer segmentation, in particular, allows businesses to create targeted marketing strategies, improve customer experience, and ultimately, increase revenue (Hosseini and Shabani [2015](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR12 "Hosseini, M., and M. Shabani. 2015. New Approach to Customer Segmentation Based on Changes in Customer Value. Journal of Marketing Analytics 3: 110–121."); Simões and Nogueira [2022](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR41 "Simões, D., and J. Nogueira. 2022. Learning about the Customer for Improving Customer Retention Proposal of an Analytical Framework. Journal of Marketing Analytics.                    https://doi.org/10.1057/s41270-021-00126-7                                    ."); Spoor [2022](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR42 "Spoor, J.M. 2022. Improving Customer Segmentation via Classification of Key Accounts as Outliers. Journal of Marketing Analytics.                    https://doi.org/10.1057/s41270-022-00185-4                                    .")). As the potential benefits are plentiful, most firms perform customer segmentation across industries, irrespective of their size (Zhou et al. [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR53 "Zhou, J., J. Wei, and B. Xu. 2021. Customer Segmentation by Web Content Mining. Journal of Retailing and Consumer Services 61: 102588.")). With the rise of artificial intelligence (AI) and machine learning (ML) technologies (Mustak et al. [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR30 "Mustak, M., J. Salminen, L. Plé, and J. Wirtz. 2021. Artificial Intelligence in Marketing: Topic Modeling, Scientometric Analysis, and Research Agenda. Journal of Business Research 124: 389–404.")), firms are increasingly turning to more advanced AI and ML algorithms (we refer to these as AI/ML algorithms henceforth; for the reader interested in the conceptual distinction of these two terms, we recommend reading Kühl et al. [2022](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR20 "Kühl, N., M. Schemmer, M. Goutier, and G. Satzger. 2022. Artificial Intelligence and Machine Learning. Electronic Markets 32 (4): 2235–2244.")) to perform customer segmentation. To this end, customer segmentation undoubtedly represents a cornerstone application of AI for business purposes, as it represents an unsupervised learning problem where AI/ML algorithms are known to be applicable (Joung and Kim [2023](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR15 "Joung, J., and H. Kim. 2023. Interpretable Machine Learning-Based Approach for Customer Segmentation for New Product Development from Online Product Reviews. International Journal of Information Management 70: 102641."); Ranjan and Srivastava [2022](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR60 "Ranjan, A., and S. Srivastava. 2022. Customer Segmentation Using Machine Learning: A Literature Review. In: AIP Conference Proceedings, 2022. vol. 2481. AIP Publishing LLC, p. 020036.")). This relationship is illustrated in Fig. [1](https://link.springer.com/article/10.1057/s41270-023-00235-5#Fig1).

**Fig. 1**

![Fig. 1](https://media.springernature.com/lw685/springer-static/image/art%3A10.1057%2Fs41270-023-00235-5/MediaObjects/41270_2023_235_Fig1_HTML.png)

[Full size image](https://link.springer.com/article/10.1057/s41270-023-00235-5/figures/1)

The hierarchy of key concepts in this study. AI is a general concept referring to (pseudo-)intelligent algorithms performing tasks that require intelligence. Machine learning is an application of AI. Unsupervised learning is a type of machine learning, of which clustering is the most common approach. Clustering, when applied to a customer dataset, then becomes the customer segmentation task

However, at the same time, firms struggle to understand these novel AI/ML methods and their implementation in everyday customer segmentation—for example, what algorithm to choose for their given data? Should they use one algorithm or many? How many customer segments should be created? How to evaluate the results? These motivational questions reveal a _practical_ research gap for customer segmentation research. Simultaneously, extant academic research lacks a synthesis of how customer segmentation is carried out in research studies, in terms of methods, parameters, evaluation, and so on—in other words, there is a _theoretical_ research gap. Taken together, these two gaps hinder the development of the body of knowledge around the practice and theory of customer segmentation, especially in the light of novel AI technologies (the most cited article assessing the use of clustering in marketing, by Punj and Stewart, is from 1983, so there is a need for an updated study). It becomes harder for firms and researchers to develop better approaches, evaluate them, and implement them if we do not know adequately well _how_ customer segmentation has been done in the past.

We address this knowledge gap by exploring the various customer segmentation methods used in business practices and then delve into the various AI/ML algorithms used for customer segmentation. Therefore, this research emphasizes algorithmic approaches to study what we term algorithmic customer segmentation (ACS). The central premise of our treatise is that AI/ML methods have become increasingly commonplace in marketing, specifically in customer segmentation. However, the extant academic literature lacks a holistic view of _how customer ACS is done_. Offering such a view is valuable for scholars (in terms of identifying patterns and gaps) and practitioners, as lessons from previous work are likely to offer a useful starting point for robust customer segmentation while helping to identify novel angles for future work in this domain.

Overall, this study aims to increase knowledge of customer segmentation research, and, more explicitly, the role of algorithms and AI in customer segmentation, toward understanding the theory and practice of ACS. In addition, based on our analysis of the extant literature, we offer a detailed and comprehensive agenda for future academic inquiry. To this end, we formulate specific research questions (RQs) that are addressed by a systematic literature review (SLR):

- **RQ1:** _What algorithms are typically used for customer segmentation?_ To understand ACS, we must familiarize ourselves with the different algorithms applied for the customer segmentation task in scholarly literature.

- **RQ2:** _Does customer segmentation typically use one or many algorithms? When many, what algorithms emerge in combination?_ The interaction among different algorithms poses an impactful question, as the field of customer segmentation migrates toward interactive systems that enable stakeholders to interact with the customer segments directly—thus, one algorithm might not be sufficient for more advanced systems (Jung et al. [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR57 "Jung, S.-G., J. Salminen, J. An, H. Kwak, and B.J. Jansen. 2018. Automatically Conceptualizing Social Media Analytics Data via Personas. In: Proceedings of the International AAAI Conference on Web and Social Media (ICWSM 2018), June 25, 2018. San Francisco, California, USA.")).

- **RQ3:** _How many customer segments are typically created?_ There could be two, three, or ten segments—but it is unclear what the optimal number of customer segments should be. Furthermore, this number will likely vary by the dataset in question (Salminen et al. [2022](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR39 "Salminen, J., K. Chhirang, S.-G. Jung, S. Thirumuruganathan, K.W. Guan, and B.J. Jansen. 2022. Big Data, Small Personas: How Algorithms Shape the Demographic Representation of Data-Driven User Segments. Big Data.                    https://doi.org/10.1089/big.2021.0177                                    .")). The current body of knowledge lacks systematic insights into how many customer segments are created in research, so we investigate this RQ.

- **RQ4:** _How is customer segmentation typically evaluated?_ ‘Evaluation’ means determining the quality of an algorithmic process; so, how well the customer segmentation worked (Thirumuruganathan et al. [2023](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR45 "Thirumuruganathan, S., N.A. Emadi, S. Jung, J. Salminen, D.R. Robillos, and B.J. Jansen. 2023. Will They Take This Offer? A Machine Learning Price Elasticity Model for Predicting Upselling Acceptance of Premium Airline Seating. Information & Management 60: 103759.")). This typically measures the segmentation algorithm’s ability to clearly distinguish one group of customers from another group. As evaluation is an essential part of the customer segmentation process, we investigate this RQ.

- **RQ5:** _What hyperparameters are used in algorithmic customer segmentation?_ A ‘hyperparameter’ refers to a parameter external to the model (Jansen et al. [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR13 "Jansen, B., S. Jung, and J. Salminen. 2021. The Effect of Hyperparameter Selection on the Personification of Customer Population Data. International Journal of Electrical and Computer Engineering Research.                    https://doi.org/10.53375/ijecer.2021.31                                    .")). The human (or an automated script) selects the “optimal” hyperparameters based on manual viewing or some technical measure. The most central hyperparameter for customer segmentation is the number of segments created (i.e., the segment size). However, there could be other relevant hyperparameters, which is why we are investigating this RQ.

- **RQ6:** _How frequently are subject matter experts used for evaluating the customer segments?_ The quality of customer segmentation can be ascertained using both automatic and manual means. ‘Automatic’ implies that the decision-making relies on technical metrics. However, at least of equal importance is exposing the customer segments to human decision-makers, e.g., managers, software developers, designers, and others that rely on customer segmentation as inputs in their decision-making. To this end, it is worthwhile to investigate how these stakeholders are involved in the customer segmentation process.


## Methodology

### Overview

We adopt the SLR methodology to discover and analyze pertinent existing studies. The SLR process provides a precise and reliable appraisal of the topic under examination, acknowledges existing flaws, and is less biased than typical judgment-based evaluations done by professionals in a specific field. In our approach, we adhered to the review procedure described by Kitchenham et al. ( [2009](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR19 "Kitchenham, B., O.P. Brereton, D. Budgen, M. Turner, J. Bailey, and S. Linkman. 2009. Systematic Literature Reviews in Software Engineering–a Systematic Literature Review. Information and Software Technology 51 (1): 7–15.")) and conducted the review in three sequential stages: (a) literature search, (b) assessment of the evidence base, and (c) analysis and synthesis of the findings.

### Literature search

In this study, we have included literature from various business domains, for instance, marketing and management. Further, as a high degree of relevant knowledge is available in the field of computer science, it is worthwhile to pursue knowledge developed there while concurrently examining its marketing implications (Mustak et al. [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR30 "Mustak, M., J. Salminen, L. Plé, and J. Wirtz. 2021. Artificial Intelligence in Marketing: Topic Modeling, Scientometric Analysis, and Research Agenda. Journal of Business Research 124: 389–404."); Salminen et al. [2019](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR38 "Salminen, J., V. Yoganathan, J. Corporan, B.J. Jansen, and S.-G. Jung. 2019. Machine Learning Approach to Auto-Tagging Online Content for Content Marketing Efficiency: A Comparative Analysis between Methods and Content Type. Journal of Business Research 101: 203–217.")). Predominantly, we focus on _customer_ segmentation, not _market_ segmentation. Although these two concepts appear similar, they are not: Market segmentation is the process of dividing a market into different subgroups of consumers with similar needs, wants, behavior, or other characteristics. In turn, customer segmentation is the process of dividing customers into groups based on their qualities, attributes, and behaviors. So, the former deals with the _overall_ market and the latter with the _specific, current_ customer base.

To identify relevant literature, we used four prominent academic databases: Web of Science (WoS), Emerald Insight, ACM Digital Library, and ABI/INFORM Collection (ProQuest). WoS is the most comprehensive generic database, encompassing more than 12,000 high-impact journals and research articles from more than 3,300 publishers. The Emerald Insight and ABI/INFORM Collection (ProQuest) are also similar—as generic databases, they offer a collection of many relevant journals and scientific articles. The ACM Digital Library is a specialized database focusing on technical disciplines and thus helps uncover the articles focused on technical aspects of customer segmentation. Combined, these four databases offer balanced coverage of the existing literature on customer segmentation from multiple scientific disciplines.

We conducted detailed searches in each of the four databases. We did not want to pre-limit the searches with highly specific keywords and narrow terms, which may exclude crucial articles, as those articles may address the very same topic but use different terms. Rather, to identify a wide range of publications that may shed light on customer segmentation, we used only the following keywords: “customer segmentation\*”, “user segmentation\*”, and “audience segmentation\*” (‘\*’ denotes plural forms) and identified all the associated articles. However, in the case of WoS, after the initial search, which resulted in 574 entries, we kept articles from the fields of business and computer science (as categorized by WoS) and excluded articles from other fields that we deemed outside the scope of this study. These fields included, for example, materials science, physics, chemistry, or integrative complementary medicine. The specific search details, along with the assessment of the evidence base, are presented in Table [1](https://link.springer.com/article/10.1057/s41270-023-00235-5#Tab1).

**Table 1 Details of literature searches for this study**

[Full size table](https://link.springer.com/article/10.1057/s41270-023-00235-5/tables/1)

### Assessment of the evidence base

We carried out the article screening in two stages. In the first stage, we focused on “hygiene factors” (see Table [2](https://link.springer.com/article/10.1057/s41270-023-00235-5#Tab2)), such as removing duplicates, articles with missing information, those written in a language other than English, and articles published before the year 2000, as we considered the past 20 years or so to contain most relevant work for our research purpose. Figure [2](https://link.springer.com/article/10.1057/s41270-023-00235-5#Fig2) illustrates the general interest in segmentation among studies in or related to marketing.

**Table 2 Inclusion/exclusion steps applied in the first stage of screening, along with the number of articles remaining after each step**

[Full size table](https://link.springer.com/article/10.1057/s41270-023-00235-5/tables/2)

**Fig. 2**

![Fig. 2](https://media.springernature.com/lw685/springer-static/image/art%3A10.1057%2Fs41270-023-00235-5/MediaObjects/41270_2023_235_Fig2_HTML.png)

[Full size image](https://link.springer.com/article/10.1057/s41270-023-00235-5/figures/2)

Approximate search results when searching Google Scholar for \[+ segmentation + marketing\]. The results indicate a general increase in interest in segmentation among studies in or related to marketing. The vertical line (the year 2000) indicates our sample’s cut-off year

After the first round of screening, we checked the remaining 204 articles based on their contents, i.e., assessing their relevance to our research purpose. We found that 32 (15.7%) articles were irrelevant to our research purpose (e.g., they were literature reviews or did not use empirical data to conduct customer segmentation). This reduction left us with 172 (84.3%) articles, 134 (77.9%) of which contained algorithm-based approaches to customer segmentation (i.e., representing ACS), while 38 (22.1%) articles applied non-algorithm-based customer segmentation (see Fig. [3](https://link.springer.com/article/10.1057/s41270-023-00235-5#Fig3)). In our analysis, for RQ1-2 and RQ4-RQ5, we focus on the 134 articles that were algorithm-based. For RQ3 and RQ6, we focus on the full 172 articles that passed the pre-screening as these RQs do not require the articles to be algorithm-based.

**Fig. 3**

![Fig. 3](https://media.springernature.com/lw685/springer-static/image/art%3A10.1057%2Fs41270-023-00235-5/MediaObjects/41270_2023_235_Fig3_HTML.png)

[Full size image](https://link.springer.com/article/10.1057/s41270-023-00235-5/figures/3)

Research process leading to article coding. Essentially, this took place in four stages: Screening, Relevance Assessment, Algorithm Assessment, and Data Extraction

### Article coding

After the screening, we extracted information from the articles to address our RQs using a data extraction sheet. The information fields were designed to correspond with the RQs (see Table [3](https://link.springer.com/article/10.1057/s41270-023-00235-5#Tab3)). The coding was carried out by one researcher, with another researcher verifying the quality of the coding outcomes by randomly investigating a sample of 20 articles. This inspection was carried out successfully and revealed that the data was coded following the guidelines in Table [3](https://link.springer.com/article/10.1057/s41270-023-00235-5#Tab3). The results (see Section " [RQ2: does customer segmentation typically use one or many algorithms?](https://link.springer.com/article/10.1057/s41270-023-00235-5#Sec9)") were obtained by carefully reviewing the full-text articles.

**Table 3 Data extracted from the research articles**

[Full size table](https://link.springer.com/article/10.1057/s41270-023-00235-5/tables/3)

## Results

### RQ1: What algorithms are typically used for customer segmentation?

After a thorough overview of the ACS literature, _we identified 46 different algorithms used for customer segmentation_, whose usage frequencies are illustrated in Fig. [4](https://link.springer.com/article/10.1057/s41270-023-00235-5#Fig4).

**Fig. 4**

![Fig. 4](https://media.springernature.com/lw685/springer-static/image/art%3A10.1057%2Fs41270-023-00235-5/MediaObjects/41270_2023_235_Fig4_HTML.png)

[Full size image](https://link.springer.com/article/10.1057/s41270-023-00235-5/figures/4)

Frequency chart for the algorithms used. The _y_-axis represents the name of the algorithms used for customer segmentation, and the x-axis shows the frequency, i.e., the number of times each algorithm has been used in the literature for customer segmentation. The ‘Other’ class contains all the algorithms that were used only once

As can be seen in Fig. [4](https://link.springer.com/article/10.1057/s41270-023-00235-5#Fig4), K-means clustering is the most frequently used algorithm, as it is used 27 times (20.1%) in our sample of reviewed literature. Other prominent algorithms include variants of K-means clustering with a frequency of 10 (7.5%), fuzzy algorithms, and latent class analysis models are all used 8 (6.0%) times, respectively. The recency-frequency-monetary gain (RFM) and its variants have been used 6 (4.5%) times, while Self-Organizing Maps (SOM) and Genetic Algorithms (GA) have been used three times (2.25%) each. Other algorithms, for example, the Louvain algorithm, Ward’s algorithm, and hierarchical clustering algorithms have been used two to three times varyingly. Furthermore, some algorithms have only been used once, indicating that these approaches may not have been thoroughly explored in the context of customer segmentation. Examples include direct grouping iterative merge and consistency-based clustering algorithms, suggesting that there is scope for further nuanced research in these areas.

_Overall, the results highlight the wide range of algorithms available for customer segmentation and the need for further exploration and comparison of these methods to determine the most effective approach for different business scenarios._

### RQ2: Does customer segmentation typically use one or many algorithms?

After a thorough overview of the ACS literature, it appears that in most cases, researchers have utilized one algorithm for customer segmentation (i.e., in roughly 80% of them). However, there are also instances where multiple algorithms have been combined for more effective results. For example, K-means clustering, SOM, and RFM approaches have been applied in combination with other approaches (see Table [4](https://link.springer.com/article/10.1057/s41270-023-00235-5#Tab4)).

**Table 4 Examples of combining customer segmentation algorithms**

[Full size table](https://link.springer.com/article/10.1057/s41270-023-00235-5/tables/4)

In general, the employment of multiple algorithms in combination may aid in addressing the shortcomings specific to each algorithm and may also help in the creation of more robust and distinct customer segments. Furthermore, technical reasons hailing from the domain of applied ML can explain the use of multiple algorithms. It is expected that AI/ML research studies compare and evaluate multiple algorithms for one task; this involves experimenting with combinations of different algorithms and calculating the accuracy/performance among them. This is often done by conducting an ablation study (Symeonidis et al. [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR44 "Symeonidis, S., D. Effrosynidis, and A. Arampatzis. 2018. A Comparative Evaluation of Pre-Processing Techniques and Their Interactions for Twitter Sentiment Analysis. Expert Systems with Applications 110: 298–310.")). An ablation study is a form of experimental design used to study the effect of removing a specific part or feature of a model on its overall performance, typically used in the field of ML and AI. It can involve removing individual components of a larger model or system, a subset of data features, or hyperparameters to see how they affect the accuracy, cost, and other metrics of the ML model. Similarly, the researchers developing new customer segmentation algorithms are required to demonstrate the value of their approach; for this reason, algorithms are often compared against one another.

### RQ3: How many customer segments are typically created?

Our analyses show that various numbers of customer segments have been suggested/created by researchers based on the application area and/or target market and objectives of the research (see Fig. [5](https://link.springer.com/article/10.1057/s41270-023-00235-5#Fig5)). Most commonly, researchers have suggested/created _four_ customer segments ( _n_ = 32, 21.2%). On average, researchers created 5.7 segments (SD = 3.9). Interestingly, no study produced more than 20 customer segments (apart from the outlier study mentioned in Fig. [1](https://link.springer.com/article/10.1057/s41270-023-00235-5#Fig1) caption), while the lowest number of segments produced was one (in this particular study, the researchers applied a decision-rule algorithm to discover the most ideal customer type (Lee, J. H. & Park, 2005)). Interestingly, more than half ( _n_ = 103, 68.2%) of the studies generated between two and five segments (see Fig. [5](https://link.springer.com/article/10.1057/s41270-023-00235-5#Fig5)). Furthermore, 92.1% of the studies generated ten or fewer segments.

**Fig. 5**

![Fig. 5](https://media.springernature.com/lw685/springer-static/image/art%3A10.1057%2Fs41270-023-00235-5/MediaObjects/41270_2023_235_Fig5_HTML.png)

[Full size image](https://link.springer.com/article/10.1057/s41270-023-00235-5/figures/5)

Number of customer segments created in research articles. The numbers are based on 151 articles (87.7% of the total 172) that expressed the number of segments created. In the case the researchers presented multiple segmentations with different numbers (e.g., 7, 7, 8), as was sometimes the case when experimenting with multiple algorithms or datasets, we have taken the average of the reported numbers and rounded it either up or down based on standard rounding rules (e.g., 7, 7, 8 would yield the average of 7.3 which rounds to the segment size of 7). Twenty-one articles (12.2%) did not report the segment size. Also, we omitted one outlier article from the analysis, as the researchers created 1209 and 8984 segments from two datasets, respectively (Böttcher et al. [2009](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR4 "Böttcher, M., M. Spott, D. Nauck, and R. Kruse. 2009. Mining Changing Customer Segments in Dynamic Markets. Expert Systems with Applications 36 (1): 155–164."))

Typically, the number of segments is not determined beforehand but in a _data-driven way_ (Hiziroglu [2013](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR10 "Hiziroglu, A. 2013. A Neuro-Fuzzy Two-Stage Clustering Approach to Customer Segmentation. Journal of Marketing Analytics 1 (4): 202–221."); Hong and Kim [2012](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR11 "Hong, T., and E. Kim. 2012. Segmenting Customers in Online Stores Based on Factors That Affect the Customer’s Intention to Purchase. Expert Systems with Applications 39 (2): 2127–2131.")), which means determining the segment size based on quantitative evaluation metrics (i.e., the number of segments is such that best fits the data based on an evaluation metric when experimentally varying the segment size). For example, the researchers may attempt multiple numbers for _k_ where _k_ indicates the number of segments, and then visualize at what number of _k_ the obtained information noticeably decreases—the so-called elbow method where elbow indicates this decrease (Syakur et al. [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR61 "Syakur, M.A., B.K. Khotimah, E.M.S. Rochman, and B.D. Satoto. 2018. Integration K-Means Clustering Method and Elbow Method for Identification of the Best Customer Profile Cluster. In: IOP Conference Series: Materials Science and Engineering, 2018. vol. 336, 012017. IOP Publishing.")). So, the number of clusters is neither random nor determined a priori, but all the reviewed articles used some quantitative metrics/criteria to validate or choose the number of segments.

### RQ4: How is customer segmentation typically evaluated?

In ACS, the evaluation of the customer segments is crucial for the effectiveness of the segmentation process. As ACS tends to be an unsupervised ML task (where there is no single “correct” value for a segment, but instead, the algorithm aims to organize the data into groups, i.e., segments), accuracy is used more rarely in ACS than in other types of ML tasks, including supervised learning tasks such as prediction. Hence, there are several measures and criteria that researchers have used to evaluate the quality of customer segments. Overall, we identified 14 different metrics for evaluating customer segmentation outputs, of which six (42.9%) focused on statistical indicators and eight (57.1%) focused on distances and/or similarity calculation (see Table [5](https://link.springer.com/article/10.1057/s41270-023-00235-5#Tab5)). We discuss the metrics in alphabetical order.

**Table 5 Segmentation evaluation metrics**

[Full size table](https://link.springer.com/article/10.1057/s41270-023-00235-5/tables/5)

_Accuracy_ (ACC) is used to evaluate the quality of segments, i.e., how well “unseen” or new members (customers) the segmentation algorithm can allocate to the correct segment (Wu, S. et al., 2021). ACC is typically calculated by dividing the number of correct values by the total number of predicted values. The use of ACC requires that there are ‘ground truth’ values or labels against which the predictive ability of an algorithm is compared.

The _Adjusted Rand Index_ (ARI) measures the similarity between two segmentations (Xu, X. et al., 2007). The ARI considers the random chance that objects between the segmentations might be similar. It compares object pairs in two sets of segments and computes the difference between the observed agreement and the expected agreement under random labeling. The value of -1 indicates perfect dissimilarity, and + 1 indicates perfect similarity. So, the higher the ARI, the more similar the two customer segmentations are.

The _Analysis of Variance_ (ANOVA) test is a statistical method used to test the difference in means between two or more groups. In customer segmentation, ANOVA can test for significant numerical differences in customer characteristics between the segments (Ballestar et al. [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR1 "Ballestar, M.T., P. Grau-Carles, and J. Sainz. 2018. Customer Segmentation in E-Commerce: Applications to the Cashback Business Model. Journal of Business Research 88: 407–414."); Kashwan and Velu [2013](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR17 "Kashwan, K.R., and C. Velu. 2013. Customer Segmentation Using Clustering and Data Mining Techniques. International Journal of Computer Theory and Engineering 5: 856–861.")).

The _Average Clustering Error_ (ACE) evaluates the average distance between data points within each segment (Manjunath and Kashef [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR28 "Manjunath, Y.S.K., and R.F. Kashef. 2021. Distributed Clustering Using Multi-Tier Hierarchical Overlay Super-Peer Peer-to-Peer Network Architecture for Efficient Customer Segmentation. Electronic Commerce Research and Applications 47: 101040.")). The ACE is calculated by taking the average of the sum of the distances from each point in the dataset to its closest segment center. It indicates how well the segmentation algorithm has been able to group points with similar characteristics. If the ACE is low, this indicates an effective segmentation algorithm.

The _Bayesian Information Criterion_ (BIC) is a measure used for model selection and comparison, including in segmentation (Bhade et al. [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR55 "Bhade, K., V. Gulalkari, N. Harwani, and S.N. Dhage. 2018. A Systematic Approach to Customer Segmentation and Buyer Targeting for Profit Maximization. In: 2018 9th International Conference on Computing, Communication and Networking Technologies (ICCCNT), 1–6, 2018. IEEE.")). To calculate the BIC, the log-likelihood of the segmentation model is adjusted by penalizing complex models. The BIC score is obtained by subtracting the penalty term from the maximum log-likelihood, where a lower BIC value indicates a better-fitting and more parsimonious model.

The _Calinski-Harabasz Index_ (CHI) evaluates the separation between the segments and the compactness within each segment (Kandeil et al. [2014](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR58 "Kandeil, D.A., A.A. Saad, and S.M. Youssef. 2014. A Two-Phase Clustering Analysis for B2B Customer Segmentation. In: 2014 International Conference on Intelligent Networking and Collaborative Systems, 221–228, 2014. IEEE.")). The CHI is calculated by comparing the within-segment dispersion to the between-segment dispersion. A higher value indicates that the segments are well-defined and that the dataset has been well-split into distinct segments.

The _Davies Bouldin Index_ (DBI) assesses the similarity between the segments based on the distance between their centroids (i.e., midpoints). The lower the DBI score, the better the segmentation result, indicating that the segments are more compact and less scattered (Aryuni et al. [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR54 "Aryuni, M., E.D. Madyatmadja, and E. Miranda. 2018. Customer Segmentation in XYZ Bank Using K-Means and K-Medoids clustering. In: 2018 International Conference on Information Management and Technology (ICIMTech), 412–416, 2018. IEEE.")). The DBI penalizes algorithms that produce segments with a wide variety of sizes and shapes, with larger diameters relative to the separation between the segments.

The _Dunn Index_ (DI) evaluates the separation between the segments and the compactness within each segment (Khajvand and Tarokh [2011](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR18 "Khajvand, M., and M.J. Tarokh. 2011. Estimating Customer Future Value of Different Customer Segments Based on Adapted RFM Model in Retail Banking Context. Procedia Computer Science 3: 1327–1332.")). The calculation of the DI is done by taking the ratio of the minimum intra-segment distance to the maximum inter-segment distance. A higher value indicates that the segments are better separated.

The _Fukuyama and Sugeno_ method (FS) is an approach to evaluate segmentation results based on fuzzy sets and fuzzy logic. The FS involves assigning membership values to data points indicating their degree of belongingness to each segment. The process incorporates expert knowledge through the formulation of fuzzy rules, which guide the decision-making process. These membership values are then used to calculate a validity index, which measures the quality of the segmentation by considering their compactness and separation (Nemati et al. [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR31 "Nemati, Y., A. Mohaghar, M.H. Alavidoost, and H. Babazadeh. 2018. A CLV-Based Framework to Prioritize Promotion Marketing Strategies—Case Study of Telecom Industry. Iranian Journal of Management Studies.                    https://doi.org/10.22059/ijms.2018.242492.672837                                    .")).

The _Mann–Whitney rank test_ (MW) is a non-parametric statistical test used to compare the difference in the median between two groups. In customer segmentation, the MW can be used to test whether there are significant differences in customer characteristics between the different segments (Jiang and Tuzhilin [2009](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR14 "Jiang, T., and A. Tuzhilin. 2009. Improving Personalization Solutions through Optimal Segmentation of Customer Bases. IEEE Transactions on Knowledge and Data Engineering 21 (3): 305–320.")).

The _Silhouette Index_ (SI) is a metric used to measure how well-defined a segment is and how strongly a data point is assigned to its associated segment (Dzulhaq et al. [2019](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR56 "Dzulhaq, M.I., K.W. Sari, S. Ramdhan, and R. Tullah. 2019. Customer Segmentation Based on RFM Value Using K-Means Algorithm. In: 2019 Fourth International Conference on Informatics and Computing (ICIC), 1–7, 2019. IEEE.")). The SI ranges from − 1 to 1, with a score of 1 indicating that the data point is perfectly matched to its own segment, a score of − 1 indicating that the data point is more closely associated with another segment, and a score close to 0 indicating that the data point does not have a clear segment assignment. The SI is calculated by taking the average of the difference between the data point’s own segment similarity and the lowest segment similarity with the other segments.

The _Total Clustering Effectiveness_ (TCE) is a metric used by Lu and Wu ( [2009](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR26 "Lu, T.-C., and K.-Y. Wu. 2009. A Transaction Pattern Analysis System Based on Neural Network. Expert Systems with Applications 36 (3, Part 2): 6091–6099.")). The TCE combines an inter-cluster correlation indicator and an inner density indicator. The numerator represents the sum of densities for two segments, where a higher value indicates better performance. The denominator represents the correlation coefficient between the two segments, with a smaller value indicating better results. Incorporating both values, a higher TCE indicates better results.

The _Validity Index_ (VI) is a measure that evaluates the quality of the segmentation result based on specific criteria (Pramono et al. [2019](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR59 "Pramono, P.P., I. Surjandari, and E. Laoh. 2019. Estimating Customer Segmentation Based on Customer Lifetime Value Using Two-Stage Clustering Method. In: 2019 16th International Conference on Service Systems and Service Management (ICSSSM), 1–5, 2019. IEEE.")). These criteria can include factors such as intra-segment cohesion (compactness), inter-segment separation, or the overall structure of the segments. VIs provide a numerical score or value that indicates the goodness of fit of the segmentation solution, with higher values suggesting better quality or validity. Different VIs employ distinct formulas or methodologies to capture different aspects of segmentation performance.

Finally, the _Xie-Beni Index_ (XBI) is a validity index used to evaluate the quality of segmentation results (Munusamy and Murugesan [2020](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR29 "Munusamy, S., and P. Murugesan. 2020. Modified Dynamic Fuzzy C-Means Clustering Algorithm—Application in Dynamic Customer Segmentation. Applied Intelligence 50 (6): 1922–1942.")). The XBI quantifies the trade-off between segment compactness and separation by calculating the ratio of the sum of squared distances between data points and segment centroids to the product of the segment compactness and the number of data points. A lower value indicates better segmentation with tighter and well-separated segments.

_A few conclusions can be made. First, the metrics can be divided into statistics- and separation-focused metrics, with the latter being slightly more typical. Second, statistics-focused metrics emphasize segment-to-segment differences, while separation-focused metrics emphasize low intra-segment distance (i.e., compactness) and high inter-segment distance (i.e., separation). Third, customer segmentation evaluation is centered on using metrics derived from clustering practices, rather than using metrics especially tailored to customer segmentation, business outcomes, or ecological validity._

### RQ5: What hyperparameters are used for algorithmic customer segmentation?

In ML, a hyperparameter refers to a configuration setting (i.e., a numeric value) that is external to the model itself and is typically set before the learning process begins (Jansen et al. [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR13 "Jansen, B., S. Jung, and J. Salminen. 2021. The Effect of Hyperparameter Selection on the Personification of Customer Population Data. International Journal of Electrical and Computer Engineering Research.                    https://doi.org/10.53375/ijecer.2021.31                                    .")). Unlike model parameters, which are learned from the training data, hyperparameters are predefined choices (range of values when experimenting with multiple hyperparameter values) that affect the model’s performance and behavior. These parameters can include things like the learning rate, the number of hidden layers in a neural network, or the regularization parameter. Selecting appropriate hyperparameter values is crucial for achieving optimal model performance, and it often involves experimentation, trial and error, or using techniques like grid search or Bayesian optimization (Jansen et al. [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR13 "Jansen, B., S. Jung, and J. Salminen. 2021. The Effect of Hyperparameter Selection on the Personification of Customer Population Data. International Journal of Electrical and Computer Engineering Research.                    https://doi.org/10.53375/ijecer.2021.31                                    .")).

In our review, out of the 169 studies that offered information about hyperparameters, more than four out of every five articles ( _n_ = 138, 81.7%) applied only segment size as a hyperparameter, while less than one out of five ( _n_ = 31, 18.3%) applied additional hyperparameters. In ACS, the algorithms may combine technical and business hyperparameters, with the technical parameters stemming from the inputs required by the algorithm (most commonly, the number of segments to create, i.e., the segment size and the distance measure—how the distance between the segments is calculated) to perform its computation and the latter arising from the particular business scenario the segmentation aims to address. For example, Munusamy and Murugesan ( [2020](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR29 "Munusamy, S., and P. Murugesan. 2020. Modified Dynamic Fuzzy C-Means Clustering Algorithm—Application in Dynamic Customer Segmentation. Applied Intelligence 50 (6): 1922–1942.")) performed customer segmentation based on the Fuzzy C-mean clustering algorithm and defined U matrix parameters to make their data compatible with the Fuzzy C-mean algorithm.

In contrast, Peker et al. ( [2017](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR34 "Peker, S., A. Kocyigit, and P.E. Eren. 2017. A Hybrid Approach for Predicting Customers’ Individual Purchase Behavior. Kybernetes 46 (10): 1614–1631.")) formulated a hybrid approach for customer behavior prediction and used many AI/ML algorithms, including Neural Networks, SVM, Decision Tree, and Radial Basis Functions that make use of different hyperparameters, for instance, cost, gamma, number of hidden layers, weights, number of leaf nodes and number of trees, etc. In another contribution, the authors formulated a hybrid big data model for analyzing customer patterns in an integrated supply chain network (Wang et al. [2020](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR47 "Wang, S.-C., Y.-T. Tsai, and Y.-S. Ciou. 2020. A Hybrid Big Data Analytical Approach for Analyzing Customer Patterns through an Integrated Supply Chain Network. Journal of Industrial Information Integration 20: 100177.")). They applied Linked Based Bloom Filters (LBF) that served as parameter functions directly linked with customer segmentation. Liu et al. ( [2009](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR25 "Liu, D.-R., C.-H. Lai, and W.-J. Lee. 2009. A Hybrid of Sequential Rules and Collaborative Filtering for Product Recommendation. Information Sciences 179 (20): 3505–3519.")) formulated a hybrid approach for a product recommendation that directly relates to customer segmentation. Their proposed approach used learning rate, grid structure, and distance normalization as hyperparameters.

Although these parameters are not directly linked with customer segmentation, they contribute to the overall segmentation process in terms of providing a method for ascertaining a _technically optimal_ number (and structure) of the segments. In turn, the business parameters aim to provide more information about the domain-specific business context. These may include the likes of Length of customer involvement (L) and Periodicity (P) that were applied by Nemati et al. ( [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR31 "Nemati, Y., A. Mohaghar, M.H. Alavidoost, and H. Babazadeh. 2018. A CLV-Based Framework to Prioritize Promotion Marketing Strategies—Case Study of Telecom Industry. Iranian Journal of Management Studies.                    https://doi.org/10.22059/ijms.2018.242492.672837                                    .")). Zhu et al. ( [2015](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR63 "Zhu, B., C. He, and X. Jiang. 2015. A Consistency-Based Validation for Data Clustering—IOS Press [Online].                    https://content.iospress.com/articles/intelligent-data-analysis/ida727                                    . Accessed 3 Mar 2023.")) applied Profitability ( _prof_), Accuracy ( _acc_), and lead time as hyperparameters that contribute to customer segmentation in demand fulfillment of customers in case of supply shortage. Wu and Liu ( [2020](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR50 "Wu, T., and X. Liu. 2020. A Dynamic Interval Type-2 Fuzzy Customer Segmentation Model and Its Application in E-Commerce. Applied Soft Computing 94: 106366.")) incorporated group preferences and linguistics parameters into their Type 2 fuzzy customer segmentation models and concluded that these parameters greatly affect the customer segmentation task.

_Overall, the hyperparameters applied by most articles stem from the standard/default hyperparameters used by these algorithms in any dimensionality reduction context, of which customer segmentation is a special case._

### RQ6: How frequently are subject matter experts used for evaluating the customer segments?

In this study, we encountered only seven cases (4.1%) where subject matter experts were used to evaluate the quality of customer segmentation and provide expert opinions. In other words, it is a rare, perhaps too rare, practice to invite stakeholders and subject matter experts to validate the results of the customer segmentation process in academic research articles. Out of the rare examples that do exist, Nemati et al. ( [2018](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR31 "Nemati, Y., A. Mohaghar, M.H. Alavidoost, and H. Babazadeh. 2018. A CLV-Based Framework to Prioritize Promotion Marketing Strategies—Case Study of Telecom Industry. Iranian Journal of Management Studies.                    https://doi.org/10.22059/ijms.2018.242492.672837                                    .")) formulated a customer lifetime value (CLV) approach for prioritizing marketing strategies in the telecom industry. The experts were first asked through a questionnaire to provide different parameters for the said tasks. Once the segmentation was done, the experts were again consulted to evaluate and validate the results. Safari et al. ( [2016](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR37 "Safari, F., N. Safari, and G.A. Montazer. 2016. Customer Lifetime Value Determination Based on RFM Model. Marketing Intelligence & Planning 34: 446–461.")) formulated an RFM-based CLV determination approach that performs customer segmentation based on the RFM values. To do so, subject matter experts were asked through a questionnaire, and once the segmentation was carried out, a total number of 16 experts expressed their opinions about the accuracy of the segments.

Similarly, Sun et al. ( [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR43 "Sun, Z.-H., T.-Y. Zuo, D. Liang, X. Ming, Z. Chen, and S. Qiu. 2021. GPHC: A Heuristic Clustering Method to Customer Segmentation. Applied Soft Computing 111: 107677.")) introduced a heuristic approach to customer segmentation. The experimental results show that the customer segmentation output by their proposed method was consistent with the customer segmentation result given by experts. Manidatta et al. ( [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR27 "Manidatta, R., M. Ray, K. Muduli, A. Banaitis, and A. Kumar. 2021. Integrated Approach of Fuzzy Multi-Attribute Decision Making and Data Mining for Customer Segmentation. E a M: Ekonomie a Management 24: 174–188.")) introduced an integrated approach for customer segmentation and evaluated their approach through experiments. They collected responses from nine subject matter experts from the Indian retail industry regarding their perception of the relative importance of four CLV criteria and evaluated the weights of each criterion using fuzzy AHP. Transaction data for 18 months was analyzed to segment 1,600 customers into eight segments using the fuzzy c-means clustering analysis technique. The segmentation results of their proposed integrated method were further validated by the nine experts from the Indian retail industry.

In another study, Li et al. ( [2011](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR24 "Li, K.J., D.K.H. Fong, and S.H. Xu. 2011. Managing Trade-in Programs Based on Product Characteristics and Customer Heterogeneity in Business-to-Business Markets. Manufacturing & Service Operations Management 13 (1): 108–123.")) formulated an agglomerative clustering-based approach for customer segmentation, and as a result of their proposed approach, the customer was segmented into four distinct groups/segments. Subject experts validated and evaluated the experimental results for customer segmentation by their approach (Li et al. [2011](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR24 "Li, K.J., D.K.H. Fong, and S.H. Xu. 2011. Managing Trade-in Programs Based on Product Characteristics and Customer Heterogeneity in Business-to-Business Markets. Manufacturing & Service Operations Management 13 (1): 108–123.")). Lee and Cho ( [2021](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR22 "Lee, Y., and S. Cho. 2021. User Segmentation via Interpretable User Representation and Relative Similarity-Based Segmentation Method. Multimedia Systems 27 (1): 61–72.")) formulated a customer segmentation approach based on the Leuven algorithm. To verify and validate the segmentation results of their proposed approach, they consulted a subject matter expert, and the algorithm determined the modularity for ten segments, which was the same number of segments identified by the domain expert. Warner ( [2019](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR48 "Warner, L.A. 2019. Using Homeowners’ Association Membership to Define Audience Segments for Targeted Local Social Marketing Interventions: Implications From a Statewide Study. Social Marketing Quarterly 25 (4): 291–307.")) conducted a study on audience segmentation using a survey approach. Before conducting the study, a seven-member expert panel was asked to review the instrument and provide their expert opinion on the number of segments created. The domain expert team validated the audience segmentation results.

_Thus, our analysis indicates that most often, the results of customer segmentation (including both algorithmic and non-algorithmic customer segmentation research) are not validated using external feedback, but the authors tend to rely on technical evaluation metrics to justify the quality of their work._ This practice likely stems from the ML research tradition, in which metrics such as accuracy, precision, recall, etc., are used to evaluate the performance of an algorithm (Bell [2014](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR3 "Bell, J. 2014. Machine Learning: Hands-on for Developers and Technical Professionals, 1st ed. Hoboken: John Wiley & Sons."); Kühl et al. [2022](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR20 "Kühl, N., M. Schemmer, M. Goutier, and G. Satzger. 2022. Artificial Intelligence and Machine Learning. Electronic Markets 32 (4): 2235–2244.")), rather than “subjective” human feedback. _However, when they are used, most typically, multiple subject matter experts participate in evaluating the created segments._

## Discussion

### Study highlights

Here, we discuss the highlights of our findings.

_We identified 46 different algorithms applied by researchers for customer segmentation_. This finding highlights not only the methodological (algorithmic) plurality within customer segmentation studies but also the influence of the current AI and ML technologies in this domain, as these algorithms overwhelmingly stem from the ML research tradition.

_Most of the reviewed studies used one segmentation algorithm, making multi-algorithm customer segmentation a minority endeavor_. The promise in multi-algorithms customer segmentation is that, in theory, it is better able to handle the plurality of segmentation criteria and be more responsive to organizational requirements for changing the segmentation parameters with updating business requirements.

In ACS, the number of segments is not pre-assigned, but it is inductively determined based on quantitative evaluation metrics. _On average, researchers create 5.7 customer segments per study (SD_ = _3.9, Mode_ = _4, Median_ = _5)_. So, even though creating four segments is the most common, the number of segments created varies substantially across the reviewed studies. No analyzed study created more than 20 segments (Min = 1, Max = 20).

_Few studies explicitly define the concept of customer segmentation_. Instead, the concept is often treated implicitly, as “everyone knows what it is”. This conceptual vagueness can hinder the development of scientific advances in customer segmentation, as ‘customer segmentation’ might not be a similar task to other clustering tasks \[the (dis)similarity of customer segmentation to other clustering tasks remains unaddressed in the literature\].

_Research outlines numerous ‘theoretical’ use cases and benefits for customer segmentation_. These benefits, ranging from pricing to targeting and personalization of offerings and messaging, emphasize the central role of customer segmentation as a key business application of AI and ML technologies. Concurrently, few studies show empirical evidence of these benefits in organizational use cases or systems (i.e., ecological validity).

_There is no one set of customer segmentation criteria, but the studies vastly vary in terms of the segmentation criteria applied_. In fact, no two studies may have a single criterion (i.e., customer attribute) in common. This plurality of criteria partially explains the algorithmic or methodological plurality, as different criteria represent different data types that require distinct preprocessing and analysis approaches to apply the algorithms. Therefore, it is unlikely that we would end up in a situation where only one (or even a few) algorithms would cover all use cases for customer segmentation.

_Researchers developing novel customer segmentation algorithms tend to see customer segmentation as a computational task_. This viewpoint is visible in how algorithms are used, studies are structured, and outputs are evaluated. Machine learning studies follow a particular paradigm of benchmark comparison, which may explain why a large portion of literature puts less emphasis on conceptual and theoretical aspects of customer segmentation and instead focuses on it as a technical problem or ‘task’.

_We identified 14 unique evaluation metrics for the quality of customer segmentation, all technical_. The many metrics are the consequence of multiple algorithms: because the statistical and mathematical properties of different algorithms vary, one metric cannot be applied to evaluate the (internal) success of the modeling task. However, it would be valuable to have more centralized evaluation metrics for customer segmentation success; as the internal evaluation is affected by computational specificities, perhaps researchers could shift their focus on external (ecological) evaluation metrics, focusing on the business outcomes and the customer dynamics of applying customer segmentation rather than the segments’ creation process.

_Business orientation separates customer segmentation from other clustering tasks_. In addition to ML-dependent technical hyperparameters (e.g., number of segments, distance function), researchers utilize business-specific hyperparameters (e.g., length of customer involvement, profitability) for customer segmentation inputs. However, most studies reviewed (82%) only applied segment size as the hyperparameter.

Considering the historical development of the use of clustering in marketing, the post-2000 sample we analyzed shows some progress compared to the previous analysis made by Punj and Stewart in 1983. Specifically, the researchers indicated then that there is a “failure of numerous authors in the marketing literature to specify what clustering method is being used.” (p. 134). In our more recent sample, this condition does not take place as the authors are more explicit on the precise method being used—so, there has been progress in the reporting of clustering details in marketing work.

However, our results confirm the fundamental challenges of clustering (segmentation) as stated by Punj and Stewart ( [1983](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR35 "Punj, G., and D.W. Stewart. 1983. Cluster Analysis in Marketing Research: Review and Suggestions for Application. Journal of Marketing Research 20 (2): 134–148.")): “choice of an appropriate metric, selection of variables, cross- validation, and external validation” (p. 134). As then, these challenges remain topical and fundamentally unresolved. There are many metrics to choose from. The selection of segmentation variables is arbitrary. Cross-validation and external validation (ecological validity) are difficult to execute and thus often omitted. So, the fundamental nature of segmentation has not changed with the novel AI technologies, at least yet.

Interestingly, there can be seen as a continuation of knowledge. That is, the analysis by Punj and Stewart from 1983 (see their Table [4](https://link.springer.com/article/10.1057/s41270-023-00235-5#Tab4) on pp. 141–142) indicates K-Means as one of the most popular algorithms. Forty years later, this algorithm still maintains its position as the leading segmentation algorithm. We can interpret this finding as either proof of its superiority in this problem, or as traditionalism. However, either way, the conclusion remains that the novel AI-based approaches have not been able to replace the “old AI” approaches, at least when it comes to K-Means.

In addition to the above highlights, in the following subsection, we provide a taxonomy of algorithms for customer segmentation.

### Central goals and directions for future research

From our review, there are multiple avenues for future research to advance customer segmentation research. In the following, we outline seven key goals (KG) for future work:

- _KG01: Providing taxonomies of algorithms and metrics._ There is a need for conceptual frameworks, classifications, and taxonomies that help address the undeniable plurality of algorithms in the domain of customer segmentation research, which includes at least (a) algorithm selection plurality, (b) segmentation criteria plurality, (c) hyperparameter plurality, and (d) evaluation metric plurality. Our taxonomy of algorithms for customer segmentation provides a starting point and an example of outputs that can help address this gap. We invite other researchers to provide conceptual work (not only empirical!) that systemically categorizes the extant work on customer segmentation. Additionally, consensus on some fundamental concepts is much needed—for instance, how can ‘high-quality’ customer segmentation be distinguished from ‘low-quality’ customer segmentation? Should we focus on the quality of the process, the quality of the evaluation metrics, or the quality of the actual customer segments? Propositions (or even discussions) concerning these matters are direly needed.

- _KG02: Providing empirical evidence on customer segmentation outcomes._ Based on our literature review, we observed that few studies provide an empirical analysis of the actual application of ACS in organizations. Algorithmic studies tend to stop at the stage of creating the customer segments; their application in companies is not explored. On the one hand, this casts shadows on whether the potential benefits of customer segmentation mentioned in the studies are rather hypothetical, or whether they can be backed up with empirical evidence. Therefore, we encourage researchers to shift their focus from creating segments to applying them in firms and other organizations. This not only represents an exciting research gap but efforts in this regard can help further enhance and incentivize research projects on customer segmentation, as they would be more strongly linked to key performance metrics that firms and other organizations value. To this end, case studies, field studies, A/B tests, experiments, and longitudinal studies would be welcome to address this vast knowledge gap.

- _KG03: Integrating algorithms into customer segmentation systems._ One central direction for segmentation research is developing more comprehensive pipelines that can handle multiple different data types (i.e., customer segmentation criteria of different types) and changing business requirements. A key direction in this regard would be merging customer segmentation research with _intelligent systems_ research (i.e., research that focuses on developing systems that can think, reason, and make decisions independently, without human intervention, interacting with the environment and making decisions to optimize quantitative outcomes (Bauer and Dey [2016](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR2 "Bauer, C., and A.K. Dey. 2016. Considering Context in the Design of Intelligent Systems: Current Practices and Suggestions for Improvement. Journal of Systems and Software 112: 26–47."))) to generate and empirically investigate more comprehensive customer segmentation systems that stakeholders can interact with, not merely isolated attempts of testing how ‘Algorithm X’ fares with the customer segmentation task. Again, this corresponds to our postulation that, based on our review, customer segmentation research would benefit from a higher degree of ambition and scope, as the current body of work focuses on developing and testing algorithms instead of systems.

- _KG04: Proposing a standardized framework for evaluation._ Due to methodological plurality, there is a lack of consensus on what constitutes ‘quality’ in customer segmentation. However, the consensus from prior research indicates that quality is perceived as models’ internal consistency and evaluated using technical performance metrics focused on this internal consistency. ACS has inherited its evaluation metrics from the ML research tradition, essentially adopting the metrics used in other clustering and data dimensionality tasks to customer segmentation as well. While we do not deny the merits of these technical metrics—they provide useful information about the model’s fit with the customer dataset—we call for further extensions and contributions to broaden the hierarchy of evaluating customer segmentation outputs. In addition to technical metrics, we ought to consider other metrics as well, such as stakeholder perception (“Are these segments useful? How useful?”) and organizational outcomes (e.g., the “ROI of customer segmentation”, i.e., how much does the implementation of customer segmentation improve the profit of the company?). A more holistic and nuanced, hierarchical way of measuring the quality of customer segmentation would further develop the field in academic and practical circles.

- _KG05: Exploring organizational challenges of customer segmentation._ Challenges in customer segmentation arise, on the one hand, from organizational realities such as culture, capabilities, and individual experience and, on the other hand, from technical rationale such as data availability, selection of algorithms, and validating the quality of customer segmentation. The organizational aspect of applying customer segmentation in decision-making is a clear and present research gap. Again, qualitative studies can help generate rich insights into how customer segmentation algorithms transit into organizational adoption. So, we need a more collaborative approach to customer segmentation research. This means not giving up on developing better algorithms, but in addition to that, engaging with social science researchers in a pursuit to discover the impact of applying these algorithms in the real world. Such extension presents an exciting new field of study.

- _KG06: Providing more critical analyses._ Researchers typically do not discuss the fundamental limitations of using AI and ML in customer segmentation, such as the fact that clustering algorithms were not originally developed for customer segmentation. Questions such as “What are the downsides of using AI for customer segmentation?” are not asked. Yet, they _should_ be asked, as critical analyses can reveal insights into transformative improvements in this field. As a starting point for such analyses, we offer some ideas: first, the use of algorithms may distance the stakeholders from the data, especially if the creation of the segments is not a participatory process but outsourced to a group of analysts/data scientists who will not be part of the eventual use of the segments. So, there can be a problem of detachment and silos. Second, algorithms may cause segmentation to become overly rigid and resistant to change, so the same criteria used to group customers may not be relevant after a certain amount of time. Third, customers may resent being “put into a box” and may not appreciate feeling like just another anonymous statistic; thus, customer perceptions regarding customer segmentation could be explored. These and other negative aspects of ACS should be studied much more.

- _KG07: Making the role of humans explicit._ Currently, humans play a central role in ACS; they select the algorithms and evaluation metrics, program the experiments, interpret the results, and choose final hyperparameter combinations. They also evaluate the results and make the final judgment of whether an algorithm did a good job at the segmentation. Finally, humans apply the segments in practice and make decisions based on them. Yet, we speak of ‘algorithmic customer segmentation’ and seem to delegate a lot of responsibility for the segmentation process to algorithms, often obfuscating the role of humans. As the field of customer segmentation is increasingly reliant on AI to do this work, a vital question is, what can AI learn from non-AI-reliant customer segmentation? In other words, there is a need to better understand human factors in the segmentation process and how these can support or bias the process when co-existing with algorithms.


### Practical implications

There are three main practical implications (PI) for researchers and practitioners:

- _PI01: Segmenting Beyond K-means_: Although nearly fifty algorithms were identified, k-means or a derivative is by far the most popular (27.6%) algorithmic approach for customer segmentation. This situation presents an opportunity and a need for exploring and comparing these algorithmic approaches to determine the most effective approach for different business scenarios—earlier research has partially done this (Punj and Stewart [1983](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR35 "Punj, G., and D.W. Stewart. 1983. Cluster Analysis in Marketing Research: Review and Suggestions for Application. Journal of Marketing Research 20 (2): 134–148.")), but not in a completely systematic way and not considering business scenarios. To do this comparing, it would entail both algorithmic investigation and business context research to identify characteristics for different business scenarios and how these relate to the selection of the best scenarios to address such analysis.

- _PI02: Sensemaking of the Segments_: In addition to investigating approach algorithms given the attributes of business scenarios, there is a general lack of evaluation of the resulting segment, with most of the evaluations done using technical measures related to the chosen algorithm. However, given the algorithmic plurality, this results in a plurality of evaluation techniques as well. This calls for standard evaluation criteria for customer segments extending across the various algorithms. Finally, there is a critical and unmet need for evaluating segmentation beyond the algorithmic nuances, using broader criteria of accuracy, fairness, diversity, or coverage. For these, investigations of segmentation hyperparameters would most likely be needed.

- _PI03: Finding the “X” in \[Segmentation + X\]_: The richness of segmentation criteria implies a nearly infinite number of ways of dividing a customer population into segments and these segments into sub-segments. Also, the segmentation criteria can be modified by adding or removing specific criteria at any time. Each of these segmentations offers one view of the segmentation that most likely has many possible views. So, which one is correct? This question is probably impossible without an ‘X’, i.e., some criteria external to the data for which to evaluate the segmentation. For this, the segmentation results need to be placed within the given business scenario, as discussed above, and the segments validated using external feedback, organizational key performance indicators, or achievement of business scenario goals.


Overall, customer segmentation, especially when applying AI and ML algorithms, is a socio-technical problem. In other words, both ‘technical’ (algorithm choice, data availability) and ‘social’ aspects (culture, goals) affect the success of customer segmentation projects. Therefore, mere technical solutions or more sophisticated algorithms are not adequate for ensuring successful customer segmentation projects. Thus, it is vital to understand customer segmentation projects as long-term processes that require stakeholder buy-in and effective implementation plans (i.e., the segmentation process does not end with creating the segments but only begins).

The current body of ACS literature focuses on the technical application of algorithms but largely omits the role of humans in this process, whether the role deals with various aspects of using the AI/ML algorithms (i.e., using judgment for the hyperparameter selection), evaluating the results, and eventually applying the results of ACS. Given the predominant focus on technical metrics and algorithms, there is a need to go beyond these aspects into the realm of inspecting the technology’s impact on actual organizations. According to our understanding, this can best be achieved by cross-disciplinary collaboration with social scientists, marketers, and other stakeholders who understand the qualitative side of customer segmentation and have access to organizational performance data. So, while this step of expanding ACS research into the realm of application is likely to involve a certain exit from the ML paradigm’s “comfort zone”, it is a necessary step to establish true scientific progress in this domain. Fernández-Delgado et al. ( [2014](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR8 "Fernández-Delgado, M., E. Cernadas, S. Barro, and D. Amorim. 2014. Do We Need Hundreds of Classifiers to Solve Real World Classification Problems? The Journal of Machine Learning Research 15 (1): 3133–3181.")) famously asked in the context of classification, “Do we need hundreds of classifiers to solve real world classification problems?” (cited 3594 times at the time of writing this); we can paraphrase this question: _Do we really need 46 different customer segmentation algorithms?_ Given the discrepancy between the large number of algorithms and the scarce number of articles applying subject matter experts for the evaluation of successful customer segmentation, the answer might be negative.

### Study limitations

We did not include articles published before the year 2000 in our sample. We did not include keywords dealing with market segmentation or consumer segmentation (e.g., Kamakura and Russell [1989](https://link.springer.com/article/10.1057/s41270-023-00235-5#ref-CR16 "Kamakura, W.A., and G.J. Russell. 1989. A Probabilistic Choice Model for Market Segmentation and Elasticity Structure. Journal of Marketing Research 26 (4): 379–390."))—conceptually, these are different goals, as ‘market’ includes non-customers as well. However, it could be interesting to compare the methods and variables used in these different segmentation tasks. We leave this for future work.

## Conclusion

Customer segmentation has been a major focus in academic literature for many years and continues to be one. It is also of high value to marketers in industry. However, due to a myriad of different approaches, the field suffers from the lack of clarity that we aimed to address with this study. We found that researchers have used 46 different algorithms for customer segmentation. Interestingly, around 80% of them utilized a single algorithm for this purpose. On average, they created about 5.7 customer segments, deciding the exact number inductively based on quantitative evaluation metrics. Surprisingly, few articles offer empirical evidence of the benefits of customer segmentation. Our results point the way for future research, as addressing the proposed key goals helps successfully develop customer segmentation algorithms, make sense of the customer segments, and evaluate the impact of the segmentation.

## References

- Ballestar, M.T., P. Grau-Carles, and J. Sainz. 2018. Customer Segmentation in E-Commerce: Applications to the Cashback Business Model. _Journal of Business Research_ 88: 407–414.

[Article](https://doi.org/10.1016%2Fj.jbusres.2017.11.047) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Customer%20Segmentation%20in%20E-Commerce%3A%20Applications%20to%20the%20Cashback%20Business%20Model&journal=Journal%20of%20Business%20Research&doi=10.1016%2Fj.jbusres.2017.11.047&volume=88&pages=407-414&publication_year=2018&author=Ballestar%2CMT&author=Grau-Carles%2CP&author=Sainz%2CJ)

- Bauer, C., and A.K. Dey. 2016. Considering Context in the Design of Intelligent Systems: Current Practices and Suggestions for Improvement. _Journal of Systems and Software_ 112: 26–47.

[Article](https://doi.org/10.1016%2Fj.jss.2015.10.041) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Considering%20Context%20in%20the%20Design%20of%20Intelligent%20Systems%3A%20Current%20Practices%20and%20Suggestions%20for%20Improvement&journal=Journal%20of%20Systems%20and%20Software&doi=10.1016%2Fj.jss.2015.10.041&volume=112&pages=26-47&publication_year=2016&author=Bauer%2CC&author=Dey%2CAK)

- Bell, J. 2014. _Machine Learning: Hands-on for Developers and Technical Professionals_, 1st ed. Hoboken: John Wiley & Sons.

[Book](https://doi.org/10.1002%2F9781119183464) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Machine%20Learning%3A%20Hands-on%20for%20Developers%20and%20Technical%20Professionals&doi=10.1002%2F9781119183464&publication_year=2014&author=Bell%2CJ)

- Böttcher, M., M. Spott, D. Nauck, and R. Kruse. 2009. Mining Changing Customer Segments in Dynamic Markets. _Expert Systems with Applications_ 36 (1): 155–164.

[Article](https://doi.org/10.1016%2Fj.eswa.2007.09.006) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Mining%20Changing%20Customer%20Segments%20in%20Dynamic%20Markets&journal=Expert%20Systems%20with%20Applications&doi=10.1016%2Fj.eswa.2007.09.006&volume=36&issue=1&pages=155-164&publication_year=2009&author=B%C3%B6ttcher%2CM&author=Spott%2CM&author=Nauck%2CD&author=Kruse%2CR)

- Cooil, B., L. Aksoy, and T.L. Keiningham. 2008. Approaches to Customer Segmentation. _Journal of Relationship Marketing_ 6 (3–4): 9–39.

[Article](https://doi.org/10.1300%2FJ366v06n03_02) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Approaches%20to%20Customer%20Segmentation&journal=Journal%20of%20Relationship%20Marketing&doi=10.1300%2FJ366v06n03_02&volume=6&issue=3%E2%80%934&pages=9-39&publication_year=2008&author=Cooil%2CB&author=Aksoy%2CL&author=Keiningham%2CTL)

- Coussement, K., F.A.M. Van den Bossche, and K.W. De Bock. 2014. Data Accuracy’s Impact on Segmentation Performance: Benchmarking RFM Analysis, Logistic Regression, and Decision Trees. _Journal of Business Research_ 67 (1): 2751–2758.

[Article](https://doi.org/10.1016%2Fj.jbusres.2012.09.024) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Data%20Accuracy%E2%80%99s%20Impact%20on%20Segmentation%20Performance%3A%20Benchmarking%20RFM%20Analysis%2C%20Logistic%20Regression%2C%20and%20Decision%20Trees&journal=Journal%20of%20Business%20Research&doi=10.1016%2Fj.jbusres.2012.09.024&volume=67&issue=1&pages=2751-2758&publication_year=2014&author=Coussement%2CK&author=Bossche%2CFAM&author=Bock%2CKW)

- Deng, Y., and Q. Gao. 2020. RETRACTED ARTICLE: A Study on e-Commerce Customer Segmentation Management Based on Improved K-Means Algorithm. _Information Systems and e-Business Management_ 18 (4): 497–510.

[Article](https://link.springer.com/article/10.1007/s10257-018-0381-3) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=RETRACTED%20ARTICLE%3A%20A%20Study%20on%20e-Commerce%20Customer%20Segmentation%20Management%20Based%20on%20Improved%20K-Means%20Algorithm&journal=Information%20Systems%20and%20e-Business%20Management&doi=10.1007%2Fs10257-018-0381-3&volume=18&issue=4&pages=497-510&publication_year=2020&author=Deng%2CY&author=Gao%2CQ)

- Fernández-Delgado, M., E. Cernadas, S. Barro, and D. Amorim. 2014. Do We Need Hundreds of Classifiers to Solve Real World Classification Problems? _The Journal of Machine Learning Research_ 15 (1): 3133–3181.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Do%20We%20Need%20Hundreds%20of%20Classifiers%20to%20Solve%20Real%20World%20Classification%20Problems%3F&journal=The%20Journal%20of%20Machine%20Learning%20Research&volume=15&issue=1&pages=3133-3181&publication_year=2014&author=Fern%C3%A1ndez-Delgado%2CM&author=Cernadas%2CE&author=Barro%2CS&author=Amorim%2CD)

- Güçdemir, H., and H. Selim. 2015. Integrating Multi-Criteria Decision Making and Clustering for Business Customer Segmentation. _Industrial Management & Data Systems_ 115 (6): 1022–1040.

[Article](https://doi.org/10.1108%2FIMDS-01-2015-0027) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Integrating%20Multi-Criteria%20Decision%20Making%20and%20Clustering%20for%20Business%20Customer%20Segmentation&journal=Industrial%20Management%20%26%20Data%20Systems&doi=10.1108%2FIMDS-01-2015-0027&volume=115&issue=6&pages=1022-1040&publication_year=2015&author=G%C3%BC%C3%A7demir%2CH&author=Selim%2CH)

- Hiziroglu, A. 2013. A Neuro-Fuzzy Two-Stage Clustering Approach to Customer Segmentation. _Journal of Marketing Analytics_ 1 (4): 202–221.

[Article](https://doi.org/10.1057%2Fjma.2013.17) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Neuro-Fuzzy%20Two-Stage%20Clustering%20Approach%20to%20Customer%20Segmentation&journal=Journal%20of%20Marketing%20Analytics&doi=10.1057%2Fjma.2013.17&volume=1&issue=4&pages=202-221&publication_year=2013&author=Hiziroglu%2CA)

- Hong, T., and E. Kim. 2012. Segmenting Customers in Online Stores Based on Factors That Affect the Customer’s Intention to Purchase. _Expert Systems with Applications_ 39 (2): 2127–2131.

[Article](https://doi.org/10.1016%2Fj.eswa.2011.07.114) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Segmenting%20Customers%20in%20Online%20Stores%20Based%20on%20Factors%20That%20Affect%20the%20Customer%E2%80%99s%20Intention%20to%20Purchase&journal=Expert%20Systems%20with%20Applications&doi=10.1016%2Fj.eswa.2011.07.114&volume=39&issue=2&pages=2127-2131&publication_year=2012&author=Hong%2CT&author=Kim%2CE)

- Hosseini, M., and M. Shabani. 2015. New Approach to Customer Segmentation Based on Changes in Customer Value. _Journal of Marketing Analytics_ 3: 110–121.

[Article](https://doi.org/10.1057%2Fjma.2015.10) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=New%20Approach%20to%20Customer%20Segmentation%20Based%20on%20Changes%20in%20Customer%20Value&journal=Journal%20of%20Marketing%20Analytics&doi=10.1057%2Fjma.2015.10&volume=3&pages=110-121&publication_year=2015&author=Hosseini%2CM&author=Shabani%2CM)

- Jansen, B., S. Jung, and J. Salminen. 2021. The Effect of Hyperparameter Selection on the Personification of Customer Population Data. _International Journal of Electrical and Computer Engineering Research_. [https://doi.org/10.53375/ijecer.2021.31](https://doi.org/10.53375/ijecer.2021.31).

[Article](https://doi.org/10.53375%2Fijecer.2021.31) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20Effect%20of%20Hyperparameter%20Selection%20on%20the%20Personification%20of%20Customer%20Population%20Data&journal=International%20Journal%20of%20Electrical%20and%20Computer%20Engineering%20Research&doi=10.53375%2Fijecer.2021.31&publication_year=2021&author=Jansen%2CB&author=Jung%2CS&author=Salminen%2CJ)

- Jiang, T., and A. Tuzhilin. 2009. Improving Personalization Solutions through Optimal Segmentation of Customer Bases. _IEEE Transactions on Knowledge and Data Engineering_ 21 (3): 305–320.

[Article](https://doi.org/10.1109%2FTKDE.2008.163) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Improving%20Personalization%20Solutions%20through%20Optimal%20Segmentation%20of%20Customer%20Bases&journal=IEEE%20Transactions%20on%20Knowledge%20and%20Data%20Engineering&doi=10.1109%2FTKDE.2008.163&volume=21&issue=3&pages=305-320&publication_year=2009&author=Jiang%2CT&author=Tuzhilin%2CA)

- Joung, J., and H. Kim. 2023. Interpretable Machine Learning-Based Approach for Customer Segmentation for New Product Development from Online Product Reviews. _International Journal of Information Management_ 70: 102641.

[Article](https://doi.org/10.1016%2Fj.ijinfomgt.2023.102641) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Interpretable%20Machine%20Learning-Based%20Approach%20for%20Customer%20Segmentation%20for%20New%20Product%20Development%20from%20Online%20Product%20Reviews&journal=International%20Journal%20of%20Information%20Management&doi=10.1016%2Fj.ijinfomgt.2023.102641&volume=70&publication_year=2023&author=Joung%2CJ&author=Kim%2CH)

- Kamakura, W.A., and G.J. Russell. 1989. A Probabilistic Choice Model for Market Segmentation and Elasticity Structure. _Journal of Marketing Research_ 26 (4): 379–390.

[Article](https://doi.org/10.1177%2F002224378902600401) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Probabilistic%20Choice%20Model%20for%20Market%20Segmentation%20and%20Elasticity%20Structure&journal=Journal%20of%20Marketing%20Research&doi=10.1177%2F002224378902600401&volume=26&issue=4&pages=379-390&publication_year=1989&author=Kamakura%2CWA&author=Russell%2CGJ)

- Kashwan, K.R., and C. Velu. 2013. Customer Segmentation Using Clustering and Data Mining Techniques. _International Journal of Computer Theory and Engineering_ 5: 856–861.

[Article](https://doi.org/10.7763%2FIJCTE.2013.V5.811) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Customer%20Segmentation%20Using%20Clustering%20and%20Data%20Mining%20Techniques&journal=International%20Journal%20of%20Computer%20Theory%20and%20Engineering&doi=10.7763%2FIJCTE.2013.V5.811&volume=5&pages=856-861&publication_year=2013&author=Kashwan%2CKR&author=Velu%2CC)

- Khajvand, M., and M.J. Tarokh. 2011. Estimating Customer Future Value of Different Customer Segments Based on Adapted RFM Model in Retail Banking Context. _Procedia Computer Science_ 3: 1327–1332.

[Article](https://doi.org/10.1016%2Fj.procs.2011.01.011) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Estimating%20Customer%20Future%20Value%20of%20Different%20Customer%20Segments%20Based%20on%20Adapted%20RFM%20Model%20in%20Retail%20Banking%20Context&journal=Procedia%20Computer%20Science&doi=10.1016%2Fj.procs.2011.01.011&volume=3&pages=1327-1332&publication_year=2011&author=Khajvand%2CM&author=Tarokh%2CMJ)

- Kitchenham, B., O.P. Brereton, D. Budgen, M. Turner, J. Bailey, and S. Linkman. 2009. Systematic Literature Reviews in Software Engineering–a Systematic Literature Review. _Information and Software Technology_ 51 (1): 7–15.

[Article](https://doi.org/10.1016%2Fj.infsof.2008.09.009) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Systematic%20Literature%20Reviews%20in%20Software%20Engineering%E2%80%93a%20Systematic%20Literature%20Review&journal=Information%20and%20Software%20Technology&doi=10.1016%2Fj.infsof.2008.09.009&volume=51&issue=1&pages=7-15&publication_year=2009&author=Kitchenham%2CB&author=Brereton%2COP&author=Budgen%2CD&author=Turner%2CM&author=Bailey%2CJ&author=Linkman%2CS)

- Kühl, N., M. Schemmer, M. Goutier, and G. Satzger. 2022. Artificial Intelligence and Machine Learning. _Electronic Markets_ 32 (4): 2235–2244.

[Article](https://link.springer.com/article/10.1007/s12525-022-00598-0) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Artificial%20Intelligence%20and%20Machine%20Learning&journal=Electronic%20Markets&doi=10.1007%2Fs12525-022-00598-0&volume=32&issue=4&pages=2235-2244&publication_year=2022&author=K%C3%BChl%2CN&author=Schemmer%2CM&author=Goutier%2CM&author=Satzger%2CG)

- Kuo, R.J., C.H. Mei, F.E. Zulvia, and C.Y. Tsai. 2016. An Application of a Metaheuristic Algorithm-Based Clustering Ensemble Method to APP Customer Segmentation. _Neurocomputing_ 205: 116–129.

[Article](https://doi.org/10.1016%2Fj.neucom.2016.04.017) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=An%20Application%20of%20a%20Metaheuristic%20Algorithm-Based%20Clustering%20Ensemble%20Method%20to%20APP%20Customer%20Segmentation&journal=Neurocomputing&doi=10.1016%2Fj.neucom.2016.04.017&volume=205&pages=116-129&publication_year=2016&author=Kuo%2CRJ&author=Mei%2CCH&author=Zulvia%2CFE&author=Tsai%2CCY)

- Lee, Y., and S. Cho. 2021. User Segmentation via Interpretable User Representation and Relative Similarity-Based Segmentation Method. _Multimedia Systems_ 27 (1): 61–72.

[Article](https://link.springer.com/article/10.1007/s00530-020-00702-4) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=User%20Segmentation%20via%20Interpretable%20User%20Representation%20and%20Relative%20Similarity-Based%20Segmentation%20Method&journal=Multimedia%20Systems&doi=10.1007%2Fs00530-020-00702-4&volume=27&issue=1&pages=61-72&publication_year=2021&author=Lee%2CY&author=Cho%2CS)

- Lee, J.H., and S.C. Park. 2005. Intelligent Profitable Customers Segmentation System Based on Business Intelligence Tools. _Expert Systems with Applications_ 29 (1): 145–152.

[Article](https://doi.org/10.1016%2Fj.eswa.2005.01.013) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Intelligent%20Profitable%20Customers%20Segmentation%20System%20Based%20on%20Business%20Intelligence%20Tools&journal=Expert%20Systems%20with%20Applications&doi=10.1016%2Fj.eswa.2005.01.013&volume=29&issue=1&pages=145-152&publication_year=2005&author=Lee%2CJH&author=Park%2CSC)

- Li, K.J., D.K.H. Fong, and S.H. Xu. 2011. Managing Trade-in Programs Based on Product Characteristics and Customer Heterogeneity in Business-to-Business Markets. _Manufacturing & Service Operations Management_ 13 (1): 108–123.

[Article](https://doi.org/10.1287%2Fmsom.1100.0307) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Managing%20Trade-in%20Programs%20Based%20on%20Product%20Characteristics%20and%20Customer%20Heterogeneity%20in%20Business-to-Business%20Markets&journal=Manufacturing%20%26%20Service%20Operations%20Management&doi=10.1287%2Fmsom.1100.0307&volume=13&issue=1&pages=108-123&publication_year=2011&author=Li%2CKJ&author=Fong%2CDKH&author=Xu%2CSH)

- Liu, D.-R., C.-H. Lai, and W.-J. Lee. 2009. A Hybrid of Sequential Rules and Collaborative Filtering for Product Recommendation. _Information Sciences_ 179 (20): 3505–3519.

[Article](https://doi.org/10.1016%2Fj.ins.2009.06.004) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Hybrid%20of%20Sequential%20Rules%20and%20Collaborative%20Filtering%20for%20Product%20Recommendation&journal=Information%20Sciences&doi=10.1016%2Fj.ins.2009.06.004&volume=179&issue=20&pages=3505-3519&publication_year=2009&author=Liu%2CD-R&author=Lai%2CC-H&author=Lee%2CW-J)

- Lu, T.-C., and K.-Y. Wu. 2009. A Transaction Pattern Analysis System Based on Neural Network. _Expert Systems with Applications_ 36 (3, Part 2): 6091–6099.

[Article](https://doi.org/10.1016%2Fj.eswa.2008.07.073) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Transaction%20Pattern%20Analysis%20System%20Based%20on%20Neural%20Network&journal=Expert%20Systems%20with%20Applications&doi=10.1016%2Fj.eswa.2008.07.073&volume=36&issue=3%2C%20Part%202&pages=6091-6099&publication_year=2009&author=Lu%2CT-C&author=Wu%2CK-Y)

- Manidatta, R., M. Ray, K. Muduli, A. Banaitis, and A. Kumar. 2021. Integrated Approach of Fuzzy Multi-Attribute Decision Making and Data Mining for Customer Segmentation. _E a M: Ekonomie a Management_ 24: 174–188.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Integrated%20Approach%20of%20Fuzzy%20Multi-Attribute%20Decision%20Making%20and%20Data%20Mining%20for%20Customer%20Segmentation&journal=E%20a%20M%3A%20Ekonomie%20a%20Management&volume=24&pages=174-188&publication_year=2021&author=Manidatta%2CR&author=Ray%2CM&author=Muduli%2CK&author=Banaitis%2CA&author=Kumar%2CA)

- Manjunath, Y.S.K., and R.F. Kashef. 2021. Distributed Clustering Using Multi-Tier Hierarchical Overlay Super-Peer Peer-to-Peer Network Architecture for Efficient Customer Segmentation. _Electronic Commerce Research and Applications_ 47: 101040.

[Article](https://doi.org/10.1016%2Fj.elerap.2021.101040) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Distributed%20Clustering%20Using%20Multi-Tier%20Hierarchical%20Overlay%20Super-Peer%20Peer-to-Peer%20Network%20Architecture%20for%20Efficient%20Customer%20Segmentation&journal=Electronic%20Commerce%20Research%20and%20Applications&doi=10.1016%2Fj.elerap.2021.101040&volume=47&publication_year=2021&author=Manjunath%2CYSK&author=Kashef%2CRF)

- Munusamy, S., and P. Murugesan. 2020. Modified Dynamic Fuzzy C-Means Clustering Algorithm—Application in Dynamic Customer Segmentation. _Applied Intelligence_ 50 (6): 1922–1942.

[Article](https://link.springer.com/article/10.1007/s10489-019-01626-x) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Modified%20Dynamic%20Fuzzy%20C-Means%20Clustering%20Algorithm%E2%80%94Application%20in%20Dynamic%20Customer%20Segmentation&journal=Applied%20Intelligence&doi=10.1007%2Fs10489-019-01626-x&volume=50&issue=6&pages=1922-1942&publication_year=2020&author=Munusamy%2CS&author=Murugesan%2CP)

- Mustak, M., J. Salminen, L. Plé, and J. Wirtz. 2021. Artificial Intelligence in Marketing: Topic Modeling, Scientometric Analysis, and Research Agenda. _Journal of Business Research_ 124: 389–404.

[Article](https://doi.org/10.1016%2Fj.jbusres.2020.10.044) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Artificial%20Intelligence%20in%20Marketing%3A%20Topic%20Modeling%2C%20Scientometric%20Analysis%2C%20and%20Research%20Agenda&journal=Journal%20of%20Business%20Research&doi=10.1016%2Fj.jbusres.2020.10.044&volume=124&pages=389-404&publication_year=2021&author=Mustak%2CM&author=Salminen%2CJ&author=Pl%C3%A9%2CL&author=Wirtz%2CJ)

- Nemati, Y., A. Mohaghar, M.H. Alavidoost, and H. Babazadeh. 2018. A CLV-Based Framework to Prioritize Promotion Marketing Strategies—Case Study of Telecom Industry. _Iranian Journal of Management Studies_. [https://doi.org/10.22059/ijms.2018.242492.672837](https://doi.org/10.22059/ijms.2018.242492.672837).

[Article](https://doi.org/10.22059%2Fijms.2018.242492.672837) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20CLV-Based%20Framework%20to%20Prioritize%20Promotion%20Marketing%20Strategies%E2%80%94Case%20Study%20of%20Telecom%20Industry&journal=Iranian%20Journal%20of%20Management%20Studies&doi=10.22059%2Fijms.2018.242492.672837&publication_year=2018&author=Nemati%2CY&author=Mohaghar%2CA&author=Alavidoost%2CMH&author=Babazadeh%2CH)

- Nie, D., P. Cappellari, and M. Roantree. 2020. A Methodology for Classification and Validation of Customer Datasets. _Journal of Business & Industrial Marketing_ 36 (5): 821–833.

[Article](https://doi.org/10.1108%2FJBIM-02-2020-0077) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Methodology%20for%20Classification%20and%20Validation%20of%20Customer%20Datasets&journal=Journal%20of%20Business%20%26%20Industrial%20Marketing&doi=10.1108%2FJBIM-02-2020-0077&volume=36&issue=5&pages=821-833&publication_year=2020&author=Nie%2CD&author=Cappellari%2CP&author=Roantree%2CM)

- Nisan, S., Ş Elif, and Ç.U. Banu. 2022. Discrete Event Simulation Model Performed with Data Analytics for a Call Center Optimization. _Istanbul Business Research_ 51 (1): 189–208.

[Google Scholar](http://scholar.google.com/scholar_lookup?&title=Discrete%20Event%20Simulation%20Model%20Performed%20with%20Data%20Analytics%20for%20a%20Call%20Center%20Optimization&journal=Istanbul%20Business%20Research&volume=51&issue=1&pages=189-208&publication_year=2022&author=Nisan%2CS&author=Elif%2C%C5%9E&author=Banu%2C%C3%87U)

- Peker, S., A. Kocyigit, and P.E. Eren. 2017. A Hybrid Approach for Predicting Customers’ Individual Purchase Behavior. _Kybernetes_ 46 (10): 1614–1631.

[Article](https://doi.org/10.1108%2FK-05-2017-0164) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Hybrid%20Approach%20for%20Predicting%20Customers%E2%80%99%20Individual%20Purchase%20Behavior&journal=Kybernetes&doi=10.1108%2FK-05-2017-0164&volume=46&issue=10&pages=1614-1631&publication_year=2017&author=Peker%2CS&author=Kocyigit%2CA&author=Eren%2CPE)

- Punj, G., and D.W. Stewart. 1983. Cluster Analysis in Marketing Research: Review and Suggestions for Application. _Journal of Marketing Research_ 20 (2): 134–148.

[Article](https://doi.org/10.1177%2F002224378302000204) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Cluster%20Analysis%20in%20Marketing%20Research%3A%20Review%20and%20Suggestions%20for%20Application&journal=Journal%20of%20Marketing%20Research&doi=10.1177%2F002224378302000204&volume=20&issue=2&pages=134-148&publication_year=1983&author=Punj%2CG&author=Stewart%2CDW)

- Repschlaeger, J., K. Erek, and R. Zarnekow. 2013. Cloud Computing Adoption: An Empirical Study of Customer Preferences among Start-up Companies. _Electronic Markets_ 23 (2): 115–148.

[Article](https://link.springer.com/article/10.1007/s12525-012-0119-x) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Cloud%20Computing%20Adoption%3A%20An%20Empirical%20Study%20of%20Customer%20Preferences%20among%20Start-up%20Companies&journal=Electronic%20Markets&doi=10.1007%2Fs12525-012-0119-x&volume=23&issue=2&pages=115-148&publication_year=2013&author=Repschlaeger%2CJ&author=Erek%2CK&author=Zarnekow%2CR)

- Safari, F., N. Safari, and G.A. Montazer. 2016. Customer Lifetime Value Determination Based on RFM Model. _Marketing Intelligence & Planning_ 34: 446–461.

[Article](https://doi.org/10.1108%2FMIP-03-2015-0060) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Customer%20Lifetime%20Value%20Determination%20Based%20on%20RFM%20Model&journal=Marketing%20Intelligence%20%26%20Planning&doi=10.1108%2FMIP-03-2015-0060&volume=34&pages=446-461&publication_year=2016&author=Safari%2CF&author=Safari%2CN&author=Montazer%2CGA)

- Salminen, J., V. Yoganathan, J. Corporan, B.J. Jansen, and S.-G. Jung. 2019. Machine Learning Approach to Auto-Tagging Online Content for Content Marketing Efficiency: A Comparative Analysis between Methods and Content Type. _Journal of Business Research_ 101: 203–217.

[Article](https://doi.org/10.1016%2Fj.jbusres.2019.04.018) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Machine%20Learning%20Approach%20to%20Auto-Tagging%20Online%20Content%20for%20Content%20Marketing%20Efficiency%3A%20A%20Comparative%20Analysis%20between%20Methods%20and%20Content%20Type&journal=Journal%20of%20Business%20Research&doi=10.1016%2Fj.jbusres.2019.04.018&volume=101&pages=203-217&publication_year=2019&author=Salminen%2CJ&author=Yoganathan%2CV&author=Corporan%2CJ&author=Jansen%2CBJ&author=Jung%2CS-G)

- Salminen, J., K. Chhirang, S.-G. Jung, S. Thirumuruganathan, K.W. Guan, and B.J. Jansen. 2022. Big Data, Small Personas: How Algorithms Shape the Demographic Representation of Data-Driven User Segments. _Big Data_. [https://doi.org/10.1089/big.2021.0177](https://doi.org/10.1089/big.2021.0177).

[Article](https://doi.org/10.1089%2Fbig.2021.0177) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Big%20Data%2C%20Small%20Personas%3A%20How%20Algorithms%20Shape%20the%20Demographic%20Representation%20of%20Data-Driven%20User%20Segments&journal=Big%20Data&doi=10.1089%2Fbig.2021.0177&publication_year=2022&author=Salminen%2CJ&author=Chhirang%2CK&author=Jung%2CS-G&author=Thirumuruganathan%2CS&author=Guan%2CKW&author=Jansen%2CBJ)

- Seret, A., S. Maldonado, and B. Baesens. 2015. Identifying next Relevant Variables for Segmentation by Using Feature Selection Approaches. _Expert Systems with Applications_ 42 (15): 6255–6266.

[Article](https://doi.org/10.1016%2Fj.eswa.2015.01.070) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Identifying%20next%20Relevant%20Variables%20for%20Segmentation%20by%20Using%20Feature%20Selection%20Approaches&journal=Expert%20Systems%20with%20Applications&doi=10.1016%2Fj.eswa.2015.01.070&volume=42&issue=15&pages=6255-6266&publication_year=2015&author=Seret%2CA&author=Maldonado%2CS&author=Baesens%2CB)

- Simões, D., and J. Nogueira. 2022. Learning about the Customer for Improving Customer Retention Proposal of an Analytical Framework. _Journal of Marketing Analytics_. [https://doi.org/10.1057/s41270-021-00126-7](https://doi.org/10.1057/s41270-021-00126-7).

[Article](https://doi.org/10.1057%2Fs41270-021-00126-7) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Learning%20about%20the%20Customer%20for%20Improving%20Customer%20Retention%20Proposal%20of%20an%20Analytical%20Framework&journal=Journal%20of%20Marketing%20Analytics&doi=10.1057%2Fs41270-021-00126-7&publication_year=2022&author=Sim%C3%B5es%2CD&author=Nogueira%2CJ)

- Spoor, J.M. 2022. Improving Customer Segmentation via Classification of Key Accounts as Outliers. _Journal of Marketing Analytics_. [https://doi.org/10.1057/s41270-022-00185-4](https://doi.org/10.1057/s41270-022-00185-4).

[Article](https://doi.org/10.1057%2Fs41270-022-00185-4) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Improving%20Customer%20Segmentation%20via%20Classification%20of%20Key%20Accounts%20as%20Outliers&journal=Journal%20of%20Marketing%20Analytics&doi=10.1057%2Fs41270-022-00185-4&publication_year=2022&author=Spoor%2CJM)

- Sun, Z.-H., T.-Y. Zuo, D. Liang, X. Ming, Z. Chen, and S. Qiu. 2021. GPHC: A Heuristic Clustering Method to Customer Segmentation. _Applied Soft Computing_ 111: 107677.

[Article](https://doi.org/10.1016%2Fj.asoc.2021.107677) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=GPHC%3A%20A%20Heuristic%20Clustering%20Method%20to%20Customer%20Segmentation&journal=Applied%20Soft%20Computing&doi=10.1016%2Fj.asoc.2021.107677&volume=111&publication_year=2021&author=Sun%2CZ-H&author=Zuo%2CT-Y&author=Liang%2CD&author=Ming%2CX&author=Chen%2CZ&author=Qiu%2CS)

- Symeonidis, S., D. Effrosynidis, and A. Arampatzis. 2018. A Comparative Evaluation of Pre-Processing Techniques and Their Interactions for Twitter Sentiment Analysis. _Expert Systems with Applications_ 110: 298–310.

[Article](https://doi.org/10.1016%2Fj.eswa.2018.06.022) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Comparative%20Evaluation%20of%20Pre-Processing%20Techniques%20and%20Their%20Interactions%20for%20Twitter%20Sentiment%20Analysis&journal=Expert%20Systems%20with%20Applications&doi=10.1016%2Fj.eswa.2018.06.022&volume=110&pages=298-310&publication_year=2018&author=Symeonidis%2CS&author=Effrosynidis%2CD&author=Arampatzis%2CA)

- Thirumuruganathan, S., N.A. Emadi, S. Jung, J. Salminen, D.R. Robillos, and B.J. Jansen. 2023. Will They Take This Offer? A Machine Learning Price Elasticity Model for Predicting Upselling Acceptance of Premium Airline Seating. _Information & Management_ 60: 103759.

[Article](https://doi.org/10.1016%2Fj.im.2023.103759) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Will%20They%20Take%20This%20Offer%3F%20A%20Machine%20Learning%20Price%20Elasticity%20Model%20for%20Predicting%20Upselling%20Acceptance%20of%20Premium%20Airline%20Seating&journal=Information%20%26%20Management&doi=10.1016%2Fj.im.2023.103759&volume=60&publication_year=2023&author=Thirumuruganathan%2CS&author=Emadi%2CNA&author=Jung%2CS&author=Salminen%2CJ&author=Robillos%2CDR&author=Jansen%2CBJ)

- Tsai, C.-F., Y.-H. Hu, and Y.-H. Lu. 2015. Customer Segmentation Issues and Strategies for an Automobile Dealership with Two Clustering Techniques. _Expert Systems_ 32 (1): 65–76.

[Article](https://doi.org/10.1111%2Fexsy.12056) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Customer%20Segmentation%20Issues%20and%20Strategies%20for%20an%20Automobile%20Dealership%20with%20Two%20Clustering%20Techniques&journal=Expert%20Systems&doi=10.1111%2Fexsy.12056&volume=32&issue=1&pages=65-76&publication_year=2015&author=Tsai%2CC-F&author=Hu%2CY-H&author=Lu%2CY-H)

- Wang, S.-C., Y.-T. Tsai, and Y.-S. Ciou. 2020. A Hybrid Big Data Analytical Approach for Analyzing Customer Patterns through an Integrated Supply Chain Network. _Journal of Industrial Information Integration_ 20: 100177.

[Article](https://doi.org/10.1016%2Fj.jii.2020.100177) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Hybrid%20Big%20Data%20Analytical%20Approach%20for%20Analyzing%20Customer%20Patterns%20through%20an%20Integrated%20Supply%20Chain%20Network&journal=Journal%20of%20Industrial%20Information%20Integration&doi=10.1016%2Fj.jii.2020.100177&volume=20&publication_year=2020&author=Wang%2CS-C&author=Tsai%2CY-T&author=Ciou%2CY-S)

- Warner, L.A. 2019. Using Homeowners’ Association Membership to Define Audience Segments for Targeted Local Social Marketing Interventions: Implications From a Statewide Study. _Social Marketing Quarterly_ 25 (4): 291–307.

[Article](https://doi.org/10.1177%2F1524500419882978) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Using%20Homeowners%E2%80%99%20Association%20Membership%20to%20Define%20Audience%20Segments%20for%20Targeted%20Local%20Social%20Marketing%20Interventions%3A%20Implications%20From%20a%20Statewide%20Study&journal=Social%20Marketing%20Quarterly&doi=10.1177%2F1524500419882978&volume=25&issue=4&pages=291-307&publication_year=2019&author=Warner%2CLA)

- Wong, E., and Y. Wei. 2018. Customer Online Shopping Experience Data Analytics: Integrated Customer Segmentation and Customised Services Prediction Model. _International Journal of Retail & Distribution Management_ 46 (4): 406–420.

[Article](https://doi.org/10.1108%2FIJRDM-06-2017-0130) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Customer%20Online%20Shopping%20Experience%20Data%20Analytics%3A%20Integrated%20Customer%20Segmentation%20and%20Customised%20Services%20Prediction%20Model&journal=International%20Journal%20of%20Retail%20%26%20Distribution%20Management&doi=10.1108%2FIJRDM-06-2017-0130&volume=46&issue=4&pages=406-420&publication_year=2018&author=Wong%2CE&author=Wei%2CY)

- Wu, T., and X. Liu. 2020. A Dynamic Interval Type-2 Fuzzy Customer Segmentation Model and Its Application in E-Commerce. _Applied Soft Computing_ 94: 106366.

[Article](https://doi.org/10.1016%2Fj.asoc.2020.106366) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20Dynamic%20Interval%20Type-2%20Fuzzy%20Customer%20Segmentation%20Model%20and%20Its%20Application%20in%20E-Commerce&journal=Applied%20Soft%20Computing&doi=10.1016%2Fj.asoc.2020.106366&volume=94&publication_year=2020&author=Wu%2CT&author=Liu%2CX)

- Wu, S., W.-C. Yau, T.-S. Ong, and S.-C. Chong. 2021. Integrated Churn Prediction and Customer Segmentation Framework for Telco Business. _IEEE Access_ 9: 62118–62136.

[Article](https://doi.org/10.1109%2FACCESS.2021.3073776) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Integrated%20Churn%20Prediction%20and%20Customer%20Segmentation%20Framework%20for%20Telco%20Business&journal=IEEE%20Access&doi=10.1109%2FACCESS.2021.3073776&volume=9&pages=62118-62136&publication_year=2021&author=Wu%2CS&author=Yau%2CW-C&author=Ong%2CT-S&author=Chong%2CS-C)

- Yao, Z., P. Sarlin, T. Eklund, and B. Back. 2014. Combining Visual Customer Segmentation and Response Modeling. _Neural Computing and Applications_ 25 (1): 123–134.

[Article](https://link.springer.com/article/10.1007/s00521-013-1454-3) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Combining%20Visual%20Customer%20Segmentation%20and%20Response%20Modeling&journal=Neural%20Computing%20and%20Applications&doi=10.1007%2Fs00521-013-1454-3&volume=25&issue=1&pages=123-134&publication_year=2014&author=Yao%2CZ&author=Sarlin%2CP&author=Eklund%2CT&author=Back%2CB)

- Zhou, J., J. Wei, and B. Xu. 2021. Customer Segmentation by Web Content Mining. _Journal of Retailing and Consumer Services_ 61: 102588.

[Article](https://doi.org/10.1016%2Fj.jretconser.2021.102588) [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Customer%20Segmentation%20by%20Web%20Content%20Mining&journal=Journal%20of%20Retailing%20and%20Consumer%20Services&doi=10.1016%2Fj.jretconser.2021.102588&volume=61&publication_year=2021&author=Zhou%2CJ&author=Wei%2CJ&author=Xu%2CB)

- Aryuni, M., E.D. Madyatmadja, and E. Miranda. 2018. Customer Segmentation in XYZ Bank Using K-Means and K-Medoids clustering. In: 2018 International Conference on Information Management and Technology (ICIMTech), 412–416, 2018. IEEE.

- Bhade, K., V. Gulalkari, N. Harwani, and S.N. Dhage. 2018. A Systematic Approach to Customer Segmentation and Buyer Targeting for Profit Maximization. In: 2018 9th International Conference on Computing, Communication and Networking Technologies (ICCCNT), 1–6, 2018. IEEE.

- Dzulhaq, M.I., K.W. Sari, S. Ramdhan, and R. Tullah. 2019. Customer Segmentation Based on RFM Value Using K-Means Algorithm. In: 2019 Fourth International Conference on Informatics and Computing (ICIC), 1–7, 2019. IEEE.

- Jung, S.-G., J. Salminen, J. An, H. Kwak, and B.J. Jansen. 2018. Automatically Conceptualizing Social Media Analytics Data via Personas. In: Proceedings of the International AAAI Conference on Web and Social Media (ICWSM 2018), June 25, 2018. San Francisco, California, USA.

- Kandeil, D.A., A.A. Saad, and S.M. Youssef. 2014. A Two-Phase Clustering Analysis for B2B Customer Segmentation. In: 2014 International Conference on Intelligent Networking and Collaborative Systems, 221–228, 2014. IEEE.

- Pramono, P.P., I. Surjandari, and E. Laoh. 2019. Estimating Customer Segmentation Based on Customer Lifetime Value Using Two-Stage Clustering Method. In: 2019 16th International Conference on Service Systems and Service Management (ICSSSM), 1–5, 2019. IEEE.

- Ranjan, A., and S. Srivastava. 2022. Customer Segmentation Using Machine Learning: A Literature Review. In: AIP Conference Proceedings, 2022. vol. 2481. AIP Publishing LLC, p. 020036.

- Syakur, M.A., B.K. Khotimah, E.M.S. Rochman, and B.D. Satoto. 2018. Integration K-Means Clustering Method and Elbow Method for Identification of the Best Customer Profile Cluster. In: IOP Conference Series: Materials Science and Engineering, 2018. vol. 336, 012017. IOP Publishing.

- Xu, X., N. Yuruk, Z. Feng, and T.A. Schweiger. 2007. Scan: A Structural Clustering Algorithm for Networks. In: Proceedings of the 13th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 824–833, 2007.

- Zhu, B., C. He, and X. Jiang. 2015. _A Consistency-Based Validation for Data Clustering—IOS Press_ \[Online\]. [https://content.iospress.com/articles/intelligent-data-analysis/ida727](https://content.iospress.com/articles/intelligent-data-analysis/ida727). Accessed 3 Mar 2023.


[Download references](https://citation-needed.springer.com/v2/references/10.1057/s41270-023-00235-5?format=refman&flavour=references)

## Funding

Open Access funding provided by University of Vaasa (UVA). Funding was provided by Liikesivistysrahasto.

## Author information

### Authors and Affiliations

1. University of Vaasa, Vaasa, Finland

Joni Salminen

2. Hanken School of Economics, Helsinki, Finland

Mekhail Mustak

3. University of Jyväskylä, Jyvaskyla, Finland

Muhammad Sufyan

4. Qatar Computing Research Institute, Hamad Bin Khalifa University, Doha, Qatar

Bernard J. Jansen


Authors

1. Joni Salminen


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Joni%20Salminen)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Joni%20Salminen) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Joni%20Salminen%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

2. Mekhail Mustak


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Mekhail%20Mustak)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Mekhail%20Mustak) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Mekhail%20Mustak%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

3. Muhammad Sufyan


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Muhammad%20Sufyan)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Muhammad%20Sufyan) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Muhammad%20Sufyan%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)

4. Bernard J. Jansen


[View author publications](https://link.springer.com/search?sortBy=newestFirst&contributor=Bernard%20J.%20Jansen)





Search author on:[PubMed](https://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=search&term=Bernard%20J.%20Jansen) [Google Scholar](https://scholar.google.co.uk/scholar?as_q=&num=10&btnG=Search+Scholar&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors=%22Bernard%20J.%20Jansen%22&as_publication=&as_ylo=&as_yhi=&as_allsubj=all&hl=en)


### Corresponding author

Correspondence to
[Joni Salminen](mailto:jonisalm@uwasa.fi).

## Ethics declarations

### Conflict of interest

On behalf of all authors, the corresponding author states that there is no conflict of interest.

## Additional information

### Publisher's Note

Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

## Rights and permissions

**Open Access** This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit [http://creativecommons.org/licenses/by/4.0/](http://creativecommons.org/licenses/by/4.0/).

[Reprints and permissions](https://s100.copyright.com/AppDispatchServlet?title=How%20can%20algorithms%20help%20in%20segmenting%20users%20and%20customers%3F%20A%20systematic%20review%20and%20research%20agenda%20for%20algorithmic%20customer%20segmentation&author=Joni%20Salminen%20et%20al&contentID=10.1057%2Fs41270-023-00235-5&copyright=The%20Author%28s%29&publication=2050-3318&publicationDate=2023-07-06&publisherName=SpringerNature&orderBeanReset=true&oa=CC%20BY)

## About this article

[![Check for updates. Verify currency and authenticity via CrossMark](<Base64-Image-Removed>)](https://crossmark.crossref.org/dialog/?doi=10.1057/s41270-023-00235-5)

### Cite this article

Salminen, J., Mustak, M., Sufyan, M. _et al._ How can algorithms help in segmenting users and customers? A systematic review and research agenda for algorithmic customer segmentation.
_J Market Anal_ **11**, 677–692 (2023). https://doi.org/10.1057/s41270-023-00235-5

[Download citation](https://citation-needed.springer.com/v2/references/10.1057/s41270-023-00235-5?format=refman&flavour=citation)

- Revised: 11 April 2023

- Accepted: 21 June 2023

- Published: 06 July 2023

- Version of record: 06 July 2023

- Issue date: December 2023

- DOI: https://doi.org/10.1057/s41270-023-00235-5


### Share this article

Anyone you share the following link with will be able to read this content:

Get shareable link

Sorry, a shareable link is not currently available for this article.

Copy shareable link to clipboard

Provided by the Springer Nature SharedIt content-sharing initiative


### Keywords

- [Customer segmentation](https://link.springer.com/search?query=Customer%20segmentation&facet-discipline=%22Business%20and%20Management%22)
- [Machine learning](https://link.springer.com/search?query=Machine%20learning&facet-discipline=%22Business%20and%20Management%22)
- [AI](https://link.springer.com/search?query=AI&facet-discipline=%22Business%20and%20Management%22)
- [Algorithms](https://link.springer.com/search?query=Algorithms&facet-discipline=%22Business%20and%20Management%22)

### Profiles

1. Mekhail Mustak [View author profile](https://link.springer.com/researchers/21305182SN)