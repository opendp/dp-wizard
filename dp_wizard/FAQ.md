### What does DP Wizard do?

DP Wizard guides you through the application of differential privacy.
After selecting a local CSV, you'll be prompted to describe the analysis you need.
Output options include:
- A Jupyter notebook which demonstrates how to use
the [OpenDP Library](https://docs.opendp.org/).
- A plain Python script.
- Text and CSV reports.

### Does differential privacy provide anonymization?

Yes and no.

Interpretted narrowly, anonymization describes a particular way of protecting sensitive information, by dropping any identifying information before beginning an analysis, while differential privacy (as implemented by DP Wizard) adds noise to the final results.
They are different approaches.

However, if you don't select any columns with identifying information for analysis in DP Wizard, you are effectively using anonymization _and_ differential privacy: The techniques can be combined.

Moreover, anonymization should not be taken as a gold standard:
Even if the obvious identifiers have been stripped, there may be combinations of fields that can link records back to individuals or small groups.
In this light, if there is a requirement for anonymization it is worth asking if the intent is to prescribe a particular approach, or to ensure that personal information is protected by some means.

### Where can I learn more?

One place to begin is [this slideshow](https://opendp.github.io/dp-wizard):
it provides an introduction to differential privacy and DP Wizard, with some group exercises along the way.
At the end there are suggestions for further reading.

### How can I report bugs or request features?

If you are not on github, feel free to [email the maintainer](cmccallum@g.harvard.edu) directly.
If you are on github, please [file an issue](https://github.com/opendp/dp-wizard/issues/new/choose).
Thank you for the feedback!
