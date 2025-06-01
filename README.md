# FastAPI Messenger
![](https://img.shields.io/github/stars/TrialByFire37/FastAPI-Messenger) ![](https://img.shields.io/github/forks/TrialByFire37/FastAPI-Messenger) ![](https://img.shields.io/github/issues/TrialByFire37/FastAPI-Messenger)

------------
A project made for SPbSPU's discipline "Technologies of quality software development".

[Task board (obsolete)](https://ru.yougile.com/team/5266086dd05f/Messenger)

[Front-end repo](https://github.com/oblachnyy/P2P-Messenger-frontend)

### How to setup
1. Make sure you have the following installed on your system:
 * Python 3.10.
 * PostgreSQL 15.7.
 * Git.
 * Node.js 16.20.2.
 * npm 8.19.4.

2. Clone both repos locally:
`git clone https://github.com/TrialByFire37/Team-Messenger.git`
`git clone https://github.com/oblachnyy/P2P-Messenger-frontend.git`

4. Start your local PostgreSQL server.

5. Backend:
 * Install dependencies specified in "requirements.txt":
`pip install -r requirements`
 * Make up your own env-file, like this:

 ```
 DB_USER=<your DB user>
 DB_PASS=<your DB user's password'>
 DB_HOST=<your DB hostname>
 DB_PORT=<your DB port>
 DB_NAME=<the name of your DB for main data>
 
 SECRET_AUTH=<random secret word>

 ENDPOINT=<AWS bucket endpoint>
 KEY_ID_RO=<AWS bucket key>
 APPLICATION_KEY_RO=<AWS bucket private key>
 YANDEX_BUCKET=<AWS bucket name>
 
 SHOTSTACK_API=<Shotstack API key>
 
 DB_USER_TEST=<your test DB user>
 DB_PASS_TEST=<your test DB user's password'>
 DB_HOST_TEST=<your test DB hostname>
 DB_PORT_TEST=<your test DB port>
 DB_NAME_TEST=<the name of your DB for test data>
 ```
 * Migrate the existing version of DB from "migrations/versions":
`py alembic upgrade <sequence of letters and numbers from the filename>`
 * Run the server using "src/main.py".

5. Frontend:
 * Install dependencies listed in the "package.json":
 `npm install`
 * Once all the packages are install, start the frontend piece:
 `npm start`

The default address is `localhost:3000`.
