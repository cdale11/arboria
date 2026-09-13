"""R1 species catalog: six representative species with provisional parameters.

Every record carries explicit provenance and calibration status. No numerical
value here is a measured species constant: all biological coefficients are
provisional placeholders chosen for stable R1 starter dynamics, per the
repository rule that uninspected sources must never back a parameter. Each
record lists supported, approximated, and unsupported processes so coverage
claims stay honest.
"""

from __future__ import annotations

from dataclasses import dataclass

from arboria.biology.nutrients import NutrientParameters

SPECIES_SCHEMA_VERSION = 1
PROVISIONAL_PROVENANCE = (
    "provisional-calibration: no inspected source backs these values; "
    "magnitudes are chosen for stable R1 starter dynamics, not measurement"
)


@dataclass(frozen=True)
class SiteRecord:
    site_id: str
    par_w_m2: float
    description: str


@dataclass(frozen=True)
class SpeciesRecord:
    species_id: str
    schema_version: int
    scientific_name: str
    common_names: tuple[str, ...]
    functional_group: str
    photosynthetic_pathway: str
    site_id: str
    provenance: str
    calibration_status: str
    amax_kg_c_m2_s: float
    half_saturation_w_m2: float
    temperature_factor: float
    conductance_kg_s: float
    transpiration_kg_s_m2: float
    growth_reserve_fraction: float
    growth_length_m_per_tick: float
    growth_water_fraction: float
    growth_nutrient_fraction: float
    nutrients: NutrientParameters
    reference_scenario: str
    supported_processes: tuple[str, ...]
    approximated_processes: tuple[str, ...]
    unsupported_processes: tuple[str, ...]


SITES: dict[str, SiteRecord] = {
    "greenhouse": SiteRecord(
        site_id="greenhouse",
        par_w_m2=250.0,
        description="Sheltered R1 greenhouse bench with moderate steady light.",
    ),
    "outdoor": SiteRecord(
        site_id="outdoor",
        par_w_m2=400.0,
        description="Open R1 outdoor bed with stronger steady light.",
    ),
}

_R1_SUPPORTED = (
    "organ topology",
    "resource-bounded vegetative growth",
    "saturating light-driven carbon assimilation",
    "root-zone water uptake and transpiration",
    "substrate N/P/K uptake",
    "deficiency stress",
    "irreversible stress damage and death",
)

_R1_UNSUPPORTED = (
    "sexual reproduction",
    "thermal-time development",
    "photoperiod and dormancy",
    "species morphology grammar",
    "layered substrate chemistry",
    "fertilizer input",
    "damage recovery",
    "pest and pathogen interaction",
)


def _nutrients(
    reference_n: float,
    reference_p: float,
    reference_k: float,
    uptake_rate_per_s: float,
    damage_rate_per_s: float,
) -> NutrientParameters:
    return NutrientParameters(
        uptake_rate_per_s=uptake_rate_per_s,
        reference_nitrogen_kg=reference_n,
        reference_phosphorus_kg=reference_p,
        reference_potassium_kg=reference_k,
        capacity_nitrogen_kg=2.0 * reference_n,
        capacity_phosphorus_kg=2.0 * reference_p,
        capacity_potassium_kg=2.0 * reference_k,
        damage_stress_threshold=0.5,
        damage_rate_per_s=damage_rate_per_s,
    )


