# -*- coding: utf-8 -*-
# =============================================================================
# SPSS Accessibility Plugin - bilingual statistics glossary
#
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Bouronikos Christos
# This file is covered by the GNU General Public License v2.
# =============================================================================

"""A glossary of statistical terms spoken by the read-glossary command.

Terms are grounded in the IBM SPSS Statistics 31 Base and Core System guides.
Each entry gives a short, plain-language definition, so a user unfamiliar
with a statistic can still follow what SPSS reported.
"""

from .core import node as N


GLOSSARY = (
	N(u"Mean", u"Μέσος όρος", u"The arithmetic average: the sum of the values divided by how many there are.", u"Ο αριθμητικός μέσος: το άθροισμα των τιμών διά το πλήθος τους."),
	N(u"Median", u"Διάμεσος", u"The middle value when the data are sorted; half the cases fall above it and half below.", u"Η μεσαία τιμή όταν τα δεδομένα ταξινομηθούν· οι μισές περιπτώσεις βρίσκονται πάνω και οι μισές κάτω από αυτήν."),
	N(u"Mode", u"Επικρατούσα τιμή", u"The value that occurs most often.", u"Η τιμή που εμφανίζεται πιο συχνά."),
	N(u"Standard deviation", u"Τυπική απόκλιση", u"A measure of how spread out the values are around the mean. In a normal distribution, about 68 percent of cases fall within one standard deviation of the mean.", u"Μέτρο του πόσο διασκορπισμένες είναι οι τιμές γύρω από τον μέσο. Σε κανονική κατανομή, περίπου το 68% των περιπτώσεων βρίσκεται εντός μίας τυπικής απόκλισης από τον μέσο."),
	N(u"Variance", u"Διακύμανση", u"The standard deviation squared; also a measure of spread, in squared units.", u"Το τετράγωνο της τυπικής απόκλισης· επίσης μέτρο διασποράς, σε τετραγωνικές μονάδες."),
	N(u"Standard error", u"Τυπικό σφάλμα", u"An estimate of how much a statistic, such as the mean, would vary from sample to sample.", u"Εκτίμηση του πόσο θα διέφερε μια στατιστική, όπως ο μέσος, από δείγμα σε δείγμα."),
	N(u"Confidence interval", u"Διάστημα εμπιστοσύνης", u"A range that is likely to contain the true population value, at a stated confidence level such as 95 percent.", u"Εύρος τιμών που πιθανώς περιέχει την πραγματική τιμή του πληθυσμού, σε δεδομένο επίπεδο εμπιστοσύνης, π.χ. 95%."),
	N(u"Significance level", u"Επίπεδο σημαντικότητας", u"Also called the p-value. The probability of seeing a result this extreme if there were really no effect. A common cutoff is 0.05.", u"Επίσης γνωστό ως τιμή p. Η πιθανότητα να παρατηρηθεί τόσο ακραίο αποτέλεσμα αν πραγματικά δεν υπήρχε επίδραση. Συνηθισμένο όριο είναι το 0.05."),
	N(u"Degrees of freedom", u"Βαθμοί ελευθερίας", u"A number related to the sample size that a statistical test uses to judge significance, usually shown as df.", u"Αριθμός σχετιζόμενος με το μέγεθος δείγματος, που χρησιμοποιεί ένας στατιστικός έλεγχος για να κρίνει τη σημαντικότητα, συνήθως ως df."),
	N(u"T test", u"Έλεγχος t", u"A statistical test that compares means, using the t distribution to judge whether a difference is likely to be real.", u"Στατιστικός έλεγχος που συγκρίνει μέσους, χρησιμοποιώντας την κατανομή t για να κρίνει αν μια διαφορά είναι πιθανώς πραγματική."),
	N(u"Chi-square", u"Χι-τετράγωνο", u"A statistic that tests whether observed category counts differ from what would be expected.", u"Στατιστική που ελέγχει αν τα παρατηρούμενα πλήθη κατηγοριών διαφέρουν από τα αναμενόμενα."),
	N(u"Correlation coefficient", u"Συντελεστής συσχέτισης", u"A number between -1 and 1 that measures how strongly two variables move together. Near 0 means little relationship; near 1 or -1 means a strong relationship.", u"Αριθμός μεταξύ -1 και 1 που μετρά πόσο ισχυρά συνδέονται δύο μεταβλητές. Κοντά στο 0 σημαίνει ασθενή σχέση· κοντά στο 1 ή -1 σημαίνει ισχυρή σχέση."),
	N(u"R squared", u"R τετράγωνο", u"In regression, the proportion of variance in the outcome that is explained by the predictors, from 0 to 1.", u"Στην παλινδρόμηση, το ποσοστό της διακύμανσης του αποτελέσματος που εξηγείται από τους προβλέπτες, από 0 έως 1."),
	N(u"Regression coefficient", u"Συντελεστής παλινδρόμησης", u"How much the outcome is predicted to change for a one-unit change in a predictor, holding the other predictors constant.", u"Πόσο προβλέπεται να αλλάξει το αποτέλεσμα για μία μονάδα αλλαγής σε έναν προβλέπτη, κρατώντας σταθερούς τους υπόλοιπους."),
	N(u"Odds ratio", u"Λόγος πιθανοτήτων", u"In logistic regression, how much the odds of the outcome multiply for a one-unit change in a predictor.", u"Στη λογιστική παλινδρόμηση, πόσο πολλαπλασιάζονται οι πιθανότητες του αποτελέσματος για μία μονάδα αλλαγής σε έναν προβλέπτη."),
	N(u"Skewness", u"Ασυμμετρία", u"How asymmetric a distribution is. Zero means symmetric; positive means a longer tail on the high side.", u"Πόσο ασύμμετρη είναι μια κατανομή. Μηδέν σημαίνει συμμετρική· θετική τιμή σημαίνει μεγαλύτερη ουρά προς τις υψηλές τιμές."),
	N(u"Kurtosis", u"Κύρτωση", u"How peaked or flat a distribution is compared to a normal distribution.", u"Πόσο αιχμηρή ή επίπεδη είναι μια κατανομή σε σχέση με την κανονική κατανομή."),
	N(u"Outlier", u"Ακραία τιμή", u"A case with a value very different from the rest of the data, which can affect statistics like the mean.", u"Περίπτωση με τιμή πολύ διαφορετική από το υπόλοιπο των δεδομένων, που μπορεί να επηρεάσει στατιστικά όπως τον μέσο."),
	N(u"Cronbach's alpha", u"Άλφα του Cronbach", u"A reliability coefficient that shows how consistently a set of items measures the same underlying idea, from 0 to 1.", u"Συντελεστής αξιοπιστίας που δείχνει πόσο συνεπώς ένα σύνολο ερωτημάτων μετρά την ίδια υποκείμενη έννοια, από 0 έως 1."),
	N(u"Effect size", u"Μέγεθος επίδρασης", u"A standardized measure of how large a difference or relationship is, independent of sample size, for example Cohen's d.", u"Τυποποιημένο μέτρο του πόσο μεγάλη είναι μια διαφορά ή σχέση, ανεξάρτητα από το μέγεθος δείγματος, π.χ. το Cohen's d."),
	N(u"Levene's test", u"Έλεγχος Levene", u"A test of whether two or more groups have equal variance, often checked before a t test or ANOVA.", u"Έλεγχος για το αν δύο ή περισσότερες ομάδες έχουν ίση διακύμανση, που συχνά ελέγχεται πριν από t test ή ANOVA."),
	N(u"ANOVA", u"Ανάλυση διακύμανσης (ANOVA)", u"Analysis of variance: a technique that compares means across three or more groups at once.", u"Τεχνική που συγκρίνει μέσους σε τρεις ή περισσότερες ομάδες ταυτόχρονα."),
	N(u"Missing value", u"Ελλείπουσα τιμή", u"A value SPSS treats as unknown or not applicable, either because it is blank (system-missing) or because it matches a value you defined as missing.", u"Τιμή που το SPSS αντιμετωπίζει ως άγνωστη ή μη εφαρμόσιμη, είτε γιατί είναι κενή (system-missing) είτε γιατί ταιριάζει με τιμή που ορίσατε ως ελλείπουσα."),
	N(u"Value label", u"Ετικέτα τιμής", u"A human-readable name attached to a coded data value, for example 1 equals Male.", u"Ευανάγνωστο όνομα που αποδίδεται σε κωδικοποιημένη τιμή δεδομένων, για παράδειγμα 1 ίσον Άνδρας."),
	N(u"Frequency", u"Συχνότητα", u"How many cases have a particular value.", u"Πόσες περιπτώσεις έχουν συγκεκριμένη τιμή."),
	N(u"Percentile", u"Εκατοστημόριο", u"The value below which a given percentage of the data falls, for example the 90th percentile.", u"Η τιμή κάτω από την οποία βρίσκεται δεδομένο ποσοστό των δεδομένων, π.χ. το 90ό εκατοστημόριο."),
	N(u"Quartile", u"Τεταρτημόριο", u"One of the three values that split ordered data into four equal-sized groups.", u"Μία από τις τρεις τιμές που χωρίζουν τα ταξινομημένα δεδομένα σε τέσσερις ίσες ομάδες."),
	N(u"Bootstrap", u"Bootstrap", u"A resampling method that estimates how much a statistic would vary, without assuming a particular distribution.", u"Μέθοδος επαναδειγματοληψίας που εκτιμά πόσο θα διέφερε μια στατιστική, χωρίς να προϋποθέτει συγκεκριμένη κατανομή."),
	N(u"Nonparametric test", u"Μη παραμετρικός έλεγχος", u"A statistical test that does not assume the data follow a normal distribution.", u"Στατιστικός έλεγχος που δεν προϋποθέτει ότι τα δεδομένα ακολουθούν κανονική κατανομή."),
	N(u"Case", u"Περίπτωση", u"One row of data, usually one respondent, subject, or observation.", u"Μία γραμμή δεδομένων, συνήθως ένας ερωτηθείς, υποκείμενο ή παρατήρηση."),
	N(u"Variable", u"Μεταβλητή", u"One column of data, representing one measured characteristic.", u"Μία στήλη δεδομένων, που αντιπροσωπεύει ένα μετρούμενο χαρακτηριστικό."),
)
