# R1 UI upgrade — experience, implementation, and acceptance plan

Status: **approved direction; UI-01 review draft pending visual approval**. Recorded 2026-09-14.
This is a normative R1 implementation plan, not evidence of a completed UI.
The source audit covers the baseline at commit `0f5532a`; no real-browser visual
inspection was performed for this documentation change.

Read with [game design](game-design.md), [architecture](architecture.md),
[current controls](ui-controls.md), [testing](testing.md), and
[the R1 roadmap](../ROADMAP.md). This plan operationalizes the existing R1
experience; it does not unlock R2–R7 mechanics or relax R1 learning requirements.

## 1. Confirmed choices and remaining decisions

The user confirmed all four directions through the question tool:

1. **Detailed stylized nursery:** recognizable foliage, dimensional containers,
   benches, greenhouse/outdoor spaces, and soft lighting using generated assets.
2. **Scene-first play:** select a plant in the scene, then use a focused inspector;
   keep a searchable list as an alternative, not every plant's controls at once.
3. **Suggested care:** server-calculated watering suggestion with an editable
   amount, explanation, tank use, and immediate moisture preview.
4. **Desktop and phone equally:** neither is a deferred layout or acceptance path.

Implementation defaults below (component names, breakpoints, gesture thresholds)
are engineering starting points, not additional user-confirmed preferences.
Actual device/browser models, art-reference frames, species care target values,
and any new morphology or placement schema still need explicit resolution in
their owning work item. Do not invent biological calibration to unblock art.

Priority: complete the playable UI and its necessary R1 backend contracts before
further long soak work. Existing release gates remain on the roadmap; moving
their execution later does not waive them.

## 2. Audit: current implementation versus intended experience

These are source findings, not screenshot or performance measurements.

| Area / source | Current gap | Required correction |
| --- | --- | --- |
| `web/src/main.ts`, `renderControlPanel` | Long page of every plant and operational control; repeated IDs and scientific values | Scene, navigation, selected-plant inspector, progressive disclosure |
| `renderNurseryScene` | Static SVG shapes; no picking, pan, zoom, or organ inspection | Selectable orthographic Three.js nursery |
| Scene layout | List-index placement and `Math.min(row, 3)` overlap plants in larger collections | Stable spatial identity, framing, depth handling, reachable plant list |
| Scene appearance | Generic canopy ellipses and stems across species | Recognizable visual profiles, topology-derived structure, containers and environments |
| `formatPlantSummary` | Summed structural length labelled height; inverse damage labelled overall health | Correct quantities and separate condition, damage, moisture, and stress meanings |
| Care button | Fixed 20 mL gives no indication whether it is needed or sufficient | Suggested amount, immediate effect, editable dose, resource constraints |
| Dashboard/clock controls | Ticks as time; selected speed is not hydrated from authoritative clock state | Simulation calendar, actual speed, pause and connection state |
| `createApiClient.load` | Independently fetched world and plant responses can span revisions | Coherent presentation snapshot and revision reconciliation |
| `mountNurseryApp.refresh` | Recreates controls, can lose drafts/focus; errors replace the application | Persistent UI state, incremental updates, non-destructive recovery |
| `inspectPlant` | Detail fetched separately then retained while summaries refresh | Revision-qualified detail refresh and stale-detail indicator |
| Shop | No pre-action price, affordability, sale consequence or quote shown | Catalog-backed purchase/sale previews and precise unavailable reasons |
| Companion API and `sim/companion.py` | Enabled flag gates manual requests; no background scheduling or persisted policy | Manual mode labelled honestly; automatic mode requires server scheduling/persistence |
| Server lifecycle | `tick_world` called by requests/stream messages; no independent ticking task in inspected lifespan | Single-owner background scheduling; never fake autonomy with browser polling |
| Save controls | Base64 textarea and full archive in result message; restore immediately mutates | File download/upload, named save metadata and explicit restore preview |
| Feedback | Technical command names; result at page bottom | Local readable acknowledgement with authoritative result and recovery |
| Mobile/accessibility | Minimum heights and stacking, without measured usability | Real layout, gesture, keyboard, focus, semantic and physical-device checks |
| `web/src/e2e.test.ts` | jsdom with mocked client; no rendered-pixel or real-server evidence | Keep component tests; add separately identified real-browser/server flows |