SPECIES: dict[str, SpeciesRecord] = {
    "ocimum_basilicum": SpeciesRecord(
        species_id="ocimum_basilicum",
        schema_version=SPECIES_SCHEMA_VERSION,
        scientific_name="Ocimum basilicum",
        common_names=("sweet basil",),
        functional_group="herb",
        photosynthetic_pathway="C3",
        site_id="greenhouse",
        provenance=PROVISIONAL_PROVENANCE,
        calibration_status="provisional",
        amax_kg_c_m2_s=1.2e-6,
        half_saturation_w_m2=120.0,
        temperature_factor=1.0,
        conductance_kg_s=2.2e-7,
        transpiration_kg_s_m2=4.5e-7,
        growth_reserve_fraction=0.0008,
        growth_length_m_per_tick=0.0008,
        growth_water_fraction=0.01,
        growth_nutrient_fraction=0.005,
        nutrients=_nutrients(0.0012, 0.00024, 0.00048, 1.2e-4, 1.0e-6),
        reference_scenario=(
            "Single-plant starter survives 200 ticks with watering every 25 "
            "ticks, stays alive, and does not lose structural carbon."
        ),
        supported_processes=_R1_SUPPORTED,
        approximated_processes=(
            "saturating C3 assimilation response",
            "well-mixed root zone",
        ),
        unsupported_processes=_R1_UNSUPPORTED,
    ),
    "solanum_lycopersicum": SpeciesRecord(
        species_id="solanum_lycopersicum",
        schema_version=SPECIES_SCHEMA_VERSION,
        scientific_name="Solanum lycopersicum",
        common_names=("tomato",),
        functional_group="vegetable",
        photosynthetic_pathway="C3",
        site_id="greenhouse",
        provenance=PROVISIONAL_PROVENANCE,
        calibration_status="provisional",
        amax_kg_c_m2_s=1.1e-6,
        half_saturation_w_m2=130.0,
        temperature_factor=1.0,
        conductance_kg_s=2.0e-7,
        transpiration_kg_s_m2=4.2e-7,
        growth_reserve_fraction=0.0007,
        growth_length_m_per_tick=0.0007,
        growth_water_fraction=0.01,
        growth_nutrient_fraction=0.006,
        nutrients=_nutrients(0.0015, 0.00030, 0.00060, 1.4e-4, 1.2e-6),
        reference_scenario=(
            "Single-plant starter survives 200 ticks with watering every 25 "
            "ticks, stays alive, and does not lose structural carbon."
        ),
        supported_processes=_R1_SUPPORTED,
        approximated_processes=(
            "saturating C3 assimilation response",
            "well-mixed root zone",
        ),
        unsupported_processes=_R1_UNSUPPORTED
        + ("fruit and seed development",),
    ),
    "ficus_benjamina": SpeciesRecord(
        species_id="ficus_benjamina",
        schema_version=SPECIES_SCHEMA_VERSION,
        scientific_name="Ficus benjamina",
        common_names=("weeping fig",),
        functional_group="houseplant tree",
        photosynthetic_pathway="C3",
        site_id="greenhouse",
        provenance=PROVISIONAL_PROVENANCE,
        calibration_status="provisional",
        amax_kg_c_m2_s=0.9e-6,
        half_saturation_w_m2=110.0,
        temperature_factor=1.0,
        conductance_kg_s=1.8e-7,
        transpiration_kg_s_m2=3.8e-7,
        growth_reserve_fraction=0.0004,
        growth_length_m_per_tick=0.0004,
        growth_water_fraction=0.01,
        growth_nutrient_fraction=0.005,
        nutrients=_nutrients(0.0010, 0.00020, 0.00040, 1.0e-4, 1.0e-6),
        reference_scenario=(
            "Single-plant starter survives 200 ticks with watering every 25 "
            "ticks, stays alive, and does not lose structural carbon."
        ),
        supported_processes=_R1_SUPPORTED,
        approximated_processes=(
            "saturating C3 assimilation response",
            "well-mixed root zone",
        ),
        unsupported_processes=_R1_UNSUPPORTED,
    ),
    "crassula_ovata": SpeciesRecord(
        species_id="crassula_ovata",
        schema_version=SPECIES_SCHEMA_VERSION,
        scientific_name="Crassula ovata",
        common_names=("jade plant",),
        functional_group="succulent",
        photosynthetic_pathway="C3-modelled CAM plant",
        site_id="greenhouse",
        provenance=PROVISIONAL_PROVENANCE,
        calibration_status="provisional",
        amax_kg_c_m2_s=0.5e-6,
        half_saturation_w_m2=100.0,
        temperature_factor=1.0,
        conductance_kg_s=1.0e-7,
        transpiration_kg_s_m2=1.0e-7,
        growth_reserve_fraction=0.0003,
        growth_length_m_per_tick=0.0002,
        growth_water_fraction=0.008,
        growth_nutrient_fraction=0.004,
        nutrients=_nutrients(0.0006, 0.00012, 0.00024, 0.6e-4, 0.6e-6),
        reference_scenario=(
            "Single-plant starter survives 200 ticks with watering every 25 "
            "ticks, stays alive, and does not lose structural carbon."
        ),
        supported_processes=_R1_SUPPORTED,
        approximated_processes=(
            "CAM physiology approximated with the C3 saturating response",
            "well-mixed root zone",
        ),
        unsupported_processes=_R1_UNSUPPORTED
        + (
            "CAM day/night acid storage",
            "succulent water-storage tissue",
        ),
    ),
    "juniperus_procumbens": SpeciesRecord(
        species_id="juniperus_procumbens",
        schema_version=SPECIES_SCHEMA_VERSION,
        scientific_name="Juniperus procumbens",
        common_names=("Japanese garden juniper",),
        functional_group="bonsai-suitable conifer",
        photosynthetic_pathway="C3",
        site_id="outdoor",
        provenance=PROVISIONAL_PROVENANCE,
        calibration_status="provisional",
        amax_kg_c_m2_s=0.7e-6,
        half_saturation_w_m2=140.0,
        temperature_factor=0.9,
        conductance_kg_s=1.5e-7,
        transpiration_kg_s_m2=3.0e-7,
        growth_reserve_fraction=0.0003,
        growth_length_m_per_tick=0.0003,
        growth_water_fraction=0.01,
        growth_nutrient_fraction=0.004,
        nutrients=_nutrients(0.0008, 0.00016, 0.00032, 0.8e-4, 0.9e-6),
        reference_scenario=(
            "Single-plant starter survives 200 ticks with watering every 25 "
            "ticks, stays alive, and does not lose structural carbon."
        ),
        supported_processes=_R1_SUPPORTED,
        approximated_processes=(
            "saturating C3 assimilation response",
            "well-mixed root zone",
            "conifer foliage as a leaf cohort",
        ),
        unsupported_processes=_R1_UNSUPPORTED + ("wiring and pruning response",),
    ),
    "quercus_robur": SpeciesRecord(
        species_id="quercus_robur",
        schema_version=SPECIES_SCHEMA_VERSION,
        scientific_name="Quercus robur",
        common_names=("English oak",),
        functional_group="outdoor tree",
        photosynthetic_pathway="C3",
        site_id="outdoor",
        provenance=PROVISIONAL_PROVENANCE,
        calibration_status="provisional",
        amax_kg_c_m2_s=0.8e-6,
        half_saturation_w_m2=150.0,
        temperature_factor=0.9,
        conductance_kg_s=1.8e-7,
        transpiration_kg_s_m2=3.5e-7,
        growth_reserve_fraction=0.0003,
        growth_length_m_per_tick=0.0003,
        growth_water_fraction=0.01,
        growth_nutrient_fraction=0.005,
        nutrients=_nutrients(0.0008, 0.00016, 0.00032, 0.8e-4, 1.0e-6),
        reference_scenario=(
            "Single-plant starter survives 200 ticks with watering every 25 "
            "ticks, stays alive, and does not lose structural carbon."
        ),
        supported_processes=_R1_SUPPORTED,
        approximated_processes=(
            "saturating C3 assimilation response",
            "well-mixed root zone",
        ),
        unsupported_processes=_R1_UNSUPPORTED
        + (
            "masting and acorn production",
            "mycorrhizal association",
        ),
    ),
}


