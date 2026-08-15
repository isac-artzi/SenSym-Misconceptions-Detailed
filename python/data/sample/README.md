# Sample data — NOT your dataset

Twelve demo responses across three misconceptions, here so that a freshly
cloned repository runs end to end before you've written anything of your own:

```bash
python misconception/run_experiment.py --mock --sample
python misconception/analyze.py
```

Use it to prove your setup works and to see what the finished thing produces.
Then write your **own** 10 misconceptions and 40 answers in `data/`.

**Never report numbers from this file.** It's scaffolding, and somebody else
wrote it — the whole point is that you write and label the answers yourself. The
automated tests use it as a smoke test, nothing more.