Renaming kg to mL was useful but did not resolve the player's decision burden.
CSS cards and passing DOM tests likewise did not establish playability.

## 3. Target interaction model

### Desktop

```text
+------------------------------------------------------------------+
| Cash | Water tank | Simulation day/time | Pause/speed | Companion  |
| Nursery | Plants | Shop | Companion | Saves                       |
+--------------------------------------+---------------------------+
| Interactive nursery                  | Selected plant            |
| Greenhouse / Outdoor                 | Condition and reason      |
|                                      | Suggested care + preview  |
| Camera reset / focus selected        | Not for sale / Sell       |
|                                      | Scientific detail tabs    |
+--------------------------------------+---------------------------+
| Prioritized alerts / action feedback                             |
+------------------------------------------------------------------+
```

Desktop inspector default width: 320–380 CSS px. Prefer a scene-led viewport
over a tall page; panels may scroll internally. At narrower widths, change to
the phone interaction model before either scene or inspector becomes unusable.

### Phone

- Compact persistent status header; no giant four-card dashboard above the scene.
- Bottom navigation: Nursery, Plants, Shop, Companion, Saves.
- Selecting a plant opens a bottom sheet with compact and expanded states.
- Compact sheet retains name, condition, suggested care and explicit action.
- Expanded sheet holds details; dismiss returns focus and scene context.
- Opening the software keyboard must keep the edited field and submit action
  reachable. Account for safe-area insets and dynamic viewport height.
- Pan/pinch gestures belong to the canvas; panel scrolling remains native.

Primary journey: **see a need → select plant → understand why → preview care →
act → see confirmed outcome**. An alert must focus its target or open the relevant
shop/companion panel, not merely add another paragraph.

### Common state behavior

| State | Visible behavior | Mutation behavior |
| --- | --- | --- |
| Initial loading | Named loading regions; stable shell | No uninitialized controls |
| Empty collection | Explain empty nursery; offer real shop/restore paths | No fake demo plants |
| Selected plant sold/deleted | Clear inspector with reason; preserve camera | Cancel stale target drafts |
| Request in flight | Local progress and readable action name | Block accidental duplicate submission |
| Applied receipt | Confirm amount/cost and update from authoritative state | Never create optimistic biology or money |
| Rejected receipt | Specific reason plus relevant next action | Keep useful user input |
| Connection lost | Retain last valid scene, mark stale, show reconnect | No blind new-ID retry of uncertain mutations |
| Timeline changed | Clear old receipts/previews/detail, fetch new snapshot | Reject abandoned timeline commands |
| Paused | Persistent paused state with Resume | Show actual command semantics; lifecycle remains usable |
| WebGL unavailable/lost | Keep list, inspector, shop and saves usable | No change to server biology |

Unavailable **implemented** actions may be disabled with a visible reason and
accessible description. Unsupported future mechanics must not appear as dummy
buttons. This distinction replaces the overly broad old "no disabled control"
wording; disabled explanations must not substitute for implementing a feature.

## 4. Ownership and contracts for implementation agents

### Frontend module ownership

Use the locked TypeScript/Three.js stack. No framework or package migration is
implied. Create files only when their behavior exists; no skeleton directory work.

