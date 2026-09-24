import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import feedback, web  # noqa: E402

# 与 services/agreement/feedback.py 共用 shared/feedback.py 里的同一份实现，
# 只有表名和端口不同。
app = feedback.create_feedback_app(__name__, "feedback_b")

if __name__ == "__main__":
    web.run_flask(app, 5031)
