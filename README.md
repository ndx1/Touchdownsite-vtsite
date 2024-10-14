cf. doc

# VictoryTouchdown

## Application de gestion des commandes de produits marketing.
### Comment installer Vtsite/Vtshop en local : 
---

0. Pré-requis : 
 - Avoir installé Python v10. ou plus sur la machine locale. https://www.python.org/downloads/
 - Avoir installé Git sur la machine locale. https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
 - Optionnel : avoir installé PostgreSQL sur la machine locale. https://www.postgresql.org/download/

1. Cloner le projet : 
 - Copier le lien Github en haut à droite de la page "code" du dépôt.
 - Dans un terminal, se placer à l'emplacement local où l'on veut que le dossier source soit cloné.
 - Exécuter la commande git clone : 
````
 git clone https://github.com/ndx1/vtsite.git
````

 - En principe un dossier nommé vtsite s'est crée. S'y déplacer : 
````
 cd vtsite
````
2. Créer un environnement virtuel (ici nommé *env* ) à l'aide de la commande : 
````
 python3 -m venv env
````

3. Activer l'environnement virtuel à l'aide de la commande : 
 
* pour les plateformes Unix/Linux : 
````
 source env/bin/activate
````

* pour la plateforme Windows (cmd.exe):
````
 source env/scripts/activate
````
 * autre : consulter https://docs.python.org/3/library/venv.html

Votre invite de commande doit maintenant être précédée de `(env)`, vous indiquant que vous êtes bien dans l'environnement virtuel.

4. Installer les dépendances du projet : 
````
 pip install -r requirements.txt
````

5. Base de données : 

 - Soit la BDD SQlite3 utilisée par défaut par Django :

    - S'il n'existe pas déjà, créer un fichier nommé `db.sqlite3` à la racine du projet : 
      ````
      touch db.sqlite3
      ````
 
    - modifier le fichier `vtsite/settings.py` comme suit :

      ````
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.sqlite3',
              'NAME': BASE_DIR / 'db.sqlite3',
          }
      }
      ````

 - Soit une BDD Postgres : https://www.postgresql.org/download/ 

      Et dans ce cas, modifier le fichier `vtsite/settings.py` et accorder le dictionnaire DATABASES avec vos propres clés NAME et USER qui sont généralement le nom de votre compte utilisateur sur votre machine. 
      ````
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.postgresql',
              'NAME': 'username',
              'USER': 'username',
              'PASSWORD': '',
              'HOST': 'localhost',
              'PORT': '5432',
          }
      }
      ````

7. Jouer les migrations pour créer les tables dans la BDD : 
````
 python manage.py makemigrations vtshop
 python manage.py migrate
````

8. Créer un dossier `media/` à la racine du projet. Django y stockera les photos des produits.
````
mkdir media
````

9. Lancer l'application : 
````
 python manage.py runserver
````

On peut retrouver la page d'ouverture à l'adresse locale : 
````
 http://127.0.0.1:8000/
````


## Utilisation : 
---

 - On peut peupler la BDD à l'aide de la **fixture** se trouvant dans le dossier **vtshop/fixtures**.

Pour intégrer des données, utiliser la commande **loaddata** (Django trouve le fichier tout seul en principe):
````
 python manage.py loaddata vtdata.json
````

Et éventuellement créer un superuser Django avec la commande : 
````
 python manage.py createsuperuser
````

 - On peut aussi tout créer depuis la BDD vide de données :

1. Créer un superuser Django avec la commande précédente 

2. Ensuite, avec ce super utilisateur, on accède à la partie admin de Django ici http://127.0.0.1:8000/admin

    Ceci nous permet de créer un utilisateur avec un compte administrateur pour vtsite. Ne pas oublier de lui attribuer le rôle admin.

3. En se connectant avec ce compte administrateur dans l'interface vtouchdown, on accède à l'Espace Administrateur pour créer un/des Employé.e.s.

4. Ensuite le compte Employé quant à lui permet de créer et gérer produits, commandes, etc. à partir de son espace "Intranet".

Se référer au Quick Start Guide disponible dans la documentation, SVP, pour retrouver le détail de ces étapes à l'utilisation de Vtshop, y compris en tant que Visiteur / Utilisateur.

---
