# YATUBE
🛠 With this social network project, you can create posts, leave comments under posts, and subscribe to the authors you like. 
#### Used tools:
- Python, 
- Django, 
- Pillow
- sorl-thumbnail
- Bootstrap

# 🚀 Project installation

Клонируйте репозиторий

```sh
git clone git@github.com:gufin/hw05_final.git
```

Install and activate the virtual environment

```sh
python -m venv venv
source venv/scripts/activate
python -m pip install --upgrade pip
```
Next, you need to perform migrations:
```sh
python manage.py migrate
```
Create django superuser:
```sh
python manage.py createsuperuser
```
Collect static files:
```sh
python manage.py collectstatic
```
And run the project
```sh
python manage.py runserver
```
# :smirk_cat: Author
Drobyshev Ivan
