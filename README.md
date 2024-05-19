# Stock Watcher

Stock Watcher is a Django-based application that tracks the availability of products and notifies users when their tracked products are back in stock. This project leverages Docker, Celery, and Redis for background task processing and scheduling.

## Features

- User registration and authentication
- Product tracking with specified intervals
    - Crobjob set up 
- Email notifications when products are in stock
- 

## Project Structure
![image](https://github.com/Alhatoon/stock_watcher/assets/91088103/e9457964-0b3f-4432-925e-e59015946352)




## Installation

### Prerequisites

- Docker
- Docker Compose

### Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/Alhatoon/stock_watcher.git
    cd stock_watcher
    ```

2. **Build and Run Docker Containers**

    ```bash
    docker-compose -f docker-compose.yml up --build
    ```

    This will build the Docker images and start the containers for the web service, proxy (if configured), Celery and the database (Cassandra).

3. **Access the Application**

    Open your web browser and go to `http://localhost:8001` to access the application.

4. API testing: Postman 
    [<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://god.gw.postman.com/run-collection/34867969-de52a209-6aea-4534-8a38-62e88ee9bf3f?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D34867969-de52a209-6aea-4534-8a38-62e88ee9bf3f%26entityType%3Dcollection%26workspaceId%3D91c9a4f6-53d4-43e6-adca-e688005c96af)


   Please Note: All APIs run on 8001 as 8000 is for reverse proxy set 
