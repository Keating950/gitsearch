# Gitsearch
Simple command line utility for searching and cloning repos from Github.
Move the cursor and turn pages with Vim-style hjkl inputs.
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

## TODO:
* Enable horizontal scrolling in path input window, enabling the input of paths
    longer than the input window is wide. 