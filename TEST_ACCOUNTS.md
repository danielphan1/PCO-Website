# Test Accounts

Local development accounts for QA testing. **Do not commit to production.**

## Admin Account
- **Email:** admin@test.com
- **Password:** TestAdmin123
- **Role:** admin
- **Name:** Test Admin

## Member Account
- **Email:** member@test.com
- **Password:** TestMember123
- **Role:** member
- **Name:** Test Member

## Officer Accounts (password: TestOfficer123)
- **president@test.com** — Alex Chen (president)
- **vp@test.com** — Jamie Torres (vp)
- **treasurer@test.com** — Sam Park (treasurer)

---

_Accounts live in the local PostgreSQL Docker container (`docker-db-1`, database `pco`)._
_To reset: delete and recreate via `docker exec docker-db-1 psql -U postgres -d pco`._
