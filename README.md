API Server

### 1. Install requirements
    pip install -r requirements.txt
    
### 2. redis run
    docker run --name some-redis redis -p 6379:6379 redis
    redis-server

### 3. Run the APIserver
    python run.py
