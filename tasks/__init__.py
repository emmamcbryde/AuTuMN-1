"""
Runs AuTuMN tasks, which are large jobs to be run on remote servers.
These tasks are orchestrated using Luigi.

This module requires AWS access to run.

You can access this script from your CLI by running the Luigi CLI:
https://luigi.readthedocs.io/en/stable/running_luigi.html

aws --profile autumn s3 rm --recursive s3://autumn-data/malaysia-111111111-aaaaaaa

./scripts/website/deploy.sh
http://www.autumn-data.com/model/malaysia/run/malaysia-111111111-aaaaaaa.html

export LUIGI_CONFIG_PATH=tasks/luigi.cfg

# Run a calibration
python3 -m luigi \
    --module tasks \
    RunCalibrate \
    --run-id malaysia-111111111-aaaaaaa \
    --num-chains 2 \
    --CalibrationChainTask-model-name malaysia \
    --CalibrationChainTask-runtime 30 \
    --local-scheduler \
    --workers 4 \
    --logging-conf-file tasks/luigi-logging.ini

# Run full models
python3 -m luigi \
    --module tasks \
    RunFullModels \
    --run-id malaysia-111111111-aaaaaaa \
    --FullModelRunTask-burn-in 0 \
    --FullModelRunTask-model-name malaysia \
    --local-scheduler \
    --workers 4 \
    --logging-conf-file tasks/luigi-logging.ini

# Run PowerBI processing
python3 -m luigi \
    --module tasks \
    RunPowerBI \
    --run-id malaysia-111111111-aaaaaaa \
    --local-scheduler \
    --workers 4 \
    --logging-conf-file tasks/luigi-logging.ini


python3 -m luigi \
    --module tasks RunFullModels \
    --run-id manila-1594621996-7671bcd \
    --FullModelRunTask-burn-in 1000 \
    --FullModelRunTask-model-name manila \
    --local-scheduler \
    --workers 4 \
    --logging-conf-file tasks/luigi-logging.ini

"""
import os
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


from .settings import BASE_DIR
from .calibrate import RunCalibrate
from .full_model_run import RunFullModels
from .powerbi import RunPowerBI

os.makedirs(BASE_DIR, exist_ok=True)
