from demand.acquisition.source import Source


IMD = Source(

    id="IMD",

    name="India Meteorological Department",

    homepage="https://mausam.imd.gov.in/",

    download_url="https://mausam.imd.gov.in/responsive/rainfallinformation_swd.php",

    update_frequency="daily",

    format="html",

    storage_folder="imd",

)