| Proposed path under `web/src/` | Owns | Must not own |
| --- | --- | --- |
| `main.ts` | Bootstrap, composition, disposal | Full renderer, all panels, policy logic |
| `api/contracts.ts`, `api/client.ts` | Runtime-validated wire types, auth/CSRF, HTTP | Biological formulas or DOM |
| `api/stream.ts` | Connection lifecycle, bounded reconnect, resync | World mutation or unbounded event history |
| `state/world-store.ts` | Last coherent server projection, subscriptions | Predicted authoritative values |
| `state/ui-store.ts` | Selection, panel, drafts, camera preference | Cash, biology, companion authority |
| `state/commands.ts` | Receipt lifecycle and uncertain-request reconciliation | Fresh-ID replay after timeout |
| `render/nursery-scene.ts` | Scene lifecycle and incremental sync | API fetches or gameplay policy |
| `render/camera-controller.ts`, `render/picking.ts` | Camera and stable-ID selection | Care/sale command submission |
| `render/plant-renderer.ts`, `render/species-visuals.ts` | Organ/cohort meshes and visual profiles | New biological organs or model calibration |
| `ui/app-shell.ts`, `ui/status-bar.ts` | Navigation, persistent status | Independent duplicate snapshots |
| `ui/plant-inspector.ts`, `ui/plant-list.ts`, `ui/care-controls.ts` | Focused inspection, alternative selection and preview | Hard-coded care targets |
| `ui/shop-panel.ts`, `ui/companion-panel.ts`, `ui/saves-panel.ts` | Domain panels | Direct pool changes, pretend autonomy |
| `ui/feedback.ts`, `ui/formatters.ts` | Accessible feedback and exact unit presentation | Hidden defaults for unknown data |
| `styles/tokens.css`, `styles/layout.css`, `styles/components.css` | Shared typography, spacing, layout and controls | Per-plant generated inline style systems |

One selected identity is shared by canvas and DOM: `(world_id, timeline_id,
plant_id)`. Follow architecture's decimal-string stable-ID contract when evolving
the API; do not use array indexes or lose 64-bit precision. Any migration from
current numeric IDs must be versioned with compatibility tests.

### Backend dependencies

Domain-owned Python projection builders provide presentation data. Keep pure
biology free of network, DB and renderer imports. `server.py` composes handlers;
do not grow it into a second UI or a client-specific policy engine.

Before UI-02 code, specify these **proposed, not currently available** fields and
endpoint/version decisions in the API contract:

| Contract | Required content |
| --- | --- |
| Coherent snapshot | Schema, world/timeline/epoch, presentation revision, clock, nursery totals, plant summaries, companion mode, catalog version |
| Clock | Sim seconds, day/year/calendar phase where configured, speed, paused, lag indication |
| Plant summary/detail | Identity, common/scientific name, site/container, alive, damage, water amount/capacity, distinct stress values, supported care, source revision |
| Care preview | Target identity/revision, policy version, reason code, suggested amount, command cap, available water, expected immediate transfer/drainage and resulting stored water |
| Render projection | Stable plant/organ/parent IDs, organ geometry/cohorts, spatial anchor, visual-profile version, bounding dimensions and explicit approximations |
| Shop quote | Item/plant identity, price in minor units, quantity/unit, stock/demand, availability reason, expiry/quote identity and balance effect |
| Companion status | Manual/baseline automatic/learned-assisted mode, enabled/suspended state, capabilities, reserve/spending policy, scheduling and bounded activity |
| Save metadata | Name, snapshot identity, simulation date, creation time, autosave status, coverage/version and validation result |

Capture shared values under the one-writer boundary; unrelated parallel GETs
must not masquerade as one snapshot. Chosen endpoint names must be documented
before clients implement them, not guessed independently by each agent.

Presentation revisions must advance on relevant command mutations even while
biology is paused. Keep biological tick count distinct. For stream deltas,
require matching timeline and base revision; otherwise replace with a snapshot.
Ignore obsolete async responses, cancel stale detail requests and clear old-world
drafts. Persist reconciliation information where the command contract requires it.

## 5. Ordered R1 work packages

All UI packages remain unchecked until their specific evidence exists. Each
package must implement loading, empty, success, stale, unavailable and error
states from section 3, plus desktop and phone behavior.

### UI-01 — Layouts, visual target, and gameplay flows

**Depends on:** confirmed choices in section 1. **Owns:** design artifacts and
specification; no production behavior claim.

1. Draft desktop and phone frames for overview, dry/healthy/dead selected plant,
   empty tank, protected sale, purchase, companion activity, disconnect, restore
   preview and empty nursery.
2. Produce detailed-stylized target frames for greenhouse/outdoor overview and
   close inspection, with six plant visual profiles and a consistent scale key.
3. Define typography, spacing, contrast, selected/focus/error states and icon
   labels in one token sheet. Do not rely on color alone.
4. Ask the user to approve the frames, specifically selection, care clarity and
   visual fidelity on both form factors. Record requested changes.

