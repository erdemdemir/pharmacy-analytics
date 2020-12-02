# TODO List

## England Pharmacy Dispensing Data EDA (29/11/2020)

**Code a helper function**

- [ ] I should write a function to extend `describe()` with skewness
- [ ] I can extend this function with dataframe comparison instead of running the same function one after another like above.

**Go out and find out**

- [ ] I have no idea if that's relevant or not, but I want to check sometime later why these pharmacies have that many months with zero items.
- [ ] Just curious. How is DispenserCode assigned? Can it be assigned to a new pharmacy, when the old one is closed?
- [ ] What happened to Multiples after the end of 2016?
- [ ] What happened between June - August 2019 to Independents and Multiples?

**Get more data to answer the following questions**

- [ ] How is the number of dispensers across the years is related to the number of pharmacists registered with the GPHC? I should get in contact with the GPHC to ask for more data.
- [ ] Which group of medications are used more, and which are used less during the Covid-10 era?
- [ ] Item numbers are growing every year. Is the growth of items proportional to population growth?

**Consider later**
- [ ] Extend dispensers table using Postcode information, then perform a location-based analysis
- [ ] I should consider downloading [CPPQs (Community Pharmacy Patient Questionnaire)](https://psnc.org.uk/contract-it/essential-service-clinical-governance/cppq/) from NHS website. The age range of customers might an interesting addition to the dataset.