
import shelve

def track_visitors():
    # Open the shelve database
    with shelve.open('visitor_count') as db:
        # Increment the visitor count
        if 'visitor_count' in db:
            visitor_count = db['visitor_count'] + 1
        else:
            visitor_count = 1
        # Store the updated visitor count
        db['visitor_count'] = visitor_count
    # Return the visitor count in HTML
    return "<html><body><h1>Welcome!</h1><p>You are visitor number {}</p></body></html>".format(visitor_count)