from datetime import date

from demand.history.orchestrator import HistoryDownloader


HistoryDownloader().run(

    date(2023, 8, 1),

    date(2023, 8, 10),

)
