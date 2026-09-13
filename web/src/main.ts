export interface PlantSummary {
  plant_id: number;
  organ_count: number;
  leaf_area_m2: number;
  stem_length_m: number;
  reserve_carbon_kg: number;
  structural_carbon_kg: number;
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
  return (
    `Plant ${plant.plant_id}: ${plant.organ_count} organs, ` +
    `stem ${plant.stem_length_m.toFixed(3)} m, ` +
    `leaf ${plant.leaf_area_m2.toFixed(3)} m2, ` +
    `reserve C ${plant.reserve_carbon_kg.toExponential(2)} kg`
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
    `${world.nursery.plant_count} plants, ${world.nursery.organ_count} organs. ` +
    `Reserve carbon ${world.nursery.reserve_carbon_kg.toExponential(2)} kg. ` +
    `Water, nutrients, economy, and companion management are not implemented yet.`;

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

const app = document.querySelector<HTMLElement>("#app");

if (app !== null) {
  renderDependencyBaseline(app);
}
