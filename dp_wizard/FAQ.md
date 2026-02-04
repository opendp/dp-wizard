### What does DP Wizard do?

DP Wizard guides you through the application of differential privacy.
After selecting a local CSV, you'll be prompted to describe the analysis you need.
Output options include:
- A Jupyter notebook which demonstrates how to use
the [OpenDP Library](https://docs.opendp.org/).
- A plain Python script.
- Text and CSV reports.

### Does differential privacy provide anonymization?

This is one definition of anonymization:

> Anonymisation is the way in which you turn personal data into anonymous information, so that it then falls outside the scope of data protection law. You can consider data to be effectively anonymised if people are not (or are no longer) identifiable.
>
> We use the broad term ‘anonymisation’ to cover the techniques and approaches you can use to prevent identifying people that the data relates to.

(From the UK Information Commissioner's Office [_Introduction to Anonymisation_](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/introduction-to-anonymisation/#whatisanonymisation))

Differential privacy, used appropriately, may provide anonymization, but just as with other anonymization techniques it needs to be applied carefully.

It may be helpful to compare the vulnerabilities of different anonymization techniques:
If indentifying values are dropped from datasets for anonymization, that may not be sufficient if other combinations of individual characteristics are still distinctive.
In contrast, differential privacy does not have this particular vulnerability, but it does present other challenges: successive DP releases on the same dataset will expose incrementally more information and consume a larger privacy budget.

Anonymization requirements vary legal regimes, data domains, and end uses, and any approach to anonymization should be reviewed by an expert who understands your particular requirements.

### How do I choose a privacy budget?

It may be helpful to make transparent the competing needs for accuracy and privacy.
Accuracy may be the easier one:
The confidence margins that result from additional noise can often be precisely characterized.
You should not use a larger budget than necessary for your analysis.

The privacy requirements on the other hand can not be reduced to a number.
Although the epsilon value has a definition as a log-odds ratio, it embodies worst case assumptions, and doesn't take into account legal requirements, or possible harms to the individuals involved.

These tradeoffs are not unique to differential privacy: _Any_ disclosure of information carries with it a risk of revealing personal information. One strength of differential privacy is that it makes this tradeoff more clear.

### Can synthetic data from DP Wizard be used for analysis?

Synthetic data has certainly been used for analysis when individual privacy needs to be preserved. The 2020 US Census is a notable example of a synthetic data product.

However, conducting an analysis on synthetic data is not the only possibility:
It can also be used as a proxy.
Analyses can be prepared against the synthetic dataset, and then once the bugs have been worked out, the analysis can be run against the real data in a protected environment.
Whether this is feasible will depend on your organizational constraints.

One thing to remember is that the synthetic data is derived from the contingency table, and if a question can be answered directly from the contingency table, that is usually better.
Contingency tables also make assumptions like bin ranges transparent to the user.


### Where can I learn more?

One place to begin is [this slideshow](https://opendp.github.io/dp-wizard):
it provides an introduction to differential privacy and DP Wizard, with some group exercises along the way.
At the end there are suggestions for further reading.

### How can I report bugs or request features?

If you are not on github, feel free to [email the maintainer](cmccallum@g.harvard.edu) directly.
If you are on github, please [file an issue](https://github.com/opendp/dp-wizard/issues/new/choose).
Thank you for the feedback!
