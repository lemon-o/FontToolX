import os
import re
import subprocess
import shutil
import sys
import json
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sympy import symbols


# ─────────────────────── 路径辅助 ────────────────────────────────

def _app_dir() -> str:
    """
    返回「程序工作目录」：
    - PyInstaller 打包后：exe 文件所在目录（icon 文件夹需与 exe 同级）
    - 源码直接运行：脚本文件所在目录
    """
    if getattr(sys, "frozen", False):
        # 打包后 sys.executable 就是 exe 本身
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))
# ══════════════════════════════════════════════════════════════════
#  样式表
# ══════════════════════════════════════════════════════════════════
STYLE = """
* {
    font-family: "Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 14px;
    color: #dde1f0;
}
QMainWindow, QWidget {
    background: #161622;
}
QDialog {
    background: #161622;
}

/* ── 复选框 ── */
QCheckBox {
    color: #b0b4d0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #35355a;
    border-radius: 4px;
    background: #0f0f1a;
}
QCheckBox::indicator:checked {
    background: #3d6be8;
    border-color: #3d6be8;
}
QCheckBox::indicator:hover {
    border-color: #5555a0;
}

/* ── 工具提示 ── */
QToolTip {
    background: #1e1e2e;
    color: #dde1f0;
    border: 1px solid #5555a0;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}

/* ── GroupBox ── */
QGroupBox {
    background: transparent;
    border: 1px solid #2e2e45;
    border-radius: 10px;
    margin-top: 22px;
    padding-top: 16px;
    padding-bottom: 12px;
    padding-left: 14px;
    padding-right: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: 3px;
    padding: 2px 8px;
    background: transparent;
    color: #7aa2f7;
    font-size: 13px;
    font-weight: bold;
}

/* ── 输入控件 ── */
QLineEdit, QSpinBox, QComboBox {
    background: #0f0f1a;
    border: 1px solid #35355a;
    border-radius: 7px;
    padding: 6px 10px;
    color: #dde1f0;
    min-height: 30px;
    selection-background-color: #7aa2f7;
    selection-color: #0f0f1a;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1.5px solid #7aa2f7;
    background: #12121f;
}
QLineEdit::placeholder { color: #454560; }

QSpinBox {
    padding-right: 24px;
}

QComboBox QAbstractItemView {
    background: #1e1e2e;
    border: 1px solid #35355a;
    outline: none;
    selection-background-color: #3a3a7a;
    selection-color: #dde1f0;
    padding: 4px;
}

/* ── 复选框 ── */
QCheckBox {
    color: #b0b4d0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #35355a;
    border-radius: 4px;
    background: #0f0f1a;
}
QCheckBox::indicator:checked {
    background: #3d6be8;
    border-color: #3d6be8;
}
QCheckBox::indicator:hover {
    border-color: #5555a0;
}

/* ── 通用按钮 ── */
QPushButton {
    background: #25253a;
    border: 1px solid #35355a;
    border-radius: 7px;
    padding: 7px 16px;
    color: #b0b4d0;
    min-height: 32px;
}
QPushButton:hover   { background: #2e2e50; border-color: #5555a0; color: #dde1f0; }
QPushButton:pressed { background: #3a3a60; }
QPushButton:disabled { background: #1e1e2e; border-color: #2a2a40; color: #404060; }

/* 主操作按钮：生成 */
QPushButton#btn_generate {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3d6be8, stop:1 #2955cc);
    border: none;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
    border-radius: 9px;
    min-height: 44px;
    letter-spacing: 1px;
}
QPushButton#btn_generate:hover   { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #5580ff, stop:1 #3d6be8); }
QPushButton#btn_generate:pressed { background: #2244bb; }
QPushButton#btn_generate:disabled { background: #1e1e35; color: #404060; border: 1px solid #2a2a45; }

/* 副操作按钮：预览 */
QPushButton#btn_preview {
    background: transparent;
    border: 1.5px solid #5a5a9a;
    color: #9aa8f0;
    font-weight: bold;
    font-size: 14px;
    border-radius: 9px;
    min-height: 44px;
    letter-spacing: 1px;
}
QPushButton#btn_preview:hover   { background: #1e1e3a; border-color: #7a80d0; color: #c0c8ff; }
QPushButton#btn_preview:pressed { background: #252545; }
QPushButton#btn_preview:disabled { border-color: #2a2a40; color: #404060; }

/* 小按钮 */
QPushButton#btn_sm {
    background: #1e1e2e;
    border: 1px solid #2e2e48;
    border-radius: 6px;
    padding: 5px 14px;
    font-size: 13px;
    min-height: 28px;
    color: #9090b8;
}
QPushButton#btn_sm:hover { background: #252540; border-color: #4545a0; color: #c0c0e0; }

/* 危险按钮 */
QPushButton#btn_danger {
    background: #2a1525;
    border: 1px solid #8b3060;
    border-radius: 7px;
    color: #f7768e;
    font-weight: bold;
    padding: 6px 14px;
    min-height: 30px;
}
QPushButton#btn_danger:hover { background: #3a1a30; border-color: #cc4480; }

/* ── 分隔线 ── */
QFrame#divider {
    background: #252535;
    max-width: 1px;
    min-width: 1px;
}

/* ── 标签 ── */
QLabel#tag_section {
    color: #5566cc;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1px;
}
QLabel#status_ok   { color: #9ece6a; font-size: 13px; }
QLabel#status_err  { color: #f7768e; font-size: 13px; }
QLabel#status_warn { color: #e0af68; font-size: 13px; }
QLabel#env_ok  { color: #9ece6a; font-size: 13px; }
QLabel#env_err { color: #f7768e; font-size: 13px; }

/* ── 进度条 ── */
QProgressBar {
    background: #1a1a2e;
    border: 1px solid #2e2e50;
    border-radius: 5px;
    height: 6px;
    text-align: center;
    font-size: 0px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3d6be8, stop:1 #7aa2f7);
    border-radius: 5px;
}

/* ── 滚动条 ── */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical   { background:#161622; width:7px;  border-radius:3px; }
QScrollBar:horizontal { background:#161622; height:7px; border-radius:3px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #35355a; border-radius: 3px; min-length: 30px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #5555a0; }
QScrollBar::add-line, QScrollBar::sub-line { width:0; height:0; }
"""

# ══════════════════════════════════════════════════════════════════
#  配置文件管理
# ══════════════════════════════════════════════════════════════════
def get_config_path():
    """获取配置文件路径（C盘用户文档目录）"""
    doc_dir = os.path.join(os.path.expanduser("~"), "Documents", "FontTool")
    os.makedirs(doc_dir, exist_ok=True)
    return os.path.join(doc_dir, "config.json")

