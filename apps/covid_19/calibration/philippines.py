from apps.covid_19.calibration.base import run_calibration_chain, get_priors_and_targets

country = "philippines"
PAR_PRIORS, TARGET_OUTPUTS = get_priors_and_targets(country, "deaths", 2)

# Get rid of time in the params to calibrate
del PAR_PRIORS[1]

# target_to_plots = {
#     "infection_deathsXall": {
#         "times": TARGET_OUTPUTS[0]["years"],
#         "values": [[d] for d in TARGET_OUTPUTS[0]["values"]],
#     }
# }
# print(target_to_plots)


def run_phl_calibration_chain(max_seconds: int, run_id: int):
    run_calibration_chain(max_seconds, run_id, country, PAR_PRIORS, TARGET_OUTPUTS)
