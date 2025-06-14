import pytest
import os
import io # For BytesIO
from app import app as flask_app
from app import recipes as global_recipes_list
from werkzeug.datastructures import FileStorage # For simulating file uploads

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms

    # Determine project root dynamically to set UPLOAD_FOLDER correctly
    # __file__ is tests/test_app.py, so dirname(__file__) is tests/
    # dirname(dirname(__file__)) is the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flask_app.config['UPLOAD_FOLDER'] = os.path.join(project_root, 'static', 'uploads')

    upload_folder = flask_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    else:
        # Clean up upload folder before each test
        for f in os.listdir(upload_folder):
            os.remove(os.path.join(upload_folder, f))

    global_recipes_list.clear() # Clear recipes list before each test

    with flask_app.test_client() as client:
        yield client

def test_home_page(client):
    """トップページ (/) が正常に表示されるかテスト"""
    response = client.get('/')
    assert response.status_code == 200
    # Adjusted based on actual content from previous steps
    assert b"Hello, Flask!" in response.data
    assert b"Register a new Recipe" in response.data
    assert b"登録レシピ一覧を見る" in response.data

def test_register_page_get(client):
    """レシピ登録ページ (/register) がGETリクエストで正常に表示されるかテスト"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register New Recipe" in response.data

def test_recipes_page_empty(client):
    """レシピ一覧ページ (/recipes) が (レシピがない状態で) 正常に表示されるかテスト"""
    response = client.get('/recipes')
    assert response.status_code == 200
    assert b"Registered Recipes" in response.data
    assert b"まだレシピが登録されていません。" in response.data

# New test cases
def test_register_recipe_post_and_redirect(client):
    """レシピ登録POSTとリダイレクト、一覧表示、画像アップロードをテスト"""
    upload_folder = flask_app.config['UPLOAD_FOLDER']

    # Dummy image file data using BytesIO
    image_content = b"this is a dummy png image"
    dummy_image_stream = io.BytesIO(image_content)
    dummy_image = FileStorage(
        stream=dummy_image_stream,
        filename="test_image.png",
        content_type="image/png"
    )

    recipe_data = {
        'recipe_name': 'Test Cake',
        'material1_name': 'Flour',
        'material1_price': '100.50',
        'material1_expiry': '30',
        'recipe_image': dummy_image
    }
    response_post = client.post('/register', data=recipe_data, content_type='multipart/form-data')

    # POST should redirect to the recipes list page
    assert response_post.status_code == 302
    # Check if location is /recipes or /recipes/ (Flask behavior can vary slightly)
    assert response_post.location.endswith('/recipes') or response_post.location.endswith('/recipes/')


    # Follow the redirect
    response_get_recipes = client.get(response_post.location)
    assert response_get_recipes.status_code == 200
    assert b"Test Cake" in response_get_recipes.data
    # Assuming material name is not directly displayed in the list, but cost is.
    # The list_recipes.html shows: "{{ recipe.recipe_name }} - 原価: {{ "%.2f"|format(recipe.calculated_cost) }}円 - 原価率: {{ recipe.cost_rate }}"
    assert b"100.50" in response_get_recipes.data # Check for cost
    assert b"test_image.png" in response_get_recipes.data # Check if image filename is in the HTML (e.g., in img src)

    # Check if the image file was uploaded
    # secure_filename in app.py might alter "test_image.png" if it contains unsafe chars.
    # Assuming "test_image.png" is safe or testing the exact output of secure_filename is out of scope here.
    uploaded_files = os.listdir(upload_folder)
    assert "test_image.png" in uploaded_files

    # Verify the content of the global_recipes_list
    assert len(global_recipes_list) == 1
    registered_recipe = global_recipes_list[0]
    assert registered_recipe['recipe_name'] == 'Test Cake'
    assert registered_recipe['material_name'] == 'Flour'
    assert registered_recipe['material_cost'] == 100.50  # Should be float
    assert registered_recipe['image_filename'] == "test_image.png" # Assuming secure_filename doesn't change it

def test_cost_calculation_display(client):
    """原価計算が正しく表示されるかテスト (画像なし)"""
    recipe_data = {
        'recipe_name': 'Simple Jelly',
        'material1_name': 'Gelatin',
        'material1_price': '50.25',
        'material1_expiry': '100',
        # No recipe_image key, or it's None/empty FileStorage
    }
    # When posting form data without files, content_type can be 'application/x-www-form-urlencoded' (default for client.post if no files)
    # or 'multipart/form-data' if you set it. Let's be explicit.
    response_post = client.post('/register', data=recipe_data, content_type='multipart/form-data')
    assert response_post.status_code == 302 # Should redirect

    response = client.get('/recipes') # After redirect
    assert response.status_code == 200
    assert b"Simple Jelly" in response.data
    # Check for the cost, formatted as "50.25円" in list_recipes.html
    # The format filter "%.2f"|format(value) produces a string.
    assert b"50.25" in response.data
    assert b"画像なし" in response.data # "(画像なし)" should be present

    # Verify global list
    assert len(global_recipes_list) == 1
    registered_recipe = global_recipes_list[0]
    assert registered_recipe['recipe_name'] == 'Simple Jelly'
    assert registered_recipe['material_cost'] == 50.25
    assert registered_recipe['image_filename'] is None # No image uploaded

def test_register_recipe_without_image(client):
    """画像なしでレシピを登録するテスト"""
    recipe_data = {
        'recipe_name': 'No Image Soup',
        'material1_name': 'Water',
        'material1_price': '1.00',
        'material1_expiry': '1',
    }
    response_post = client.post('/register', data=recipe_data, content_type='multipart/form-data')
    assert response_post.status_code == 302

    response_get_recipes = client.get(response_post.location)
    assert response_get_recipes.status_code == 200
    assert b"No Image Soup" in response_get_recipes.data
    assert b"1.00" in response_get_recipes.data # Cost
    assert b"(画像なし)" in response_get_recipes.data

    assert len(global_recipes_list) == 1
    registered_recipe = global_recipes_list[0]
    assert registered_recipe['recipe_name'] == 'No Image Soup'
    assert registered_recipe['image_filename'] is None

# Helper to check for secure_filename behavior if needed (example)
# from werkzeug.utils import secure_filename as werkzeug_secure_filename
# def test_secure_filename_behavior():
#     assert werkzeug_secure_filename("test image.png") == "test_image.png"
#     assert werkzeug_secure_filename("../../../etc/passwd") == "etc_passwd"

# test_app.py
# (Existing imports and fixtures)

def test_sorting_recipes(client):
    """レシピ一覧のソート機能が正しく動作するかテスト"""
    # Add a few recipes with varying names and costs
    recipes_data = [
        {'recipe_name': 'Apple Pie', 'material1_name': 'Apples', 'material1_price': '150.00', 'material1_expiry': '7'},
        {'recipe_name': 'Banana Bread', 'material1_name': 'Bananas', 'material1_price': '120.50', 'material1_expiry': '5'},
        {'recipe_name': 'Carrot Cake', 'material1_name': 'Carrots', 'material1_price': '180.75', 'material1_expiry': '10'},
    ]
    for data in recipes_data:
        client.post('/register', data=data, content_type='multipart/form-data')

    # Test sort by name
    response_name_sort = client.get('/recipes?sort_by=name')
    assert response_name_sort.status_code == 200
    content_name_sort = response_name_sort.data.decode('utf-8')
    # Expected order: Apple Pie, Banana Bread, Carrot Cake
    assert content_name_sort.find("Apple Pie") < content_name_sort.find("Banana Bread") < content_name_sort.find("Carrot Cake")

    # Test sort by cost ascending
    response_cost_asc_sort = client.get('/recipes?sort_by=cost_asc')
    assert response_cost_asc_sort.status_code == 200
    content_cost_asc_sort = response_cost_asc_sort.data.decode('utf-8')
    # Expected order: Banana Bread (120.50), Apple Pie (150.00), Carrot Cake (180.75)
    assert content_cost_asc_sort.find("Banana Bread") < content_cost_asc_sort.find("Apple Pie") < content_cost_asc_sort.find("Carrot Cake")

    # Test sort by cost descending
    response_cost_desc_sort = client.get('/recipes?sort_by=cost_desc')
    assert response_cost_desc_sort.status_code == 200
    content_cost_desc_sort = response_cost_desc_sort.data.decode('utf-8')
    # Expected order: Carrot Cake (180.75), Apple Pie (150.00), Banana Bread (120.50)
    assert content_cost_desc_sort.find("Carrot Cake") < content_cost_desc_sort.find("Apple Pie") < content_cost_desc_sort.find("Banana Bread")

    # Test registration order (default, or sort_by unspecified)
    # Clear and re-add in specific order for this test
    global_recipes_list.clear()
    client.post('/register', data=recipes_data[2], content_type='multipart/form-data') # Carrot Cake first
    client.post('/register', data=recipes_data[0], content_type='multipart/form-data') # Apple Pie second
    client.post('/register', data=recipes_data[1], content_type='multipart/form-data') # Banana Bread third

    response_default_sort = client.get('/recipes')
    assert response_default_sort.status_code == 200
    content_default_sort = response_default_sort.data.decode('utf-8')
    # Expected order: Carrot Cake, Apple Pie, Banana Bread
    assert content_default_sort.find("Carrot Cake") < content_default_sort.find("Apple Pie") < content_default_sort.find("Banana Bread")
