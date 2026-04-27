"""
MDM 模拟接口服务
提供两个无认证 API 接口用于 MDM 系统联调测试
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

app = FastAPI(title="MDM 模拟接口服务", version="1.0.0")

# CORS 配置，允许外部访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "mdm.db")


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库和表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 创建 source_departments 表（抓取数据源）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departmentCode TEXT NOT NULL,
            departmentName TEXT NOT NULL,
            createTime TEXT NOT NULL
        )
    """)

    # 创建 received_departments 表（接收推送数据）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS received_departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            departmentCode TEXT NOT NULL,
            departmentName TEXT NOT NULL,
            createTime TEXT NOT NULL
        )
    """)

    # 检查 source_departments 是否有数据，如果没有则初始化
    cursor.execute("SELECT COUNT(*) FROM source_departments")
    if cursor.fetchone()[0] == 0:
        source_data = [
            ("01", "运营部"),
            ("02", "采购部"),
            ("03", "内勤"),
            ("04", "仓储部"),
        ]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.executemany(
            "INSERT INTO source_departments (departmentCode, departmentName, createTime) VALUES (?, ?, ?)",
            [(code, name, now) for code, name in source_data]
        )
        conn.commit()

    conn.close()


# 请求体模型
class DepartmentItem(BaseModel):
    departmentCode: str
    departmentName: str


# 接口一：GET 抓取部门数据
@app.get("/api/department/queryAllDepartment")
def query_all_department():
    """
    从 source_departments 表查询所有部门数据
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT departmentCode, departmentName FROM source_departments")
    rows = cursor.fetchall()
    conn.close()

    data = [
        {"departmentCode": row["departmentCode"], "departmentName": row["departmentName"]}
        for row in rows
    ]

    return {
        "code": 200,
        "msg": "操作成功",
        "data": data
    }


# 接口二：POST 批量接收部门数据
@app.post("/api/department/batchInsertDept")
def batch_insert_dept(departments: list[DepartmentItem]):
    """
    批量接收并保存 MDM 推送的部门数据
    """
    if not departments:
        return {
            "code": 200,
            "msg": "插入成功",
            "data": {"inserted": 0}
        }

    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [(dept.departmentCode, dept.departmentName, now) for dept in departments]

    cursor.executemany(
        "INSERT INTO received_departments (departmentCode, departmentName, createTime) VALUES (?, ?, ?)",
        data
    )
    conn.commit()
    inserted = cursor.rowcount
    conn.close()

    return {
        "code": 200,
        "msg": "插入成功",
        "data": {"inserted": inserted}
    }


@app.get("/")
def root():
    return {"message": "MDM 模拟接口服务已启动", "docs": "/docs"}


@app.get("/api/department/getReceivedDepts")
def get_received_departments():
    """
    查询已接收的部门数据（从 received_departments 表）
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, departmentCode, departmentName, createTime FROM received_departments ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    data = [
        {
            "id": row["id"],
            "departmentCode": row["departmentCode"],
            "departmentName": row["departmentName"],
            "createTime": row["createTime"]
        }
        for row in rows
    ]

    return {
        "code": 200,
        "msg": "操作成功",
        "data": data
    }


@app.delete("/api/department/clearReceivedDepts")
def clear_received_departments():
    """
    清空 received_departments 表中的所有数据
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM received_departments")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return {
        "code": 200,
        "msg": "清空成功",
        "data": {"deleted": deleted}
    }


# 启动时初始化数据库
init_database()