def get_species(species_id: str) -> SpeciesRecord:
    try:
        return SPECIES[species_id]
    except KeyError as exc:
        raise ValueError(f"unknown species: {species_id}") from exc


def get_site(site_id: str) -> SiteRecord:
    try:
        return SITES[site_id]
    except KeyError as exc:
        raise ValueError(f"unknown site: {site_id}") from exc


def validate_species(record: SpeciesRecord) -> None:
    if not record.species_id or not record.scientific_name:
        raise ValueError("species must have an ID and scientific name")
    if not record.common_names:
        raise ValueError("species must list at least one common name")
    if record.schema_version != SPECIES_SCHEMA_VERSION:
        raise ValueError("species schema version mismatch")
    if record.site_id not in SITES:
        raise ValueError(f"species site must be a known site: {record.site_id}")
    if not record.provenance or not record.calibration_status:
        raise ValueError("species must carry provenance and calibration status")
    for name in (
        "amax_kg_c_m2_s",
        "half_saturation_w_m2",
        "temperature_factor",
        "conductance_kg_s",
        "transpiration_kg_s_m2",
        "growth_reserve_fraction",
        "growth_length_m_per_tick",
        "growth_water_fraction",
        "growth_nutrient_fraction",
    ):
        value = getattr(record, name)
        if not isinstance(value, float | int) or not _is_positive_finite(value):
            raise ValueError(f"{name} must be a positive finite number")
    from arboria.biology.nutrients import validate_nutrient_parameters

    validate_nutrient_parameters(record.nutrients)
    if not record.reference_scenario:
        raise ValueError("species must document a reference scenario")
    if not record.supported_processes:
        raise ValueError("species must list supported processes")


def _is_positive_finite(value: float | int) -> bool:
    import math

    return math.isfinite(float(value)) and float(value) > 0.0


for _record in SPECIES.values():
    validate_species(_record)
