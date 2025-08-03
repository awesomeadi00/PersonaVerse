
<!-- ![Workflow Status](https://github.com/software-students-fall2023/5-final-project-mostly_afk/actions/workflows/webapp.yml/badge.svg?branch=main&kill_cache=1)
![Workflow Status](https://github.com/software-students-fall2023/5-final-project-mostly_afk/actions/workflows/client.yml/badge.svg?branch=main&kill_cache=1)
![Workflow Status](https://github.com/software-students-fall2023/5-final-project-mostly_afk/actions/workflows/ci-cd.yml/badge.svg?branch=main&kill_cache=1) -->

# PersonaVerse

PersonaVerse is a creative web application that allows users to engage in conversations with a variety of AI chatbots, each boasting a unique personality, from a helpful mom to a mysterious vampire. The app features an intuitive chat interface, enabling users to select different AI personalities and view their chat histories and express themselves to all sorts of personalities!

## Team: 

- [Aditya Pandhare](https://github.com/awesomeadi00)
- [Anzhelika Nastashchuk](https://github.com/annsts)
- [Baani Pasrija](https://github.com/zeepxnflrp)

## Setup Locally: 

### Prerequisites: 

Before you start the steps below, make sure you have the following downloaded on your system: 

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

1. Clone the repository:
```
git clone https://github.com/awesomeadi00/PersonaVerse.git
```

2. Navigate to the project directory: 
```
cd PersonaVerse
```

3. Create a `.env` file inside the `client/` folder and place the OpenAI API Key that should be provided to you:
```
OPENAI_API_KEY = <API Key>
```

4. Create a `.env` file inside the `web_app/` folder and create a Flask App Secret Key using: 
```
import secrets
print(secrets.token_hex(32))
```

Then put it in 

5. Build docker images and run the containers:
```
docker compose up --build -d
```

6. Open the application in your browser:
```
http://localhost:5001
```

7. To stop the containers, run the command: 
```
docker-compose stop
```

## Database Information:

- **Database**: MongoDB (automatically set up via Docker)
- **Collections**: 
  - `users` - stores user account information
  - `chat` - stores conversation history
- **Setup**: Collections are created automatically when the application starts
- **Access**: You can view the database using MongoDB Compass by connecting to `mongodb://localhost:27017`

## Docker Hub
You can pull the images for the client and webapp through the following commands: 
```
docker pull awesomeadi00/personaverse-webapp
docker pull awesomeadi00/personaverse-client
```