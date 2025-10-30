from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = '!@#$%'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskmysql'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'inpEmail' in request.form and 'inpPass' in request.form:
        email = request.form['inpEmail']
        passwd = request.form['inpPass']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, passwd))
        result = cur.fetchone()
        if result:
            session['is_logged_in'] = True
            session['username'] = result[1]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', msg='Email atau password salah!')
    return render_template('login.html')

@app.route('/home')
def home():
    if 'is_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        data = cur.fetchall()
        cur.close()
        return render_template('home.html', users=data)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'inpUser' in request.form and 'inpEmail' in request.form and 'inpPass' in request.form:
        username = request.form['inpUser']
        email = request.form['inpEmail']
        passwd = request.form['inpPass']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, passwd))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('is_logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/api/users', methods=['GET'])
def api_get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    cur.close()

    users = []
    for row in rows:
        users.append({
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'email': row[3],
            'alamat': row[4],
            'nomor_telepon': row[5]
        })

    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def api_add_user():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    alamat = data['alamat']
    nomor_telepon = data['nomor_telepon']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO users (username, password, email, alamat, `nomor telepon`) VALUES (%s, %s, %s, %s, %s)",
        (username, password, email, alamat, nomor_telepon)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'User berhasil ditambahkan!'}), 201


if __name__ == '__main__':
    app.run(debug=True)
