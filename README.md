# Gitsearch
Simple command line utility for searching and cloning repos from Github.
Move the cursor with Vim-style hjkl inputs. Flip pages with Tab and Shift+Tab.
```
usage: gitsearch.py [-h] [--sort statistic] [--order asc, desc] [--lang lang] "query"

positional arguments:
  "query"            A quoted query string.

optional arguments:
  -h, --help         show this help message and exit
  --sort statistic   Sort by stars, forks, help-wanted-issues, or updated.
                     Default is best match.
  --order asc, desc  asc or desc. Default is descending.
  --lang lang        Restrict results by programming language.

```

## Roadmap
* Support for resizing terminal windows
* General UI polish
