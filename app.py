import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
recipes = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_form():
    if request.method == 'POST':
        recipe_name = request.form.get('recipe_name')
        material_name = request.form.get('material1_name')
        material_cost_str = request.form.get('material1_price')
        material_expiry = request.form.get('material1_expiry')

        try:
            material_cost = float(material_cost_str) if material_cost_str else 0.0
        except ValueError:
            material_cost = 0.0 # Handle cases where conversion might fail, though 'number' input type helps

        image_filename = None
        if 'recipe_image' in request.files:
            file = request.files['recipe_image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_filename = filename # Save only the filename

        recipe_data = {
            "recipe_name": recipe_name,
            "material_name": material_name,
            "material_cost": material_cost, # Stored as float
            "material_expiry": material_expiry,
            "image_filename": image_filename
        }
        recipes.append(recipe_data)

        # Print statement can be removed later, kept for now for verification
        print(f"Recipe Added: {recipe_data}")
        print(f"Current Recipes: {recipes}")


        return redirect(url_for('index'))
    return render_template('register_recipe.html')

@app.route('/recipes')
def list_recipes_view():
    sort_by = request.args.get('sort_by')

    # Process recipes to include calculated_cost and cost_rate
    recipes_with_costs = []
    for recipe_data in recipes: # Iterate over the original global recipes list
        updated_recipe = recipe_data.copy()
        updated_recipe['calculated_cost'] = updated_recipe.get('material_cost', 0.0)
        updated_recipe['cost_rate'] = "未計算"
        recipes_with_costs.append(updated_recipe)

    # Sort the list that has costs calculated
    recipes_to_display = recipes_with_costs.copy() # Work with a copy for sorting

    if sort_by == 'name':
        recipes_to_display.sort(key=lambda r: r['recipe_name'])
    elif sort_by == 'cost_asc':
        recipes_to_display.sort(key=lambda r: r['calculated_cost'])
    elif sort_by == 'cost_desc':
        recipes_to_display.sort(key=lambda r: r['calculated_cost'], reverse=True)
    # If no sort_by or unknown value, it remains as recipes_with_costs (which is in registration order)

    return render_template('list_recipes.html', recipes=recipes_to_display)

if __name__ == '__main__':
    app.run(debug=True)
