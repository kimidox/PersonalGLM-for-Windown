from datetime import datetime

from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON, Text

from system.database import Base, engine
from system.database.utils import get_local_time


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(TIMESTAMP, default=get_local_time())
    updated_at = Column(TIMESTAMP, default=get_local_time())
    def to_dict(self):
        return {c.name:getattr(self,c.name) for c in self.__table__.columns}
class Conversations(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String)
    created_at = Column(TIMESTAMP, default=get_local_time())
    updated_at = Column(TIMESTAMP, default=get_local_time())
    def to_dict(self):
        return {c.name:getattr(self,c.name) for c in self.__table__.columns}
class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    conversation_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    ext=Column(JSON)
    created_at = Column(TIMESTAMP, default=get_local_time())
    updated_at = Column(TIMESTAMP, default=get_local_time())

    def to_dict(self):
        return {c.name:getattr(self,c.name) for c in self.__table__.columns}

class Agents(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    name = Column(String)
    description = Column(Text)
    config = Column(JSON)
    created_at = Column(TIMESTAMP, default=get_local_time())
    updated_at = Column(TIMESTAMP, default=get_local_time())

    def to_dict(self):
        return {c.name:getattr(self,c.name) for c in self.__table__.columns}

class AgentsNodes(Base):
    __tablename__ = 'agents_nodes'
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True)
    node_id = Column(String, index=True)
    node_type = Column(String)
    config=Column(JSON)
    created_at = Column(TIMESTAMP, default=get_local_time())
    updated_at = Column(TIMESTAMP, default=get_local_time())
    def to_dict(self):
        return {c.name:getattr(self,c.name) for c in self.__table__.columns}
class Nodes(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, unique=True, index=True)
    node_type = Column(String)
    name = Column(String)
    description = Column(Text)
    config = Column(JSON)
    created_at = Column(TIMESTAMP, default=get_local_time())
    updated_at = Column(TIMESTAMP, default=get_local_time())
    def to_dict(self):
        return {c.name:getattr(self,c.name) for c in self.__table__.columns}
if __name__ == '__main__':
    Base.metadata.create_all(engine)