"""Project Configuration Manager for Task Flow

Manages project configuration file initialization and updates.
"""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from packaging.version import Version, InvalidVersion

from .template_loader import TemplateLoader
from .content_merger import ContentMerger
from .template_renderer import TemplateRenderer
from .exceptions import ConfigError, FileWriteError, TemplateNotFoundError


class CIConfig(Enum):
    """CI 环境类型"""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    TRAVIS_CI = "travis_ci"
    CIRCLE_CI = "circle_ci"
    APPVEYOR = "appveyor"
    BITBUCKET = "bitbucket"
    AZURE_DEVOPS = "azure_devops"
    UNKNOWN = "unknown"


@dataclass
class ConfigMetadata:
    """配置元数据"""
    initialized: bool = False
    config_file: Optional[str] = None
    existing_version: Optional[str] = None
    current_version: str = "2.3.0"
    needs_update: bool = False
    is_ci: bool = False
    ci_type: CIConfig = CIConfig.UNKNOWN
    last_updated: Optional[str] = None


@dataclass
class InitResult:
    """初始化结果"""
    success: bool
    config_file: Optional[str] = None
    backup_file: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    metadata: ConfigMetadata = field(default_factory=ConfigMetadata)


class ConfigManager:
    """项目配置管理器：负责检测、更新 CLAUDE.md/AGENTS.md"""

    # 标记文件和版本标记
    INIT_MARKER = ".task-flow-initialized"
    VERSION_FILE = ".task-flow-version"
    CURRENT_VERSION = "2.3.0"

    # 版本标记格式
    VERSION_MARKER = "<!-- TASK-FLOW-VERSION:{} -->"
    SECTION_START = "<!-- TASK-FLOW-SECTION -->"
    SECTION_END = "<!-- END-TASK-FLOW-SECTION -->"

    # 预编译的 CI 环境检测模式
    _CI_PATTERNS = [
        re.compile(r'github_actions', re.IGNORECASE),
        re.compile(r'gitlab_ci', re.IGNORECASE),
        re.compile(r'jenkins_home', re.IGNORECASE),
        re.compile(r'travis', re.IGNORECASE),
        re.compile(r'circle_ci', re.IGNORECASE),
        re.compile(r'appveyor', re.IGNORECASE),
        re.compile(r'bitbucket_build_number', re.IGNORECASE),
        re.compile(r'tf_build', re.IGNORECASE),
        re.compile(r'codebuild_build_id', re.IGNORECASE),
    ]

    # CI 环境变量指示器（去重）
    _CI_INDICATORS = [
        'CI', 'CONTINUOUS_INTEGRATION',
        'GITHUB_ACTIONS', 'GITLAB_CI',
        'JENKINS_HOME', 'TRAVIS',
        'CIRCLECI', 'APPVEYOR',
        'BITBUCKET_BUILD_NUMBER',
        'TF_BUILD', 'CI_NAME', 'CODEBUILD_BUILD_ID',
        'AZURE_PIPELINE_ID',
    ]

    def __init__(self, project_root: Path) -> None:
        """初始化配置管理器

        Args:
            project_root: 项目根目录路径
        """
        self._project_root = Path(project_root).resolve()
        self._config_file: Optional[Path] = None
        self._template_loader: Optional[TemplateLoader] = None
        self._content_merger: Optional[ContentMerger] = None
        self._template_renderer: Optional[TemplateRenderer] = None

    @property
    def project_root(self) -> Path:
        """项目根目录"""
        return self._project_root

    @property
    def config_file(self) -> Optional[Path]:
        """配置文件路径（延迟查找）"""
        if self._config_file is None:
            self._config_file = self._find_config_file()
        return self._config_file

    @property
    def template_loader(self) -> TemplateLoader:
        """模板加载器（延迟初始化）"""
        if self._template_loader is None:
            self._template_loader = TemplateLoader()
        return self._template_loader

    @property
    def content_merger(self) -> ContentMerger:
        """内容合并器（延迟初始化）"""
        if self._content_merger is None:
            self._content_merger = ContentMerger()
        return self._content_merger

    @property
    def template_renderer(self) -> TemplateRenderer:
        """模板渲染器（延迟初始化）"""
        if self._template_renderer is None:
            self._template_renderer = TemplateRenderer()
        return self._template_renderer

    def _find_config_file(self) -> Optional[Path]:
        """查找配置文件：优先 CLAUDE.md，其次 AGENTS.md

        Returns:
            配置文件路径，如果都不存在则返回 None
        """
        for filename in ["CLAUDE.md", "AGENTS.md"]:
            path = self._project_root / filename
            if path.exists():
                return path
        return None

    @classmethod
    def is_initialized(cls, project_root: Path) -> bool:
        """快速检测是否已初始化

        Args:
            project_root: 项目根目录路径

        Returns:
            是否已初始化
        """
        return (project_root / cls.INIT_MARKER).exists()

    @classmethod
    def is_ci_environment(cls) -> bool:
        """检测是否在 CI 环境中

        Returns:
            是否在 CI 环境
        """
        return any(os.environ.get(key) for key in cls._CI_INDICATORS)

    @classmethod
    def detect_ci_type(cls) -> CIConfig:
        """检测 CI 环境类型

        Returns:
            CI 环境类型
        """
        env_str = " ".join(f"{k}={v}" for k, v in os.environ.items())

        for pattern, ci_type in [
            (cls._CI_PATTERNS[0], CIConfig.GITHUB_ACTIONS),
            (cls._CI_PATTERNS[1], CIConfig.GITLAB_CI),
            (cls._CI_PATTERNS[2], CIConfig.JENKINS),
            (cls._CI_PATTERNS[3], CIConfig.TRAVIS_CI),
            (cls._CI_PATTERNS[4], CIConfig.CIRCLE_CI),
            (cls._CI_PATTERNS[5], CIConfig.APPVEYOR),
            (cls._CI_PATTERNS[6], CIConfig.BITBUCKET),
            (cls._CI_PATTERNS[8], CIConfig.AZURE_DEVOPS),
        ]:
            if pattern.search(env_str):
                return ci_type
        return CIConfig.UNKNOWN

    def detect_existing_version(self) -> Optional[str]:
        """检测现有 task-flow 内容的版本

        Returns:
            版本号，如果不存在则返回 None
        """
        if not self.config_file or not self.config_file.exists():
            return None

        try:
            content = self.config_file.read_text(encoding="utf-8")
            return self.content_merger.detect_existing_version(content)
        except (OSError, IOError):
            return None

    def needs_update(self) -> bool:
        """判断是否需要更新

        Returns:
            是否需要更新
        """
        existing_version = self.detect_existing_version()
        if not existing_version:
            return True  # 无现有内容，需要添加

        try:
            return Version(existing_version) < Version(self.CURRENT_VERSION)
        except InvalidVersion:
            return True  # 版本号格式错误，需要更新

    def initialize(
        self,
        template_type: str = "standard",
        force: bool = False,
        interactive: bool = True,
        backup: bool = True,
    ) -> InitResult:
        """初始化项目配置

        Args:
            template_type: 模板类型 (minimal/standard/full)
            force: 强制覆盖现有内容
            interactive: 是否显示确认提示
            backup: 是否备份现有文件

        Returns:
            初始化结果对象
        """
        metadata = ConfigMetadata(
            is_ci=self.is_ci_environment(),
            ci_type=self.detect_ci_type(),
            current_version=self.CURRENT_VERSION,
        )

        try:
            # 1. 验证项目目录
            if not self._project_root.exists():
                return InitResult(
                    success=False,
                    message=f"项目目录不存在: {self._project_root}",
                    error="PROJECT_NOT_FOUND",
                    metadata=metadata,
                )

            # 2. 检查写入权限
            if not self._check_write_permission():
                return InitResult(
                    success=False,
                    message=f"无写入权限: {self._project_root}",
                    error="PERMISSION_DENIED",
                    metadata=metadata,
                )

            # 3. 检查是否已初始化
            if self.is_initialized(self._project_root) and not force:
                existing_version = self.detect_existing_version()
                if existing_version:
                    try:
                        if Version(existing_version) >= Version(self.CURRENT_VERSION):
                            metadata.initialized = True
                            metadata.existing_version = existing_version
                            return InitResult(
                                success=True,
                                message=f"项目已是最新版本 (v{existing_version})",
                                metadata=metadata,
                            )
                    except InvalidVersion:
                        pass  # 继续执行初始化

            # 4. 加载模板
            try:
                template = self.template_loader.load_template(template_type)
            except (FileNotFoundError, TemplateNotFoundError) as e:
                return InitResult(
                    success=False,
                    message=f"加载模板失败: {e}",
                    error="TEMPLATE_NOT_FOUND",
                    metadata=metadata,
                )

            # 5. 渲染模板并添加版本标记
            rendered = self.template_renderer.render(template)
            versioned_content = self.template_renderer.add_version_markers(
                rendered,
                self.CURRENT_VERSION
            )

            # 6. 处理现有文件
            backup_path = None
            if self.config_file and self.config_file.exists():
                # 备份现有文件
                if backup:
                    backup_path = self._backup_existing_file()
                    if backup_path is None:
                        print("⚠️  备份失败，但将继续执行")

                # 合并内容
                existing_content = self.config_file.read_text(encoding="utf-8")
                final_content = self.content_merger.merge_content(
                    existing_content,
                    versioned_content,
                    self.CURRENT_VERSION
                )

                if interactive:
                    print(f"📄 将更新文件: {self.config_file.name}")
                    if not self._confirm_action():
                        return InitResult(
                            success=False,
                            message="用户取消初始化",
                            error="USER_CANCELLED",
                            metadata=metadata,
                        )
            else:
                # 创建新文件
                self._config_file = self._project_root / "CLAUDE.md"
                final_content = self._add_file_header(versioned_content)
                if interactive:
                    print(f"📄 将创建文件: {self.config_file.name}")

            # 7. 写入文件
            try:
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                self.config_file.write_text(final_content, encoding="utf-8")
            except (OSError, IOError) as e:
                raise FileWriteError(str(self.config_file), str(e))

            # 8. 创建标记文件
            self._create_init_marker()

            metadata.initialized = True
            metadata.config_file = self.config_file.name
            metadata.last_updated = datetime.now().isoformat()

            return InitResult(
                success=True,
                config_file=str(self.config_file),
                backup_file=str(backup_path) if backup_path else None,
                message=f"已初始化 {self.config_file.name}",
                metadata=metadata,
            )

        except (ConfigError, FileWriteError) as e:
            return InitResult(
                success=False,
                message=f"初始化失败: {e}",
                error=str(type(e).__name__),
                metadata=metadata,
            )
        except Exception as e:
            return InitResult(
                success=False,
                message=f"未知错误: {e}",
                error="UNKNOWN_ERROR",
                metadata=metadata,
            )

    def _check_write_permission(self) -> bool:
        """检查写入权限

        Returns:
            是否有写入权限
        """
        test_file = self._project_root / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
            return True
        except (OSError, PermissionError):
            return False

    def _backup_existing_file(self) -> Optional[Path]:
        """备份现有文件

        Returns:
            备份文件路径，失败返回 None
        """
        if not self.config_file or not self.config_file.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.config_file.with_suffix(
            f".md.backup_{timestamp}"
        )

        try:
            shutil.copy2(self.config_file, backup_path)
            print(f"📦 已备份到: {backup_path.name}")
            return backup_path
        except (OSError, IOError):
            return None

    def _create_init_marker(self) -> None:
        """创建初始化标记文件"""
        marker_file = self._project_root / self.INIT_MARKER
        marker_file.write_text(
            f"Initialized: task-flow v{self.CURRENT_VERSION}\n"
            f"Date: {datetime.now().isoformat()}\n"
        )

        version_file = self._project_root / self.VERSION_FILE
        version_file.write_text(self.CURRENT_VERSION)

    def _add_file_header(self, content: str) -> str:
        """为新文件添加头部说明

        Args:
            content: 原始内容

        Returns:
            添加了头部的内容
        """
        header = f"""<!-- This file was auto-generated by task-flow v{self.CURRENT_VERSION} -->
<!-- You can edit this file, but the task-flow section will be auto-updated -->

"""
        return header + content

    @staticmethod
    def _confirm_action() -> bool:
        """确认操作

        Returns:
            用户是否确认
        """
        try:
            response = input("确认执行? [Y/n]: ").strip().lower()
            return response in ['', 'y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return False

    def get_config_filename(self) -> Optional[str]:
        """获取配置文件名

        Returns:
            配置文件名，如果不存在则返回 None
        """
        return self.config_file.name if self.config_file else None

    def get_status(self) -> ConfigMetadata:
        """获取当前配置状态

        Returns:
            配置元数据对象
        """
        return ConfigMetadata(
            initialized=self.is_initialized(self._project_root),
            config_file=self.get_config_filename(),
            existing_version=self.detect_existing_version(),
            current_version=self.CURRENT_VERSION,
            needs_update=self.needs_update(),
            is_ci=self.is_ci_environment(),
            ci_type=self.detect_ci_type(),
        )
