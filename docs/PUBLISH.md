# Publish this extracted repository

The prepared local repository uses branch `main`. Its intended GitHub home is
`CC-David-CC/strata-control-lab`. It is a fresh repository, not another Strata
engine branch.

[Create the empty public repository on GitHub](https://github.com/new?owner=CC-David-CC&name=strata-control-lab&visibility=public&description=Offline-first%20visual%20experiments%20for%20logprobs%2C%20grammar%20and%20model%20control).

Check the owner and name. Leave **Add README**, **Add .gitignore**, and **Choose a
license** unselected: those files are already in this local commit. Then click
**Create repository**. GitHub documents these creation options in its
[new repository guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository).

Once it exists, from this local repository folder:

```powershell
git remote -v
git push -u origin main
```

The configured origin is `git@github.com:CC-David-CC/strata-control-lab.git`.
SSH access that pushes the Strata fork can push this repository after GitHub has
created it for the same account. If you chose a different owner or name, change
the origin explicitly before pushing. Do not force-push over an initialized or
unrelated repository.

After publication, set the GitHub About description to:

> Offline-first visual experiments for logprobs, grammar and model control.

Suggested topics: `llm`, `logprobs`, `gbnf`, `model-control`, `fastapi`,
`educational`, `local-inference`.

The website runs locally as a Python application. Publishing this source does
not deploy a public web service or expose a model server. The README, screenshots,
evidence and portable examples can all be browsed on GitHub.
