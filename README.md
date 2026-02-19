# FastAPI URL Shortener

A minimal URL shortener built with **FastAPI** and **SQLAlchemy Core**.  
It stores shortened URLs in a database, lists stored URLs, and redirects short codes to the original URL while recording visits.

## Features

- Create a shortened URL (`POST /urls`)
- List all shortened URLs (`GET /urls`)
- Redirect by code and record a visit (`GET /{url_code}`)

## Future Improvement

My purpose of building this app is to implement backend development concepts I have learned so far. Naturally, there are a lot of improvements that will be implemented as I learn.

- [x] ORMs
- [ ] Users
- [ ] Auth
- [ ] More endpoints:
    - [ ] List URLs per user
    - [ ] Retrieve URL by code without redirecting
    - [ ] Get shortcodes for a given domain
- [ ] Professional archeticture and project structure
- [ ] Migrations
- [ ] Deployment
- [ ] Testing
- [ ] Simple Forntend
- [ ] CI/CD?
