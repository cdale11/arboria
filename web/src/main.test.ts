import { describe, expect, it } from "vitest";

import {
  formatPlantSummary,
  renderDependencyBaseline,
  renderNurseryApp,
} from "./main.ts";

describe("dependency baseline app", () => {
  it("renders an honest project status", () => {
    const target = document.createElement("main");

    renderDependencyBaseline(target);

    expect(target.textContent).toContain("Dependency baseline verified");
    expect(target.textContent).toContain("not implemented yet");
  });

  it("renders living nursery projections honestly", () => {
    const target = document.createElement("main");

    renderNurseryApp(
      target,
      {
        sim_tick: 3,
        world_revision: 3,
        nursery: {
          plant_count: 1,
          organ_count: 3,
          reserve_carbon_kg: 0.01,
          structural_carbon_kg: 0.036,
          atmospheric_carbon_uptake_kg: 0.00001,
        },
      },
      [
        {
          plant_id: 1,
          organ_count: 3,
          leaf_area_m2: 0.06,
          stem_length_m: 0.18,
          reserve_carbon_kg: 0.01,
          structural_carbon_kg: 0.036,
        },
      ],
    );

    expect(target.textContent).toContain("Tick 3");
    expect(target.textContent).toContain("Plant 1");
    expect(target.textContent).toContain("Water, nutrients, economy");
    expect(formatPlantSummary).toBeDefined();
  });
});
