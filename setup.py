import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

PACKAGES = setuptools.find_packages("src")

setuptools.setup(
    name="Vira TAAVON Website",
    version="0.1.0",
    author="Vira Backend Team",
    author_email="info@Vira.com",
    description="Vira TAAVON Website",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.Vira.com/backend/vira",
    packages=PACKAGES,
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8.2",
)
