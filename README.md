# Asset Manager
This is my Andela Boot Camp V project. It's a web app to keep inventory of assets, mainly electronics e.g. laptop, projector, cables, etc.

## Specification
There are three type of users:

 1. **Super Admins:**
 A super admin can add other admins.

 2. **Admins:**
 The admins for this app, are staff members in the Ops and Facilities Department and the rest are staff members (and fellows)
  * An admin can add asset records.
  * An admin can add assign an asset to a staff member and set a date to reclaim assets
  * An admin can reclaim (un-assign) from a staff member
  * An admin can see a list of assigned assets (and their assignees) and a list of available (unassigned) items
  * An admin can get a reminder (notification) for items that are to be reclaimed soon, or the reclaiming date has passed
  * They can view all the cases of lost items, and lost-and-found items
  * They can mark a case as resolved (appropriately), with some description

 3. **Staff Members:**
  * They can report a case of an item getting lost
  * They can report a case of a lost-and-found item

## URL
[http://inventory-andela-bc.herokuapp.com/](http://inventory-andela-bc.herokuapp.com/)
