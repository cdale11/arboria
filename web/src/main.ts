export interface PlantSummary {
  plant_id: number;
  species_id: string;
  site_id: string;
  protected: boolean;
  organ_count: number;
  leaf_area_m2: number;
  stem_length_m: number;
  reserve_carbon_kg: number;
  structural_carbon_kg: number;
  zone_water_kg: number;
  water_stress_factor: number;
  alive: boolean;
  damage_fraction: number;
  nutrient_stress_factor: number;
  zone_nitrogen_kg: number;
  zone_phosphorus_kg: number;
  zone_potassium_kg: number;
}

export interface NurseryWorld {
  sim_tick: number;
  world_revision: number;
  nursery: {
    plant_count: number;
    organ_count: number;
    species_ids: string[];
    cash_minor: number;
    demand_remaining: { species_id: string; remaining: number }[];
    reserve_carbon_kg: number;
    structural_carbon_kg: number;
    atmospheric_carbon_uptake_kg: number;
    zone_water_kg: number;
    reservoir_kg: number;
    transpired_kg: number;
    drainage_kg: number;
    zone_nitrogen_kg: number;
    zone_phosphorus_kg: number;
    zone_potassium_kg: number;
    dead_plant_count: number;
    protected_plant_ids: number[];
  };
}

export function renderDependencyBaseline(target: HTMLElement): void {
  target.replaceChildren();

  const heading = document.createElement("h1");
  heading.textContent = "Arboria";

  const status = document.createElement("p");
  status.textContent = "Dependency baseline verified. The playable nursery is not implemented yet.";

  target.append(heading, status);
}

export function formatPlantSummary(plant: PlantSummary): string {
  const health = plant.alive
    ? `Health: ${(100 - plant.damage_fraction * 100).toFixed(1)}%`
    : "Status: dead";
  return (
    `Plant ${plant.plant_id} · ${formatSpeciesName(plant.species_id)} · ${plant.site_id} · ` +
    `${plant.organ_count} organs · height ${formatLength(plant.stem_length_m)} · ` +
    `water ${formatMass(plant.zone_water_kg)} · N ${formatMass(plant.zone_nitrogen_kg)} · ` +
    health
  );
}

