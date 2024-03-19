from secret import access_secret_version

SUPPORT_EMAIL = access_secret_version("support-email")
API_KEY = access_secret_version("mailersend-api-key")  # no default value
