# Shop economy contract

## 1. Money

Cash is tracked in integer minor units (`cash_minor`) and can never go
negative. All prices are integer minor units; the only float-to-money
conversion is reservoir water at 200 minor/kg, rounded up per purchase with a
1-minor minimum. No credit, interest, random pricing, or synthetic profit
exists.

## 2. Starting state and prices

- Starting cash: 20000 minor units.
- Reservoir water refill: 200 minor/kg into a 5.0 kg capped reservoir.
- Per-species purchase prices, sale prices, and finite buyer demand live in
  `PRICE_TABLE` (`src/arboria/sim/economy.py`). All values are provisional
  gameplay parameters, not market data. Sale prices sit below purchase prices
  structurally, so buy-then-sell always loses cash.

## 3. Commands

- `shop.buy_water {water_kg}` charges cash and adds reservoir water. Rejected
  on non-positive amounts, insufficient cash, or reservoir overflow.
- `shop.buy_plant {species_id}` charges the purchase price and adds one live
  starter plant of a catalog species with fresh plant/organ IDs, starter
  zones, and a species-mapping entry. Rejected on unknown species or
  insufficient cash.
- `shop.sell_plant {plant_id}` removes a live plant with its zones and mapping
  entry, credits the sale price, and consumes one unit of species demand.
  Rejected on unknown plants, dead plants, exhausted demand, or unknown
  species. Reselling an already-sold plant reports unknown plant.

All three run through the standard bounded command envelope with receipts, so
duplicate `command_id` submissions apply once and validation failures are
receipt-backed rejections, never silent state changes.

## 4. Persistence

Checkpoints (nursery schema version 4) carry the plant-to-species mapping and
the economy state (cash plus per-species demand). Restore and startup fall
back to the deterministic starter mapping and starter economy for older
checkpoints. Cash, demand, reservoir, and plant inventory stay consistent
across save/restore cycles.
