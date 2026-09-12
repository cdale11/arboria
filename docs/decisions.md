# Decision register

Date of baseline: 2026-09-12. Status labels: **confirmed** = user choice; **adopted** = engineering default within delegated authority; **gate** = evidence or clarification required before the affected implementation can be accepted.

## Confirmed requirements

| ID | Decision | Consequence |
| --- | --- | --- |
| D01 | Organ-level functional biology | Explicit topology and coupled resource processes; no requirement for whole-plant cellular simulation |
| D02 | Accelerated continuous time | Client absence does not alter progression |
| D03 | Resume saved time after server downtime | No wall-clock catch-up on restart |
| D04 | 2.5D nursery targeting 500–1,000 plants | Visual instancing, biological cohorts, hardware acceptance tests |
| D05 | Mixed nursery | Temperate outdoors plus greenhouse; broad plant categories |
| D06 | Strict biological consequences | Death, disease, and commercial losses are possible; no hidden absence protection |
| D07 | Full shop manager | Autonomous care and commerce with explicit player protections |
| D08 | Compositional emergence then experimental rule invention | Rule invention is a later research gate, not assumed baseline capability |
| D09 | One shared shop with password | Concurrent owner devices; no initial multi-account economy |
| D10 | Conda `arboria`, npm inside it allowed | No pip fallback; all shell work activated |
| D11 | One-script build and run | Idempotent launcher owns setup/build/start contract |
| D12 | Save/load includes AI | Complete world and learner checkpoints |
| D13 | Maintain exhaustive docs and commit/push changes | Mandatory agent workflow |
| D14 | Clarify uncertainty through question tool | No silent consequential requirement decisions |

## Adopted engineering defaults

| ID | Default | Rationale and revision rule |
| --- | --- | --- |
| E01 | 1 sim day / 30 real minutes; speed 48× | User delegated selection; roughly weekly years. Balance review can change default with a decision record |
| E02 | Bind `0.0.0.0:8765` | Previously proposed and accepted single-shop option; configurable |
| E03 | Python + TypeScript, FastAPI, SQLite, Three.js | Scientific development and procedural web presentation without a large game engine |
| E04 | Conda numerical stack, optional Numba | Compile measured hot loops; versions resolved in R1 |
| E05 | NumPy-sized small online networks initially | No large-model runtime requirement; retain explicit checkpointable optimizers |
| E06 | 5 simulated minutes per base tick | At default speed, 6.25 real seconds per tick; renderer runs independently |
| E07 | 30 sim minutes between manager planning cycles | Emergency checks every base tick; commands can run at next tick |
| E08 | Autosave every 60 real seconds and on graceful shutdown | Bounded crash rollback without saving each frame |
| E09 | UTC-like 365-day synthetic calendar | No leap years/DST inside biology; latitude and season phase explicit |
| E10 | Positive normal speed range 1×–144× | Pause available for deliberate management/restore; higher test speeds are headless tools |
| E11 | Initial data under repository `var/` | Configurable absolute override; always excluded from Git |
| E12 | LAN-first HTTP deployment | Shared password; remote public access requires separately documented TLS deployment |

## Gates, not permission to invent

1. **Dependency resolution (R1):** prove the Python/NumPy/Numba/Node combination is available via allowed managers. A supported Python minor may replace the preexisting 3.14. Record the lock and compatibility result. Ask if an essential dependency cannot be installed under policy.
2. **Scientific parameter provenance (every species release):** inspect and cite trustworthy sources, distinguish observation from fit, and document uncertainty. Baseline equations here are modeling contracts, not empirical parameter tables.
3. **Starter species package (R1):** proposed representatives are *Acer palmatum*, *Ficus microcarpa*, *Crassula ovata*, *Ocimum basilicum*, *Solanum lycopersicum*, and *Chlorophytum comosum*. Deliver all six with honest R1 process coverage, or ask before substituting scope. Cultivar and CAM/C3 distinctions must be explicit.
4. **Performance (R1 and R6):** measure target hardware. If fidelity and scale cannot both pass, report the bottleneck and ask before reducing promised behavior or capacity.
5. **Biological calibration:** publish sources and reference scenarios before asserting realism. Uncalibrated coefficients must remain visibly provisional, with release review deciding whether they support the claimed coverage.
6. **Experimental rule invention (R7):** proposal generator technology is intentionally undecided. Benchmark local feasibility and ask the user before adopting remote AI, ongoing external cost, additional package-manager exceptions, or altered deployment requirements.
7. **Public release licensing:** no project license has been selected by the user. Ask before applying a project-wide license or representing the repository as open-source. Third-party component/asset licenses must be tracked regardless.

## Changing a decision

Add date, prior decision, proposed replacement, reason, evidence, affected schemas/tests/docs, and whether user clarification was required. Preserve the history. A local optimization that preserves observable contracts needs a changelog entry, not a new product decision; a change to biology, autonomy, time, persistence, or release scope does.
