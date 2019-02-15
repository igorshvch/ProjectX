import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='atctds_search_civil',
    version="0.3.2",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        # If any package contains *.txt files, include them:
        '': ['data/*.txt', 'data/*.pckl', 'data/pad_icon2.ico']
    },
    install_requires=['pymorphy2 >= 0.8'],
    author='Igor Shevchenko',
    author_email="igorshvch@gmail.com",
    license='PSF',
    description='Package provides tools to automate court decisions search'
)