**Artifact:** [`docs/ui-design-frames.md`](ui-design-frames.md).

**Accept when:** approved frames and state flows are linked from evidence, with
art references inspected if used. Mockups are labelled design artifacts, never
reported as application screenshots.

### UI-02 — Authoritative presentation and coherent client state

**Depends on:** UI-01 information hierarchy. **Owns:** API projections,
`api/*`, `state/*`, revision and lifecycle contracts.

1. Audit current fields against section 4; implement missing projections and
   version changes with backend tests before panels consume them.
2. Implement coherent snapshot loading and one subscribed client store.
3. Add client stream consumption, reconnect backoff, stale indication and
   snapshot replacement. Bound queues/history; document retry limits.
4. Add per-command presentation invalidation, including paused commands.
5. Refresh selected detail only when its accepted identity/revision changes.
6. Implement independent single-owner server ticking for genuine time/autonomy;
   serialize requests and scheduled work rather than adding a racing timer.
7. Keep paused-command behavior truthful. Current commands apply immediately
   while paused; target queued horticulture needs its own implementation/tests
   before displaying "queued until resume". Resolve the contract transition in
   the decision register; never change it by wording alone.

**Accept when:** deterministic tests cover reordered responses, stale detail,
two tabs, paused mutation, restore, expiry and reconnect; all displayed totals
and plant values use compatible revisions. A browser disconnect does not become
the mechanism that stops/starts server ticking.

### UI-03 — Persistent desktop shell and phone navigation

**Depends on:** UI-01, UI-02. **Owns:** app shell, status, UI state, styles.

1. Keep one mounted shell, renderer and panel host. Patch changed content instead
   of `target.replaceChildren()` after ordinary mutations.
2. Show cash, tank quantity/capacity, real sim time/speed/pause and companion mode.
   Render the calendar from authoritative time; season only from configured
   phase, not a fabricated biological season system. Put ticks in diagnostics.
3. Add navigation, inspector/bottom-sheet states and list search/filter by
   common name, condition, zone and not-for-sale state.
4. Preserve active panel, selection, scroll, input draft and focus on updates.
   Dirty drafts remain editable; refreshed previews must not silently overwrite
   them or submit an obsolete amount.
5. Add alert priority and local command results. Keep unsupported-feature notes
   in help/coverage rather than crowding the status bar.

**Accept when:** 360px and desktop flows retain focus and drafts across refresh;
Shop/Saves do not require scrolling through all plants; current pause/speed is
hydrated rather than defaulted to the first dropdown option.

### UI-04 — Navigable, selectable orthographic nursery

**Depends on:** UI-02, UI-03. **Owns:** scene, camera, picking, render projection.

1. Mount a Three.js orthographic scene using the locked dependency; camera reset
   frames current plant bounds. Start with validated geometry before art detail.
2. Define stable placement. If slots/container occupancy become gameplay state,
   Python allocates and persists them, including migration and purchase/sale
   integration. Visual-only layout must be labelled as such and must not imply
   relocation/light changes. Do not derive slots from transient list order.
3. Raycast hit volumes mapped to stable IDs, selection ring, name and focus
   control. A list alternative can select any obscured plant.
4. Desktop wheel zoom and empty-space drag pan; phone pinch and drag pan; explicit
   zoom/reset controls. Start with a 6 CSS-pixel drag threshold, cancel tap after
   multi-touch, pointer cancellation or pan. Tune from real-device evidence.
5. Canvas selection opens the inspector only. Care needs a second explicit
   control. Wire keyboard list selection and camera buttons.
6. Handle resize, device pixel ratio, context loss and disposal without losing
   the DOM gameplay path.

**Accept when:** API reordering and purchase/sale never reshuffle existing plants;
every plant remains reachable; pan/pinch/selection cannot mutate the world;
selection persists through accepted state updates.

### UI-05 — Intuitive inspection and server-suggested care

**Depends on:** UI-02–04; versioned care preset decision. **Owns:** care preview
builder, inspector, care controls, formatters.

1. Primary inspector: common name/location, condition plus cause, moisture
   indicator, suggestion, tank use, expected immediate effect, action, and
   editable amount. Keep organ/resource quantities in optional scientific tabs.
