import db_utils
from db_utils import DB

db = DB()

db.cursor.execute(
    "DROP TABLE `site_users` ;"
)