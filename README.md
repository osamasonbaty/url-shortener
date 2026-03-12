# FastAPI URL Shortener

A minimal URL shortener built with **FastAPI** and **SQLAlchemy**.  
It stores shortened URLs in a database, lists stored URLs, and redirects short codes to the original URL while recording visits.

## Features

- Auth: get access token (`POST /token`)
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
- [ ] Send email on register
- [ ] More standard user options (delete, update info, deactivate, admin)
- [ ] More endpoints:
    - [x] List URLs per user
    - [ ] Get shortcodes for a given domain
- [x] Professional archeticture and project structure
    - [x] Continue (routes)
    - [ ] Run a check with AI
- [ ] Migrations
- [ ] Deployment
- [ ] Testing
- [ ] Simple Forntend
- [ ] CI/CD?
