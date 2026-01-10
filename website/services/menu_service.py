from typing import List, Dict, Any, Optional
from website.models import FoodItem, Category
from website.repositories import (
    FoodItemRepository,
    CategoryRepository,
    FavoriteRepository,
    ReviewRepository
)
from utils import errhandler


class MenuService:
    """
    Service for menu browsing and food item operations.
    """

    def __init__(
        self,
        food_item_repo: FoodItemRepository = None,
        category_repo: CategoryRepository = None,
        favorite_repo: FavoriteRepository = None,
        review_repo: ReviewRepository = None
    ):
        self.food_item_repo = food_item_repo or FoodItemRepository()
        self.category_repo = category_repo or CategoryRepository()
        self.favorite_repo = favorite_repo or FavoriteRepository()
        self.review_repo = review_repo or ReviewRepository()

    # Menu Listing

    def get_menu_data(
        self,
        category_id: int = None,
        search: str = None,
        page: int = 1,
        per_page: int = 20,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Get complete menu data with categories and items.
        Main method for menu page.
        """
        try:
            # Get all active categories
            categories = self.category_repo.find_all_active()

            # Get food items based on filters
            if search:
                items = self.food_item_repo.search_by_name(
                    search_term=search,
                    available_only=True,
                    page=page,
                    per_page=per_page
                )
                total_items = len(items)  # Approximate for search
            elif category_id:
                items = self.food_item_repo.find_by_category(
                    category_id=category_id,
                    available_only=True,
                    page=page,
                    per_page=per_page
                )
                total_items = self.food_item_repo.count_by_category(category_id)
            else:
                items = self.food_item_repo.find_all_available(
                    page=page,
                    per_page=per_page
                )
                total_items = self.food_item_repo.count_available()

            # Get user favorites if logged in
            user_favorites = set()
            if user_id:
                favorites = self.favorite_repo.find_by_user(user_id)
                user_favorites = {fav.food_item_id for fav in favorites}

            # Format items
            formatted_items = [
                self._format_menu_item(item, item.id in user_favorites)
                for item in items
            ]

            # Format categories
            formatted_categories = [
                self._format_category(cat)
                for cat in categories
            ]

            return {
                'categories': formatted_categories,
                'items': formatted_items,
                'current_category': category_id,
                'search_term': search,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_items,
                    'total_pages': (total_items + per_page - 1) // per_page
                }
            }
        except Exception as e:
            errhandler(e, log="get_menu_data", path="menu_service")
            return {
                'categories': [],
                'items': [],
                'current_category': None,
                'search_term': None,
                'pagination': {'page': 1, 'per_page': per_page, 'total': 0, 'total_pages': 0}
            }

    def get_category_items(
        self,
        category_id: int,
        page: int = 1,
        per_page: int = 20,
        user_id: int = None
    ) -> Dict[str, Any]:
        """Get items for a specific category"""
        try:
            category = self.category_repo.get_by_id(category_id)

            if not category:
                return {
                    'category': None,
                    'items': [],
                    'pagination': {'page': 1, 'per_page': per_page, 'total': 0, 'total_pages': 0}
                }

            items = self.food_item_repo.find_by_category(
                category_id=category_id,
                available_only=True,
                page=page,
                per_page=per_page
            )

            total_items = self.food_item_repo.count_by_category(category_id)

            # Get user favorites
            user_favorites = set()
            if user_id:
                favorites = self.favorite_repo.find_by_user(user_id)
                user_favorites = {fav.food_item_id for fav in favorites}

            formatted_items = [
                self._format_menu_item(item, item.id in user_favorites)
                for item in items
            ]

            return {
                'category': self._format_category(category),
                'items': formatted_items,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_items,
                    'total_pages': (total_items + per_page - 1) // per_page
                }
            }
        except Exception as e:
            errhandler(e, log="get_category_items", path="menu_service")
            return {
                'category': None,
                'items': [],
                'pagination': {'page': 1, 'per_page': per_page, 'total': 0, 'total_pages': 0}
            }

    def search_items(
        self,
        search_term: str,
        page: int = 1,
        per_page: int = 20,
        user_id: int = None
    ) -> Dict[str, Any]:
        """Search food items by name"""
        try:
            items = self.food_item_repo.search_by_name(
                search_term=search_term,
                available_only=True,
                page=page,
                per_page=per_page
            )

            # Get user favorites
            user_favorites = set()
            if user_id:
                favorites = self.favorite_repo.find_by_user(user_id)
                user_favorites = {fav.food_item_id for fav in favorites}

            formatted_items = [
                self._format_menu_item(item, item.id in user_favorites)
                for item in items
            ]

            return {
                'search_term': search_term,
                'items': formatted_items,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': len(items),
                    'total_pages': 1
                }
            }
        except Exception as e:
            errhandler(e, log="search_items", path="menu_service")
            return {
                'search_term': search_term,
                'items': [],
                'pagination': {'page': 1, 'per_page': per_page, 'total': 0, 'total_pages': 0}
            }

    # Food Item Details

    def get_food_item_details(
        self,
        food_item_id: int,
        user_id: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete details for a single food item.
        Main method for food item detail page.
        """
        try:
            # Get item with all relationships
            item = self.food_item_repo.find_by_id_with_details(food_item_id)

            if not item:
                return None

            # Check if user has favorited
            is_favorited = False
            if user_id:
                is_favorited = self.favorite_repo.is_favorited(user_id, food_item_id)

            # Check if user has reviewed
            user_review = None
            if user_id:
                review = self.review_repo.find_by_user_and_item(user_id, food_item_id)
                if review:
                    user_review = {
                        'id': review.id,
                        'rating': review.rating,
                        'comment': review.comment,
                        'created_at': review.created_at.isoformat()
                    }

            # Get rating statistics
            avg_rating = self.food_item_repo.get_average_rating(food_item_id)
            review_count = self.food_item_repo.get_review_count(food_item_id)

            # Calculate rating distribution
            rating_distribution = self._calculate_rating_distribution(item.reviews)

            # Format reviews
            formatted_reviews = [
                {
                    'id': review.id,
                    'user_name': f"{review.user.first_name} {review.user.last_name}",
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                }
                for review in sorted(item.reviews, key=lambda r: r.created_at, reverse=True)
            ]

            # Format ingredients
            formatted_ingredients = [
                {
                    'name': ing.name,
                    'is_allergen': ing.is_allergen
                }
                for ing in item.ingredients
            ]

            # Get allergens list
            allergens = [ing.name for ing in item.ingredients if ing.is_allergen]

            return {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'image_url': item.image_url,
                'is_available': item.is_available,
                'category': {
                    'id': item.category.id,
                    'name': item.category.name
                },
                'ingredients': formatted_ingredients,
                'allergens': allergens,
                'is_favorited': is_favorited,
                'rating': {
                    'average': round(avg_rating, 1),
                    'count': review_count,
                    'distribution': rating_distribution
                },
                'reviews': formatted_reviews,
                'user_review': user_review,
                'created_at': item.created_at.isoformat() if item.created_at else None
            }
        except Exception as e:
            errhandler(e, log="get_food_item_details", path="menu_service")
            return None

    # Featured Items

    def get_featured_items(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get featured items for homepage/promotions.
        Returns popular, top-rated, and newest items.
        """
        try:
            popular = self.food_item_repo.get_popular_items(limit=6)
            top_rated = self.food_item_repo.get_top_rated_items(limit=6, min_reviews=3)
            newest = self.food_item_repo.get_newest_items(limit=6)

            return {
                'popular': [self._format_menu_item(item) for item in popular],
                'top_rated': [self._format_menu_item(item) for item in top_rated],
                'newest': [self._format_menu_item(item) for item in newest]
            }
        except Exception as e:
            errhandler(e, log="get_featured_items", path="menu_service")
            return {
                'popular': [],
                'top_rated': [],
                'newest': []
            }

    # Helper Methods

    def _format_menu_item(
        self,
        item: FoodItem,
        is_favorited: bool = False
    ) -> Dict[str, Any]:
        """Format food item for menu listing"""
        avg_rating = self.food_item_repo.get_average_rating(item.id)
        review_count = self.food_item_repo.get_review_count(item.id)

        return {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': float(item.price),
            'image_url': item.image_url,
            'is_available': item.is_available,
            'category': {
                'id': item.category.id,
                'name': item.category.name
            },
            'rating': {
                'average': round(avg_rating, 1),
                'count': review_count
            },
            'is_favorited': is_favorited
        }

    def _format_category(self, category: Category) -> Dict[str, Any]:
        """Format category for display"""
        return {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'sort_order': category.sort_order
        }

    def _calculate_rating_distribution(self, reviews: List) -> Dict[int, int]:
        """Calculate how many reviews for each star rating"""
        distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

        for review in reviews:
            if review.rating in distribution:
                distribution[review.rating] += 1

        return distribution