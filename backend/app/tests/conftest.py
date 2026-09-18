import os
import tempfile

# 在导入任何 app 模块前把数据目录指到临时位置，避免测试碰到真实 app.db
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="ladderbill-test-"))
