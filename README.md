tibiantis-login-bot/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── character.py
│   │       └── user.py
│   ├── db/
│   │   ├── models/
│   │   │   ├── character.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── character.py
│   │   │   └── user.py
│   │   ├── crud/
│   │   │   ├── character.py
│   │   │   └── user.py
│   │   ├── base.py
│   │   └── session.py
│   ├── services/
│   │   └── tibiantis_scraper.py
│   ├── discord_bot/
│   │   └── bot.py
│   ├── core/
│   │   ├── config.py
│   │   └── logger.py
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
