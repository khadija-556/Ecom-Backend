from .selectors import search_categories, search_subcategories, search_products

def universal_search(query):
    """
    Perform a universal search across categories, subcategories, and products.

    Args:
        query (str): The search query string.

    """
    results = []

    #Categories

    for category in search_categories(query):
        results.append({
            "type": "category",
            "id": category.id,
            "title": category.title,
            "slug": category.slug,
        })

    # Subcategories

    for subcategory in search_subcategories(query):
        results.append({
            "type": "subcategory",
            "id": subcategory.id,
            "title": subcategory.title,
            "slug": subcategory.slug,
            "category":{
                "id": subcategory.category.id,
                "title": subcategory.category.title,
                "slug": subcategory.category.slug,
            }

        })

    # Products

    for product in search_products(query):
        results.append({
            "type": "product",
            "id": product.id,
            "title": product.title,
            "slug": product.slug,

            "subcategory": {
                "id": product.subcategory.id,
                "title": product.subcategory.title,
            } if product.subcategory else None,


            "category": {
                "id": product.subcategory.category.id,
                "title": product.subcategory.category.title,
            } if product.subcategory else None,
        })

    return results