from fastapi import APIRouter

mockRouter = APIRouter(
    prefix="/mock",
    tags=["mock"],
    responses={404: {"description": "Not found"}},
)


@mockRouter.get("/userinfo")
async def example(user_id: int):
    print("user_id:", user_id)
    userinfo = {
        # 报销系统老师信息
        "id": 1,
        "name": "李老师",
        "age": 30,
        "department": "计算机系",
        "position": "教授",
        "salary": 10000,
        "phone": "12345678901",
    }
    return {"userinfo": userinfo}


@mockRouter.get("/projectinfo")
async def example(user_id: int):
    print("project_id:", user_id)
    projectinfo = [{
        # 报销系统项目信息
        "id": 1,
        "name": "项目1",
        "department": "计算机系",
        "type": "科研",
        "money": 10000,
        "status": "进行中",
    }, {
        "id": 2,
        "name": "项目2",
        "department": "计算机系",
        "type": "科研",
        "money": 20000,
        "status": "已结束",
    }, {
        "id": 3,
        "name": "项目3",
        "department": "计算机系",
        "type": "科研",
        "money": 30000,
        "status": "进行中",
    }]

    return {"projectinfo": projectinfo}
