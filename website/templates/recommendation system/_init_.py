from flask import Flask, render_template, request
import tensorflow as tf
import numpy as np
import shelve
import os

# Load the trained model
model = tf.keras.models.load_model('my_model.h5')

# Set the input and output dimensions
input_dim = model.input_shape[1]
output_dim = model.output_shape[1]

# Initialize the Flask app
app = Flask(__name__)

# Set the route for the index page
@app.route('/')
def index():
  return render_template('index.html')

# Set the route for the chat endpoint
@app.route('/chat', methods=['GET', 'POST'])
def chat():
  # If a GET request is made, return the conversation history
  if request.method == 'GET':
    # Open the conversation history
    with shelve.open('conversation') as db:
      # Get the conversation history
      conversation = db.get('conversation', [])
      # Return the conversation history as a JSON object
      return {'conversation': conversation}
  # If a POST request is made, send the input to the chatbot and return the response
  elif request.method == 'POST':
    # Get the user's input
    input = request.json['input']
    # Preprocess the input
    input = np.array(input)
    input = np.expand_dims(input, 0)
    input = tf.one_hot(input, input_dim)
    # Get the chatbot's response
    response = model.predict(input)
    response = np.argmax(response, axis=-1)
    response = np.squeeze(response)
    response = int(response)
    response = response.tolist()
    response = response.decode()
    # Update the conversation history
    with shelve.open('conversation') as db:
      # Get the conversation history
      conversation = db['conversation']
      # Add the input and response to the conversation history
      conversation.append((input, response))
      # Save the updated conversation history
      db['conversation'] = conversation
    # Return the response as a JSON object
    return {'response': response}
@app.route('/get_shelve_data')
def get_shelve_data_route():
    data = chat()
    return data

# Run the app
if __name__ == '__main__':
  app.run(debug=True)
