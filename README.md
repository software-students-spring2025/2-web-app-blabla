# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

The Dream Journal App helps users log, analyze, and reflect on their dreams, enabling personal insights and recurring pattern tracking.

## User stories

[Issues Page](https://github.com/software-students-spring2025/2-web-app-blabla/issues)

## Steps necessary to run the software

### Prerequisites

Before running the software, ensure you have the following installed:
- [Python 3.10+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)
- [MongoDB](https://www.mongodb.com/try/download/community) (or a MongoDB URI for a hosted solution)

### Getting Started

Follow these steps to get the software running on your local machine.

#### 1. Clone the Repository

  Clone the project repository from GitHub:

#### 2. Install Dependencies

  Install all the required packages globally using `pip` in the terminal:

    pip install Flask pymongo python-dotenv Werkzeug bson

#### 3. Environment Variables 

  Make sure `.env` file is included in the repository for running the application. 

#### 4. Running the Application

  With the dependencies installed and the `.env` file configured, run the Flask application:

    flask run

  For Windows users, use the following commands:

    set FLASK_APP=app.py
    set FLASK_ENV=development
    flask run

  The application will run locally at [http://127.0.0.1:5000](http://127.0.0.1:5000).

#### 5. Using the Application

- **Login:** When you access the root URL (`/`), you'll see the login page.
- **Sign Up:** If you don't have an account, go to `/signup` to register.
- **Home:** After logging in, visit `/home` where you can select from four functions: Add, Edit, Search, or Analyze your dreams.
- **Add Dream:** Click the "Add Dream" button on the home page to create a new dream entry.
- **Edit Dream:** Click the stars on the home page to open the corresponding dream for editing.
- **Analysis:** Go to `/analysis` to view detailed insights and trends about your dreams.
- **Search:** Use the search feature to filter dreams by tags (like "Happy", "Funny", "Excited", or "XXXX"). Matching dreams will be highlighted (for example, with blue stars).



## Task boards

[Task Boards - Sprint 1](https://github.com/orgs/software-students-spring2025/projects/5)

[Task Boards - Sprint 2](https://github.com/orgs/software-students-spring2025/projects/137/views/1?layout=board)
