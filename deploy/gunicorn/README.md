# Deployment with Gunicorn

If you want to deploy the app in production, it's best to use gunicorn,
in which case use the configuration file gunicorn_config.py when starting
the app with supervisor.

See the supervisor/service.conf template file for how to use this.