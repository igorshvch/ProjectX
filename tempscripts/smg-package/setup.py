import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smg_text_ig",
    version="0.2.4",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        # If any package contains *.txt files, include them:
        '': ['data/*.txt', 'data/*.pckl']
    },
    #install_requires=['pymorphy2 >= 0.8']
)