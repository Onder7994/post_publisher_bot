import requests
from logger import Logging
from dataclasses import dataclass
from database import DbProcess

@dataclass
class ApiMethods:
    base_url: str
    api_ep: str
    logger: Logging
    db: DbProcess

    @staticmethod
    def send_api_requests(**kwargs):
        params={'per_page': 1, 'orderby': 'date', 'order': 'desc'}
        logger = kwargs.get("logger")
        if kwargs.get("method") == "GET":
            try:
                response = requests.get(url=kwargs.get("url"), params=params)
                if response.status_code == 200:
                    return response.json()
            except requests.exceptions.RequestException as err:
                logger.warning("Ошибка при отправке запроса на %s. Код ответа %s", kwargs.get("url"), response.status_code)
        return None

    def get_latest_post(self):
        request_url = f"{self.base_url}/{self.api_ep}"
        response = self.send_api_requests(method="GET", url=request_url, logger=self.logger)
        post_mapping = {}
        try:
            latest_post = response[0]
            post_url = latest_post["guid"]["rendered"]
            post_title= latest_post["title"]["rendered"]
            attach_url = latest_post["_links"]["wp:attachment"][0]["href"]
            logo_attach_response = self.send_api_requests(method="GET", url=attach_url, logger=self.logger)
            post_logo = logo_attach_response[0]["guid"]["rendered"]
            post_mapping = {
                "post_url": post_url,
                "post_title": post_title,
                "post_logo": post_logo
            }
            return post_mapping
        except (IndexError, KeyError, TypeError, AttributeError) as err:
            self.logger.error("Ошибка при чтении данных из API WP: %s", err)
        return None

    def upload_post_into_db(self):
        make_post_in_telegram = False
        column_name = self.db.column_name
        post_url = self.get_latest_post()[column_name]
        self.db.create_table()
        check_exist_post_in_db = self.db.select_data(post_url)
        if check_exist_post_in_db is None:
            self.db.inser_data(post_url)
            make_post_in_telegram = True
        else:
            if check_exist_post_in_db[column_name] != post_url:
                self.db.inser_data(post_url)
                make_post_in_telegram = True
        return make_post_in_telegram

    
            