2. Condition must distinguish alive/dead, damage and current stress. Never call
   `100 - damage_fraction * 100` comprehensive health or claim stress is moisture.
   Use reason codes and unknown/unavailable states, not default green badges.
3. Python owns water capacity, target, limits and preview. Record a per-species
   care preset version, provisional-calibration label and provenance. Ask before
   choosing unresolved scientific targets; this plan sets no optimal moisture.
4. Compute a bounded suggestion in canonical kg:

   ```text
   needed = max(0, target_water_kg - current_water_kg)
   free_capacity = max(0, capacity_kg - current_water_kg)
   suggested = min(needed, available_tank_kg, free_capacity, command_limit_kg)
   ```

5. Explain the limiting factor and preview resulting stored water/drainage with
   the real watering kernel. A limited dose is not a promise to reach target;
   never issue hidden repeated commands. Manual doses may drain if supported;
   show that explicitly before execution.
6. Convert kg to mL/L at the presentation boundary using documented approximate
   water density 1 kg/L. Round display consistently; displayed submitted amount
   must match canonical payload after chosen input quantization.
7. Zero suggestion offers no watering-needed state. Empty tank links to actual
   purchase; dead plant gets no revival promise; nutrient stress must not be
   misrepresented as fixable with water. Preserve irreversible-damage truth.
8. On submit revalidate target, supply and constraints. Show changed preview on
   stale failure, then require fresh intent; never silently change the dose.

**Acceptance examples (test fixtures, not biological defaults):** capacity
0.20 kg, current 0.10 kg, target 0.14 kg, tank 2 kg and cap 0.05 kg yields 40 mL,
140 mL soil water and 1.96 L tank after transfer. With only 0.01 kg in the tank,
suggest 10 mL and explain target unmet. Test zero need, empty tank, dead target,
full zone, manual drainage, duplicate action and intervening caretaker action.

**Accept when:** a player identifies need and chooses a valid dose without
interpreting stress coefficients; scene, inspector and tank agree after receipt.

### UI-06 — Detailed stylized plants and environments

**Depends on:** UI-01 visual approval, UI-04 spatial rendering. **Owns:** plant
renderer, species profiles, environment art, geometry projection contract.

1. Build dimensional pot sides/rims/substrate, benches, paths and greenhouse
   framing. Match light direction, scale and grounded shadows; distinguish zones
   without inventing unsupported weather/relocation behavior.
2. Map structural meshes to server organ topology/dimensions, leaf instances to
   cohorts/area, and alive/damage/stress styling to supplied state. Identify
   selected organ in scientific view; provide root cutaway from actual root data.
3. Resolve missing orientation/geometry fields before promising detailed
   inspection. Document which geometry is measured by the simulation and which
   orientation/tessellation is an approximate visual representation.
4. Create distinguishable profiles for currently implemented basil, tomato,
   weeping fig, jade, juniper and oak: leaf shape, thickness, grouping/material
   and grounded growth-form cues. The earlier proposed species list differs
   from the implemented catalog; resolve that catalog decision separately before
   substituting species or labelling this set newly user-approved.
5. Do not invent mature branching, flowers or roots solely to beautify a screen.
   If recognizable morphology requires organ initiation not yet modeled, report
   that biological dependency and implement it under its own contract. Do not
   call generic stems mature stock or a display ellipse a leaf-level simulation.
6. Stable visual variation uses a separate seed/profile version. Do not consume
   biological RNG, re-randomize on refresh or use visual LOD to disable biology.
7. Reuse geometries/materials; instance foliage/containers; update only dirty
   plants. Dispose removals. Profile draw calls, frame time and retained resources
   at repeated select/update cycles. Reduce shadows/mesh detail before controls.

**Accept when:** actual-browser overview/inspection frames match UI-01 direction,
species remain visually distinguishable, pots feel grounded, selection stays
readable, bounds do not clip plants, and all approximations are disclosed.
User visual review and measured renderer behavior are required in addition to
tests. A polygon count is not a visual-quality acceptance criterion.

### UI-07 — Shop, protections, and transaction previews

