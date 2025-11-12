import json, subprocess, time
from pathlib import Path

# Simple runner to be used by CI
if __name__=='__main__':
    Path('../results').mkdir(parents=True, exist_ok=True)
    subprocess.check_call(['cmd','/c','run_tests.sh','1000'])
    print('Pre results:')
    print(Path('../results/results_pre.json').read_text())
