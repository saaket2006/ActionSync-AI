import os

# Set test database URL environment variable before any modules are imported/instantiated by pytest
os.environ["DATABASE_URL"] = "sqlite:///./storage/actionsync_test.db"
