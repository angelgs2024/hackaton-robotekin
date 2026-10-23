from setuptools import setup

setup(
    name="hri",
    version="0.1.0",
    packages=["hri"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/hri"]),
        ("share/hri", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    entry_points={"console_scripts": [
        "pregunta = hri.pregunta:main",
        "escucha = hri.escucha:main",
        "confirma = hri.confirma:main",
    ]},
)
