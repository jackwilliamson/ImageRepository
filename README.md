## ImageRepository

Endpoints:

# POST /auth/register
requires 'username', 'password' in body

Registers username and password as a user in system, as long as username hasn't been used before

# POST /auth/login
requires username, password in body

If password is correct, sets the sessions current user as this user

# GET /auth/logout
Logs current user out of session


# POST /images/
requires 'file' in body, which is the image to upload

allowed param '?private=True', which will set this image to be private to this user

# GET /images/
returns all public images (as urls), along with a user's private images if they are logged in

# GET /images/mine/
returns all images (as urls) this user uploaded, including the private images

allowed param '?private=True', which will return only the private images this user has uploaded

# DELETE /images/mine/
will delete all images the user uploaded

# GET /images/<int:image_id>
returns image if public image or if logged on user is accessing their own private image

# DELETE /images/<int:image_id>
deletes this image if the logged in user uploaded the image
