import autumn.model_runner
import autumn.outputs as outputs
from copy import copy

''' some preliminary work '''
def run_model(characteristics):
    """
    This method runs the model based on the parameters listed in 'characteristics'.

    Args:
        characteristics: list of parameters that are usually obtained from the user interface

    Returns: a model_runner object containing the model completely run
    """
    # initialise the model_runner object
    m_r = autumn.model_runner.TbRunner(characteristics)
    # run the model
    m_r.master_runner()

    # initialise the output object
    project = outputs.Project(m_r, characteristics)
    # produce the outputs
    out_dir_project = project.master_outputs_runner()
    # open the directory to which everything has been written to save the user a click or two
    project.open_output_directory(out_dir_project)
    return m_r

# standard parameters obtained from the user interface when running for Fiji
standard_gui_outputs = {'is_shortcourse_improves_outcomes': True, 'pickle_uncertainty': 'No saving or loading',
               'scenario_4': False, 'plot_option_start_time': 1990.0, 'is_vary_force_infection_by_riskgroup': False,
               'age_breakpoints': [5, 15, 25], 'riskgroup_indigenous': False, 'integration_method': 'Explicit',
               'plot_option_overlay_targets': True, 'scenario_6': False, 'plot_option_vars_two_panels': True,
               'time_step': 0.5, 'is_adjust_population': True, 'plot_option_overlay_gtb': True,
               'comorbidity_to_increment': 'Diabetes', 'output_scaleups': True, 'output_param_plots': False,
               'country': 'Fiji', 'is_lowquality': False, 'is_vary_detection_by_riskgroup': False,
               'is_include_hiv_treatment_outcomes': True, 'search_width': 0.05, 'n_centiles_for_shading': 100,
               'fitting_method': 'Method 5', 'n_samples': 20, 'riskgroup_prison': False,
               'plot_option_overlay_input_data': True, 'output_flow_diagram': False, 'riskgroup_urbanpoor': False,
               'organ_strata': 'Pos / Neg / Extra', 'scenario_5': False, 'is_include_relapse_in_ds_outcomes': True,
               'scenario_7': False, 'is_misassignment': False, 'scenario_1': False, 'output_by_subgroups': True,
               'scenario_3': False, 'scenario_2': False, 'output_documents': False, 'run_mode': 'Scenario analysis',
               'default_smoothness': 1.0, 'scenario_9': False, 'scenario_8': False, 'output_age_fractions': False,
               'riskgroup_ruralpoor': False, 'scenario_10': False, 'scenario_13': False, 'scenario_12': False,
               'plot_option_end_time': 2020.0, 'scenario_14': False, 'output_horizontally': False,
               'is_timevariant_organs': False, 'write_uncertainty_outcome_params': True, 'riskgroup_hiv': False,
               'is_treatment_history': True, 'output_spreadsheets': False,
               'uncertainty_intervention': 'int_prop_treatment_support_relative', 'uncertainty_runs': 2,
               'output_by_scenario': False, 'burn_in_runs': 0, 'output_compartment_populations': True,
               'plot_option_title': True, 'strains': 'Single strain', 'output_likelihood_plot': False,
               'output_epi_plots': True, 'scenario_11': False, 'output_plot_economics': False,
               'is_amplification': False, 'riskgroup_diabetes': True, 'is_vary_detection_by_organ': True,
               'plot_option_plot_all_vars': False}

''' define several versions of the simulator '''
characteristics_1 = copy(standard_gui_outputs)

# refining time-step
characteristics_2 = copy(standard_gui_outputs)
characteristics_2['time_step'] = 0.1 # baseline was 0.5

# change integration method
characteristics_3 = copy(standard_gui_outputs)
characteristics_3['integration_method'] = 'Runge Kutta'  # baseline was Explicit

# change age brackets
characteristics_4 = copy(standard_gui_outputs)
characteristics_4['age_breakpoints'] = [5, 15, 25, 35, 45]   # baseline was [5, 15, 25]

# include more risk-groups (further stratify the population)
characteristics_5 = copy(standard_gui_outputs)
characteristics_5['riskgroup_prison'] = True  # baseline was False
characteristics_5['riskgroup_hiv'] = True  # baseline was False
characteristics_5['riskgroup_ruralpoor'] = True  # baseline was False
characteristics_5['riskgroup_urbanpoor'] = True  # baseline was False

''' define objective functions associated with different optimisation problems '''
annual_budget = 1.e6  # total budget available every year
tb_indicator = "incidence"   # could be "mortality" or "prevalence" or "notifications"

baseline_m_r = run_model(characteristics_1)
baseline_m_r.inputs.run_mode = 'spending_inputs'


def objective_1(funding):
    """
    Objective function associated with the problem of resource allocation where there is a constraint on the budget
    Note that this function requires a baseline model to be run first.
    Args:
        funding: dictionary keyed with the names of the different interventions and valued with the allocated funding
        proportion. This proportion represents the share of the annual budget allocated for each intervention.

    Returns:
        the estimated incidence (or mortality, or prevalence, or notification) of tuberculosis in 2035
    """
    # Check that the constraint is verified
    assert sum(funding.values()) <= 1., "The sum of the funding proportions should be <= 1"

    # Create a spending_plan dictionary formatted to match model requirements
    spending_plan = {}
    for key, val in funding.iteritems():
        spending_plan[key] = {}
        for year in range(int(baseline_m_r.inputs.original_data['default_constants']['before_intervention_time']) - 1,
                                  int(baseline_m_r.inputs.original_data['default_constants']['scenario_end_time']) + 1):
            spending_plan[key][year] = val * annual_budget

    # run model from 2014 until 2035 with funding driving the epidemic
    baseline_m_r.run_spending_inputs(spending_plan)
    # read the output of interest
    outcome = baseline_m_r.outputs['manual']['epi'][17][tb_indicator][-1]
    return outcome


def objective_2(parameters):
    """

    Args:
        parameters:

    Returns:

    """
    pass


funding = {'int_perc_ipt_age0to5': 0.2,
            'int_perc_ipt_age5to15': 0.1,
           'int_perc_xpertacf': 0.2,
           'int_perc_decentralisation': 0.2,
           'int_perc_treatment_support_relative': 0.2,
           'int_perc_xpert': 0.1
           }

parameters = {'tb_n_contact': 10.,
              'tb_multiplier_treated_protection': 0.6,
              'tb_prop_casefatality_untreated_smearpos': 0.7,
              'tb_timeperiod_activeuntreated': 2.8,
              }
