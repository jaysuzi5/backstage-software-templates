# Documentation for ${{values.app_name}}
## This is a fastAPI application
### ${{values.app_description}}
This application has two generic endpoints:
Describe the application and container:
    - /v1/${{values.app_name}}/info
Healthcheck for the application:
    - /v1/${{values.app_name}}/health


### CRUD Endpoints:
## 2. CRUD Endpoints (Versioned)
| Method | URL Pattern           | Action             | Example             |
|--------|-----------------------|--------------------|---------------------|
| GET    | /api/v1/${{values.app_name}}         | List all ${{values.app_name}}     | /api/v1/${{values.app_name}}       |
| GET    | /api/v1/${{values.app_name}}/{id}    | Get ${{values.app_name}} by ID     | /api/v1/${{values.app_name}}/42    |
| POST   | /api/v1/${{values.app_name}}         | Create new ${{values.app_name}}    | /api/v1/${{values.app_name}}       |
| PUT    | /api/v1/${{values.app_name}}/{id}    | Update ${{values.app_name}} (full) | /api/v1/${{values.app_name}}/42    |
| PATCH  | /api/v1/${{values.app_name}}/{id}    | Update ${{values.app_name}} (partial) | /api/v1/${{values.app_name}}/42 |
| DELETE | /api/v1/${{values.app_name}}/{id}    | Delete ${{values.app_name}}        | /api/v1/${{values.app_name}}/42    |


# How to access the app?
You can access the app by accessing the URL: http://home.${{values.app_env}}.com/api/v1/${{values.app_name}}/info