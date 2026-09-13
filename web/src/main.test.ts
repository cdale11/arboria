import { describe, expect, it, vi } from "vitest";

import {
  createApiClient,
  formatPlantSummary,
  loadNurseryApp,
  mountNurseryApp,
  parseNurseryApi,
  readCsrfToken,
  renderDependencyBaseline,
  renderNurseryApp,
  renderNurseryScene,
  type NurseryApi,
  type NurseryClient,
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
          cash_minor: 20000,
          demand_remaining: [{ species_id: "ocimum_basilicum", remaining: 3 }],
          protected_plant_ids: [],
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
          protected: false,
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
    expect(target.querySelector('[data-action="nursery-scene"]')).not.toBeNull();
    expect(target.textContent).toContain("Fertilizer input, price forecasting");
    expect(formatPlantSummary).toBeDefined();
  });

  it("generates a display-only nursery scene from plant projections", () => {
    const scene = renderNurseryScene(stubApiData().plants);

    expect(scene.getAttribute("role")).toBe("img");
    expect(scene.getAttribute("aria-label")).toContain("2.5D");
    expect(scene.querySelector('[data-action="nursery-floor"]')).not.toBeNull();
    expect(scene.querySelectorAll("ellipse[data-plant-id]").length).toBeGreaterThan(1);
    expect(scene.querySelector('line[data-plant-id="1"]')).not.toBeNull();
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
          cash_minor: 20000,
          demand_remaining: [{ species_id: "ocimum_basilicum", remaining: 3 }],
          protected_plant_ids: [],
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
            protected: false,
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
        cash_minor: 20000,
        demand_remaining: [{ species_id: "ocimum_basilicum", remaining: 3 }],
        protected_plant_ids: [],
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
          protected: false,
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

function stubApiData(): NurseryApi {
  return {
    world: {
      sim_tick: 3,
      world_revision: 3,
      nursery: {
        plant_count: 1,
        organ_count: 3,
        species_ids: ["ocimum_basilicum"],
        cash_minor: 20000,
        demand_remaining: [{ species_id: "ocimum_basilicum", remaining: 3 }],
        protected_plant_ids: [],
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
        protected: false,
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

function stubClient(overrides: Partial<NurseryClient> = {}): NurseryClient {
  return {
    load: async () => stubApiData(),
    inspect: async (plantId: number) => ({
      plant_id: plantId,
      species_id: "ocimum_basilicum",
      site_id: "greenhouse",
      protected: false,
      alive: true,
      organs: [{ organ_id: 1, kind: "root", alive: true, damage_fraction: 0 }],
    }),
    sendCommand: async () => ({ status: "applied", reason: null }),
    pauseClock: async () => {},
    resumeClock: async () => {},
    setSpeed: async () => {},
    checkpoint: async () => {},
    namedSave: async () => {},
    listSaves: async () => [{ name: "first" }],
    restore: async () => {},
    exportSave: async () => ({
      format: "arboria-current-domain-checkpoint+zip+base64",
      checkpoint_id: "checkpoint-1",
      archive_base64: "YXJib3JpYQ==",
    }),
    importSave: async () => {},
    ...overrides,
  };
}

async function mountedClient(
  overrides: Partial<NurseryClient> = {},
): Promise<{ target: HTMLElement; client: NurseryClient }> {
  const client = stubClient(overrides);
  const target = document.createElement("main");
  await mountNurseryApp(target, client);
  return { target, client };
}

function clickAction(target: HTMLElement, action: string, plantId?: number): void {
  const selector =
    plantId === undefined
      ? `button[data-action="${action}"]`
      : `button[data-action="${action}"][data-plant-id="${plantId}"]`;
  const button = target.querySelector<HTMLButtonElement>(selector);
  expect(button).not.toBeNull();
  button?.click();
}

describe("nursery controls", () => {
  it("mounts the generated nursery scene in the live app", async () => {
    const { target } = await mountedClient();

    const scene = target.querySelector('[data-action="nursery-scene"]');

    expect(scene).not.toBeNull();
    expect(scene?.querySelector('[data-action="nursery-floor"]')).not.toBeNull();
    expect(scene?.querySelectorAll("ellipse[data-plant-id]").length).toBeGreaterThan(1);
  });

  it("reads the CSRF token from cookies", () => {
    expect(readCsrfToken("a=1; arboria_csrf=token123; b=2")).toBe("token123");
    expect(readCsrfToken("a=1")).toBeNull();
    expect(readCsrfToken("arboria_csrf=")).toBeNull();
  });

  it("sends commands with world snapshot and CSRF header", async () => {
    const seen: { url: string; init?: RequestInit }[] = [];
    const fetcher = (async (url: string, init?: RequestInit): Promise<Response> => {
      seen.push({ url: String(url), init });
      if (String(url).includes("/commands")) {
        return new Response(JSON.stringify({ status: "applied" }), { status: 200 });
      }
      return new Response(
        JSON.stringify({ world_id: "w", timeline_id: "t", request_epoch: 1 }),
        { status: 200 },
      );
    }) as typeof fetch;
    const client = createApiClient(fetcher, () => "csrf-token");

    const receipt = await client.sendCommand("nursery.water", { plant_id: 1, water_kg: 0.02 });

    expect(receipt.status).toBe("applied");
    const commandCall = seen.find((call) => call.url.includes("/commands"));
    expect(commandCall?.init?.headers).toMatchObject({ "x-arboria-csrf": "csrf-token" });
    const body = JSON.parse(String(commandCall?.init?.body));
    expect(body).toMatchObject({
      schema_version: 1,
      world_id: "w",
      timeline_id: "t",
      request_epoch: 1,
      kind: "nursery.water",
      payload: { plant_id: 1, water_kg: 0.02 },
    });
    expect(typeof body.command_id).toBe("string");
  });

  it("refuses commands without a CSRF token", async () => {
    const fetcher = (async (): Promise<Response> => new Response("{}", { status: 200 })) as typeof fetch;
    const client = createApiClient(fetcher, () => null);

    await expect(client.sendCommand("nursery.water", {})).rejects.toThrow("CSRF");
  });

  it("mounts care, shop, clock, and save controls", async () => {
    const { target } = await mountedClient();

    expect(target.textContent).toContain("Tick 3");
    for (const action of [
      "inspect",
      "water",
      "sell",
      "protect",
      "buy-water",
      "buy-plant",
      "pause",
      "resume",
      "set-speed",
      "checkpoint",
      "named-save",
      "restore",
      "export",
      "import",
      "refresh",
    ]) {
      expect(target.querySelector(`[data-action="${action}"]`)).not.toBeNull();
    }
  });

  it("waters a plant and reports the receipt", async () => {
    const sendCommand = vi.fn(async () => ({ status: "applied", reason: null }));
    const { target } = await mountedClient({ sendCommand });

    clickAction(target, "water", 1);
    await vi.waitFor(() => expect(sendCommand).toHaveBeenCalled());
    await vi.waitFor(() =>
      expect(target.querySelector('[data-action="result"]')?.textContent).toContain(
        "nursery.water applied",
      ),
    );
    expect(sendCommand).toHaveBeenCalledWith("nursery.water", {
      plant_id: 1,
      water_kg: 0.02,
    });
  });

  it("surfaces command rejections honestly", async () => {
    const sendCommand = vi.fn(async () => ({ status: "rejected", reason: "no buyer demand" }));
    const { target } = await mountedClient({ sendCommand });

    clickAction(target, "sell", 1);
    await vi.waitFor(() =>
      expect(target.querySelector('[data-action="result"]')?.textContent).toContain(
        "no buyer demand",
      ),
    );
  });

  it("buys water and plants through the shop", async () => {
    const sendCommand = vi.fn(async () => ({ status: "applied", reason: null }));
    const { target } = await mountedClient({ sendCommand });

    clickAction(target, "buy-water");
    await vi.waitFor(() => expect(sendCommand).toHaveBeenCalledWith("shop.buy_water", {
      water_kg: 0.5,
    }));
    clickAction(target, "buy-plant");
    await vi.waitFor(() => expect(sendCommand).toHaveBeenCalledWith("shop.buy_plant", {
      species_id: "ocimum_basilicum",
    }));
  });

  it("protects and unprotects plants through validated commands", async () => {
    const sendCommand = vi.fn(async () => ({ status: "applied", reason: null }));
    const firstLoad = stubApiData();
    const protectedLoad = stubApiData();
    firstLoad.plants[0]!.protected = false;
    protectedLoad.plants[0]!.protected = true;
    protectedLoad.world.nursery.protected_plant_ids = [1];
    let loads = 0;
    const load = vi.fn(async () => (loads++ === 0 ? firstLoad : protectedLoad));
    const { target } = await mountedClient({ load, sendCommand });

    clickAction(target, "protect", 1);
    await vi.waitFor(() => expect(sendCommand).toHaveBeenCalledWith("nursery.protect", {
      plant_id: 1,
    }));
    await vi.waitFor(() => expect(target.querySelector('[data-action="unprotect"]')).not.toBeNull());
    clickAction(target, "unprotect", 1);
    await vi.waitFor(() => expect(sendCommand).toHaveBeenCalledWith("nursery.unprotect", {
      plant_id: 1,
    }));
  });

  it("inspects a plant and shows organs", async () => {
    const inspect = vi.fn(stubClient().inspect);
    const { target } = await mountedClient({ inspect });

    clickAction(target, "inspect", 1);
    await vi.waitFor(() => expect(inspect).toHaveBeenCalledWith(1));
    await vi.waitFor(() => expect(target.textContent).toContain("Organ 1 root"));
  });

  it("pauses, resumes, and sets clock speed", async () => {
    const pauseClock = vi.fn(async () => {});
    const resumeClock = vi.fn(async () => {});
    const setSpeed = vi.fn(async () => {});
    const { target } = await mountedClient({ pauseClock, resumeClock, setSpeed });

    clickAction(target, "pause");
    await vi.waitFor(() => expect(pauseClock).toHaveBeenCalled());
    clickAction(target, "resume");
    await vi.waitFor(() => expect(resumeClock).toHaveBeenCalled());
    const speedSelect = target.querySelector<HTMLSelectElement>('[data-action="speed-select"]');
    speedSelect!.value = "48";
    clickAction(target, "set-speed");
    await vi.waitFor(() => expect(setSpeed).toHaveBeenCalledWith(48));
  });

  it("saves and restores through named saves", async () => {
    const checkpoint = vi.fn(async () => {});
    const namedSave = vi.fn(async () => {});
    const restore = vi.fn(async () => {});
    const { target } = await mountedClient({ checkpoint, namedSave, restore });

    clickAction(target, "checkpoint");
    await vi.waitFor(() => expect(checkpoint).toHaveBeenCalled());
    const nameInput = target.querySelector<HTMLInputElement>('[data-action="save-name"]');
    nameInput!.value = "before-sale";
    clickAction(target, "named-save");
    await vi.waitFor(() => expect(namedSave).toHaveBeenCalledWith("before-sale"));
    clickAction(target, "restore");
    await vi.waitFor(() => expect(restore).toHaveBeenCalledWith("first"));
  });

  it("exports and imports backup archives", async () => {
    const exportSave = vi.fn(stubClient().exportSave);
    const importSave = vi.fn(async () => {});
    const { target } = await mountedClient({ exportSave, importSave });

    clickAction(target, "export");
    await vi.waitFor(() => expect(exportSave).toHaveBeenCalled());
    await vi.waitFor(() =>
      expect(target.querySelector('[data-action="result"]')?.textContent).toContain(
        "YXJib3JpYQ==",
      ),
    );
    const archive = target.querySelector<HTMLTextAreaElement>('[data-action="export-archive"]');
    expect(archive?.value).toBe("YXJib3JpYQ==");
    archive!.value = "YXJjaGl2ZQ==";
    clickAction(target, "import");
    await vi.waitFor(() => expect(importSave).toHaveBeenCalledWith("YXJjaGl2ZQ=="));
  });

  it("requires a save name before named saves", async () => {
    const namedSave = vi.fn(async () => {});
    const { target } = await mountedClient({ namedSave });

    clickAction(target, "named-save");
    await vi.waitFor(() =>
      expect(target.querySelector('[data-action="result"]')?.textContent).toContain(
        "Save name is required",
      ),
    );
    expect(namedSave).not.toHaveBeenCalled();
  });
});
