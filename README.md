# Metrics Service

Assignment Software Engineer Cloud Services

## Installation

### Dependencies

We are use the `Pipenv` to keep all the dependencies up to date.

- Install pipenv module

```bash
$ apt install pipenv
```

- After that we can create a virtualenv

```bash
$ pipenv shell
```

- Now you can install the 3rd party package you need

```bash
$ pipenv install fastapi
```

- You can specify that this dependency is only for development

```bash
$ pipenv install pytest --dev
```

- Now is time to install all dependencies

```bash
$ pipenv install # This install all dependencies necesaries to the project work
$ pipenv install --dev # This install all dependencies even develop dependencies
```

- To unistall all dependencies use

```bash
$ pipenv uninstall --all
```

- If everything working well in local environment, now we can push it to production. To be ensure we have the same one in production use the `Pipfile.lock`

```bash
$ pipenv lock
```

- Once you get your code and Pipfile.lock in your production environment, you should install the last successful environment recorded

```bash
$ pipenv install --ignore-pipfile
```

## Running

### Run local project

We use `uvicorn` to run service in local

```bash
$ uvicorn --port 8080 --host 0.0.0.0 --timeout-keep-alive 300 app.main:app
```

Hostnames for accessing the service directly

```
http://127.0.0.1:8080
```

See OpenAPI documentation

```
http://127.0.0.1:8080/docs
```

### Docker Run

- Build Docker image

```
docker build -t metrics .
```

- Run Docker Image

```
docker run -p 8080:8080 --network=host metrics
```

## Run test

The library for unit test we are to use is `pytest` this library to allow creating test quickly.

To run the test use the following command in the root directory:

```bash
$ pytest -v
```

To get the coverage run:

```bash
$ pytest --cov-report term-missing --cov=. app/tests/
```