def load_config():
    """加载配置文件"""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config_data):
    """保存配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存配置失败: {e}")

# ══════════════════════════════════════════════════════════════════
#  RLE 压缩算法（适用于点阵字库）
# ══════════════════════════════════════════════════════════════════
def compress_bitmap_rle(bitmap_bytes: list) -> tuple:
    """
    RLE (Run-Length Encoding) 压缩点阵数据
    
    压缩格式: 每个单元 2 字节
    - 字节1: 计数值 (0x00-0xFF)
      - 0x01-0x7F: 后续重复字节的次数 (1-127)
      - 0x81-0xFF: 后续不重复字节的个数 (1-127，取低7位)
    - 字节2: 数据字节
    
    返回: (compressed_bytes, compression_ratio)
    """
    if not bitmap_bytes:
        return [], 0.0
    
    compressed = []
    i = 0
    total = len(bitmap_bytes)
    
    while i < total:
        # 检测重复字节序列
        run_len = 1
        while (i + run_len < total and 
               run_len < 127 and 
               bitmap_bytes[i + run_len] == bitmap_bytes[i]):
            run_len += 1
        
        if run_len >= 3:  # 至少3个重复才值得压缩
            compressed.append(run_len)      # 重复次数
            compressed.append(bitmap_bytes[i])  # 重复的字节
            i += run_len
        else:
            # 不重复的序列
            start = i
            i += 1
            while i < total:
                # 检测下一个可能的重复序列
                next_run = 1
                while (i + next_run < total and 
                       next_run < 3 and 
                       bitmap_bytes[i + next_run] == bitmap_bytes[i]):
                    next_run += 1
                
                if next_run >= 3:
                    break
                i += 1
                
                # 最多127个不重复字节
                if i - start >= 127:
                    break
            
            length = i - start
            compressed.append(0x80 | length)  # 高位标记 + 长度
            compressed.extend(bitmap_bytes[start:i])
    
    # 添加结束标记
    compressed.append(0x00)
    
    ratio = len(compressed) / len(bitmap_bytes) * 100 if bitmap_bytes else 0
    
    return compressed, ratio


def decompress_bitmap_rle(compressed: list) -> list:
    """RLE 解压缩（用于验证和运行时解压）"""
    if not compressed:
        return []
    
    decompressed = []
    i = 0
    
    while i < len(compressed):
        cmd = compressed[i]
        
        if cmd == 0x00:  # 结束标记
            break
        
        if cmd & 0x80:  # 不重复字节序列
            length = cmd & 0x7F
            decompressed.extend(compressed[i+1:i+1+length])
            i += 1 + length
        else:  # 重复字节
            byte_val = compressed[i+1]
            decompressed.extend([byte_val] * cmd)
            i += 2
    
    return decompressed


# ══════════════════════════════════════════════════════════════════
#  环境检测 & 安装
# ══════════════════════════════════════════════════════════════════
def check_node():         return shutil.which("node") is not None
def check_npm():          return shutil.which("npm")  is not None
def check_lv_font_conv(): return shutil.which("lv_font_conv") is not None


class InstallThread(QThread):
    log     = pyqtSignal(str)
    success = pyqtSignal()
    failed  = pyqtSignal(str)

    def run(self):
        # 匹配 ANSI 控制字符的正则（用于剔除终端颜色代码和光标控制符）
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        def read_process_output(proc):
            """动态解码生成器，处理 utf-8 和 gbk 混杂的情况"""
            for raw_line in iter(proc.stdout.readline, b''):
                try:
                    # 先尝试用 UTF-8 解码
                    line = raw_line.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果失败，退回到 Windows 默认的 GBK 解码
                    line = raw_line.decode('gbk', errors='replace')
                
                # 清理 ANSI 字符并去除头尾空格
                clean_line = ansi_escape.sub('', line).strip()
                if clean_line:
                    self.log.emit(clean_line)

        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

            # ── 1. 检查并安装 Node.js ──
            if not check_node():
                self.log.emit("> 🔴 未检测到 Node.js，准备自动安装 LTS 版本...")
                self.log.emit("> (此过程可能需要几分钟，若弹出权限许可框请点击【允许】)")
                
                # 新增参数 --disable-interactivity 禁用交互式进度条
                cmd_node = [
                    "winget", "install", "OpenJS.NodeJS.LTS", "-e", 
                    "--accept-source-agreements", "--accept-package-agreements",
                    "--disable-interactivity"
                ]
                
                proc = subprocess.Popen(
                    cmd_node,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=0, # 关闭缓冲，实时输出
                    creationflags=flags
                )
                
                read_process_output(proc)
                proc.wait()
                
                if proc.returncode != 0:
                    raise RuntimeError("Node.js 自动安装失败。可能您的系统不支持 winget，请手动下载安装。")
                
                self.log.emit("> ✔ Node.js 安装成功！")
                raise RuntimeError("REQUIRE_RESTART")

            # ── 2. 检查并安装 lv_font_conv ──
            if not check_lv_font_conv():
                self.log.emit("> 🔵 Node.js 已就绪，准备启动 npm 安装...")
                npm = shutil.which("npm") or "npm"
                
                # 新增参数 --no-color 和 --no-progress 强制纯文本输出
                cmd_npm = [npm, "install", "-g", "lv_font_conv", "--no-color", "--no-progress", "--no-audit", "--no-fund"]
                
                proc = subprocess.Popen(
                    cmd_npm,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=0,
                    creationflags=flags
                )
                
                read_process_output(proc)
                proc.wait()
                
                if proc.returncode != 0:
                    raise RuntimeError(f"npm 返回了错误码: {proc.returncode}")
                
            self.success.emit()
            
        except Exception as e:
            self.failed.emit(str(e))


# ══════════════════════════════════════════════════════════════════
#  启动时自动检测 / 安装对话框
# ══════════════════════════════════════════════════════════════════
class EnvCheckDialog(QDialog):
    """
    启动后弹出：检测环境，如有缺失则全自动执行安装。
    内置日志视图，支持跨环境链式安装与重启提示。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("环境检测与配置")
        self.setFixedWidth(500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(14)

        title = QLabel("环境检测与配置")
        title.setStyleSheet("font-size:17px; font-weight:bold; color:#7aa2f7;")
        lay.addWidget(title)

        # 状态区
        self.lbl_node = QLabel(); lay.addWidget(self.lbl_node)
        self.lbl_npm  = QLabel(); lay.addWidget(self.lbl_npm)
        self.lbl_lv   = QLabel(); lay.addWidget(self.lbl_lv)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        lay.addWidget(self.progress)

        # 日志区
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFixedHeight(140)
        self.log_view.setStyleSheet("""
            QPlainTextEdit {
                background: #0a0a14; border: 1px solid #35355a;
                border-radius: 6px; padding: 6px;
                color: #9aa8f0; font-family: Consolas, "Courier New", monospace;
                font-size: 12px;
            }
            QScrollBar:vertical { background:#161622; width:7px; border-radius:3px; }
            QScrollBar::handle:vertical { background: #35355a; border-radius: 3px; }
        """)
        self.log_view.setVisible(False)
        lay.addWidget(self.log_view)

        self.lbl_msg = QLabel("")
        self.lbl_msg.setObjectName("status_warn")
        self.lbl_msg.setWordWrap(True)
        lay.addWidget(self.lbl_msg)

        # 按钮行
        btn_row = QHBoxLayout()
        self.btn_install = QPushButton("重试安装")
        self.btn_install.setObjectName("btn_generate")
        self.btn_install.setVisible(False)
        self.btn_install.clicked.connect(self.do_install)
        
        self.btn_close = QPushButton("关闭")
        self.btn_close.setObjectName("btn_sm")
        self.btn_close.clicked.connect(self.accept)
        
        btn_row.addWidget(self.btn_install)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_close)
        lay.addLayout(btn_row)

        self._install_thread = None
        QTimer.singleShot(100, self.run_check)

    def _set(self, lbl, text, ok):
        icon = "✔" if ok else "✘"
        lbl.setText(f"{icon}  {text}")
        lbl.setObjectName("env_ok" if ok else "env_err")
        lbl.style().unpolish(lbl)
        lbl.style().polish(lbl)

    def run_check(self):
        ok_node = check_node()
        ok_npm  = check_npm()
        ok_lv   = check_lv_font_conv()

        self._set(self.lbl_node, "Node.js",      ok_node)
        self._set(self.lbl_npm,  "npm",           ok_npm)
        self._set(self.lbl_lv,   "lv_font_conv",  ok_lv)

        missing = []
        if not ok_node: missing.append("Node.js")
        if not ok_npm:  missing.append("npm")
        if not ok_lv:   missing.append("lv_font_conv")

        if not missing:
            self.lbl_msg.setText("✔  所有依赖已就绪，可以开始使用。")
            self.lbl_msg.setObjectName("status_ok")
            self.lbl_msg.setStyle(self.lbl_msg.style())
            # 全通过，延时 1 秒自动关闭弹窗
            QTimer.singleShot(1000, self.accept)
        else:
            self.lbl_msg.setText("⚠  检测到缺失依赖，正在为您自动配置...")
            self.lbl_msg.setObjectName("status_warn")
            self.lbl_msg.setStyle(self.lbl_msg.style())
            self.btn_install.setVisible(False)
            self.adjustSize()
            
            # 延时一点自动执行安装，避免界面来不及渲染
            QTimer.singleShot(500, self.do_install)

    def do_install(self):
        self.btn_install.setEnabled(False)
        self.progress.setVisible(True)
        self.log_view.setVisible(True)
        self.log_view.clear()
        
        self.lbl_msg.setText("正在执行后台安装，请耐心等待...")
        self.adjustSize()

        self._install_thread = InstallThread()
        self._install_thread.log.connect(self.append_log)
        self._install_thread.success.connect(self.on_install_ok)
        self._install_thread.failed.connect(self.on_install_fail)
        self._install_thread.start()

    def append_log(self, text):
        self.log_view.appendPlainText(text)
        bar = self.log_view.verticalScrollBar()
        bar.setValue(bar.maximum())

    def on_install_ok(self):
        self.progress.setVisible(False)
        self.btn_install.setVisible(False)
        self.log_view.setVisible(False) # 成功后隐藏丑陋的日志，界面清爽
        self.run_check()

    def on_install_fail(self, msg):
        self.progress.setVisible(False)
        
        # 如果是 Node 安装成功的重启信号
        if msg == "REQUIRE_RESTART":
            self.lbl_msg.setText("✔ Node.js 安装成功！\n\n正在为您重启软件以加载环境变量...")
            self.lbl_msg.setObjectName("status_ok")
            self.lbl_msg.setStyle(self.lbl_msg.style())
            self.adjustSize()
            
            # 延时 2 秒后重启，确保用户能看到提示
            QTimer.singleShot(2000, self.restart_app)
        else:
            # 原有的错误处理逻辑
            self.btn_install.setVisible(True) 
            self.btn_install.setEnabled(True)
            self.btn_install.setText("重试安装")
            self.lbl_msg.setText(f"✘  安装失败：{msg}")
            self.lbl_msg.setObjectName("status_err")
            self.lbl_msg.setStyle(self.lbl_msg.style())
            self.append_log(f"\n[错误中断] {msg}")
            self.adjustSize()
            
        self.adjustSize()

    def restart_app(self):
            """重启当前 Python 进程"""
            import sys
            import os
            
            # 停止所有逻辑，彻底退出并重启
            python = sys.executable
            # 使用 os.execl 替换当前进程
            # sys.argv 是当前启动的参数，确保重启后参数一致
            os.execl(python, python, *sys.argv)

