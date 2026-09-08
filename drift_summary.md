# Synthèse drift — PSI · KS · Chi²

Repères conventionnels PSI : < 0.10 signal faible, 0.10–0.25 signal à investiguer, > 0.25 signal fort.
Ce sont des heuristiques de place, pas des lois statistiques : un chiffre n'est pas un verdict.

| Feature | Type | Calcul | Verdict | Interprétation |
|---|---|---|---|---|
| `int_rate` | numerique | PSI=0.444 ; KS p=4.63e-65 | dérive | signal fort (PSI > 0.25) ; KS significatif (p<0.05) |
| `grade` | categorielle | Chi2 p=3.65e-07 | dérive | Chi² significatif (p<0.05) : répartition des modalités différente |
| `revol_util` | numerique | PSI=0.187 ; KS p=3.82e-20 | suspect | à investiguer (PSI 0.10-0.25) ; KS significatif (p<0.05) |
| `annual_inc` | numerique | PSI=0.067 ; KS p=2.28e-09 | stable | signal faible (PSI < 0.10) ; KS significatif (p<0.05) |
| `installment` | numerique | PSI=0.015 ; KS p=0.663 | stable | signal faible (PSI < 0.10) ; KS non significatif |
| `dti` | numerique | PSI=0.011 ; KS p=0.11 | stable | signal faible (PSI < 0.10) ; KS non significatif |
| `fico_range_low` | numerique | PSI=0.007 ; KS p=0.489 | stable | signal faible (PSI < 0.10) ; KS non significatif |
| `loan_amnt` | numerique | PSI=0.003 ; KS p=0.989 | stable | signal faible (PSI < 0.10) ; KS non significatif |
| `term` | categorielle | Chi2 p=0.316 | stable | Chi² non significatif : répartition des modalités stable |
| `emp_length` | categorielle | Chi2 p=0.492 | stable | Chi² non significatif : répartition des modalités stable |
| `home_ownership` | categorielle | Chi2 p=0.631 | stable | Chi² non significatif : répartition des modalités stable |
| `verification_status` | categorielle | Chi2 p=0.586 | stable | Chi² non significatif : répartition des modalités stable |
| `purpose` | categorielle | Chi2 p=0.199 | stable | Chi² non significatif : répartition des modalités stable |
