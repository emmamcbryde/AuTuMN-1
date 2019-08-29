from autumn_from_summer.tb_model import *
import summer_py.post_processing as post_proc
from summer_py.outputs import Outputs


def build_model_for_calibration(start_time=1800., stratify_by=['age'], time_variant_cdr=False):
    input_database = InputDB()

    integration_times = numpy.linspace(start_time, 2020.0, 50).tolist()

    # set basic parameters, flows and times, then functionally add latency
    case_fatality_rate = 0.4
    untreated_disease_duration = 3.0
    parameters = \
        {"contact_rate": 100.,
         "recovery": case_fatality_rate / untreated_disease_duration,
         "infect_death": (1.0 - case_fatality_rate) / untreated_disease_duration,
         "universal_death_rate": 1.0 / 50.0,
         "case_detection": 0.,
         "dr_amplification": 0.001,  # high value for testing
         "crude_birth_rate": 20.0 / 1e3}
    parameters.update(change_parameter_unit(provide_aggregated_latency_parameters(), 365.251))

    # sequentially add groups of flows
    flows = add_standard_infection_flows([])
    flows = add_standard_latency_flows(flows)
    flows = add_standard_natural_history_flows(flows)

    # compartments
    compartments = ["susceptible", "early_latent", "late_latent", "infectious", "recovered"]

    # define model     #replace_deaths
    if len(stratify_by) > 0:
        _tb_model = StratifiedModel(
            integration_times, compartments, {"infectious": 1e-3}, parameters, flows, birth_approach="replace_deaths",
            starting_population=3000000)
    else:
        _tb_model = EpiModel(
            integration_times, compartments, {"infectious": 1e-3}, parameters, flows, birth_approach="replace_deaths",
            starting_population=3000000)


    # add crude birth rate from un estimates
    _tb_model = get_birth_rate_functions(_tb_model, input_database, 'MNG')

     # add case detection process to basic model
    _tb_model.add_transition_flow(
        {"type": "standard_flows", "parameter": "case_detection", "origin": "infectious", "to": "recovered"})

    if "strain" in stratify_by:
        _tb_model.stratify("strain", ["ds", "mdr"], ["early_latent", "late_latent", "infectious"], verbose=False,
                           requested_proportions={"mdr": 0.})
        _tb_model.add_transition_flow(
            {"type": "standard_flows", "parameter": "dr_amplification",
             "origin": "infectiousXstrain_ds", "to": "infectiousXstrain_mdr",
             "implement": len(_tb_model.all_stratifications)})

    if "location" in stratify_by:
        _tb_model.stratify("location", ["rural", "province", "urban"], [],
                           requested_proportions={"rural": .32, "province": .16}, verbose=False,
                           )

    if "housing" in stratify_by:
        _tb_model.stratify("housing", ["ger", "non-ger"], [], requested_proportions={"ger": .45}, verbose=False,
                           )

    # age stratification
    if "age" in stratify_by:
        age_breakpoints = [5, 15, 60]
        age_infectiousness = get_parameter_dict_from_function(logistic_scaling_function(10.0), age_breakpoints)
        age_params = get_adapted_age_parameters(age_breakpoints)
        age_params.update(split_age_parameter(age_breakpoints, "contact_rate"))

        _tb_model.stratify("age", copy.deepcopy(age_breakpoints), [], {}, adjustment_requests=age_params,
                           infectiousness_adjustments=age_infectiousness, verbose=False)

    if 'bcg' in stratify_by:
         # get bcg coverage function
        _tb_model = get_bcg_functions(_tb_model, input_database, 'MNG')

        # stratify by vaccination status
        bcg_wane = create_sloping_step_function(15.0, 0.3, 30.0, 1.0)
        age_bcg_efficacy_dict = get_parameter_dict_from_function(lambda value: bcg_wane(value), age_breakpoints)
        bcg_efficacy = substratify_parameter("contact_rate", "vaccinated", age_bcg_efficacy_dict, age_breakpoints)
        _tb_model.stratify("bcg", ["vaccinated", "unvaccinated"], ["susceptible"],
                           requested_proportions={"vaccinated": 0.0},
                           entry_proportions={"vaccinated": "bcg_coverage",
                                              "unvaccinated": "bcg_coverage_complement"},
                           adjustment_requests=bcg_efficacy,
                           verbose=False)
    if time_variant_cdr:
        # loading time-variant case detection rate
        input_database = InputDB()
        res = input_database.db_query("gtb_2015", column="c_cdr", is_filter="country", value="Mongolia")

        # add scaling case detection rate
        cdr_adjustment_factor = 1.
        cdr_mongolia = res["c_cdr"].values / 1e2 * cdr_adjustment_factor
        cdr_mongolia = numpy.concatenate(([0.0], cdr_mongolia))
        res = input_database.db_query("gtb_2015", column="year", is_filter="country", value="Mongolia")
        cdr_mongolia_year = res["year"].values
        cdr_mongolia_year = numpy.concatenate(([1950.], cdr_mongolia_year))
        cdr_scaleup = scale_up_function(cdr_mongolia_year, cdr_mongolia, smoothness=0.2, method=5)
        prop_to_rate = convert_competing_proportion_to_rate(1.0 / untreated_disease_duration)
        detect_rate = return_function_of_function(cdr_scaleup, prop_to_rate)

        _tb_model.time_variants["case_detection"] = detect_rate

    # create_flowchart(_tb_model)

    if 'smear' in stratify_by:
        _tb_model.stratify("smear", ["smearpos", "smearneg", "extrapul"], ["infectious"],
                           adjustment_requests={}, verbose=False, requested_proportions={})

    return _tb_model


