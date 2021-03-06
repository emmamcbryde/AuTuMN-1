"""
Runs AuTuMN apps

You can access this script from your CLI by running:

    python -m apps --help

"""
import click

from apps.covid_19 import calibration as covid_calibration
from apps.marshall_islands import calibration as rmi_calibration
from apps.mongolia import calibration as mongolia_calibration


@click.group()
def calibrate():
    """
    Calibrate a model
    """


for region in covid_calibration.CALIBRATIONS.keys():

    @calibrate.command(region)
    @click.argument("max_seconds", type=int)
    @click.argument("run_id", type=int)
    @click.option("--num-chains", type=int, default=1)
    def run_region_calibration(max_seconds, run_id, num_chains, region=region):
        """Run COVID model calibration for region"""
        calib_func = covid_calibration.get_calibration_func(region)
        calib_func(max_seconds, run_id, num_chains)


@calibrate.command("mongolia")
@click.argument("max_seconds", type=int)
@click.argument("run_id", type=int)
@click.option("--num-chains", type=int, default=1)
def mongolia_calibration(max_seconds, run_id, num_chains):
    """Run Mongolia TB model calibration."""
    mongolia_calibration.run_calibration_chain(max_seconds, run_id, num_chains)


@calibrate.command("rmi")
@click.argument("max_seconds", type=int)
@click.argument("run_id", type=int)
@click.option("--num-chains", type=int, default=1)
def rmi_calibration(max_seconds, run_id, num_chains):
    """Run Marshall Islands TB model calibration."""
    rmi_calibration.run_calibration_chain(max_seconds, run_id, num_chains)
