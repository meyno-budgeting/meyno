import nox

nox.options.default_venv_backend = "uv"


@nox.session(python=["3.11", "3.12", "3.13", "3.14"])
def tests(session: nox.Session) -> None:
    session.install(".")
    session.install("pytest", "pytest-cov")
    session.run("pytest")


@nox.session(python="3.15")
def tests_315(session: nox.Session) -> None:
    session.env["PYTHONPATH"] = "src"

    session.install(
        "alembic>=1.20,<1.21",
        "pydantic>=2.13.0,<3.0",
        "sqlalchemy>=2.0,<2.1",
        "pytest>=9.0,<10.0",
        "pytest-cov>=7.1,<8.0",
    )

    session.run("pytest")
