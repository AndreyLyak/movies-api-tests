from clients.movies_client import MoviesAPI
from clients.reviews_client import ReviewsAPI


class ApiManager:

    def __init__(self, session):
        self.session = session
        self.movies_api = MoviesAPI(session)
        self.reviews_api = ReviewsAPI(session)