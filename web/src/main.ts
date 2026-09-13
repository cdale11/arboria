export interface PlantSummary {
  plant_id: number;
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
    ? `damage ${(plant.damage_fraction * 100).toFixed(1)}%`
    : "dead";
  return (
    `Plant ${plant.plant_id}: ${plant.organ_count} organs, ` +
    `stem ${plant.stem_length_m.toFixed(3)} m, ` +
    `leaf ${plant.leaf_area_m2.toFixed(3)} m2, ` +
    `reserve C ${plant.reserve_carbon_kg.toExponential(2)} kg, ` +
    `zone water ${plant.zone_water_kg.toFixed(3)} kg, ` +
    `zone N ${plant.zone_nitrogen_kg.toExponential(2)} kg, ` +
    health
  );
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
  status.textContent =
    `Tick ${world.sim_tick}, revision ${world.world_revision}, ` +
    `${world.nursery.plant_count} plants, ${world.nursery.organ_count} organs, ` +
    `${world.nursery.dead_plant_count} dead. ` +
    `Reserve carbon ${world.nursery.reserve_carbon_kg.toExponential(2)} kg, ` +
    `zone water ${world.nursery.zone_water_kg.toFixed(3)} kg, ` +
    `zone N/P/K ${world.nursery.zone_nitrogen_kg.toExponential(2)}/` +
    `${world.nursery.zone_phosphorus_kg.toExponential(2)}/` +
    `${world.nursery.zone_potassium_kg.toExponential(2)} kg, ` +
    `reservoir ${world.nursery.reservoir_kg.toFixed(3)} kg. ` +
    `Fertilizer input, economy, and companion management are not implemented yet.`;

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

  target.append(heading, status, list);
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
    parsedPlants.push({
      plant_id: fields[0] as number,
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

const app = document.querySelector<HTMLElement>("#app");

if (app !== null) {
  void loadNurseryApp(app);
}
