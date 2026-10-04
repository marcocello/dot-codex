# Independent author repair and coverage addition

Author: `/root/round_acceptance`. Date: 2026-09-30.

The first implementation run failed during fixture setup on macOS because TemporaryDirectory returned `/var/folders/...`, whose `/var` ancestor is a symlink. Public capture intentionally rejects symlink paths. The fixture now resolves its own temporary repository once, preserving the strict public capture policy. This is a portable fixture correction, not a target, scope, outcome, or assertion relaxation. The preceding default-path failure is retained by the parent implementation run; this record preserves exact prior-input hash and diff.

Independent review also requested cases already promised by FEATURE: additions/deletions under selected directories invalidate evidence, and historical inventory remains readable while current-round checks reject changed candidates. Added black-box CLI assertions for both; no feature criteria changed.

Prior acceptance.py SHA-256: `09fb39daff0133e99ca00f5405ff299a21227eddfb5022f6f2a42d61125db9c5`.

Revised acceptance.py SHA-256: `ec17de84dd5b6c9d89fba1cc47a185c0b507f9cd7bf0e53e9c04eea596f99e7c`.

```diff
--- acceptance.py (prior)
+++ acceptance.py (revised)
@@ -15,7 +15,7 @@
     def setUp(self):
         self.temp = tempfile.TemporaryDirectory(prefix='shared-journey-acceptance-')
         self.addCleanup(self.temp.cleanup)
-        self.root = Path(self.temp.name)
+        self.root = Path(self.temp.name).resolve()
         self.run_command(['git', 'init', '-q'])
         self.write('src/journey.txt', 'journey-v1\n')
         self.write('src/access.txt', 'access-v1\n')
@@ -198,6 +198,36 @@
         self.write('src/unrelated.txt', 'changed-after-review\n')
         self.cli('verification_receipt.py', 'check-round', '--root', self.root, '--round-review', receipt, ok=False)
         self.status('case', 'implemented', 'done', '--round-review', receipt, ok=False)
+
+    def test_directory_scope_tracks_additions_and_deletions(self):
+        self.implement('case')
+        self.implement('closure')
+        self.write('src/selected/config.txt', 'configuration-v1\n')
+        runs = [self.capture('journey', '--scope', 'src/journey.txt', '--scope', 'src/selected'),
+                self.capture('access', '--scope', 'src/access.txt')]
+        self.round(runs, name='initial-directory')
+        added = self.write('src/selected/added.txt', 'new determining input\n')
+        self.round(runs, name='added-input', ok=False)
+        runs[0] = self.capture('journey', '--scope', 'src/journey.txt', '--scope', 'src/selected')
+        self.round(runs, name='recaptured-directory')
+        added.unlink()
+        self.round(runs, name='deleted-input', ok=False)
+        runs[0] = self.capture('journey', '--scope', 'src/journey.txt', '--scope', 'src/selected')
+        self.round(runs, name='recaptured-deletion')
+
+    def test_historical_inventory_survives_later_candidate_changes(self):
+        self.write('.gitignore', '__pycache__/\n')
+        self.implement('case')
+        self.implement('closure')
+        receipt = self.round(self.captures())
+        for feature in ('case', 'closure'):
+            self.status(feature, 'implemented', 'done', '--round-review', receipt)
+        before = (self.root / 'docs/features/status.json').read_bytes()
+        self.write('src/journey.txt', 'subsequent-implementation\n')
+        self.cli('gate.py', '--root', self.root, '--profile', 'other')
+        self.assertEqual((self.root / 'docs/features/status.json').read_bytes(), before)
+        self.cli('verification_receipt.py', 'check-round', '--root', self.root, '--round-review', receipt, ok=False)
+        self.assertTrue((self.root / receipt).is_file())
 
     def test_implemented_can_reopen_without_claiming_verification(self):
         self.implement('case')
```
