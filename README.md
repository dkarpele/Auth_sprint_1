# Service Auth API.

It provides the service to work with users and thier roles: create, update and delete; user login. Changing user roles. The service uses FastApi for API, Postgres to store user data and roles, and Redis for caching invalid access tokens and refresh tokens. The first thing to do is to create _admin_ user and _admin_ role (use `docker-compose up`):

```
pyhton3 src/create_admin.py
```

## Project structure:

* API service - uses FastApi Async framework to provide API for external services.
* tests - pytest based tests for API


## Documentation

[OpenAPI](http://localhost/api/openapi) documentation is available after creating the service.


## Installation

1. Clone [repo](https://github.com/dkarpele/Auth_sprint_1).
2. Create ```.env``` file according to ```.env.example```.
3. Launch the project ```docker-compose up```.

## Testing

1. Go to `/tests/functional`
2. Create ```.env``` file according to ```.env.example```.
3. Launch the project ```docker-compose up```.

## API calls
auth

- POST http://127.0.0.1/api/v1/auth/signup - create new account
- POST http://127.0.0.1/api/v1/auth/login - login
- POST http://127.0.0.1/api/v1/auth/logout - logout (must be authorised)
- POST://127.0.0.1/api/v1/auth/refresh - receive new pair of tokens

roles:
(only for _admin_ role, must be authorised)
- GET http://127.0.0.1/api/v1/roles/ - receive list of all available roles in DB
- POST http://127.0.0.1/api/v1/roles/create - create new role
- PATCH http://127.0.0.1/api/v1/roles/<role_id> - update role
- DELETE http://127.0.0.1/api/v1/roles/<role_id> - delete role

users:

- POST http://127.0.0.1/api/v1/users/add-role - add role to user (only for _admin_ role)
- DELETE http://127.0.0.1/api/v1/users/delete-role - remove role from user (only for _admin_ role)
- GET http://127.0.0.1/api/v1/users/roles - list all roles for current user (only for _admin_ role)
- GET http://127.0.0.1/api/v1/users/me - get all data about current user (must be authorised)
- POST http://127.0.0.1/api/v1/users/change-login-password - change user's login/password (must be authorised)


## Authors
* Lubov Sovina [@lubovSovina](https://github.com/lubovSovina)
* Denis Karpelevich [@dkarpele](https://github.com/dkarpele)
