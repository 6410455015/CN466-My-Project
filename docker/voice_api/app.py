# import os
# from dotenv import load_dotenv
# from flask import Flask

# load_dotenv()

# # Initialize Flask app
# app = Flask(__name__)

# from routes.line import line_blueprint

# app.register_blueprint(line_blueprint, url_prefix='/line')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')
import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

from routes.line import line_blueprint

app.register_blueprint(line_blueprint, url_prefix='/line')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
# import os
# from dotenv import load_dotenv
# from flask import Flask

# load_dotenv()

# # Initialize Flask app
# app = Flask(__name__)

# from routes.line import line_blueprint, register_blueprint

# # Register the LINE blueprint with URL prefix
# app.register_blueprint(line_blueprint, url_prefix='/line')

# # Additional app-specific logic for the blueprint
# register_blueprint(app)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')


