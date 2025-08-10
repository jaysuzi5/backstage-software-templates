# Documentation for ${{values.app_name}}
### ${{values.description}}
This application has two endpoints:
- /v1/${{values.app_name}}/info
- /v1/${{values.app_name}}/health


### CRUD Endpoints:
- GET: /v1/${{values.app_name}}/
- POST: /v1/${{values.app_name}}/

>Here you can expand on what each of these endpoints do.

# How to access the app?
You can access the app by accessing the URL: http://home.${{values.app_env}}.com/api/v1/${{values.app_name}}/info