#!/bin/bash
# Plan Packet Skill 迁移脚本
# 将旧的 plan-packet 结构迁移到新的标准结构

set -euo pipefail

SKILL_DIR="$HOME/.claude/skills/plan-packet"
REFACTOR_DIR="/Users/cunning/Workspaces/heavy/skills-creation/plan-packet-refactor"

echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  Plan Packet Skill 迁移工具                                 │"
echo "├─────────────────────────────────────────────────────────────┤"
echo ""

# 检查目录是否存在
if [[ ! -d "$SKILL_DIR" ]]; then
    echo "❌ 错误: plan-packet skill 目录不存在"
    echo "   路径: $SKILL_DIR"
    exit 1
fi

cd "$SKILL_DIR" || exit 1

echo "📍 当前目录: $SKILL_DIR"
echo ""

# 1. 删除无用文件
echo "🗑️  删除无用文件..."
rm -f ANALYSIS.md TEST-REPORT.md AGENTS-MD-SUPPORT-TEST-REPORT.md
rm -f test-agents-md-support.py watch-task-files.py wt-integration.sh
rm -f skill.md
echo "   ✓ 已删除开发文档和旧脚本"
echo ""

# 2. 创建目录
echo "📁 创建标准目录结构..."
mkdir -p templates scripts
echo "   ✓ 已创建 templates/ 和 scripts/"
echo ""

# 3. 移动现有文件
echo "📦 整理现有文件..."
[[ -f claude-md-fragment.md ]] && mv claude-md-fragment.md templates/ 2>/dev/null && echo "   ✓ 移动 claude-md-fragment.md → templates/"
[[ -f plan-packet-template.md ]] && mv plan-packet-template.md templates/ 2>/dev/null && echo "   ✓ 移动 plan-packet-template.md → templates/"
[[ -f merge-claude-md.py ]] && mv merge-claude-md.py scripts/ 2>/dev/null && echo "   ✓ 移动 merge-claude-md.py → scripts/"
echo ""

# 4. 复制新文件
echo "📄 复制新文件..."
if [[ -f "$REFACTOR_DIR/SKILL.md" ]]; then
    cp "$REFACTOR_DIR/SKILL.md" .
    echo "   ✓ 已复制 SKILL.md"
fi

if [[ -f "$REFACTOR_DIR/scripts/plan-packet.py" ]]; then
    cp "$REFACTOR_DIR/scripts/plan-packet.py" scripts/
    echo "   ✓ 已复制 scripts/plan-packet.py"
fi

# 复制模板文件（如果不存在或需要更新）
if [[ -f "$REFACTOR_DIR/templates/claude-md-fragment.md" ]]; then
    cp "$REFACTOR_DIR/templates/claude-md-fragment.md" templates/
    echo "   ✓ 已更新 templates/claude-md-fragment.md"
fi

if [[ -f "$REFACTOR_DIR/templates/plan-packet-template.md" ]]; then
    cp "$REFACTOR_DIR/templates/plan-packet-template.md" templates/
    echo "   ✓ 已更新 templates/plan-packet-template.md"
fi
echo ""

# 5. 显示结果
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  ✅ 迁移完成！                                               │"
echo "├─────────────────────────────────────────────────────────────┤"
echo "│                                                             │"
echo "│  新的目录结构：                                              │"
echo ""
ls -la "$SKILL_DIR" | grep -v "^total" | grep -v "^d" | tail -n +4 | while read -r line; do
    printf "│  %s│\n" "$line"
done
echo ""
echo "│  templates/                                                 │"
echo "│  ├── claude-md-fragment.md                                  │"
echo "│  └── plan-packet-template.md                                │"
echo "│                                                             │"
echo "│  scripts/                                                   │"
echo "│  ├── plan-packet.py                                         │"
echo "│  └── merge-claude-md.py                                     │"
echo "│                                                             │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""
echo "现在你可以在 Claude Code 中使用 plan-packet skill 了！"
