A project made for SPbSPU's discipline "Technologies of quality software development".

МИГРАЦИЯ БАЗЫ ДАННЫХ:
Создать папку миграции: alembic init migrations

в [alembic.ini](alembic.ini) поменять
sqlalchemy.url = postgresql://%(DB_USER)s:%(DB_PASS)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s

в [env.py](migrations%2Fenv.py) поменять
config = context.config
section = config.config_ini_section
config.set_section_option(section, "DB_USER", DB_USER)
config.set_section_option(section, "DB_PASS", DB_PASS)
config.set_section_option(section, "DB_HOST", DB_HOST)
config.set_section_option(section, "DB_PORT", DB_PORT)
config.set_section_option(section, "DB_NAME", DB_NAME)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = metadata

Создать первый "commit" миграции: alembic revision --autogenerate -m "Database create"

Создание миграции: alembic upgrade 699e6767d414 ( Посмотреть в директории [versions](migrations%2Fversions) )