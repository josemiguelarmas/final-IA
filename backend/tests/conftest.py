import os
import tempfile

# Las pruebas usan una base temporal: así no ensucian la base de demostración
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["FORCE_RULE_ENGINE"] = "true"
