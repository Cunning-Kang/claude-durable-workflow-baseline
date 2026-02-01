"""测试 PathInference"""

import pytest
from plan_generator.path_inference import PathInference


def test_python_model_path_inference():
    """测试 Python 模型路径推断"""
    inference = PathInference()
    path = inference.infer("User", "python", ["fastapi"])

    assert path == "src/models/user.py"


def test_python_service_path_inference():
    """测试 Python 服务路径推断"""
    inference = PathInference()
    path = inference.infer("AuthService", "python", ["fastapi"])

    assert path == "src/services/auth_service.py"


def test_python_api_route_path_inference():
    """测试 Python API 路由路径推断"""
    inference = PathInference()
    path = inference.infer("AuthRoutes", "python", ["fastapi"])

    assert path == "src/api/routes/auth.py"


def test_javascript_component_path_inference():
    """测试 JavaScript/TypeScript 组件路径推断"""
    inference = PathInference()
    path = inference.infer("UserProfile", "javascript", ["react"])

    assert path == "components/UserProfile.tsx"


def test_javascript_hook_path_inference():
    """测试 JavaScript Hook 路径推断"""
    inference = PathInference()
    path = inference.infer("useAuth", "javascript", ["react"])

    assert path == "hooks/useAuth.ts"


def test_javascript_util_path_inference():
    """测试 JavaScript 工具函数路径推断"""
    inference = PathInference()
    path = inference.infer("formatDate", "javascript", ["typescript"])

    assert path == "utils/formatDate.ts"


def test_go_model_path_inference():
    """测试 Go 模型路径推断"""
    inference = PathInference()
    path = inference.infer("User", "go", ["gin"])

    assert path == "models/user.go"


def test_feature_type_detection():
    """测试功能类型检测"""
    inference = PathInference()

    # 检测模型类型
    model_type = inference._detect_feature_type("User")
    assert model_type == "model"

    # 检测服务类型
    service_type = inference._detect_feature_type("AuthService")
    assert service_type == "service"

    # 检测 API 类型
    api_type = inference._detect_feature_type("AuthRoutes")
    assert api_type == "api"

    # 检测组件类型
    component_type = inference._detect_feature_type("UserProfile")
    assert component_type == "component"


def test_infer_test_path():
    """测试测试路径推断"""
    inference = PathInference()

    # Python 测试路径
    python_test = inference.infer_test_path("src/models/user.py", "pytest")
    assert python_test == "tests/models/test_user.py"

    # JavaScript 测试路径
    js_test = inference.infer_test_path("components/UserProfile.tsx", "jest")
    assert js_test == "components/__tests__/UserProfile.test.tsx"

    # Go 测试路径
    go_test = inference.infer_test_path("models/user.go", "go")
    assert go_test == "models/user_test.go"
