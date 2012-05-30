from flask import render_template, redirect, url_for, session, flash
from larva_library import app, db

@app.route('/')
def index():
    if session.get('user_email') is not None:
        libraries = list(db.Library.find({'User':session['user_email']}))
        return render_template('index.html', libraries=libraries)
    else:
        return render_template('index.html')

@app.route('/remove_libraries')
def remove_libraries():
    db.drop_collection('libraries')
    return redirect(url_for('index'))

#temp
@app.route('/detail/<library_name>')
def detailed_view(library_name):
    if library_name is None:
        flash('Cannot find a library without a name')
        return redirect(url_for('index'))
    else:
        library = db.Library.find_one({'User':session['user_email'],'Name':library_name})
        if library is None:
            flash('Cannot find ' + library_name + ' for current user')
            return redirect(url_for('index'))
        else:
            return render_template('index.html',
                                   detail=True,
                                   name=library['Name'],
                                   genus=library['Genus'],
                                   species=library['Species'],
                                   common_name=library['Common Name']
                                   )
    