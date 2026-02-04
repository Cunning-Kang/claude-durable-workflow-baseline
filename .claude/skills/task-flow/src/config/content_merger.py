"""Content Merger for Task Flow

Intelligently merges content with existing files using configurable strategies.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from packaging.version import Version, InvalidVersion


class MergeStrategy(Enum):
    """内容合并策略"""
    REPLACE = "replace"  # 替换现有内容
    APPEND = "append"    # 追加到末尾
    INSERT = "insert"    # 智能插入
    MERGE = "merge"      # 合并内容


class ContentMerger:
    """智能内容合并：决定插入/更新位置"""

    # 预编译的正则模式
    WORKFLOW_PATTERNS = [
        re.compile(r'^#{1,2}\s*(工作流|流程|指南|使用指南|workflow)', re.IGNORECASE),
        re.compile(r'^#{1,2}\s*(quick\s+start|快速开始)', re.IGNORECASE),
        re.compile(r'^#{1,2}\s*(开发流程|development)', re.IGNORECASE),
        re.compile(r'^#{1,2}\s*(task\s+flow|任务流)', re.IGNORECASE),
    ]

    VERSION_PATTERN = re.compile(r'<!-- TASK-FLOW-VERSION:([0-9.]+\.[0-9]+.*?)(?= -->)')
    SECTION_PATTERN = re.compile(
        r'<!-- TASK-FLOW-VERSION:[0-9.]+\.[0-9]+.*? -->.*?<!-- END-TASK-FLOW-SECTION -->',
        re.DOTALL
    )

    # 受保护的键，不能被覆盖
    _PROTECTED_KEYS: set[str] = {"VERSION", "DATE", "YEAR"}

    def __init__(self, strategy: MergeStrategy = MergeStrategy.MERGE) -> None:
        """初始化内容合并器

        Args:
            strategy: 合并策略
        """
        self._strategy = strategy

    def find_insertion_point(self, content: str) -> int:
        """查找最佳插入位置（字符索引）

        策略：
        1. 查找工作流相关章节前
        2. 文件末尾

        Args:
            content: 现有文件内容

        Returns:
            插入位置的字符索引
        """
        lines = content.split('\n')

        # 策略 1: 查找工作流相关章节前
        for i, line in enumerate(lines):
            if self._is_workflow_heading(line):
                return sum(len(l) + 1 for l in lines[:i])

        # 策略 2: 文件末尾
        return len(content)

    def _is_workflow_heading(self, line: str) -> bool:
        """检测是否为工作流相关章节标题

        Args:
            line: 行内容

        Returns:
            是否为工作流章节标题
        """
        stripped = line.strip()
        return any(pattern.match(stripped) for pattern in self.WORKFLOW_PATTERNS)

    def merge_content(
        self,
        existing: str,
        new_section: str,
        version: str
    ) -> str:
        """合并内容：替换或追加

        Args:
            existing: 现有文件内容
            new_section: 新的内容块（带版本标记）
            version: 新版本号

        Returns:
            合并后的内容
        """
        # 检查是否存在现有 task-flow 内容
        if self.SECTION_PATTERN.search(existing):
            # 替换现有内容
            return self.SECTION_PATTERN.sub(
                new_section,
                existing
            )
        else:
            # 追加新内容
            insertion_point = self.find_insertion_point(existing)

            # 确保插入位置前后有合适的换行
            prefix = existing[:insertion_point].rstrip()
            suffix = existing[insertion_point:].lstrip()

            return (
                prefix +
                "\n\n" +
                new_section.strip() +
                "\n\n" +
                suffix
            )

    def detect_existing_version(self, content: str) -> Optional[str]:
        """检测现有 task-flow 内容的版本

        Args:
            content: 文件内容

        Returns:
            版本号，如果不存在则返回 None
        """
        match = self.VERSION_PATTERN.search(content)
        return match.group(1) if match else None

    def needs_update(self, existing: str, current_version: str) -> bool:
        """判断是否需要更新

        Args:
            existing: 现有文件内容
            current_version: 当前版本号

        Returns:
            是否需要更新
        """
        existing_version = self.detect_existing_version(existing)
        if not existing_version:
            return True  # 无现有内容，需要添加

        try:
            return Version(existing_version) < Version(current_version)
        except InvalidVersion:
            # 版本号格式错误，保守起见返回 True
            return True

    def has_taskflow_section(self, content: str) -> bool:
        """检查文件是否已包含 task-flow 章节

        Args:
            content: 文件内容

        Returns:
            是否包含 task-flow 章节
        """
        return bool(self.SECTION_PATTERN.search(content))

    def extract_taskflow_section(self, content: str) -> Optional[str]:
        """提取现有的 task-flow 章节

        Args:
            content: 文件内容

        Returns:
            task-flow 章节内容，如果不存在则返回 None
        """
        match = self.SECTION_PATTERN.search(content)
        return match.group(0) if match else None

    def compare_versions(self, v1: str, v2: str) -> int:
        """比较两个版本号

        Args:
            v1: 版本号 1
            v2: 版本号 2

        Returns:
            -1 如果 v1 < v2
            0 如果 v1 == v2
            1 如果 v1 > v2
        """
        try:
            version1 = Version(v1)
            version2 = Version(v2)
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            else:
                return 0
        except InvalidVersion:
            # 如果版本号格式错误，使用字符串比较作为后备
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
