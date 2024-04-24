```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
from app.dependencies import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理接收到的数据，可以进行数据库操作等
            # 例如，将接收到的数据保存到数据库
            # db.add(SomeModel(data=data))
            # db.commit()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
```

1. `ConnectionManager` 类：
   - 用于管理 WebSocket 连接的自定义类。
   - `active_connections` 属性存储当前活动的 WebSocket 连接列表。
   - `connect` 方法在新的 WebSocket 连接建立时调用，将连接添加到 `active_connections` 列表中。
   - `disconnect` 方法在 WebSocket 连接关闭时调用，将连接从 `active_connections` 列表中移除。
   - `send_personal_message` 方法用于向特定的 WebSocket 连接发送个人消息。
   - `broadcast` 方法用于向所有活动的 WebSocket 连接广播消息。

2. `@router.websocket("/ws/{client_id}")` 装饰器：
   - 定义了一个 WebSocket 端点，路径为 `/ws/{client_id}`，其中 `client_id` 是一个路径参数，表示客户端的唯一标识符。

3. `websocket_endpoint` 函数：
   - 处理 WebSocket 连接的主要函数。
   - 使用 `Depends(get_db)` 依赖注入获取数据库会话对象 `db`。
   - 调用 `manager.connect(websocket)` 将新的 WebSocket 连接添加到 `ConnectionManager` 中。
   - 在一个无限循环中，等待接收来自客户端的消息，并进行相应的处理。
   - 可以在接收到消息后进行数据库操作，例如将接收到的数据保存到数据库中。
   - 使用 `manager.send_personal_message` 向当前连接发送个人消息。
   - 使用 `manager.broadcast` 向所有活动的连接广播消息。

4. `WebSocketDisconnect` 异常处理：
   - 当 WebSocket 连接关闭时，会引发 `WebSocketDisconnect` 异常。
   - 在异常处理块中，调用 `manager.disconnect(websocket)` 将关闭的连接从 `ConnectionManager` 中移除。
   - 使用 `manager.broadcast` 向其他活动的连接广播客户端离开的消息。