This project is an e-commerce model project. All aspect of this 
webpage is a dummy model for any type of an e-commerce business. 
In this document, we will define what an e-commerce business is 
briefly, the goal of this project, how we start a django project, 
...

An e-commerce business is an organization or platform that facilitates 
the buying and selling of goods or services over the internet. 
It leverages digital technologies to allow customers to browse products, 
place orders, make payments, and arrange for delivery or digital fulfillment, 
often providing features such as product catalogs, shopping carts, 
secure payment gateways, and customer support. E-commerce businesses can operate in various models, including business-to-consumer (B2C), 
business-to-business (B2B), consumer-to-consumer (C2C), and more, 
enabling transactions to occur seamlessly regardless of geographical boundaries.

The goal of this project is to have a fully functional e-commerce business 
model. It should be able to have a home page, a products page, a details 
page, shopping cart, secured login/logout page, email verification page, 
.....

## What is Python?

Python is a versatile, high-level programming language known for its 
readability, simplicity, and wide range of applications, 
from web development and automation to data analysis and artificial 
intelligence. Its clear syntax and extensive standard library make it 
a popular choice for both beginners and experienced developers.

### Python Version Used

This project uses **Python 3.12**, as specified in the `pyproject.toml` 
file. Python 3.12 introduces new language features and optimizations, 
ensuring compatibility with the latest Django releases and third-party 
packages.

## What is Django?

Django is a high-level Python web framework that encourages rapid 
development and clean, pragmatic design. It provides a robust set of 
tools and features out of the box, such as an ORM (Object-Relational Mapper), 
authentication, admin interface, and templating system, making it easier 
to build secure and maintainable web applications. Django follows the 
"batteries-included" philosophy, allowing developers to focus on writing 
their application without having to reinvent common solutions.

## What is a virtual environment?

A **Python virtual environment** is an isolated workspace that allows 
you to manage dependencies for a specific project without affecting the 
global Python installation. This ensures that each project can have its 
own set of packages and versions, avoiding conflicts between projects.

- **venv** is a built-in Python module that creates lightweight virtual 
environments. It is included in Python’s standard library 
(from Python 3.3 onwards) and can be used with the command 
`python -m venv <env_name>` to set up a new environment.

- **Poetry** is a modern dependency management and packaging tool for 
Python projects. It simplifies the creation and management of virtual 
environments, handles dependencies, and provides a standardized way to 
build and publish Python packages. Poetry uses the `pyproject.toml` 
file to manage project configuration and dependencies.

## Poetry Download and Install

In this project, we will be using Poetry as a Python virtual environment 
manager. To get started, follow these steps to download and install Poetry:

1. **Download and Install Poetry**  
    Open your terminal and run the following command:
    ```bash
    pip install poetry
    ```
    Alternatively, you can use the official installation script:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
2. **Verify Installation**  
    After installation, check that Poetry is installed correctly by running:
    ```bash
    poetry --version
    ```
Poetry will now be available for managing your project's 
dependencies and virtual environments. Currently, we are using 
poetry version 1.7.0.

The steps below are the way to start a Django Project, with which we 
used poetry as our virtual environment. The term 'bash' is a command 
line use on a computer terminal. Also on the command terminal, 
there is no need to type 'bash' into each command, as it is the 
process being used. 

# Starting a Django Project with Poetry

1. **Install Poetry**  
    ```bash
    pip install poetry
    ```

2. **Create a New Project Directory**  
    ```bash
    mkdir my_django_project
    cd my_django_project
    ```

3. **Initialize Poetry**  
    ```bash
    poetry init
    ```
    Follow the prompts or use `poetry new .` for a default setup.

    poetry new allows for a bare bones set up that only includes the pyproject.toml file. 

4. **Add Django as a Dependency**  
    ```bash
    poetry add django
    ```

5. **Activate the Virtual Environment**  
    ```bash
    poetry shell
    ```

6. **Start a New Django Project**  
    ```bash
    django-admin startproject config .
    ```
    Replace `config` with your desired project name.

7. **Run Initial Migrations**  
    ```bash
    python manage.py migrate
    ```

8. **Start the Development Server**  
    ```bash
    python manage.py runserver
    ```

Your Django project is now set up and running inside a Poetry-managed virtual environment.

## Understanding `pyproject.toml`

The `pyproject.toml` file is a configuration file used by modern Python 
projects to manage dependencies, build systems, and project metadata. 
The `.toml` (Tom's Obvious, Minimal Language) format is a simple, 
human-readable markup language designed for configuration files.

### What is a `.toml` File?

A `.toml` file is a plain text file that uses a straightforward syntax 
for defining key-value pairs, tables, and arrays. It is widely adopted 
in the Python ecosystem for its readability and ease of use.

### Purpose of `pyproject.toml`

In Python projects, `pyproject.toml` serves several purposes:
- **Dependency Management:** Lists all packages required for the project.
- **Build System Specification:** Defines how the project should be 
    built (e.g., using Poetry, setuptools).
- **Project Metadata:** Contains information like project name, 
    version, authors, and license.

### Python and Django Dependencies in This Project

For this Django e-commerce model, the `pyproject.toml` file (managed by Poetry) will include at least the following dependencies:

```toml
[tool.poetry]
name = "e_com_model"
version = "0.1.0"
description = "A Django-based e-commerce model project"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
django = "^4.2"
python-dotenv = "^1.1.0"
pillow = "^11.2.1"
django-mathfilters = "^1.0.0"
django-crispy-forms = "1.14.0"
django-utils-six = "^2.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

- **python:** Specifies the compatible Python version.
- **django:** Adds Django as the main web framework for the project.
- Additional dependencies (e.g., for email, authentication, or testing) 
  can be added as needed.
### Python and Django Dependencies in This Project

For this Django e-commerce model, the `pyproject.toml` file 
(managed by Poetry) will include at least the following dependencies:

```toml
[tool.poetry]
name = "e_com_model"
version = "0.1.0"
description = "A Django-based e-commerce model project"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
django = "^4.2"
python-dotenv = "^1.1.0"
pillow = "^11.2.1"
django-mathfilters = "^1.0.0"
django-crispy-forms = "1.14.0"
django-utils-six = "^2.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

- **python-dotenv:** Loads environment variables from a `.env` file, 
   useful for managing secrets and configuration.
- **pillow:** Adds image processing capabilities, often needed for 
   handling product images.
- **django-mathfilters:** Provides additional math filters for Django templates.
- **django-crispy-forms:** Improves form rendering and layout in Django.
- **django-utils-six:** Utilities for supporting Python 2 and 3 compatibility 
  (legacy support).

The `pyproject.toml` file ensures that anyone working on the project 
can easily install the correct dependencies and maintain a consistent 
development environment.