def new_build_model_for_calibration(stratify_by):
    input_database = InputDB()

    external_params = {'start_time': 1800.,
                       'case_fatality_rate': 0.4,
                       'untreated_disease_duration': 3.0,
                       'treatment_success_prop': 0.8,
                       'dr_amplification_prop_among_nonsuccess': 0.07,
                       'relative_control_recovery_rate_mdr': 0.5,
                       'rr_transmission_ger': 2.
                       }

    integration_times = numpy.linspace(external_params['start_time'], 2020.0, 50).tolist()
    # set basic parameters, flows and times, then functionally add latency

    parameters = \
        {"contact_rate": 10.,
         "recovery": external_params['case_fatality_rate'] / external_params['untreated_disease_duration'],
         "infect_death": (1.0 - external_params['case_fatality_rate']) / external_params['untreated_disease_duration'],
         "universal_death_rate": 1.0 / 50.0,
         "case_detection": 0.,
         "dr_amplification": .0,  # high value for testing
         "crude_birth_rate": 20.0 / 1e3}
    parameters.update(change_parameter_unit(provide_aggregated_latency_parameters(), 365.251))

    # sequentially add groups of flows
    flows = add_standard_infection_flows([])
    flows = add_standard_latency_flows(flows)
    flows = add_standard_natural_history_flows(flows)

    # compartments
    compartments = ["susceptible", "early_latent", "late_latent", "infectious", "recovered"]

    # define model     #replace_deaths
    if len(stratify_by) > 0:
        _tb_model = StratifiedModel(
            integration_times, compartments, {"infectious": 1e-3}, parameters, flows, birth_approach="replace_deaths",
            starting_population=3000000)
    else:
        _tb_model = EpiModel(
            integration_times, compartments, {"infectious": 1e-3}, parameters, flows, birth_approach="replace_deaths",
            starting_population=3000000)

    # provisional patch
    _tb_model.adaptation_functions["universal_death_rateX"] = lambda x: 2.0 / 70.0

    # add crude birth rate from un estimates
    _tb_model = get_birth_rate_functions(_tb_model, input_database, 'MNG')

    # add case detection process to basic model
    _tb_model.add_transition_flow(
        {"type": "standard_flows", "parameter": "case_detection", "origin": "infectious", "to": "recovered"})

    # loading time-variant case detection rate
    input_database = InputDB()
    res = input_database.db_query("gtb_2015", column="c_cdr", is_filter="country", value="Mongolia")

    # add scaling case detection rate
    cdr_adjustment_factor = .5
    cdr_mongolia = res["c_cdr"].values / 1e2 * cdr_adjustment_factor
    cdr_mongolia = numpy.concatenate(([0.0], cdr_mongolia))
    res = input_database.db_query("gtb_2015", column="year", is_filter="country", value="Mongolia")
    cdr_mongolia_year = res["year"].values
    cdr_mongolia_year = numpy.concatenate(([1950.], cdr_mongolia_year))
    cdr_scaleup = scale_up_function(cdr_mongolia_year, cdr_mongolia, smoothness=0.2, method=5)
    prop_to_rate = convert_competing_proportion_to_rate(1.0 / external_params['untreated_disease_duration'])
    detect_rate = return_function_of_function(cdr_scaleup, prop_to_rate)

    tb_control_recovery_rate = lambda x: external_params['treatment_success_prop'] * detect_rate(x)
    if len(stratify_by) == 0:
        _tb_model.time_variants["case_detection"] = tb_control_recovery_rate
    else:
        _tb_model.adaptation_functions["case_detection"] = tb_control_recovery_rate
        _tb_model.parameters["case_detection"] = "case_detection"

    if "strain" in stratify_by:
        _tb_model.stratify("strain", ["ds", "mdr"], ["early_latent", "late_latent", "infectious"], verbose=False,
                           requested_proportions={"mdr": 0.},
                           adjustment_requests={'case_detection':
                                                    {"mdr": external_params['relative_control_recovery_rate_mdr']}})
        _tb_model.add_transition_flow(
            {"type": "standard_flows", "parameter": "dr_amplification",
             "origin": "infectiousXstrain_ds", "to": "infectiousXstrain_mdr",
             "implement": len(_tb_model.all_stratifications)})

        dr_amplification_rate = lambda x: detect_rate(x) * (1. - external_params['treatment_success_prop']) *\
                                          external_params['dr_amplification_prop_among_nonsuccess']

        _tb_model.adaptation_functions["dr_amplification"] = dr_amplification_rate
        _tb_model.parameters["dr_amplification"] = "dr_amplification"

    if 'smear' in stratify_by:
        _tb_model.stratify("smear", ["smearpos", "smearneg", "extrapul"], ["infectious"],
                           infectiousness_adjustments={"smearpos": 1., "smearneg": 0.25, "extrapul": 0.},
                           verbose=False, requested_proportions={"smearpos": 0.5, "smearneg": 0.25})

    # age stratification
    if "age" in stratify_by:
        age_breakpoints = [5, 15, 60]
        age_infectiousness = get_parameter_dict_from_function(logistic_scaling_function(10.0), age_breakpoints)
        age_params = get_adapted_age_parameters(age_breakpoints)
        age_params.update(split_age_parameter(age_breakpoints, "contact_rate"))

        pop_morts = get_pop_mortality_functions(input_database, age_breakpoints, country_iso_code='MNG')
        age_params["universal_death_rate"] = {}
        for age_break in age_breakpoints:
            _tb_model.time_variants["universal_death_rateXage_" + str(age_break)] = pop_morts[age_break]
            _tb_model.parameters["universal_death_rateXage_" + str(age_break)] = "universal_death_rateXage_" + str(age_break)

            age_params["universal_death_rate"][str(age_break) + 'W'] = "universal_death_rateXage_" + str(age_break)
            _tb_model.parameters["universal_death_rateX"] = 0.

        _tb_model.stratify("age", copy.deepcopy(age_breakpoints), [], {}, adjustment_requests=age_params,
                           infectiousness_adjustments=age_infectiousness, verbose=False)

    # if 'bcg' in stratify_by:
    #      # get bcg coverage function
    #     _tb_model = get_bcg_functions(_tb_model, input_database, 'MNG')
    #
    #     # stratify by vaccination status
    #     bcg_wane = create_sloping_step_function(15.0, 0.3, 30.0, 1.0)
    #     age_bcg_efficacy_dict = get_parameter_dict_from_function(lambda value: bcg_wane(value), age_breakpoints)
    #     bcg_efficacy = substratify_parameter("contact_rate", "vaccinated", age_bcg_efficacy_dict, age_breakpoints)
    #     _tb_model.stratify("bcg", ["vaccinated", "unvaccinated"], ["susceptible"],
    #                        requested_proportions={"vaccinated": 0.0},
    #                        entry_proportions={"vaccinated": "bcg_coverage",
    #                                           "unvaccinated": "bcg_coverage_complement"},
    #                        adjustment_requests=bcg_efficacy,
    #                        verbose=False)

    if "housing" in stratify_by:
        _tb_model.stratify("housing", ["ger", "non-ger"], [], requested_proportions={"ger": .45}, verbose=False,
                           adjustment_requests={'contact_rate': {"ger": 2.}}
                           )


    _tb_model.transition_flows.to_csv("transitions.csv")
    # _tb_model.death_flows.to_csv("deaths.csv")

    return _tb_model


if __name__ == "__main__":
    stratify_by = ['age', 'housing']
    mongolia_model = new_build_model_for_calibration(stratify_by=stratify_by)
    mongolia_model.run_model()

    req_outputs = ['distribution_of_strataXage', 'distribution_of_strataXlocation', 'distribution_of_strataXhousing',
                   'distribution_of_strataXstrain', 'distribution_of_strataXbcg', 'distribution_of_strataXsmear',
                   'prevXinfectiousXamong',
                   'prevXlatentXamong',
                   'prevXlatentXamongXage_5',
                   'prevXinfectiousXamongXhousing_ger',
                   'prevXinfectiousXamongXhousing_non-ger']

    req_multipliers = {'prevXinfectiousXamong': 1.e5,
                       'prevXinfectiousXamongXhousing_ger': 1.e5,
                       'prevXinfectiousXamongXhousing_non-ger': 1.e5}

    pp = post_proc.PostProcessing(mongolia_model, req_outputs, multipliers=req_multipliers)

    # generate outputs
    outputs = Outputs(pp)
    outputs.plot_requested_outputs()