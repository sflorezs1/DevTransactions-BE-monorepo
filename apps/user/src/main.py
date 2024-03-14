from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from libs.ms_tools import Hoppy, SQLAlchemyAdapter, MessageQueues, Event

db_adapter = SQLAlchemyAdapter('your-database-url') 
app = Hoppy('User', rabbitmq_host='localhost', rabbitmq_port=5672, database_adapter=db_adapter)

@app.queue_listener(MessageQueues.User.CREATE_ACCOUNT_QUEUE)
async def user_register_handler(event: Event, db: AsyncSession) -> None:
    user = User(name = event.body.name, email = event.body.email)
    await db.add(user)
    await db.commit()

async def start():
    await app.start()
