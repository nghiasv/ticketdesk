import environ

env = environ.Env()
SECRET_KEY = "DJANGO_SECRET_KEY"
DATABASES = {"default": "database_url"}
AUTH_USER_MODEL = "accounts.User"
INSTALLED_APP = ["apps.accounts", "apps.tickets"]
