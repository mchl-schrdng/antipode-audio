import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CliTests(unittest.TestCase):
    def test_generate_process_render_and_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "audio with spaces"
            command = [sys.executable, "-m", "antipode.cli", "--workspace", str(workspace)]

            def run(*args):
                return subprocess.run(command + list(args), text=True, capture_output=True, timeout=20)

            generated = run("generate", "chime.wav", "--duration", "0.1")
            self.assertEqual(generated.returncode, 0, generated.stderr)
            self.assertEqual(json.loads(generated.stdout)["frames"], 4800)
            processed = run("process", "chime.wav", "quiet.wav", "--gain-db", "-6")
            self.assertEqual(processed.returncode, 0, processed.stderr)
            self.assertAlmostEqual(json.loads(processed.stdout)["peak_dbfs"], -18, delta=0.02)
            duplicate = run("generate", "chime.wav")
            self.assertEqual(duplicate.returncode, 1)
            self.assertEqual(duplicate.stdout, "")
            self.assertIn("already exists", duplicate.stderr)
            self.assertNotIn("Traceback", duplicate.stderr)

            recipe = Path(directory) / "recipe.json"
            recipe.write_text(json.dumps({"duration": 0.2, "layers": [{"preset": "tone", "duration": 0.1}]}))
            rendered = run("render", str(recipe), "layered.wav")
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertEqual(json.loads(rendered.stdout)["channels"], 2)
            recipe.write_text("{broken")
            invalid = run("render", str(recipe), "invalid.wav")
            self.assertEqual(invalid.returncode, 1)
            self.assertFalse((workspace / "invalid.wav").exists())


if __name__ == "__main__":
    unittest.main()
