#!/usr/bin/env python3
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / 'results'
PROJECTS = ['Project_A_PreImprove_UI', 'Project_B_PostImprove_UI']

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

for p in PROJECTS:
    src = ROOT / p / 'screenshots'
    if src.exists():
        dst = RESULTS_DIR / p
        dst.mkdir(parents=True, exist_ok=True)
        for file in src.glob('*'):
            shutil.copy(file, dst / file.name)
    # copy logs
    logs = ROOT / p / 'logs'
    if logs.exists():
        dst_logs = RESULTS_DIR / p / 'logs'
        dst_logs.mkdir(parents=True, exist_ok=True)
        for file in logs.glob('*'):
            shutil.copy(file, dst_logs / file.name)

print('Artifacts collected to results/')
