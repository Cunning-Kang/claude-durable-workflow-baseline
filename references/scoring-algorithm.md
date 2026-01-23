# 评分算法详解

## 算法设计

综合评分 = Stars(30%) + 更新时间(25%) + Issues响应率(20%) + Forks(15%) + Contributors(10%)

## 各维度详解

### Stars (30%)
使用对数函数避免大数优势:
```python
stars_score = min(log(stars + 1) * 3, 30)
```

- 1K stars ≈ 21 分
- 10K stars ≈ 28 分
- 100K stars ≈ 30 分(封顶)

### 更新时间 (25%)
- 30 天内: 25 分
- 90 天内: 20 分
- 180 天内: 15 分
- 365 天内: 10 分
- 超过 1 年: 5 分

### Issues 响应率 (20%)
```python
issues_score = (closed_issues / total_issues) * 20
```

- 全部关闭: 20 分
- 一半关闭: 10 分
- 全部开放: 0 分
- 无 issues: 默认 10 分

### Forks (15%)
```python
forks_score = min(log(forks + 1) * 2, 15)
```

### Contributors (10%)
```python
contributors_score = min(contributors / 10, 1.0) * 10
```

- 10+ contributors: 10 分
- 5 contributors: 5 分

## 过滤规则

- 评分 < 30: 不展示
- 过滤后 < 3 个: 降低阈值到 20
- 仍然不足: 展示所有有效结果

## 优化建议

可根据实际使用调整:
- 权重分配
- 评分阈值
- 时间分段
