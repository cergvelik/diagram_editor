from sqlalchemy import URL

class Config():

    def Get_URL():
        return URL.create(
            "postgresql+pg8000",
            username="dbuser",
            password="kx@jj5/g",
            host="pghost10",
            database="appdb",
        )