"""Private actual launcher/native fixture. Run explicitly; absent tools fail.

The tiny Go bridge reuses the pinned Diagram acceptance builder in a PRIVATE
source snapshot. No source is written to Diagram's real checkout.
"""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PIN = 'd29c0809f722985bf2fd2a7fd5cfd8a2e4ce573e'

class NativeComposition(unittest.TestCase):
    def test_private_actual_launcher_native(self):
        source = Path(os.environ['DIAG_REVIEW_TEST_SOURCE']).resolve()
        self.assertEqual(subprocess.check_output(['git','-C',str(source),'rev-parse',PIN],text=True).strip(),PIN)
        with tempfile.TemporaryDirectory(prefix='farmboy025-') as tmp:
            root=Path(tmp)
            archive=root/'source.tar'
            with archive.open('wb') as f:
                subprocess.run(['git','-C',str(source),'archive',PIN],stdout=f,check=True)
            snapshot=root/'source'; snapshot.mkdir()
            with tarfile.open(archive) as tf:
                for entry in tf.getmembers():
                    self.assertFalse(entry.name.startswith('/') or '..' in Path(entry.name).parts)
                tf.extractall(snapshot)
            bridge=snapshot/'modules/diagram-cli/tests/acceptance/farmboy025_composition_test.go'
            shutil.copyfile(HERE/'native_fixture_bridge.go.txt',bridge)
            cli=root/'diagram'; launcher=root/'diagram-launch'
            go=os.environ['DIAG_REVIEW_TEST_GO']
            env=os.environ.copy(); env.pop('GOROOT',None); env['GOTOOLCHAIN']='local'; env['PATH']=str(Path(go).parent)+os.pathsep+env['PATH']
            for binary,pkg in [(cli,'./modules/diagram-cli/cmd/diagram'),(launcher,'./modules/diagram-cli/cmd/diagram-launch')]:
                subprocess.run([go,'build','-o',str(binary),pkg],cwd=snapshot,env=env,check=True)
            env.update(FB025_TEST_CLI=str(cli),FB025_TEST_LAUNCHER=str(launcher),FB025_TEST_PYTHON=os.sys.executable,FB025_TEST_HANDLER=str(HERE/'controlled_codex.py'),FB025_SOURCE=str(ROOT),FB025_MODE=os.environ.get('FB025_MODE','controlled'))
            # Fixture setup reuses core helpers that resolve its own explicit tools.
            subprocess.run([go,'test','-tags=acceptance','./modules/diagram-cli/tests/acceptance','-run','^TestFarmboy025Composition$','-count=1','-v'],cwd=snapshot,env=env,check=True)

if __name__=='__main__':
    unittest.main()
