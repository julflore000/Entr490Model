import scrapy
import numpy as np
import pandas as pd
from datetime import datetime

class ercotLoadSpider(scrapy.Spider):
    name = 'ercotLoad'
    mainLink = "https://www.ercot.com/content/cdr/html/%s_dam_mcpc.html" % (datetime.today().strftime('%Y%m%d'))
    start_urls = [mainLink]
    
    
    def parse(self, response):        
        #select out relevant data table
        data = response.css("table.tableStyle")
        
        #get real data and reshape into array for writing into file
        dataList = data.css("td::text").extract()
        npArray = np.reshape(np.array(dataList),(24,6))
        
        #inputing col names, left in if future development requires these prices
        colNames = ["Day","Hour Ending","NSPIN","REGDN","REGUP","RRS"]
        pdArray = pd.DataFrame(npArray,columns=colNames)
        
        #writing to unqieu file name of the respective date (checks first if data is already called before operation)
        fileName = ("%s_Load.xlsx" % npArray[0][0].replace("/","_"))
        pdArray[["Hour Ending","REGDN","REGUP"]].to_excel(fileName,index=False)
 