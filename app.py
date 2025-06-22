from flask import Flask, render_template, request
import subprocess
import json
import os
import shlex

app = Flask(__name__)

def tf_format(k, v):
    return f"-var={k}={shlex.quote(str(v))}"

@app.route("/", methods=["GET", "POST"])
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
            alb_dns = "url"
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
def destroy():
    result = subprocess.run(["terraform", "destroy", "-auto-approve"], cwd="terraform", capture_output=True, text=True)
    if result.returncode != 0:
        return f"<h2>Error al destruir:</h2><pre>{result.stderr}</pre>"
    return "<h2>Infraestructura destruida con éxito ✅</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
