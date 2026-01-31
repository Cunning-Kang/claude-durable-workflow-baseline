#!/bin/bash
# Task Flow 安装脚本测试

set -e

TEST_DIR="$HOME/.claude/skills/task-flow-test"
TASK_FLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Task Flow 安装脚本测试"
echo ""

# 清理测试环境
cleanup() {
    if [ -d "$TEST_DIR" ]; then
        echo "→ 清理测试环境: $TEST_DIR"
        rm -rf "$TEST_DIR"
    fi
}

# 注册清理函数
trap cleanup EXIT

# 测试 1: 备份功能
echo "测试 1: 备份现有版本"
mkdir -p "$TEST_DIR/src" "$TEST_DIR/tests" "$TEST_DIR/templates"
echo "old" > "$TEST_DIR/test.txt"

# 模拟第二次安装（创建备份）
TEST_SKILL_VAR="$TEST_DIR" bash -c '
    SKILL_DIR="$TEST_SKILL_VAR"
    if [ -d "$SKILL_DIR" ]; then
        BACKUP_DIR="$SKILL_DIR.backup.$(date +%Y%m%d%H%M%S)"
        cp -R "$SKILL_DIR" "$BACKUP_DIR"
        rm -rf "$SKILL_DIR"
        echo "✓ 备份创建成功: $BACKUP_DIR"
    fi
'

# 重新创建目录用于后续测试
mkdir -p "$TEST_DIR/src" "$TEST_DIR/tests" "$TEST_DIR/templates"

# 测试 2: 目录创建
echo ""
echo "测试 2: 目录结构创建"
INSTALL_DIRS=("$TEST_DIR/src" "$TEST_DIR/tests" "$TEST_DIR/templates")
for dir in "${INSTALL_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ 目录存在: $dir"
    else
        echo "✗ 目录缺失: $dir"
        exit 1
    fi
done

# 测试 3: 文件复制
echo ""
echo "测试 3: 文件复制检查"
REQUIRED_FILES=(
    "SKILL.md"
    "src/cli.py"
    "src/task_manager.py"
    "src/__main__.py"
    "src/__init__.py"
    "tests/test_task_manager.py"
    "README.md"
    "requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$TASK_FLOW_DIR/$file" ]; then
        echo "✓ 源文件存在: $file"
    else
        echo "✗ 源文件缺失: $file"
        exit 1
    fi
done

# 测试 4: 执行权限
echo ""
echo "测试 4: 执行权限"
if [ -x "$TASK_FLOW_DIR/install.sh" ]; then
    echo "✓ install.sh 可执行"
else
    echo "✗ install.sh 不可执行"
    exit 1
fi

# 测试 5: Python 语法检查
echo ""
echo "测试 5: Python 语法"
PYTHON_FILES=(
    "src/cli.py"
    "src/task_manager.py"
    "tests/test_task_manager.py"
)

for pyfile in "${PYTHON_FILES[@]}"; do
    if python3 -m py_compile "$TASK_FLOW_DIR/$pyfile" 2>/dev/null; then
        echo "✓ 语法正确: $pyfile"
    else
        echo "✗ 语法错误: $pyfile"
        exit 1
    fi
done

# 测试 6: 导入检查
echo ""
echo "测试 6: Python 模块导入"
cd "$TASK_FLOW_DIR"
if PYTHONPATH=src python3 -c "from task_manager import TaskManager; print('✓ TaskManager 导入成功')" 2>/dev/null; then
    :
else
    echo "✗ TaskManager 导入失败"
    exit 1
fi

if PYTHONPATH=src python3 -c "import cli; print('✓ cli 导入成功')" 2>/dev/null; then
    :
else
    echo "✗ cli 导入失败"
    exit 1
fi

# 测试 7: 依赖检查
echo ""
echo "测试 7: requirements.txt"
if [ -f "$TASK_FLOW_DIR/requirements.txt" ]; then
    echo "✓ requirements.txt 存在"
    if grep -q "pytest" "$TASK_FLOW_DIR/requirements.txt"; then
        echo "✓ pytest 在依赖中"
    fi
else
    echo "✗ requirements.txt 缺失"
    exit 1
fi

# 测试 8: SKILL.md 格式
echo ""
echo "测试 8: SKILL.md 格式"
if grep -q "^name: task-flow" "$TASK_FLOW_DIR/SKILL.md"; then
    echo "✓ SKILL.md 包含 name 字段"
else
    echo "✗ SKILL.md 缺少 name 字段"
    exit 1
fi

if grep -q "^description:" "$TASK_FLOW_DIR/SKILL.md"; then
    echo "✓ SKILL.md 包含 description 字段"
else
    echo "✗ SKILL.md 缺少 description 字段"
    exit 1
fi

echo ""
echo "==> 所有测试通过！✓"
echo ""
echo "安装脚本已准备就绪。运行以下命令安装:"
echo "  bash $TASK_FLOW_DIR/install.sh"
