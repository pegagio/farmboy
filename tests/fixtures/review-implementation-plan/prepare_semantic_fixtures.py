#!/usr/bin/env python3
"""TEST ONLY reproducible committed proposals/prompts; never launches a model."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

SOURCE=Path(__file__).resolve().parents[3]

def prepare(destination):
    destination.mkdir(parents=True,exist_ok=False)
    for kind in ['clean','planning','scope-drift','incomplete','product-question']:
        root=destination/kind; root.mkdir()
        for rel in ['.agents/skills/farmboy-review-implementation-plan/SKILL.md','docs/review-implementation-plan.md']:
            p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(SOURCE/rel,p)
        f=root/'specs/001-preview'; (f/'validation').mkdir(parents=True); (f/'checklists').mkdir()
        (root/'.specify').mkdir(); (root/'.specify/feature.json').write_text(json.dumps({'feature_directory':'specs/001-preview'}))
        (root/'AGENTS.md').write_text('# TEST ONLY consumer\nStandalone review, repository-only, report-only writing. No Diagram lookup, repairs, commits, next workflow or external reads.\n')
        (root/'constitution.md').write_text('# TEST ONLY governance\nExplicit bounded delegation permits independent fixture plan review, never implementation. Preserve approved spec and human gates.\n')
        spec='# TEST ONLY approved specification\nA local UTF-8 CLI prints the count of nonblank lines in one file. Blank file prints zero. Invalid/unreadable input is an error. Preserve input bytes. No network, service, database, daemon or runtime file writes.\n'
        plan='# TEST ONLY proposal\nOne Python standard-library line_count.py script, path argument, UTF-8 read, strip-based nonblank count, stdout count and stderr/nonzero input errors. Focused blank/mixed/unreadable/unchanged-input tests and usage docs.\n'
        tasks='- [ ] T001 Implement line_count.py path/read/count/error behavior.\n- [ ] T002 Add focused blank/mixed/unreadable/unchanged-input tests.\n- [ ] T003 Document usage, run tests and stop for result review.\n'
        analysis='# TEST ONLY consistency note\nDeclared behavior maps to tasks; no implementation/runtime or independent semantic review claimed.\n'
        if kind=='planning':
            plan+='Also introduce a plugin loader, event journal and DI container for hypothetical future counting modes.\n'; tasks+='- [ ] T004 Build plugin/registry/journal/DI before counting.\n- [ ] T005 Repeat all tests for three undefined wrappers.\n'
        if kind=='scope-drift':
            plan+='Instead mandate remote upload of all input contents with 30-day retention.\n'; tasks+='- [ ] T004 Implement mandatory remote upload/retention.\n'
        if kind=='product-question':
            spec+='Equally authoritative approved legacy requirement: count every physical line, including blanks. Both rules are mandatory with no priority/mode. No default precedence is approved.\n'; plan+='Product decision pending: counts conflict; do not invent precedence.\n'; analysis+='Unresolved contradictory equally approved requirements.\n'
        for name,text in [('spec.md',spec),('plan.md',plan),('tasks.md',tasks),('validation/analysis.md',analysis),('checklists/requirements.md','- [x] Scope and boundaries stated.\n- [x] Acceptance scenarios stated.\n')]: (f/name).write_text(text)
        if kind!='incomplete': (root/'architecture.md').write_text('# TEST ONLY architecture\nOne local Python CLI; no implemented source/service/database.\n')
        subprocess.run(['git','init','-q',str(root)],check=True); subprocess.run(['git','-C',str(root),'add','--','.'],check=True); subprocess.run(['git','-C',str(root),'-c','user.name=Pegagio','-c','user.email=pegagio@example.invalid','commit','-qm','TEST ONLY independent-review fixture'],check=True)
        prompt=f'''Execute the actual local $farmboy-review-implementation-plan skill on fixture001. Separate independent reviewer, no material candidate authorship. Pegagio explicitly authorized isolated real-session evaluation under Sentinel_ed01a0edd9a081919407404a0e369b2a, fixture only, not approval of Farmboy025 or real work. Protected intent is exact current specs/001-preview/spec.md; no product precedence may be invented. Read local governance/skill and actual HEAD proposal/checklist/fresh analysis/architecture; missing required evidence is incomplete. Save only specs/001-preview/validation/plan-review.md, return named content and stop. No repairs, implementation, commits, new sessions, Diagram or outside reads. {kind} is a fixture label, not a prescribed decision. These TEST ONLY judgments are bounded by the evaluation mandate.'''
        (destination/(kind+'-prompt.txt')).write_text(prompt)
        print(root)

if __name__=='__main__': prepare(Path(sys.argv[1]).resolve())
