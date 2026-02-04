"""Template Loader for Task Flow

Loads template files from the templates/ directory with caching.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

from packaging.version import Version

from .exceptions import TemplateNotFoundError


class TemplateLoader:
    """从 templates/ 目录加载内置模板（带缓存）"""

    # 预编译的正则模式
    _VERSION_PLACEHOLDER_PATTERN = re.compile(r'\{VERSION\}')
    _FILENAME_VERSION_PATTERN = re.compile(r'\{VERSION(?::[^}]+)?\}')

    def __init__(self, skill_dir: Optional[Path] = None) -> None:
        """初始化模板加载器

        Args:
            skill_dir: task-flow 技能目录路径，默认自动检测
        """
        self._skill_dir = skill_dir
        self._template_dir: Optional[Path] = None

    @property
    def template_dir(self) -> Path:
        """延迟加载模板目录路径"""
        if self._template_dir is None:
            self._template_dir = self._get_template_dir(self._skill_dir)
        return self._template_dir

    def _get_template_dir(self, skill_dir: Optional[Path] = None) -> Path:
        """获取模板目录路径

        Args:
            skill_dir: 技能目录路径

        Returns:
            模板目录的完整路径
        """
        if skill_dir is None:
            # 从当前文件向上查找技能目录
            current_file = Path(__file__).resolve()
            skill_dir = current_file.parent.parent.parent

        template_dir = skill_dir / "templates"
        if not template_dir.exists():
            raise FileNotFoundError(
                f"Template directory not found: {template_dir}\n"
                f"Please ensure task-flow is properly installed."
            )
        return template_dir

    @lru_cache(maxsize=32)
    def load_template(self, template_type: str = "standard") -> str:
        """加载指定类型的模板（带缓存）

        Args:
            template_type: 模板类型 (minimal/standard/full/section_template)

        Returns:
            模板内容字符串

        Raises:
            TemplateNotFoundError: 模板文件不存在
        """
        template_file = self.template_dir / f"{template_type}.md"
        if not template_file.exists():
            available = self._list_available_templates()
            raise TemplateNotFoundError(
                template_name=template_type,
                template_dir=str(self.template_dir),
                available=available,
            )
        return template_file.read_text(encoding="utf-8")

    def get_section_template(self) -> str:
        """获取用于嵌入的章节模板

        Returns:
            章节模板内容
        """
        return self.load_template("section_template")

    def _list_available_templates(self) -> list[str]:
        """列出所有可用的模板

        Returns:
            模板名称列表（不含 .md 扩展名），排序
        """
        try:
            templates = [
                f.stem for f in self.template_dir.glob("*.md")
                if not f.name.startswith("_")
            ]
            return sorted(templates)
        except (FileNotFoundError, OSError):
            return []

    def template_exists(self, template_type: str) -> bool:
        """检查模板是否存在

        Args:
            template_type: 模板类型

        Returns:
            模板是否存在
        """
        try:
            return (self.template_dir / f"{template_type}.md").exists()
        except (FileNotFoundError, OSError):
            return False

    def invalidate_cache(self) -> None:
        """清除模板缓存"""
        self.load_template.cache_clear()

    def get_available_templates(self) -> list[str]:
        """获取所有可用模板列表

        Returns:
            可用模板名称列表
        """
        return self._list_available_templates()
