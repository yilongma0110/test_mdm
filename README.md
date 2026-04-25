# MDM 模拟接口服务

用于 MDM 系统联调测试的模拟 API 服务，提供两个无认证接口。

## 接口列表

### 1. 抓取部门数据
- **路径**: `GET /api/department/queryAllDepartment`
- **功能**: 从数据库查询所有部门数据
- **返回格式**:
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {"departmentCode": "01", "departmentName": "运营部"},
    {"departmentCode": "02", "departmentName": "采购部"},
    {"departmentCode": "03", "departmentName": "内勤"},
    {"departmentCode": "04", "departmentName": "仓储部"}
  ]
}
```

### 2. 批量接收部门数据
- **路径**: `POST /api/department/batchInsertDept`
- **功能**: 接收并保存 MDM 推送的部门数据
- **请求体**:
```json
[
  {"departmentCode": "CS001", "departmentName": "测试部门1"},
  {"departmentCode": "CS002", "departmentName": "测试部门2"}
]
```
- **返回格式**:
```json
{
  "code": 200,
  "msg": "插入成功",
  "data": {"inserted": 2}
}
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 9099
```

服务启动后可访问:
- API 文档: http://localhost:9099/docs
- 接口地址: http://localhost:9099/api/department/queryAllDepartment

## 测试命令

### 测试抓取接口 (GET)
```bash
curl http://localhost:9099/api/department/queryAllDepartment
```

### 测试批量插入接口 (POST)
```bash
curl -X POST http://localhost:9099/api/department/batchInsertDept \
  -H "Content-Type: application/json" \
  -d "[{\"departmentCode\": \"CS001\", \"departmentName\": \"测试部门1\"}, {\"departmentCode\": \"CS002\", \"departmentName\": \"测试部门2\"}]"
```

## 数据库

使用 SQLite 数据库 (`mdm.db`)，包含两张表：

- **source_departments**: 抓取数据源（预置 4 条模拟数据）
- **received_departments**: 接收推送数据

表结构:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| departmentCode | TEXT | 部门编码 |
| departmentName | TEXT | 部门名称 |
| createTime | TEXT | 创建时间 |

## 注意事项

- 接口无认证保护，仅用于测试环境
- 服务监听 0.0.0.0，可从外部机器访问
- 默认端口: 9099
