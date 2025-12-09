from app import create_app
from flask import render_template

if __name__ == '__main__':
    app = create_app()
    
    # Add root route for index
    @app.route('/')
    def index():
        return render_template('index.html')
    
    app.run(debug=True, host='localhost', port=5000)
