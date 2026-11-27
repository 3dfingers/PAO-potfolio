# Problems found in messy_crm_v2.csv (1005 data rows)

Found by opening the file in VS Code (with Claude's help to list line numbers; I checked each by eye).

| # | Problem | Example (file line) |
|---|---|---|
| 1 | File starts with a BOM (UTF-8 with BOM) | line 1 |
| 2 | Status has padding spaces and mixed case ("  CHURNED  ", "  Active  ") | line 2 |
| 3 | Amount written as a word: none / NULL / N/A | lines 3, 8, 17 |
| 4 | Amount has spaces around it (" 3492.21 ") | line 4 |
| 5 | Negative amounts (-17.09) | line 5 |
| 6 | Amount has a £ sign (£352.43) | line 5 |
| 7 | Name contains a comma, in quotes ("Dubois, Søren") | line 6 |
| 8 | Non-ASCII names (Nørgaard, Hélène, Åke) | lines 4, 7 |
| 9 | Status empty | line 10 |
| 10 | £ amount with a thousands comma NOT in quotes (£2,683.75): it splits into two columns, so amount becomes "£2" and status becomes "683.75" | line 22 |
| 11 | Amount empty | line 26 |
| 12 | Extra column at the end (",EXTRA_FIELD") | line 43 |
| 13 | Blank line in the middle of the file | line 52 |
| 14 | Short row: status column missing completely | line 57 |
| 15 | Amount is not a number ("abc") | line 62 |
| 16 | Amount is just "£" | line 64 |
| 17 | Status not one of active/trial/churned (pending_approval, unknown, suspended, archived) | lines 88, 108, 113 |
| 18 | Name is only spaces ("   ") | line 166 |
| 19 | Same person's name appears with different ids (e.g. Alan Turing: ids 1119, 1138, 1177) | lines 121, 140, 180 |