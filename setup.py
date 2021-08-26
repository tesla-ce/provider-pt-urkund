import os
import setuptools


with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'README.md')), "r") as fh:
    long_description = fh.read()

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'requirements.txt')), "r") as fh:
    requirements_raw = fh.read()
    requirements_list = requirements_raw.split('\n')
    requirements = []
    for req in requirements_list:
        if not req.strip().startswith('#') and len(req.strip()) > 0:
            requirements.append(req)

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "src/urkund/data/VERSION")), "r") as fh:
    version = fh.read()

setuptools.setup(
    name="tesla-ce-provider-pt-urkund",
    version=version,
    author="Roger Muñoz Bernaus",
    author_email="rmunozber@uoc.edu",
    description="TeSLA CE Urkund Plagiarism Provider",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tesla-ce.github.io",
    project_urls={
        'Documentation': 'https://tesla-ce.github.io/provider-pt-urkund/',
        'Source': 'https://github.com/tesla-ce/provider-pt-urkund',
    },
    packages=setuptools.find_packages('src', exclude='__pycache__'),
    package_dir={'': 'src'},  # tell distutils packages are under src
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    package_data={
        '': ['*.cfg', 'VERSION'],
        'urkund': [
            'data/*',
                    ],
    },
    include_package_data=True,
    install_requires=requirements
)
