from flask_admin import Admin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
admin = Admin(name="Семицветик", template_mode="bootstrap4")
metrics = PrometheusMetrics.for_app_factory(group_by="endpoint")
