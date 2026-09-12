# Learning, adaptation, and emergence

## 1. Responsibilities

Learning is a core R1 behavior, not a decorative future promise. It predicts plant responses and adapts manager choices; later releases add demand learning, longer-horizon production, evolutionary selection, and experimental rule proposals.

The authoritative biology remains explicit and resource-conserving. Models cannot directly change plant pools, account balances, ownership, compatibility, or protections. They propose predictions/actions that ordinary validators evaluate.

Do not require a large language model, pretrained download, cloud API, GPU, or internet connection for the playable game. Explanations can use structured reasons rendered as readable text.

## 2. R1 learned predictor

Adopt a small ensemble of three feed-forward neural networks as the initial candidate, each with two 64-unit hidden layers. This is an engineering starting point, not an empirically optimal architecture. Use bounded activations/outputs where appropriate, float32 model tensors, explicit seeded initialization, and fully serialized optimizer state. NumPy implementation is acceptable if gradient/numerical tests pass; a Conda-supplied framework is allowed only with measured resource justification.

### Input contract

Versioned features include observed soil water fraction, plant hydraulic stress, assimilate reserves normalized by structural mass, nutrient status, leaf/root area ratios, recent temperature/light/humidity, species functional traits, season/time-of-day encodings, and candidate action amounts. No organ IDs used as ordinal biological features. Include missingness masks and feature availability; do not zero-fill unknowns indistinguishably from measured zero.

Normalize with streaming statistics fitted only on past training observations. Checkpoint counts, means, and variance accumulators. Freeze the normalization snapshot used by a particular model activation. Changes require transforming weights appropriately or retraining/revalidating, not silently reinterpreting input scale.

Targets over a one-sim-hour horizon initially: root-zone water change, reserve-carbon change, and stress change. Record units and normalization. Delayed labels are joined by world/timeline/target/horizon IDs. Death, sale, repotting, or other interventions during the horizon require explicit censoring or action-sequence features, not an invalid single-action label.

Loss is a scaled robust regression loss with target-specific documented weights. Training uses a bounded replay buffer, chronological holdout, gradient-norm clipping, finite checks, and validation before activation. Learning rates, batch sizes, and clipping thresholds are versioned engineering hyperparameters verified in R1; they are not biological constants.

### Initial resource budget

- Replay buffer: at most 50,000 compact transitions, configurable downward.
- Batch size starting point: 128.
- At most 20 optimizer steps per simulated hour, further limited by a real-time worker budget.
- Background training target: at most 10% of total host CPU capacity averaged over five minutes; report how measured.
- Never accumulate an unbounded backlog to "catch up" training; missed optional training opportunities are recorded, not queued indefinitely.
- Pause, restore, or schema change cancels outstanding work; no training across abandoned timelines.

Resource limits may be tuned with evidence. Learning cadence and missed-update counters are persisted so performance constraints are visible.

## 3. Manager algorithm

1. Read an immutable observation containing actual resources, constraints, and supported actions.
2. Generate a bounded candidate set from horticultural policies and shop opportunities.
3. Remove actions prohibited by protections, compatibility, available stock, money, or capacity.
4. Use the learned predictor to estimate short-horizon effects and uncertainty. Compare against a conservative baseline where prediction is uncertain or out of distribution.
5. Score survival/health, future value, resource efficiency, and inferred player preferences with a documented objective. Hard constraints remain outside the score.
6. Enqueue selected actions; revalidate at execution because player commands may have changed the world.
7. Record predicted/actual outcomes and policy version.

The initial objective is lexicographic: enforce protections and solvency, prioritize feasible responses to severe health risk, then improve expected shop value and player preferences. It cannot sacrifice a protected plant for a larger scalar reward. Already irrecoverable plants may be discarded under manager policy, with explanations and material accounting.

Preference learning begins with a small regularized online model over interpretable features (retaining cultivars, desired inventory mix, selling versus keeping, labor-saving choices). Mark emergency actions and ambiguous observations; avoid treating all interventions as demonstrations. Show learned preferences and provide a reset/override. Overrides are distinct from inferred values and take precedence.

R1 planning supports purchases, sales, water, nutrients, relocation, and available plant-care actions. Later pruning/propagation/harvest planners arrive with the respective biological release; never emit unknown commands to imply capability.

