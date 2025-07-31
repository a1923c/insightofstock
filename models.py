from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import text
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('/var/www/insightofstock/.env')

Base = declarative_base()

class Ticker(Base):
    __tablename__ = 'tickers'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), unique=True, nullable=False)
    symbol = Column(String(10))
    name = Column(String(100))
    area = Column(String(50))
    industry = Column(String(50))
    list_date = Column(String(10))
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    top_holders = relationship("TopHolder", back_populates="ticker")
    
    def __repr__(self):
        return f"<Ticker(ts_code='{self.ts_code}', name='{self.name}')>"

class TopHolder(Base):
    __tablename__ = 'top_holders'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)
    ann_date = Column(String(10))
    end_date = Column(String(10))
    holder_name = Column(String(100))
    hold_amount = Column(Float)
    hold_ratio = Column(Float)
    holder_type = Column(String(10))  # G=个人, C=机构, P=私募, E=信托, O=其他
    hold_change = Column(Float)  # 持股变动数量
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ticker = relationship("Ticker", back_populates="top_holders")
    
    def __repr__(self):
        return f"<TopHolder(ts_code='{self.ts_code}', holder_name='{self.holder_name}', hold_ratio={self.hold_ratio})>"

class UpdateLog(Base):
    __tablename__ = 'update_log'
    
    id = Column(Integer, primary_key=True)
    update_type = Column(String(50), nullable=False)  # 'tickers', 'holders', 'full'
    last_update_date = Column(String(10), nullable=False)  # Latest end_date from data
    record_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UpdateLog(update_type='{self.update_type}', last_update_date='{self.last_update_date}')>"

# Database setup
def get_engine():
    database_url = os.getenv('DATABASE_URL', 'sqlite:///database/insightofstock.db')
    engine = create_engine(database_url)
    return engine

def create_tables():
    engine = get_engine()
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create individual holder tickers view
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE VIEW IF NOT EXISTS individual_holder_tickers AS
            SELECT 
                holder_name,
                COUNT(DISTINCT ts_code) as ticker_count
            FROM top_holders 
            WHERE holder_type = '自然人' 
            GROUP BY holder_name
            HAVING ticker_count>=2 
            ORDER BY ticker_count DESC
        """))
        
        # Create tickers with multiple holders view (individual shareholders only)
        conn.execute(text("""
            CREATE VIEW IF NOT EXISTS tickers_with_multiple_holders AS
            SELECT 
                ts_code, 
                COUNT(DISTINCT holder_name) as holder_count 
            FROM top_holders 
            WHERE holder_type = '自然人' 
            GROUP BY ts_code
            HAVING holder_count>=2 
            ORDER BY holder_count DESC
        """))
        conn.commit()
    
    return engine

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")