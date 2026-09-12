# Game design contract

## 1. Experience

The player grows, studies, shapes, propagates, and sells living plants. The shop is both livelihood and an experimental garden. Scientific depth is available on inspection; routine controls remain straightforward. The simulation must explain causes without requiring the player to inspect every number.

No research tree or payment gate artificially unlocks modeled biology. Physical equipment, stock, space, money, time, and biological compatibility are legitimate constraints. Features outside the current release are described in documentation, not represented by nonfunctional buttons. Species coverage and model limitations are inspectable.

## 2. Time

- Default speed: 48 simulated seconds per real second, giving one day per 30 minutes.
- Base tick: 300 simulated seconds. Ordinary scheduling uses a monotonic clock, never local civil time.
- Display sim date, season, time, speed, and pause state. Speed changes apply at a tick boundary and are logged.
- Client disconnection causes no speed change. Training and management continue.
- Server shutdown/crash freezes time at the recovered checkpoint. Restart does not calculate elapsed wall-time biology.
- Explicit pause is available to the owner. Pause freezes biology, markets, and learning; UI and save/restore remain responsive. State-changing horticultural commands queue for resume, with this clearly shown.
- If CPU cannot keep up, retain ordered ticks and show simulation lag. Do not silently jump the clock or skip care.
- A year has 365 days; photoperiod uses configured latitude and day of year. Outdoor starting climate is a documented temperate preset, not an assumed player's location.

## 3. Nursery and shop

Zones include outdoor beds, greenhouse benches, shop display, propagation space, and compost stations as their complete releases arrive. Each zone defines light exposure, capacity, temperature/humidity modifiers, irrigation configuration, and environmental coupling.

Initial R1 stock includes established plants as well as young stock so bonsai/tree inspection is meaningful before years of growth. R1 has finite nursery space, replenishable suppliers, bounded customer demand, plant purchases/sales, and care consumables. Later products join the same item/transaction system.

### Item definition

An item type has a stable ID, schema version, label, physical category, quantity unit, storage behavior, applicable transformations, and provenance. Biological material can retain genotype, viability, health, origin, and age. Mixtures store constituent amounts; a new label cannot conjure new physical properties.

Use integer minor currency units and fixed-precision commodity quantities where necessary. Prices are quotes with expiry and quantity limits. Purchases atomically debit currency and credit stock; sales do the reverse. Orders cannot sell the same unique plant twice. Do not simulate every customer as a large agent: demand cohorts with interpretable preferences and bounded budgets suffice.

Starting stock, cash, supplier margins, demand caps, and recovery economics require a versioned balance preset and scenario tests in R1. No invisible free money, unlimited profitable resell loop, or automatic bailout is permitted. If the player loses everything, provide an explicit new-world or restore path; never overwrite the failed world automatically.

## 4. Companion contract

Full manager authority is enabled after first-run onboarding explains it. The manager can water, fertilize, buy, sell, move plants, propagate, prune, harvest, and manage production when those actions are implemented and feasible.

Protections are hard constraints, not soft preferences:

- Pin a plant as not for sale.
- Forbid destructive operations such as pruning, root pruning, or harvest.
- Set a minimum cash reserve and spending caps.
- Restrict selected zones, species, or action categories.
- Suspend autonomous management independently of simulation time.

Defaults: no plants protected, full authority, no discretionary spending that violates a displayed reserve policy. The initial balance preset must choose and display that reserve; the user may set it to zero. The manager cannot spend below zero, borrow, delete a world, restore a save, modify authentication, or remove player protections.

Every intervention records action, target, observed reason, predicted effect, confidence, cost, and eventual outcome where attributable. The player can inspect this without a conversational language model. Player preferences are inferred cautiously; a single emergency action is not treated as a universal preference. Learned preference changes cannot change protections.

An emergency care policy exists before learning. It is subject to actual supplies, money, transport/capacity abstractions, and biology. Competence does not guarantee survival of an already fatally damaged plant.

## 5. Interface

### Main view

- Orthographic 2.5D nursery with selectable plants, zones, benches, and containers.
- Persistent cash, date/time/speed, manager status, and prioritized alerts.
- Plant inspection: recognizable appearance, concise condition summary, recent changes, care actions, protections, price/market state.
- Optional scientific tabs: organ topology, carbon/water/nutrient pools, root-zone profile, lineage, environmental history, model coverage.
- Shop panel: inventory, suppliers, listings, completed transactions, demand summaries.
- Companion panel: activity feed, policies, learning progress, uncertainty, comparison with baseline.
- Save panel: named snapshots, autosave status, export/import, explicit restore confirmation.

### Input and accessibility

- Tap/click selects; second explicit control opens actions. No hover-only actions.
- Pinch or wheel zoom; drag empty space pans. Placement also supports select-destination-confirm without dragging.
- Interactive touch targets at least 44 CSS pixels. At 360 CSS-pixel width, primary actions need no horizontal page scrolling.
- Keyboard focus visible; panels and actions usable with Tab/Enter/Escape. Shortcuts never fire while typing.
- Status uses text/icons as well as color. Reduced-motion mode disables nonessential animation.
- Prune previews and sale summaries show consequences before player execution. Companion actions follow policies without repeated approval prompts.
- Disconnect/reconnect status is explicit; pending commands display their authoritative result rather than assuming success.

### Graphics

Procedural stems, leaf instances, flowers, fruit, pots, substrate, and terrain; generated bark/leaf patterns. Meshes are projections of server topology with client-only visual jitter from a separate visual seed. Visual randomness cannot consume biological RNG streams.

Nursery-scale plants use instanced/coarsened geometry. Inspection increases mesh detail and exposes root cutaways. It cannot create missing physiology or change sim results. Static lighting and restrained shadows are acceptable mobile fallbacks; visual features must degrade without changing controls or biology.

## 6. Release coverage

R1: complete vegetative nursery loop, real online prediction/preference learning, full management of available actions, six representative species with declared approximations, procedural graphics, saves, password access.

R2: development, reproduction, propagation, genetics, pollination, harvest and products.

R3: advanced bonsai structure, root pruning, wiring, wounds, grafting with validated compatibility.

R4: layered substrates, fertilizer chemistry, compost cohorts, pests/pathogens and ecological coupling.

R5: production planning, learned demand/pricing, robust autonomous multi-season shop operation.

R6: expanded species and calibrated 1,000-plant performance release.

R7: opt-in validated rule-proposal laboratory.

R1 physiology must already respond to root-zone water, light, carbon, temperature, and nutrients; later releases deepen those models rather than substitute decorative features. A bonsai-form starter in R1 is not a claim that advanced bonsai craft is complete.
