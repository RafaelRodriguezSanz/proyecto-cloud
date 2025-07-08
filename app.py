from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
import subprocess
import json
import os
import shlex
import threading
import time
from authlib.integrations.flask_client import OAuth
import boto3
import re

app = Flask(__name__)
oauth = OAuth(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev")

COGNITO_DOMAIN = "https://flask-app-2581f801.auth.us-east-1.amazoncognito.com"
CLIENT_ID = "1699j2536posq0i09bml0bjdb8"
USER_POOL_ID = "us-east-1_tcdc9CIJo"
IDENTIY_POOL_ID = "us-east-1:1b1bcc0a-a4f2-48b1-9967-2c5000807873"

oauth.register(
    name='oidc',
    authority='https://cognito-idp.us-east-1.amazonaws.com/'+USER_POOL_ID,
    client_id=CLIENT_ID,
    client_secret= None,
    server_metadata_url='https://cognito-idp.us-east-1.amazonaws.com/'+USER_POOL_ID+'/.well-known/openid-configuration',
    client_kwargs={'scope': 'email openid profile'}
)

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False
)

def ansi_to_html(text):
    # Mapeo de ANSI a CSS
    ansi_colors = {
        '0': 'ansi-reset',      # Reset
        '1': 'ansi-bold',       # Bold
        '2': 'ansi-dim',        # Dim
        '4': 'ansi-underline',  # Underline
        '30': 'ansi-black',     # Black
        '31': 'ansi-red',       # Red
        '32': 'ansi-green',     # Green
        '33': 'ansi-yellow',    # Yellow
        '34': 'ansi-blue',      # Blue
        '35': 'ansi-magenta',   # Magenta
        '36': 'ansi-cyan',      # Cyan
        '37': 'ansi-white',     # White
        '90': 'ansi-bright-black',   # Bright Black
        '91': 'ansi-bright-red',     # Bright Red
        '92': 'ansi-bright-green',   # Bright Green
        '93': 'ansi-bright-yellow',  # Bright Yellow
        '94': 'ansi-bright-blue',    # Bright Blue
        '95': 'ansi-bright-magenta', # Bright Magenta
        '96': 'ansi-bright-cyan',    # Bright Cyan
        '97': 'ansi-bright-white',   # Bright White
    }
    
    def replace_ansi(match):
        codes_str = match.group(1).rstrip('m')
        if not codes_str:
            return ''
            
        codes = codes_str.split(';')
        classes = []
        
        for code in codes:
            if code in ansi_colors:
                classes.append(ansi_colors[code])
        
        if classes:
            # Si es reset, cerrar tags
            if '0' in codes:
                return '</span>'
            else:
                return f'<span class="{" ".join(classes)}">'
        else:
            return ''
    
    # Reemplazar códigos ANSI con HTML
    ansi_pattern = r'\x1b\[([0-9;]*m?)'
    text = re.sub(ansi_pattern, replace_ansi, text)
    ansi_pattern2 = r'\033\[([0-9;]*m?)'
    text = re.sub(ansi_pattern2, replace_ansi, text)
    
    return text

def tf_format(k, v):
    return f"-var={k}={shlex.quote(str(v))}"

def stream_terraform_command(cmd, cwd="terraform"):
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            bufsize=1
        )
        
        for line in iter(process.stdout.readline, ''):
            if line:
                processed_line = ansi_to_html(line.rstrip())
                yield processed_line
        
        process.wait()
        
        if process.returncode != 0:
            yield f"TERRAFORM_ERROR: Command failed with return code {process.returncode}"
        else:
            yield "TERRAFORM_SUCCESS: Command completed successfully"
            
    except Exception as e:
        yield f"TERRAFORM_ERROR: {str(e)}"

def require_login(f):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/", methods=["GET", "POST"])
@require_login
def index():
    if request.method == "POST":
        session['terraform_data'] = {
            "app": request.form["app"],
            "github_repo_owner": request.form["github_repo_owner"],
            "buildspec_path": "buildspec.yml",
            "tag": request.form["tag"],
            "port": int(request.form["port"]),
            "cpu": int(request.form["cpu"]),
            "memory": int(request.form["memory"]),
            "replicas": int(request.form["replicas"]),
            "buildspec_content": request.form["buildspec_content"],
            "action": request.form.get("action", "apply")
        }
        
        # Preparar buildspec.yml
        os.makedirs("terraform", exist_ok=True)
        with open("terraform/buildspec.yml", "w") as f:
            f.write(request.form["buildspec_content"])
        
        # Retornar JSON para indicar que se debe usar SSE
        return jsonify({"status": "ready", "use_sse": True})

    return render_template("form.html")

