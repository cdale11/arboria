"""Tests for the R1 species catalog and per-species reference scenarios."""

from __future__ import annotations

import pytest

from arboria.biology.organs import total_resource_pools
from arboria.biology.species import (
    SITES,
    SPECIES,
    get_site,
    get_species,
    validate_species,
)
from arboria.sim.nursery import (
    STARTER_RESERVOIR_KG,
    advance_nursery,
    starter_nutrient_zones_for,
    starter_plant_organs,
    starter_zones_for,
    water_plant,
)

EXPECTED_SPECIES = (
    "ocimum_basilicum",
    "solanum_lycopersicum",
    "ficus_benjamina",
    "crassula_ovata",
    "juniperus_procumbens",
    "quercus_robur",
)


def test_catalog_holds_six_validated_species() -> None:
    assert tuple(sorted(SPECIES)) == tuple(sorted(EXPECTED_SPECIES))
    for record in SPECIES.values():
        validate_species(record)


def test_species_carry_provisional_provenance_and_coverage() -> None:
    for record in SPECIES.values():
        assert "provisional" in record.provenance
        assert record.calibration_status == "provisional"
        assert record.supported_processes
        assert record.unsupported_processes
        assert record.reference_scenario
        assert record.site_id in SITES


def test_species_cover_greenhouse_and_outdoor_sites() -> None:
    sites = {record.site_id for record in SPECIES.values()}
    assert sites == {"greenhouse", "outdoor"}
    assert get_site("greenhouse").par_w_m2 > 0.0
    assert get_site("outdoor").par_w_m2 > get_site("greenhouse").par_w_m2


def test_unknown_species_and_sites_are_rejected() -> None:
    with pytest.raises(ValueError, match="unknown species"):
        get_species("arabidopsis_thaliana")
    with pytest.raises(ValueError, match="unknown site"):
        get_site("growth_chamber")


@pytest.mark.parametrize("species_id", EXPECTED_SPECIES)
def test_reference_scenario_survives_with_care(species_id: str) -> None:
    plant_id = 7
    organs = starter_plant_organs(plant_id, species_id, 1)
    zones = starter_zones_for(organs)
    nutrients = starter_nutrient_zones_for(organs)
    mapping = {plant_id: species_id}
    start_structural = total_resource_pools(organs).structural_carbon_kg
    start_reserve = total_resource_pools(organs).reserve_carbon_kg
    reservoir = STARTER_RESERVOIR_KG
    for _ in range(8):
        result = advance_nursery(organs, zones, nutrients, 25, mapping)
        organs, zones, nutrients = result.organs, result.zones, result.nutrient_zones
        zones, reservoir, _ = water_plant(zones, reservoir, plant_id, 0.05)

    roots = [organ for organ in organs if organ.parent_id is None]
    assert len(roots) == 1
    assert roots[0].alive
    totals = total_resource_pools(organs)
    assert totals.structural_carbon_kg >= start_structural
    assert totals.reserve_carbon_kg > start_reserve
    assert nutrients[plant_id].nitrogen_kg < 0.020
    assert reservoir < STARTER_RESERVOIR_KG
