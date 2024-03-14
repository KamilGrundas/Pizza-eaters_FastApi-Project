# PhotoShare REST API Project

## Overview

PhotoShare is a comprehensive REST API built with FastAPI, designed to facilitate photo sharing with robust authentication, photo management, and interactive features. It supports user roles, photo uploads with descriptions, tagging, comments, and more, leveraging JWT tokens for authentication and integrating Cloudinary for image operations.

## Features

### Authentication

- JWT token-based authentication mechanism.
- Three user roles: standard user, moderator, and administrator. The first user is always an administrator.
- Role-based access control using FastAPI decorators to check user tokens and roles.

### Photo Management

- Users can upload, delete, edit descriptions, and retrieve photos using unique links.
- Up to 5 tags can be added to each photo. Tagging is optional during photo upload.
- Tags are unique across the application. A tag is sent to the server by name; if it doesn't exist, it's created.
- Basic image operations supported via Cloudinary.
- Users can generate links to transformed images for display as URL and QR code.

### Comments

- Comment block under each photo for users to interact.
- Users can edit but not delete their comments.
- Administrators and moderators have the authority to delete comments.
- Comments include creation and edit timestamps, implementing a "one-to-many" relationship between photos and comments.


### Search and Filtering

- Photo search by keywords or tags.
- Filtering search results by rating or date added.
- Moderator and administrator capabilities to search and filter by user.

## Technical Specifications

- **Backend Framework**: FastAPI
- **Authentication**: JWT Tokens
- **Image Operations**: Cloudinary (Image Transformations) and QR Code Generation (https://pypi.org/project/qrcode/)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy

## Getting Started

1. Clone the repository to your local machine.
2. Ensure PostgreSQL is installed and running.
3. Set up a virtual environment and install dependencies from `requirements.txt`.
4. Create a `.env` file for environment variables (JWT secret key, database URL, Cloudinary credentials).
5. Run the application using Uvicorn: `uvicorn app.main:app --reload`.

## Documentation

Swagger documentation is automatically generated and accessible at `/docs` or `/redoc` paths, providing a full overview of available endpoints and operations.


## Docker Support

`Dockerfile` enables containerization, making the application easily deployable with Docker.
