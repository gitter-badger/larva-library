from flask import url_for, request, redirect, flash, render_template, session, send_file, make_response, jsonify
from larva_library import app, db
from larva_library.models.library import LibrarySearch, Library
from utils import retrieve_by_terms, retrieve_all
from shapely.wkt import loads
from shapely.geometry import Point
import StringIO
import json

@app.route('/library/<ObjectId:library_id>', methods=['GET'])
def detail_view(library_id):
    if library_id is None:
        flash('Recieved an entry without an id')
        return redirect(url_for('index'))

    entry = db.Library.find_one({'_id': library_id})

    if entry is None:
        flash('Cannot find object ' + str(library_id))
        return redirect(url_for('index'))

    marker_positions = []
    # load the polygon
    if entry.geometry:
        polygon = loads(entry.geometry)
        for pt in polygon.exterior.coords:
            # Google maps is y,x not x,y
            marker_positions.append((pt[1], pt[0]))

    entry['markers'] = marker_positions

    return render_template('library_detail.html', entry=entry)

@app.route('/library/<ObjectId:library_id>.json', methods=['GET'])
def json_view(library_id):
    entry = db.Library.find_one({'_id': library_id})
    return jsonify({"results" : json.loads(entry.to_json()) })

@app.route("/library/search", methods=["POST", "GET"])
def library_search():

    if request.method == 'GET':
        return redirect(url_for('index'))

    form = LibrarySearch(request.form)

    if form.search_keywords.data is None or form.search_keywords.data == '':
        flash('Please enter a search term')
        return render_template('index.html', form=form)

    # Build query; first look for entries that belong to user, then look for entries that are marked public
    keywords = form.search_keywords.data
    entries = retrieve_by_terms(keywords, email=session.get('user_email', None), owned=form.user_owned.data)

    if len(entries) == 0:
        flash("Searching for '%s' returned 0 results" % keywords)
        return render_template('index.html', form=form)

    return render_template('library_list.html', libraries=entries)

@app.route("/library/search.json", methods=["GET"])
def library_json_search():
    email = request.args.get("email", None)
    keywords = request.args.get("terms", None)
    owned = bool(request.args.get("owned", False))

    results = retrieve_by_terms(keywords, email=email, owned=owned)
    entries = [json.loads(js.to_json()) for js in results]

    return jsonify({"results" : entries})
    

@app.route('/library')
def list_library():
    # retrieve entries marked as public and that belong to the user
    entry_list = list()
    user = session.get('user_email', None)

    entry_list = retrieve_all(user)

    if len(entry_list) == 0:
        flash('No entries exist in the library')

    return render_template('library_list.html', libraries=entry_list)

#debug
@app.route('/library/remove_entries')
def remove_libraries():
    db.drop_collection('libraries')
    return redirect(url_for('index'))