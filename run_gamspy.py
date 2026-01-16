import subprocess
import sys

cmd = [
    sys.executable,
    'scripts/enhanced/enh_RURO_estimate_FR.py',
    '--mnl-base', 'U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl',
    '--output-dir', 'outputs/estimates/fr/2016_gamspy',
    '--group', 'joint',
    '--solver', 'gamspy-conopt',
    '--spec-config', 'scripts/enhanced/estimation_spec.yaml',
    '--auto-timestamp'
]

print("Running GAMSPy joint estimation...")
print("Command:", ' '.join(cmd))
print()

result = subprocess.run(cmd)
sys.exit(result.returncode)
