import { describe, expect, it } from "vitest";

import {
  formatPlantSummary,
  loadNurseryApp,
  parseNurseryApi,
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
          zone_water_kg: 0.12,
          reservoir_kg: 2.0,
          transpired_kg: 0.0,
          drainage_kg: 0.0,
          zone_nitrogen_kg: 0.02,
          zone_phosphorus_kg: 0.004,
          zone_potassium_kg: 0.008,
          dead_plant_count: 0,
          species_ids: ["ocimum_basilicum"],
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
          zone_water_kg: 0.12,
          water_stress_factor: 0.74,
          species_id: "ocimum_basilicum",
          site_id: "greenhouse",
          alive: true,
          damage_fraction: 0.0,
          nutrient_stress_factor: 1.0,
          zone_nitrogen_kg: 0.02,
          zone_phosphorus_kg: 0.004,
          zone_potassium_kg: 0.008,
        },
      ],
    );

    expect(target.textContent).toContain("Tick 3");
    expect(target.textContent).toContain("Plant 1");
    expect(target.textContent).toContain("Fertilizer input, economy");
    expect(formatPlantSummary).toBeDefined();
  });

  it("parses nursery API payloads", () => {
    const parsed = parseNurseryApi(
      {
        sim_tick: 3,
        world_revision: 3,
        nursery: {
          plant_count: 1,
          organ_count: 3,
          reserve_carbon_kg: 0.01,
          structural_carbon_kg: 0.036,
          atmospheric_carbon_uptake_kg: 0.00001,
          zone_water_kg: 0.12,
          reservoir_kg: 2.0,
          transpired_kg: 0.0,
          drainage_kg: 0.0,
          zone_nitrogen_kg: 0.02,
          zone_phosphorus_kg: 0.004,
          zone_potassium_kg: 0.008,
          dead_plant_count: 0,
          species_ids: ["ocimum_basilicum"],
        },
      },
      {
        plants: [
          {
            plant_id: 1,
            organ_count: 3,
            leaf_area_m2: 0.06,
            stem_length_m: 0.18,
            reserve_carbon_kg: 0.01,
            structural_carbon_kg: 0.036,
            zone_water_kg: 0.12,
            water_stress_factor: 0.74,
            species_id: "ocimum_basilicum",
            site_id: "greenhouse",
            alive: true,
            damage_fraction: 0.0,
            nutrient_stress_factor: 1.0,
            zone_nitrogen_kg: 0.02,
            zone_phosphorus_kg: 0.004,
            zone_potassium_kg: 0.008,
          },
        ],
      },
    );

    expect(parsed?.world.sim_tick).toBe(3);
    expect(parsed?.plants).toHaveLength(1);
    expect(parseNurseryApi({}, {})).toBeNull();
  });

  it("loads and renders nursery projections", async () => {
    const target = document.createElement("main");
    const world = {
      sim_tick: 3,
      world_revision: 3,
      nursery: {
        plant_count: 1,
        organ_count: 3,
        reserve_carbon_kg: 0.01,
        structural_carbon_kg: 0.036,
        atmospheric_carbon_uptake_kg: 0.00001,
        zone_water_kg: 0.12,
        reservoir_kg: 2.0,
        transpired_kg: 0.0,
        drainage_kg: 0.0,
        zone_nitrogen_kg: 0.02,
        zone_phosphorus_kg: 0.004,
        zone_potassium_kg: 0.008,
        dead_plant_count: 0,
        species_ids: ["ocimum_basilicum"],
      },
    };
    const plants = {
      plants: [
        {
          plant_id: 1,
          organ_count: 3,
          leaf_area_m2: 0.06,
          stem_length_m: 0.18,
          reserve_carbon_kg: 0.01,
          structural_carbon_kg: 0.036,
          zone_water_kg: 0.12,
          water_stress_factor: 0.74,
          species_id: "ocimum_basilicum",
          site_id: "greenhouse",
          alive: true,
          damage_fraction: 0.0,
          nutrient_stress_factor: 1.0,
          zone_nitrogen_kg: 0.02,
          zone_phosphorus_kg: 0.004,
          zone_potassium_kg: 0.008,
        },
      ],
    };
    const fetcher = async (input: string | URL | Request): Promise<Response> =>
      new Response(JSON.stringify(String(input).includes("/plants") ? plants : world), {
        status: 200,
      });

    await loadNurseryApp(target, fetcher as typeof fetch);

    expect(target.textContent).toContain("Arboria Nursery");
    expect(target.textContent).toContain("Plant 1");
  });

  it("reports nursery fetch failures honestly", async () => {
    const target = document.createElement("main");
    const fetcher = async (): Promise<Response> => new Response("{}", { status: 500 });

    await loadNurseryApp(target, fetcher as typeof fetch);

    expect(target.textContent).toContain("unavailable");
  });
});