**Depends on:** UI-02, UI-03; quote/availability backend. **Owns:** shop projection,
shop panel, selected-plant sale preview and command states.

1. Show catalog common names, price, quantity, supplier availability, tank/space
   capacity and affordability. Server owns quotes; do not duplicate price tables.
2. Preview exact total and balance after water/plant purchase. Supplier offers
   and buyer demand are distinct; do not populate purchase options solely from
   buyer demand. Surface actual finite-space rules once implemented.
3. Label sale protection "Not for sale" and explain it does not prevent watering.
   Sale preview names the plant, proceeds, removal consequence and blockers.
4. Server revalidates quote/target/protection/demand/funds at execution. Expired
   quotes need a refreshed preview, not silent repricing. Duplicate submissions
   retain original identity and receipt.
5. Show readable transaction outcomes and bounded history; unavailable actions
   explain protected/dead/no-demand/no-funds/no-space reasons.

**Accept when:** price and consequence are known before execution; protected
sales cannot happen via player or companion; depleted demand and insufficient
funds are actionable states, not opaque error strings.

### UI-08 — Truthful, persisted companion experience [AI/ML]

**Depends on:** UI-02, UI-03 and R1 companion/learning backend tasks.
**Owns:** companion panel and its required scheduling/persistence contracts.

1. Label current behavior "Manual care assistant" until automatic scheduling
   actually exists. Never treat `enabled=true` alone as evidence of autonomy.
2. Implement server-owned emergency/planning cadence through the validated
   command path; browser polling must not power the manager. Serialize with the
   one writer; pause/suspend/shutdown/restore must remain serviceable.
3. Persist policy, scheduling counters, pending actions and bounded activity
   with the world; test restart/restore/export and abandoned-timeline handling.
4. Implement full available-action authority, reserves/spending limits and hard
   player protections in Python before presenting those controls as functional.
   First-run onboarding explains authority and displays the chosen reserve.
5. Feed entries show target, observed reason, executed action/amount/cost/result,
   simulation time and attribution. Link back to the plant. Prefer readable
   reason codes over dumping policy coefficients.
6. Distinguish suspended, manual-only, automatic baseline and learned-assisted
   modes. Display real learning/evaluation results only when implemented;
   unavailable predictions have no fabricated confidence or progress bar.

**Accept when:** automatic care operates without clients; suspension and world
pause differ visibly; settings survive restart/restore; activity matches receipts;
the full-authority and learner roadmap gates remain separately evidence-backed.

### UI-09 — Saves, recovery, onboarding, and feedback

**Depends on:** UI-03, UI-05, UI-07; persistence and companion capability contracts.
**Owns:** login/onboarding, saves panel and shared feedback.

1. Style login consistently; label password/error/loading state and return to
   the nursery after authentication. Preserve safe navigation on session expiry.
2. Provide brief dismissible/reopenable guidance for selection, needs, care,
   tank purchase, save and manager authority. Do not enable full management
   before its explanation and actual backend exist.
3. List snapshots by name, sim date and creation time; show last successful
   autosave and failures. Status comes from persisted state, not a browser timer.
4. Export via file download; import via file picker with validation and coverage
   preview. An adapter may wrap the current bounded base64 archive in a versioned
   file format, but must document it and revoke temporary object URLs. Never
   print the archive in a toast or retain unbounded copies.
5. Restore has explicit target/date/consequence preview and confirmation.
   Inspect existing import semantics first: if import activates a world, obtain
   restore-level confirmation before calling it; never assume it only stages.
6. Keep last valid scene on errors and provide Retry. Local action results read
   "Watered Basil with 40 mL" using receipt data, not a technical command name.
7. Empty/dead collections offer valid purchase/restore paths. If a new-world
   operation is needed, implement a separately validated explicit operation;
   never overwrite a failed world automatically or expose a dummy reset button.

**Accept when:** backup/restore can be performed without developer tools or
base64 copying; cancellation does not mutate; corrupt import retains current
world; feedback reaches keyboard and screen-reader users without focus theft.

### UI-10 — Real-browser, accessibility, and visual acceptance

**Depends on:** all preceding packages. Browser infrastructure should be prepared
early so vertical slices can use it; final acceptance is last.

