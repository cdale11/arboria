import { describe, expect, it, vi } from "vitest";

import {
  createApiClient,
  acceptsNurserySnapshot,
  formatPlantSummary,
  formatWaterVolume,
  loadNurseryApp,
  mountNurseryApp,
  parseNurseryApi,
  parseNurseryStreamFrame,
  parseNurseryStreamSnapshot,
  NurseryWorldStore,
  NurseryStreamClient,
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
    expect(target.textContent).toContain("$200.00");
    expect(target.textContent).toContain("2.00 L");
    expect(target.textContent).toContain("Fertilizer input, price forecasting");
    expect(formatPlantSummary).toBeDefined();
  });

  it("formats player-facing water amounts as volume", () => {
    expect(formatWaterVolume(0.02)).toBe("20 mL");
    expect(formatWaterVolume(0.5)).toBe("500 mL");
    expect(formatWaterVolume(2)).toBe("2.00 L");
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

  it("rejects plant projections from a different world revision", () => {
    const world = {
      sim_tick: 3,
      world_revision: 3,
      nursery: {
        plant_count: 0, organ_count: 0, reserve_carbon_kg: 0,
        structural_carbon_kg: 0, atmospheric_carbon_uptake_kg: 0,
        zone_water_kg: 0, reservoir_kg: 0, transpired_kg: 0, drainage_kg: 0,
        zone_nitrogen_kg: 0, zone_phosphorus_kg: 0, zone_potassium_kg: 0,
        dead_plant_count: 0, species_ids: [], cash_minor: 0,
        demand_remaining: [], protected_plant_ids: [],
      },
    };
    expect(parseNurseryApi(world, { revision: 2, plants: [] })).toBeNull();
  });

  it("does not accept an older nursery snapshot", () => {
    const current = stubApiData();
    const older = {
      ...current,
      world: { ...current.world, world_revision: current.world.world_revision - 1 },
    };
    expect(acceptsNurserySnapshot(current, older)).toBe(false);
    expect(acceptsNurserySnapshot(current, current)).toBe(true);
  });

  it("publishes accepted snapshots and ignores stale replacements", () => {
    const store = new NurseryWorldStore();
    const listener = vi.fn();
    const current = stubApiData();
    const newer = {
      ...current,
      world: { ...current.world, world_revision: current.world.world_revision + 1 },
    };
    const unsubscribe = store.subscribe(listener);

    expect(store.replace(current)).toBe(true);
    expect(store.replace({ ...current, world: { ...current.world, world_revision: 1 } })).toBe(false);
    expect(store.replace(newer)).toBe(true);
    expect(store.snapshot).toBe(newer);
    expect(listener).toHaveBeenCalledTimes(2);
    unsubscribe();
    expect(store.replace({ ...newer, world: { ...newer.world, world_revision: 4 } })).toBe(true);
    expect(listener).toHaveBeenCalledTimes(2);
  });

  it("parses stream frames and only accepts deltas from the current revision", () => {
    const store = new NurseryWorldStore();
    const current = stubApiData();
    store.replace(current);
    const frame = parseNurseryStreamFrame({
      kind: "delta", revision: 4, base_revision: 3, payload: { plants: [] },
    });
    expect(frame).not.toBeNull();
    expect(store.canAcceptFrame(frame!, null)).toBe(true);
    expect(store.canAcceptFrame({ ...frame!, base_revision: 2 }, null)).toBe(false);
    expect(parseNurseryStreamFrame({ kind: "unknown", revision: 4 })).toBeNull();
  });

  it("converts an authoritative stream snapshot into the world store shape", () => {
    const frame = parseNurseryStreamFrame({
      kind: "snapshot", revision: 3, base_revision: 3,
      payload: {
        loop: { sim_tick: 3 },
        nursery: { ...stubApiData().world.nursery, plants: stubApiData().plants },
      },
    });
    const snapshot = frame === null ? null : parseNurseryStreamSnapshot(frame);
    expect(snapshot?.world.world_revision).toBe(3);
    expect(snapshot?.plants).toHaveLength(1);
  });

  it("opens the stream, pings, forwards frames, and reconnects after close", async () => {
    class FakeSocket {
      static readonly OPEN = 1;
      readyState = FakeSocket.OPEN;
      onopen: (() => void) | null = null;
      onmessage: ((event: { data: string }) => void) | null = null;
      onclose: (() => void) | null = null;
      sent: string[] = [];
      send(value: string): void { this.sent.push(value); }
      close(): void { this.onclose?.(); }
    }
    const sockets: FakeSocket[] = [];
    const frames: string[] = [];
    const client = new NurseryStreamClient("ws://nursery", {
      onFrame: (frame) => frames.push(frame.kind),
    }, () => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    client.start();
    const first = sockets[0]!;
    first.onopen?.();
    first.onmessage?.({ data: JSON.stringify({ kind: "pong", revision: 3, base_revision: 3, payload: {} }) });
    expect(JSON.parse(first.sent[0]!)).toEqual({ kind: "ping" });
    expect(frames).toEqual(["pong"]);
    first.onclose?.();
    await new Promise((resolve) => setTimeout(resolve, 260));
    expect(sockets).toHaveLength(2);
    client.stop();
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
    companionStatus: async () => ({
      enabled: false,
      water_threshold: 0.55,
      max_actions_per_tick: 1,
      actions_proposed: 0,
      actions_applied: 0,
      actions_rejected: 0,
      last_reason: null,
      last_plant_id: null,
    }),
    setCompanion: async () => ({
      enabled: false,
      water_threshold: 0.55,
      max_actions_per_tick: 1,
      actions_proposed: 0,
      actions_applied: 0,
      actions_rejected: 0,
      last_reason: null,
      last_plant_id: null,
    }),
    runCompanion: async () => ({
      enabled: false,
      water_threshold: 0.55,
      max_actions_per_tick: 1,
      actions_proposed: 0,
      actions_applied: 0,
      actions_rejected: 0,
      last_reason: null,
      last_plant_id: null,
    }),
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
    expect(target.querySelector(".scene-frame h2")?.textContent).toBe("Living nursery");
    expect(target.querySelectorAll(".plant-card")).toHaveLength(1);
    expect(target.textContent).toContain("Water 20 mL");
    expect(target.textContent).toContain("Buy 500 mL water");
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
      "companion-toggle",
      "companion-run",
      "refresh",
    ]) {
      expect(target.querySelector(`[data-action="${action}"]`)).not.toBeNull();
    }
  });

  it("runs the baseline caretaker through companion controls", async () => {
    const runCompanion = vi.fn(async () => ({
      enabled: true,
      water_threshold: 0.55,
      max_actions_per_tick: 1,
      actions_proposed: 1,
      actions_applied: 1,
      actions_rejected: 0,
      last_reason: "water plant 1",
      last_plant_id: 1,
    }));
    const { target } = await mountedClient({
      runCompanion,
      companionStatus: async () => ({
        enabled: true,
        water_threshold: 0.55,
        max_actions_per_tick: 1,
        actions_proposed: 0,
        actions_applied: 0,
        actions_rejected: 0,
        last_reason: null,
        last_plant_id: null,
      }),
    });

    clickAction(target, "companion-run");
    await vi.waitFor(() => expect(runCompanion).toHaveBeenCalled());
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
