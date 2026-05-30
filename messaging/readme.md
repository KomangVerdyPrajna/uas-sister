# Please follow the instructions below to run:
1. Make sure you have Docker and RabbitMQ running on your system.<br>
   Docker Desktop can be downloaded from [here](https://www.docker.com/get-started/).<br>
   RabbitMQ can be downloaded from [here](https://www.rabbitmq.com/). Alternatively, for Windows, use rabbitmq-server-4.3.0.exe from [here](https://github.com/rabbitmq/rabbitmq-server/releases)
3. Execute services:<br>
   Run the RabbitMQ Broker:
   ```
   root-dir> docker compose up -d --build rabbitmq
   ```
   a) Send a message:
   ```
   root-dir> docker compose run --rm producer python producer.py
   ```
   OR:
   ```
   root-dir> docker compose run --rm producer python producer.py 120000 VA_MANDIRI
   root-dir> docker compose run --rm producer python producer.py 100000 QRIS
   ```
   Consume/work on the message:
   ```
   root-dir> docker compose up -d --build worker
   ```
   OR, if you want to use three (more) workers:
   ```
   root-dir> docker compose up -d --build --scale worker=3 worker
   ```
   Then check the result:
   ```
   root-dir> docker compose up -d --build result
   ```
   b) Check the worker output
   ```
   docker compose logs -f worker
   ```
   You may repeat the processes of a) & b) thereafter to see more working messages.
6. To remove all services:
   ```
   docker compose down
7. Check the RabbitMQ Management at: http://localhost:15672
    ```
    user: guest/guest