## 4. Evaluation and activation

Every training result includes source timeline, input schema, catalog/rule versions, architecture hash, dataset range, optimizer step, normalization snapshot, loss metrics, and finite checks. Reject stale/incompatible results. Activate only at a safe world boundary after validation.

Validate against both recent chronological holdout and retained anchor scenarios to detect forgetting. Do not validate on the same batch used to train. Compare with persistence/linear or horticultural baselines as appropriate. Record at least prediction error, calibration of ensemble disagreement, action outcomes, constraint rejections, health losses, profit, inventory diversity, and resource use.

If training diverges, discard the candidate, retain the last accepted model and optimizer checkpoint, and reduce or suspend training with a recorded reason. The baseline caretaker remains available; disclose whether actions are currently learned-model-assisted or baseline-only. No silent presentation of fallback behavior as successful learning.

Behavioral evidence must include ablation: identical initial worlds and controlled external streams with learning enabled versus frozen, over multiple seeds. Online prediction improvement alone is insufficient to claim better management; demonstrate a consequential action change and measured outcome without relaxed constraints.

## 5. Reproducibility and save semantics

Persist initialization/training/sample-selection RNG streams, data ordering, delayed labels, model tensors, optimizer moments, step counters, feature schema, normalization, preference model, evaluation anchors, active/candidate metadata, and scheduling counters.

Exact continuation is tested in a deterministic execution mode with specified package versions, thread policy, and synchronous training barriers. Ordinary background scheduling may change model activation timing; record accepted activation events for diagnosis. Do not promise bitwise reproduction across CPU/GPU backends or different numerical library versions.

Randomness enables variation; explicit seeds and persistent state enable debugging. Procedural graphics uses independent randomness. Biological mutation, weather, demand, and learner sampling use separate named streams so adding a visual feature cannot alter reproduction.

## 6. Later learning releases

R2 evaluates trait evolution and selection under explicit genotype–phenotype rules. Evolutionary search cannot mutate species compatibility, costs, or conservation laws.

R5 adds adaptive demand forecasting, constrained price selection, inventory/propagation scheduling, and seasonal model-predictive planning. Customers have budgets and preferences; profit must correspond to transactions with demand, not synthetic random gains. Exploration is bounded by player policies and stock/cash exposure. Demand shifts use explicit customer/environment causes.

Novelty metrics include phenotype diversity, distinct viable recipes, strategy diversity, and previously untested interactions. Novelty is not automatically usefulness or scientific validity. Store examples with causal traces and compare to nonadaptive baselines.

## 7. R7 restricted rule-proposal laboratory

This release is opt-in and may remain blocked if its research gates fail. The base game must not depend on it.

Allowed initial proposal forms: material recipes, bounded modifier expressions over named state, conditional interaction rules, and item definitions built from known physical categories. Proposals may introduce a new interaction through this vocabulary, but cannot invent executable Python/JavaScript, import code, use files/network, allocate unbounded memory, redefine currency, or replace conservation accounting.

Example structural schema (illustrative, not an implemented language):

```text
proposal_id, schema_version, parent_rule_set_hash
kind: recipe | bounded_interaction | item_definition
inputs: typed existing material/state references
preconditions: bounded expression AST
effects: typed resource transfers and bounded parameter modifiers
provenance: generator, training checkpoint, motivation
limits: evaluation cost, maximum applications per tick
```

Validation pipeline:

1. Parse against a closed, typed schema; reject unknown operations and cycles/unbounded recursion.
2. Check dimensions, resources, compatibility, bounds, dependencies, and evaluation cost.
3. Execute in an isolated test world with fixed CPU/memory/tick budgets; no access to the live shop.
4. Run adversarial, conservation, stability, economy-exploit, and multi-season scenarios.
5. Evaluate novelty and usefulness separately from validity; preserve rejected proposals and reasons within bounded history.
6. Activate a versioned rule set only in opted-in worlds at a checkpoint boundary, with a retained preactivation snapshot.
7. On failure, roll back the entire world to the compatible preactivation snapshot, not only rule text while retaining impossible assets. Explain lost postactivation progress.

The generation method and acceptance thresholds require R7 feasibility evidence. If the proposal vocabulary cannot express a requested new mechanic, ask for an ordinary engineering extension; never claim arbitrary open-ended scientific discovery.
