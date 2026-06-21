# AccessEase

Accessibility-focused electronics e-commerce platform — built for everyone, including users with disabilities. Sells mobiles, laptops, watches, earbuds, and speakers with full cart, checkout, wishlist, reviews, and admin panel.

## Run & Operate

- Flask app auto-starts via the `Accessibility-in-Digital-World` workflow
- Admin login: username=`admin` password=`Admin@123`
- DB is auto-initialized (SQLite) on first run — file: `Accessibility-in-Digital-World/accessease.db`

## Stack

- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript (vanilla)
- **Backend**: Python Flask 3.0
- **Database**: SQLite (dev) / MySQL via PyMySQL (set MYSQL_URL to switch)
- **Auth**: Flask session-based auth (users + admin)

## Where things live

- `artifacts/accessease/app.py` — Flask routes and business logic (786 lines)
- `artifacts/accessease/init_db.py` — SQLite schema + seed data initializer
- `artifacts/accessease/database/schema.sql` — MySQL schema (for MySQL deployments)
- `artifacts/accessease/templates/` — Jinja2 HTML templates
- `artifacts/accessease/static/css/style.css` — Main stylesheet (dark mode, high contrast, responsive)
- `artifacts/accessease/static/js/main.js` — Accessibility toolbar, search, chatbot, voice commands

## Architecture decisions

- Flask serves all HTML (server-rendered Jinja2 templates), not a SPA
- SQLite used by default — no external DB setup needed; MySQL supported via MYSQL_URL env var
- Accessibility toolbar (dark mode, high contrast, font size, text-to-speech, voice commands) built into every page via `base.html`
- Admin panel at `/admin` with separate session (admin_id) from user session (user_id)

## Product

- **Home**: Featured products + category previews
- **Products**: Filterable/sortable product listing with brand and price filters
- **Product Detail**: Images, reviews, add to cart/wishlist
- **Cart**: Quantity management, shipping calculation
- **Checkout**: Address form, COD/online payment selection
- **Orders**: Order history and tracking with status timeline
- **Profile**: Edit details, change password
- **Wishlist**: Saved products
- **Admin**: Dashboard, product CRUD, order management, user management
- **Accessibility toolbar**: Font size, dark mode, high contrast, read aloud (TTS), voice commands, keyboard shortcuts
