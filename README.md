# FastAPI URL Shortener

A minimal URL shortener built with **FastAPI**, **SQLAlchemy**, and **Alembic**.  
It stores shortened URLs in a database, lists stored URLs, and redirects short codes to the original URL while recording visits.

## Features

- Auth: get access token (`POST /login/access-token`)
- Auth: register user (`POST /users`)
- Create a shortened URL (`POST /urls`)
- List current user URLs (`GET /urls`)
- List visits for current user URLs (`GET /urls/visits`)
- Redirect by code and record a visit (`GET /{url_code}`)

## Future Improvement

My purpose of building this app is to implement backend development concepts I have learned so far. Naturally, there are a lot of improvements that will be implemented as I learn.

- [x] ORMs
- [x] Users
- [x] Auth
- [x] ORM relationships
- [x] Service layer for business logic 
- [x] More standard user options (delete, update info, deactivate)
- [x] Update db schema to match (is_active, is_superuser)
- [ ] Super user and its endpoints
- [ ] Send email on register
- [ ] More endpoints:
    - [x] List URLs per user
    - [ ] Get shortcodes for a given domain
- [x] Professional archeticture and project structure
    - [x] Continue (routes)
    - [x] Run a check with AI
- [x] Migrations
- [ ] Deployment
- [ ] Testing
- [ ] Simple Forntend
- [ ] CI/CD?
