import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import config  # noqa: E402

import uvicorn

def main():
    uvicorn.run(
        "app.server:app",
        host=config.setting("SERVICE_HOST", "127.0.0.1"),
        port=int(config.setting("SERVICE_PORT", "8000")),
        reload=config.flask_debug(),
    )

if __name__ == "__main__":
    main()