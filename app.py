from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import json
import os
import shlex
from authlib.integrations.flask_client import OAuth
import boto3

app = Flask(__name__)
oauth = OAuth(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev")

COGNITO_DOMAIN = "https://flask-app-2e9924f0.auth.us-east-1.amazoncognito.com"
CLIENT_ID = "3n751dbue5mo0l54p1vkp7opj4"
USER_POOL_ID = "us-east-1_jH6fsG1L4"
IDENTIY_POOL_ID = "us-east-1:c2813282-b9c0-4bf3-812c-c40fcb4f066e"

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

def tf_format(k, v):
    return f"-var={k}={shlex.quote(str(v))}"

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
        action = request.form.get("action", "apply")

        data = {
            "app": request.form["app"],
            "github_repo_owner": request.form["github_repo_owner"],
            "buildspec_path": "buildspec.yml",
            "tag": request.form["tag"],
            "port": int(request.form["port"]),
            "cpu": int(request.form["cpu"]),
            "memory": int(request.form["memory"]),
            "replicas": int(request.form["replicas"])
        }

        os.makedirs("terraform", exist_ok=True)
        with open("terraform/buildspec.yml", "w") as f:
            f.write(request.form["buildspec_content"])

        terraform_vars = [tf_format(k, v) for k, v in data.items()]

        id_token = session.get('id_token')
        if not id_token:
            return redirect(url_for('login'))

        creds = get_credentials_from_identity_pool(id_token)
        os.environ["AWS_ACCESS_KEY_ID"] = creds["AccessKeyId"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = creds["SecretKey"]
        os.environ["AWS_SESSION_TOKEN"] = creds["SessionToken"]

        if action == "destroy":
            cmd = ["terraform", "destroy", "-auto-approve"] + terraform_vars
        else:
            terraform_cmds = [
                ["terraform", "init"],
                ["terraform", "apply", "-auto-approve"] + terraform_vars
            ]

            for cmd in terraform_cmds:
                result = subprocess.run(cmd, cwd="terraform", capture_output=True, text=True)
                if result.returncode != 0:
                    return f"<h2>Error ejecutando {' '.join(cmd)}:</h2><pre>{result.stderr}</pre>"

            output = subprocess.check_output(["terraform", "output", "-json"], cwd="terraform")
            outputs = json.loads(output)
            alb_dns = outputs.get("alb_dns_name", {}).get("value", "No DNS found")
            return f"""
                <h2 class='deploy-success'>¡Despliegue exitoso!</h2>
                <p><a class='deploy-link' href='http://{alb_dns}' target='_blank'>{alb_dns}</a></p>
            """

        result = subprocess.run(cmd, cwd="terraform", capture_output=True, text=True)
        if result.returncode != 0:
            return f"<h2>Error ejecutando {' '.join(cmd)}:</h2><pre>{result.stderr}</pre>"
        return """
            <div style="margin-top: 3rem; background-color: rgba(255, 99, 71, 0.1); border: 1px solid #f87171;
                padding: 1.5rem; border-radius: 16px; color: #f87171; font-family: 'Inter', sans-serif; text-align: center;">
                <h2 style="margin-bottom: 1rem;">⚠️ Infraestructura destruida</h2>
                <p>Todos los recursos han sido eliminados con éxito.</p>
            </div>
        """

    return render_template("form.html")

@app.route("/destroy", methods=["POST"])
@require_login
def destroy():
    result = subprocess.run(["terraform", "destroy", "-auto-approve"], cwd="terraform", capture_output=True, text=True)
    if result.returncode != 0:
        return f"<h2>Error al destruir:</h2><pre>{result.stderr}</pre>"
    return "<h2>Infraestructura destruida con éxito ✅</h2>"

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
