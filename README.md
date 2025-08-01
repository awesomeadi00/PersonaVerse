
![Workflow Status](https://github.com/software-students-fall2023/5-final-project-mostly_afk/actions/workflows/webapp.yml/badge.svg?branch=main&kill_cache=1)
![Workflow Status](https://github.com/software-students-fall2023/5-final-project-mostly_afk/actions/workflows/client.yml/badge.svg?branch=main&kill_cache=1)
![Workflow Status](https://github.com/software-students-fall2023/5-final-project-mostly_afk/actions/workflows/ci-cd.yml/badge.svg?branch=main&kill_cache=1)

# PersonaVerse

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

## [Live Demo](http://159.65.44.240:5001/)

## Team Members: 

- [Aditya Pandhare](https://github.com/awesomeadi00)
- [Anzhelika Nastashchuk](https://github.com/annsts)
- [Baani Pasrija](https://github.com/zeepxnflrp)

## Description: 

PersonaVerse is a creative web application that allows users to engage in conversations with a variety of AI chatbots, each boasting a unique personality, from a helpful mom to a mysterious vampire. The app features an intuitive chat interface, enabling users to select different AI personalities and view their chat histories and express themselves to all sorts of personalities!

## Setup Locally: 

### Prerequisites: 

Before you start the steps below, make sure you have the following downloaded on your system: 

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

1. Clone the repository:
```
git clone https://github.com/software-students-fall2023/5-final-project-mostly_afk.git
```

2. Navigate to the project directory: 
```
cd 5-final-project-mostly_afk
```

3. Create a .env file inside the `client/` folder and place the OpenAI Api Key that should be provided to you:
```
OPENAI_API_KEY = "Api Key Provided to you"
```

4. Build docker images and run the containers:
```
docker compose up --build -d
```

5. Open the application in your browser:
```
http://localhost:5001
```

6. To stop the containers, run the command: 
```
docker-compose stop
```
