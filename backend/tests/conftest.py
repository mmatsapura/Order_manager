import os


os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DATABASE", "order_manager_test")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-unit-tests!!")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
