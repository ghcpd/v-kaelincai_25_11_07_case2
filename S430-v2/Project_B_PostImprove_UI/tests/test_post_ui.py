import subprocess
from pathlib import Path
if __name__=='__main__':
    Path('../results').mkdir(parents=True, exist_ok=True)
    subprocess.check_call(['cmd','/c','run_tests.sh','1000'])
    print('Post results:')
    print(Path('../results/results_post.json').read_text())