function formatSpeciesName(speciesId: string): string {
  return speciesId
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatLength(metres: number): string {
  return metres < 1 ? `${(metres * 100).toFixed(1)} cm` : `${metres.toFixed(2)} m`;
}

function formatMass(kg: number): string {
  return kg < 0.1 ? `${(kg * 1000).toFixed(1)} g` : `${kg.toFixed(2)} kg`;
}

function formatCash(minor: number): string {
  return `$${(minor / 100).toFixed(2)}`;
}

function formatNurseryStatus(world: NurseryWorld): string {
  return (
    `Tick ${world.sim_tick} · revision ${world.world_revision} · ` +
    `${world.nursery.plant_count} plants · ${world.nursery.dead_plant_count} dead · ` +
    `${world.nursery.organ_count} organs · Cash ${formatCash(world.nursery.cash_minor)} · ` +
    `Water reserve ${world.nursery.reservoir_kg.toFixed(2)} kg · ` +
    `Fertilizer input, price forecasting, and companion management are not implemented yet.`
  );
}

export function renderNurseryScene(plants: PlantSummary[]): SVGSVGElement {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 420 260");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Generated 2.5D nursery view");
  svg.dataset.action = "nursery-scene";

  const floor = document.createElementNS(svg.namespaceURI, "polygon");
  floor.setAttribute("points", "210,38 386,126 210,226 34,126");
  floor.setAttribute("fill", "#d8c49a");
  floor.setAttribute("stroke", "#9d8051");
  floor.setAttribute("stroke-width", "2");
  floor.setAttribute("data-action", "nursery-floor");
  svg.append(floor);

  for (const y of [96, 126, 156]) {
    const shelf = document.createElementNS(svg.namespaceURI, "polyline");
    shelf.setAttribute("points", `${84},${y} 210,${y - 60} 336,${y}`);
    shelf.setAttribute("fill", "none");
    shelf.setAttribute("stroke", "#b5925e");
    shelf.setAttribute("stroke-width", "1.5");
    shelf.setAttribute("opacity", "0.6");
    svg.append(shelf);
  }

  const ordered = [...plants].sort((left, right) => left.plant_id - right.plant_id);
  for (const [index, plant] of ordered.entries()) {
    const column = index % 4;
    const row = Math.floor(index / 4);
    const isoX = 116 + column * 48 - Math.min(row, 3) * 28;
    const isoY = 130 + column * 18 + Math.min(row, 3) * 24;
    const height = Math.max(24, Math.min(92, plant.stem_length_m * 280));
    const canopy = Math.max(12, Math.min(36, plant.leaf_area_m2 * 380));
    const stress = Math.min(1, plant.water_stress_factor, plant.nutrient_stress_factor);
    const leafColor = plant.alive
      ? `rgb(${Math.round(80 + (1 - stress) * 100)}, ${Math.round(120 + stress * 90)}, 70)`
      : "#6f6759";

    const group = document.createElementNS(svg.namespaceURI, "g");
    group.setAttribute("data-plant-id", String(plant.plant_id));
    group.setAttribute("opacity", plant.alive ? "1" : "0.7");

    const shadow = document.createElementNS(svg.namespaceURI, "ellipse");
    shadow.setAttribute("cx", String(isoX + 10));
    shadow.setAttribute("cy", String(isoY + 12));
    shadow.setAttribute("rx", "28");
    shadow.setAttribute("ry", "9");
    shadow.setAttribute("fill", "#4b3a28");
    shadow.setAttribute("opacity", "0.22");
    group.append(shadow);

    const potSide = document.createElementNS(svg.namespaceURI, "path");
    potSide.setAttribute(
      "d",
      `M ${isoX - 20} ${isoY} Q ${isoX} ${isoY + 11} ${isoX + 20} ${isoY} L ${isoX + 15} ${isoY + 28} Q ${isoX} ${isoY + 38} ${isoX - 15} ${isoY + 28} Z`,
    );
    potSide.setAttribute("fill", plant.protected ? "#7b9aca" : "#b2663b");
    potSide.setAttribute("stroke", "#6d432b");
    potSide.setAttribute("stroke-width", "1.5");
    group.append(potSide);

    const potRim = document.createElementNS(svg.namespaceURI, "ellipse");
    potRim.setAttribute("cx", String(isoX));
    potRim.setAttribute("cy", String(isoY));
    potRim.setAttribute("rx", "22");
    potRim.setAttribute("ry", "9");
    potRim.setAttribute("fill", "#6b4b2f");
    potRim.setAttribute("stroke", "#4c3522");
    potRim.setAttribute("data-plant-id", String(plant.plant_id));
    group.append(potRim);

    const stem = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "line",
    ) as SVGLineElement;
    stem.setAttribute("x1", String(isoX));
    stem.setAttribute("y1", String(isoY - 4));
    stem.setAttribute("x2", String(isoX + 8));
    stem.setAttribute("y2", String(isoY - height));
    stem.setAttribute("stroke", plant.protected ? "#2f5d9f" : "#5b3a24");
    stem.setAttribute("stroke-width", plant.protected ? "5" : "3");
    stem.dataset.plantId = String(plant.plant_id);
    group.append(stem);

    for (const [dx, dy, scale] of [[-8, 0, 0.78], [11, 2, 0.72], [2, -9, 1]] as const) {
      const leaves = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "ellipse",
      ) as SVGEllipseElement;
      leaves.setAttribute("cx", String(isoX + 8 + dx));
      leaves.setAttribute("cy", String(isoY - height + dy));
      leaves.setAttribute("rx", String(canopy * scale));
      leaves.setAttribute("ry", String(Math.max(7, canopy * 0.44 * scale)));
      leaves.setAttribute("fill", leafColor);
      leaves.setAttribute("stroke", plant.alive ? "#466b31" : "#5f584c");
      leaves.setAttribute("stroke-width", "1");
      leaves.setAttribute("opacity", plant.alive ? "0.94" : "0.65");
      leaves.setAttribute("transform", `rotate(${-18 + dx}, ${isoX + 8 + dx}, ${isoY - height + dy})`);
      leaves.dataset.plantId = String(plant.plant_id);
      group.append(leaves);
    }

    svg.append(group);
  }

  return svg;
}

export function renderNurseryApp(
  target: HTMLElement,
  world: NurseryWorld,
  plants: PlantSummary[],
): void {
  target.replaceChildren();
  const heading = document.createElement("h1");
  heading.textContent = "Arboria Nursery";

  const status = document.createElement("p");
  status.textContent = formatNurseryStatus(world);

  const list = document.createElement("ul");
  for (const plant of plants) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.plantId = String(plant.plant_id);
    button.textContent = formatPlantSummary(plant);
    item.append(button);
    list.append(item);
  }

  target.append(heading, status, renderNurseryScene(plants), list);
}

export function renderLoadError(target: HTMLElement, detail: string): void {
  target.replaceChildren();
  const heading = document.createElement("h1");
  heading.textContent = "Arboria Nursery";
  const status = document.createElement("p");
  status.textContent = `Nursery data is unavailable: ${detail}`;
  target.append(heading, status);
}

