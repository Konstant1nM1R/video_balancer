from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  
    max_overflow=10,  
    pool_timeout=30,  
    pool_recycle=1800, 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BalancerConfig(Base):
    __tablename__ = "balancer_config"

    id = Column(Integer, primary_key=True, index=True)
    cdn_host = Column(String, nullable=False)
    redirect_ratio = Column(Integer, nullable=False, default=5)

_config_cache = None
_config_cache_time = 0
CACHE_TTL = 60  

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cached_config():
    global _config_cache, _config_cache_time
    import time
    
    current_time = time.time()
    if _config_cache is None or (current_time - _config_cache_time) > CACHE_TTL:
        db = SessionLocal()
        try:
            config = db.query(BalancerConfig).first()
            if not config:
                config = BalancerConfig(
                    cdn_host=settings.CDN_HOST,
                    redirect_ratio=settings.REDIRECT_RATIO
                )
                db.add(config)
                db.commit()
                db.refresh(config)
            _config_cache = config
            _config_cache_time = current_time
        finally:
            db.close()
    return _config_cache

Base.metadata.create_all(bind=engine)