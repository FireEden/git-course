# Everyday Git

Notes from working through this repo. The commands, the mental models, and the
handful of gotchas that account for nearly all of it.

---

## Four places your code can be

Git isn't "saved / unsaved." A change moves through four stages, and each command
moves it exactly one step. Almost every confusion in git comes from not knowing
which stage you're in.

```
┌─────────────── on your laptop — no network ───────────────┐
│                                                           │
│  working tree  ──add──▶  staging  ──commit──▶  local repo │ ──push──▶  GitHub
│  (your files)            (marked for      (permanent      │
│                           next commit)     history)       │
└───────────────────────────────────────────────────────────┘
```

**A commit is a save. A push is an upload.** Everything inside the box happens
offline. Commits are one-per-change; a push ships however many are waiting, all at
once. Nothing exists on GitHub until you push — that's the whole answer to "where
did my code go?"

| Command | What it changes |
| --- | --- |
| `git add <file>` | Marks the file's *current* content for the next commit. Edit again afterwards and you must re-add. |
| `git diff --staged` | Read-only preview of exactly what you're about to commit. Ten seconds that catches leftover debug code. |
| `git commit -m "…"` | Records staging as permanent history and empties staging. Moves the branch pointer forward. |
| `git push` | Uploads local commits the remote doesn't have. The only one that touches the network. |

---

## `status` is the present tense, `log` is the past

If you're wondering about staging, you're asking a `status` question — staging has
no hash, so it never appears in `log` at all.

```
$ git log --oneline
2b9c928 (HEAD -> main, origin/main) Add a done command (#1)
8ff0a4b Ignore local scratch notes
f139ff0 Document Python version requirement
```

Every line is one save point: a short hash, then your message. **Newest on top** —
reading downward goes back in time. Most commits have nothing in parentheses;
those are just labels stuck on particular commits.

| Label | Means |
| --- | --- |
| `HEAD` | **You are here.** `HEAD -> main` means you're on branch `main`, and `main` sits on this commit. |
| `main` | A local branch pointer — a sticky note holding one commit hash. That's all a branch is. |
| `origin/main` | Where GitHub's `main` was *last time you checked*. A cache, not a live reading — it only moves on push, fetch, or pull. |

The vertical gap between `main` and `origin/main` is your unpushed work. When both
labels sit on the same line, you're in sync. Run `git fetch` to refresh the
`origin/*` labels without touching your files.

---

## The workflow: branch, push, PR, merge, sync

Creating a branch copies nothing and costs nothing — it writes one sticky note and
stands on it. But your folder only ever holds **one** branch's files at a time;
switching rewrites them on disk.

**1. Branch off `main`**

```bash
git switch -c add-done-command
```

**2. Work, then commit as usual**

```bash
git add tasks.py
git diff --staged
git commit -m "Add done command"
```

**3. First push needs `-u`**

A brand-new branch has no partner on the remote, so git refuses to guess. `-u`
pairs them permanently — after this, bare `git push` and `git pull` work on this
branch forever.

```bash
git push -u origin add-done-command
```

**4. Open the pull request**

`--base` is the **destination**, `--head` is the **source**. Swap them and the diff
looks insane.

```bash
gh pr create --base main --head add-done-command \
  --title "Add a done command" --body "…"
```

**5. Review, fix, push again**

A PR points at the branch, not a snapshot. Push a fix to the same branch and the PR
updates itself — that's the entire review cycle.

**6. Merge — squash is the sane default**

Squash flattens every commit on the branch into one new commit on `main`, so
history reads as one line per feature instead of "add thing, fix thing I just
broke."

```bash
gh pr merge --squash --delete-branch
```

**7. Sync your laptop — the step everyone forgets**

Merging happened on GitHub. Your local `main` knows nothing until you pull.

```bash
git switch main
git pull
git branch -d add-done-command   # -d refuses if unmerged; safe
git fetch --prune                # drop stale origin/* labels
```

---

## Undoing: almost nothing is unrecoverable

| I want to… | Command |
| --- | --- |
| Throw away unstaged edits to a file | `git restore <file>` |
| Unstage something, keeping the edit | `git restore --staged <file>` |
| Fix the last commit's message | `git commit --amend -m "…"` |
| Add a forgotten file to the last commit | `git commit --amend --no-edit` |
| Undo a commit that's already pushed | `git revert <hash>` |

**The one rule that keeps you safe:** `revert` for anything pushed, `amend` only
for commits still on your laptop. `revert` adds a new commit that undoes the old
one, so nobody's history shifts underneath them. `amend` replaces a commit with a
different hash — harmless locally, genuinely destructive once shared.

> ⚠️ `git reset --hard` discards commits **and** wipes your working tree. It's the
> one command here that can lose work for good. `restore` and `revert` cover the
> real cases — reach for those.

---

## Merge conflicts: not an error, a question

Git merges automatically almost always, line by line. A conflict happens *only*
when two branches change the same lines of the same file. Git isn't broken; it's
refusing to guess which version you meant.

```
<<<<<<< HEAD
A tiny task-list CLI for learning Git and GitHub.      ← your current branch
=======
A minimal command-line task tracker.                   ← the incoming branch
>>>>>>> edit-tagline-b
```

1. **Run `git status`** — it names every conflicted file and tells you what to do
   next. Read it instead of panicking.
2. **Edit the file — it's just text.** Keep either side, or write a third version
   combining them. **All three marker lines must be deleted**, or you'll commit
   them.
3. **`git add <file>` means "resolved."** That's `add`'s second job during a merge.
4. **`git commit`** — no `-m` needed, the merge message is pre-filled. Save and
   close the editor. (Stuck in Vim? `:wq` then Enter.)

> 🛟 `git merge --abort` rewinds you to exactly before the merge, at any point,
> with nothing lost. If you remember one command from this section, make it this
> one.

---

## Things that bite everyone once

**Terminal seems frozen after `git log` or `git diff`**
You're in the `less` pager, not a hung command. Press <kbd>q</kbd>. Space pages
down, <kbd>b</kbd> pages back. To skip it permanently:
`git config --global core.pager cat`.

**.gitignore isn't ignoring my file**
It only affects files git isn't *already* tracking. Once a file is committed,
`.gitignore` does nothing — untrack it first with `git rm --cached <file>`.

**"Up to date" when I'm clearly not**
`origin/main` is a cached pointer. Git doesn't phone GitHub during `status` or
`log`. Run `git fetch` for a live reading.

**My PR diff shows hundreds of unrelated files**
`--base` and `--head` are swapped. Base is where the code is *going*.

**My branch switch is refused**
You have uncommitted changes that would be overwritten. Commit them, or park them
with `git stash` and bring them back later with `git stash pop`.

**The commit message has a typo and it's pushed**
Leave it. Rewriting shared history to fix a cosmetic problem trades it for a real
one. Every real repo has warts.

---

The four-command loop — `add`, `diff --staged`, `commit`, `push` — is roughly 90%
of daily git. Everything else is scaffolding around it.
