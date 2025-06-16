from flask import Flask, render_template, request, redirect, url_for
import os
import csv

app = Flask(__name__)
DATA_FOLDER = 'data'
CSV_FILE = os.path.join(DATA_FOLDER, 'inventory.csv')

# Ensure data folder exists
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Initialize CSV file with headers if it doesn't exist or is empty
if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'quantity', 'unit_price'])
        # Optionally add a sample item
        # writer.writerow(['1', 'Sample Item', '10', '5.99'])


def read_inventory():
    items = []
    if not os.path.exists(CSV_FILE):
        return items
    with open(CSV_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert to appropriate types
            row['id'] = int(row['id'])
            row['quantity'] = int(row['quantity'])
            row['unit_price'] = float(row['unit_price'])
            items.append(row)
    return items

def write_inventory(items):
    with open(CSV_FILE, 'w', newline='') as f:
        fieldnames = ['id', 'name', 'quantity', 'unit_price']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # Ensure all items are dictionaries as expected by DictWriter
        processed_items = []
        for item in items:
            if isinstance(item, dict):
                processed_items.append(item)
            else:
                # This case should ideally not happen if data is handled correctly
                print(f"Warning: Skipping non-dict item: {item}")
        writer.writerows(processed_items)


def get_next_id(items):
    if not items:
        return 1
    return max(int(item['id']) for item in items) + 1

@app.route('/')
def home():
    inventory = read_inventory()
    return render_template('index.html', inventory=inventory, next_id=get_next_id(inventory))

@app.route('/add', methods=['POST'])
def add_item():
    inventory = read_inventory()
    item_name = request.form['name']
    item_quantity = int(request.form['quantity'])
    item_price = float(request.form['unit_price'])

    new_item = {
        'id': get_next_id(inventory),
        'name': item_name,
        'quantity': item_quantity,
        'unit_price': item_price
    }
    inventory.append(new_item)
    write_inventory(inventory)
    return redirect(url_for('home'))

@app.route('/update/<int:item_id>', methods=['POST'])
def update_item(item_id):
    inventory = read_inventory()
    new_quantity = int(request.form['quantity'])
    for item in inventory:
        if item['id'] == item_id:
            item['quantity'] = new_quantity
            break
    write_inventory(inventory)
    return redirect(url_for('home'))

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    inventory = read_inventory()
    inventory = [item for item in inventory if item['id'] != item_id]
    write_inventory(inventory)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Ensure the app listens on 0.0.0.0 for Render
    app.run(debug=False, host='0.0.0.0', port=port) # Important: Set debug=False for production
