# 2023-05-09-chep23-analysis-of-physicists

## Producing the talk PDF

The LaTeX sources for the talk are all in this repo; just `git clone` it and

```bash
pdflatex -halt-on-error -shell-escape main.tex
```

to make `main.pdf` (the talk).

## Reproducing the analysis

Actually doing the analysis would be more complex. This analysis pulls in data from many sources, so unfortunately, I can't provide a push-button reproducer like [reana](https://reanahub.io/) or [Galaxy](https://usegalaxy.org/) or something. You'll have to manually follow my instructions and make modifications for your system as you go along.

Before going into the main part ("Analysis of source code online"), I'd like to give you some pointers on how to do other types of analyses: "Download stats" and "Textual analysis of CHEP/ACAT".

### Download PyPI stats

For "Download stats", you can get [PyPI download counts from Google BigQuery](https://cloud.google.com/blog/topics/developers-practitioners/analyzing-python-package-downloads-bigquery/). After setting up your BigQuery account, `bigquery-public-data.pypi.file_downloads` is just an SQL table in the system whose [schema is described here](https://packaging.python.org/en/latest/guides/analyzing-pypi-package-downloads/). I have been using

```sql
SELECT
  DATE(timestamp) AS date,
  details.system.name AS os,
  REGEXP_EXTRACT(details.python, r"[0-9]+\.[0-9]+") AS python_version,
  file.project AS project,
  REGEXP_REPLACE(file.version, "\\.[0123456789]{1,}$", "") AS version,
  COUNT(*) AS count
FROM `bigquery-public-data.pypi.file_downloads`
WHERE
  DATE(timestamp)
    BETWEEN DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 65 MONTH), MONTH)
    AND CURRENT_DATE()
    AND (file.project = "uproot" OR
         file.project = "uproot3" OR
         file.project = "uproot4" OR
         file.project = "awkward" OR
         file.project = "awkward0" OR
         file.project = "awkward1")
  AND details.installer.name = "pip" -- Important!
GROUP BY project, version, date, os, python_version
ORDER BY project, version, date, os, python_version
```

to aggregate download counts by package + major.minor version numbers per day from the whole dataset (currently 21.76 TB). You can also include some very popular packages in the list, such as `file.project = "numpy"`, and the result won't be too huge because you get a CSV line per day, rather than per download.

Once you get the CSV, load it in a Pandas DataFrame and do whatever additional aggregations you want to do. If you want to be sensitive to package revision number (the third digit in the string), then you'll need to edit the SQL. I haven't used this on any packages that use CalVer-formatted versions, so you'd need to make some modifications there, too, or just don't reformat the version numbers at all: replace

```sql
REGEXP_REPLACE(file.version, "\\.[0123456789]{1,}$", "") AS version
```

with

```sql
file.version as version
```

There are ways to get download statistics from conda-forge as well, [as preaggregated Parquet files](https://gist.github.com/mariusvniekerk/eff538447e79d5c42c3abfc8d7d815f3) or [using a specialized tool](https://www.anaconda.com/blog/get-python-package-download-statistics-with-condastats), but I haven't tried that yet.

### Textual analysis of conferences

To make plots of regex matches in CHEP and ACAT talks, we can just download all of the titles and abstracts of all the CHEP, ACAT talks on [InspireHEP](https://inspirehep.net/). InspireHEP [has a JSON-REST API](https://blog.inspirehep.net/2020/06/we-released-the-new-inspire-api/) that is mercifully similar to the GUI web search: you can test searches in the webpage's search box, and when you have the set of results that you want, just modify the URL slightly to get a URL for `curl` or `wget`. The [API is described here](https://github.com/inspirehep/rest-api-doc).

Here's a query that I used for CHEP only:

```bash
curl -s 'https://inspirehep.net/api/literature?sort=mostrecent&size=250&page=1&q=%28publication_info.cnum%3AC85-06-25%20or%20publication_info.cnum%3AC87-02-02.2%20or%20publication_info.cnum%3AC89-04-10%20or%20publication_info.cnum%3AC90-04-09%20or%20publication_info.cnum%3AC91-03-11%20or%20publication_info.cnum%3AC92-09-21%20or%20publication_info.cnum%3AC94-04-21%20or%20publication_info.cnum%3AC95-09-18%20or%20publication_info.cnum%3AC97-04-07%20or%20publication_info.cnum%3AC98-08-31%20or%20publication_info.cnum%3AC00-02-07%20or%20publication_info.cnum%3AC01-09-03.1%20or%20publication_info.cnum%3AC03-03-24.1%20or%20publication_info.cnum%3AC04-09-27%20or%20publication_info.cnum%3AC06-02-13%20or%20publication_info.cnum%3AC07-09-02.1%20or%20publication_info.cnum%3AC09-03-21%20or%20publication_info.cnum%3AC10-10-18.4%20or%20publication_info.cnum%3AC12-05-21.3%20or%20publication_info.cnum%3AC13-10-14.1%20or%20publication_info.cnum%3AC15-04-13%20or%20publication_info.cnum%3AC16-10-14%20or%20publication_info.cnum%3AC18-07-09.6%20or%20publication_info.cnum%3AC19-11-04%20or%20publication_info.cnum%3AC21-05-17.1%29' 2>&1 > all-chep-papers-page1.json
```

It's pagenated: the `page=1` in the query gives you the first 250 results; you have to run the above with `page=2` etc. up to `page=23` to get all of the data. (You'll know you're done when there are no more results.

My query for ACAT was

```bash
curl -s 'https://inspirehep.net/api/literature?sort=mostrecent&size=250&page=1&q=%28publication_info.cnum%3AC90-03-19%20or%20publication_info.cnum%3AC92-01-13.1%20or%20publication_info.cnum%3AC94-04-21%20or%20publication_info.cnum%3AC95-04-03%20or%20publication_info.cnum%3AC96-09-02.4%20or%20publication_info.cnum%3AC99-04-12%20or%20publication_info.cnum%3AC00-10-16.1%20or%20publication_info.cnum%3AC02-06-24.3%20or%20publication_info.cnum%3AC03-12-01.2%20or%20publication_info.cnum%3AC05-05-22%20or%20publication_info.cnum%3AC07-04-23.1%20or%20publication_info.cnum%3AC08-11-03.1%20or%20publication_info.cnum%3AC10-02-22%20or%20publication_info.cnum%3AC11-09-05.3%20or%20publication_info.cnum%3AC13-05-16%20or%20publication_info.cnum%3AC14-09-01.1%20or%20publication_info.cnum%3AC16-01-18.1%20or%20publication_info.cnum%3AC17-08-21%20or%20publication_info.cnum%3AC19-03-11%20or%20publication_info.cnum%3AC21-11-29%29' 2>&1 > acat-papers-page-1.json
```

up to `page=9`.

These conference are the IDs for the first 25 CHEPs:

 * `"C85-06-25"`
 * `"C87-02-02.2"`
 * `"C89-04-10"`
 * `"C90-04-09"`
 * `"C91-03-11"`
 * `"C92-09-21"`
 * `"C94-04-21"`
 * `"C95-09-18"`
 * `"C97-04-07"`
 * `"C98-08-31"`
 * `"C00-02-07"`
 * `"C01-09-03.1"`
 * `"C03-03-24.1"`
 * `"C04-09-27"`
 * `"C06-02-13"`
 * `"C07-09-02.1"`
 * `"C09-03-21"`
 * `"C10-10-18.4"`
 * `"C12-05-21.3"`
 * `"C13-10-14.1"`
 * `"C15-04-13"`
 * `"C16-10-14"`
 * `"C18-07-09.6"`
 * `"C19-11-04"`
 * `"C21-05-17.1"`

and these are the conference IDs for the first 20 ACATs:

 * `C90-03-19`
 * `C92-01-13.1`
 * `C94-04-21`
 * `C95-04-03`
 * `C96-09-02.4`
 * `C99-04-12`
 * `C00-10-16.1`
 * `C02-06-24.3`
 * `C03-12-01.2`
 * `C05-05-22`
 * `C07-04-23.1`
 * `C08-11-03.1`
 * `C10-02-22`
 * `C11-09-05.3`
 * `C13-05-16`
 * `C14-09-01.1`
 * `C16-01-18.1`
 * `C17-08-21`
 * `C19-03-11`
 * `C21-11-29`

After that, you have to find the titles and abstracts in the JSON: lots of Python for loops! [Here](https://github.com/jpivarski-talks/2022-03-04-reload-statistics/blob/main/chep-papers.ipynb) and [here](https://github.com/jpivarski-talks/2022-03-04-reload-statistics/blob/main/acat-papers.ipynb) are two Jupyter notebooks that do that (not in this repo, but a previous one).

### Analysis of source code

(Skim this section before following all of the instructions. If you're looking for exactly the same dataset that I used in the talk, it's downloadable from an S3 bucket and you can skip a lot of these steps.)

The first step of the large source code analysis uses the [GitHub API](https://docs.github.com/en/rest). It's similar to the InspireHEP API (above) in that it's a REST API: you have to deal with pagination and parsing JSON. One additional difficulty is that GitHub applies a rate-limit to your frequency of requests to prevent it from being abused. If you're going to be repeating this step, you'll need a [GitHub token](https://github.com/settings/tokens) with at least the following permissions: `read:packages` and `read:user`. You can pass these to `curl` with

```bash
curl -u USERNAME:TOKEN ...
```

where `USERNAME` is your GitHub login name and `TOKEN` is the secret that the tokens-generator shows you once and never again. Since this is such a weak token (can only read public package and user data), I don't mind it getting into my bash history.

You can check your current rate limit status with

```bash
curl -s -u USERNAME:TOKEN https://api.github.com/rate_limit
```

To get a list of all forks of CMSSW, I used

```bash
for x in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38; do curl -s -D/dev/stderr -u USERNAME:TOKEN 'https://api.github.com/repos/cms-sw/cmssw/forks?per_page=100&page='$x > cmssw-users/page-$x.json; wc cmssw-users/page-$x.json; sleep 1; done
```

The `wc` command lets me know when I've reached the end of the populated pages, and `sleep 1` prevents me from hitting a secondary rate limit (beyond the usual rate limit that GitHub reports).

The results in `cmssw-users/page-*.json` is a list of repos (the CMSSW forks themselves), but each JSON record has an `"owner"` with a `"login"` that is the userid.

I extracted these (interactively) into a plain text file with one username per line called `usernames.txt` and then did

```bash
for username in `cat usernames.txt`; do curl -s -u USERNAME:TOKEN 'https://api.github.com/users/'$username'/repos?per_page=100' >> user-repos/$username.json; wc user-repos/$username.json; sleep 1; done
```

to get all of the users' repos. Since the (currently) 3697 users means 3697 separate GitHub API requests, you really use your rate limit. You get to do 5000 requests per hour, so you might want to wait to start this after a rate limit refresh.

Next, you'll want to `git clone` all of those repos. Do this where you have at least 1.2 TB of disk space. To make all of the `git clone` commands, I used these lines of Python:

```python
import json, glob
everything = [json.load(open(x)) for x in glob.glob("user-repos/*")]
open("git-clone-user-repos", "w").write("\n".join(f"mkdir -p {y['owner']['login']}\ngit clone {y['git_url'].replace('git://', 'https://')} {y['full_name']}" for x in everything for y in x if not y['fork']) + "\n")
```

and then `git-clone-user-repos` is a shell script that makes a two-level directory structure: `user/repo` and clones them all. Even though this is a much larger transfer of data, it has no rate limit that I'm aware of.

Now you have a lot of local git directories. Most of the analyses used time as an independent variable, but the UNIX time of files in these directories is not the time of last modification in git. Therefore, I used

```bash
for x in */*; do cd $x; git rev-parse --show-toplevel | sed 's/\/mnt\/actual-repos\//REPO: /' >> ~/file-last-touch.txt ; git ls-tree -r --name-only HEAD -z | TZ=UTC xargs -0n1 -I_ git --no-pager log -1 --date=iso-local --format="%ad _" -- _ >> ~/file-last-touch.txt ; cd ../.. ; done
```

to iterate through all of the `user/repo` directories and collect the last-touch times of all their files (in their main-branch state: doesn't include files that used to exist in the git history). The output file, `~/file-last-touch.txt`, looks like this:

```
REPO: 1/24LopezR/Cosmics-Analyzer
2023-02-01 15:01:05 +0000 2023-02-01 15:01:05 +0000 d273c383aa98bb1a9bb9470f783149ed77c6cf9a .gitignore
2023-02-01 15:01:05 +0000 2023-02-01 15:01:05 +0000 d273c383aa98bb1a9bb9470f783149ed77c6cf9a config/nDThits.txt
2023-02-01 15:01:05 +0000 2023-02-01 15:01:05 +0000 d273c383aa98bb1a9bb9470f783149ed77c6cf9a config/nhits.txt
2023-02-01 15:01:05 +0000 2023-02-01 15:01:05 +0000 d273c383aa98bb1a9bb9470f783149ed77c6cf9a config/one_down_muon.txt
2023-02-01 15:01:05 +0000 2023-02-01 15:01:05 +0000 d273c383aa98bb1a9bb9470f783149ed77c6cf9a config/phig0.txt
2023-02-01 15:01:05 +0000 2023-02-01 15:01:05 +0000 d273c383aa98bb1a9bb9470f783149ed77c6cf9a config/phil0.txt
2023-02-01 15:01:05 +0000 2023-02-01 15:01:05 +0000 d273c383aa98bb1a9bb9470f783149ed77c6cf9a config/spikes.txt
2023-02-01 15:01:05 +0000 2023-02-01 15:01:05 +0000 d273c383aa98bb1a9bb9470f783149ed77c6cf9a config/trigger.txt
2023-02-14 12:19:57 +0000 2023-02-14 12:19:57 +0000 af2c4a0f97600ba93671c26bf08237af64cf8040 fill.py
...
```

Note: this is a computationally expensive step! I split it into 16 jobs on a 16-core machine (filling `~/file-last-touch-1.txt`, etc.) and it ran overnight.

Once these file last-touch times have been collected, they can be converted into the format used in this repo's Jupyter notebooks using [analysis/gather-file-ages.py](analysis/gather-file-ages.py). The author-time, committer-time (which happens to be the same), and last commit hash are all put into a JSON list, with repo name and file name being keys of nested JSON dicts to look them up. The analysis only uses the author-time, so if you're having troubles with a `git` version (like I did, in the ROOT-seeded analysis) and it only gives you author-time, that's fine. Just change `gather-file-ages.py` to ignore the unused list items.

(In the future, we could consider doing an analysis of time-slices, using all of the git information, not just the time of last file-touch. It would be very computationally expensive, but easier to interpret. Instead of each file or repo being an entry in the time-histogram, which can migrate time-bins as files and repos change on GitHub, each time-bin would describe the state of the files that existed at that time. The same file would contribute to multiple bins, as it continues to exist, but as files and repos change, the past time-slices wouldn't change. We're also not considering any git branches other than the one that led to the present `HEAD`.)

Before downloading it, I removed

 * the `.git` directory from every repo
 * all non-source files larger than 1 MB

using

```bash
rm -rf */*/.git
find . -type f -not \( -name "*.py" -o -name "*.PY" -o -name "*.ipynb" -o -name "*.IPYNB" -o -name "*.c" -o -name "*.cc" -o -name "*.cpp" -o -name "*.cp" -o -name "*.cxx" -o -name "*.c++" -o -name "*.C" -o -name "*.CC" -o -name "*.CPP" -o -name "*.CP" -o -name "*.CXX" -o -name "*.C++" -o -name "*.h" -o -name "*.hpp" -o -name "*.hp" -o -name "*.hh" -o -name "*.H" -o -name "*.HPP" -o -name "*.HP" -o -name "*.HH" \) -size +1M -delete
```

and made a compressed tarball of each repo individually. Then I made an uncompressed tarball of all the compressed tarballs, just to have only one file to transfer.

**Here's where I say that you may just skip all of the work described above.** The `file-ages.json` and tarball of all repos are publicly available for download:

 * 110.5 MB [https://pivarski-princeton.s3.amazonaws.com/GitHub-CMSSW-user-nonfork-raw-data-1Mcut-ages.json.gz](https://pivarski-princeton.s3.amazonaws.com/GitHub-CMSSW-user-nonfork-raw-data-1Mcut-ages.json.gz), the `file-ages.json` for the CMSSW-seeded analysis
 * 82.7 GB [https://pivarski-princeton.s3.amazonaws.com/GitHub-CMSSW-user-nonfork-raw-data-1Mcut.tar](https://pivarski-princeton.s3.amazonaws.com/GitHub-CMSSW-user-nonfork-raw-data-1Mcut.tar), the tarball of repos for the CMSSW-seeded analysis
 * 40.3 MB [https://pivarski-princeton.s3.amazonaws.com/GitHub-ROOT-user-nonfork-raw-data-1Mcut-ages.json.gz](https://pivarski-princeton.s3.amazonaws.com/GitHub-ROOT-user-nonfork-raw-data-1Mcut-ages.json.gz), the `file-ages.json` for the ROOT-seeded analysis
 * 44.3 GB [https://pivarski-princeton.s3.amazonaws.com/GitHub-ROOT-user-nonfork-raw-data-1Mcut.tar](https://pivarski-princeton.s3.amazonaws.com/GitHub-ROOT-user-nonfork-raw-data-1Mcut.tar)

The Jupyter notebooks in the [analysis](analysis) directory assume that you have the file ages uncompressed in a file named `file-ages.json` and the outer layer of tarball untarred—that is, a director full of files like `user/repo.tgz`. When the Jupyter notebooks iterate over git repos, they use Python's `tarfile` library to uncompress them in memory, rather than on disk.

Warning! Untar those tarballs in a new, empty directory. They will create thousands of `user` directories, which can be hard to disentangle from a directory with important stuff in it.

(Once you have uncompressed the `file-ages.json` files and untarred the uncompressed tarball, the [analysis/check-file-ages.py](analysis/check-file-ages.py) can tell you how many files in `file-ages.json` are not in the repo data.)

The instructions above were about the CMSSW-seeded analysis. The ROOT-seeded analysis has an additional step: we have to get the list of users from the [GitHub Archive](https://www.gharchive.org/), which is a public dataset in Google BigQuery like the PyPI downloads, above.

Although it would be possible to do an interesting social-network graph analysis with these data (selectively using the GitHub Archive [event types](https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads)), I just dumped usernames of everyone who touched the ROOT repo, with times (which I didn't use).

```sql
SELECT type, actor.login, org.login, created_at FROM `githubarchive.year.20*` WHERE repo.name = 'root-project/root';
```

(Selecting `githubarchive.year.20*` tables gets all of them because the archive only dates back to 2017. In fact, GitHub itself is entirely 21st century.)

The three Jupyter notebooks, [analysis/analysis-1.ipynb](analysis/analysis-1.ipynb), [analysis/analysis-2.ipynb](analysis/analysis-2.ipynb), and [analysis/analysis-3.ipynb](analysis/analysis-3.ipynb), assume that these source files are in particular directories (prefixed by `/home/jpivarski`), so you'll need to do some edits. These notebooks create new files used by subsequent notebooks, so the order matters.

Also, rather early in the first notebook, there's a cut against "fake non-forks." We had selected repos in which GitHub's `"fork"` boolean was set to `false`, but still some repos are clearly not the user's own. This isn't a big deal for plots in which each repo counts with a weight of 1, but some of the new plots count each _file_ with a weight of 1, and the fake non-forks have a lot of files in them. At first (see notebook), I thought I could identify them by variance of file ages, thinking that users just copy-pasted all of the files at once, but no: in all cases that I saw, they preserved the git history. The file dates are therefore a broad distribution, but fake non-forks can be distinguished by the committer names, which are not equal to the user who owns the repo.

The GitHub API has a way to get a list of contributors, though it's one request per repo, and it would take a long time to ask for this information for tens of thousands of repos, due to the rate limit. Therefore, I selected only the ones whose `"size"` is greater than `10000`. I don't know what the units are on this size, whether it represents compressed or uncompressed, whether it includes history (though it very likely does), but this cut selects the top 10% or so of repos, which are the only ones I'm worried about anyway. [analysis/analysis-1.ipynb](analysis/analysis-1.ipynb) uses the output of these files to plot the "fraction of commits self-authored" with a peak below 1%, representing the fake non-forks. The notebook explicitly lists the repos that go into `cmssw_repo_exclude` and `root_repo_exclude`, but for completeness, I've also made the GitHub API contributor data downloadable:

 * 949.4 KB [https://pivarski-princeton.s3.amazonaws.com/GitHub-CMSSW-user-nonfork-raw-data-1Mcut-contributors.tgz](https://pivarski-princeton.s3.amazonaws.com/GitHub-CMSSW-user-nonfork-raw-data-1Mcut-contributors.tgz)
 * 570.3 KB [https://pivarski-princeton.s3.amazonaws.com/GitHub-ROOT-user-nonfork-raw-data-1Mcut-contributors.tgz](https://pivarski-princeton.s3.amazonaws.com/GitHub-ROOT-user-nonfork-raw-data-1Mcut-contributors.tgz)

### User bios word clouds

This is another use of the GitHub API. Starting from the list of user names in `usernames.txt`, I requested every user's profile.

```bash
for x in `cat usernames.txt`; do echo $x; if ! test -f user-profiles/$x.json; then curl -s -u USERNAME:TOKEN  https://api.github.com/users/$x > user-profiles/$x.json ; sleep 0.2; fi; done
```

This shell script has `if ! test -f user-profiles/$x.json; then curl ...` in it so that I could stop it and restart it when it got stuck. It consists of thousands of HTTP requests.

I pulled the `"bio"` field out of each profile, ran a stop-word analysis on it using [NLTK](https://www.nltk.org/),

```python
import nltk.tokenize, nltk.corpus, string, json, glob
stopwords = set(nltk.corpus.stopwords.words("english")).union(set(string.punctuation))
bios = [json.load(open(filename)).get("bio") for filename in glob.glob("user-profiles/*.json")]
bios = [x for x in bios if x is not None and x != ""]
" ".join([x for x in nltk.tokenize.word_tokenize(" ".join(bios).lower()) if x not in stopwords])
```

and then pasted the resulting text into [https://www.jasondavies.com/wordcloud/](https://www.jasondavies.com/wordcloud/). I used the **Archimedean** spiral, **√n** scale, **5** orientations from **-30** to **30** degrees, **250** words, set the font to **sans** and downloaded an SVG. It is important to pick a boring font like **sans**, or else the SVG will be unreadable.

## That's everything!

As you can see, it would be a lot of effort to reproduce this analysis exactly the way it was done before, but I think it would be more interesting to make improvements, anyway. Some of these steps could be formalized into push-button machinery, but large disk and compute resources would be needed to do that routinely.
