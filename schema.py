"""This contains the schema for various tables in the database"""

ingredientSchema = '''INGREDIENT
       (ID           INTEGER PRIMARY KEY AUTOINCREMENT,
       NAME          TEXT                UNIQUE,
       CALORIES      NUM                 CHECK (CALORIES >= 0),
       CARBOHYDRATE  NUM                 DEFAULT 0,
       PROTEIN       NUM                 DEFAULT 0,
       FAT           NUM                 DEFAULT 0,
       FIBER         NUM                 DEFAULT 0,
       FRUIT         BOOLEAN             DEFAULT 0,
       VEGETABLE     CHAR(1)             DEFAULT 'N',
       QUANTITY      NUM                 CHECK (QUANTITY > 0),
       SERVING_UNIT  TEXT                NOT NULL);'''

mealSchema = '''MEAL
        (ID           INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME          TEXT                UNIQUE,
        INGREDIENTS   ARRAY?              NOT NULL
        QUANTITIES    ARRAY?              NOT NULL);'''
   
foodlogSchema = '''FOODLOG
        (LOG_ID        INTEGER PRIMARY KEY AUTOINCREMENT,
        DATE           NUM                 NOT NULL,
        INGREDIENT     INTEGER             NOT NULL,
        QUANTITY_EATEN NUM                 CHECK (QUANTITY_EATEN > 0));'''
	   
exerciseSchema = '''EXERCISE
        (ID               INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME              TEXT                UNIQUE,
        PRIMARY MUSCLE    TEXT                NOT NULL,
        SECONDARY MUSCLES ARRAY?              DEFAULT 0,
        FORCE             TEXT                NOT NULL,
        QUANTITY          NUM                 CHECK (QUANTITY > 0),
        REP_UNIT          TEXT                NOT NULL);'''

routineSchema = '''ROUTINE
        (ID               INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME              TEXT                UNIQUE,
        EXERCISES         ARRAY?              NOT NULL,
        QUANTITIES        ARRAY?              NOT NULL);'''

exerciselogSchema = '''EXERCISELOG
        (LOG_ID        INTEGER PRIMARY KEY AUTOINCREMENT,
        DATE           NUM                 NOT NULL,
        EXERCISE       INTEGER             NOT NULL,
        WEIGHT         INTEGER             DEFAULT 0,
        QUANTITY_DONE  NUM                 CHECK (QUANTITY_DONE > 0));'''
	   
weightlogSchema = '''WEIGHTLOG
        (LOG_ID       INTEGER PRIMARY KEY AUTOINCREMENT,
        DATE          NUM                 NOT NULL,
        QUANTITY      NUM                 NOT NULL);'''