1. Keep Vitest/jsdom as component tests. Add a clearly separate real-browser test
   command against the Python server and isolated test data. Lock tooling and
   document explicit browser installation under the Conda/npm policy. Ask before
   a package-manager exception; no runtime binary downloads.
2. Required viewport matrix: 1440×900, 1024×768, 390×844 and 360×800 CSS pixels.
   Name actual browser/device versions. Physical phone evidence is separate
   from viewport emulation and requires device access/user participation.
3. Capture overview, healthy/dry/dead selection, care preview/result, empty tank,
   shop, protected sale, companion, save/restore, reconnect and WebGL fallback.
4. Check labelled controls, Tab/Enter/Escape operation, focus restoration,
   44×44 targets, contrast, reduced motion, software keyboard and screen-reader
   status output. Hidden drawers must not retain keyboard focusable controls.
5. Verify pan/pinch submits no commands; repeated tap yields one intended action;
   save/input drafts survive live updates; stale responses cannot overwrite
   newer numbers; no horizontal page scrolling at 360px.
6. Run a real-server journey: login → select dry plant → preview/water → see
   consistent outcome → buy water/plant → protect and preview sale → save →
   change world → restore → reconnect. Add autonomous companion journey once its
   backend exists; mocks do not satisfy that gate.
7. Measure rendering on named hardware/settings at 500 plants and characterize
   1,000, including varied modeled organ counts. Use the existing mobile ≥30 fps
   target; report frame time, memory and quality settings, not headless tick
   latency as proof of graphics performance. Long soak reruns are not UI work.
8. Ask for visual/usability review of actual application screenshots and the
   journey. Record defects and resolve them before closing broad UI acceptance.

**Accept when:** browser flows and accessibility checks pass, evidence covers
both device classes, and the user accepts the implemented visual/interaction
result. Screenshots alone do not prove commands work; DOM tests alone do not
prove the interface looks or feels right.

## 6. Delivery sequence and evidence discipline

First playable vertical slice: **scene → select → understand need → suggested
water preview → validated action → coherent outcome**, on desktop and phone.
Build it using UI-01–05 plus a representative approved UI-06 plant/environment
and early browser infrastructure. Then extend fidelity across the catalog and
complete UI-07–10. Do not deliver another cosmetic-only pass as this milestone.

Before every implementation task, record: task ID, exact dependencies, owned
files, input/output contracts, all state cases, test commands and completion
criteria. If a dependency is missing, implement it or report the blocker; do not
substitute guessed UI state. No subagents are authorized by this plan alone.

Tests for a slice must exercise its behavior: delayed response ordering,
preview/receipt reconciliation, resource-limited care, selection identity,
protection, focus/drafts and persistence. Avoid tests that only assert the same
hard-coded string or count of ellipses produced by the implementation.

Evidence entries under `docs/evidence/` must record commit, exact command,
environment, fixture/world identity, viewport/device/browser, expected/actual
outcome, screenshot/report location, failures, limitations and review outcome.
Keep large generated reports and private saves outside Git; commit compact
reviewable evidence. Reference an artifact only after it exists and was inspected.

For each coherent delivered change, update controls/docs/changelog and relevant
roadmap task, run applicable checks, review diff, commit and verify push as
required by `AGENTS.md`. Re-run checks only when implementation changes or
unresolved failures justify it. Documentation-only updates need local-reference,
consistency and whitespace review, not numerical or soak reruns.

## 7. Definition of R1 UI done

- UI-01–10 have their own acceptance evidence, not just a checked parent row.
- Scene-first selection/care, meaningful visual fidelity and consistent values
  work on desktop and phone.
- Commerce, saves and companion controls represent implemented authoritative
  behavior with explicit consequences and recovery.
- Scientific detail is available without dominating routine play.
- Unsupported behavior and provisional models are inspectable and not presented
  as fake controls, anatomy, learning, confidence or guaranteed recovery.
- Current README/evidence no longer contradict source behavior.
- User-facing experience review accompanies actual-browser technical evidence.

Completing this UI plan does not by itself complete the remaining biological,
learning, persistence or operational requirements of R1.
