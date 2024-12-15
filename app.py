from flask import Flask, render_template, request
from test import estimate_property_value

app = Flask(__name__)
# prix terrain mètre carré 
NEIGHBORHOOD_PRICES = {
    "centre urbain nord": 3500,
    "ariana": 2200,
    "mutuelleville": 2700,
    "alain savary": 2900,
    "menzah 1": 2450,
    "menzah 4": 2500
}
@app.route('/', methods=['GET', 'POST'])
def property_valuation():
    result = None
    property_details = {}  # Initialize property_details

    if request.method == 'POST':
        try:
            property_details = {
                'size': int(request.form['size']),
                'rooms': int(request.form['rooms']),
                'bathrooms': int(request.form['bathrooms']),
                'parkings': int(request.form['parkings']),
                'condition': request.form['condition'],
                'standing': request.form['standing'],
                'pty_type': request.form['pty_type'],
                'market_demand': int(request.form['market_demand']),
                'neighborhood': request.form['neighborhood'],
                'artery': request.form['artery'],
                'amenities': request.form.getlist('amenities'),
                'price_per_sqm': float(request.form.get('price_per_sqm', NEIGHBORHOOD_PRICES[request.form['neighborhood']]))
            }
            
            result = estimate_property_value(**property_details)
        except Exception as e:
            result = {"error": str(e) + property_details}
    
    return render_template('valuation.html', result=result,property_details=property_details)

if __name__ == '__main__':
    app.run(debug=True)