import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rcon_server",
    version="0.1.1",
    author="Johannes Erwerle",
    author_email="johannes.erwerle@googlemail.com",
    description="a server side implementaiton of the RCON Protocol.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/991jo/rcon-server/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
    ],
)

