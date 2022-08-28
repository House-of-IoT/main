import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hoi-client-phantexcreations",
    version="1.0.0",
    author="ronaldcolyar",
    install_requires=["websockets"],
    description="HOI client library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/House-of-IoT/HOI.py",
    project_urls={
        "Bug Tracker": "https://github.com/House-of-IoT/HOI.py/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)