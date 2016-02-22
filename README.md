# Asset Tracker
A web app to keep inventory of assets, mainly electronics e.g. laptop, projector, cables, etc.

## Specification
 * This app should be able to keep inventory of Andela’s assets, mainly electronics e.g. laptop, projector, cables, etc.
 * The admins for this app, are staff members in the Ops and Facilities Department and the rest are staff members (and fellows)
 * As a super-admin, I should be to sign-in and add other admins
 * As an admin, I should be able to sign-in
 * As an admin, I should be able to add an asset record, with the following details: Asset Name, Description, Serial Number, Andela Serial Code, Date bought, etc.
 * As an admin, I should be able to assign an asset to a staff member. I should add the date for reclaiming back the asset
 * As an admin, I should be able to un-assign (reclaim) an asset from a staff member
 * As an admin, I should be able to see a list of assigned assets (and their assignees) and a list of available (unassigned) items
 * As an admin, I should be able to see a reminder (notification) for items that are to be reclaimed soon, or the reclaiming date has passed
 * As a user (staff member), I should be able to report a case of an item getting lost
 * As a user (staff member), I should be able to report a case of a lost-and-found item
 * As an admin, I should be able to view all the cases of lost items, and lost-and-found items
 * As an admin, I should be able to mark a case as resolved (appropriately), with some description

## Usage
### Using existing deployments
Follow the following URL to try out a **stable** version of the app:
 * [https://asset-tracker-ke.herokuapp.com](https://asset-tracker-ke.herokuapp.com)

To try out all the **newest features** of this app go to:
 * [https://asset-tracker-ke-staging.herokuapp.com](https://asset-tracker-ke-staging.herokuapp.com)

### Deploying
To deploy this app you need to have python and pip package manager installed in your computer.

Run `git clone https://github.com/thuo/AssetTracker` to clone the repo.

Run `cd AssetTracker` to make the project directory your working directory.

Run `pip install -r requirements` to install packages required by the app. To keep this installation separate from others, you should use [virtualenv](https://pypi.python.org/pypi/virtualenv).

Set the following environment variables required by the app:

 * `MAIL_USERNAME` and `MAIL_PASSWORD`: SMTP username and password for sending emails. The SMTP Server is set in `config.py` which is where you should edit if want to change it from GMail.
 * `APP_CONFIG`: use `config.DevelopmentConfig` for a development deployment. Other options are `config.ProductionConfig` and `config.StagingConfig`
 * `DATABASE_URL`: A database url in the format `postgresql://<username>:<password>@<host>/<database name>` e.g `postgresql://user:lion@localhost/asset_tracker`
 * `GOOGLE_CLIENT_ID`: To ensure _Sign in with Google_ works. You need a Google API project to obtain a client id.
 * `GOOGLE_WEB_CLIENT_ID`: Also, to ensure _Sign in with Google_ works.


Run `python manage.py db upgrade` to create database and its tables.

Run `python manage.py runserver` to start the server.

## Roadmap
 * The app should use a message queue for sending emails.
 * Provide instructions on how to deploy to Heroku.
