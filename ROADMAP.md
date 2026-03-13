# Aktuelle Architektur 

```text
+-------------------+        JSON Export / Import        +---------------------+
|                   |  ------------------------------->  |                     |
|   Ionic App       |                                    |      Backend        |
|   (Angular)       |  <-------------------------------   |  Vue + Django API   |
|                   |        JSON Import / Export        |                     |
+---------+---------+                                    +----------+----------+
          |                                                         |
          |                                                         |
          v                                                         v
+------------------+                                    +----------------------+
| Local Storage /  |                                    |      PostgreSQL      |
| Preferences      |                                    |     (unused or       |
| JSON Files       |                                    |   partially used)    |
+------------------+                                    +----------------------+
```

# Zielstruktur

```text
                +----------------------+
                |                      |
                |      Web GUI         |
                |     (Vue / Web)      |
                |                      |
                +----------+-----------+
                           |
                           | REST API / WebSocket
                           |
+--------------------------v--------------------------+
|                                                     |
|                   Django Backend                    |
|                                                     |
|  - Authentication (JWT / Session / Passkey)        |
|  - Password API                                     |
|  - Sync Engine                                      |
|  - Encryption Layer                                 |
|                                                     |
+--------------------------+--------------------------+
                           |
                           |
                           v
                    +-------------+
                    | PostgreSQL  |
                    |  Database   |
                    +-------------+
                           ^
                           |
                           |
                REST API / Sync
                           |
+--------------------------+--------------------------+
|                                                     |
|                 Ionic Mobile App                    |
|                                                     |
|  - Local Cache (Preferences / SQLite)               |
|  - Sync Client                                      |
|  - Biometric Unlock                                 |
|                                                     |
+-----------------------------------------------------+
```

## Model
```text
User
 └── Application
       ├── PasswordGroup
       │      └── PasswordItem
       │
       └── RecipeCategory
              └── Recipe
```




