from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import pandas as pd

app = Flask(__name__)

def conectar():
    return sqlite3.connect("database.db")

def crear_tabla():
    conn = conectar()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS contactos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apellido TEXT,
        nombre TEXT,
        direccion TEXT,
        localidad TEXT,
        provincia TEXT,
        pais TEXT,
        cargo TEXT,
        telefono TEXT,
        mail TEXT,
        institucion TEXT
    )
    """)
    conn.commit()
    conn.close()

crear_tabla()

@app.route("/")
def inicio():
    q = request.args.get("q","")
    inst = request.args.get("institucion","")
    loc = request.args.get("localidad","")

    conn = conectar()
    cur = conn.cursor()

    query = "SELECT * FROM contactos WHERE 1=1"
    params = []

    if q:
        query += " AND (apellido LIKE ? OR nombre LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]

    if inst:
        query += " AND institucion LIKE ?"
        params.append(f"%{inst}%")

    if loc:
        query += " AND localidad LIKE ?"
        params.append(f"%{loc}%")

    query += " ORDER BY apellido"

    cur.execute(query, params)
    contactos = cur.fetchall()
    conn.close()

    return render_template("index.html", contactos=contactos)

@app.route("/agregar", methods=["GET","POST"])
def agregar():
    if request.method=="POST":
        datos = (
            request.form.get("apellido"),
            request.form.get("nombre"),
            request.form.get("direccion"),
            request.form.get("localidad"),
            request.form.get("provincia"),
            request.form.get("pais"),
            request.form.get("cargo"),
            request.form.get("telefono"),
            request.form.get("mail"),
            request.form.get("institucion")
        )
        conn=conectar()
        conn.execute("""
        INSERT INTO contactos (
        apellido,nombre,direccion,localidad,provincia,pais,
        cargo,telefono,mail,institucion)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, datos)
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("agregar.html")

@app.route("/editar/<int:id>", methods=["GET","POST"])
def editar(id):
    conn=conectar()
    cur=conn.cursor()

    if request.method=="POST":
        datos = (
            request.form.get("apellido"),
            request.form.get("nombre"),
            request.form.get("direccion"),
            request.form.get("localidad"),
            request.form.get("provincia"),
            request.form.get("pais"),
            request.form.get("cargo"),
            request.form.get("telefono"),
            request.form.get("mail"),
            request.form.get("institucion"),
            id
        )

        cur.execute("""
        UPDATE contactos SET
        apellido=?,nombre=?,direccion=?,localidad=?,provincia=?,
        pais=?,cargo=?,telefono=?,mail=?,institucion=?
        WHERE id=?
        """, datos)

        conn.commit()
        conn.close()
        return redirect("/")

    cur.execute("SELECT * FROM contactos WHERE id=?", (id,))
    contacto=cur.fetchone()
    conn.close()

    return render_template("editar.html", contacto=contacto)

@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn=conectar()
    conn.execute("DELETE FROM contactos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/ver/<int:id>")
def ver(id):
    conn=conectar()
    cur=conn.cursor()
    cur.execute("SELECT * FROM contactos WHERE id=?", (id,))
    c=cur.fetchone()
    conn.close()
    return render_template("ver.html", contacto=c)

@app.route("/listar")
def listar():
    conn=conectar()
    cur=conn.cursor()
    cur.execute("SELECT * FROM contactos ORDER BY apellido")
    contactos=cur.fetchall()
    conn.close()
    return render_template("listar.html", contactos=contactos)

@app.route("/exportar")
def exportar():
    conn=conectar()
    df = pd.read_sql_query("SELECT * FROM contactos", conn)
    conn.close()
    archivo="agenda.xlsx"
    df.to_excel(archivo, index=False)
    return send_file(archivo, as_attachment=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)