# ══════════════════════════════════════════════════════════════════
#  后台生成线程
# ══════════════════════════════════════════════════════════════════
class BuildThread(QThread):
    finished = pyqtSignal(str, bool)
    error    = pyqtSignal(str)

    def __init__(self, font, size, bpp, symbols, save_file=False, compress=False, dedup_info=None):
        super().__init__()
        self.font = font
        self.size = size
        self.bpp  = bpp
        self.symbols = symbols
        self.save_file = save_file
        self.compress = compress
        self.dedup_info = dedup_info

    def run(self):
        import tempfile
        tmp_dir = tempfile.gettempdir()
        tmp = os.path.join(tmp_dir, "tmp_font.c")
        
        try:
            lv = shutil.which("lv_font_conv") or "lv_font_conv"

            cmd = [
                lv, "--font", self.font,
                "--size", str(self.size),
                "--bpp",  str(self.bpp),
                f"--symbols={self.symbols}",   # 用等号形式，避免 - 开头被误判为选项
                "--format", "lvgl",
                "-o", tmp
            ]
            
            if not self.compress:
                cmd.insert(-2, "--no-compress")
            
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            r = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags)
            
            if r.returncode != 0:
                raise RuntimeError(r.stderr.strip() or "lv_font_conv 返回错误")
            self.finished.emit(tmp, self.save_file)
        except Exception as e:
            self.error.emit(str(e))

# ══════════════════════════════════════════════════════════════════
#  点阵解析 → QPixmap
# ══════════════════════════════════════════════════════════════════
def parse_glyphs_to_pixmap(c_file: str, bpp: int, wrap_width: int = 0) -> QPixmap:
    """
    解析点阵数据并生成QPixmap。
    如果指定wrap_width > 0，则按该宽度自动换行排列字符。
    """
    with open(c_file, "r", encoding="utf-8") as f:
        data = f.read()

    bmp_m = re.search(r"glyph_bitmap\[\]\s*=\s*\{(.*?)\};", data, re.S)
    dsc_m = re.search(r"glyph_dsc\[\]\s*=\s*\{(.*?)\};",    data, re.S)
    if not bmp_m or not dsc_m:
        return QPixmap()

    bmp_bytes = [int(h, 16) for h in re.findall(r"0x[0-9a-fA-F]+", bmp_m.group(1))]
    dsc_list  = re.findall(
        r"\{\s*\.bitmap_index\s*=\s*(\d+).*?\.box_w\s*=\s*(\d+).*?\.box_h\s*=\s*(\d+)",
        dsc_m.group(1), re.S
    )

    ppb  = 8 // bpp
    mask = (1 << bpp) - 1
    valid = [(int(b), int(w), int(h)) for b, w, h in dsc_list if int(w) > 0 and int(h) > 0]
    if not valid:
        return QPixmap()

    PAD = 10
    
    if wrap_width <= 0:
        total_w = sum(w + PAD for _, w, h in valid) + PAD
        max_h = max(h for _, w, h in valid) + PAD * 2
        lines = [(valid, max_h - PAD * 2)]
        total_h = max_h

    else:
        lines = []
        current_line = []
        line_width = PAD
        line_height = 0
        max_line_w = 0
        
        for b_idx, w, h in valid:
            char_total_w = w + PAD
            if current_line and line_width + char_total_w > wrap_width:
                max_line_w = max(max_line_w, line_width)
                lines.append((current_line, line_height))
                current_line = []
                line_width = PAD
                line_height = 0
            
            current_line.append((b_idx, w, h))
            line_width += char_total_w
            line_height = max(line_height, h)
        
        if current_line:
            max_line_w = max(max_line_w, line_width)
            lines.append((current_line, line_height))
        
        total_w = max_line_w
        total_h = sum(lh + PAD for _, lh in lines) + PAD

    pm = QPixmap(total_w, total_h)
    pm.fill(QColor("#0a0a14"))
    painter = QPainter(pm)

    y = PAD
    for line_chars, line_h in lines:
        x = PAD
        for b_idx, w, h in line_chars:
            y0 = y + (line_h - h) // 2
            for row in range(h):
                for col in range(w):
                    pi  = row * w + col
                    bo  = pi // ppb
                    bs  = 8 - bpp - (pi % ppb) * bpp
                    idx = b_idx + bo
                    if idx < len(bmp_bytes):
                        val = (bmp_bytes[idx] >> bs) & mask
                        if val > 0:
                            c = int((val / mask) * 255)
                            painter.fillRect(x + col, y0 + row, 1, 1,
                                           QBrush(QColor(c, c, c)))
            x += w + PAD
        y += line_h + PAD

    painter.end()
    return pm


