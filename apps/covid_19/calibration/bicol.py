from autumn.constants import Region
from apps.covid_19.calibration import base


def run_calibration_chain(max_seconds: int, run_id: int, num_chains: int):
    base.run_calibration_chain(
        max_seconds,
        run_id,
        num_chains,
        Region.BICOL,
        PAR_PRIORS,
        TARGET_OUTPUTS,
        mode="autumn_mcmc",
        _multipliers=MULTIPLIERS,
    )


MULTIPLIERS = {
    "prevXlateXclinical_icuXamong": 6133850.0
}  # to get absolute pop size instead of proportion


PAR_PRIORS = [
    {"param_name": "contact_rate", "distribution": "uniform", "distri_params": [0.010, 0.05],},
    {"param_name": "start_time", "distribution": "uniform", "distri_params": [0.0, 40.0],},
    # Add extra params for negative binomial likelihood
    {
        "param_name": "infection_deathsXall_dispersion_param",
        "distribution": "uniform",
        "distri_params": [0.1, 5.0],
    },
    {
        "param_name": "notifications_dispersion_param",
        "distribution": "uniform",
        "distri_params": [0.1, 5.0],
    },
    {
        "param_name": "prevXlateXclinical_icuXamong_dispersion_param",
        "distribution": "uniform",
        "distri_params": [0.1, 5.0],
    },
    {
        "param_name": "compartment_periods_calculated.incubation.total_period",
        "distribution": "gamma",
        "distri_mean": 5.0,
        "distri_ci": [4.4, 5.6],
    },
    {
        "param_name": "compartment_periods_calculated.total_infectious.total_period",
        "distribution": "gamma",
        "distri_mean": 7.0,
        "distri_ci": [4.5, 9.5],
    },
    # parameters to derive age-specific IFRs
    {
        "param_name": "ifr_double_exp_model_params.k",
        "distribution": "uniform",
        "distri_params": [8.0, 16.0],
    },
    {
        "param_name": "ifr_double_exp_model_params.last_representative_age",
        "distribution": "uniform",
        "distri_params": [75.0, 85.0],
    },
]

# death data:
death_times = [
    94,
    110,
    114,
    118,
    136,
]

death_values = [
    1,
    1,
    1,
    1,
    1,
]

# notification data:
notification_times = [
    67,
    72,
    76,
    77,
    79,
    81,
    85,
    86,
    88,
    90,
    93,
    97,
    100,
    103,
    105,
    107,
    108,
    109,
    110,
    111,
    112,
    113,
    115,
    117,
    118,
    119,
    120,
    121,
    122,
    124,
    125,
    126,
    128,
    130,
    133,
    134,
    136,
    141,
    143,
    144,
    145,
    146,
    151,
    153,
    157,
    158,
    159,
    160,
    161,
    163,
    165,
    166,
    167,
    168,
]

notification_values = [
    1,
    1,
    2,
    1,
    1,
    1,
    1,
    2,
    3,
    2,
    1,
    2,
    2,
    1,
    2,
    3,
    4,
    1,
    2,
    1,
    2,
    1,
    2,
    1,
    2,
    1,
    9,
    1,
    1,
    1,
    11,
    1,
    1,
    1,
    1,
    1,
    2,
    1,
    1,
    1,
    6,
    2,
    1,
    4,
    3,
    1,
    1,
    1,
    1,
    1,
    4,
    2,
    1,
    3,
]

# ICU data:
icu_times = [
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
    163,
    164,
    165,
    166,
    167,
    168,
    169,
    170,
    171,
    172,
    173,
    174,
    175,
    176,
]

icu_values = [
    17,
    3,
    2,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    2,
    2,
    2,
    1,
    1,
    1,
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
    1,
    1,
    0,
]

TARGET_OUTPUTS = [
    {
        "output_key": "infection_deathsXall",
        "years": death_times,
        "values": death_values,
        "loglikelihood_distri": "negative_binomial",
    },
    {
        "output_key": "notifications",
        "years": notification_times,
        "values": notification_values,
        "loglikelihood_distri": "negative_binomial",
    },
    {
        "output_key": "prevXlateXclinical_icuXamong",
        "years": icu_times,
        "values": icu_values,
        "loglikelihood_distri": "negative_binomial",
    },
]
