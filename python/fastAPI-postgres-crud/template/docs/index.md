# Documentation for ${{values.app_name}}
### fastAPI: ${{values.app_description}}


Test: ${{values.app_name_capitalized}} (should be capitalized)


This application has two generic endpoints:

| Method | URL Pattern           | Description             |
|--------|-----------------------|--------------------|
| GET    | /api/v1/${{values.app_name}}/info         | Basic description of the application and container     |
| GET    | /api/v1/${{values.app_name}}/health    | Health check endpoint     |



## CRUD Endpoints:
| Method | URL Pattern           | Description             | Example             |
|--------|-----------------------|--------------------|---------------------|
| GET    | /api/v1/${{values.app_name}}         | List all ${{values.app_name}}     | /api/v1/${{values.app_name}}       |
| GET    | /api/v1/${{values.app_name}}/{id}    | Get ${{values.app_name}} by ID     | /api/v1/${{values.app_name}}/42    |
| POST   | /api/v1/${{values.app_name}}         | Create new ${{values.app_name}}    | /api/v1/${{values.app_name}}       |
| PUT    | /api/v1/${{values.app_name}}/{id}    | Update ${{values.app_name}} (full) | /api/v1/${{values.app_name}}/42    |
| PATCH  | /api/v1/${{values.app_name}}/{id}    | Update ${{values.app_name}} (partial) | /api/v1/${{values.app_name}}/42 |
| DELETE | /api/v1/${{values.app_name}}/{id}    | Delete ${{values.app_name}}        | /api/v1/${{values.app_name}}/42    |


### Access the info endpoint
http://home.${{values.app_env}}.com/api/v1/${{values.app_name}}/info

### View test page
http://home.${{values.app_env}}.com/${{values.app_name}}/test/${{values.app_name}}.html

### Swagger:
http://home.dev.com/api/v1/${{values.app_name}}/docs