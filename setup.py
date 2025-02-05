from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='async_flow',
    version='0.1.0',
    description='A high-performance load balancer with health checks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Diva Dugar',
    author_email='divadugar@gmail.com',
    url='https://github.com/divan009/async_flow',  # Replace with your project's URL
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'aiohttp>=3.8.0',
        'pydantic>=1.8.0',
        'pyyaml>=6.0',
        'toml>=0.10.2',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-asyncio>=0.15.0',
            'black>=22.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'async_flow=async_flow.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',  # Choose your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)


if __name__ == '__main__':
    print(this_directory)