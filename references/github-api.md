# GitHub API 使用参考

## 认证

GitHub API 支持两种模式:

### 无认证模式
- 速率限制: 每小时 60 次请求
- 适用场景: 偶尔使用

### PAT 认证模式
- 速率限制: 每小时 5000 次请求
- 适用场景: 频繁使用

## 获取 Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限: `repo` (full control)
4. 生成并复制 token

## 配置方式

### 环境变量
```bash
export GITHUB_TOKEN="your_token_here"
```

### 文件配置
```bash
echo "your_token_here" > ~/.github-token
chmod 600 ~/.github-token
```

## API 限制

- 搜索结果最多返回 1000 个
- 每次查询建议限制在 10-20 个结果
- 注意处理速率限制错误

## 错误处理

主要错误类型:
- `403`: 速率限制超出
- `401`: Token 无效
- `404`: 资源不存在
- `503`: 服务临时不可用
