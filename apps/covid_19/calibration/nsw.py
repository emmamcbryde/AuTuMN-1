from autumn.constants import Region
from apps.covid_19.calibration import base


def run_calibration_chain(max_seconds: int, run_id: int, num_chains: int):
    base.run_calibration_chain(
        max_seconds, run_id, num_chains, Region.NSW, PAR_PRIORS, TARGET_OUTPUTS, mode="autumn_mcmc",
    )


# _______ Define the priors
PAR_PRIORS = [
    # Extra parameter for the negative binomial likelihood
    {
        "param_name": "notifications_dispersion_param",
        "distribution": "uniform",
        "distri_params": [0.1, 5.0],
    },
    # Transmission parameter
    {"param_name": "contact_rate", "distribution": "uniform", "distri_params": [0.025, 0.08],},
    # Parameters defining the natural history of COVID-19
    {
        "param_name": "non_sympt_infect_multiplier",
        "distribution": "beta",
        "distri_mean": 0.5,
        "distri_ci": [0.4, 0.6],
    },
    {
        "param_name": "compartment_periods_calculated.incubation.total_period",
        "distribution": "gamma",
        "distri_mean": 5.0,
        "distri_ci": [3.0, 7.0],
    },
    # Programmatic parameters
    {
        "param_name": "prop_detected_among_symptomatic",
        "distribution": "beta",
        "distri_mean": 0.85,
        "distri_ci": [0.8, 0.9],
    },
    # Parameter to vary the mixing adjustment in other_locations
    {
        "param_name": "npi_effectiveness.other_locations",
        "distribution": "beta",
        "distri_mean": 0.9,
        "distri_ci": [0.8, 0.99],
    },
    # Parameters related to case importation
    {
        "param_name": "data.n_imported_cases(-1)",
        "distribution": "gamma",
        "distri_mean": 1.0,
        "distri_ci": [0.1, 2.0],
    },
    {
        "param_name": "self_isolation_effect",
        "distribution": "beta",
        "distri_mean": 0.67,
        "distri_ci": [0.55, 0.80],
        "distri_ci_width": 0.95,
    },
    {
        "param_name": "enforced_isolation_effect",
        "distribution": "beta",
        "distri_mean": 0.90,
        "distri_ci": [0.80, 0.99],
    },
]

# _______ Define the calibration targets
# Local transmission data: look at malaysia for tv_detection, also adjust c, the inflection time point
data_times = [
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
    80,
    81,
    82,
    83,
    84,
    85,
    86,
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    98,
    99,
    100,
    101,
    102,
    103,
    104,
    105,
    106,
    107,
    108,
    109,
    110,
    111,
    112,
    113,
    114,
    115,
    116,
    117,
    118,
    119,
    120,
    121,
    122,
    123,
    124,
    125,
    126,
    127,
    128,
    129,
    130,
    131,
    132,
    133,
    134,
    135,
    136,
    137,
    138,
    139,
    140,
    141,
    142,
    143,
    144,
    145,
    146,
    147,
    148,
    149,
    150,
    151,
    152,
    153,
    154,
    155,
    156,
    157,
    158,
    159,
    160,
    161,
    162,
]
# case counts are all cases
case_counts = [
    0,
    1,
    2,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    1,
    0,
    0,
    1,
    0,
    1,
    0,
    3,
    3,
    0,
    4,
    0,
    0,
    2,
    0,
    3,
    0,
    8,
    6,
    1,
    2,
    0,
    4,
    2,
    1,
    0,
    7,
    3,
    2,
    2,
    4,
    12,
    4,
    14,
    6,
    11,
    21,
    12,
    14,
    22,
    50,
    52,
    35,
    33,
    52,
    53,
    37,
    95,
    113,
    103,
    112,
    107,
    113,
    87,
    133,
    141,
    112,
    88,
    82,
    101,
    109,
    74,
    31,
    45,
    42,
    28,
    31,
    39,
    34,
    19,
    16,
    26,
    9,
    24,
    11,
    20,
    17,
    13,
    36,
    28,
    12,
    4,
    13,
    7,
    16,
    10,
    6,
    8,
    3,
    3,
    0,
    10,
    7,
    7,
    7,
    3,
    9,
    8,
    1,
    0,
    3,
    3,
    1,
    5,
    2,
    4,
    0,
    0,
    0,
    0,
    0,
    2,
    1,
    1,
    2,
    4,
    0,
    1,
    0,
    0,
    0,
    0,
    0,
    2,
    0,
    0,
    0,
    1,
    5,
    0,
    1,
    0,
    1,
    1,
]

# _______ Print targets to plot to be added to plots.yml file
# target_to_plots = {"notifications": {"times": data_times, "values": [[d] for d in case_counts]}}
# print(target_to_plots)

TARGET_OUTPUTS = [
    {
        "output_key": "notifications",
        "years": data_times,
        "values": case_counts,
        "loglikelihood_distri": "negative_binomial",
    }
]

if __name__ == "__main__":
    run_calibration_chain(
        30 * 60, 1
    )  # first argument only relevant for autumn_mcmc mode (time limit in seconds)