# ══════════════════════════════════════════════════════════════════
#  预览弹窗
# ══════════════════════════════════════════════════════════════════
class PreviewDialog(QDialog):
    def __init__(self, pixmap: QPixmap, w: int, h: int, title: str = "点阵预览", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint
        )
        self._pixmap = pixmap

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #0a0a14;
            }
            QScrollBar:vertical {
                background: #161622;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar:horizontal {
                background: #161622;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #35355a;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:horizontal {
                background: #35355a;
                border-radius: 4px;
                min-width: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5555a0;
            }
            QScrollBar::handle:horizontal:hover {
                background: #5555a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                height: 0px;
            }
        """)

        content_width = pixmap.width() if pixmap and not pixmap.isNull() else w
        content_height = pixmap.height() if pixmap and not pixmap.isNull() else h
        canvas = _PixmapWidget(pixmap, content_width, content_height)
        
        scroll_area.setWidget(canvas)
        scroll_area.setFixedSize(w, h)
        
        if content_width <= w:
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(scroll_area)

        self.setFixedSize(self.sizeHint())

class _PixmapWidget(QWidget):
    """显示点阵预览图，保持原始像素大小。"""
    def __init__(self, pm, w, h):
        super().__init__()
        self._pm = pm
        self.setFixedSize(w, h)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#0a0a14"))
        if self._pm and not self._pm.isNull():
            p.drawPixmap(0, 0, self._pm)
        else:
            p.setPen(QColor("#35355a"))
            p.setFont(QFont("Microsoft YaHei UI", 12))
            p.drawText(self.rect(), Qt.AlignCenter, "暂无预览数据")
        p.end()

# ══════════════════════════════════════════════════════════════════
#  主窗口
# ══════════════════════════════════════════════════════════════════
class FontTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FontToolX")
        self.setMinimumSize(600, 800)

        icon_path = os.path.join(_app_dir(), "icon", "FontToolX.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_thread  = None
        self._last_pixmap   = None
        self._preview_win   = None

        root = QWidget()
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(22, 22, 22, 22)
        lay.setSpacing(16)

        # ════════ 字体设置 ════════
        grp_font = QGroupBox("字体设置")
        gf = QVBoxLayout(grp_font)
        gf.setSpacing(10)

        row_f = QHBoxLayout(); row_f.setSpacing(8)
        self.le_font = QLineEdit()
        self.le_font.setPlaceholderText("请选择 .ttf / .otf 字体文件…")
        btn_pick = QPushButton("选择字体"); btn_pick.setObjectName("btn_sm")
        btn_pick.setFixedWidth(92); btn_pick.clicked.connect(self.pick_font)
        row_f.addWidget(self.le_font); row_f.addWidget(btn_pick)
        gf.addLayout(row_f)

        row_opts = QHBoxLayout(); row_opts.setSpacing(20)
        lbl_sz = QLabel("字号(px)"); lbl_sz.setFixedWidth(70)
        self.sp_size = QSpinBox(); self.sp_size.setRange(6, 256); self.sp_size.setValue(50)
        self.sp_size.setFixedWidth(100)
        lbl_bpp = QLabel("像素深度(BPP)"); lbl_bpp.setFixedWidth(100)
        self.cb_bpp = QComboBox(); self.cb_bpp.addItems(["1","2","4","8"])
        self.cb_bpp.setCurrentIndex(2); self.cb_bpp.setFixedWidth(100)
        row_opts.addWidget(lbl_sz); row_opts.addWidget(self.sp_size)
        row_opts.addSpacing(10)
        row_opts.addWidget(lbl_bpp); row_opts.addWidget(self.cb_bpp)
        row_opts.addStretch()
        gf.addLayout(row_opts)
        lay.addWidget(grp_font)

        # ════════ 字符集 ════════
        grp_sym = QGroupBox("字符集")
        gs = QVBoxLayout(grp_sym); gs.setSpacing(10)
        self.le_sym = QLineEdit("0123456789")
        self.le_sym.setPlaceholderText("输入要生成的字符…")
        gs.addWidget(self.le_sym)

        row_pre = QHBoxLayout(); row_pre.setSpacing(8)
        lbl_pre = QLabel("快速预设"); lbl_pre.setObjectName("tag_section"); lbl_pre.setFixedWidth(70)
        row_pre.addWidget(lbl_pre)
        for label, text in [
            ("数字",   "0123456789"),
            ("字母",   "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"),
            ("ASCII",  "".join(chr(i) for i in range(32, 127)))
        ]:
            b = QPushButton(label); b.setObjectName("btn_sm")
            b.clicked.connect(lambda _, t=text: self.le_sym.setText(t))
            row_pre.addWidget(b)
        row_pre.addStretch()
        gs.addLayout(row_pre)
        lay.addWidget(grp_sym)

        # ════════ 输出 & 预览尺寸 & 压缩选项 ════════
        grp_io = QGroupBox("输出设置")
        gi = QVBoxLayout(grp_io); gi.setSpacing(10)

        row_out = QHBoxLayout(); row_out.setSpacing(8)
        lbl_out = QLabel("输出目录"); lbl_out.setFixedWidth(70)
        self.le_out = QLineEdit(os.getcwd())
        btn_out = QPushButton("选择目录"); btn_out.setObjectName("btn_sm")
        btn_out.setFixedWidth(92); btn_out.clicked.connect(self.pick_out)
        row_out.addWidget(lbl_out); row_out.addWidget(self.le_out); row_out.addWidget(btn_out)
        gi.addLayout(row_out)

        # 预览尺寸行
        row_wh = QHBoxLayout(); row_wh.setSpacing(12)
        lbl_pw = QLabel("预览宽度"); lbl_pw.setFixedWidth(70)
        self.sp_pw = QSpinBox(); self.sp_pw.setRange(40,4096); self.sp_pw.setValue(240); self.sp_pw.setFixedWidth(100)
        lbl_ph = QLabel("预览高度"); lbl_ph.setFixedWidth(70)
        self.sp_ph = QSpinBox(); self.sp_ph.setRange(40,4096); self.sp_ph.setValue(240); self.sp_ph.setFixedWidth(100)
        row_wh.addWidget(lbl_pw); row_wh.addWidget(self.sp_pw)
        row_wh.addSpacing(10)
        row_wh.addWidget(lbl_ph); row_wh.addWidget(self.sp_ph)
        row_wh.addStretch()
        gi.addLayout(row_wh)
        
        # 压缩选项行
        row_compress = QHBoxLayout(); row_compress.setSpacing(12)
        self.cb_compress = QCheckBox("压缩字体（RLE编码，减小Flash占用）")
        self.cb_compress.setToolTip(
            "启用后使用 RLE (Run-Length Encoding) 压缩点阵数据\n"
            "可节省 30%-70% Flash 空间\n"
            "需要固件端实现解压缩函数（会生成配套的解压代码）"
        )
        self.cb_compress.stateChanged.connect(self.on_compress_changed)
        row_compress.addWidget(self.cb_compress)
        
        self.lbl_compress_info = QLabel("")
        self.lbl_compress_info.setObjectName("tag_section")
        self.lbl_compress_info.setVisible(False)
        row_compress.addWidget(self.lbl_compress_info)
        row_compress.addStretch()
        gi.addLayout(row_compress)
        
        lay.addWidget(grp_io)

        # ════════ 环境状态（紧凑横排）════════
        grp_env = QGroupBox("运行环境")
        ge = QHBoxLayout(grp_env); ge.setSpacing(24)
        self.lbl_node = QLabel()
        self.lbl_npm = QLabel()
        self.lbl_lv = QLabel()

        # 【新增代码】：给标签一个基础宽度，防止启动时瞬间文字被截断
        self.lbl_node.setMinimumWidth(80)
        self.lbl_npm.setMinimumWidth(80)
        self.lbl_lv.setMinimumWidth(120)
        ge.addWidget(self.lbl_node); ge.addWidget(self.lbl_npm); ge.addWidget(self.lbl_lv)
        ge.addStretch()
        btn_recheck = QPushButton("重新检测"); btn_recheck.setObjectName("btn_sm")
        btn_recheck.setFixedWidth(92); btn_recheck.clicked.connect(self.refresh_env)
        ge.addWidget(btn_recheck)
        lay.addWidget(grp_env)

        lay.addStretch()

        # ════════ 状态栏 ════════
        # self.lbl_status = QLabel("就绪")
        # self.lbl_status.setObjectName("status_ok")
        # self.lbl_status.setFixedHeight(24)
        # lay.addWidget(self.lbl_status)

        # ════════ 操作按钮行 ════════
        btn_row = QHBoxLayout(); btn_row.setSpacing(12)
        self.btn_generate = QPushButton("生成")
        self.btn_generate.setObjectName("btn_generate")
        self.btn_generate.clicked.connect(self.build)

        self.btn_preview = QPushButton("预览")
        self.btn_preview.setObjectName("btn_preview")
        self.btn_preview.clicked.connect(self.preview) 

        btn_row.addWidget(self.btn_generate)
        btn_row.addWidget(self.btn_preview)
        lay.addLayout(btn_row)

        # 加载配置
        self.load_settings()
        
        # 启动后自动检测环境
        QTimer.singleShot(200, self.auto_env_check)

    # ─────────────────────────────────────────────
    def pick_font(self):
        p, _ = QFileDialog.getOpenFileName(self, "选择字体文件", "", "字体文件 (*.ttf *.otf)")
        if p: self.le_font.setText(p)

    def pick_out(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录", self.le_out.text())
        if d: self.le_out.setText(d)

    # ─────────────────────────────────────────────
    def on_compress_changed(self, state):
        """压缩复选框状态改变"""
        if state == Qt.Checked:
            self.lbl_compress_info.setObjectName("status_ok")
        else:
            self.lbl_compress_info.setObjectName("tag_section")
        self.lbl_compress_info.setVisible(True)
        self.lbl_compress_info.setStyle(self.lbl_compress_info.style())

    # ─────────────────────────────────────────────
    def _set_env_lbl(self, lbl, text, ok):
        lbl.setText(("✔ " if ok else "✘ ") + text)
        lbl.setObjectName("env_ok" if ok else "env_err")
        lbl.style().unpolish(lbl)
        lbl.style().polish(lbl)

    def refresh_env(self):
        self.lbl_node.setText("检测中...")
        self.lbl_npm.setText("检测中...")
        self.lbl_lv.setText("检测中...")
        
        self.lbl_node.setObjectName("status_warn")
        self.lbl_npm.setObjectName("status_warn")
        self.lbl_lv.setObjectName("status_warn")
        
        # 【新增代码】：强制刷新这三个标签的样式表
        for lbl in (self.lbl_node, self.lbl_npm, self.lbl_lv):
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

        QApplication.processEvents()

        self._set_env_lbl(self.lbl_node, "Node.js",      check_node())
        self._set_env_lbl(self.lbl_npm,  "npm",           check_npm())
        self._set_env_lbl(self.lbl_lv,   "lv_font_conv",  check_lv_font_conv())

    def auto_env_check(self):
        self.refresh_env()
        missing_lv   = not check_lv_font_conv()
        missing_node = not check_node() or not check_npm()
        if missing_lv or missing_node:
            dlg = EnvCheckDialog(self)
            dlg.exec_()
            self.refresh_env()

    # ─────────────────────────────────────────────
    # def set_status(self, msg, kind="ok"):
    #     self.lbl_status.setText(msg)
    #     self.lbl_status.setObjectName(f"status_{kind}")
    #     self.lbl_status.setStyle(self.lbl_status.style())

    # ─────────────────────────────────────────────
    def load_settings(self):
        """从配置文件加载设置"""
        config = load_config()
        if not config:
            return
        
        font_path = config.get("font_path", "")
        if font_path and os.path.exists(font_path):
            self.le_font.setText(font_path)
        
        font_size = config.get("font_size", 50)
        if 6 <= font_size <= 256:
            self.sp_size.setValue(font_size)
        
        bpp = config.get("bpp", 4)
        bpp_str = str(bpp)
        idx = self.cb_bpp.findText(bpp_str)
        if idx >= 0:
            self.cb_bpp.setCurrentIndex(idx)
        
        out_dir = config.get("output_dir", "")
        if out_dir and os.path.exists(out_dir):
            self.le_out.setText(out_dir)
        
        preview_w = config.get("preview_w", 240)
        if 40 <= preview_w <= 4096:
            self.sp_pw.setValue(preview_w)
        
        preview_h = config.get("preview_h", 240)
        if 40 <= preview_h <= 4096:
            self.sp_ph.setValue(preview_h)
        
        symbols = config.get("symbols", "")
        if symbols:
            self.le_sym.setText(symbols)
        
        # 加载压缩选项
        compress = config.get("compress", False)
        self.cb_compress.setChecked(compress)

    def save_settings(self):
        """保存当前设置到配置文件"""
        config = {
            "font_path": self.le_font.text().strip(),
            "font_size": self.sp_size.value(),
            "bpp": int(self.cb_bpp.currentText()),
            "output_dir": self.le_out.text().strip(),
            "preview_w": self.sp_pw.value(),
            "preview_h": self.sp_ph.value(),
            "symbols": self.le_sym.text(),
            "compress": self.cb_compress.isChecked(),
        }
        save_config(config)

    def closeEvent(self, event):
        """窗口关闭时保存配置"""
        self.save_settings()
        super().closeEvent(event)

    # ─────────────────────────────────────────────
    def build(self):
        font = self.le_font.text().strip()
        if not font or not os.path.exists(font):
            QMessageBox.warning(self, "提示", "请先选择有效的字体文件"); return
        if not check_lv_font_conv():
            QMessageBox.warning(self, "提示", "未找到 lv_font_conv，请在环境检测中安装"); return

        self.save_settings()

        self.btn_generate.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self._last_pixmap = None

        symbols = self.le_sym.text()
        original_len = len(symbols)
        total_removed = 0
        
        # 字符去重（保持原有顺序）
        deduped_symbols = ''.join(dict.fromkeys(symbols))
        removed_count = original_len - len(deduped_symbols)
        total_removed += removed_count
        
        # 更新输入框
        if deduped_symbols != symbols:
            self.le_sym.setText(deduped_symbols)
            symbols = deduped_symbols
        
        if sys.platform == "win32":
            problematic_chars = set('><|&^')
            removed = [c for c in symbols if c in problematic_chars]
            if removed:
                filtered = ''.join(c for c in symbols if c not in problematic_chars)
                symbols = filtered
                self.le_sym.setText(filtered)
                total_removed += len(removed)
        
        # 存储去重信息（使用最终的去重总数）
        dedup_info = {
            'removed': total_removed,
            'original_len': original_len,
            'new_len': len(symbols)
        }
        
        self._build_thread = BuildThread(
            font, 
            self.sp_size.value(),
            int(self.cb_bpp.currentText()),
            symbols,
            save_file=True,
            compress=self.cb_compress.isChecked(),
            dedup_info=dedup_info  # 传递去重信息
        )
        self._build_thread.finished.connect(self.on_built)
        self._build_thread.error.connect(self.on_error)
        self._build_thread.start()

    def on_built(self, tmp, save_file):
        try:
            bpp = int(self.cb_bpp.currentText())
            preview_width = self.sp_pw.value()
            self._last_pixmap = parse_glyphs_to_pixmap(tmp, bpp, wrap_width=preview_width)
            
            if save_file:
                # 获取去重后的字符集
                final_symbols = self._build_thread.symbols if self._build_thread else self.le_sym.text()
                
                # 传入去重后的字符集
                out = self.make_header(tmp, self.le_out.text(), final_symbols=final_symbols)
                
                # 获取去重信息
                dedup_info = self._build_thread.dedup_info if self._build_thread else None
                
                # 构建提示消息
                msg_parts = []
                if dedup_info and dedup_info.get('removed', 0) > 0:
                    msg_parts.append(f"已自动去除 {dedup_info['removed']} 个重复字符")
                    msg_parts.append(f"字符数: {dedup_info['original_len']} → {dedup_info['new_len']}")
                    msg_parts.append("")
                
                msg_parts.append(f"字库生成成功！")
                msg_parts.append(f"文件: {os.path.basename(out)}")
                
                # 如果启用了压缩，显示压缩率
                if self.cb_compress.isChecked():
                    try:
                        with open(out, 'r', encoding='utf-8') as f:
                            content = f.read()
                            compress_match = re.search(r'节省空间:\s*([\d.]+)\s*KB\s*\(([\d.]+)%\)', content)
                            if compress_match:
                                saved_kb = compress_match.group(1)
                                saved_percent = compress_match.group(2)
                                msg_parts.append(f"🗜️  压缩节省: {saved_kb} KB ({saved_percent}%)")
                    except:
                        pass
                
                msg = "\n".join(msg_parts)
                
                qmessagebox = QMessageBox(self)
                qmessagebox.setWindowTitle("生成成功")
                qmessagebox.setText(msg)
                qmessagebox.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
        finally:
            # 修改：只删除传入的临时文件
            try:
                if os.path.exists(tmp): 
                    os.remove(tmp)
            except: 
                pass
            self.btn_generate.setEnabled(True)
            self.btn_preview.setEnabled(True)


    def preview(self):
        """预览：生成临时文件用于预览，不保存"""
        font = self.le_font.text().strip()
        if not font or not os.path.exists(font):
            QMessageBox.warning(self, "提示", "请先选择有效的字体文件"); return
        if not check_lv_font_conv():
            QMessageBox.warning(self, "提示", "未找到 lv_font_conv，请在环境检测中安装"); return

        self.save_settings()

        self.btn_generate.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self._last_pixmap = None

        symbols = self.le_sym.text()
        # 字符去重（保持原有顺序）
        deduped_symbols = ''.join(dict.fromkeys(symbols))
        
        # 如果去重后变了，更新输入框并提示用户
        if deduped_symbols != symbols:
            self.le_sym.setText(deduped_symbols)
            QMessageBox.information(self, "提示", 
                f"已自动去除重复字符\n\n"
                f"原字符数: {len(symbols)}\n"
                f"去重后: {len(deduped_symbols)} 个")
            symbols = deduped_symbols
        
        if sys.platform == "win32":
            problematic_chars = set('><|&^')
            removed = [c for c in symbols if c in problematic_chars]
            if removed:
                filtered = ''.join(c for c in symbols if c not in problematic_chars)
                QMessageBox.information(self, "提示", 
                    f"以下字符无法处理，已自动移除：\n{''.join(set(removed))}")
                symbols = filtered
                self.le_sym.setText(filtered)  # 同步更新输入框

        # 预览时始终不压缩（保证预览正常）
        self._build_thread = BuildThread(
            font, 
            self.sp_size.value(),
            int(self.cb_bpp.currentText()),
            symbols,
            save_file=False,
            compress=False
        )
        self._build_thread.finished.connect(self.on_preview_done)
        self._build_thread.error.connect(self.on_preview_error)
        self._build_thread.start()

    def on_preview_done(self, tmp, save_file):
        """预览生成完成"""
        try:
            bpp = int(self.cb_bpp.currentText())
            preview_width = self.sp_pw.value()
            self._last_pixmap = parse_glyphs_to_pixmap(tmp, bpp, wrap_width=preview_width)
            # self.set_status("预览就绪", "ok")
            self.show_preview()
        except Exception as e:
            self.set_status(f"✘  {e}", "err")
            QMessageBox.critical(self, "错误", str(e))
        finally:
            try:
                if os.path.exists(tmp): 
                    os.remove(tmp)
            except: 
                pass
            self.btn_generate.setEnabled(True)
            self.btn_preview.setEnabled(True)

    def on_preview_error(self, msg):
        """预览生成出错"""
        # self.set_status(f"✘  {msg}", "err")
        QMessageBox.critical(self, "预览失败", msg)
        self.btn_generate.setEnabled(True)
        self.btn_preview.setEnabled(True)

    def on_error(self, msg):
        # self.set_status(f"✘  {msg}", "err")
        QMessageBox.critical(self, "生成失败", msg)
        self.btn_generate.setEnabled(True)
        self.btn_preview.setEnabled(True)

    # ─────────────────────────────────────────────
    def show_preview(self):
        if not self._last_pixmap or self._last_pixmap.isNull():
            QMessageBox.information(self, "提示", "暂无预览数据"); return

        w = self.sp_pw.value()
        h = self.sp_ph.value()

        if self._preview_win and self._preview_win.isVisible():
            self._preview_win.close()

        font_name = os.path.splitext(os.path.basename(self.le_font.text()))[0]
        title = f"点阵预览 — {font_name} {self.sp_size.value()}px"

        self._preview_win = PreviewDialog(self._last_pixmap, w, h, title, parent=self)
        self._preview_win.show()

    # ─────────────────────────────────────────────
    def make_header(self, tmp_file, out_dir, final_symbols=None):
        name = os.path.splitext(os.path.basename(self.le_font.text()))[0]
        compress = self.cb_compress.isChecked()
        
        if compress:
            suffix = f"{self.sp_size.value()}px_compressed"
        else:
            suffix = f"{self.sp_size.value()}px"
        
        out = os.path.join(out_dir, f"{name}_{suffix}.h")

        with open(tmp_file, "r", encoding="utf-8") as f:
            content = f.read()

        bm = re.search(r"glyph_bitmap\[\]\s*=\s*\{(.*?)\};", content, re.S)
        dm = re.search(r"glyph_dsc\[\]\s*=\s*\{(.*?)\};",    content, re.S)
        if not bm: raise Exception("未能提取 glyph_bitmap 数据")
        if not dm: raise Exception("未能提取 glyph_dsc 数据")

        # ══════════════════════════════════════════════════════
        #  提取并计算数据
        # ══════════════════════════════════════════════════════
        
        bitmap_hex = bm.group(1)
        bitmap_bytes_list = [int(h, 16) for h in re.findall(r"0x[0-9a-fA-F]+", bitmap_hex)]
        original_bitmap_size = len(bitmap_bytes_list)
        
        dsc_content = dm.group(1)
        char_count = len(re.findall(r"\.bitmap_index\s*=", dsc_content))
        
        DSC_SIZE = 16
        dsc_total = char_count * DSC_SIZE
        
        # 获取生成参数
        font_path = self.le_font.text().strip()
        font_name_str = os.path.basename(font_path)
        font_size_px = self.sp_size.value()
        bpp = int(self.cb_bpp.currentText())
        
        # ══════════════════════════════════════════════════════
        #  从原始 .c 文件提取 line_height 和 base_line
        #  这是计算 ofs_y 对齐偏移的关键参数，不能用 font_size_px 代替
        # ══════════════════════════════════════════════════════
        lh_match = re.search(r"\.line_height\s*=\s*(\d+)", content)
        bl_match = re.search(r"\.base_line\s*=\s*(\d+)", content)
        line_height = int(lh_match.group(1)) if lh_match else font_size_px
        base_line   = int(bl_match.group(1)) if bl_match else 0
        ascent      = line_height - base_line  # 基线以上的像素数（行顶到基线）

        # 使用传入的去重后的字符集，如果没有则从输入框读取
        if final_symbols is None:
            final_symbols = self.le_sym.text()
        
        # lv_font_conv 生成的点阵描述符默认按照 Unicode 升序排列。
        # 必须在这里对去重后的字符进行一次升序排序，才能保证 unicode_list 索引与 glyph_dsc 数据一一对应。
        final_symbols = ''.join(sorted(final_symbols))
        
        # ═══════════════════ 【核心修复点】 ═══════════════════
        # LVGL 生成的 glyph_dsc[0] 默认是空字模/兜底字模（宽高为0）
        # 我们的 unicode_list 必须在索引 0 处强行插入 0x0000 才能与之 1:1 严格对齐
        unicode_list = [0]
        for char in final_symbols:
            unicode_list.append(ord(char))
        # ══════════════════════════════════════════════════════
        
        # 提取 dsc 条目
        dsc_entries = re.findall(
            r"\{\s*\.bitmap_index\s*=\s*\d+.*?\}",
            dsc_content, re.S
        )

        # ══════════════════════════════════════════════════════
        #  压缩模式：重新计算解压后的 bitmap_index
        # ══════════════════════════════════════════════════════
        if compress and bitmap_bytes_list:
            compressed_bytes, compression_ratio = compress_bitmap_rle(bitmap_bytes_list)
            compressed_size = len(compressed_bytes)
            saved_bytes = original_bitmap_size - compressed_size
            saved_percent = (1 - compression_ratio / 100) * 100

            # 重新计算每个字形在解压缓冲区中的偏移
            fixed_dsc_entries = []
            running_offset = 0
            for entry in dsc_entries:
                entry_clean = re.sub(r'\s+', ' ', entry.strip())

                # 替换为正确的解压后偏移
                entry_clean = re.sub(
                    r'\.bitmap_index\s*=\s*\d+',
                    f'.bitmap_index = {running_offset}',
                    entry_clean
                )

                # 提取 box_w / box_h 计算本字形解压后占用字节数
                w_match = re.search(r'\.box_w\s*=\s*(\d+)', entry_clean)
                h_match = re.search(r'\.box_h\s*=\s*(\d+)', entry_clean)
                box_w = int(w_match.group(1)) if w_match else 0
                box_h = int(h_match.group(1)) if h_match else 0

                glyph_bytes = (box_w * box_h * bpp + 7) // 8  # 向上取整，兼容非整字节
                running_offset += glyph_bytes

                fixed_dsc_entries.append(entry_clean)

            # 解压缓冲区真实大小
            real_bitmap_size = running_offset
            flash_total = compressed_size + dsc_total

        else:
            compressed_bytes = None
            compressed_size = 0
            saved_bytes = 0
            saved_percent = 0.0
            fixed_dsc_entries = [re.sub(r'\s+', ' ', e.strip()) for e in dsc_entries]
            real_bitmap_size = original_bitmap_size
            flash_total = original_bitmap_size + dsc_total

        # ══════════════════════════════════════════════════════
        #  将 ofs_y 从 LVGL 坐标系转换为行顶部相对坐标
        #
        #  LVGL 坐标系：ofs_y 以行底部为原点，向上为正
        #               行底部 = 行顶部 + line_height
        #               基线   = 行底部 + base_line（base_line 向上偏移）
        #
        #  目标坐标系：new_ofs_y 以行顶部为原点，向下为正
        #              即字形顶部距行顶部的像素数
        #
        #  推导：
        #    字形顶部（LVGL）= 基线 + ofs_y + box_h  （从基线向上 ofs_y+box_h）
        #    基线距行顶部    = ascent = line_height - base_line
        #    字形顶部距行顶部 = ascent - (ofs_y + box_h) = ascent - ofs_y - box_h
        #
        #  效果：渲染端直接用 draw_y = y + dsc.ofs_y + row，无需任何额外换算
        # ══════════════════════════════════════════════════════
        converted_dsc_entries = []
        for entry in fixed_dsc_entries:
            h_match = re.search(r'\.box_h\s*=\s*(\d+)', entry)
            y_match = re.search(r'\.ofs_y\s*=\s*(-?\d+)', entry)

            if h_match and y_match:
                box_h     = int(h_match.group(1))
                ofs_y     = int(y_match.group(1))
                new_ofs_y = ascent - ofs_y - box_h
                entry = re.sub(r'\.ofs_y\s*=\s*-?\d+', f'.ofs_y = {new_ofs_y}', entry)

            converted_dsc_entries.append(entry)

        fixed_dsc_entries = converted_dsc_entries

        # 格式化函数
        def format_size(size_bytes):
            if size_bytes < 1024:
                return f"{size_bytes} Bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB ({size_bytes} Bytes)"
            else:
                return f"{size_bytes / (1024*1024):.2f} MB ({size_bytes} Bytes)"

        with open(out, "w", encoding="utf-8") as f:
            # ══════════════════════════════════════════════════════
            #  文件头部注释
            # ══════════════════════════════════════════════════════
            f.write("/**\n")
            f.write(" * @file " + os.path.basename(out) + "\n")
            f.write(" * @brief 点阵字库 (LVGL 兼容格式)\n")
            if compress:
                f.write(" * @note  已启用 RLE 压缩\n")
            f.write(" * \n")
            f.write(" * 生成信息:\n")
            f.write(f" * 字体文件:   {font_name_str}\n")
            f.write(f" * 字体大小:   {font_size_px}px\n")
            f.write(f" * 像素深度:   {bpp} BPP\n")
            f.write(f" * 字符数量:   {char_count} 个\n")
            f.write(f" * 字符集:     {final_symbols}\n")
            f.write(f" * 行高:       {line_height}px  (ascent={ascent}, descent={base_line})\n")
            f.write(" * \n")
            f.write(" * Flash 占用估算:\n")
            
            if compress:
                f.write(f" * 原始点阵:   {format_size(original_bitmap_size)}\n")
                f.write(f" * 压缩后:     {format_size(compressed_size)}\n")
                f.write(f" * 节省空间:   {format_size(saved_bytes)} ({saved_percent:.1f}%)\n")
                f.write(f" * 字符描述:   {format_size(dsc_total)} (每个 {DSC_SIZE} Bytes)\n")
                f.write(f" * ─────────────────────────\n")
                f.write(f" * 总计占用:   {format_size(flash_total)}\n")
            else:
                f.write(f" * 点阵数据:   {format_size(original_bitmap_size)}\n")
                f.write(f" * 字符描述:   {format_size(dsc_total)} (每个 {DSC_SIZE} Bytes)\n")
                f.write(f" * ─────────────────────────\n")
                f.write(f" * 总计占用:   {format_size(flash_total)}\n")
            
            f.write(" * \n")
            f.write(" * 说明:\n")
            f.write(" * - 上述大小对应固件中 const 数据段 (.rodata)\n")
            f.write(" * - 实际 Flash 占用可能因编译器对齐优化略有差异 (±2%)\n")
            if compress:
                f.write(" * - 数据已使用 RLE 算法压缩，使用前需调用解压函数\n")
                f.write(" * - 数据解压函数已包含在本文件中，可直接使用\n")
            else:
                f.write(" * - 点阵数据未压缩，如需减小体积可启用压缩选项\n")
            f.write(" * - ofs_y 已转换为行顶部相对值，渲染时直接用 y + ofs_y + row 即可\n")
            f.write(" */\n\n")
            
            f.write("#pragma once\n")
            f.write("#include <stdint.h>\n")
            f.write("#include <string.h>\n\n")
            
            # ══════════════════════════════════════════════════════
            #  字体参数宏定义
            # ══════════════════════════════════════════════════════
            f.write("/** @defgroup font_params 字体参数宏定义 */\n")
            f.write(f"/** @brief 字体像素深度 (Bits Per Pixel) */\n")
            f.write(f"#define FONT_BPP          {bpp}\n\n")
            
            f.write(f"/** @brief 字体大小 (像素) */\n")
            f.write(f"#define FONT_SIZE_PX      {font_size_px}\n\n")
            
            f.write(f"/** @brief 行高 (像素，含上下边距) */\n")
            f.write(f"#define FONT_LINE_HEIGHT  {line_height}\n\n")

            f.write(f"/** @brief 基线以上高度 (行顶到基线的像素数) */\n")
            f.write(f"#define FONT_ASCENT       {ascent}\n\n")

            f.write(f"/** @brief 基线以下高度 (descent) */\n")
            f.write(f"#define FONT_DESCENT      {base_line}\n\n")

            f.write(f"/** @brief 字符数量 */\n")
            f.write(f"#define FONT_CHAR_COUNT   {char_count}\n\n")
            
            if compress:
                f.write(f"/** @brief 点阵数据原始大小 (解压后字节数) */\n")
                f.write(f"#define FONT_BITMAP_SIZE  {real_bitmap_size}\n\n")
                
                f.write(f"/** @brief 压缩数据大小 (字节) */\n")
                f.write(f"#define FONT_COMPRESSED_SIZE {compressed_size}\n\n")
            else:
                f.write(f"/** @brief 点阵数据大小 (字节) */\n")
                f.write(f"#define FONT_BITMAP_SIZE  {original_bitmap_size}\n\n")
            
            # 像素掩码和移位宏
            ppb = 8 // bpp
            pixel_mask = (1 << bpp) - 1
            
            f.write(f"/** @brief 每字节像素数 */\n")
            f.write(f"#define FONT_PIXELS_PER_BYTE {ppb}\n\n")
            
            f.write(f"/** @brief 像素值掩码 */\n")
            f.write(f"#define FONT_PIXEL_MASK      0x{pixel_mask:02X}\n\n")
            
            if bpp == 1:
                f.write("/** @brief 提取像素值 (BPP=1) */\n")
                f.write("#define FONT_GET_PIXEL(byte, pos) (((byte) >> (7 - (pos))) & 0x01)\n\n")
            elif bpp == 2:
                f.write("/** @brief 提取像素值 (BPP=2) */\n")
                f.write("#define FONT_GET_PIXEL(byte, pos) (((byte) >> (6 - (pos) * 2)) & 0x03)\n\n")
            elif bpp == 4:
                f.write("/** @brief 提取像素值 (BPP=4) */\n")
                f.write("#define FONT_GET_PIXEL(byte, pos) (((byte) >> (4 - (pos) * 4)) & 0x0F)\n\n")
            elif bpp == 8:
                f.write("/** @brief 提取像素值 (BPP=8) */\n")
                f.write("#define FONT_GET_PIXEL(byte, pos) (byte)\n\n")
            
            # ══════════════════════════════════════════════════════
            #  Unicode 字符编码数组
            # ══════════════════════════════════════════════════════
            f.write("/** @brief Unicode 字符编码数组 (与 glyph_dsc 索引对应) */\n")
            f.write(f"static const uint32_t unicode_list[{char_count}] = {{\n")
            for i in range(0, len(unicode_list), 8):
                line = ", ".join(f"0x{code:04X}" for code in unicode_list[i:i+8])
                if i + 8 < len(unicode_list):
                    f.write(f"    {line},\n")
                else:
                    f.write(f"    {line}\n")
            f.write("};\n\n")
            
            # 字符描述符结构体
            f.write("/**\n")
            f.write(" * @brief 字符描述符结构体\n")
            f.write(" * @note  ofs_y 为行顶部相对值（向下为正），渲染时直接用 y + ofs_y + row\n")
            f.write(" */\n")
            f.write("typedef struct {\n"
                    "    uint32_t bitmap_index;  /**< 点阵数据索引 */\n"
                    "    uint32_t adv_w;         /**< 字符宽度 + 间距 */\n"
                    "    uint16_t box_w;         /**< 点阵宽度 */\n"
                    "    uint16_t box_h;         /**< 点阵高度 */\n"
                    "    int16_t  ofs_x;         /**< X 轴偏移 */\n"
                    "    int16_t  ofs_y;         /**< Y 轴偏移 (行顶部相对值，向下为正) */\n"
                    "} GlyphDsc;\n\n")
            
            # ══════════════════════════════════════════════════════
            #  点阵数据
            # ══════════════════════════════════════════════════════
            if compress:
                # RLE 解压缩函数
                f.write("/**\n")
                f.write(" * @brief RLE 解压缩点阵数据\n")
                f.write(" * @param src  压缩数据源\n")
                f.write(" * @param dst  解压后数据缓冲区（需预先分配足够空间）\n")
                f.write(" * @return     解压后的字节数\n")
                f.write(" */\n")
                f.write("static inline uint32_t glyph_decompress(const uint8_t *src, uint8_t *dst) {\n")
                f.write("    uint32_t out_idx = 0;\n")
                f.write("    uint32_t in_idx = 0;\n")
                f.write("    \n")
                f.write("    while (1) {\n")
                f.write("        uint8_t cmd = src[in_idx++];\n")
                f.write("        \n")
                f.write("        if (cmd == 0x00) break;  // 结束标记\n")
                f.write("        \n")
                f.write("        if (cmd & 0x80) {\n")
                f.write("            // 不重复字节序列\n")
                f.write("            uint8_t len = cmd & 0x7F;\n")
                f.write("            memcpy(&dst[out_idx], &src[in_idx], len);\n")
                f.write("            out_idx += len;\n")
                f.write("            in_idx += len;\n")
                f.write("        } else {\n")
                f.write("            // 重复字节\n")
                f.write("            uint8_t byte_val = src[in_idx++];\n")
                f.write("            memset(&dst[out_idx], byte_val, cmd);\n")
                f.write("            out_idx += cmd;\n")
                f.write("        }\n")
                f.write("    }\n")
                f.write("    \n")
                f.write("    return out_idx;\n")
                f.write("}\n\n")
                
                # 压缩数据
                f.write(f"/** @brief RLE 压缩点阵数据 ({compressed_size} Bytes, 原始 {original_bitmap_size} Bytes) */\n")
                f.write(f"static const uint8_t glyph_bitmap_compressed[{compressed_size}] = {{\n")
                for i in range(0, len(compressed_bytes), 16):
                    line = ", ".join(f"0x{b:02X}" for b in compressed_bytes[i:i+16])
                    if i + 16 < len(compressed_bytes):
                        f.write(f"    {line},\n")
                    else:
                        f.write(f"    {line}\n")
                f.write("};\n\n")
                
            else:
                # 未压缩数据
                f.write(f"/** @brief 点阵数据 ({original_bitmap_size} Bytes) */\n")
                f.write(f"static const uint8_t glyph_bitmap[{original_bitmap_size}] = {{\n")
                hex_values = re.findall(r"0x[0-9a-fA-F]+", bitmap_hex)
                for i in range(0, len(hex_values), 16):
                    line = ", ".join(hex_values[i:i+16])
                    if i + 16 < len(hex_values):
                        f.write(f"    {line},\n")
                    else:
                        f.write(f"    {line}\n")
                f.write("};\n\n")
            
            # ══════════════════════════════════════════════════════
            #  字符描述符数组（ofs_y 已转换为行顶部相对值）
            # ══════════════════════════════════════════════════════
            f.write(f"/** @brief 字符描述符数组 ({char_count} 个字符，ofs_y 已转换为行顶部相对值) */\n")
            f.write(f"static const GlyphDsc glyph_dsc[{char_count}] = {{\n")
            for i, entry_clean in enumerate(fixed_dsc_entries):
                comma = "," if i < len(fixed_dsc_entries) - 1 else ""
                f.write(f"    {entry_clean}{comma}\n")
            f.write("};\n\n")
            
            # ══════════════════════════════════════════════════════
            #  辅助查找函数
            # ══════════════════════════════════════════════════════
            f.write("/**\n")
            f.write(" * @brief 根据 Unicode 字符查找字形索引\n")
            f.write(" * @param unicode Unicode 字符编码\n")
            f.write(" * @return 字形索引，未找到返回 -1\n")
            f.write(" */\n")
            f.write("static inline int16_t font_find_char(uint32_t unicode) {\n")
            f.write("    for (int16_t i = 0; i < FONT_CHAR_COUNT; i++) {\n")
            f.write("        if (unicode_list[i] == unicode) {\n")
            f.write("            return i;\n")
            f.write("        }\n")
            f.write("    }\n")
            f.write("    return -1;\n")
            f.write("}\n\n")
            
            # ══════════════════════════════════════════════════════
            #  使用示例
            # ══════════════════════════════════════════════════════
            if compress:
                f.write("/**\n")
                f.write(" * @brief 使用示例（固件端）\n")
                f.write(" * \n")
                f.write(" * // 1. 分配解压缓冲区（可复用）\n")
                f.write(" * static uint8_t glyph_buffer[FONT_BITMAP_SIZE];\n")
                f.write(" * \n")
                f.write(" * // 2. 初始化时解压一次\n")
                f.write(" * void font_init(void) {\n")
                f.write(" *     glyph_decompress(glyph_bitmap_compressed, glyph_buffer);\n")
                f.write(" * }\n")
                f.write(" * \n")
                f.write(" * // 3. 渲染时使用\n")
                f.write(" * //    x, y 为行顶部左上角坐标\n")
                f.write(" * //    ofs_y 已是行顶部相对值，直接相加即可，无需基线换算\n")
                f.write(" * void draw_char(uint32_t unicode, int x, int y) {\n")
                f.write(" *     int16_t idx = font_find_char(unicode);\n")
                f.write(" *     if (idx < 0) return;\n")
                f.write(" * \n")
                f.write(" *     const GlyphDsc *dsc = &glyph_dsc[idx];\n")
                f.write(" *     const uint8_t *bitmap = &glyph_buffer[dsc->bitmap_index];\n")
                f.write(" * \n")
                f.write(" *     for (int row = 0; row < dsc->box_h; row++) {\n")
                f.write(" *         for (int col = 0; col < dsc->box_w; col++) {\n")
                f.write(" *             int pixel_idx = row * dsc->box_w + col;\n")
                f.write(" *             int byte_idx  = pixel_idx / FONT_PIXELS_PER_BYTE;\n")
                f.write(" *             int bit_pos   = pixel_idx % FONT_PIXELS_PER_BYTE;\n")
                f.write(" *             uint8_t pixel = FONT_GET_PIXEL(bitmap[byte_idx], bit_pos);\n")
                f.write(" *             if (pixel > 0) {\n")
                f.write(" *                 draw_pixel(x + dsc->ofs_x + col,\n")
                f.write(" *                            y + dsc->ofs_y + row, pixel);\n")
                f.write(" *             }\n")
                f.write(" *         }\n")
                f.write(" *     }\n")
                f.write(" * }\n")
                f.write(" */\n")
            else:
                f.write("/**\n")
                f.write(" * @brief 使用示例（固件端）\n")
                f.write(" * \n")
                f.write(" * //    x, y 为行顶部左上角坐标\n")
                f.write(" * //    ofs_y 已是行顶部相对值，直接相加即可，无需基线换算\n")
                f.write(" * void draw_char(uint32_t unicode, int x, int y) {\n")
                f.write(" *     int16_t idx = font_find_char(unicode);\n")
                f.write(" *     if (idx < 0) return;\n")
                f.write(" * \n")
                f.write(" *     const GlyphDsc *dsc = &glyph_dsc[idx];\n")
                f.write(" *     const uint8_t *bitmap = &glyph_bitmap[dsc->bitmap_index];\n")
                f.write(" * \n")
                f.write(" *     for (int row = 0; row < dsc->box_h; row++) {\n")
                f.write(" *         for (int col = 0; col < dsc->box_w; col++) {\n")
                f.write(" *             int pixel_idx = row * dsc->box_w + col;\n")
                f.write(" *             int byte_idx  = pixel_idx / FONT_PIXELS_PER_BYTE;\n")
                f.write(" *             int bit_pos   = pixel_idx % FONT_PIXELS_PER_BYTE;\n")
                f.write(" *             uint8_t pixel = FONT_GET_PIXEL(bitmap[byte_idx], bit_pos);\n")
                f.write(" *             if (pixel > 0) {\n")
                f.write(" *                 draw_pixel(x + dsc->ofs_x + col,\n")
                f.write(" *                            y + dsc->ofs_y + row, pixel);\n")
                f.write(" *             }\n")
                f.write(" *         }\n")
                f.write(" *     }\n")
                f.write(" * }\n")
                f.write(" */\n")
        
        return out

# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    win = FontTool()
    win.show()
    sys.exit(app.exec_())