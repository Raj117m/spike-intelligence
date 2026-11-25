from demand.acquisition.database import DatasetDatabase

db = DatasetDatabase()

db.initialize()

con = db.con

datasets = [

(
"WIKIDATA",
"Wikidata JSON Dump",
"Wikimedia Foundation",
"knowledge_graph",
"https://dumps.wikimedia.org/wikidatawiki/entities/",
"https://dumps.wikimedia.org/wikidatawiki/entities/",
"weekly",
"2014",
"json.bz2",
150,
"CC0",
10,
True,
),

(
"GDELT",
"GDELT Event Database",
"GDELT",
"events",
"https://www.gdeltproject.org/",
"http://data.gdeltproject.org/",
"15 minutes",
"1979",
"csv.zip",
3000,
"Open",
10,
True,
),

(
"WIKI_PAGEVIEWS",
"Wikipedia Pageviews",
"Wikimedia Foundation",
"attention",
"https://dumps.wikimedia.org/other/pageview_complete/",
"https://dumps.wikimedia.org/other/pageview_complete/",
"monthly",
"2015",
"bz2",
500,
"CC BY-SA",
9,
True,
),

]

for d in datasets:

    con.execute(

        """
        INSERT OR REPLACE INTO datasets
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,

        d,

    )

print(con.execute("SELECT id,name FROM datasets").fetchall())
