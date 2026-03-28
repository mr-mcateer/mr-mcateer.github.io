# /dispatch -- Zero-Friction Thought Capture

You are executing the Dispatch protocol. Activation energy must be ZERO.

## Input
The user has provided raw, unstructured input. It might be a voice note transcription,
a quick text, or a stream-of-consciousness dump. Do NOT ask follow-up questions
unless critical data is genuinely missing (e.g., a date with no month).

## Step 1: Classify
Read the input and classify each item into exactly one domain:
- **school** -- Anything about CVHS, metals, autos, shop inventory, students, Canvas,
  lesson plans, dry runs, safety protocols, 10mm sockets, bar stock, equipment
- **llc** -- Anything about Prompt AI Solutions, clients, invoices, website, CAD/CAM,
  3D printing, consulting, promptaisolutions.com, brand assets
- **personal** -- Anything about James, John, Stacie, family schedules, medical,
  household tasks, groceries, personal errands

## Step 2: Route
Append each classified item to the correct file with a timestamp:
- School --> `logs/capture-school.md`
- LLC --> `logs/capture-llc.md`
- Personal --> `logs/capture-personal.md`

Format each entry as:
```
### [HH:MM] [Brief title]
[Processed content -- cleaned up but preserving intent]
```

Create the capture file if it does not exist.

## Step 3: Cross-Reference
Quickly scan the relevant memory directory for connections:
- Does this relate to an existing project in `memory/cvhs/active_curriculum.md`?
- Does this match an open item in `memory/llc/active_projects.md`?
- Does this conflict with anything in `memory/dad/stacie_sync.md`?

If a connection is found, note it in the capture entry.

## Step 4: Confirm
Respond with a single line per item captured. No follow-up questions. No suggestions.
Format: `[domain] Captured: [brief description] (linked to [project] if applicable)`

Example:
```
school  Captured: Order 10mm sockets for auto shop (linked to CNC Machining module)
personal  Captured: James permission slip due Friday
llc  Captured: Invoice Client X tonight at 8 PM
```

## Step 5: Log
Append a one-line summary to today's run-log under `## Captures`.
