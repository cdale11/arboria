import { describe, expect, it, vi } from "vitest";

import { mountNurseryApp, type NurseryApi, type NurseryClient } from "./main.ts";


function api(protectedPlant = false): NurseryApi {
  return {
    world: {
      sim_tick: 3,
      world_revision: protectedPlant ? 4 : 3,
      nursery: {
        plant_count: 1,
        organ_count: 3,
        species_ids: ["ocimum_basilicum"],
        cash_minor: 20000,
        demand_remaining: [{ species_id: "ocimum_basilicum", remaining: 3 }],
        protected_plant_ids: protectedPlant ? [1] : [],
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
      },
    },
    plants: [
      {
        plant_id: 1,
        species_id: "ocimum_basilicum",
        site_id: "greenhouse",
        protected: protectedPlant,
        organ_count: 3,
        leaf_area_m2: 0.06,
        stem_length_m: 0.18,
        reserve_carbon_kg: 0.01,
        structural_carbon_kg: 0.036,
        zone_water_kg: 0.12,
        water_stress_factor: 0.74,
        alive: true,
        damage_fraction: 0.0,
        nutrient_stress_factor: 1.0,
        zone_nitrogen_kg: 0.02,
        zone_phosphorus_kg: 0.004,
        zone_potassium_kg: 0.008,
      },
    ],
  };
}


function click(target: HTMLElement, action: string): void {
  const button = target.querySelector<HTMLButtonElement>(`button[data-action="${action}"]`);
  expect(button).not.toBeNull();
  button?.click();
}


describe("R1 playable nursery e2e flow", () => {
  it("covers inspect, water, sale, protection, clock, and save controls", async () => {
    let protectedPlant = false;
    const client: NurseryClient = {
      load: vi.fn(async () => api(protectedPlant)),
      inspect: vi.fn(async () => ({
        plant_id: 1,
        species_id: "ocimum_basilicum",
        site_id: "greenhouse",
        protected: protectedPlant,
        alive: true,
        organs: [{ organ_id: 1, kind: "root", alive: true, damage_fraction: 0 }],
      })),
      sendCommand: vi.fn(async (kind: string) => {
        if (kind === "nursery.protect") {
          protectedPlant = true;
        }
        if (kind === "nursery.unprotect") {
          protectedPlant = false;
        }
        return { status: "applied", reason: null };
      }),
      pauseClock: vi.fn(async () => {}),
      resumeClock: vi.fn(async () => {}),
      setSpeed: vi.fn(async () => {}),
      checkpoint: vi.fn(async () => {}),
      namedSave: vi.fn(async () => {}),
      listSaves: vi.fn(async () => [{ name: "before-sale" }]),
      restore: vi.fn(async () => {}),
      exportSave: vi.fn(async () => ({
        format: "arboria-current-domain-checkpoint+zip+base64",
        checkpoint_id: "checkpoint-1",
        archive_base64: "YXJib3JpYQ==",
      })),
      importSave: vi.fn(async () => {}),
      companionStatus: vi.fn(async () => ({
        enabled: false,
        water_threshold: 0.55,
        max_actions_per_tick: 1,
        actions_proposed: 0,
        actions_applied: 0,
        actions_rejected: 0,
        last_reason: null,
        last_plant_id: null,
      })),
      setCompanion: vi.fn(async (policy) => policy),
      runCompanion: vi.fn(async () => ({
        enabled: false,
        water_threshold: 0.55,
        max_actions_per_tick: 1,
        actions_proposed: 0,
        actions_applied: 0,
        actions_rejected: 0,
        last_reason: null,
        last_plant_id: null,
      })),
    };
    const target = document.createElement("main");

    await mountNurseryApp(target, client);
    click(target, "inspect");
    await vi.waitFor(() => expect(client.inspect).toHaveBeenCalledWith(1));
    click(target, "water");
    await vi.waitFor(() => expect(client.sendCommand).toHaveBeenCalledWith("nursery.water", {
      plant_id: 1,
      water_kg: 0.02,
    }));
    click(target, "protect");
    await vi.waitFor(() => expect(client.sendCommand).toHaveBeenCalledWith("nursery.protect", {
      plant_id: 1,
    }));
    await vi.waitFor(() =>
      expect(target.querySelector('button[data-action="unprotect"]')).not.toBeNull(),
    );
    click(target, "unprotect");
    await vi.waitFor(() => expect(client.sendCommand).toHaveBeenCalledWith("nursery.unprotect", {
      plant_id: 1,
    }));
    click(target, "sell");
    await vi.waitFor(() => expect(client.sendCommand).toHaveBeenCalledWith("shop.sell_plant", {
      plant_id: 1,
    }));
    click(target, "pause");
    click(target, "resume");
    click(target, "checkpoint");
    click(target, "export");
    await vi.waitFor(() => expect(client.exportSave).toHaveBeenCalled());
    const archive = target.querySelector<HTMLTextAreaElement>('[data-action="export-archive"]');
    archive!.value = "YXJjaGl2ZQ==";
    click(target, "import");
    await vi.waitFor(() => expect(client.pauseClock).toHaveBeenCalled());
    await vi.waitFor(() => expect(client.resumeClock).toHaveBeenCalled());
    await vi.waitFor(() => expect(client.checkpoint).toHaveBeenCalled());
    await vi.waitFor(() => expect(client.importSave).toHaveBeenCalledWith("YXJjaGl2ZQ=="));

    expect(target.textContent).toContain("Arboria Nursery");
    expect(target.querySelectorAll("button").length).toBeGreaterThan(5);
  });
});
