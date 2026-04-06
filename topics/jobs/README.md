# Jobs Workspace

This folder is the job-search prep workspace.

Each company lives in its own folder under `topics/jobs/<company>/`. The goal is to keep all research, prep, transcripts, and interview-specific artifacts in one place so a company can be resumed quickly without reconstructing context.

## Design Principles

- One company = one self-contained workspace.
- Keep raw material, synthesized notes, and interview prep separate.
- Prefer dated or numbered interview folders so the timeline is obvious.
- Keep top-level company files minimal: overview, instructions, and a few high-signal anchors.
- Add specialized folders only when the company actually needs them.

## Common Company Structure

This is the current de facto structure based on `delphyr/` and `finom/`.

```text
topics/jobs/<company>/
  README.md
  CLAUDE.md
  AGENTS.md
  interviewers/
  interviews/
    1-<stage>--<person-or-topic>/
    2-<stage>--<person-or-topic>/
  prep/
  artifacts/
```

## What Each Item Is For

### `README.md`

The company dashboard.

Use it for:
- company snapshot
- role context
- current interview timeline
- team/interviewer summary
- strongest fit points and known gaps
- pointers to the most important files

Why:
- this is the fastest re-entry point for future sessions
- it prevents context from being scattered across prep notes only

### `CLAUDE.md`

Always point to `AGENTS.md`.

### `AGENTS.md`

Operational instructions for agents working inside that company folder.

Use it for:
- file placement rules
- naming rules
- what to update after each interview
- preferred artifact types
- how much synthesis vs raw capture to keep

### `interviewers/`

One file per interviewer.

Use it for:
- role/title
- likely angle
- what they probably care about
- how to calibrate answers and questions for them

Why:
- interviewer-specific notes are reusable across rounds
- it keeps those notes separate from one-off interview prep

### `interviews/`

One folder per interview round.

Recommended naming:
- `<sequence>-<stage>--<person-or-topic>`

Examples:
- `1-introduction--michel`
- `2-technical--dejan-tim`
- `1-introduction--dmitry`
- `2-central-ai--ivo`

Use each interview folder for:
- raw recording
- transcript
- transcript cleanup / summary
- round-specific prep
- interviewer-specific research that only matters for that round

Why:
- keeps the timeline explicit
- groups raw and derived material together
- avoids mixing first-round notes with later-stage prep

Observed file pattern for an interview folder:

```text
interviews/<round>/
  <audio>.m4a # raw interview recording
  <transcript>.txt # raw transcript
  <date>-Audio.md # cleaned interview recording metadata
  <date>-Interview.md # cleaned interview summary/notes
  README.md                # when prep is specific to the round
  <person>-PROFILE.md      # optional, if interviewer research is round-specific
  INTERVIEWER-CHEAT-SHEET.md  # optional
```

### `prep/`

Focused study notes and short tactical prep docs.

Use it for:
- 24h/48h prep plans
- topic cheat sheets
- question lists
- implementation notes for concepts you need to review

Why:
- prep docs change fast and should not overload the main company README

### `artifacts/`

Generated or packaged study material.

Use it for:
- NotebookLM source packs
- audio overview plans
- slide scripts
- synthesized deliverables intended for reuse

Why:
- separates “final-ish assets” from working notes

#### `application/`

Use it for:
- saved job posting
- fit/match analysis
- resume/application-tailoring notes

Why:
- application materials are distinct from later interview prep

### Optional Company-Specific Folders

These appear when a company needs deeper work beyond normal interview prep.

#### `code/`

Seen in `delphyr/`.

Use it for:
- prototypes
- example implementations
- technical talking points backed by code

Why:
- some interviews benefit from hands-on rehearsal or demonstrable examples

#### `reports/`

Seen in `delphyr/`.

Use it for:
- long-form research imports
- external research summaries
- topic deep-dives

Why:
- keeps heavy reference material out of `prep/`

#### `notebooklm/`

Seen in `delphyr/`.

Use it for:
- NotebookLM output prompts
- studio artifacts such as slide-deck prompts

Why:
- useful when NotebookLM becomes part of the prep workflow

#### `updates/`

Seen in `delphyr/`.

Use it for:
- recent company news
- timeline updates
- changing org or product signals

Why:
- company updates age differently from evergreen prep notes

## Recommended Tree

This is the recommended structure going forward. It is slightly stricter than the current state.

```text
topics/jobs/<company>/
  README.md
  CLAUDE.md
  AGENTS.md
  application/                # optional
  interviewers/
    <Name>.md
  interviews/
    1-<stage>--<slug>/
      <raw-audio>.m4a
      <raw-transcript>.txt
      <date>-Audio.md
      <date>-Interview.md
      README.md               # only if round-specific prep is needed
    2-<stage>--<slug>/
  prep/
    <topic-or-round>.md
  artifacts/
    <reusable-study-assets>.md
  code/                       # optional
  reports/                    # optional
  notebooklm-studio/          # optional
  updates/                    # optional
```

## Working Conventions

### Naming

- Use lowercase company folder names: `finom`, `delphyr`
- Use numbered interview folders: `1-...`, `2-...`, `3-...`
- Use readable slugs after the interview number
- Prefer Markdown for synthesized notes
- Keep raw audio/transcript filenames unchanged if they come from the source system

### File Placement

- Put evergreen company context in `README.md`
- Put per-interviewer notes in `interviewers/`
- Put per-round prep in that round’s `interviews/<round>/README.md` or in `prep/`
- Put reusable generated study material in `artifacts/`
- Put imported or long-form research in `reports/` when the volume justifies it

### When To Add A New Folder

Add a new folder only when it creates a durable category.

Good reasons:
- multiple files of the same kind are accumulating
- raw and synthesized material are getting mixed together
- a workflow like NotebookLM or coding practice has become recurring

Bad reason:
- one-off note that can live cleanly in `prep/` or an interview folder

## Practical Takeaway

If you create a new company folder today, start with:

```text
topics/jobs/<company>/
  README.md
  CLAUDE.md
  AGENTS.md
  interviewers/
  interviews/
  prep/
  artifacts/
```

Then add `application/`, `code/`, `reports/`, `notebooklm-studio/`, or `updates/` only if the company workspace actually grows into those needs.
