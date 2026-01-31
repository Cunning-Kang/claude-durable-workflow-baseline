#!/bin/bash
# Plan Packet v2.1 一键安装脚本
#
# 使用方法:
#   bash /path/to/plan-packet-refactor/install.sh

set -e

SKILL_DIR="$HOME/.claude/skills/plan-packet"
REFACTOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Plan Packet v2.1 安装脚本"
echo ""

# 1. 备份现有版本
if [ -d "$SKILL_DIR" ]; then
    BACKUP_DIR="$SKILL_DIR.backup.$(date +%Y%m%d%H%M%S)"
    echo "→ 备份现有版本到: $BACKUP_DIR"
    cp -R "$SKILL_DIR" "$BACKUP_DIR"
    rm -rf "$SKILL_DIR"
fi

# 2. 创建新目录
echo "→ 创建 skill 目录: $SKILL_DIR"
mkdir -p "$SKILL_DIR"
mkdir -p "$SKILL_DIR/scripts"
mkdir -p "$SKILL_DIR/templates"

# 3. 复制文件
echo "→ 复制 SKILL.md"
cp "$REFACTOR_DIR/SKILL.md" "$SKILL_DIR/"

echo "→ 复制脚本"
cp "$REFACTOR_DIR/scripts/plan-packet.py" "$SKILL_DIR/scripts/"
if [ -f "$REFACTOR_DIR/scripts/merge-claude-md.py" ]; then
    cp "$REFACTOR_DIR/scripts/merge-claude-md.py" "$SKILL_DIR/scripts/"
fi

echo "→ 复制模板"
cp "$REFACTOR_DIR/templates/claude-md-fragment.md" "$SKILL_DIR/templates/"
cp "$REFACTOR_DIR/templates/plan-packet-template.md" "$SKILL_DIR/templates/"

# 4. 设置执行权限
chmod +x "$SKILL_DIR/scripts/plan-packet.py"
if [ -f "$SKILL_DIR/scripts/merge-claude-md.py" ]; then
    chmod +x "$SKILL_DIR/scripts/merge-claude-md.py"
fi

echo ""
echo "✓ 安装完成！"
echo ""
echo "文件结构:"
ls -la "$SKILL_DIR"
echo ""
echo "测试脚本:"
python3 "$SKILL_DIR/scripts/plan-packet.py" --help
echo ""
echo "==> 安装成功！现在可以在 Claude Code 中使用 plan-packet skill"