export interface NurseryApi {
  world: NurseryWorld;
  plants: PlantSummary[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function toNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function parseNurseryApi(worldJson: unknown, plantsJson: unknown): NurseryApi | null {
  if (!isRecord(worldJson) || !isRecord(plantsJson)) {
    return null;
  }
  const simTick = toNumber(worldJson["sim_tick"]);
  const revision = toNumber(worldJson["world_revision"]);
  const nursery = worldJson["nursery"];
  const plants = plantsJson["plants"];
  if (simTick === null || revision === null || !isRecord(nursery) || !Array.isArray(plants)) {
    return null;
  }
  const numbers: (number | null)[] = [
    toNumber(nursery["plant_count"]),
    toNumber(nursery["organ_count"]),
    toNumber(nursery["reserve_carbon_kg"]),
    toNumber(nursery["structural_carbon_kg"]),
    toNumber(nursery["atmospheric_carbon_uptake_kg"]),
    toNumber(nursery["zone_water_kg"]),
    toNumber(nursery["reservoir_kg"]),
    toNumber(nursery["transpired_kg"]),
    toNumber(nursery["drainage_kg"]),
    toNumber(nursery["zone_nitrogen_kg"]),
    toNumber(nursery["zone_phosphorus_kg"]),
    toNumber(nursery["zone_potassium_kg"]),
    toNumber(nursery["dead_plant_count"]),
  ];
  if (numbers.some((value) => value === null)) {
    return null;
  }
  const speciesIds = nursery["species_ids"];
  if (
    !Array.isArray(speciesIds) ||
    speciesIds.some((value) => typeof value !== "string")
  ) {
    return null;
  }
  const cashMinor = toNumber(nursery["cash_minor"]);
  const protectedRaw = nursery["protected_plant_ids"];
  const demandRaw = nursery["demand_remaining"];
  if (cashMinor === null || !Array.isArray(demandRaw) || !Array.isArray(protectedRaw)) {
    return null;
  }
  const protectedIds = protectedRaw.map(toNumber);
  if (protectedIds.some((value) => value === null)) {
    return null;
  }
  const demand: { species_id: string; remaining: number }[] = [];
  for (const entry of demandRaw) {
    if (!isRecord(entry)) {
      return null;
    }
    const remaining = toNumber(entry["remaining"]);
    if (typeof entry["species_id"] !== "string" || remaining === null) {
      return null;
    }
    demand.push({ species_id: entry["species_id"] as string, remaining });
  }
  const parsedPlants: PlantSummary[] = [];
  for (const entry of plants) {
    if (!isRecord(entry)) {
      return null;
    }
    const fields: (number | null)[] = [
      toNumber(entry["plant_id"]),
      toNumber(entry["organ_count"]),
      toNumber(entry["leaf_area_m2"]),
      toNumber(entry["stem_length_m"]),
      toNumber(entry["reserve_carbon_kg"]),
      toNumber(entry["structural_carbon_kg"]),
      toNumber(entry["zone_water_kg"]),
      toNumber(entry["water_stress_factor"]),
      toNumber(entry["damage_fraction"]),
      toNumber(entry["nutrient_stress_factor"]),
      toNumber(entry["zone_nitrogen_kg"]),
      toNumber(entry["zone_phosphorus_kg"]),
      toNumber(entry["zone_potassium_kg"]),
    ];
    if (fields.some((value) => value === null)) {
      return null;
    }
    if (typeof entry["alive"] !== "boolean") {
      return null;
    }
    if (typeof entry["protected"] !== "boolean") {
      return null;
    }
    if (typeof entry["species_id"] !== "string" || typeof entry["site_id"] !== "string") {
      return null;
    }
    parsedPlants.push({
      plant_id: fields[0] as number,
      species_id: entry["species_id"] as string,
      site_id: entry["site_id"] as string,
      protected: entry["protected"] as boolean,
      organ_count: fields[1] as number,
      leaf_area_m2: fields[2] as number,
      stem_length_m: fields[3] as number,
      reserve_carbon_kg: fields[4] as number,
      structural_carbon_kg: fields[5] as number,
      zone_water_kg: fields[6] as number,
      water_stress_factor: fields[7] as number,
      alive: entry["alive"] as boolean,
      damage_fraction: fields[8] as number,
      nutrient_stress_factor: fields[9] as number,
      zone_nitrogen_kg: fields[10] as number,
      zone_phosphorus_kg: fields[11] as number,
      zone_potassium_kg: fields[12] as number,
    });
  }
  return {
    world: {
      sim_tick: simTick,
      world_revision: revision,
      nursery: {
        plant_count: numbers[0] as number,
        organ_count: numbers[1] as number,
        reserve_carbon_kg: numbers[2] as number,
        structural_carbon_kg: numbers[3] as number,
        atmospheric_carbon_uptake_kg: numbers[4] as number,
        zone_water_kg: numbers[5] as number,
        reservoir_kg: numbers[6] as number,
        transpired_kg: numbers[7] as number,
        drainage_kg: numbers[8] as number,
        zone_nitrogen_kg: numbers[9] as number,
        zone_phosphorus_kg: numbers[10] as number,
        zone_potassium_kg: numbers[11] as number,
        dead_plant_count: numbers[12] as number,
        species_ids: speciesIds as string[],
        cash_minor: cashMinor,
        demand_remaining: demand,
        protected_plant_ids: protectedIds as number[],
      },
    },
    plants: parsedPlants,
  };
}

export async function loadNurseryApp(
  target: HTMLElement,
  fetcher: typeof fetch = fetch,
): Promise<void> {
  const loading = document.createElement("p");
  loading.textContent = "Loading nursery...";
  target.replaceChildren(loading);
  let worldResponse: Response;
  let plantsResponse: Response;
  try {
    [worldResponse, plantsResponse] = await Promise.all([
      fetcher("/api/v1/world", { credentials: "same-origin" }),
      fetcher("/api/v1/plants", { credentials: "same-origin" }),
    ]);
  } catch {
    renderLoadError(target, "network request failed");
    return;
  }
  if (!worldResponse.ok || !plantsResponse.ok) {
    renderLoadError(target, `world ${worldResponse.status}, plants ${plantsResponse.status}`);
    return;
  }
  const parsed = parseNurseryApi(
    await worldResponse.json(),
    await plantsResponse.json(),
  );
  if (parsed === null) {
    renderLoadError(target, "unexpected response shape");
    return;
  }
  renderNurseryApp(target, parsed.world, parsed.plants);
}

export interface CommandReceipt {
  status: string;
  reason: string | null;
}

export interface PlantOrgan {
  organ_id: number;
  kind: string;
  alive: boolean;
  damage_fraction: number;
}

export interface PlantDetail {
  plant_id: number;
  species_id: string;
  site_id: string;
  protected: boolean;
  alive: boolean;
  organs: PlantOrgan[];
}

export interface SaveSnapshot {
  name: string;
}

export interface ExportPayload {
  format: string;
  checkpoint_id: string;
  archive_base64: string;
}

export interface CompanionStatus {
  enabled: boolean;
  water_threshold: number;
  max_actions_per_tick: number;
  actions_proposed: number;
  actions_applied: number;
  actions_rejected: number;
  last_reason: string | null;
  last_plant_id: number | null;
}

export interface NurseryClient {
  load(): Promise<NurseryApi>;
  inspect(plantId: number): Promise<PlantDetail>;
  sendCommand(kind: string, payload: Record<string, unknown>): Promise<CommandReceipt>;
  pauseClock(): Promise<void>;
  resumeClock(): Promise<void>;
  setSpeed(speed: number): Promise<void>;
  checkpoint(): Promise<void>;
  namedSave(name: string): Promise<void>;
  listSaves(): Promise<SaveSnapshot[]>;
  restore(name: string): Promise<void>;
  exportSave(): Promise<ExportPayload>;
  importSave(archiveBase64: string): Promise<void>;
  companionStatus(): Promise<CompanionStatus>;
  setCompanion(policy: CompanionStatus): Promise<CompanionStatus>;
  runCompanion(): Promise<CompanionStatus>;
}

export function readCsrfToken(cookieString: string): string | null {
  for (const part of cookieString.split(";")) {
    const trimmed = part.trim();
    if (trimmed.startsWith("arboria_csrf=")) {
      const value = trimmed.slice("arboria_csrf=".length).trim();
      return value === "" ? null : value;
    }
  }
  return null;
}

function generateCommandId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `cmd-${Date.now()}-${Math.floor(Math.random() * 1e9)}`;
}

export function createApiClient(
  fetcher: typeof fetch,
  getCsrfToken: () => string | null,
): NurseryClient {
  async function readJson(response: Response): Promise<unknown> {
    try {
      return await response.json();
    } catch {
      throw new Error(`request failed with status ${response.status}`);
    }
  }

  function csrfHeaders(): Record<string, string> {
    const token = getCsrfToken();
    if (token === null) {
      throw new Error("missing CSRF token; reload after login");
    }
    return { "Content-Type": "application/json", "x-arboria-csrf": token };
  }

  async function postJson(
    path: string,
    body: unknown,
    headers: Record<string, string>,
  ): Promise<unknown> {
    let response: Response;
    try {
      response = await fetcher(path, {
        method: "POST",
        credentials: "same-origin",
        headers,
        body: JSON.stringify(body),
      });
    } catch {
      throw new Error("network request failed");
    }
    const payload = await readJson(response);
    if (!response.ok) {
      const detail =
        isRecord(payload) && typeof payload["detail"] === "string"
          ? (payload["detail"] as string)
          : `request failed with status ${response.status}`;
      throw new Error(detail);
    }
    return payload;
  }

  async function getJson(path: string): Promise<unknown> {
    let response: Response;
    try {
      response = await fetcher(path, { credentials: "same-origin" });
    } catch {
      throw new Error("network request failed");
    }
    const payload = await readJson(response);
    if (!response.ok) {
      throw new Error(`request failed with status ${response.status}`);
    }
    return payload;
  }

  function parseReceipt(payload: unknown): CommandReceipt {
    if (!isRecord(payload) || typeof payload["status"] !== "string") {
      throw new Error("unexpected command response shape");
    }
    const reason = payload["reason"];
    return {
      status: payload["status"] as string,
      reason: typeof reason === "string" ? reason : null,
    };
  }

  function parseDetail(payload: unknown): PlantDetail {
    if (!isRecord(payload)) {
      throw new Error("unexpected plant detail shape");
    }
    const plantId = toNumber(payload["plant_id"]);
    const organs = payload["organs"];
    if (
      plantId === null ||
      typeof payload["species_id"] !== "string" ||
      typeof payload["site_id"] !== "string" ||
      typeof payload["protected"] !== "boolean" ||
      typeof payload["alive"] !== "boolean" ||
      !Array.isArray(organs)
    ) {
      throw new Error("unexpected plant detail shape");
    }
    const parsedOrgans: PlantOrgan[] = [];
    for (const entry of organs) {
      if (!isRecord(entry)) {
        throw new Error("unexpected plant detail shape");
      }
      const organId = toNumber(entry["organ_id"]);
      const damage = toNumber(entry["damage_fraction"]);
      if (
        organId === null ||
        typeof entry["kind"] !== "string" ||
        typeof entry["alive"] !== "boolean" ||
        damage === null
      ) {
        throw new Error("unexpected plant detail shape");
      }
      parsedOrgans.push({
        organ_id: organId,
        kind: entry["kind"] as string,
        alive: entry["alive"] as boolean,
        damage_fraction: damage,
      });
    }
    return {
      plant_id: plantId,
      species_id: payload["species_id"] as string,
      site_id: payload["site_id"] as string,
      protected: payload["protected"] as boolean,
      alive: payload["alive"] as boolean,
      organs: parsedOrgans,
    };
  }

  function parseExport(payload: unknown): ExportPayload {
    if (
      !isRecord(payload) ||
      typeof payload["format"] !== "string" ||
      typeof payload["checkpoint_id"] !== "string" ||
      typeof payload["archive_base64"] !== "string"
    ) {
      throw new Error("unexpected export response shape");
    }
    return {
      format: payload["format"] as string,
      checkpoint_id: payload["checkpoint_id"] as string,
      archive_base64: payload["archive_base64"] as string,
    };
  }

  function parseCompanion(payload: unknown): CompanionStatus {
    if (!isRecord(payload)) {
      throw new Error("unexpected companion response shape");
    }
    const numericKeys = [
      "water_threshold", "max_actions_per_tick", "actions_proposed",
      "actions_applied", "actions_rejected",
    ];
    if (
      typeof payload["enabled"] !== "boolean" ||
      numericKeys.some((key) => toNumber(payload[key]) === null)
    ) {
      throw new Error("unexpected companion response shape");
    }
    const lastPlant = payload["last_plant_id"];
    return {
      enabled: payload["enabled"] as boolean,
      water_threshold: payload["water_threshold"] as number,
      max_actions_per_tick: payload["max_actions_per_tick"] as number,
      actions_proposed: payload["actions_proposed"] as number,
      actions_applied: payload["actions_applied"] as number,
      actions_rejected: payload["actions_rejected"] as number,
      last_reason: typeof payload["last_reason"] === "string" ? payload["last_reason"] as string : null,
      last_plant_id: typeof lastPlant === "number" ? lastPlant : null,
    };
  }

  return {
    async load(): Promise<NurseryApi> {
      const [worldJson, plantsJson] = await Promise.all([
        getJson("/api/v1/world"),
        getJson("/api/v1/plants"),
      ]);
      const parsed = parseNurseryApi(worldJson, plantsJson);
      if (parsed === null) {
        throw new Error("unexpected response shape");
      }
      return parsed;
    },
    async inspect(plantId: number): Promise<PlantDetail> {
      return parseDetail(await getJson(`/api/v1/plants/${plantId}`));
    },
    async sendCommand(kind, payload): Promise<CommandReceipt> {
      const headers = csrfHeaders();
      const world = await getJson("/api/v1/world");
      if (
        !isRecord(world) ||
        typeof world["world_id"] !== "string" ||
        typeof world["timeline_id"] !== "string" ||
        typeof world["request_epoch"] !== "number"
      ) {
        throw new Error("unexpected world snapshot shape");
      }
      return parseReceipt(
        await postJson(
          "/api/v1/commands",
          {
            schema_version: 1,
            command_id: generateCommandId(),
            world_id: world["world_id"] as string,
            timeline_id: world["timeline_id"] as string,
            request_epoch: world["request_epoch"] as number,
            kind,
            payload,
          },
          headers,
        ),
      );
    },
    async pauseClock(): Promise<void> {
      await postJson("/api/v1/clock/pause", {}, csrfHeaders());
    },
    async resumeClock(): Promise<void> {
      await postJson("/api/v1/clock/resume", {}, csrfHeaders());
    },
    async setSpeed(speed: number): Promise<void> {
      await postJson("/api/v1/clock/speed", { speed }, csrfHeaders());
    },
    async checkpoint(): Promise<void> {
      await postJson("/api/v1/saves/checkpoint", {}, csrfHeaders());
    },
    async namedSave(name: string): Promise<void> {
      await postJson("/api/v1/saves/named", { name }, csrfHeaders());
    },
    async listSaves(): Promise<SaveSnapshot[]> {
      const payload = await getJson("/api/v1/saves");
      if (!isRecord(payload) || !Array.isArray(payload["snapshots"])) {
        throw new Error("unexpected saves shape");
      }
      const saves: SaveSnapshot[] = [];
      for (const entry of payload["snapshots"]) {
        if (!isRecord(entry) || typeof entry["name"] !== "string") {
          throw new Error("unexpected saves shape");
        }
        saves.push({ name: entry["name"] as string });
      }
      return saves;
    },
    async restore(name: string): Promise<void> {
      await postJson("/api/v1/saves/restore", { name }, csrfHeaders());
    },
    async exportSave(): Promise<ExportPayload> {
      return parseExport(await postJson("/api/v1/saves/export", {}, csrfHeaders()));
    },
    async importSave(archiveBase64: string): Promise<void> {
      await postJson(
        "/api/v1/saves/import",
        { archive_base64: archiveBase64.trim() },
        csrfHeaders(),
      );
    },
    async companionStatus(): Promise<CompanionStatus> {
      return parseCompanion(await getJson("/api/v1/companion"));
    },
    async setCompanion(policy: CompanionStatus): Promise<CompanionStatus> {
      return parseCompanion(await postJson(
        "/api/v1/companion",
        {
          enabled: policy.enabled,
          water_threshold: policy.water_threshold,
          max_actions_per_tick: policy.max_actions_per_tick,
        },
        csrfHeaders(),
      ));
    },
    async runCompanion(): Promise<CompanionStatus> {
      const payload = await postJson("/api/v1/companion/run", {}, csrfHeaders());
      if (!isRecord(payload)) {
        throw new Error("unexpected companion response shape");
      }
      return parseCompanion(payload["companion"]);
    },
  };
}

export interface ControlCallbacks {
  onInspect(plantId: number): void;
  onWater(plantId: number): void;
  onSell(plantId: number): void;
  onProtect(plantId: number): void;
  onUnprotect(plantId: number): void;
  onBuyWater(): void;
  onBuyPlant(speciesId: string): void;
  onPause(): void;
  onResume(): void;
  onSpeed(speed: number): void;
  onCheckpoint(): void;
  onNamedSave(name: string): void;
  onRestore(name: string): void;
  onExport(): void;
  onImport(archiveBase64: string): void;
  onCompanionToggle(): void;
  onCompanionRun(): void;
  onRefresh(): void;
}

export interface ControlContext {
  plants: PlantSummary[];
  demand: { species_id: string; remaining: number }[];
  saves: SaveSnapshot[];
  detail: PlantDetail | null;
  result: string | null;
  exportArchive: string;
  companion: CompanionStatus;
}

function actionButton(
  label: string,
  action: string,
  handler: (button: HTMLButtonElement) => void,
  extra: Record<string, string> = {},
): HTMLButtonElement {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.dataset.action = action;
  for (const [key, value] of Object.entries(extra)) {
    button.dataset[key] = value;
  }
  button.addEventListener("click", () => handler(button));
  return button;
}

export function renderControlPanel(
  panel: HTMLElement,
  callbacks: ControlCallbacks,
  context: ControlContext,
): void {
  panel.replaceChildren();

  const care = document.createElement("section");
  care.className = "control-section care-section";
  const careHeading = document.createElement("h2");
  careHeading.textContent = "Care";
  care.append(careHeading);
  for (const plant of context.plants) {
    const row = document.createElement("p");
    row.className = "plant-card";
    row.textContent = formatPlantSummary(plant) + " ";
    row.append(
      actionButton("Inspect", "inspect", () => callbacks.onInspect(plant.plant_id), {
        plantId: String(plant.plant_id),
      }),
      document.createTextNode(" "),
      actionButton(
        "Water 0.02 kg",
        "water",
        (button) => {
          button.disabled = true;
          callbacks.onWater(plant.plant_id);
        },
        { plantId: String(plant.plant_id) },
      ),
      document.createTextNode(" "),
      actionButton("Sell", "sell", (button) => {
        button.disabled = true;
        callbacks.onSell(plant.plant_id);
      }, { plantId: String(plant.plant_id) }),
      document.createTextNode(" "),
      actionButton(
        plant.protected ? "Unprotect" : "Protect",
        plant.protected ? "unprotect" : "protect",
        () => {
          if (plant.protected) {
            callbacks.onUnprotect(plant.plant_id);
          } else {
            callbacks.onProtect(plant.plant_id);
          }
        },
        { plantId: String(plant.plant_id) },
      ),
    );
    care.append(row);
  }
  if (context.detail !== null) {
    const detailBox = document.createElement("div");
    const detailHeading = document.createElement("h3");
    detailHeading.textContent =
      `Plant ${context.detail.plant_id} (${context.detail.species_id}, ` +
      `${context.detail.site_id}, ${context.detail.alive ? "alive" : "dead"})`;
    detailBox.append(detailHeading);
    const organs = document.createElement("ul");
    for (const organ of context.detail.organs) {
      const item = document.createElement("li");
      item.textContent =
        `Organ ${organ.organ_id} ${organ.kind}: ` +
        `${organ.alive ? "alive" : "dead"}, ` +
        `damage ${(organ.damage_fraction * 100).toFixed(1)}%`;
      organs.append(item);
    }
    detailBox.append(organs);
    care.append(detailBox);
  }
  panel.append(care);

  const shop = document.createElement("section");
  shop.className = "control-section";
  const shopHeading = document.createElement("h2");
  shopHeading.textContent = "Shop";
  shop.append(shopHeading);
  shop.append(actionButton("Buy 0.5 kg water", "buy-water", () => callbacks.onBuyWater()));
  const speciesSelect = document.createElement("select");
  speciesSelect.dataset.action = "species-select";
  for (const entry of context.demand) {
    const option = document.createElement("option");
    option.value = entry.species_id;
    option.textContent = `${entry.species_id} (demand ${entry.remaining})`;
    speciesSelect.append(option);
  }
  const buyPlant = actionButton("Buy plant", "buy-plant", () =>
    callbacks.onBuyPlant(speciesSelect.value),
  );
  shop.append(document.createTextNode(" "), speciesSelect, document.createTextNode(" "), buyPlant);
  panel.append(shop);

  const clock = document.createElement("section");
  clock.className = "control-section";
  const clockHeading = document.createElement("h2");
  clockHeading.textContent = "Clock";
  clock.append(clockHeading);
  clock.append(
    actionButton("Pause", "pause", () => callbacks.onPause()),
    document.createTextNode(" "),
    actionButton("Resume", "resume", () => callbacks.onResume()),
  );
  const speedSelect = document.createElement("select");
  speedSelect.dataset.action = "speed-select";
  for (const speed of ["1", "12", "48", "144"]) {
    const option = document.createElement("option");
    option.value = speed;
    option.textContent = `${speed}x`;
    speedSelect.append(option);
  }
  clock.append(
    document.createTextNode(" "),
    speedSelect,
    document.createTextNode(" "),
    actionButton("Set speed", "set-speed", () => callbacks.onSpeed(Number(speedSelect.value))),
  );
  panel.append(clock);

  const saves = document.createElement("section");
  saves.className = "control-section saves-section";
  const savesHeading = document.createElement("h2");
  savesHeading.textContent = "Saves";
  saves.append(savesHeading);
  saves.append(actionButton("Checkpoint now", "checkpoint", () => callbacks.onCheckpoint()));
  const nameInput = document.createElement("input");
  nameInput.type = "text";
  nameInput.placeholder = "Save name";
  nameInput.dataset.action = "save-name";
  saves.append(
    document.createTextNode(" "),
    nameInput,
    document.createTextNode(" "),
    actionButton("Named save", "named-save", () => callbacks.onNamedSave(nameInput.value)),
  );
  const restoreSelect = document.createElement("select");
  restoreSelect.dataset.action = "restore-select";
  for (const save of context.saves) {
    const option = document.createElement("option");
    option.value = save.name;
    option.textContent = save.name;
    restoreSelect.append(option);
  }
  saves.append(
    document.createTextNode(" "),
    restoreSelect,
    document.createTextNode(" "),
    actionButton("Restore", "restore", () => callbacks.onRestore(restoreSelect.value)),
  );
  const exportBox = document.createElement("textarea");
  exportBox.rows = 3;
  exportBox.placeholder = "Export/import archive base64";
  exportBox.dataset.action = "export-archive";
  exportBox.value = context.exportArchive;
  saves.append(
    document.createTextNode(" "),
    actionButton("Export", "export", () => callbacks.onExport()),
    document.createTextNode(" "),
    exportBox,
    document.createTextNode(" "),
    actionButton("Import", "import", () => callbacks.onImport(exportBox.value)),
  );
  panel.append(saves);

  const companion = document.createElement("section");
  companion.className = "control-section companion-section";
  const companionHeading = document.createElement("h2");
  companionHeading.textContent = "Caretaker companion";
  const companionStatus = document.createElement("p");
  companionStatus.textContent = context.companion.enabled
    ? `On · ${context.companion.actions_applied} care actions applied`
    : "Off · baseline caretaker will only water plants below its threshold";
  const companionToggle = actionButton(
    context.companion.enabled ? "Turn off" : "Turn on",
    "companion-toggle",
    () => callbacks.onCompanionToggle(),
  );
  const companionRun = actionButton("Check plants now", "companion-run", () =>
    callbacks.onCompanionRun(),
  );
  companion.append(companionHeading, companionStatus, companionToggle, document.createTextNode(" "), companionRun);
  if (context.companion.last_reason !== null) {
    const reason = document.createElement("p");
    reason.textContent = context.companion.last_reason;
    companion.append(reason);
  }
  panel.append(companion);

  const tools = document.createElement("p");
  tools.append(actionButton("Refresh", "refresh", () => callbacks.onRefresh()));
  const result = document.createElement("p");
  result.dataset.action = "result";
  result.setAttribute("role", "status");
  result.textContent = context.result ?? "";
  tools.append(document.createTextNode(" "), result);
  panel.append(tools);
}

export async function mountNurseryApp(
  target: HTMLElement,
  client: NurseryClient,
): Promise<void> {
  target.replaceChildren();
  const heading = document.createElement("h1");
  heading.textContent = "Arboria Nursery";
  const status = document.createElement("p");
  status.dataset.action = "status";
  status.textContent = "Loading nursery...";
  const scene = document.createElement("div");
  scene.dataset.action = "nursery-scene-slot";
  scene.className = "scene-frame";
  const sceneTitle = document.createElement("h2");
  sceneTitle.textContent = "Living nursery";
  scene.append(sceneTitle);
  const panel = document.createElement("div");
  target.append(heading, status, scene, panel);

  let detail: PlantDetail | null = null;
  let result: string | null = null;
  let exportArchive = "";

  async function refresh(): Promise<void> {
    try {
      const [api, saves, companion] = await Promise.all([
        client.load(),
        client.listSaves(),
        client.companionStatus(),
      ]);
      const lines =
        formatNurseryStatus(api.world);
      status.textContent = lines;
      scene.replaceChildren(sceneTitle, renderNurseryScene(api.plants));
      const callbacks: ControlCallbacks = {
        onInspect: (plantId) => void inspectPlant(plantId),
        onWater: (plantId) => void runCommand("nursery.water", {
          plant_id: plantId,
          water_kg: 0.02,
        }),
        onSell: (plantId) => void runCommand("shop.sell_plant", { plant_id: plantId }),
        onProtect: (plantId) => void runCommand("nursery.protect", { plant_id: plantId }),
        onUnprotect: (plantId) => void runCommand("nursery.unprotect", { plant_id: plantId }),
        onBuyWater: () => void runCommand("shop.buy_water", { water_kg: 0.5 }),
        onBuyPlant: (speciesId) => void runCommand("shop.buy_plant", {
          species_id: speciesId,
        }),
        onPause: () => void runClock("paused", () => client.pauseClock()),
        onResume: () => void runClock("resumed", () => client.resumeClock()),
        onSpeed: (speed) => void runClock(`speed ${speed}x`, () => client.setSpeed(speed)),
        onCheckpoint: () => void runSimple("Checkpoint written.", () => client.checkpoint()),
        onNamedSave: (name) => {
          if (name.trim() === "") {
            result = "Save name is required.";
            void refresh();
            return;
          }
          void runSimple(`Saved "${name.trim()}".`, () => client.namedSave(name.trim()));
        },
        onRestore: (name) => {
          if (name === "") {
            result = "No save selected.";
            void refresh();
            return;
          }
          detail = null;
          void runSimple(`Restored "${name}".`, () => client.restore(name));
        },
        onExport: () => void exportSave(),
        onImport: (archiveBase64) => void importSave(archiveBase64),
        onCompanionToggle: () => void toggleCompanion(companion),
        onCompanionRun: () => void runCompanion(),
        onRefresh: () => {
          result = null;
          void refresh();
        },
      };
      renderControlPanel(panel, callbacks, {
        plants: api.plants,
        demand: api.world.nursery.demand_remaining,
        saves,
        detail,
        result,
        exportArchive,
        companion,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "unknown error";
      renderLoadError(target, message);
    }
  }

  async function inspectPlant(plantId: number): Promise<void> {
    try {
      detail = await client.inspect(plantId);
      result = `Inspecting plant ${plantId}.`;
    } catch (error) {
      result = error instanceof Error ? error.message : "unknown error";
    }
    await refresh();
  }

  function describeReceipt(kind: string, receipt: CommandReceipt): string {
    if (receipt.status === "applied") {
      return `${kind} applied.`;
    }
    return `${kind} ${receipt.status}${receipt.reason ? `: ${receipt.reason}` : "."}`;
  }

  async function runCommand(kind: string, payload: Record<string, unknown>): Promise<void> {
    try {
      result = describeReceipt(kind, await client.sendCommand(kind, payload));
    } catch (error) {
      result = error instanceof Error ? error.message : "unknown error";
    }
    await refresh();
  }

  async function runClock(label: string, action: () => Promise<void>): Promise<void> {
    try {
      await action();
      result = `Clock ${label}.`;
    } catch (error) {
      result = error instanceof Error ? error.message : "unknown error";
    }
    await refresh();
  }

  async function runSimple(label: string, action: () => Promise<void>): Promise<void> {
    try {
      await action();
      result = label;
    } catch (error) {
      result = error instanceof Error ? error.message : "unknown error";
    }
    await refresh();
  }

  async function exportSave(): Promise<void> {
    try {
      const exported = await client.exportSave();
      exportArchive = exported.archive_base64;
      result = `Exported checkpoint ${exported.checkpoint_id}: ${exported.archive_base64}`;
    } catch (error) {
      result = error instanceof Error ? error.message : "unknown error";
    }
    await refresh();
  }

  async function importSave(archiveBase64: string): Promise<void> {
    if (archiveBase64.trim() === "") {
      result = "Import archive is required.";
      await refresh();
      return;
    }
    try {
      await client.importSave(archiveBase64);
      result = "Imported archive.";
      exportArchive = archiveBase64.trim();
      detail = null;
    } catch (error) {
      result = error instanceof Error ? error.message : "unknown error";
    }
    await refresh();
  }

  async function toggleCompanion(current: CompanionStatus): Promise<void> {
    try {
      await client.setCompanion({ ...current, enabled: !current.enabled });
      result = `Companion ${current.enabled ? "off" : "on"}.`;
    } catch (error) {
      result = error instanceof Error ? error.message : "unknown error";
    }
    await refresh();
  }

  async function runCompanion(): Promise<void> {
    try {
      const companion = await client.runCompanion();
      result = companion.last_reason ?? "Companion checked the nursery.";
    } catch (error) {
      result = error instanceof Error ? error.message : "unknown error";
    }
    await refresh();
  }

  await refresh();
}

const app = document.querySelector<HTMLElement>("#app");

if (app !== null) {
  const client = createApiClient(fetch, () => readCsrfToken(document.cookie));
  void mountNurseryApp(app, client);
}
