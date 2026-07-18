from ..models import Category, SubCategory, Product

def search_categories(query):
    """
    Search for categories based on the provided query.

    Args:
        query (str): The search query string.
    
    """
    return Category.objects.filter(title__icontains=query, is_active=True)[:5]

def search_subcategories(query):
    """
    Search for subcategories based on the provided query.

    Args:
        query (str): The search query string.
    
    """
    return SubCategory.objects.filter(title__icontains=query, is_active=True)[:5]

def search_products(query):
    """
    Search for products based on the provided query.

    Args:
        query (str): The search query string.
    
    """
    return Product.objects.select_related('subcategory', 'subcategory__category').filter(title__icontains=query, product_status="publish")[:10]