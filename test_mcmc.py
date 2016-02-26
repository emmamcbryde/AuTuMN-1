# -*- coding: utf-8 -*-

"""
Tests out the Parameter object in parameter_estimation.py (which is currently
just a prior setting object) and the Evidence object (which isn't yet used
within the Parameter object).
@author: James
"""

import os
import collections

import numpy
import pylab
import emcee
import scipy.optimize as optimize
from numpy import isfinite
from scipy.stats import beta, gamma, norm, truncnorm

import autumn.model
from autumn.plotting import plot_fractions, plot_populations, set_axes_props



def make_gamma_dist(mean, std):
    loc = 0
    shape = mean ** 2 / std ** 2  
    scale = std ** 2 / mean
    return gamma(shape, loc, scale)


def is_positive_definite(v):
    return isfinite(v) and v > 0.0


class ModelRunner():

    def __init__(self):
        self.model = autumn.model.SingleStrainModel()
        self.model.make_times(1950, 2015, 1.)
        self.is_last_run_sucess = False
        self.param_props_list = [
            { 
                'init': 15,
                'scale': 10.,
                'key': 'n_tb_contact',
            },
            { 
                'init': 60E6,
                'scale': 10E6,
                'key': 'init_population',
            },
            { 
                'init': .15,
                'scale': .1,
                'key': 'tb_death_rate',
            },
            { 
                'init': .15,
                'scale': .1,
                'key': 'tb_recover_rate',
            },
        ]

    def set_model_with_params(self, param_dict):

        self.model.set_param(
            "tb_n_contact", param_dict["n_tb_contact"])

        self.model.set_compartment(
            "susceptible_fully", param_dict['init_population'])

        for organ in self.model.organ_status:

            self.model.set_param(
                "tb_rate_death",
                param_dict["tb_death_rate"])
            self.model.set_infection_death_rate_flow(
                "active" + organ,
                "tb_rate_death")
            self.model.set_infection_death_rate_flow(
                "detect" + organ,
                "tb_rate_death")

            self.model.set_param(
                "tb_rate_recover",
                param_dict["tb_recover_rate"])
            self.model.set_fixed_transfer_rate_flow(
                "active" + organ,
                "latent_late",
                "tb_rate_recover")

    def convert_param_list_to_dict(self, params):
        param_dict = {}
        for val, props in zip(params, self.param_props_list):
            param_dict[props['key']] = val
        return param_dict

    def run_with_params(self, params):
        for i, p in enumerate(params):
            if not is_positive_definite(p):
                print "Warning: parameter%d=%f is invalid for model" % (i, p)
                self.is_last_run_sucess = False
                return
        param_dict = self.convert_param_list_to_dict(params)
        self.set_model_with_params(param_dict)
        self.is_last_run_sucess = True
        self.model.integrate_explicit()
        # try:
        #     self.model.integrate_explicit()
        # except:
        #     print "Warning: parameters=%s failed with model" % params
        #     self.is_last_run_sucess = False

    def ln_overall(self, params):
        self.run_with_params(params)
        if not self.is_last_run_sucess:
            return -numpy.inf

        param_dict = self.convert_param_list_to_dict(params)

        final_pop = self.model.vars["population"]
        # prevalence = self.model.vars["infectious_population"] / final_pop * 1E5
        incidence = self.model.vars["incidence"]
        mortality = self.model.vars["rate_infection_death"] / final_pop * 1E5

        ln_prior = 0.0
        ln_prior += make_gamma_dist(40, 20).logpdf(param_dict['n_tb_contact'])

        ln_posterior = 0.0
        ln_posterior += norm(99E6, 5E6).logpdf(final_pop)
        # ln_posterior += norm(417, 10).logpdf(prevalence)
        ln_posterior += norm(288, 10).logpdf(incidence)
        ln_posterior += norm(10, 2).logpdf(mortality)

        ln_overall = ln_prior + ln_posterior

        print_dict = collections.OrderedDict()
        print_dict["n"] = "{:<2.0f}".format(param_dict['n_tb_contact'])
        print_dict["pop0"] = "{:<4}".format("{:.0f}M".format(param_dict['init_population']/1E6))
        print_dict["pop1"] = "{:<4}".format("{:.0f}M".format(final_pop/1E6))
        print_dict["tb_death"] = "{:<4.2f}".format(param_dict['tb_death_rate'])
        print_dict["tb_recov"] = "{:<4.2f}".format(param_dict['tb_recover_rate'])
        print_dict["inci"] = "{:<4.0f}".format(incidence)
        print_dict["mort"] = "{:<4.0f}".format(mortality)
        print_dict["-lnprob"] = "{:.0f}".format(-ln_overall)
        print " ".join("%s=%s" % (k,v) for k,v in print_dict.items())

        return ln_overall

    def scale_params(self, params):
        return [
            param / d['scale']
            for param, d in
            zip(params, self.param_props_list)]

    def revert_scaled_params(self, scaled_params):
        return [
            scaled_param * prop['scale']
            for scaled_param, prop
            in zip(scaled_params, self.param_props_list)]

    def minimize(self):

        def scaled_min_fn(scaled_params):
            params = self.revert_scaled_params(scaled_params)
            return -self.ln_overall(params)
        
        n_param = len(self.param_props_list)
        init_params = [d['init'] for d in self.param_props_list]
        scaled_init_params = self.scale_params(init_params)

        # select the TNC method which is a basic method that
        # allows bouns in the search
        bnds = [(0, None) for i in range(n_param)]
        self.minimum = optimize.minimize(
            scaled_min_fn, scaled_init_params, 
            method='TNC', bounds=bnds)

        self.minimum.best_params = self.revert_scaled_params(self.minimum.x)
        return self.minimum

    def get_init_params(self):
        return [props['init'] for props in self.param_props_list]

    def mcmc(self, n_mcmc_step=40, n_walker_per_param=2):
        n_param = len(self.param_props_list)
        self.n_walker = n_walker_per_param * n_param
        self.n_mcmc_step = n_mcmc_step
        self.sampler = emcee.EnsembleSampler(
            self.n_walker, 
            n_param,
            lambda p: self.ln_overall(p))
        init_walkers = numpy.zeros((self.n_walker, n_param))
        init_params = self.get_init_params()
        for i_walker in range(self.n_walker):
             for i_param, init_x in enumerate(init_params):
                  init_walkers[i_walker, i_param] = init_x + 1e-1 * init_x * numpy.random.uniform()
        self.sampler.run_mcmc(init_walkers, self.n_mcmc_step)
        # Emma cautions here that if the step size is proportional to the parameter value,
        # then detailed balance will not be present.

    def plot_mcmc_params(self, base, n_burn_step=0):
        sampler = self.sampler
        n_walker, n_mcmc_step, n_param = sampler.chain.shape
        for i_param in range(n_param):
            pylab.clf()
            max_val = 0.0
            for i_walker in range(n_walker):
                vals = sampler.chain[i_walker, n_burn_step:, i_param]
                pylab.plot(range(len(vals)), vals)
                max_val = max(vals.max(), max_val)
            pylab.ylim([0, 1.2 * max_val])
            key = self.param_props_list[i_param]['key']
            set_axes_props(
                pylab.gca(), 
                'MCMC steps', 
                '', 
                "Parameter: " + key, 
                False)
            pylab.savefig("%s.param.%s.png" % (base, key))

    def plot_mcmc_var(self, var, base, n_burn_step=0, n_model_show=40):
        model = self.model
        sampler = self.sampler
        times = model.times

        chain = sampler.chain[:, n_burn_step:, :]
        n_param = chain.shape[-1]
        samples = chain.reshape((-1, n_param))
        n_sample = samples.shape[0]

        pylab.clf()

        for i_sample in numpy.random.randint(n_sample, size=n_model_show):
            params = samples[i_sample, :]
            self.run_with_params(params)
            model.calculate_diagnostics()
            pylab.plot(times, model.get_var_soln(var), color="k", alpha=0.1)

        self.run_with_params(numpy.average(samples, axis=0))
        model.calculate_diagnostics()
        pylab.plot(times, model.get_var_soln(var), color="r", alpha=0.8)

        set_axes_props(
            pylab.gca(), 
            'year', 
            var, 
            'Modelled %s for selection of MCMC parameters' % var, 
            False)
        pylab.savefig(base + '.' + var + '.png')


out_dir = "mcmc_graphs"
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

model_runner = ModelRunner()

# base = os.path.join(out_dir, 'minimize')
# minimum = model_runner.minimize()
# print minimum.best_params
# model_runner.run_with_params(minimum.best_params)
# model = model_runner.model
# plot_fractions(model, model.labels[:])
# pylab.savefig(base + '.fraction.png')
# plot_populations(model, model.labels[:])
# pylab.savefig(base + '.population.png')

base = os.path.join(out_dir, 'mcmc')
model_runner.mcmc(n_mcmc_step=100)
model_runner.plot_mcmc_params(base, n_burn_step=0)
model_runner.plot_mcmc_var(
        'population', 
        base, 
        n_burn_step=40,
        n_model_show=100)


