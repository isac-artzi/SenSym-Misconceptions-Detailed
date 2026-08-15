# How to write your data files

This is the part only you can do, and it decides whether the results mean
anything.

⚠️ **These examples are here to show the STYLE, not to be copied.** Use your own
misconceptions from your doc and write your own answers. If example text ends up
in your real files, nobody can trust any of it.

---

## Part 1 — `misconceptions.csv`

Pick **10** from your list of 32. Choose ones that are genuinely *different* from
each other, so you're covering the topic rather than testing the same idea ten
times. A reasonable spread:

| Sub-area | Pick about |
|---|---|
| Password strength & composition | 2–3 |
| Password reuse & rotation | 2 |
| Password managers & storage | 2 |
| MFA / biometrics | 2 |
| Site trust signals (HTTPS, padlock) | 1–2 |

### Example row

```csv
M01,Long passwords are always strong,"Length helps, but a long password made of
common words or predictable patterns (e.g. 'passwordpasswordpassword') is still
easy to crack; strength comes from unpredictability (entropy), not length
alone","A user picks a long but guessable passphrase, believes they are safe,
and their account is taken over in a dictionary attack"
```

**Tip:** if a field contains a comma, wrap the whole thing in double quotes.
Honestly it's easier to open the CSV in Excel or Google Sheets, type normally,
and save as CSV — the quoting gets handled for you.

---

## Part 2 — `responses.csv` (the hard part, and the interesting one)

For each of your 10 misconceptions, write **4** short answers: **2 with the
misconception (M)** and **2 that are correct (C)** about the same thing.

Imagine the question was: *"In a sentence or two, how do you decide whether a
password is strong?"* Then write what four different people in your grade would
actually say.

### Worked example — misconception M01 "long passwords are always strong"

| id | truth | response |
|---|---|---|
| R01 | **M** | "My password is 24 characters so it's basically uncrackable. Length is the only thing that really matters for password strength." |
| R02 | **M** | "I use 'ilovepizzaandicecream' — it's really long, so even if it's just normal words a hacker would never get through it." |
| R03 | **C** | "Length helps a lot, but a long password made of common words can still be guessed by a dictionary attack. It needs to be long *and* unpredictable." |
| R04 | **C** | "I use a long passphrase, but I make sure it's random words that don't form a normal sentence, because attackers try common phrases first." |

What makes these good:

- The M answers sound **confident and believable**, not stupid. That's what a
  real misconception looks like — a grain of truth ("length helps") pushed too
  far.
- The C answers aren't **obviously different**. Same topic, similar words — R01
  and R03 both talk about length. The model has to actually think, not match
  keywords.
- They're **one or two sentences**. Short enough to run fast, long enough to
  contain a real idea.
- They sound like a **person**, not a textbook.

### The trap

❌ **Too easy** — your numbers will be high and meaningless:

| truth | response |
|---|---|
| M | "long password good always" |
| C | "A password's strength depends on its entropy, which is a function of both length and character-set unpredictability, per NIST SP 800-63B." |

Any model splits those instantly. You've measured nothing. If you score 100%,
suspect your answers before you celebrate.

---

## Checklist before you run it

- [ ] Exactly 10 misconceptions in `misconceptions.csv`, no placeholders left
- [ ] Exactly 40 answers in `responses.csv`, no placeholders left
- [ ] 20 labeled `M`, 20 labeled `C`
- [ ] Labels are capital `M` / `C` with no stray spaces
- [ ] Nothing longer than about 3 sentences
- [ ] You read all 40 out loud and none sound like a robot wrote them
- [ ] A friend could read an M answer and not spot the error straight away

---

## One check worth doing

Get **one other person** — a friend, a sibling, a parent — to label a random 10
of your answers M or C without seeing your labels. Then compare.

- Agree on all 10? Your labels are solid.
- Disagree on 2 or more? Those items are ambiguous — rewrite them.

This is a stripped-down version of something called **inter-rater reliability**.
Worth doing, and worth a sentence when you write it up. Note down how many you
agreed on.
