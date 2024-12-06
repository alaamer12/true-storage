from setuptools import setup, find_packages

setup(
    name='true-storage',
    version='0.1.0',
    packages=find_packages(),
    # url='https://github/alaamer12/true-storage',
    license='MIT',
    author='Alaamer',
    author_email='alaamerthefirst@gmail.com',
    description='A boilerplate utility package',
    long_description="A Comprehensive yet simple boilerplate package to solve simple but yet impactful problems",
    long_description_content_type='text/markdown',
    install_requires=[
        'redis>=4.5.0',
        'python-dotenv>=1.0.0'
    ],
    keywords=['storage', 'cache', 'session'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        # 'Bug Reports': 'https://github.com/alaamer12/true-storage/issues',
        # 'Source': 'https://github.com/alaamer12/true-storage',
        # 'Documentation': 'https://github.com/alaamer12/true-storage',
        # 'Website': 'https://github.com/alaamer12/true-storage',
    }
)
