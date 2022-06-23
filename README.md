# Im2SQL - API

![Image-2-SQL](https://user-images.githubusercontent.com/76481787/138583272-aa3f1f50-a56b-483f-b8ed-a51e7c4d37be.png)

<!-- <center><img src="https://user-images.githubusercontent.com/76481787/138583272-aa3f1f50-a56b-483f-b8ed-a51e7c4d37be.png" style="align: center;"></center> -->

## What is it?

The FastAPI-based API backend-only implementation of Im2SQL. Im2SQL is an app to reduce the cumbersome task of writing data entry statements manually, Im2SQL converts Table Images to SQL INSERT commands that are returned in a textbox within max 8 seconds.

Needs a JS-based frontend.

## End Points:

### ```/sqlify/make/``` - To convert the image to SQL ```INSERT``` commands.

Supported paramters:

1. ```typecheck```: Checks for the correctness of the SQL commands.

2. ```columns```: Intended number of columns for the table to contain.

3. ```table_name```: The table name to generate the commands with.

4. ```include_schema```: Whether to consider schema or not:
    - **true** will imply that the data starts from second row from the table, and the first row will be omitted.

    - **false** will imply that the data starts from the first row.

5. ```uploadfile```: The image to upload.
