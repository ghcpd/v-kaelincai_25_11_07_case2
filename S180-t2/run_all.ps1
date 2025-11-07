# PowerShell master runner
cd Project_A_PreImprove_UI; .\setup.ps1; .\run_tests.ps1
cd ..\Project_B_PostImprove_UI; .\setup.ps1; .\run_tests.ps1
cd ..
python -c "import json; f1=open('Project_A_PreImprove_UI/results/results_pre.json'); f2=open('Project_B_PostImprove_UI/results/results_post.json'); pre=json.load(f1); post=json.load(f2); aggr={'pre':pre,'post':post}; open('results/aggregated_metrics.json','w').write(json.dumps(aggr,indent=2)); report=''; keys=['time_to_title_visible_ms','task_create_ms']; report+='## Metrics\n'; report+='\n'; report+='\n'.join([f'* {k}: pre={pre.get(k)}ms, post={post.get(k)}ms, delta={((pre.get(k,0)-post.get(k,0))/pre.get(k,1))*100 if pre.get(k) else 0:.1f}%' for k in keys]); open('compare_report.md','w').write('# Comparison Report\n\n'+report); print('Aggregated metrics and report saved')"Write-Host 'Complete. See compare_report.md and results/ folder.'
