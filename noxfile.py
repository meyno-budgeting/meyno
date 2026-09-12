import nox

nox.options.default_venv_backend = "uv"


@nox.session(python=["3.11", "3.12", "3.13", "3.14"])
def tests(session: nox.Session) -> None:
    session.install(".")
    session.install("pytest", "pytest-cov")
    session.run("pytest")
