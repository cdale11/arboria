# UI-01 design frames

Status: **approved by user on 2026-09-14**. These are layout and
interaction artifacts, not application screenshots or evidence that the runtime
already implements the design. The implementation sequence is in
[`r1-ui-upgrade.md`](r1-ui-upgrade.md).

## Design intent

The nursery is the play surface. The player should notice a plant's need in the
scene, select it, understand the reason, preview a bounded intervention, and see
the authoritative result. Operational information is persistent but quiet. The
scene has visual character without fabricating biological detail.

## Frame A: desktop overview, 1440 x 900

```text
+--------------------------------------------------------------------------+
| ARBORIA   $42.50   WATER 1.80 L / 2.00 L   DAY 12, 08:30   [||] [48x]   |
|                                                                          |
| [NURSERY]  [PLANTS]  [SHOP]  [COMPANION]  [SAVES]             [Account]  |
+--------------------------------------------------------------------------+
|                                                                          |
|  GREENHOUSE                                         SELECTED PLANT       |
|  +-------------------------------+                  Basil                |
|  |       ^ light / glass roof    |                  Greenhouse A / Bay 1  |
|  |   (fig)        (basil)  !     |                  [healthy]             |
|  |          (tomato)             |                  Moisture 62%         |
|  |  [benches]     [paths]        |                  Needs attention: ...  |
|  |                         (jade)|                  Suggested care        |
|  |  OUTDOOR                      |                  Add 40 mL           |
|  |  (oak)       (juniper)        |                  Soil +40 mL          |
|  +-------------------------------+                  Tank -40 mL         |
|  [Reset camera] [Focus selected] |                  Amount [ 40 ] mL     |
|                                  |                  [Preview] [Water]     |
|                                  |                  [Details] [Protect]   |
+----------------------------------+---------------------------------------+
| ALERTS  Basil is dry. [Focus basil]     Watered basil with 40 mL. [Dismiss] |
+--------------------------------------------------------------------------+
```

Rules:

- The scene receives the largest region. The inspector is 320–380 CSS px wide.
- The selected plant has a visible outline and a non-color selection marker.
- `Water` is explicit and disabled only when the real server says it is
  unavailable; the reason is visible and announced.
- `Preview` does not mutate. The receipt, not an optimistic card, updates the
  tank and plant values.
- Alerts focus a target or open the relevant panel. They do not duplicate the
  full plant list.

## Frame B: phone overview, 390 x 844

```text
+--------------------------------------+
| ARBORIA       1.80 / 2.00 L   48x    |
| Day 12, 08:30        [Pause]         |
+--------------------------------------+
|                                      |
|             NURSERY                  |
|       (fig)       (basil) !          |
|          (tomato)                    |
|       [Reset] [Focus]                |
|                                      |
+--------------------------------------+
| BASIL              [healthy]         |
| Greenhouse A / Bay 1                 |
| Needs attention: low root-zone water |
| Suggested 40 mL       [Preview]      |
| Amount [40] mL        [Water]         |
| [More details ^]                     |
+--------------------------------------+
| Nursery | Plants | Shop | Care | Saves|
+--------------------------------------+
```

Rules:

- The bottom sheet is compact by default after selection and expands on
  `More details`; it must not cover the selected plant's context before action.
- Bottom navigation changes the panel, not the simulation. It never creates a
  second world snapshot.
- All primary targets are at least 44 CSS px. The amount field and action remain
  visible above the software keyboard.
- Dragging/pinching on the canvas never submits care. Sheet scrolling is native
  and does not pan the scene.

## Frame C: care states

| State | Inspector content | Primary action |
| --- | --- | --- |
| Healthy / no need | `No watering needed`; current and target are separately labelled | `Close` or `Details` |
| Dry / suggestion available | Reason, suggested amount, editable amount, tank use, resulting preview | `Preview`, then `Water` |
| Tank limited | `10 mL available; target remains unmet`; editable amount capped | `Buy water` or `Water 10 mL` |
| Full zone | `0 mL can be stored`; explain capacity | `Close` |
| Dead | Death reason and irreversible state; no revival copy | `Details` |
| Stale | `World changed. Refresh preview.`; preserve typed amount | `Refresh preview` |
| Request pending | Readable action and progress; no duplicate submit | Disabled duplicate action |
| Accepted | Receipt amount/cost and authoritative new values | `Close` |
| Rejected | Server reason and recovery path | `Refresh` or relevant shop action |

The UI must never convert a damage fraction into a general health percentage or
present a nutrient problem as a water solution.

## Frame D: shop and saves panels

```text
SHOP                                      SAVES
Water reservoir                           12 Sep 08:30  Greenhouse check
500 mL  $0.50                             [Restore preview] [Export]
Tank after purchase: 2.00 L               11 Sep 18:00  Before repot
Balance after: $42.00                     [Restore preview]
[Buy 500 mL]                              [Import file] [New checkpoint]

Plant stock                                Restore preview
Basil  $8.00  2 available                 Target: Greenhouse check
Space: 498 / 500                          Sim date: Day 12, 08:30
[Buy basil]                               Consequence: replaces current future
                                          [Cancel] [Confirm restore]
```

The exact catalog, prices, space rules, quote expiry, and restore activation
semantics come from Python contracts. These frames do not authorize hard-coded
values or a restore that bypasses confirmation.

## Frame E: companion panel

```text
COMPANION
Mode: Manual care assistant
Automatic management: unavailable in current baseline

Latest activity
08:30  Basil  Observed low water
       Proposed 40 mL  [Validated by server]

Current authority: watering only
Protected sales: always blocked
[Run care check]       [Disable assistant]
```

Until automatic scheduling, policy persistence, and full authority exist, the
panel must not say “learning”, “autonomous”, or show fabricated confidence or
progress. A later learned-assisted panel will add model/evaluation provenance
only after the AI/ML roadmap gates pass.

## Visual tokens, draft defaults

These tokens are implementation defaults for review, not biological parameters.

| Token | Draft value | Use |
| --- | --- | --- |
| `--ink` | `#24322a` | Primary text |
| `--muted-ink` | `#607064` | Secondary labels |
| `--paper` | `#f7f4ec` | Main surface |
| `--surface` | `#fffdf7` | Inspector/cards |
| `--forest` | `#1d5b43` | Primary action/focus |
| `--moss` | `#789b62` | Healthy/supporting accent |
| `--amber` | `#b7791f` | Attention, never sole status signal |
| `--rust` | `#a44732` | Error/damage |
| `--line` | `#d8d4c7` | Borders |
| `--radius-panel` | `18px` | Large panels |
| `--radius-control` | `10px` | Inputs/buttons |
| `--touch-target` | `44px` | Minimum interactive size |
| `--inspector-width` | `360px` | Desktop default, within 320–380px |
| `--space-unit` | `4px` | Spacing scale |

Use a warm, high-contrast palette with redundant labels, icons, patterns, and
text. Verify contrast rather than trusting the draft hex values. Honor reduced
motion. No token may be used to imply a biological threshold without a server
reason code.

## Review checklist

- [x] User approves scene prominence and the desktop inspector balance.
- [x] User approves compact phone bottom-sheet density and navigation labels.
- [x] User approves the visual language, plant recognizability direction, and
  greenhouse/outdoor distinction.
- [x] User approves the care journey: suggestion, editable amount, preview,
  explicit action, and receipt.
- [x] User approves the empty/dead/stale/pending/rejected states as truthful.
- [ ] Actual browser screenshots will be required after implementation; these
  frames are not screenshot evidence.
