import autumn.model_runner
import autumn.outputs as outputs
from copy import copy


def run_model(params):
    m_r = autumn.model_runner.TbRunner(params)
    m_r.master_runner()
    project = outputs.Project(m_r, params)
    out_dir_project = project.master_outputs_runner()

    # open the directory to which everything has been written to save the user a click or two
    project.open_output_directory(out_dir_project)

# standard parameters obtained from the user interface for Fiji
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


parameter_set_1 = copy(standard_gui_outputs)

parameter_set_2 = copy(standard_gui_outputs)
parameter_set_2['time_step'] = 0.1 # baseline was 0.5

parameter_set_3 = copy(standard_gui_outputs)
parameter_set_3['integration_method'] = 'Runge Kutta'  # baseline was Explicit

parameter_set_4 = copy(standard_gui_outputs)
parameter_set_4['age_breakpoints'] = [5, 15, 25, 35, 45]   # baseline was [5, 15, 25]

parameter_set_5 = copy(standard_gui_outputs)
parameter_set_5['riskgroup_prison'] = True  # baseline was False
parameter_set_5['riskgroup_hiv'] = True  # baseline was False
parameter_set_5['riskgroup_ruralpoor'] = True  # baseline was False
parameter_set_5['riskgroup_urbanpoor'] = True  # baseline was False

run_model(parameter_set_5)