@app.route("/terraform-stream")
@require_login
def terraform_stream():
    """Ruta SSE para streamear el output de Terraform"""
    
    # Capturar datos de la sesión ANTES del generador
    terraform_data = session.get('terraform_data', {})
    id_token = session.get('id_token')
    
    if not terraform_data:
        return "data: TERRAFORM_ERROR: No data found in session\n\n", 200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    
    if not id_token:
        return "data: TERRAFORM_ERROR: No authentication token found\n\n", 200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    
    def generate():
        try:
            creds = get_credentials_from_identity_pool(id_token)
            os.environ["AWS_ACCESS_KEY_ID"] = creds["AccessKeyId"]
            os.environ["AWS_SECRET_ACCESS_KEY"] = creds["SecretKey"]
            os.environ["AWS_SESSION_TOKEN"] = creds["SessionToken"]
            
            action = terraform_data.get("action", "apply")
            if action == "destroy":
                commands = [["terraform", "destroy", "-auto-approve"]]
            else:
                commands = [
                    ["terraform", "init"],
                    ["terraform", "apply", "-auto-approve"]
                ]
            
            terraform_vars = [tf_format(k, v) for k, v in terraform_data.items() if k not in ["buildspec_content", "action"]]
            
            for cmd_base in commands:
                if cmd_base[0] == "terraform" and cmd_base[1] in ["apply", "destroy"]:
                    cmd = cmd_base + terraform_vars
                else:
                    cmd = cmd_base
                
                yield f"data: TERRAFORM_CMD: {' '.join(cmd)}\n\n"
                
                for line in stream_terraform_command(cmd):
                    if line.startswith("TERRAFORM_ERROR:"):
                        yield f"data: {line}\n\n"
                        return
                    elif line.startswith("TERRAFORM_SUCCESS:"):
                        yield f"data: {line}\n\n"
                        break
                    else:
                        yield f"data: {line}\n\n"
            
            if action == "apply":
                try:
                    output = subprocess.check_output(["terraform", "output", "-json"], cwd="terraform")
                    outputs = json.loads(output)
                    alb_dns = outputs.get("alb_dns_name", {}).get("value", "No DNS found")
                    yield f"data: TERRAFORM_OUTPUT: {alb_dns}\n\n"
                except Exception as e:
                    yield f"data: TERRAFORM_ERROR: Could not get outputs: {str(e)}\n\n"
            
            yield "data: TERRAFORM_COMPLETE\n\n"
            
        except Exception as e:
            yield f"data: TERRAFORM_ERROR: {str(e)}\n\n"
    
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no'
    })

@app.route("/destroy", methods=["POST"])
@require_login
def destroy():
    session['terraform_data'] = {
        "action": "destroy"
    }
    
    id_token = session.get('id_token')
    if not id_token:
        return jsonify({"error": "No authentication token found"}), 401
    
    creds = get_credentials_from_identity_pool(id_token)
    os.environ["AWS_ACCESS_KEY_ID"] = creds["AccessKeyId"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = creds["SecretKey"]
    os.environ["AWS_SESSION_TOKEN"] = creds["SessionToken"]
    
    return jsonify({"status": "ready", "use_sse": True})

@app.route("/login")
def login():
    return oauth.oidc.authorize_redirect('http://localhost:80/auth/callback')

@app.route("/auth/callback")
def auth_callback():
    token = oauth.oidc.authorize_access_token()
    id_token = token["id_token"]
    session['id_token'] = id_token
    session['user'] = token["userinfo"]
    session.permanent = True
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    logout_url = f"{COGNITO_DOMAIN}/logout?client_id={CLIENT_ID}&logout_uri=http://localhost:80/"
    return redirect(logout_url)

def get_credentials_from_identity_pool(id_token):
    user_pool_provider = "cognito-idp.us-east-1.amazonaws.com/" + USER_POOL_ID

    cognito_identity = boto3.client("cognito-identity", region_name="us-east-1")
    identity = cognito_identity.get_id(
        IdentityPoolId=IDENTIY_POOL_ID,
        Logins={user_pool_provider: id_token}
    )

    credentials = cognito_identity.get_credentials_for_identity(
        IdentityId=identity["IdentityId"],
        Logins={user_pool_provider: id_token}
    )

    return credentials["Credentials"]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
