from flask import current_app
from itsdangerous import URLSafeSerializer

# Route Info Serializer
class RouteSerializer:
    @staticmethod
    def get_serializer():
        secret_key = current_app.config['SECRET_KEY']
        return URLSafeSerializer(secret_key, salt="food-item-salt")