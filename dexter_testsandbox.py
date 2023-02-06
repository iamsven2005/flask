from flask import Flask, render_template, request, redirect
import shelve

app = Flask(__name__)

@app.route('/')
def index():
    # Open the shelve database and retrieve the list of stored images
    db = shelve.open('images_db')
    images = db.get('images', [])
    db.close()
    
    # Render the HTML template with the list of images
    return render_template('test.html', images=images)

@app.route('/upload', methods=['POST'])
def upload():
    # Retrieve the uploaded image from the request
    image = request.files.get('image')
    
    # Save the image to the shelve database
    db = shelve.open('images_db')
    images = db.get('images', [])
    images.append(image)
    db['images'] = images
    db.close()
    
    # Redirect the user back to the main page
    return redirect('/')

if __name__ == '__main__':
    app.run(debug="True")
