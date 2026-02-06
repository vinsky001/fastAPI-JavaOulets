from collections.abc import AsyncGenerator
from  sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, Text, Float, ForeignKey


DB_url = "sqlite+aiosqlite:///./javaoutlets.db"

class Base(DeclarativeBase):
    """base class for all orm models"""
    pass

class JavaOutletBase(Base):
    """Base class for all JavaOutlet orm models"""
    __tablename__ = "java_outlets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    county = Column(Text, nullable=False)
    street_address = Column(Text)
    phone_number = Column(Text)
    rating = Column(Float)
    is_open = Column(Integer, nullable=False)
    opening_time = Column(Text)
    closing_time = Column(Text)
    last_inspected_at = Column(Text)
    
    menu_items = relationship("MenuItems", back_populates="outlet", cascade="all, delete-orphan")
    orders = relationship("Orders", back_populates="outlet", cascade="all, delete-orphan")
    
class MenuItems(Base):
    """Model for menu items at Java outlets"""
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    outlet_id = Column(Integer, ForeignKey("java_outlets.id"), nullable=False)
    menu_item_name = Column(Text, nullable=False)
    category = Column(Text)
    sku = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(Text, nullable=False)
    is_available = Column(Integer, nullable=False)
    has_dairy = Column(Integer, nullable=False)
    is_seasonal = Column(Integer, nullable=False)
    
    # Relationship back to JavaOutlet
    outlet = relationship("JavaOutletBase", back_populates="menu_items")
    
    def __repr__(self):
        return f"<MenuItems(id={self.id}, menu_item_name='{self.menu_item_name}', price={self.price})>"
    
    
class Orders(Base):
    """Model for orders at Java outlets"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    outlet_id = Column(Integer, ForeignKey("java_outlets.id"), nullable=False)
    product_ids = Column(Text, nullable=False)
    total_price = Column(Float, nullable=False)
    currency = Column(Text, nullable=False)
    is_completed = Column(Integer, nullable=False)
    status = Column(Text, nullable=False)
    placed_at = Column(Text, nullable=False)
    completed_at = Column(Text)
    payment_method = Column(Text)
    notes = Column(Text)
    
    # Relationship back to JavaOutlet
    outlet = relationship("JavaOutletBase", back_populates="orders")
    
    def __repr__(self):
        return f"<Orders(id={self.id}, outlet_id={self.outlet_id}, status='{self.status}')>"
    
       
engine = create_async_engine(DB_url, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
 

    
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session   
        
async def run_db_operation(operation):
    """Execute db operations asynchronously"""  
    try:
        async with async_session_maker() as session:
            result = await operation(session)
            await session.commit()
            return result
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise e        
            
    
async def init_db() -> None:
    #Initialize the database
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e              



        
        